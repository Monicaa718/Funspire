import json
from pathlib import Path
from collections import Counter
import streamlit as st

st.set_page_config(page_title="Funspire Agent", page_icon="🎬", layout="wide")

DATA_DIR = Path("data")
RULE_PATH = DATA_DIR / "rules_expert_na.json"
MENU_PATH = DATA_DIR / "menu_config.json"

DEFAULT_MENU = {
    "slogan": "Funspire Agent 全球文化适配的内容引擎 / 内容辅助智能体",
    "markets": ["北美", "拉美", "东南亚", "中东", "日韩", "南欧", "欧洲", "全球通用"],
    "languages": ["中文输出", "中英文输出", "英文输出", "阿语输出", "泰语输出", "西语输出", "日语输出", "韩语输出"],
    "menu": {
        "工作台": ["我的项目", "高频功能快捷入口", "全球内容趋势", "待办与协作"],
        "短剧工坊": ["创意选题策划", "爆款榜单拆解", "人物体系搭建", "故事大纲创作", "分集大纲", "完整剧本", "剧本医生", "文化适配与评估"],
        "短视频工厂": ["剧情号内容", "商业广告脚本", "纪录片与深度内容", "创意病毒内容", "MCN批量生产", "分平台模板库", "在地文化适配润色"],
        "商业叙事中心": ["品牌定制剧", "游戏剧情内容", "互动剧内容", "互动故事/小说", "小说/漫画改编", "有声内容脚本", "沉浸式叙事", "教育科普叙事"],
        "跨文化适配中心": ["文化合规风险审核", "在地化叙事适配", "多地区版本生成", "在地热点工具箱", "受众偏好分析", "全球禁忌知识库", "台词本土化润色", "平台合规检测"],
        "IP资产库": ["角色资产管理", "世界观素材库", "系列IP管理", "IP衍生生成", "全球素材库"],
        "运营数据中台": ["全球爆款洞察", "逆向拆解", "宣发物料", "效果诊断", "团队协作管理"],
        "个人中心": ["账户与系统配置"]
    }
}


def safe_load_json(path, default):
    try:
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
    except Exception as e:
        st.warning(f"读取 {path} 失败：{e}")
    return default


def load_rules():
    data = safe_load_json(RULE_PATH, [])
    return data if isinstance(data, list) else []


def match_rules(script, market, genre, rules):
    matched = []
    script = script or ""
    for rule in rules:
        rule_market = rule.get("market", "")
        rule_genre = rule.get("genre", "")
        keywords = rule.get("trigger_keywords", []) or []

        market_ok = rule_market == market
        # Demo 阶段题材不做强过滤：只要市场对上，就可以参考专家规则。
        genre_ok = True if genre == "全部题材" else (rule_genre == genre or rule_genre == "通用" or True)

        if not market_ok or not genre_ok:
            continue
        hit_keywords = [kw for kw in keywords if kw and kw in script]
        if hit_keywords:
            item = rule.copy()
            item["hit_keywords"] = hit_keywords
            matched.append(item)
    return matched


def calculate_scores(matched_rules, script):
    cultural_score = 100
    compliance_score = 100
    hook_score = 48
    originality_score = 76

    strong_hook_words = [
        "曝光", "背叛", "继承", "婚约", "债务", "秘密", "复仇", "威胁",
        "解雇", "协议", "取消婚礼", "信托", "董事会", "股权", "遗嘱",
        "血脉", "宿命", "绑架", "审判"
    ]

    hook_hits = [word for word in strong_hook_words if word in script]
    hook_score = min(100, hook_score + len(hook_hits) * 6)

    severity_weights = {
        "high": 10,
        "medium": 6,
        "low": 3
    }

    if matched_rules:
        raw_penalty = 0

        for rule in matched_rules:
            severity = rule.get("severity", "medium")
            category = rule.get("category", "文化适配")

            raw_penalty += severity_weights.get(severity, 6)

            if category == "合规风险":
                compliance_score -= 16 if severity == "high" else 9

            if category in ["节奏结构", "黄金三秒"]:
                hook_score -= 5

            if category in ["世界观适配", "商业逻辑"]:
                originality_score -= 4

        rule_count = len(matched_rules)
        average_penalty = raw_penalty / rule_count
        count_penalty = min(52, rule_count * 1.4)
        severity_penalty = min(30, average_penalty * 3)

        total_cultural_penalty = count_penalty + severity_penalty
        cultural_score = 100 - total_cultural_penalty

    return (
        max(0, round(cultural_score)),
        max(0, min(100, round(hook_score))),
        max(0, round(compliance_score)),
        max(0, round(originality_score))
    )


