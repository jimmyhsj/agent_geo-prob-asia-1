from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import List


class IndicatorDimension(str, Enum):
    """Top-level board dimensions spelled out in §4 of the README."""

    INSTITUTION = "institution"
    CAPABILITY = "capability"
    ALLIANCE = "alliance"
    CAPITAL_GOVERNANCE = "capital_governance"
    FUNDS = "funds"


@dataclass(slots=True)
class IndicatorTemplate:
    key: str
    dimension: IndicatorDimension
    indicator: str
    description: str
    default_weight: int = 3
    primary_sources: List[str] = field(default_factory=list)


INDICATOR_TEMPLATES: List[IndicatorTemplate] = [
    IndicatorTemplate(
        key="institution_article9",
        dimension=IndicatorDimension.INSTITUTION,
        indicator="9条/集体自卫权口径",
        description=(
            "Monitor expansions of 'existential crisis situation' definitions,"
            " pre-emption references, or permanent authorisations in MOFA/CLB"
            " publications."
        ),
        default_weight=4,
        primary_sources=[
            "https://www.mofa.go.jp/files/000143304.pdf",
            "https://www.cas.go.jp/jp/siryou/221216anzenhoshou/nss-e.pdf",
        ],
    ),
    IndicatorTemplate(
        key="institution_nsc_process",
        dimension=IndicatorDimension.INSTITUTION,
        indicator="NSC/官邸权能",
        description="Track NSC/NSS organisational reforms that concentrate decision rights",
        primary_sources=[
            "https://www.mofa.go.jp/fp/nsp/page1we_000080.html",
        ],
    ),
    IndicatorTemplate(
        key="capability_counterstrike_delivery",
        dimension=IndicatorDimension.CAPABILITY,
        indicator="反击能力交付",
        description="Milestones for stand-off missiles, BMD, Aegis, and joint HQ readiness",
        default_weight=5,
        primary_sources=[
            "https://www.mod.go.jp/en/d_policy/index.html",
            "https://www.mod.go.jp/en/publ/w_paper/wp2024/DOJ2024_EN_Reference.pdf",
        ],
    ),
    IndicatorTemplate(
        key="capability_joint_hq",
        dimension=IndicatorDimension.CAPABILITY,
        indicator="常设统合司令部",
        description="Authority and staffing level of the permanent Joint Operations Command",
        primary_sources=["https://www.mod.go.jp/en/d_policy/index.html"],
    ),
    IndicatorTemplate(
        key="alliance_tri_lateral_text",
        dimension=IndicatorDimension.ALLIANCE,
        indicator="日美韩三边文本",
        description="Whether Russia Far East / DPRK support is bundled as joint response",
        default_weight=4,
        primary_sources=["https://www.mofa.go.jp/fp/nsp/page1we_000081.html"],
    ),
    IndicatorTemplate(
        key="alliance_joint_command_language",
        dimension=IndicatorDimension.ALLIANCE,
        indicator="联指一体化措辞",
        description="Shift from 'coordination' to '(quasi) joint command' in JTF & USFJ",
        primary_sources=["https://www.mod.go.jp/en/d_policy/index.html"],
    ),
    IndicatorTemplate(
        key="capital_tse_reform",
        dimension=IndicatorDimension.CAPITAL_GOVERNANCE,
        indicator="TSE 改革推进度",
        description="Coverage of PBR<1 disclosures, cross-shareholding unwind, EN reporting",
        primary_sources=[
            "https://www.jpx.co.jp/english/equities/follow-up/02.html",
            "https://www.reuters.com/markets/asia/tokyo-bourse-require-japanese-english-disclosures-top-firms-2024-02-26/",
        ],
    ),
    IndicatorTemplate(
        key="capital_fsa_guidance",
        dimension=IndicatorDimension.CAPITAL_GOVERNANCE,
        indicator="监管立场",
        description="FSA/JPX stance on policy-investment conflicts and capital efficiency",
        primary_sources=["https://www.fsa.go.jp/en/refer/councils/follow-up/material/20240418-04.pdf"],
    ),
    IndicatorTemplate(
        key="funds_gpif_principles",
        dimension=IndicatorDimension.FUNDS,
        indicator="GPIF 原则更新",
        description="Frequency of stewardship reports and evidence of policy allocations",
        primary_sources=[
            "https://www.gpif.go.jp/en/about/",
            "https://www.gpif.go.jp/en/investment/Stewardship_Activities_Report_2024-2025.pdf",
        ],
    ),
]


@dataclass(slots=True)
class EntrapmentSignalDefinition:
    key: str
    description: str
    trigger_condition: str
    primary_sources: List[str]


ENTRAPMENT_SIGNALS: List[EntrapmentSignalDefinition] = [
    EntrapmentSignalDefinition(
        key="trilateral_packaging",
        description="三边联合文本将俄远东/朝鲜支援俄乌打包为共同行动",
        trigger_condition="When joint statements explicitly list Russia Far East + DPRK along EU support",
        primary_sources=["https://www.mofa.go.jp/fp/nsp/page1we_000081.html"],
    ),
    EntrapmentSignalDefinition(
        key="joint_command_upgrade",
        description="联指措辞从'协调/联络'升级为'(准)共同指挥'",
        trigger_condition="Language upgrade in SDF Joint HQ or USFJ releases",
        primary_sources=["https://www.mod.go.jp/en/d_policy/index.html"],
    ),
    EntrapmentSignalDefinition(
        key="counterstrike_narrative_shift",
        description="反击能力叙事从报复性自卫滑向先发抑制",
        trigger_condition="Cabinet/NSC docs frame counter-strike as pre-emption",
        primary_sources=["https://www.cas.go.jp/jp/siryou/221216anzenhoshou/nss-e.pdf"],
    ),
]


ACH_QUESTION = "日本 12 个月内是否会进入区域有限军事行动的事实参与？"
ACH_HYPOTHESES = [
    "H1 同盟内正常化",
    "H2 同盟拖拽",
    "H3 内向化收缩",
]
