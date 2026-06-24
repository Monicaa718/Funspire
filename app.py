import json
from pathlib import Path
import streamlit as st

st.set_page_config(
    page_title="Funspire Demo",
    page_icon="🎬",
    layout="wide"
)

RULE_PATH = Path("data/rules_expert_na.json")


def load_rules():
    if not RULE_PATH.exists():
        return []
    with open(RULE_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def match_rules(script, market, genre, rules):
    matched = []

    for rule in rules:
        rule_market = rule.get("market", "")
        rule_genre = rule.get("genre", "")
        keywords = rule.get("trigger_keywords", [])

        market_ok = rule_market == market
        genre_ok = rule_genre == genre or rule_genre == "通用"

        if not market_ok or not genre_ok:
            continue

        hit_keywords = [kw for kw in keywords if kw in script]

        if hit_keywords:
            item = rule.copy()
            item["hit_keywords"] = hit_keywords
            matched.append(item)

    return matched


def calculate_scores(matched_rules, script):
    cultural_score = 100
    compliance_score = 100
    hook_score = 50

    strong_hook_words = [
        "曝光", "背叛", "继承", "婚约", "债务", "秘密",
        "复仇", "威胁", "解雇", "协议", "取消婚礼",
        "信托", "董事会", "股权", "遗嘱"
    ]

    hook_hits = [word for word in strong_hook_words if word in script]
    hook_score = min(100, hook_score + len(hook_hits) * 8)

    for rule in matched_rules:
        severity = rule.get("severity", "medium")
        category = rule.get("category", "")

        if severity == "high":
            cultural_score -= 18
        elif severity == "medium":
            cultural_score -= 10
        else:
            cultural_score -= 5

        if category == "合规风险":
            if severity == "high":
                compliance_score -= 25
            elif severity == "medium":
                compliance_score -= 15
            else:
                compliance_score -= 8

    return max(0, cultural_score), hook_score, max(0, compliance_score)


def level_text(score):
    if score >= 80:
        return "较好"
    if score >= 60:
        return "需要优化"
    return "风险较高"


def generate_simple_rewrite(matched_rules):
    if not matched_rules:
        return "当前版本暂未命中强风险规则。建议继续强化前三秒冲突、人物主动性和集尾钩子。"

    lines = []
    lines.append("【中文优化方向】")
    for rule in matched_rules:
        lines.append(f"- {rule.get('suggestion')}")
        lines.append(f"  参考改法：{rule.get('example_after')}")

    lines.append("")
    lines.append("【英文本土化方向】")
    lines.append("The scene should be adapted around contract pressure, inheritance conflict, reputation risk, or career stakes rather than direct family hierarchy.")
    lines.append("The heroine should react with evidence, negotiation, or strategic counterattack instead of passive endurance.")

    return "\n".join(lines)


def generate_simple_report(script, market, language, genre, matched_rules, cultural_score, hook_score, compliance_score):
    lines = []
    lines.append("# Funspire 北美短剧文化适配诊断报告")
    lines.append("")
    lines.append(f"目标市场：{market}")
    lines.append(f"输出语言：{language}")
    lines.append(f"题材：{genre}")
    lines.append("")
    lines.append("## 评分")
    lines.append(f"- 文化适配分：{cultural_score}/100")
    lines.append(f"- 商业钩子分：{hook_score}/100")
    lines.append(f"- 合规安全分：{compliance_score}/100")
    lines.append("")
    lines.append("## 命中问题")

    if not matched_rules:
        lines.append("暂未命中明显文化适配问题。")
    else:
        for rule in matched_rules:
            lines.append(f"### {rule.get('rule_id')}｜{rule.get('category')}")
            lines.append(f"命中关键词：{', '.join(rule.get('hit_keywords', []))}")
            lines.append(f"问题：{rule.get('problem')}")
            lines.append(f"原因：{rule.get('reason')}")
            lines.append(f"修改建议：{rule.get('suggestion')}")
            lines.append(f"参考改法：{rule.get('example_after')}")
            lines.append(f"来源：{rule.get('source')}")
            lines.append("")

    lines.append("## 初步改写方向")
    lines.append(generate_simple_rewrite(matched_rules))
    lines.append("")
    lines.append("## 原始剧本")
    lines.append(script)

    return "\n".join(lines)


st.markdown(
    """
    <style>
    .main-title {
        font-size: 42px;
        font-weight: 800;
        margin-bottom: 0px;
    }
    .subtitle {
        font-size: 18px;
        color: #666;
        margin-bottom: 25px;
    }
    .hero-box {
        padding: 24px;
        border-radius: 18px;
        background: linear-gradient(135deg, #f8f9ff 0%, #fff7f2 100%);
        border: 1px solid #eeeeee;
        margin-bottom: 20px;
    }
    .small-tag {
        display: inline-block;
        padding: 6px 10px;
        border-radius: 999px;
        background-color: #111827;
        color: white;
        font-size: 13px;
        margin-right: 8px;
    }
    .issue-card {
        padding: 18px;
        border-radius: 14px;
        border: 1px solid #eeeeee;
        background-color: #ffffff;
        margin-bottom: 14px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <div class="hero-box">
        <div class="small-tag">AI Agent</div>
        <div class="small-tag">OPC Demo</div>
        <div class="small-tag">短剧出海</div>
        <div class="main-title">Funspire：北美短剧文化适配诊断与改写 Agent</div>
        <div class="subtitle">
        输入中文短剧片段，系统识别文化适配问题，命中专家规则，并给出修改建议和初步改写方向。
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

rules = load_rules()

col_a, col_b, col_c = st.columns(3)
with col_a:
    market = st.selectbox("目标市场", ["北美"])
with col_b:
    language = st.selectbox("输出语言", ["中文+英文", "仅中文", "仅英文"])
with col_c:
    genre = st.selectbox("题材", ["CEO霸总", "豪门复仇", "狼人奇幻", "家庭伦理", "甜宠虐恋", "通用"])

st.caption(f"当前知识库规则数量：{len(rules)} 条。后续可直接替换 data/rules_expert_na.json 扩充专家规则。")

sample_script = """女主嫁入豪门后，婆婆当众羞辱她，说她出身低微，配不上自己的儿子。女主为了丈夫一直忍耐，甚至被要求下跪道歉。直到男主出现，才替她撑腰。"""

col1, col2 = st.columns([1, 1])

with col1:
    if st.button("加载示例剧本"):
        st.session_state["script"] = sample_script

with col2:
    if st.button("清空输入"):
        st.session_state["script"] = ""

script = st.text_area(
    "请粘贴中文短剧剧本",
    height=260,
    value=st.session_state.get("script", "")
)

if st.button("开始分析", type="primary"):
    if not script.strip():
        st.warning("请先输入剧本。")
    else:
        matched_rules = match_rules(script, market, genre, rules)
        cultural_score, hook_score, compliance_score = calculate_scores(matched_rules, script)

        st.divider()

        st.subheader("一、综合评分")

        s1, s2, s3, s4 = st.columns(4)
        s1.metric("文化适配分", f"{cultural_score}/100", level_text(cultural_score))
        s2.metric("商业钩子分", f"{hook_score}/100", level_text(hook_score))
        s3.metric("合规安全分", f"{compliance_score}/100", level_text(compliance_score))
        s4.metric("命中规则", f"{len(matched_rules)} 条")

        if cultural_score >= 80:
            st.success("整体文化适配较好，可以进入局部润色。")
        elif cultural_score >= 60:
            st.warning("有一定可用性，但需要重构部分冲突点。")
        else:
            st.error("文化适配风险较高，建议重写核心冲突。")

        tab1, tab2, tab3 = st.tabs(["命中问题", "改写方向", "导出报告"])

        with tab1:
            st.subheader("二、命中的文化适配问题")

            if not matched_rules:
                st.success("暂未命中明显文化适配问题。")
            else:
                for rule in matched_rules:
                    st.markdown(
                        f"""
                        <div class="issue-card">
                        <h4>{rule.get('rule_id')}｜{rule.get('category')}｜{rule.get('severity')}</h4>
                        <p><b>命中关键词：</b>{'、'.join(rule.get('hit_keywords', []))}</p>
                        <p><b>问题：</b>{rule.get('problem')}</p>
                        <p><b>原因：</b>{rule.get('reason')}</p>
                        <p><b>修改建议：</b>{rule.get('suggestion')}</p>
                        <p><b>参考改法：</b>{rule.get('example_after')}</p>
                        <p><b>来源：</b>{rule.get('source')}</p>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

        with tab2:
            st.subheader("三、初步改写方向")
            rewrite_text = generate_simple_rewrite(matched_rules)
            st.text_area("系统生成的改写方向", value=rewrite_text, height=260)

            st.info("当前版本是规则库诊断 Demo。下一步接入大模型后，这里会自动生成完整的中文优化版和英文本土化版。")

        with tab3:
            st.subheader("四、导出报告")
            report = generate_simple_report(
                script,
                market,
                language,
                genre,
                matched_rules,
                cultural_score,
                hook_score,
                compliance_score
            )

            st.download_button(
                label="下载诊断报告 Markdown",
                data=report,
                file_name="funspire_cultural_adaptation_report.md",
                mime="text/markdown"
            )

            with st.expander("预览报告内容"):
                st.markdown(report)