def level_text(score):
    if score >= 82:
        return "优秀"
    if score >= 65:
        return "需优化"
    return "高风险"


def severity_label(sev):
    labels = {
        "high": "高风险",
        "medium": "中风险",
        "low": "低风险"
    }
    return labels.get(sev, sev)


def generate_rewrite_brief(matched_rules, output_language):
    if not matched_rules:
        return "当前未命中明显风险规则。建议继续强化前三秒冲突、角色主动性、结尾付费钩子。"
    lines = []
    lines.append("【中文优化方向】")
    for i, rule in enumerate(matched_rules[:8], start=1):
        lines.append(f"{i}. {rule.get('suggestion', '')}")
    if "英文" in output_language:
        lines.append("")
        lines.append("【English adaptation direction】")
        lines.append("Adapt the conflict through locally legible mechanisms: contracts, inheritance, corporate governance, legal exposure, professional evidence, or pack/mafia rules depending on genre. Keep the emotional hook, but replace culturally mismatched logic with market-specific stakes.")
    return "\n".join(lines)


def generate_report(script, market, language, genre, module, matched_rules, scores):
    cultural_score, hook_score, compliance_score, originality_score = scores
    lines = [
        "# Funspire Agent 文化适配诊断报告",
        "",
        f"目标市场：{market}",
        f"输出语言：{language}",
        f"题材：{genre}",
        f"功能模块：{module}",
        "",
        "## 综合评分",
        f"- 文化适配分：{cultural_score}/100",
        f"- 商业钩子分：{hook_score}/100",
        f"- 合规安全分：{compliance_score}/100",
        f"- 世界观/商业真实感：{originality_score}/100",
        "",
        "## 命中规则"
    ]
    if not matched_rules:
        lines.append("暂未命中明显风险规则。")
    else:
        for rule in matched_rules:
            lines.extend([
                f"### {rule.get('rule_id')}｜{rule.get('category')}｜{severity_label(rule.get('severity'))}",
                f"来源：{rule.get('source')}",
                f"命中关键词：{'、'.join(rule.get('hit_keywords', []))}",
                f"问题：{rule.get('problem')}",
                f"原因：{rule.get('reason')}",
                f"修改建议：{rule.get('suggestion')}",
                ""
            ])
    lines.extend(["## 初步改写方向", generate_rewrite_brief(matched_rules, language), "", "## 原始剧本", script])
    return "\n".join(lines)


# CSS 美化
st.markdown("""
<style>
:root {
  --bg1: #0f1028;
  --bg2: #5317a6;
  --bg3: #ff6b6b;
  --card: rgba(255,255,255,0.92);
}
[data-testid="stAppViewContainer"] {
  background: radial-gradient(circle at 10% 20%, #fff5f7 0%, transparent 24%),
              radial-gradient(circle at 90% 10%, #ecfeff 0%, transparent 24%),
              linear-gradient(135deg, #fff7ed 0%, #eef2ff 42%, #fdf2f8 100%);
}
.hero {
  padding: 30px 32px;
  border-radius: 28px;
  color: white;
  background: linear-gradient(135deg, #111827 0%, #6d28d9 45%, #f97316 100%);
  box-shadow: 0 18px 45px rgba(79, 70, 229, 0.28);
  margin-bottom: 18px;
}
.hero h1 {font-size: 44px; margin: 12px 0 4px 0; line-height: 1.12;}
.hero p {font-size: 18px; opacity: 0.94; margin-bottom: 0;}
.pill {display:inline-block; padding:7px 12px; border-radius:999px; background:rgba(255,255,255,.18); margin-right:8px; font-size:13px; border:1px solid rgba(255,255,255,.25)}
.glass-card {
  padding: 18px;
  border-radius: 20px;
  background: rgba(255,255,255,0.82);
  border: 1px solid rgba(255,255,255,0.95);
  box-shadow: 0 10px 28px rgba(15,23,42,.08);
  min-height: 130px;
}
.module-card {
  padding: 15px 16px; border-radius: 18px; min-height: 108px;
  background: linear-gradient(160deg, rgba(255,255,255,.95), rgba(255,255,255,.68));
  border: 1px solid rgba(99,102,241,.15);
  box-shadow: 0 8px 18px rgba(99,102,241,.09);
}
.issue-card {
  padding: 18px 20px;
  border-radius: 18px;
  background: white;
  border-left: 7px solid #f97316;
  box-shadow: 0 10px 24px rgba(15,23,42,.08);
  margin-bottom: 14px;
}
.issue-card.high {border-left-color:#ef4444;}
.issue-card.medium {border-left-color:#f59e0b;}
.issue-card.low {border-left-color:#22c55e;}
.small-muted {color:#64748b; font-size:13px;}
.big-number {font-size:28px; font-weight:800;}
</style>
""", unsafe_allow_html=True)

