from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Dict, List, Sequence


GLOBAL_SYSTEM_PROMPT = (
    "你是一名严格的战略监测分析助手。\n"
    "目标：从权威来源抽取最新变更并结构化输出，附可溯源证据与不确定性等级。\n"
    "要求：仅使用提供的 [SOURCE_URLS] 及其子页；聚焦新增/删除/措辞显著变化；"
    "给出 So What；若无更新返回 no_update=true；不得编造引用。"
)


@dataclass(slots=True)
class PromptTemplate:
    key: str
    title: str
    description: str
    user_template: str
    output_schema: str
    default_source_hints: List[str]

    def render_user_prompt(self, source_urls: Sequence[str] | None = None) -> str:
        urls = list(source_urls) if source_urls else self.default_source_hints
        payload = json.dumps(urls, ensure_ascii=False)
        return self.user_template.replace("{{SOURCE_URLS}}", payload)


PROMPT_TEMPLATES: List[PromptTemplate] = [
    PromptTemplate(
        key="institution_line",
        title="制度线：NSS/安保法/NSC 更新",
        description="对比 NSS、安保法口径与 NSC 权责的措辞变化并评估出手门槛。",
        user_template=(
            "任务：对比日本国家安全战略（NSS）、安保法制（含“存立危机事态”“集体自卫权”口径）、"
            "NSC/官邸权责页面的最新更新。\n"
            "1. 抓取 [SOURCE_URLS]。\n"
            "2. 标注相对以往版本/表述的新增/删减/措辞加强。\n"
            "3. 给出对“出手门槛”的影响评估（Lower/Unchanged/Higher）。\n"
            "4. 输出 JSON，字段见下方 Schema。\n"
            "[SOURCE_URLS]={{SOURCE_URLS}}"
        ),
        output_schema="""```json
{
  "no_update": false,
  "changes": [
    {
      "doc": "NSS|SecurityLegislation|NSC",
      "section": "string",
      "change_type": "added|removed|strengthened|weakened",
      "old_snippet": "string|null",
      "new_snippet": "string",
      "impact_on_threshold": "Lower|Unchanged|Higher",
      "why_it_matters": "string",
      "source_url": "string",
      "observed_at": "YYYY-MM-DD"
    }
  ],
  "analyst_assessment": {
    "overall_threshold_shift": "Lower|Unchanged|Higher",
    "confidence": "Low|Medium|High",
    "notes": "string"
  }
}
```""",
        default_source_hints=[
            "https://www.cas.go.jp/jp/siryou/221216anzenhoshou/nss-e.pdf",
            "https://www.mofa.go.jp/fp/nsp/page1we_000081.html",
            "https://www.mofa.go.jp/files/000143304.pdf",
            "https://www.mofa.go.jp/fp/nsp/page1we_000080.html",
        ],
    ),
    PromptTemplate(
        key="capability_line",
        title="能力线：反击能力/平台里程碑",
        description="追踪反击能力、BMD/Aegis、常设统合司令部的最新 IOC/FOC 节点。",
        user_template=(
            "任务：监控“能打什么”的实操能力进度（反击能力、BMD/Aegis、远程弹药、常设统合司令部）。\n"
            "1. 逐页检索 [SOURCE_URLS]。\n"
            "2. 抽取最新里程碑（签约/测试/IOC/FOC）。\n"
            "3. 评估对“反击能力窗口期”的影响（月）。\n"
            "4. 输出 JSON，字段见 Schema。\n"
            "[SOURCE_URLS]={{SOURCE_URLS}}"
        ),
        output_schema="""```json
{
  "no_update": false,
  "milestones": [
    {
      "capability": "counterstrike|BMD|Aegis|C2|munitions|ISR|UAS",
      "event": "contract|delivery|IOC|FOC|test|integration",
      "date": "YYYY-MM-DD",
      "platform_or_unit": "string",
      "schedule_shift_months": -12,
      "why_it_matters": "string",
      "source_url": "string"
    }
  ],
  "window_estimate": {
    "counterstrike_ready_month": "YYYY-MM",
    "confidence": "Low|Medium|High",
    "assumptions": "string"
  }
}
```""",
        default_source_hints=[
            "https://www.mod.go.jp/en/publ/w_paper/wp2024/DOJ2024_EN_Reference.pdf",
            "https://www.mod.go.jp/en/press/",
        ],
    ),
    PromptTemplate(
        key="alliance_line",
        title="同盟线：指挥措辞与三边打包",
        description="识别“协调”→“（准）共同指挥”的措辞升级，并跟踪欧线-东线 bundling。",
        user_template=(
            "任务：抽取指挥关系措辞从“协调/联络”到“（准）共同指挥”的变化，记录三边文件是否将“欧线-东线”打包。\n"
            "1. 解析 [SOURCE_URLS]（美日/美日韩官方发布与通讯社原典链接）。\n"
            "2. 标注关键措辞变化与首次出现时间。\n"
            "3. 输出 JSON。\n"
            "[SOURCE_URLS]={{SOURCE_URLS}}"
        ),
        output_schema="""```json
{
  "no_update": false,
  "phrasing_shifts": [
    {
      "doc_type": "US-Japan|US-JPN-ROK",
      "old_phrase": "string",
      "new_phrase": "string",
      "first_seen": "YYYY-MM-DD",
      "implication": "coordination_to_combined|unchanged",
      "source_url": "string"
    }
  ],
  "bundling_evidence": {
    "euro_asia_bundled": true,
    "quote": "string",
    "source_url": "string",
    "why_it_matters": "string"
  },
  "analyst_flag": "Green|Yellow|Red",
  "confidence": "Low|Medium|High"
}
```""",
        default_source_hints=[
            "https://www.defense.gov/Newsroom/Releases/",
            "https://www.mod.go.jp/en/d_policy/index.html",
            "https://www.mofa.go.jp/fp/nsp/page1we_000081.html",
            "https://www.reuters.com/world/us/pentagon-chief-hegseth-says-warrior-japan-indispensable-deter-china-2025-03-30/",
        ],
    ),
    PromptTemplate(
        key="capital_line",
        title="资本/治理线：JPX/TSE 改革",
        description="跟踪 PBR<1 披露、交叉持股、英文披露等外部刹车强度。",
        user_template=(
            "任务：跟踪 JPX/TSE 公司治理改革（PBR<1 披露、交叉持股削减、英文披露）的新规与执行进度，"
            "以及监管对“低资本效率+国策投资”冲突的表态。\n"
            "1. 抓取 [SOURCE_URLS]。\n"
            "2. 抽取新增要求、截止时间、覆盖面。\n"
            "3. 输出 JSON。\n"
            "[SOURCE_URLS]={{SOURCE_URLS}}"
        ),
        output_schema="""```json
{
  "no_update": false,
  "governance_moves": [
    {
      "rule": "PBR<1 disclosure|cross-shareholding|english-disclosure|board-independence",
      "new_requirement": "string",
      "deadline": "YYYY-MM-DD",
      "coverage": "Prime|Standard|Growth|All",
      "enforcement_signal": "advisory|comply-or-explain|mandatory",
      "why_it_matters": "string",
      "source_url": "string"
    }
  ],
  "pressure_index": {
    "scale_0_5": 0,
    "rationale": "string",
    "confidence": "Low|Medium|High"
  }
}
```""",
        default_source_hints=[
            "https://www.jpx.co.jp/english/equities/improvement/",
            "https://www.jpx.co.jp/english/equities/follow-up/02.html",
            "https://www.fsa.go.jp/en/refer/councils/follow-up/material/20240418-04.pdf",
            "https://www.reuters.com/markets/asia/tokyo-bourse-require-japanese-english-disclosures-top-firms-2024-02-26/",
        ],
    ),
    PromptTemplate(
        key="funds_line",
        title="资金侧：GPIF 原则与政策边界",
        description="监测 GPIF 投资原则/受托责任中是否出现政策性配置的措辞漂移。",
        user_template=(
            "任务：监测 GPIF 投资原则/中期计划/受托责任与 ESG 报告中的政策性定向配置倾向或用语漂移。\n"
            "1. 解析 [SOURCE_URLS]。\n"
            "2. 标注“仅为被保险人长期回报”与“受托责任”措辞是否变化。\n"
            "3. 输出 JSON。\n"
            "[SOURCE_URLS]={{SOURCE_URLS}}"
        ),
        output_schema="""```json
{
  "no_update": false,
  "principle_shifts": [
    {
      "clause": "fiduciary_duty|policy_neutrality|asset_mix|alternatives_cap",
      "old_snippet": "string|null",
      "new_snippet": "string",
      "implication": "tilt_to_policy|unchanged",
      "source_url": "string",
      "observed_at": "YYYY-MM-DD"
    }
  ],
  "analyst_assessment": {
    "policy_influence_risk": "Low|Medium|High",
    "confidence": "Low|Medium|High",
    "notes": "string"
  }
}
```""",
        default_source_hints=[
            "https://www.gpif.go.jp/en/about/",
            "https://www.gpif.go.jp/en/about/15324685gpif/Investment_Principles_2025%20.pdf",
            "https://www.gpif.go.jp/en/investment/Stewardship_Activities_Report_2024-2025.pdf",
        ],
    ),
    PromptTemplate(
        key="public_opinion",
        title="舆情民意：安保 vs 民生排名",
        description="汇总近 30–60 天主流民调对安保议题的热度及排序。",
        user_template=(
            "任务：汇总近 30–60 天主流民调中，安保议题相对“物价/工资/少子化”的热度与优先级变化。\n"
            "1. 抓取 [SOURCE_URLS]（NHK、共同社、路透/日经民调稿）。\n"
            "2. 返回三项最高关注议题及占比/排序变化。\n"
            "3. 输出 JSON。\n"
            "[SOURCE_URLS]={{SOURCE_URLS}}"
        ),
        output_schema="""```json
{
  "no_update": false,
  "top_issues": [
    {"issue": "prices|wages|security|pensions|immigration|childcare", "rank": 1, "pct": 0.00}
  ],
  "shift_commentary": "string",
  "sources": ["string"],
  "confidence": "Low|Medium|High"
}
```""",
        default_source_hints=[
            "https://www3.nhk.or.jp/nhkworld/en/news/tags/30/",
            "https://english.kyodonews.net/",
            "https://asia.nikkei.com/Politics",
            "https://www.reuters.com/world/asia-pacific/",
        ],
    ),
    PromptTemplate(
        key="entrapment_alert",
        title="红灯预警：Entrapment 判定器",
        description="评估三信号（bundling/command/doctrine），并生成快报草案。",
        user_template=(
            "任务：当且仅当以下三信号同时满足时输出 alert=RED 并生成快报草案，否则为 GREEN/YELLOW。\n"
            "S1：美日韩联合文本明文将“俄远东/朝鲜援俄乌”纳入共同应对框架。\n"
            "S2：日方常设统合司令部或驻日美军司令部措辞由“协调/联络”升级为“（准）共同指挥”。\n"
            "S3：官方“反击能力”叙事出现“先发抑制/预防打击”表述替代“报复性自卫”。\n"
            "请在 [SOURCE_URLS] 中检索并打分，输出 Schema 所列字段。\n"
            "[SOURCE_URLS]={{SOURCE_URLS}}"
        ),
        output_schema="""```json
{
  "alert": "Green|Yellow|Red",
  "signals": {
    "S1_bundling": {"met": false, "quote": "string", "url": "string"},
    "S2_command": {"met": false, "quote": "string", "url": "string"},
    "S3_doctrine": {"met": false, "quote": "string", "url": "string"}
  },
  "quick_brief": {
    "what_happened": "≤80 chars",
    "so_what": ["string","string","string"],
    "next_steps": ["collect X","watch Y","engage Z"]
  },
  "confidence": "Low|Medium|High",
  "timestamp": "YYYY-MM-DD"
}
```""",
        default_source_hints=[
            "https://www.mofa.go.jp/fp/nsp/page1we_000081.html",
            "https://www.mod.go.jp/en/d_policy/index.html",
            "https://www.cas.go.jp/jp/siryou/221216anzenhoshou/nss-e.pdf",
            "https://www.reuters.com/world/us/pentagon-chief-hegseth-says-warrior-japan-indispensable-deter-china-2025-03-30/",
        ],
    ),
    PromptTemplate(
        key="ach_update",
        title="ACH 假说集：权重与证据",
        description="在 H1/H2/H3 三路径下记录支持/反驳与权重。",
        user_template=(
            "任务：针对 H1 同盟内正常化、H2 同盟拖拽、H3 内向化收缩三条互斥路径，"
            "基于当周证据更新权重（总和=1），并列出支持/反驳证据，按 ICD-203 填写来源质量。\n"
            "从 [SOURCE_URLS] 选择证据。\n"
            "[SOURCE_URLS]={{SOURCE_URLS}}"
        ),
        output_schema="""```json
{
  "weights": {"H1": 0.6, "H2": 0.3, "H3": 0.1},
  "evidence": {
    "H1_support": [{"quote":"string","url":"string","quality":"A|B|C"}],
    "H1_refute":  [{"quote":"string","url":"string","quality":"A|B|C"}],
    "H2_support": [{"quote":"string","url":"string","quality":"A|B|C"}],
    "H2_refute":  [{"quote":"string","url":"string","quality":"A|B|C"}],
    "H3_support": [{"quote":"string","url":"string","quality":"A|B|C"}],
    "H3_refute":  [{"quote":"string","url":"string","quality":"A|B|C"}]
  },
  "notes": "string",
  "confidence": "Low|Medium|High",
  "updated_at": "YYYY-MM-DD"
}
```""",
        default_source_hints=[
            "https://www.cas.go.jp/jp/siryou/221216anzenhoshou/nss-e.pdf",
            "https://www.mofa.go.jp/fp/nsp/page1we_000081.html",
            "https://www.mod.go.jp/en/publ/w_paper/wp2024/DOJ2024_EN_Reference.pdf",
            "https://www.jpx.co.jp/english/equities/follow-up/02.html",
            "https://www.gpif.go.jp/en/about/15324685gpif/Investment_Principles_2025%20.pdf",
            "https://asia.nikkei.com/Politics",
        ],
    ),
    PromptTemplate(
        key="brier_pool",
        title="概率与 Brier 记分板",
        description="为 8–12 个事件给出 12 个月概率，并记录证据。",
        user_template=(
            "任务：为 8–12 个可验证事件给出未来 12 个月内发生概率，附 ≤100 字依据，"
            "并引用关键证据 URL；初始 outcome 填 null。\n"
            "[SOURCE_URLS]={{SOURCE_URLS}}"
        ),
        output_schema="""```json
{
  "events": [
    {
      "event": "string",
      "deadline": "YYYY-MM-DD",
      "p": 0.35,
      "rationale": "string",
      "key_evidence": ["url1","url2"],
      "outcome": null
    }
  ],
  "timestamp": "YYYY-MM-DD"
}
```""",
        default_source_hints=[
            "https://www.cas.go.jp/jp/siryou/221216anzenhoshou/nss-e.pdf",
            "https://www.mod.go.jp/en/press/",
            "https://www.mofa.go.jp/fp/nsp/page1we_000081.html",
            "https://www.jpx.co.jp/english/equities/follow-up/02.html",
            "https://www.reuters.com/world/asia-pacific/",
        ],
    ),
    PromptTemplate(
        key="flash_brief",
        title="事件快报：What/So What/Next",
        description="当颜色=Red 或三信号满足时输出 ≤300 字快报草案。",
        user_template=(
            "任务：当指标颜色=Red 或三信号满足时，生成 ≤300 字快报草案，"
            "包含 What happened（≤80 字）、So What（三条）、Next（三条）、三条原典链接。\n"
            "[SOURCE_URLS]={{SOURCE_URLS}}"
        ),
        output_schema="""```json
{
  "what": "string",
  "so_what": ["string","string","string"],
  "next": ["string","string","string"],
  "sources": ["url1","url2","url3"],
  "confidence": "Low|Medium|High",
  "generated_at": "YYYY-MM-DD"
}
```""",
        default_source_hints=[
            "https://www.mofa.go.jp/fp/nsp/page1we_000081.html",
            "https://www.mod.go.jp/en/d_policy/index.html",
            "https://www.jpx.co.jp/english/equities/follow-up/02.html",
            "https://www.reuters.com/world/asia-pacific/",
        ],
    ),
]

PROMPT_INDEX: Dict[str, PromptTemplate] = {template.key: template for template in PROMPT_TEMPLATES}


def list_prompt_templates() -> List[PromptTemplate]:
    return PROMPT_TEMPLATES


def get_prompt_template(key: str) -> PromptTemplate:
    if key not in PROMPT_INDEX:
        raise KeyError(f"Unknown prompt key: {key}")
    return PROMPT_INDEX[key]


__all__ = [
    "GLOBAL_SYSTEM_PROMPT",
    "PromptTemplate",
    "PROMPT_TEMPLATES",
    "list_prompt_templates",
    "get_prompt_template",
]
