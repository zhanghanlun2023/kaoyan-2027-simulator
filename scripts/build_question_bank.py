from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "data" / "questions.json"


def optionize(correct: object, distractors: list[object], shift: int = 0, formatter=str):
    values = []
    for value in [correct, *distractors]:
        if value not in values:
            values.append(value)
    if isinstance(correct, (int, float)):
        offset = 1
        while len(values) < 4:
            candidate = correct + offset
            if candidate not in values:
                values.append(candidate)
            offset += 1
    if len(values) != 4:
        raise ValueError(f"选项必须恰好有4个不同值: {values}")
    shift %= 4
    values = values[shift:] + values[:shift]
    keys = "ABCD"
    options = {key: formatter(value) for key, value in zip(keys, values)}
    answer = keys[values.index(correct)]
    return options, answer


questions: list[dict] = []


def add(qid, subject, chapter, difficulty, qtype, stem, options, answer, points, explanation, *, format_tag="专项选择题"):
    questions.append({
        "id": qid,
        "subject": subject,
        "chapter": chapter,
        "difficulty": difficulty,
        "type": qtype,
        "stem": stem,
        "options": options,
        "answer": answer,
        "points": points,
        "explanation": explanation,
        "source": "原创仿真",
        "format_tag": format_tag,
    })


with TARGET.open("r", encoding="utf-8") as handle:
    legacy = json.load(handle)

# 仅保留旧版中题型与真实客观题训练相符的条目；英译汉不再伪装成选择题。
legacy_ids = {
    *{f"p{i:03d}" for i in range(1, 7)},
    *{f"e1{i:02d}" for i in range(1, 7)},
    *{f"e2{i:02d}" for i in range(1, 7)},
    *{f"m1{i:02d}" for i in range(1, 6)},
    *{f"m2{i:02d}" for i in range(1, 6)},
    *{f"m3{i:02d}" for i in range(1, 6)},
    *{f"c{i:03d}" for i in range(1, 9)},
}
for q in legacy:
    if q["id"] not in legacy_ids or q["chapter"] == "英译汉":
        continue
    item = dict(q)
    item.setdefault("format_tag", "专项选择题")
    questions.append(item)


# ------------------------- 思想政治理论 -------------------------
politics_bank = [
    ("马克思主义基本原理", "价值量由社会必要劳动时间决定", "某行业普遍采用新工艺后，生产同一件商品所需的平均劳动时间下降。其他条件不变，单位商品价值量将", {"A":"上升","B":"下降","C":"不变","D":"先升后降"}, "B", "行业社会劳动生产率提高，社会必要劳动时间缩短，单位商品价值量下降。"),
    ("马克思主义基本原理", "实践是检验认识真理性的唯一标准", "一项理论能否被确认为真理，最终要看它是否", {"A":"得到多数人赞同","B":"逻辑形式完美","C":"在实践中达到预期结果","D":"由权威提出"}, "C", "实践能够把主观认识同客观结果联系起来，是检验真理性的唯一标准。"),
    ("马克思主义基本原理", "矛盾普遍性与特殊性相统一", "把一般政策转化为适合本地区的具体方案，体现的哲学道理是", {"A":"否认规律客观性","B":"共性寓于个性之中","C":"现象决定本质","D":"量变必然中断"}, "B", "一般要求必须通过具体条件实现，体现矛盾普遍性和特殊性的统一。"),
    ("马克思主义基本原理", "量变是质变的必要准备", "企业持续改进工艺，积累到一定程度后生产方式发生根本变化。这说明", {"A":"质变排斥量变","B":"量变是质变的必要准备","C":"偶然性决定必然性","D":"事物发展没有过程"}, "B", "量的积累达到一定程度会引起质变。"),
    ("马克思主义基本原理", "人民群众是历史创造者", "评价社会发展动力时，坚持历史唯物主义应首先看到", {"A":"少数英雄可以脱离社会条件创造历史","B":"人民群众是社会物质财富和精神财富的创造者","C":"思想观念独立决定历史进程","D":"自然环境是唯一动力"}, "B", "人民群众是社会历史的主体和历史创造者。"),
    ("中国近现代史纲要", "帝国主义和中华民族的矛盾", "近代中国社会各种矛盾中最主要的矛盾是", {"A":"帝国主义和中华民族的矛盾","B":"工人阶级和农民阶级的矛盾","C":"城市和乡村的矛盾","D":"工业和农业的矛盾"}, "A", "帝国主义和中华民族的矛盾是近代中国社会最主要的矛盾。"),
    ("思想道德与法治", "法治与德治相结合", "推进国家治理现代化，正确处理法治与德治关系应当", {"A":"只强调道德教化","B":"只依靠法律强制","C":"坚持依法治国和以德治国相结合","D":"以个人好恶替代规则"}, "C", "法治和德治相辅相成，应坚持依法治国和以德治国相结合。"),
    ("习近平新时代中国特色社会主义思想概论", "中国式现代化", "中国式现代化本质要求的首项是", {"A":"坚持中国共产党领导","B":"照搬西方模式","C":"先污染后治理","D":"减少公共服务"}, "A", "坚持中国共产党领导是中国式现代化本质要求的首项。"),
    ("毛泽东思想和中国特色社会主义理论体系概论", "实事求是", "从实际情况出发制定政策并在实践中检验和发展真理，体现了党的思想路线中的", {"A":"实事求是","B":"闭门造车","C":"经验至上","D":"形式主义"}, "A", "实事求是要求一切从实际出发、理论联系实际，并在实践中检验和发展真理。"),
    ("思想道德与法治", "法律面前人人平等", "行政机关对事实和情节相同的案件适用同一标准，主要体现", {"A":"法外特权","B":"法律面前人人平等","C":"权力不受监督","D":"程序可以省略"}, "B", "同等情况同等对待是法律面前人人平等的基本要求。"),
]
contexts = ["下列理解正确的是：", "从这一材料可以推出：", "该案例主要说明："]
for i, (chapter, concept, stem, options, answer, explanation) in enumerate(politics_bank):
    for j, suffix in enumerate(contexts):
        add(f"gp{i:02d}{j}", "思想政治理论", chapter, 2 + (i + j) % 3, "single", f"{stem}。{suffix}", options, answer, 2, explanation, format_tag=f"稳定考点 · {concept}")


