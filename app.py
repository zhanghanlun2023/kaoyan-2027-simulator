from __future__ import annotations

import time
from datetime import date

import pandas as pd
import streamlit as st

from engine import build_paper, load_json, score_paper, stable_seed


st.set_page_config(
    page_title="研途 · 2027考研仿真题库",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
<style>
    .stApp { background: radial-gradient(circle at 95% 0%, #ffe5d8 0, transparent 25%), #f7f5f0; }
    [data-testid="stSidebar"] { background: #17212b; }
    [data-testid="stSidebar"] * { color: #f8fafc; }
    .hero { padding: 2.2rem 2.4rem; border-radius: 24px; color: white;
        background: linear-gradient(125deg,#14213d 0%,#25385c 64%,#e4572e 150%);
        box-shadow: 0 16px 40px rgba(20,33,61,.16); margin-bottom: 1.5rem; }
    .hero h1 { margin: 0 0 .45rem; font-size: clamp(2rem,4vw,3.6rem); letter-spacing:-.04em; }
    .hero p { margin: 0; max-width: 760px; color:#dbe4f0; font-size:1.05rem; }
    .eyebrow { color:#ffb199; text-transform:uppercase; letter-spacing:.16em; font-size:.75rem; font-weight:700; }
    .card { background:rgba(255,255,255,.8); border:1px solid rgba(31,42,55,.08); border-radius:18px;
        padding:1.2rem 1.3rem; min-height:132px; box-shadow:0 8px 28px rgba(31,42,55,.06); }
    .card h3 { margin:.2rem 0 .45rem; font-size:1.05rem; }
    .muted { color:#64748b; font-size:.9rem; }
    .pill { display:inline-block; border-radius:999px; background:#fce8df; color:#b43d1c;
        padding:.25rem .65rem; font-size:.78rem; font-weight:700; margin-right:.3rem; }
    .notice { padding:1rem 1.2rem; border-left:5px solid #e4572e; background:#fff5ef; border-radius:10px; }
    .question { background:#fff; padding:1.2rem 1.4rem; border-radius:16px; border:1px solid #e5e7eb; margin:.8rem 0; }
    .source { color:#64748b; font-size:.82rem; }
    footer { visibility:hidden; }
</style>
""",
    unsafe_allow_html=True,
)

questions = load_json("questions.json")
syllabus = load_json("syllabus.json")
papers = load_json("past_papers.json")
subjects = [s["name"] for s in syllabus["subjects"]]


def header(title: str, subtitle: str) -> None:
    st.markdown(f"## {title}")
    st.caption(subtitle)


with st.sidebar:
    st.markdown("## 研途 YANTU")
    st.caption("2027 考研仿真训练系统")
    page = st.radio("导航", ["备考总览", "智能组卷", "五年真题索引", "2027考纲雷达", "项目说明"], label_visibility="collapsed")
    st.divider()
    selected_subject = st.selectbox("当前科目", subjects)
    available = sum(q["subject"] == selected_subject for q in questions)
    st.caption(f"当前原创题量 · {available} 道")
    st.caption("知识状态 · 截至 2026-08-21")


if page == "备考总览":
    st.markdown(
        """
        <section class="hero">
          <div class="eyebrow">Postgraduate Entrance Exam · 2027</div>
          <h1>把每一次练习，<br>变成可解释的进步。</h1>
          <p>以五年真题结构为参照、以公开考纲为边界的原创仿真训练。先测能力，再定位章节，最后回到可执行的复习动作。</p>
        </section>
        """,
        unsafe_allow_html=True,
    )
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("覆盖统考科目", f"{len(subjects)} 门")
    c2.metric("原创仿真题", f"{len(questions)} 道")
    c3.metric("真题索引跨度", "5 年")
    c4.metric("考纲状态", "待官方发布")
    st.markdown("### 今天从哪里开始")
    cols = st.columns(3)
    cards = [
        ("01", "先看边界", "查看2027考纲雷达，区分官方信息、沿用基线与院校自命题调整。"),
        ("02", "再做诊断", f"从“{selected_subject}”抽取一组题，建议先做10—20分钟小测。"),
        ("03", "最后复盘", "按章节准确率定位薄弱点，把真题错因而不是整套试卷录入复习档案。"),
    ]
    for col, (no, title, text) in zip(cols, cards):
        col.markdown(f'<div class="card"><span class="pill">{no}</span><h3>{title}</h3><div class="muted">{text}</div></div>', unsafe_allow_html=True)
    st.markdown("### 科目地图")
    for idx in range(0, len(syllabus["subjects"]), 3):
        row = st.columns(3)
        for col, subject in zip(row, syllabus["subjects"][idx:idx+3]):
            count = sum(q["subject"] == subject["name"] for q in questions)
            col.markdown(
                f'<div class="card"><span class="pill">{subject["code"]}</span><h3>{subject["name"]}</h3>'
                f'<div class="muted">{subject["score"]}分 · {subject["minutes"]}分钟 · 当前{count}题</div></div>',
                unsafe_allow_html=True,
            )

elif page == "智能组卷":
    header("智能组卷", "同一日期、科目和配置会生成相同试卷，便于复盘与分享。")
    subject_questions = [q for q in questions if q["subject"] == selected_subject]
    chapters = sorted({q["chapter"] for q in subject_questions})
    with st.container(border=True):
        c1, c2, c3 = st.columns([2, 2, 1])
        chosen_chapters = c1.multiselect("章节范围", chapters, default=chapters)
        max_count = max(1, sum(q["chapter"] in chosen_chapters for q in subject_questions))
        count = c2.slider("题目数量", 1, max_count, min(8, max_count))
        version = c3.number_input("试卷版本", min_value=1, max_value=999, value=1)
        start = st.button("生成 / 重置试卷", type="primary", width="stretch")

    config = (selected_subject, tuple(chosen_chapters), count, int(version))
    if start or st.session_state.get("paper_config") != config:
        seed = stable_seed(date.today().isoformat(), *config)
        st.session_state.paper = build_paper(questions, selected_subject, count, seed, chosen_chapters)
        st.session_state.paper_config = config
        st.session_state.paper_started = time.time()
        st.session_state.pop("result", None)

    paper = st.session_state.get("paper", [])
    if not paper:
        st.info("当前筛选没有可用题目，请重新选择章节。")
    else:
        elapsed = int(time.time() - st.session_state.get("paper_started", time.time()))
        points = sum(q["points"] for q in paper)
        st.caption(f"试卷编号 {stable_seed(*config) % 100000:05d} · {len(paper)}题 · {points}分 · 已用时 {elapsed//60:02d}:{elapsed%60:02d}")
        answers = {}
        with st.form("exam_form"):
            for number, q in enumerate(paper, 1):
                st.markdown(f"#### {number}. {q['stem']}  `{q['points']}分`")
                opts = [f"{key}. {value}" for key, value in q["options"].items()]
                if q["type"] == "multiple":
                    raw = st.multiselect("请选择所有正确选项", opts, key=f"ans_{q['id']}")
                    answers[q["id"]] = [item.split(".", 1)[0] for item in raw]
                else:
                    raw = st.radio("请选择一项", ["未作答"] + opts, key=f"ans_{q['id']}", horizontal=True)
                    answers[q["id"]] = None if raw == "未作答" else raw.split(".", 1)[0]
                st.caption(f"{q['chapter']} · 难度 {'●' * q['difficulty']}{'○' * (5-q['difficulty'])}")
                st.divider()
            submitted = st.form_submit_button("交卷并生成诊断", type="primary", width="stretch")
        if submitted:
            st.session_state.result = score_paper(paper, answers)

        result = st.session_state.get("result")
        if result:
            st.markdown("### 本次诊断")
            a, b, c = st.columns(3)
            a.metric("得分", f"{result['earned']} / {result['possible']}")
            b.metric("正确率", f"{result['accuracy']:.0%}")
            c.metric("建议", "进入错题复盘" if result["accuracy"] < .8 else "提高难度")
            stats = pd.DataFrame([
                {"章节": chapter, "正确": stat["correct"], "总题数": stat["total"], "正确率": stat["correct"] / stat["total"]}
                for chapter, stat in result["chapter_stats"].items()
            ]).set_index("章节")
            st.bar_chart(stats["正确率"], horizontal=True)
            for i, detail in enumerate(result["details"], 1):
                q = detail["question"]
                icon = "✅" if detail["correct"] else "❌"
                with st.expander(f"{icon} 第{i}题 · {q['chapter']}"):
                    st.write(q["stem"])
                    st.write(f"你的答案：{detail['actual'] or '未作答'}")
                    st.write(f"正确答案：{q['answer']}")
                    st.info(q["explanation"])
                    st.caption(q["source"])

elif page == "五年真题索引":
    header("2022—2026 五年真题索引", "整理的是结构、年份、复盘方法和合法获取路径，不直接转载未经授权的整套试卷。")
    st.markdown(f'<div class="notice">{papers["copyright_note"]}</div>', unsafe_allow_html=True)
    st.write("")
    year_df = pd.DataFrame(papers["years"]).rename(columns={"year":"年度", "exam_date":"考试时间", "status":"状态", "focus":"复盘重点"})
    st.dataframe(year_df, width="stretch", hide_index=True)
    st.markdown("### 推荐复盘流程")
    for i, step in enumerate(papers["workflow"], 1):
        st.markdown(f"**{i:02d}**　{step}")
    st.markdown("### 各科录入模板")
    template = pd.DataFrame([
        {"年份": y, "科目": selected_subject, "题号": "", "考点": "", "错因": "概念/计算/审题/时间", "耗时(分钟)": ""}
        for y in range(2022, 2027)
    ])
    st.dataframe(template, width="stretch", hide_index=True)
    st.download_button("下载错题索引 CSV", template.to_csv(index=False).encode("utf-8-sig"), f"{selected_subject}_五年真题复盘.csv", "text/csv")

elif page == "2027考纲雷达":
    header("2027 考纲雷达", "先识别信息状态，再决定复习范围。")
    status = syllabus["status"]
    st.warning(f"截至 {status['as_of']}：{status['message']}")
    for subject in syllabus["subjects"]:
        with st.expander(f"{subject['code']} · {subject['name']}　{subject['score']}分 / {subject['minutes']}分钟", expanded=subject["name"] == selected_subject):
            st.write(" · ".join(subject["sections"]))
            st.caption(subject["note"])
    st.markdown("### 官方核验入口")
    for source in syllabus["sources"]:
        st.markdown(f"- [{source['title']}]({source['url']}) — {source['role']}")
    st.info("正式大纲发布后，应对科目代码、题型结构、内容范围和院校自命题要求逐项复核。本项目不会把培训机构预测标成官方考纲。")

else:
    header("项目说明", "一套可公开部署、可继续扩充的考研训练底座。")
    st.markdown(
        """
### 数据原则

- 训练题均标注“原创仿真”，不是历年真题的逐字复制。
- 五年真题模块保存结构化索引和个人错因，不把来源不明的整套试卷打包传播。
- 2027 全国统考考纲未正式发布时，页面明确显示“待官方发布”。

### 当前版本边界

这是首个可运行版本，覆盖 7 门通用统考科目。政治主观题、英语作文自动批改、数学/408完整大题以及院校自命题专业课仍需后续扩充；当前分数只代表抽样小测，不可直接外推到正式考试总分。
        """
    )
    st.markdown("### 技术与反馈")
    st.code("streamlit run app.py", language="bash")
    st.caption("建议通过 GitHub Issues 提交错题、勘误和新增科目需求。")
