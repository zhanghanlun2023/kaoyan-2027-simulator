"""Expand English II passages to syllabus-scale lengths without changing answers.

The script accepts the canonical english2_bank JSON on stdin and writes a revised
bank. It is deliberately deterministic so the published data can be rebuilt and
audited.
"""

from __future__ import annotations

import argparse
import base64
import json
import re
import sys
from pathlib import Path


WORD_RE = re.compile(r"[A-Za-z]+(?:['’-][A-Za-z]+)*")


def word_count(text: str) -> int:
    return len(WORD_RE.findall(text))


CLOZE_DETAILS = [
    ("library staff had noticed that evening demand was concentrated around exam periods, while weekend patterns were less predictable",
     "The pilot therefore tracked not only entry counts but also desk occupancy, requests for assistance, and the cost of keeping specialist services available."),
    ("hospital managers were trying to shorten waiting times without encouraging staff to rush conversations with patients",
     "They separated administrative delay from clinical time and invited nurses to report problems that a simple speed measure would have missed."),
    ("the retailer wanted fewer abandoned purchases but did not want a faster checkout to make returns or payment disputes more common",
     "Analysts followed customer questions, repeat visits, and support calls alongside sales, because a quick transaction is not always a satisfactory one."),
    ("transport planners needed to improve reliability on a route whose demand changed sharply with weather, school terms, and major events",
     "They logged missed connections as well as average journey time and asked drivers whether the revised schedule created pressure at particular stops."),
    ("factory managers hoped to reduce minor defects while protecting the discretion of experienced operators who often detected unusual faults first",
     "The trial recorded rework, machine stoppages, and near misses, and it gave each shift a way to challenge a misleading indicator before decisions were made."),
    ("college leaders wanted more students to complete practical assignments, yet they worried that extra reminders might encourage dependence rather than planning",
     "The evaluation combined submission records with short interviews about workload, confidence, and whether learners could transfer the new routine to other courses."),
    ("the service center was under pressure to answer clients faster, although complex cases could be harmed by targets designed for routine requests",
     "Supervisors reviewed a sample of resolved cases and compared speed with accuracy, follow-up contacts, and the clarity of explanations given to customers."),
    ("the company wanted shorter release cycles, but engineers warned that visible delivery dates could hide maintenance work and delayed technical risk",
     "The team monitored defects after release, interruptions to planned work, and the time needed for code review instead of treating output volume as the only result."),
    ("museum staff hoped clearer labels would help first-time visitors without oversimplifying objects whose histories remained contested",
     "They observed reading time, questions to guides, and visitor recall, while curators reviewed whether important uncertainty had disappeared from the revised text."),
    ("the provider wanted households to respond to usage information, though seasonal demand and housing quality could limit what customers were able to change",
     "Researchers compared similar billing periods and recorded requests for advice, not merely total consumption, so that access and understanding remained visible."),
]