# ------------------------- 英语一 / 英语二 -------------------------
cloze_bank = [
    ("Scientific conclusions should remain open to revision ___ new evidence emerges.", {"A":"unless","B":"when","C":"although","D":"before"}, "B", "when 引导时间状语，表示新证据出现时应修正结论。"),
    ("The proposal is attractive in theory; ___, its cost has not been fully assessed.", {"A":"therefore","B":"similarly","C":"however","D":"for example"}, "C", "前后是转折关系，应使用 however。"),
    ("Customers value convenience, but few are willing to ___ security for speed.", {"A":"sacrifice","B":"restore","C":"predict","D":"deliver"}, "A", "sacrifice A for B 表示为了B牺牲A。"),
    ("The result should be treated with caution, ___ the sample came from one city.", {"A":"given that","B":"even if","C":"so that","D":"whereas"}, "A", "given that 引出需要谨慎的原因。"),
    ("A good model is useful not because it copies reality perfectly, ___ because it simplifies it productively.", {"A":"or","B":"but","C":"and","D":"so"}, "B", "固定对比结构 not because..., but because...。"),
    ("The team postponed the launch in order to ___ several unresolved safety concerns.", {"A":"address","B":"display","C":"inherit","D":"estimate"}, "A", "address concerns 表示处理、应对问题。"),
    ("The policy had an effect that was small but statistically ___.", {"A":"significant","B":"ordinary","C":"available","D":"temporary"}, "A", "statistically significant 是统计学常用搭配。"),
    ("Rather than ___ employees constantly, managers should clarify goals and constraints.", {"A":"monitor","B":"monitored","C":"to monitor","D":"monitoring"}, "D", "rather than 在此与后面的动名词结构对应。"),
    ("The museum redesigned its signs so that visitors could find exhibits more ___.", {"A":"rarely","B":"easily","C":"loosely","D":"quietly"}, "B", "语境要求表达更容易找到展品。"),
    ("Evidence from a single case cannot, by itself, ___ a universal claim.", {"A":"justify","B":"borrow","C":"remove","D":"attend"}, "A", "justify a claim 表示为主张提供充分依据。"),
    ("Although the device is cheaper, it is not necessarily more ___ over its full life cycle.", {"A":"economical","B":"economic","C":"economy","D":"economize"}, "A", "economical 表示节省成本、经济实用。"),
    ("The report distinguishes correlation ___ causation.", {"A":"from","B":"with","C":"by","D":"into"}, "A", "distinguish A from B 是固定搭配。"),
    ("Public trust is difficult to build and easy to ___.", {"A":"erode","B":"arrange","C":"measure up","D":"settle down"}, "A", "erode trust 表示逐渐损害信任。"),
    ("The experiment was repeated to determine ___ the first result was accidental.", {"A":"whether","B":"what","C":"whose","D":"where"}, "A", "whether 引导宾语从句，表示是否。"),
    ("Productivity improved, ___ employees reported no increase in working hours.", {"A":"while","B":"because of","C":"unless","D":"despite"}, "A", "while 可连接两个完整分句并表示对照。"),
]
reading_bank = [
    ("A library extended weekend hours. Attendance rose sharply, while book lending changed little. Surveys showed that most new visitors used quiet desks, group rooms and free internet access.", "The passage mainly shows that the library—", {"A":"failed to promote reading","B":"serves needs beyond lending books","C":"should close on weekends","D":"attracts only internet users"}, "B", "到访增加而借阅变化不大，是因为图书馆还提供空间和网络等服务。"),
    ("A firm introduced a four-day schedule without reducing total weekly hours. Staff satisfaction improved, but sick leave and output remained almost unchanged.", "Which statement is supported?", {"A":"Employees worked fewer hours","B":"Reported satisfaction improved","C":"Sick leave disappeared","D":"Output doubled"}, "B", "材料只明确支持满意度提高。"),
    ("Algorithms can make consistent decisions. Yet consistency may simply reproduce a consistently biased rule.", "The second sentence mainly serves to—", {"A":"reject all automation","B":"distinguish consistency from fairness","C":"prove humans are unbiased","D":"describe programming languages"}, "B", "作者限定了“稳定一致”的积极含义，指出一致不等于公平。"),
    ("Researchers found that people remembered a route better when they actively chose each turn than when a navigation app directed them. The study did not claim that navigation apps always harm memory.", "What caution does the passage emphasize?", {"A":"The finding applies to every use of navigation","B":"The study supports a limited, not universal, conclusion","C":"Route choice never affects memory","D":"Navigation apps should be banned"}, "B", "末句明确限制了结论的适用范围。"),
    ("A city planted trees in its hottest neighborhoods. Surface temperatures fell near mature trees, but the effect was smaller on wide roads with heavy traffic.", "The passage suggests that tree planting—", {"A":"has identical effects everywhere","B":"can help but its effect depends on local conditions","C":"raises road temperatures","D":"works only without traffic"}, "B", "树木有降温作用，但效果受道路和交通等局部条件影响。"),
    ("Remote meetings reduce travel time. They can also make informal conversation harder, especially for new team members who have not yet built personal connections.", "The author presents remote meetings as—", {"A":"entirely harmful","B":"a trade-off with both benefits and costs","C":"useful only to new staff","D":"a complete replacement for offices"}, "B", "文本同时给出节省时间的收益与沟通成本。"),
    ("A hospital shortened appointment forms. Completion rates improved most among first-time patients, while returning patients showed little change.", "Which group benefited most?", {"A":"Returning patients","B":"First-time patients","C":"Hospital managers","D":"No group"}, "B", "材料直接说明首次就诊者改善最大。"),
    ("A company published salary ranges in job advertisements. Applications increased, but the share of qualified applicants remained stable.", "What can be inferred?", {"A":"Every applicant was qualified","B":"Transparency attracted more applications without changing the qualified share","C":"Salary ranges reduced interest","D":"Hiring standards were removed"}, "B", "申请数量增加，而合格比例稳定。"),
    ("Some failures are informative because they reveal which assumptions were wrong. This does not mean that organizations should ignore avoidable mistakes.", "The author distinguishes between—", {"A":"useful learning and careless error","B":"success and all forms of failure","C":"research and management","D":"rules and assumptions"}, "A", "作者肯定可产生学习的失败，同时反对可避免的疏忽。"),
    ("A school replaced one large exam with several smaller assessments. Average scores changed little, but students reported less anxiety before each test.", "The change primarily affected—", {"A":"reported anxiety","B":"average achievement dramatically","C":"course content","D":"class size"}, "A", "成绩变化不大，明显变化是单次考试前焦虑下降。"),
    ("An online store added detailed repair guides. Product returns declined for simple faults, while returns for major defects were unchanged.", "The guides were most useful for—", {"A":"major defects","B":"simple faults","C":"all returns equally","D":"preventing purchases"}, "B", "退货减少只出现在简单故障。"),
    ("A transit agency made real-time arrival data public. Independent developers then created accessibility tools the agency had not planned.", "The example illustrates how open data can—", {"A":"eliminate public agencies","B":"enable unanticipated services","C":"guarantee accurate predictions","D":"reduce accessibility"}, "B", "开发者创造了机构原先未规划的新工具。"),
]
for subject in ("英语一", "英语二"):
    prefix = "e1g" if subject == "英语一" else "e2g"
    for cycle in range(1):
        for i, (stem, options, answer, explanation) in enumerate(cloze_bank):
            lead = "Choose the best answer. " if cycle == 0 else "In formal written English, choose the best answer. "
            add(f"{prefix}c{cycle}{i:02d}", subject, "英语知识运用", 2 + (i + cycle) % 3, "single", lead + stem, options, answer, 0.5, explanation, format_tag="完形/词汇专项 · 每题0.5分")
    for cycle in range(1):
        for i, (passage, question, options, answer, explanation) in enumerate(reading_bank):
            add(f"{prefix}r{cycle}{i:02d}", subject, "阅读理解A", 2 + (i + cycle) % 3, "single", f"{passage}\n\n{question}", options, answer, 2, explanation, format_tag="阅读理解专项 · 每题2分")