rules = load_rules()
menu_config = safe_load_json(MENU_PATH, DEFAULT_MENU)
markets = menu_config.get("markets", DEFAULT_MENU["markets"])
languages = menu_config.get("languages", DEFAULT_MENU["languages"])
menu = menu_config.get("menu", DEFAULT_MENU["menu"])

# Hero
st.markdown(f"""
<div class="hero">
  <span class="pill">OPC Web Demo</span><span class="pill">AI Agent</span><span class="pill">全球文化适配</span><span class="pill">短剧出海</span>
  <h1>Funspire Agent</h1>
  <p>{menu_config.get('slogan', DEFAULT_MENU['slogan'])}</p>
</div>
""", unsafe_allow_html=True)

with st.sidebar:
    st.header("🌍 全局控制台")
    market = st.selectbox("目标市场", markets, index=0)
    language = st.selectbox("语言选择", languages, index=1 if "中英文输出" in languages else 0)
    primary_menu = st.selectbox("一级菜单", list(menu.keys()), index=list(menu.keys()).index("跨文化适配中心") if "跨文化适配中心" in menu else 0)
    sub_menu = st.selectbox("子功能", menu.get(primary_menu, []), index=0)
    st.caption("选定后，以下所有菜单生成的内容将自动适配该地区文化。当前 Demo 已接入北美专家规则库，其他地区为资源位预留。")
    st.divider()
    st.metric("知识库规则", len(rules))
    market_counter = Counter([r.get("market", "未知") for r in rules])
    st.write("规则库覆盖：")
    for mk in markets:
        st.write(f"- {mk}: {market_counter.get(mk, 0)} 条")

# top controls
c1, c2, c3, c4 = st.columns([1.1, 1.1, 1.2, 1.6])
with c1:
    st.markdown("<div class='glass-card'><b>当前市场</b><div class='big-number'>" + market + "</div><div class='small-muted'>未来可扩展多地区资源库</div></div>", unsafe_allow_html=True)
with c2:
    st.markdown("<div class='glass-card'><b>输出语言</b><div class='big-number' style='font-size:24px'>" + language + "</div><div class='small-muted'>Demo 先输出诊断与改写方向</div></div>", unsafe_allow_html=True)
with c3:
    st.markdown("<div class='glass-card'><b>当前模块</b><div class='big-number' style='font-size:23px'>" + primary_menu + "</div><div class='small-muted'>" + sub_menu + "</div></div>", unsafe_allow_html=True)
with c4:
    if market != "北美":
        st.warning(f"{market} 规则库位置已预留；当前演示数据主要来自北美短剧专家修改意见。")
    else:
        st.success("北美专家规则库已接入，可进行文化适配诊断。")

# Product matrix preview
with st.expander("📌 产品菜单结构预览（已预留后续全球资源库位置）", expanded=False):
    cols = st.columns(4)
    for i, (k, subs) in enumerate(menu.items()):
        with cols[i % 4]:
            st.markdown(f"<div class='module-card'><b>{k}</b><br><span class='small-muted'>{' / '.join(subs[:4])}{' ...' if len(subs)>4 else ''}</span></div>", unsafe_allow_html=True)

st.divider()

# Main workbench
left, right = st.columns([1.06, 0.94])

sample_script = """女主嫁入豪门后，婆婆当众羞辱她，说她出身低微，配不上自己的儿子。女主为了丈夫一直忍耐，甚至被要求下跪道歉。直到男主出现，才替她撑腰。"""

with left:
    st.subheader("🎬 文化适配与评估")
    genre_options = ["全部题材", "CEO霸总·豪门逆袭", "先婚后爱・隐藏身份霸总・替嫁契约", "黑手党黑市拍卖・控制与反抗・双强博弈", "狼人 Alpha・宿命伴侣・族群复仇", "通用"]
    genre = st.selectbox("题材 / Genre", genre_options)
    b1, b2 = st.columns(2)
    with b1:
        if st.button("加载示例剧本", use_container_width=True):
            st.session_state["script"] = sample_script
    with b2:
        if st.button("清空输入", use_container_width=True):
            st.session_state["script"] = ""
    script = st.text_area("请粘贴中文短剧片段 / 剧本", height=320, value=st.session_state.get("script", ""), placeholder="粘贴剧本片段后，点击右侧开始分析。")