READ_A_TOPICS = [
    ("Public libraries must decide whether longer access justifies staffing and security costs.", "Weekend hours may help workers and students whose schedules exclude weekday visits.", "seasonal demand and examination periods can distort a short trial"),
    ("Missed medical appointments waste scarce capacity, but reminders can also become intrusive.", "A timely message may help patients reorganize travel, work, or caring duties.", "patients who consent to messages may already be more engaged with treatment"),
    ("A single final examination is efficient to administer but can reward short-term recall.", "Smaller assessments may reveal misconceptions early enough for teachers to respond.", "extra tasks may increase workload without improving durable understanding"),
    ("Passengers value reliable information almost as much as a perfectly reliable timetable.", "Live arrival data can turn an uncertain wait into a manageable decision.", "technical accuracy may vary across routes and times of day"),
    ("Retail returns are costly, and some occur because buyers cannot judge whether an item is repairable.", "Practical guidance may extend product life and increase confidence before purchase.", "customers attempting difficult repairs may create new safety or warranty problems"),
    ("Routine safety messages are often ignored when workers have heard them many times.", "Short briefings tied to the day's actual tasks may make hazards easier to recognize.", "a fall in reported incidents might reflect under-reporting rather than safer work"),
    ("Museum labels must be accessible without pretending that every object has a simple history.", "Plain language can free visitors to consider the evidence instead of decoding jargon.", "simplification may remove uncertainty that curators consider intellectually important"),
    ("Account forms protect both banks and customers, yet complexity can prevent informed choice.", "A clearer sequence may reduce accidental omissions and requests for staff help.", "completion rates alone do not show whether customers understood long-term costs"),
    ("Short project cycles promise focus, though not every kind of software work divides neatly.", "Frequent review can expose weak assumptions before teams invest heavily in them.", "employees may report satisfaction while hidden maintenance work accumulates"),
    ("Online booking can widen access to community classes but may disadvantage people with limited digital skills.", "Visible availability reduces unnecessary travel and telephone waiting.", "higher attendance may come from existing users rather than new participants"),
    ("Lecture recordings can support review, illness, and students working in a second language.", "Learners can revisit difficult explanations at their own pace.", "recordings may change attendance or encourage passive study"),
    ("Nutrition labels aim to inform rather than dictate what customers should eat.", "Showing information at the moment of choice may correct mistaken estimates.", "purchases observed in restaurants may not represent a person's overall diet"),
    ("Budget documents are public, but formal accounting categories are difficult for non-specialists.", "Short summaries can show residents where major changes occurred and why.", "a simplified account can improve confidence without improving detailed knowledge"),
    ("Wide delivery windows transfer uncertainty from companies to customers.", "Narrower estimates allow people to plan work and caring responsibilities.", "accuracy may deteriorate during bad weather or exceptional demand"),
    ("Corrections are essential to trustworthy journalism, yet prominent notices may initially draw attention to mistakes.", "Clear labels let readers distinguish revision from silent alteration.", "stated trust may differ from later reading and sharing behavior"),
    ("Urban parks are public in principle, but heat can make them unusable at certain hours.", "Shade may extend visits for older people, children, and outdoor workers.", "weather during the test period may exaggerate or hide the effect"),
    ("Digital check-in can remove routine queues while leaving staff available for unusual requests.", "Guests may correct details before arrival and receive rooms more quickly.", "technology failures and accessibility needs may be rare in a small pilot"),
    ("Preregistration asks researchers to separate planned tests from later exploration.", "That distinction can make evidence easier for other scientists to interpret.", "compliance on paper does not guarantee thoughtful research decisions"),
    ("Product placement shapes attention even when shoppers believe their choices are independent.", "Moving healthier food may make comparison easier without removing alternatives.", "short-term sales do not establish lasting dietary change"),
    ("Donors often want evidence that their contribution had a concrete use.", "Project updates may strengthen a relationship by explaining progress and setbacks.", "frequent donors may be more likely both to read updates and to give again"),
    ("Fixed session times exclude members whose work and family schedules change.", "Flexible booking may reduce missed exercise without requiring more facilities.", "popular slots can become crowded and shift inconvenience to other users"),
    ("Utility bills contain necessary detail but often hide the information customers need first.", "Visual summaries can make unusual charges and trends easier to notice.", "fewer questions may reflect resignation rather than better understanding"),
    ("Archives are valuable only when researchers can discover what they contain.", "Digital indexes allow distant users to test whether a visit will be worthwhile.", "better discovery does not mean the underlying material has been digitized"),
    ("Salary secrecy can waste applicants' time and preserve unequal bargaining power.", "Published ranges help candidates judge fit before completing an application.", "employers adopting transparency may differ from those that refuse it"),
    ("Fast access to test results may reduce anxiety and speed appropriate follow-up.", "A secure portal can give patients information without waiting for office hours.", "results without explanation may confuse people or create avoidable alarm"),
    ("Sample chapters reduce uncertainty about style, difficulty, and relevance.", "Readers can make a more informed purchase rather than relying on advertising.", "free material may attract browsers who were already likely to buy"),
    ("Housing applications fail for reasons ranging from missed dates to missing evidence.", "Alerts can make deadlines visible while applicants gather documents.", "reminders cannot solve affordability or eligibility barriers"),
    ("Feedback is useful when it arrives soon enough to shape the next attempt.", "Practice comments may turn a course from content delivery into guided improvement.", "completion can rise even if skills are not retained after the course"),
    ("Hourly energy data makes invisible consumption patterns easier to connect with daily routines.", "Households may move flexible activities away from expensive peak periods.", "renters and low-income users may have less control over appliances and insulation"),
    ("Cancellation rules affect travel decisions long before a customer needs to cancel.", "Earlier explanations may prevent buyers from selecting a cheap but unsuitable option.", "clearer rules do not protect travelers from every unexpected event"),
]