# ------------------------- 数学一 / 二 / 三 -------------------------
def add_common_math(subject: str, prefix: str, include_probability: bool):
    chapter = "高等数学" if subject != "数学三" else "微积分"
    for i in range(12):
        a, b, x0 = i % 4 + 1, (i * 3) % 7 - 3, i % 3
        correct = 2 * a * x0 + b
        options, answer = optionize(correct, [correct + 1, correct - 2, a * x0 + b], i)
        add(f"{prefix}d{i:02d}", subject, chapter, 2 + i % 3, "single", f"设 f(x)={a}x²{b:+d}x+1，则 f'({x0})=", options, answer, 5, f"f'(x)={2*a}x{b:+d}，代入 x={x0} 得 {correct}。", format_tag="选择题专项 · 每题5分")
    for i in range(10):
        k, n = 2 * (i % 4 + 1), i % 3 + 1
        correct = k * n * n // 2
        options, answer = optionize(correct, [correct + n, correct + k, max(0, correct - n)], i + 1)
        add(f"{prefix}i{i:02d}", subject, chapter, 2 + i % 3, "single", f"定积分 ∫₀^{n} {k}x dx 等于", options, answer, 5, f"原函数为 {k//2}x²，代入上下限得 {correct}。", format_tag="选择题专项 · 每题5分")
    for i in range(10):
        a, b, c = i % 4 + 1, i % 5 + 1, i % 3 + 1
        correct = (a * b * c) ** 2
        options, answer = optionize(correct, [a*b*c, correct + 1, max(0, correct - a*b*c)], i + 2)
        add(f"{prefix}l{i:02d}", subject, "线性代数", 2 + i % 3, "single", f"三阶对角矩阵 A 的对角元为 {a}、{b}、{c}，则 det(A²)=", options, answer, 5, f"det(A)={a*b*c}，所以 det(A²)=det(A)²={correct}。", format_tag="选择题专项 · 每题5分")
    if include_probability:
        for i in range(10):
            vx, vy, coefficient = i % 4 + 1, i % 3 + 1, i % 3 + 1
            correct = coefficient * coefficient * vx + vy
            options, answer = optionize(correct, [coefficient*vx+vy, correct+vx, max(0, correct-vy)], i + 3)
            add(f"{prefix}p{i:02d}", subject, "概率论与数理统计", 2 + i % 3, "single", f"若 X、Y 独立，D(X)={vx}，D(Y)={vy}，则 D({coefficient}X-Y)=", options, answer, 5, f"独立时方差可加，D({coefficient}X-Y)={coefficient}²D(X)+D(Y)={correct}。", format_tag="选择题专项 · 每题5分")
    else:
        for i in range(10):
            n = i + 1
            correct = n
            options, answer = optionize(correct, [n+1, n*n, 0], i + 3)
            add(f"{prefix}h{i:02d}", subject, chapter, 2 + i % 3, "single", f"极限 lim(x→0) sin({n}x)/x 等于", options, answer, 5, f"利用 sin u/u→1，原式={n}。", format_tag="选择题专项 · 每题5分")