with right:
    st.subheader("🧠 Demo 说明")
    st.markdown("""
<div class="glass-card">
<b>当前能力：</b><br>
1. 识别北美文化适配问题<br>
2. 命中专家标注规则<br>
3. 输出问题、原因、修改方向<br>
4. 生成可下载诊断报告<br><br>
<b>后续扩展：</b> 拉美 / 东南亚 / 中东 / 日韩 / 欧洲等市场资源库、多地区版本生成、平台合规检测、台词本土化润色。
</div>
""", unsafe_allow_html=True)
    st.write("")
    analyze_clicked = st.button("🚀 开始分析", type="primary", use_container_width=True)

if analyze_clicked:
    if not script.strip():
        st.warning("请先输入剧本。")
    elif market != "北美":
        st.error("当前 Demo 仅接入北美专家规则库。其他市场的知识库位置已预留，可在融资后扩展。")
    else:
        matched_rules = match_rules(script, market, genre, rules)
        scores = calculate_scores(matched_rules, script)
        cultural_score, hook_score, compliance_score, originality_score = scores

        st.divider()
        st.subheader("📊 一、综合评分")
        m1, m2, m3, m4, m5 = st.columns(5)
        m1.metric("文化适配", f"{cultural_score}/100", level_text(cultural_score))
        m2.metric("商业钩子", f"{hook_score}/100", level_text(hook_score))
        m3.metric("合规安全", f"{compliance_score}/100", level_text(compliance_score))
        m4.metric("真实感", f"{originality_score}/100", level_text(originality_score))
        m5.metric("命中规则", f"{len(matched_rules)} 条")

        if cultural_score >= 82:
            st.success("整体适配度较好，可以进入局部润色和台词本土化。")
        elif cultural_score >= 65:
            st.warning("具备可用基础，但部分冲突机制需要重构。")
        else:
            st.error("文化适配风险较高，建议重写核心冲突与人物动机。")

        tab1, tab2, tab3, tab4 = st.tabs(["命中问题", "改写方向", "知识库透视", "导出报告"])

        with tab1:
            st.subheader("🧩 二、命中的文化适配问题")
            if not matched_rules:
                st.success("暂未命中明显文化适配问题。")
            else:
                for rule in matched_rules[:20]:
                    sev = rule.get("severity", "medium")
                    st.markdown(f"""
                    <div class="issue-card {sev}">
                    <h4>{rule.get('rule_id')}｜{rule.get('category')}｜{severity_label(sev)}</h4>
                    <p><b>来源：</b>{rule.get('source')}</p>
                    <p><b>命中关键词：</b>{'、'.join(rule.get('hit_keywords', []))}</p>
                    <p><b>问题：</b>{rule.get('problem')}</p>
                    <p><b>原因：</b>{rule.get('reason')}</p>
                    <p><b>修改建议：</b>{rule.get('suggestion')}</p>
                    </div>
                    """, unsafe_allow_html=True)
                if len(matched_rules) > 20:
                    st.info(f"共命中 {len(matched_rules)} 条规则，页面仅展示前 20 条。")

        with tab2:
            st.subheader("✍️ 三、初步改写方向")
            rewrite_text = generate_rewrite_brief(matched_rules, language)
            st.text_area("系统生成的改写方向", value=rewrite_text, height=300)
            st.info("当前版本是规则库诊断 Demo。下一步接入大模型后，此处可生成完整中文优化版和英文本土化版。")

        with tab3:
            st.subheader("🗂️ 四、知识库透视")
            cat_counter = Counter([r.get("category", "文化适配") for r in rules])
            proj_counter = Counter([r.get("project_title", "未知项目") for r in rules])
            cc1, cc2 = st.columns(2)
            with cc1:
                st.write("规则类型分布")
                st.bar_chart(dict(cat_counter))
            with cc2:
                st.write("项目来源分布")
                st.bar_chart(dict(proj_counter))
            st.caption("这些规则来自专家修改意见，后续可继续接入真实过稿/退稿数据与多地区文化禁忌库。")

        with tab4:
            st.subheader("📥 五、导出报告")
            report = generate_report(script, market, language, genre, sub_menu, matched_rules, scores)
            st.download_button("下载诊断报告 Markdown", data=report, file_name="funspire_cultural_adaptation_report.md", mime="text/markdown")
            with st.expander("预览报告"):
                st.markdown(report)