METHOD_PARAGRAPHS = [
    "A credible evaluation must therefore begin before the new arrangement is introduced. Researchers need a comparison group, a baseline, and more than one outcome. They should also record who accepts the change and who avoids it. Otherwise, an apparent improvement may simply show that the easiest cases entered the pilot while the hardest ones remained outside it.",
    "The central difficulty is separating the effect of the intervention from ordinary variation. Week-to-week demand, staff enthusiasm, publicity, and local events can all move the numbers. For that reason, the investigators compared similar users over the same period and treated comments from front-line staff as evidence rather than as decorative quotations.",
    "Numbers answer only part of the question. A policy may improve its headline measure while shifting cost, delay, or confusion somewhere else. The research team therefore specified a primary outcome, a secondary outcome, and a subgroup before examining the results. This reduced the temptation to advertise whichever number happened to look most favorable.",
    "Pilots are useful because they make uncertainty manageable, not because they remove it. The design combined routine administrative records with brief interviews and observations. That mixture helped the researchers ask both whether behavior changed and why. It also exposed practical problems that a larger statistical comparison might have hidden until much later.",
    "Any trial can influence the people taking part. Staff may work unusually hard because a project is being watched, while volunteers may be more motivated than typical users. The researchers tried to limit these effects by using existing records and a comparable group, but they did not claim that those safeguards produced a perfect experiment.",
]


IMPLICATION_PARAGRAPHS = [
    "The practical question is what should happen after the first result. Immediate expansion would save time if the idea is sound, but it would also spread any design flaw. A staged decision is slower and less dramatic. It allows the institution to test the mechanism again, include people missing from the pilot, and decide whether the observed gain is large enough to matter outside a report.",
    "This distinction matters to managers as well as researchers. An average improvement can conceal users who gained nothing or even faced a new barrier. Before adopting the change, decision makers need to examine distribution, implementation cost, and the conditions required to reproduce the effect. A result can be statistically visible yet too fragile or expensive to justify a permanent policy.",
    "Public discussion often turns a pilot into a vote for or against innovation. That framing is misleading. Evidence can support one part of an idea, challenge another, and leave important questions unanswered. The sensible response is to specify what has been learned, what remains uncertain, and which next test would reduce that uncertainty most efficiently.",
    "There is also a communication risk. A percentage increase sounds precise, but readers may not know the starting level, the comparison, or the number of people affected. Responsible reporting supplies those details and avoids causal language stronger than the design permits. Doing so does not weaken a promising finding; it makes the finding useful to people deciding whether their own circumstances are sufficiently similar.",
    "Finally, local knowledge should not be treated as the enemy of measurement. Staff and users can identify mechanisms that administrative data cannot show, while records can test impressions that feel convincing but are unrepresentative. Bringing the two forms of evidence together produces a more demanding standard than either enthusiasm or numerical change alone.",
]


READ_B_STAGE_TEXT = [
    "At the beginning, people often rush toward a solution because action feels productive. A better first move is to make the underlying task explicit, identify who is affected, and state what evidence would count as improvement. This prevents a team from solving the most visible symptom while leaving the real difficulty untouched.",
    "The next step creates a reliable point of comparison. Existing routines, costs, delays, and user experiences should be recorded before anything changes. Without that reference, ordinary variation can be mistaken for success. The record need not be elaborate, but its definitions must remain stable throughout the exercise.",
    "Implementation should be narrow enough to observe closely and large enough to reveal practical friction. Participants need clear responsibilities, a fixed period, and a way to report surprises. Keeping the first attempt limited protects people from avoidable disruption and allows weak assumptions to be corrected at modest cost.",
    "Review must look beyond the headline result. Time saved in one place may reappear as confusion, exclusion, or extra work elsewhere. Both intended and unintended effects deserve attention, including differences between groups. Honest review treats an inconvenient finding as useful information rather than as a threat to the project.",
    "The final decision should follow the evidence instead of the enthusiasm surrounding a new idea. Teams can expand, revise, repeat, or stop the change. They should document why, explain remaining uncertainty, and set a later review date. That closes one learning cycle while preserving what the next cycle needs.",
]