add_common_math("数学一", "gm1", True)
add_common_math("数学二", "gm2", False)
add_common_math("数学三", "gm3", True)


# ------------------------- 408 计算机 -------------------------
computer_concepts = [
    ("数据结构", "对长度为 n 的有序顺序表进行二分查找，最坏时间复杂度为", {"A":"O(1)","B":"O(log n)","C":"O(n)","D":"O(n log n)"}, "B", "二分查找每次将候选区间缩小约一半。"),
    ("数据结构", "采用邻接矩阵存储含 n 个顶点的无向图，判断两个给定顶点是否相邻的时间复杂度为", {"A":"O(1)","B":"O(log n)","C":"O(n)","D":"O(n²)"}, "A", "直接访问矩阵对应元素即可。"),
    ("数据结构", "在只允许从一端插入、从另一端删除的线性结构中，数据遵循", {"A":"后进先出","B":"先进先出","C":"随机访问","D":"按关键字有序"}, "B", "队列遵循先进先出原则。"),
    ("计算机组成原理", "32位地址、按字节编址的系统，其理论最大地址空间为", {"A":"2 GiB","B":"4 GiB","C":"8 GiB","D":"32 GiB"}, "B", "2³²个字节等于4 GiB。"),
    ("计算机组成原理", "提高 Cache 命中率通常能够直接降低", {"A":"平均存储访问时间","B":"指令条数","C":"磁盘容量","D":"进程数量"}, "A", "更多访问在高速缓存中完成会降低平均访问时间。"),
    ("计算机组成原理", "补码加减运算中，判断有符号数溢出主要依据", {"A":"最高位进位是否为1","B":"两个同号数相加结果是否异号","C":"结果是否为0","D":"操作数位数是否相同"}, "B", "同号数相加得到异号结果时发生溢出。"),
    ("操作系统", "运行进程主动请求尚未完成的 I/O 后，通常转入", {"A":"就绪态","B":"阻塞态","C":"终止态","D":"创建态"}, "B", "进程等待I/O事件完成时进入阻塞态。"),
    ("操作系统", "时间片用完但进程尚未结束时，该进程通常从运行态转入", {"A":"就绪态","B":"阻塞态","C":"终止态","D":"挂起态"}, "A", "时间片耗尽后等待再次调度，进入就绪态。"),
    ("操作系统", "虚拟存储器的容量主要受限于", {"A":"地址空间和外存容量","B":"CPU主频","C":"显示器分辨率","D":"网络带宽"}, "A", "虚拟地址空间与可用外存共同约束虚拟存储容量。"),
    ("计算机网络", "TCP 建立连接通常使用", {"A":"一次握手","B":"两次握手","C":"三次握手","D":"四次握手"}, "C", "TCP三次握手用于同步初始序号并确认双方收发能力。"),
    ("计算机网络", "IPv4 /24 网络在传统用法下可分配给主机的地址数为", {"A":"254","B":"255","C":"256","D":"510"}, "A", "8位主机号共256个地址，扣除网络地址和广播地址。"),
    ("计算机网络", "路由器转发 IP 分组时主要依据", {"A":"目的IP地址","B":"源MAC地址","C":"应用进程名称","D":"文件扩展名"}, "A", "IP层路由转发查找目的IP地址的最长前缀匹配。"),
]
for cycle in range(1):
    for i, (chapter, stem, options, answer, explanation) in enumerate(computer_concepts):
        lead = ["请选择正确结论：", "在典型实现中，", "不考虑特殊扩展时，"][cycle]
        add(f"gc{cycle}{i:02d}", "计算机学科专业基础", chapter, 2 + (cycle + i) % 3, "single", lead + stem, options, answer, 2, explanation, format_tag="408选择题专项 · 每题2分")
