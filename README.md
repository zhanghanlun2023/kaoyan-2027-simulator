# 研途 · 2027 考研仿真题库

一个基于 Streamlit 的全国硕士研究生招生考试训练系统。覆盖思想政治理论、英语一/二、数学一/二/三与 408，提供原创仿真组卷、自动评分、章节诊断、2022—2026 五年真题索引和 2027 考纲状态提示。

> 截至 2026-08-21，全国统考科目的 2027 官方考试大纲尚未发布。本项目不会把预测内容标为官方考纲。

## 本地运行

```bash
python -m pip install -r requirements.txt
streamlit run app.py
```

## Streamlit Community Cloud 部署

1. 将本仓库设为 GitHub 公共仓库。
2. 登录 [Streamlit Community Cloud](https://share.streamlit.io/)，选择 **Create app**。
3. 选中本仓库、默认分支与入口文件 `app.py`，然后部署。

项目不需要密钥或数据库。`requirements.txt` 与 `.streamlit/config.toml` 已就绪。

## 内容边界

- 题库训练题均为原创仿真题，不是历年真题的逐字复制。
- `data/past_papers.json` 整理近五年年份、考试时间、复盘重点和工作流，不转载未经授权的整套试卷、参考答案或机构解析。
- 院校自命题科目差异极大，应以目标院校当年招生简章、专业目录和考试大纲为准。
- 当前为首个可运行版本，抽样小测分数不可直接外推到正式考试总分。

## 权威核验入口

- [教育部：2026年全国硕士研究生招生工作管理规定](https://www.moe.gov.cn/srcsite/A15/moe_778/s3261/202509/t20250918_1413836.html)
- [中国教育考试网：全国硕士研究生招生考试](https://yankao.neea.edu.cn/)
- [中国教育考试网：考试大纲](https://yankao.neea.edu.cn/xhtml1/category/1509/6235-1.htm)
- [中国研究生招生信息网](https://yz.chsi.com.cn/)

## 测试

```bash
python -m pytest -q
```

## 许可证

代码采用 MIT License；题库内容仅供学习与非商业使用，详见 `CONTENT_LICENSE.md`。