def expand_cloze(bank: dict) -> None:
    for idx in range(10):
        pid = f"passage_en2_cloze_{idx:02d}"
        original = bank["passages"][pid]
        context, measure = CLOZE_DETAILS[idx]
        addition = (
            f"Before the formal test began, {context}. This mattered because a single headline number could make the change look more successful than it really was. Managers agreed in advance that a useful result had to improve the main service without quietly transferring cost or difficulty to another group.\n\n"
            f"{measure} These additional observations changed several early assumptions and gave the team a more realistic account of what implementation required. "
            "They also made the final discussion less dependent on anecdotes: supporters had to explain the limits of the gains, while skeptics had to identify which recorded costs were serious enough to outweigh them."
        )
        paragraphs = original.split("\n\n")
        bank["passages"][pid] = "\n\n".join([*paragraphs[:2], addition, *paragraphs[2:]])


def expand_read_a(bank: dict) -> None:
    for idx, (problem, benefit, risk) in enumerate(READ_A_TOPICS):
        pid = f"passage_en2_reada_{idx:02d}"
        original = bank["passages"][pid]
        method = METHOD_PARAGRAPHS[idx % len(METHOD_PARAGRAPHS)]
        implication = IMPLICATION_PARAGRAPHS[idx % len(IMPLICATION_PARAGRAPHS)]
        opening = (
            f"{problem} The issue is not simply whether a new arrangement sounds attractive, but whether it changes behavior under ordinary conditions. "
            f"Supporters argue that {benefit[0].lower() + benefit[1:]} Critics reply that resources are limited and that benefits for one group can create inconvenience for another."
        )
        interpretation = (
            f"The proposed mechanism is plausible: {benefit[0].lower() + benefit[1:]} Yet plausibility is not proof. In this case, {risk}. "
            "A useful study must therefore preserve the difference between a promising local result and a general rule. It should also report an outcome that the intervention was not expected to improve, since that comparison can reveal whether observers are merely seeing broad enthusiasm for change. "
            "Following the process for longer would show whether early attention fades, while repeating it elsewhere would test how strongly the outcome depends on local conditions."
        )
        bank["passages"][pid] = "\n\n".join([opening, method, interpretation, implication, original])


def expand_read_b(bank: dict) -> None:
    for idx in range(10):
        pid = f"passage_en2_readb_{idx:02d}"
        original = bank["passages"][pid]
        paragraphs = original.split("\n\n")
        if len(paragraphs) != 5:
            raise ValueError(f"{pid} should contain five paragraphs")
        revised = []
        for order, paragraph in enumerate(paragraphs):
            scenario = re.search(r"when (.+?)\. It gives", paragraph)
            setting = scenario.group(1) if scenario else "completing the process"
            revised.append(
                f"{paragraph} {READ_B_STAGE_TEXT[order]} In the context of {setting}, this stage also gives participants a shared language for explaining why later choices were made."
            )
        bank["passages"][pid] = "\n\n".join(revised)


def validate(bank: dict) -> dict:
    expected = {
        "英语知识运用（完形填空）": (340, 390, 10),
        "阅读理解A": (360, 430, 30),
        "阅读理解B（新题型）": (450, 550, 10),
    }
    by_passage = {}
    for question in bank["questions"]:
        pid = question.get("passage_id")
        if pid:
            by_passage.setdefault(pid, question["section"])
    summary = {}
    for section, (low, high, expected_count) in expected.items():
        counts = [
            word_count(bank["passages"][pid])
            for pid, item_section in by_passage.items()
            if item_section == section
        ]
        if len(counts) != expected_count:
            raise ValueError(f"{section}: expected {expected_count} passages, got {len(counts)}")
        outside = [value for value in counts if not low <= value <= high]
        if outside:
            raise ValueError(f"{section}: word counts outside {low}-{high}: {outside}")
        summary[section] = {
            "passages": len(counts),
            "min": min(counts),
            "max": max(counts),
            "average": round(sum(counts) / len(counts)),
        }
    if len(bank["questions"]) != 520:
        raise ValueError("English II bank must retain exactly 520 questions")
    return summary


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path)
    parser.add_argument("--stdin", action="store_true")
    parser.add_argument("--stdin-base64", action="store_true")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.stdin:
        bank = json.load(sys.stdin)
    elif args.stdin_base64:
        encoded = "".join(sys.stdin.read().split())
        bank = json.loads(base64.b64decode(encoded).decode("utf-8"))
    elif args.input:
        bank = json.loads(args.input.read_text(encoding="utf-8"))
    else:
        parser.error("use --stdin or --input")

    expand_cloze(bank)
    expand_read_a(bank)
    expand_read_b(bank)
    summary = validate(bank)
    args.output.write_text(json.dumps(bank, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False))


if __name__ == "__main__":
    main()