for i in range(16):
    cache, memory, hit = 1 + i % 3, 40 + (i % 5) * 10, 90 + i % 6
    correct = cache + (100-hit) * memory / 100
    options, answer = optionize(correct, [cache + memory, memory * hit / 100, cache + (100-hit)], i, lambda x: f"{x:g} ns")
    add(f"gcn{i:02d}", "计算机学科专业基础", "计算机组成原理", 3 + i % 2, "single", f"Cache命中时间{cache} ns、主存访问时间{memory} ns、命中率{hit}%，先查Cache且未命中再访主存，平均访问时间约为", options, answer, 2, f"平均时间={cache}+(1-{hit/100:.2f})×{memory}={correct:g} ns。", format_tag="408计算专项 · 每题2分")


# ------------------------- 199 管理类综合能力（MBA） -------------------------
for i in range(24):
    cost = 80 + i * 20
    markup = 20 + (i % 4) * 10
    discount = [80, 85, 90, 95][i % 4]
    correct = cost * (100 + markup) * discount // 10000
    options, answer = optionize(correct, [cost*(100+markup)//100, cost*discount//100, correct+10], i)
    add(f"mba_ps{i:02d}", "管理类综合能力", "数学基础·问题求解", 2 + i % 3, "single", f"某商品成本为{cost}元，按成本加价{markup}%标价，再按标价的{discount}%出售，售价为多少元？", options, answer, 3, f"售价={cost}×(1+{markup}%)×{discount}%={correct}元。", format_tag="199问题求解 · 15题×3分")
for i in range(16):
    first = 20 + i
    count = 5 + i % 4
    last = first + count - 1
    correct = (first + last) * count // 2
    options, answer = optionize(correct, [first*count, last*count, correct+count], i + 1)
    add(f"mba_seq{i:02d}", "管理类综合能力", "数学基础·问题求解", 2 + i % 3, "single", f"连续{count}个整数从{first}开始，它们的和为", options, answer, 3, f"等差数列求和：({first}+{last})×{count}÷2={correct}。", format_tag="199问题求解 · 15题×3分")

cs_options = {"A":"条件（1）充分，但条件（2）不充分","B":"条件（2）充分，但条件（1）不充分","C":"条件（1）和（2）单独都充分","D":"条件（1）和（2）联合充分，但单独都不充分","E":"条件（1）和（2）联合仍不充分"}
for i in range(25):
    x, y = i % 7 + 2, i % 5 + 1
    mode = i % 5
    if mode == 0:
        stem, answer, exp = f"能否确定实数x的值？\n（1）x={x}\n（2）y={y}", "A", "条件（1）直接确定x；条件（2）与x无关。"
    elif mode == 1:
        stem, answer, exp = f"能否确定实数x的值？\n（1）y={y}\n（2）x={x}", "B", "条件（2）直接确定x；条件（1）与x无关。"
    elif mode == 2:
        stem, answer, exp = f"能否确定实数x的值？\n（1）x={x}\n（2）2x={2*x}", "C", "两个条件单独都能确定x。"
    elif mode == 3:
        stem, answer, exp = f"能否确定实数x的值？\n（1）x+y={x+y}\n（2）y={y}", "D", "任一条件单独都不能确定x，联合可得x。"
    else:
        lower = 2 + i // 5
        upper = 10 + i // 5
        stem, answer, exp = f"能否确定正整数x的值？\n（1）x>{lower}\n（2）x<{upper}", "E", f"联合只能把x限制在{lower+1}至{upper-1}中的多个正整数，仍不能唯一确定。"
    add(f"mba_cs{i:02d}", "管理类综合能力", "数学基础·条件充分性判断", 3 + i % 2, "single", stem, cs_options, answer, 3, exp, format_tag="199条件充分性判断 · 10题×3分")

logic_bank = [
    ("所有完成安全培训的员工都可进入实验区。小周不能进入实验区。以下必然成立的是", {"A":"小周未完成安全培训","B":"小周不是员工","C":"小周完成了培训但忘带证件","D":"无人可进入实验区"}, "A", "由“完成培训→可进入”及“不能进入”，按逆否推理得未完成培训。"),
    ("如果项目延期，则预算需要重估。预算没有重估。由此可以推出", {"A":"项目没有延期","B":"项目一定提前","C":"预算一定增加","D":"无法判断项目是否启动"}, "A", "P→Q且非Q，可推出非P。"),
    ("某产品销量上升后，公司断言广告必然有效。以下最能削弱该断言的是", {"A":"同期主要竞争对手退出市场","B":"广告画面受到好评","C":"公司增加了广告预算","D":"销量数据按月统计"}, "A", "竞争对手退出提供了销量上升的替代原因。"),
    ("调查发现使用健身应用者平均运动更多，研究者据此认为应用使人增加运动。以下最需要排除的是", {"A":"本来爱运动的人更愿意使用健身应用","B":"应用有多种颜色","C":"不同手机品牌价格不同","D":"运动场所有开放时间"}, "A", "自选择偏差可能同时解释应用使用与运动量。"),
    ("只有获得许可，车辆才能进入园区。甲车进入了园区。可以推出", {"A":"甲车获得了许可","B":"所有获许可车辆都已进入","C":"甲车没有驾驶员","D":"园区没有其他车辆"}, "A", "“只有P才Q”等价于Q→P，进入园区可推出获得许可。"),
    ("五人排队，甲必须在乙前，丙必须在丁后。以下哪项可能成立？", {"A":"乙、甲、丙、丁、戊","B":"甲、乙、丁、丙、戊","C":"丙、丁、甲、乙、戊","D":"丁、丙、乙、甲、戊"}, "B", "B同时满足甲在乙前、丙在丁后。"),
    ("某餐厅推出低价套餐后客流增加，经理认为降价必然提高利润。以下最能指出论证漏洞的是", {"A":"客流增加不等于总利润增加，还需考虑毛利和成本","B":"套餐菜单采用彩色印刷","C":"餐厅位于一楼","D":"经理工作时间较长"}, "A", "论证把客流增加直接等同于利润增加，忽略单位利润和成本。"),
    ("某市增设自行车道后骑行人数增加。以下最能加强“自行车道促进骑行”的结论的是", {"A":"同期天气、油价和公共交通价格基本稳定","B":"自行车颜色变多","C":"城市人口略有变化","D":"部分道路正在维修"}, "A", "排除主要替代解释可增强因果推断。"),
    ("所有A类文件都需复核，有些需复核的文件是电子文件。以下不能必然推出的是", {"A":"有些电子文件是A类文件","B":"所有A类文件都需复核","C":"有些电子文件需复核","D":"可能存在非A类的需复核文件"}, "A", "两个集合都与“需复核”有交集，不代表A类与电子文件必有交集。"),
    ("甲、乙、丙三项任务中，甲既不能与乙同日，也不能与丙同日；乙与丙可以同日。若必须有两项同日，则同日的是", {"A":"甲和乙","B":"乙和丙","C":"甲和丙","D":"无法确定"}, "B", "甲不能与另外两项同日，因此必须同日的是乙和丙。"),
]
for cycle in range(1):
    for i, (stem, options, answer, explanation) in enumerate(logic_bank):
        add(f"mba_l{cycle}{i:02d}", "管理类综合能力", "逻辑推理", 2 + (cycle + i) % 3, "single", stem, options, answer, 2, explanation, format_tag="199逻辑推理 · 30题×2分")

conditional_pairs = [
    ("审计通过", "许可证获批"), ("温度低于零度", "路面结冰预警启动"), ("订单完成复核", "货物可以出库"),
    ("项目通过验收", "尾款可以支付"), ("用户完成实名认证", "账户可以提现"), ("设备通过自检", "生产线可以启动"),
    ("申请材料齐全", "窗口受理申请"), ("航班获得放行", "飞机可以起飞"), ("论文通过查重", "进入送审环节"),
    ("预算获得批准", "采购流程启动"), ("水质达到标准", "水源恢复供应"), ("候选人通过背景核验", "发出正式录用通知"),
    ("系统完成备份", "执行版本升级"), ("样品通过稳定性测试", "进入量产评估"), ("合同完成法务审核", "双方正式签署"),
]
for i, (premise, consequence) in enumerate(conditional_pairs):
    correct = f"{premise}没有发生"
    options, answer = optionize(correct, [f"{consequence}一定发生", f"{premise}与{consequence}同时发生", "无法得到任何结论"], i)
    add(f"mba_cond{i:02d}", "管理类综合能力", "逻辑推理", 2 + i % 3, "single", f"如果{premise}，那么{consequence}。现已知“{consequence}”没有发生。以下必然成立的是", options, answer, 2, "P→Q且非Q，根据逆否规则可推出非P。", format_tag="199逻辑推理 · 条件推理")

necessary_pairs = [
    ("完成伦理审查", "开展人体试验"), ("持有有效票证", "进入会场"), ("获得数据授权", "下载完整数据集"),
    ("通过资格审核", "参加面试"), ("取得施工许可", "开始主体施工"), ("完成安全培训", "进入高风险作业区"),
    ("董事会批准", "实施重大资产处置"), ("监护人签字", "未成年人参加活动"), ("完成身份核验", "领取重要文件"),
    ("满足最低资本要求", "获准开展该项业务"),
]
for i, (necessary, action) in enumerate(necessary_pairs):
    correct = f"已经{necessary}"
    options, answer = optionize(correct, [f"所有已经{necessary}的人都已{action}", f"未{action}", "无法判断是否满足任何条件"], i + 1)
    add(f"mba_nec{i:02d}", "管理类综合能力", "逻辑推理", 2 + i % 3, "single", f"只有{necessary}，才能{action}。已知某对象已经{action}，可以推出", options, answer, 2, "“只有P才Q”等价于Q→P，Q成立可推出P成立。", format_tag="199逻辑推理 · 必要条件")

causal_cases = [
    ("门店更换招牌后客流上升", "新招牌提升了客流", "同期地铁新出口在门店旁启用"),
    ("公司启用新考勤系统后迟到减少", "新系统改善了纪律", "同期公司把上班时间推迟了半小时"),
    ("学校增加晚自习后平均分提高", "晚自习提高了成绩", "本学期试卷难度明显低于上学期"),
    ("社区增设摄像头后报案数量下降", "摄像头减少了犯罪", "居民转而通过其他平台报案"),
    ("应用改版后日活跃用户增加", "新版界面提高了活跃度", "同期推出了高额签到奖励"),
    ("餐厅增加素食菜单后利润上升", "素食菜单提高了利润", "同期租金获得大幅减免"),
    ("城市提高停车费后拥堵下降", "停车费抑制了驾车需求", "同期一条主要道路长期封闭施工"),
    ("企业采用开放办公区后协作评价上升", "开放空间促进了协作", "评价问卷同时更换了评分尺度"),
    ("医院上线预约提醒后爽约率下降", "提醒减少了爽约", "同期取消预约的操作也被简化"),
    ("平台增加评论审核后投诉减少", "审核提高了内容质量", "投诉入口同时被移到更深层页面"),
    ("工厂调整照明后产量增加", "照明改善提高了产量", "同期新增了一条自动化生产线"),
    ("图书馆延长开放时间后借阅增加", "延时开放促进了借阅", "同期取消了逾期罚款"),
    ("商场举行艺术展后销售额增长", "艺术展带动了消费", "同期正值大型节假日促销"),
    ("团队采用站立会议后项目周期缩短", "站立会议提高了效率", "项目范围同时被大幅缩减"),
    ("网站启用深色模式后停留时长增加", "深色模式增强了用户黏性", "统计口径同时由中位数改为平均数"),
]
for i, (evidence, claim, alternative) in enumerate(causal_cases):
    correct = alternative
    options, answer = optionize(correct, ["该变化受到部分用户好评", "研究记录了变化发生的日期", "样本来自实际业务场景"], i + 2)
    add(f"mba_cause{i:02d}", "管理类综合能力", "逻辑推理", 3 + i % 2, "single", f"观察到“{evidence}”，研究者据此认为“{claim}”。以下哪项最能削弱该结论？", options, answer, 2, "该选项提供了结果变化的有力替代原因，削弱了题干的因果归因。", format_tag="199逻辑推理 · 论证评价")

writing_prompts = [
    ("论证有效性分析", 30, "某企业认为：凡是采用远程办公的部门成本都下降，因此只要全面取消办公室，公司利润必然大幅增长。", "检查样本范围、成本与利润的概念差异、取消办公室的新增成本，以及相关关系能否推出因果。"),
    ("论证有效性分析", 30, "调查显示高绩效员工更常参加培训，所以增加强制培训次数必然使所有员工达到高绩效。", "检查自选择、反向因果、培训质量与次数的差异，以及从平均趋势到所有个体的过度概括。"),
    ("论证有效性分析", 30, "某商店延长营业时间后销售额上升，据此认为延长到24小时营业一定能继续同比例增加利润。", "检查同期因素、销售额与利润差异、边际收益递减以及夜间成本。"),
    ("论证有效性分析", 30, "一家工厂引入自动化设备后次品率下降，因此任何工厂购买同型号设备都能消除质量问题。", "检查实施条件、人员培训、原料与流程差异，以及“下降”到“消除”的结论跳跃。"),
    ("论证有效性分析", 30, "某城市共享单车投放量增加后拥堵缓解，所以继续无限增加投放就能彻底解决拥堵。", "检查相关与因果、其他交通政策、边际效应、过量投放的负面影响。"),
    ("论说文", 35, "有人说，管理的价值在于减少不确定性；也有人认为，过度追求确定性会压制创新。请据此写一篇论说文。", "可围绕规则与试验的边界建立中心论点，用条件化观点避免二元对立。"),
    ("论说文", 35, "一家企业允许员工用20%的工作时间探索自主项目。请讨论组织效率与长期创新之间的关系。", "可从短期机会成本、长期学习收益、筛选机制和评价周期展开论证。"),
    ("论说文", 35, "材料：真正的合作不是所有人意见一致，而是在分歧中形成可执行的共同方案。", "可区分一致、服从与协作，讨论程序、信息和责任对合作质量的影响。"),
    ("论说文", 35, "请以“速度与质量”为主题，结合组织决策写一篇论说文。", "可论证时间压力下最低质量标准、可逆决策与不可逆决策应采用不同速度。"),
    ("论说文", 35, "材料：衡量什么，往往就会得到什么；但不是所有重要的事都容易衡量。", "可讨论指标的激励作用、替代效应与定量指标和专业判断的结合。"),
]
for i, (chapter, points, prompt, guide) in enumerate(writing_prompts):
    add(f"mba_w{i:02d}", "管理类综合能力", f"写作·{chapter}", 4, "essay", prompt, {}, guide, points, guide, format_tag=f"199写作 · {points}分 · 人工自评")


# ------------------------- 校验并输出 -------------------------
ids = [q["id"] for q in questions]
if len(ids) != len(set(ids)):
    duplicates = sorted({qid for qid in ids if ids.count(qid) > 1})
    raise ValueError(f"题目ID重复: {duplicates}")
for q in questions:
    if q["type"] in {"single", "multiple"}:
        if not q["options"]:
            raise ValueError(f"客观题缺少选项: {q['id']}")
        answers = q["answer"] if isinstance(q["answer"], list) else [q["answer"]]
        if any(answer not in q["options"] for answer in answers):
            raise ValueError(f"答案不在选项中: {q['id']}")

with TARGET.open("w", encoding="utf-8", newline="\n") as handle:
    json.dump(questions, handle, ensure_ascii=False, indent=2)
    handle.write("\n")

counts = {}
for q in questions:
    counts[q["subject"]] = counts.get(q["subject"], 0) + 1
print(json.dumps({"total": len(questions), "subjects": counts}, ensure_ascii=False, indent=2))

