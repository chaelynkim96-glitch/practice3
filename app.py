import calendar
from datetime import date, datetime, timedelta

import pandas as pd
import streamlit as st


st.set_page_config(
    page_title="이벤트 트렌드 캘린더",
    page_icon="📅",
    layout="wide",
    initial_sidebar_state="expanded",
)


DEFAULT_TYPES = ["전시", "팝업", "경쟁사 이벤트", "지자체/축제", "협업/브랜드"]
DEFAULT_REGIONS = ["서울", "수도권", "부산", "대구", "광주", "대전", "기타"]
DEFAULT_TARGETS = ["2030", "가족", "VIP", "관광객", "지역고객", "전체"]
TYPE_COLORS = {
    "전시": ("#8b5cf6", "#f3e8ff"),
    "팝업": ("#f59e0b", "#fff7ed"),
    "경쟁사 이벤트": ("#3b82f6", "#eff6ff"),
    "지자체/축제": ("#22c55e", "#f0fdf4"),
    "협업/브랜드": ("#d946ef", "#fdf4ff"),
    "기타": ("#6b7280", "#f3f4f6"),
}
IMPORTANCE_SCORE = {"상": 3, "중": 2, "하": 1}


CSS = """
<style>
    .stApp {
        background: #f7f8fc;
        color: #111827;
    }
    .block-container {
        padding-top: 1.2rem;
        padding-bottom: 1rem;
        max-width: 1500px;
    }
    section[data-testid="stSidebar"] {
        background: #ffffff;
        border-right: 1px solid #e5e7eb;
    }
    .sidebar-brand {
        display:flex; gap:12px; align-items:flex-start;
        padding: 10px 6px 20px 6px;
    }
    .brand-icon {
        width:40px; height:40px; border-radius:12px; background:#8b5cf6;
        color:white; display:flex; align-items:center; justify-content:center;
        font-size:20px; font-weight:700;
    }
    .brand-title {
        font-size:1.45rem; font-weight:800; line-height:1.2; margin-bottom:2px;
    }
    .brand-sub {
        font-size:0.88rem; color:#6b7280;
    }
    .side-menu-title {
        font-size:0.8rem; font-weight:700; color:#6b7280; text-transform:uppercase;
        margin-top: 10px; margin-bottom: 10px;
    }
    .side-menu-item.active {
        background:#f0ebff; color:#5b34da; font-weight:700; border:1px solid #e2d7ff;
    }
    .side-menu-item {
        padding: 12px 14px; border-radius:12px; margin-bottom:8px; background:#fff;
        border:1px solid transparent; color:#374151;
    }
    .toolbar-card, .panel-card, .summary-card {
        background:#ffffff; border:1px solid #e5e7eb; border-radius:18px; padding:16px;
        box-shadow: 0 4px 16px rgba(17, 24, 39, 0.04);
    }
    .calendar-shell {
        background:#ffffff; border:1px solid #e5e7eb; border-radius:22px; overflow:hidden;
        box-shadow: 0 4px 16px rgba(17, 24, 39, 0.04);
    }
    .month-toolbar {
        display:flex; justify-content:space-between; align-items:center; padding:16px 18px;
        border-bottom:1px solid #eef2f7; gap:12px; flex-wrap:wrap;
    }
    .month-title {
        font-size:1.7rem; font-weight:800; color:#111827;
    }
    .pill-btn {
        display:inline-block; padding:8px 14px; border-radius:12px; border:1px solid #d1d5db;
        background:#fff; font-weight:600; font-size:0.92rem;
    }
    .pill-btn.active {
        border-color:#7c3aed; color:#5b34da; background:#f5f3ff;
    }
    .calendar-header-row, .calendar-grid-row {
        display:grid; grid-template-columns: repeat(7, minmax(0, 1fr));
    }
    .calendar-header-cell {
        padding:14px 12px; border-bottom:1px solid #eef2f7; font-weight:700; background:#fff;
        text-align:left;
    }
    .calendar-cell {
        min-height:128px; border-right:1px solid #eef2f7; border-bottom:1px solid #eef2f7;
        padding:10px; background:#fff;
    }
    .calendar-cell.outside {
        background:#fafafa;
        color:#9ca3af;
    }
    .calendar-day {
        font-weight:700; margin-bottom:10px; font-size:0.96rem;
    }
    .calendar-day.today {
        display:inline-flex; align-items:center; justify-content:center;
        width:26px; height:26px; border-radius:999px; background:#315efb; color:#fff;
    }
    .event-chip {
        border-radius:12px; padding:8px 10px; margin-bottom:8px; border:1px solid transparent;
        font-size:0.82rem; line-height:1.35;
    }
    .event-chip-type { font-weight:800; margin-bottom:2px; }
    .event-chip-title { font-weight:700; color:#111827; }
    .event-chip-venue { color:#4b5563; }
    .legend-wrap { display:flex; gap:20px; flex-wrap:wrap; align-items:center; justify-content:center; padding:14px; }
    .legend-item { display:flex; gap:8px; align-items:center; color:#4b5563; font-size:0.9rem; }
    .legend-dot { width:10px; height:10px; border-radius:999px; }
    .metric-big { font-size:2.2rem; font-weight:800; color:#111827; }
    .metric-label { color:#6b7280; font-size:0.9rem; }
    .mini-stat { display:flex; gap:18px; margin-top:10px; flex-wrap:wrap; }
    .mini-stat-item strong { font-size:2rem; display:block; }
    .section-title { font-size:1.12rem; font-weight:800; margin-bottom:10px; }
    .muted { color:#6b7280; }
    .detail-badge {
        display:inline-block; padding:5px 10px; border-radius:999px; font-size:0.78rem; font-weight:700;
        margin-bottom:8px;
    }
    .detail-title { font-size:2rem; font-weight:900; line-height:1.1; margin:8px 0 10px; }
    .detail-row { color:#374151; font-size:0.95rem; margin-bottom:8px; }
    .detail-grid {
        display:grid; grid-template-columns: 120px 1fr; gap:10px; row-gap:12px;
        font-size:0.95rem; align-items:start;
    }
    .detail-grid .label {
        color:#6b7280; font-weight:700;
    }
    .divider { height:1px; background:#e5e7eb; margin:18px 0; }
    .check-line { margin-bottom:8px; }
    .insight-line { margin-bottom:10px; color:#374151; }
    .keyword-tag {
        display:inline-block; padding:8px 10px; background:#f5f3ff; color:#5b34da; border-radius:12px;
        font-weight:700; font-size:0.85rem; margin:0 8px 8px 0;
    }
    .report-link {
        display:inline-block; margin-top:10px; padding:10px 14px; border-radius:12px;
        background:#eef2ff; color:#4f46e5; font-weight:800; text-decoration:none;
    }
    .filter-head {
        display:flex; justify-content:space-between; align-items:center; margin-top:14px; margin-bottom:8px;
    }
    .filter-label { font-weight:800; }
    .small-link { color:#4f46e5; font-size:0.86rem; font-weight:700; }
    .panel-note {
        background:#faf5ff; border:1px solid #eadcff; border-radius:14px; padding:12px; color:#5b34da;
        font-size:0.9rem;
    }
    .footer-note { color:#6b7280; font-size:0.84rem; }
</style>
"""


def parse_date(value):
    if pd.isna(value) or value in (None, ""):
        return None
    if isinstance(value, date) and not isinstance(value, datetime):
        return value
    try:
        return pd.to_datetime(value).date()
    except Exception:
        return None


def text_or_default(value, default="-"):
    if pd.isna(value) or value is None or str(value).strip() == "":
        return default
    return str(value).strip()


def infer_status(start_date, end_date, today=None):
    today = today or date.today()
    if not start_date or not end_date:
        return "예정"
    if today < start_date:
        return "예정"
    if start_date <= today <= end_date:
        return "진행중"
    return "종료"


def get_type_color(event_type):
    return TYPE_COLORS.get(event_type, TYPE_COLORS["기타"])


def normalize_event_type(value):
    mapping = {
        "지자체 행사": "지자체/축제",
        "지자체": "지자체/축제",
        "축제": "지자체/축제",
        "브랜드 협업": "협업/브랜드",
        "협업": "협업/브랜드",
        "경쟁사이벤트": "경쟁사 이벤트",
    }
    value = text_or_default(value, "기타")
    return mapping.get(value, value)


def normalize_target(value):
    value = text_or_default(value, "전체")
    if value in ["일반", "전체"]:
        return "전체"
    return value


def load_sample_data():
    sample_rows = [
        {
            "id": 1,
            "collected_at": "2026-04-10",
            "event_name": "아트 협업 전시",
            "event_type": "전시",
            "host_brand": "브랜드A",
            "venue_name": "성수 팝업홀",
            "region": "서울",
            "start_date": "2026-04-10",
            "end_date": "2026-05-20",
            "status": "진행중",
            "source_site": "공식 사이트",
            "source_link": "https://example.com/1",
            "source_summary": "브랜드와 작가 협업 전시 소개",
            "ai_summary": "브랜드와 미술 작가의 협업형 전시로 포토존과 한정 굿즈가 결합된 행사",
            "keywords": "아트, 포토존, 협업",
            "target_estimate": "2030",
            "importance": "상",
            "benchmark_value": "상",
            "lotte_idea": "롯데 문화홀 시즌 전시와 굿즈 연계를 결합",
            "duplicate_flag": False,
            "review_flag": True,
            "one_line_summary": "작가 협업과 포토존 중심의 체험형 전시",
            "visual_feature": "대형 오브제와 감각적 동선",
            "experience_element": "굿즈 구매와 포토 체험",
            "buzz_basis": "SNS 언급 증가",
            "internal_similarity": "2024 아트페어 연계 행사",
            "internal_performance": "집객 우수 / 체류시간 증가",
            "address": "서울 성동구 성수동",
            "main_content": "포토존, 굿즈, 작가 협업",
            "related_link_label": "공식 사이트",
        },
        {
            "id": 2,
            "collected_at": "2026-04-15",
            "event_name": "캐릭터 브랜드 팝업",
            "event_type": "팝업",
            "host_brand": "OOO 캐릭터 컴퍼니",
            "venue_name": "롯데월드몰",
            "region": "서울",
            "start_date": "2026-04-15",
            "end_date": "2026-04-28",
            "status": "진행중",
            "source_site": "뉴스",
            "source_link": "https://example.com/2",
            "source_summary": "캐릭터 브랜드 팝업 오픈 기사",
            "ai_summary": "인기 캐릭터 IP를 활용한 체험형 팝업으로 포토존과 한정 굿즈 판매가 핵심",
            "keywords": "캐릭터 IP, 체험형 팝업, 굿즈",
            "target_estimate": "2030, 가족",
            "importance": "상",
            "benchmark_value": "상",
            "lotte_idea": "자체 캐릭터 IP 개발 및 팝업 운영 검토",
            "duplicate_flag": False,
            "review_flag": True,
            "one_line_summary": "가족 고객 유입이 기대되는 캐릭터 체험형 팝업",
            "visual_feature": "캐릭터 조형물, 포토월",
            "experience_element": "스탬프 투어와 굿즈 판매",
            "buzz_basis": "오픈 초기 대기줄 발생 및 SNS 인증 확산",
            "internal_similarity": "2023 캐릭터 팝업",
            "internal_performance": "매출 우수 / 가족 방문 비중 높음",
            "address": "서울 송파구 올림픽로 300 롯데월드몰 1F",
            "main_content": "포토존, 굿즈, 체험존",
            "related_link_label": "공식 인스타그램",
        },
        {
            "id": 3,
            "collected_at": "2026-04-18",
            "event_name": "지역문화축제",
            "event_type": "지자체 행사",
            "host_brand": "부산시",
            "venue_name": "부산 시민공원",
            "region": "부산",
            "start_date": "2026-04-22",
            "end_date": "2026-05-01",
            "status": "예정",
            "source_site": "지자체 사이트",
            "source_link": "https://example.com/3",
            "source_summary": "부산 지역문화축제 일정 공지",
            "ai_summary": "지역 연계형 문화 축제로 체험 부스와 공연이 포함된 대형 행사",
            "keywords": "지역연계, 축제, 공연",
            "target_estimate": "지역고객",
            "importance": "중",
            "benchmark_value": "중",
            "lotte_idea": "로컬 협업 행사 기획 시 참고 가능",
            "duplicate_flag": False,
            "review_flag": False,
            "one_line_summary": "지역성과 체험 요소를 결합한 대형 축제",
            "visual_feature": "야외 무대 중심",
            "experience_element": "체험 부스와 지역 브랜드 참여",
            "buzz_basis": "지역 커뮤니티 확산",
            "internal_similarity": "2022 지역 상생 행사",
            "internal_performance": "인지도 상승 / 직접 매출 제한적",
            "address": "부산 부산진구 시민공원로",
            "main_content": "공연, 체험부스, 지역협업",
            "related_link_label": "행사 안내",
        },
        {
            "id": 4,
            "collected_at": "2026-04-08",
            "event_name": "백화점 아트 살롱",
            "event_type": "경쟁사 이벤트",
            "host_brand": "경쟁사백화점",
            "venue_name": "강남점 문화홀",
            "region": "수도권",
            "start_date": "2026-04-12",
            "end_date": "2026-04-30",
            "status": "진행중",
            "source_site": "경쟁사 페이지",
            "source_link": "https://example.com/4",
            "source_summary": "경쟁사 문화행사 안내",
            "ai_summary": "VIP 고객 초청형 전시와 아트 토크를 결합한 프리미엄 행사",
            "keywords": "VIP, 전시, 토크",
            "target_estimate": "VIP",
            "importance": "중",
            "benchmark_value": "상",
            "lotte_idea": "VIP 라운지 연계 프라이빗 프로그램 기획 참고",
            "duplicate_flag": False,
            "review_flag": True,
            "one_line_summary": "VIP 대상 프라이빗 전시 경험 강화 사례",
            "visual_feature": "고급 연출",
            "experience_element": "도슨트 토크와 예약제 관람",
            "buzz_basis": "언론 기사 및 커뮤니티 후기",
            "internal_similarity": "2025 VIP 아트 나이트",
            "internal_performance": "객단가 우수 / 초청 반응 좋음",
            "address": "서울 강남구",
            "main_content": "전시, 토크, 프라이빗 초청",
            "related_link_label": "공식 페이지",
        },
        {
            "id": 5,
            "collected_at": "2026-04-20",
            "event_name": "브랜드 협업 미디어전",
            "event_type": "브랜드 협업",
            "host_brand": "브랜드C x 스튜디오D",
            "venue_name": "더현대 특별관",
            "region": "서울",
            "start_date": "2026-04-25",
            "end_date": "2026-06-10",
            "status": "예정",
            "source_site": "블로그",
            "source_link": "https://example.com/5",
            "source_summary": "브랜드 협업 미디어전 예고",
            "ai_summary": "미디어아트와 브랜드 스토리텔링을 결합한 몰입형 전시",
            "keywords": "미디어아트, 협업, 몰입형",
            "target_estimate": "2030",
            "importance": "상",
            "benchmark_value": "상",
            "lotte_idea": "시즌 브랜드 캠페인과 전시형 콘텐츠 결합 가능",
            "duplicate_flag": False,
            "review_flag": False,
            "one_line_summary": "브랜드 스토리텔링을 강화한 몰입형 미디어 전시",
            "visual_feature": "LED 미디어월",
            "experience_element": "인터랙티브 체험",
            "buzz_basis": "사전 화제성 높음",
            "internal_similarity": "2024 미디어 파사드 행사",
            "internal_performance": "브랜드 인지도 상승",
            "address": "서울 영등포구 여의대로",
            "main_content": "미디어아트, 몰입형 체험, 브랜드 협업",
            "related_link_label": "관련 기사",
        },
        {
            "id": 6,
            "collected_at": "2026-04-12",
            "event_name": "지역 미식 페스티벌",
            "event_type": "기타",
            "host_brand": "지자체/민간",
            "venue_name": "대전 엑스포광장",
            "region": "대전",
            "start_date": "2026-04-19",
            "end_date": "2026-04-27",
            "status": "진행중",
            "source_site": "행사 페이지",
            "source_link": "https://example.com/6",
            "source_summary": "지역 미식 페스티벌 안내",
            "ai_summary": "푸드와 공연을 결합한 체류형 행사",
            "keywords": "푸드, 지역, 체류형",
            "target_estimate": "관광객",
            "importance": "중",
            "benchmark_value": "중",
            "lotte_idea": "식음/라이프스타일 행사에 응용 가능",
            "duplicate_flag": False,
            "review_flag": False,
            "one_line_summary": "체류 시간을 늘리는 복합형 페스티벌",
            "visual_feature": "야외 부스형",
            "experience_element": "시식과 무대 프로그램",
            "buzz_basis": "방문 인증 리뷰 증가",
            "internal_similarity": "2023 F&B 페스티벌",
            "internal_performance": "체류시간 증가 / 구매전환 보통",
            "address": "대전 유성구",
            "main_content": "푸드, 시식, 공연",
            "related_link_label": "행사 페이지",
        },
    ]

    df = pd.DataFrame(sample_rows)
    return prepare_dataframe(df)


def prepare_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    defaults = {
        "id": "",
        "collected_at": "",
        "event_name": "",
        "event_type": "기타",
        "host_brand": "",
        "venue_name": "",
        "address": "",
        "region": "기타",
        "start_date": "",
        "end_date": "",
        "status": "",
        "source_site": "",
        "source_link": "",
        "source_summary": "",
        "ai_summary": "",
        "keywords": "",
        "target_estimate": "전체",
        "importance": "중",
        "benchmark_value": "중",
        "lotte_idea": "",
        "duplicate_flag": False,
        "review_flag": False,
        "one_line_summary": "",
        "visual_feature": "",
        "experience_element": "",
        "buzz_basis": "",
        "internal_similarity": "",
        "internal_performance": "",
        "key_points": "",
        "main_contents": "",
        "host_name": "",
        "related_link": "",
    }
    for col, default in defaults.items():
        if col not in df.columns:
            df[col] = default

    df["event_type"] = df["event_type"].apply(normalize_event_type)
    df["target_estimate"] = df["target_estimate"].apply(normalize_target)
    df["start_date"] = df["start_date"].apply(parse_date)
    df["end_date"] = df["end_date"].apply(parse_date)
    df["status"] = df.apply(
        lambda r: text_or_default(r["status"], "") if text_or_default(r["status"], "") else infer_status(r["start_date"], r["end_date"]),
        axis=1,
    )
    for col in df.columns:
        if col not in ["start_date", "end_date", "duplicate_flag", "review_flag"]:
            df[col] = df[col].apply(lambda x: text_or_default(x, ""))
    df["duplicate_flag"] = df["duplicate_flag"].astype(str).str.lower().isin(["true", "1", "y", "yes"])
    df["review_flag"] = df["review_flag"].astype(str).str.lower().isin(["true", "1", "y", "yes"])
    df["importance_score"] = df["importance"].map(IMPORTANCE_SCORE).fillna(2)
    df["sort_start"] = df["start_date"].apply(lambda x: x or date.max)
    df["sort_end"] = df["end_date"].apply(lambda x: x or date.max)
    df["all_text"] = (
        df[[
            "event_name", "event_type", "host_brand", "venue_name", "region", "address", "source_summary",
            "ai_summary", "keywords", "target_estimate", "lotte_idea", "key_points", "main_contents"
        ]]
        .fillna("")
        .astype(str)
        .agg(" ".join, axis=1)
        .str.lower()
    )
    return df


def filter_dataframe(df, selected_types, region, selected_targets, start_date, end_date, keyword):
    out = df.copy()
    if selected_types:
        out = out[out["event_type"].isin(selected_types)]
    if region != "전체 지역":
        out = out[out["region"] == region]
    if selected_targets and "전체" not in selected_targets:
        out = out[out["target_estimate"].isin(selected_targets)]
    out = out[(out["start_date"] <= end_date) & (out["end_date"] >= start_date)]
    if keyword.strip():
        out = out[out["all_text"].str.contains(keyword.strip().lower(), na=False)]
    return out


def sort_events(df, mode):
    if mode == "오픈일 순":
        return df.sort_values(["sort_start", "importance_score"], ascending=[True, False])
    if mode == "종료일 임박 순":
        return df.sort_values(["sort_end", "importance_score"], ascending=[True, False])
    return df.sort_values(["importance_score", "sort_start"], ascending=[False, True])


def period_text(start_date, end_date):
    if not start_date or not end_date:
        return "-"
    return f"{start_date.strftime('%Y.%m.%d')} ~ {end_date.strftime('%Y.%m.%d')}"


def short_period_text(start_date, end_date):
    if not start_date or not end_date:
        return "-"
    return f"{start_date.strftime('%-m.%-d')}~{end_date.strftime('%-m.%-d')}" if hasattr(start_date, 'strftime') else "-"


def event_active_on(row, target_day):
    return bool(row["start_date"] and row["end_date"] and row["start_date"] <= target_day <= row["end_date"])


def collect_keywords(df):
    keywords = []
    for _, row in df.iterrows():
        combined = ",".join([
            text_or_default(row.get("keywords", ""), ""),
            text_or_default(row.get("key_points", ""), ""),
        ])
        for raw in combined.replace("/", ",").split(","):
            token = raw.strip()
            if len(token) >= 2:
                keywords.append(token)
    top = pd.Series(keywords).value_counts().head(6) if keywords else pd.Series(dtype=int)
    return list(top.index)


def build_insights(df, today):
    if df.empty:
        return {
            "summary_lines": ["선택한 조건에 맞는 이벤트가 없습니다."],
            "trend_lines": [],
            "keywords": [],
            "top_event": None,
        }

    type_counts = df["event_type"].value_counts()
    region_counts = df["region"].value_counts()
    target_counts = df["target_estimate"].value_counts()
    experiential = df["all_text"].str.contains("체험|포토|굿즈|인증|참여|인터랙티브", na=False).sum()
    collaboration = df["all_text"].str.contains("협업|콜라보|캐릭터|ip|브랜드", na=False).sum()
    top_event = df.sort_values(["importance_score", "sort_end"], ascending=[False, True]).iloc[0]

    summary_lines = [
        f"{today.strftime('%-m')}월은 '{type_counts.index[0]}' 유형이 가장 활발하게 포착되고 있어요.",
        f"{region_counts.index[0]} 지역에서의 행사 집중도가 높고, '{target_counts.index[0]}' 타깃 비중이 큽니다.",
        f"체험형·참여형 요소가 포함된 행사는 {experiential}건으로, 공간 체류를 유도하는 구성이 강세입니다.",
    ]

    trend_lines = []
    if collaboration > 0:
        trend_lines.append("브랜드 협업 또는 캐릭터 IP 연계형 사례가 꾸준히 증가하는 흐름입니다.")
    if (df["event_type"] == "팝업").sum() > 0:
        trend_lines.append("팝업은 짧은 기간 안에 화제성을 만드는 포토존·굿즈·체험존 조합이 두드러집니다.")
    if (df["event_type"] == "지자체/축제").sum() > 0:
        trend_lines.append("지자체/축제형 행사는 지역 연계성과 현장 체험 요소를 동시에 강조하는 경향이 보입니다.")

    return {
        "summary_lines": summary_lines,
        "trend_lines": trend_lines,
        "keywords": collect_keywords(df),
        "top_event": top_event,
    }


def render_sidebar(df):
    st.markdown(
        """
        <div class='sidebar-brand'>
            <div class='brand-icon'>📆</div>
            <div>
                <div class='brand-title'>이벤트 트렌드 캘린더</div>
                <div class='brand-sub'>AI 기반 이벤트·전시·팝업 트렌드 분석</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    menu_items = ["캘린더", "트렌드 요약", "인사이트 리포트", "아이디어 보드", "데이터 관리", "설정"]
    for i, item in enumerate(menu_items):
        active = "active" if i == 0 else ""
        icon = ["📅", "📊", "🧠", "💡", "🗃️", "⚙️"][i]
        st.markdown(f"<div class='side-menu-item {active}'>{icon} {item}</div>", unsafe_allow_html=True)

    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
    st.markdown("<div class='filter-head'><div class='filter-label'>필터</div><div class='small-link'>초기화</div></div>", unsafe_allow_html=True)

    event_types = sorted(set(DEFAULT_TYPES) | set(df["event_type"].unique().tolist()))
    st.markdown("<div class='filter-head'><div class='filter-label'>유형</div><div class='small-link'>전체 선택</div></div>", unsafe_allow_html=True)
    selected_types = []
    type_map = {"전시": "전시", "팝업": "팝업", "경쟁사 이벤트": "경쟁사 이벤트", "지자체/축제": "지자체/축제", "협업/브랜드": "협업/브랜드"}
    for event_type in event_types:
        checked = st.checkbox(event_type, value=True, key=f"type_{event_type}")
        if checked:
            selected_types.append(type_map.get(event_type, event_type))

    st.markdown("<div class='filter-head'><div class='filter-label'>지역</div><div class='small-link'>전체 선택</div></div>", unsafe_allow_html=True)
    regions = ["전체 지역"] + sorted(set(DEFAULT_REGIONS) | set(df["region"].unique().tolist()))
    selected_region = st.selectbox("지역 선택", regions, label_visibility="collapsed")

    st.markdown("<div class='filter-head'><div class='filter-label'>타깃</div><div class='small-link'>전체 선택</div></div>", unsafe_allow_html=True)
    selected_targets = []
    targets = [t for t in DEFAULT_TARGETS if t != "전체"] + ["전체"]
    for target in targets:
        checked = st.checkbox(target, value=(target == "전체"), key=f"target_{target}")
        if checked:
            selected_targets.append(target)

    st.markdown("<div class='filter-head'><div class='filter-label'>기간</div><div class='small-link'>직접 선택</div></div>", unsafe_allow_html=True)
    month_anchor = st.session_state.get("month_anchor", date(2026, 4, 1))
    default_range = (month_anchor.replace(day=1), date(month_anchor.year, month_anchor.month, calendar.monthrange(month_anchor.year, month_anchor.month)[1]))
    selected_range = st.date_input("기간 선택", value=default_range, label_visibility="collapsed")
    if isinstance(selected_range, tuple) and len(selected_range) == 2:
        start_date, end_date = selected_range
    else:
        start_date, end_date = default_range

    return selected_types, selected_region, selected_targets, start_date, end_date


def render_calendar_toolbar(view_mode, month_anchor, sort_mode, keyword):
    month_label = f"{month_anchor.year}년 {month_anchor.month}월"
    st.markdown(
        f"""
        <div class='calendar-shell'>
            <div class='month-toolbar'>
                <div style='display:flex; align-items:center; gap:10px; flex-wrap:wrap;'>
                    <span class='pill-btn'>◀</span>
                    <div class='month-title'>{month_label}</div>
                    <span class='pill-btn'>▶</span>
                    <span class='pill-btn {('active' if view_mode == '월' else '')}'>월</span>
                    <span class='pill-btn {('active' if view_mode == '주' else '')}'>주</span>
                    <span class='pill-btn {('active' if view_mode == '리스트' else '')}'>리스트</span>
                </div>
                <div style='display:flex; align-items:center; gap:10px; flex-wrap:wrap;'>
                    <span class='pill-btn'>오늘</span>
                    <span class='pill-btn'>필터</span>
                    <span class='pill-btn'>검색</span>
                </div>
            </div>
        """,
        unsafe_allow_html=True,
    )


def render_calendar_grid(df, month_anchor, selected_event_id):
    cal = calendar.Calendar(firstweekday=0)
    weeks = cal.monthdatescalendar(month_anchor.year, month_anchor.month)
    weekday_labels = ["월", "화", "수", "목", "금", "토", "일"]
    st.markdown("<div class='calendar-header-row'>" + "".join([
        f"<div class='calendar-header-cell' style='color:{'#2563eb' if d == '토' else '#dc2626' if d == '일' else '#111827'}'>{d}</div>" for d in weekday_labels
    ]) + "</div>", unsafe_allow_html=True)

    today = date.today()
    for week in weeks:
        row_html = "<div class='calendar-grid-row'>"
        for day in week:
            outside = "outside" if day.month != month_anchor.month else ""
            day_cls = "today" if day == today else ""
            daily = df[df.apply(lambda r: event_active_on(r, day), axis=1)].sort_values(
                ["importance_score", "sort_end"], ascending=[False, True]
            )
            cards_html = ""
            for _, row in daily.head(2).iterrows():
                border, bg = get_type_color(row["event_type"])
                cards_html += f"""
                <div class='event-chip' style='background:{bg}; border-color:{border};'>
                    <div class='event-chip-type' style='color:{border};'>{row['event_type']}</div>
                    <div class='event-chip-title'>{row['event_name']}</div>
                    <div class='event-chip-venue'>{row['venue_name']}</div>
                </div>
                """
            if len(daily) > 2:
                cards_html += f"<div class='muted' style='font-size:0.8rem;'>+ {len(daily)-2}건 더</div>"
            row_html += f"""
            <div class='calendar-cell {outside}'>
                <div class='calendar-day {day_cls}'>{day.day}</div>
                {cards_html}
            </div>
            """
        row_html += "</div>"
        st.markdown(row_html, unsafe_allow_html=True)

    legend = ""
    for label in ["전시", "팝업", "경쟁사 이벤트", "지자체/축제", "협업/브랜드"]:
        border, _ = get_type_color(label)
        legend += f"<div class='legend-item'><span class='legend-dot' style='background:{border}'></span>{label}</div>"
    st.markdown(f"<div class='legend-wrap'>{legend}</div></div>", unsafe_allow_html=True)


def render_week_view(df, anchor_date):
    week_start = anchor_date - timedelta(days=anchor_date.weekday())
    labels = [week_start + timedelta(days=i) for i in range(7)]
    st.markdown("<div class='calendar-header-row'>" + "".join([
        f"<div class='calendar-header-cell'>{d.strftime('%m.%d')} ({['월','화','수','목','금','토','일'][i]})</div>" for i, d in enumerate(labels)
    ]) + "</div>", unsafe_allow_html=True)
    st.markdown("<div class='calendar-grid-row'>" + "".join([
        f"<div class='calendar-cell'>" + "".join([
            f"<div class='event-chip' style='background:{get_type_color(r['event_type'])[1]}; border-color:{get_type_color(r['event_type'])[0]};'>"
            f"<div class='event-chip-type' style='color:{get_type_color(r['event_type'])[0]};'>{r['event_type']}</div>"
            f"<div class='event-chip-title'>{r['event_name']}</div>"
            f"<div class='event-chip-venue'>{r['venue_name']}</div></div>"
            for _, r in df[df.apply(lambda x: event_active_on(x, d), axis=1)].sort_values(['importance_score','sort_end'], ascending=[False, True]).iterrows()
        ]) + "</div>" for d in labels
    ]) + "</div></div>", unsafe_allow_html=True)


def render_list_view(df):
    for _, row in df.iterrows():
        border, bg = get_type_color(row["event_type"])
        st.markdown(
            f"""
            <div class='panel-card' style='margin-bottom:12px; border-left:6px solid {border}; background:{bg};'>
                <div style='display:flex; justify-content:space-between; gap:16px; flex-wrap:wrap;'>
                    <div>
                        <div class='detail-badge' style='background:{bg}; color:{border}; border:1px solid {border};'>{row['event_type']}</div>
                        <div style='font-size:1.2rem; font-weight:800; margin-bottom:6px;'>{row['event_name']}</div>
                        <div class='muted'>{row['venue_name']} · {row['region']} · {period_text(row['start_date'], row['end_date'])}</div>
                    </div>
                    <div style='max-width:420px;'>{text_or_default(row['one_line_summary'])}</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def pick_default_selected_id(df):
    if df.empty:
        return None
    if "selected_event_id" in st.session_state:
        existing = st.session_state["selected_event_id"]
        if (df["id"].astype(str) == str(existing)).any():
            return str(existing)
    exact = df[df["event_name"] == "캐릭터 브랜드 팝업"]
    if not exact.empty:
        picked = str(exact.iloc[0]["id"])
        st.session_state["selected_event_id"] = picked
        return picked
    picked = str(df.sort_values(["importance_score", "sort_start"], ascending=[False, True]).iloc[0]["id"])
    st.session_state["selected_event_id"] = picked
    return picked


def render_detail_panel(df, selected_id):
    st.markdown("<div class='panel-card'>", unsafe_allow_html=True)
    if df.empty or selected_id is None:
        st.info("표시할 이벤트가 없습니다.")
        st.markdown("</div>", unsafe_allow_html=True)
        return

    row = df[df["id"].astype(str) == str(selected_id)].iloc[0]
    border, bg = get_type_color(row["event_type"])
    st.markdown(
        f"<div class='detail-badge' style='background:{bg}; color:{border}; border:1px solid {border};'>{row['event_type']}</div>",
        unsafe_allow_html=True,
    )
    st.markdown(f"<div class='detail-title'>{row['event_name']}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='detail-row'>{row['venue_name']}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='detail-row'>{period_text(row['start_date'], row['end_date'])}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='detail-row'>📍 {text_or_default(row['address'])}</div>", unsafe_allow_html=True)

    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>핵심 요약</div>", unsafe_allow_html=True)
    st.write(text_or_default(row.get("ai_summary") or row.get("source_summary") or row.get("one_line_summary")))

    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>상세 정보</div>", unsafe_allow_html=True)
    st.markdown(
        f"""
        <div class='detail-grid'>
            <div class='label'>유형</div><div>{row['event_type']}</div>
            <div class='label'>타깃</div><div>{text_or_default(row['target_estimate'])}</div>
            <div class='label'>주요 콘텐츠</div><div>{text_or_default(row.get('main_contents') or row.get('key_points') or row.get('keywords'))}</div>
            <div class='label'>주최/브랜드</div><div>{text_or_default(row.get('host_name') or row.get('host_brand'))}</div>
            <div class='label'>관련 링크</div><div>{text_or_default(row.get('related_link') or row.get('source_site') or row.get('source_link'))}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>AI 인사이트</div>", unsafe_allow_html=True)
    ai_insight = row.get("buzz_basis") or "최근 유사 유형 팝업 증가와 체험형 콘텐츠 선호 트렌드에 부합하며, 유입 확대와 화제성 확보에 유리합니다."
    st.markdown(f"<div class='insight-line'>{ai_insight}</div>", unsafe_allow_html=True)
    st.markdown("<div class='insight-line'>롯데월드몰과 같은 집객형 공간에서는 높은 유동인구와의 시너지가 기대됩니다.</div>", unsafe_allow_html=True)

    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>롯데 적용 아이디어</div>", unsafe_allow_html=True)
    idea_lines = [
        text_or_default(row.get("lotte_idea"), "자체 캐릭터 IP 개발 및 시즌 팝업 운영 검토"),
        "한정 굿즈 + 체험형 콘텐츠 결합 강화",
        "SNS 인증 이벤트를 통한 바이럴 극대화",
    ]
    for line in idea_lines:
        st.markdown(f"<div class='check-line'>✓ {line}</div>", unsafe_allow_html=True)

    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>메모</div>", unsafe_allow_html=True)
    st.text_area("메모", placeholder="메모를 입력하세요...", height=90, label_visibility="collapsed")
    c1, c2 = st.columns([5, 1])
    c1.button("아이디어 보드에 추가", use_container_width=True)
    c2.button("🔖", use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)


def render_bottom_summary(df, insights):
    type_counts = df["event_type"].value_counts() if not df.empty else pd.Series(dtype=int)
    total = len(df)
    exhibition = int(type_counts.get("전시", 0))
    popup = int(type_counts.get("팝업", 0))
    local = int(type_counts.get("지자체/축제", 0))
    competitor = int(type_counts.get("경쟁사 이벤트", 0))

    col1, col2, col3 = st.columns([1.15, 1.1, 1.1])
    with col1:
        st.markdown("<div class='summary-card'>", unsafe_allow_html=True)
        st.markdown("<div class='section-title'>📌 이번 달 한눈에 보기</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='metric-big'>{total}</div><div class='metric-label'>전체 이벤트</div>", unsafe_allow_html=True)
        st.markdown(
            f"""
            <div class='mini-stat'>
                <div class='mini-stat-item'><strong style='color:#8b5cf6'>{exhibition}</strong><span class='metric-label'>전시</span></div>
                <div class='mini-stat-item'><strong style='color:#f59e0b'>{popup}</strong><span class='metric-label'>팝업</span></div>
                <div class='mini-stat-item'><strong style='color:#22c55e'>{local}</strong><span class='metric-label'>지자체/축제</span></div>
                <div class='mini-stat-item'><strong style='color:#3b82f6'>{competitor}</strong><span class='metric-label'>경쟁사 이벤트</span></div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.markdown("<div class='summary-card'>", unsafe_allow_html=True)
        st.markdown("<div class='section-title'>🧠 AI 트렌드 요약</div>", unsafe_allow_html=True)
        for line in insights["summary_lines"][:3]:
            st.markdown(f"<div class='insight-line'>• {line}</div>", unsafe_allow_html=True)
        st.markdown("<a class='report-link' href='#'>트렌드 리포트 보기 →</a>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with col3:
        st.markdown("<div class='summary-card'>", unsafe_allow_html=True)
        st.markdown("<div class='section-title'>🏷️ 주목할 만한 키워드</div>", unsafe_allow_html=True)
        for kw in insights["keywords"][:6]:
            st.markdown(f"<span class='keyword-tag'># {kw}</span>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)


def render_report_section(df, insights, current_range):
    st.markdown("### 인사이트 리포트")
    start_date, end_date = current_range
    st.markdown(
        f"<div class='panel-note'>기준 기간: {start_date.strftime('%Y-%m-%d')} ~ {end_date.strftime('%Y-%m-%d')} · 주간/월간 보고 초안으로 바로 활용할 수 있습니다.</div>",
        unsafe_allow_html=True,
    )
    st.markdown("#### 1) 한 주 요약")
    for line in insights["summary_lines"]:
        st.write(f"- {line}")
    st.markdown("#### 2) 주목할 레퍼런스 TOP 5")
    top = df.sort_values(["importance_score", "sort_start"], ascending=[False, True]).head(5)
    for _, row in top.iterrows():
        st.write(
            f"- {row['event_name']} / {row['event_type']} / {row['venue_name']} / {period_text(row['start_date'], row['end_date'])} / 적용 아이디어: {text_or_default(row['lotte_idea'])}"
        )
    st.markdown("#### 3) 액션 제안")
    st.write("- 바로 검토할 행사 3건 선정")
    st.write("- 종료 임박 행사 중 현장 방문 후보 2건 검토")
    st.write("- 다음 회의 안건: 체험형 팝업, 지역 연계 행사, IP 협업형 전시")


def main():
    st.markdown(CSS, unsafe_allow_html=True)

    with st.sidebar:
        uploaded = st.file_uploader("CSV 업로드", type=["csv"])
        if uploaded is not None:
            df = prepare_dataframe(pd.read_csv(uploaded))
        else:
            df = load_sample_data()

        if "month_anchor" not in st.session_state:
            st.session_state["month_anchor"] = date(2026, 4, 1)

        selected_types, selected_region, selected_targets, filter_start, filter_end = render_sidebar(df)

    top_left, top_mid, top_right = st.columns([1.2, 1, 1])
    with top_left:
        month_anchor = st.session_state["month_anchor"]
        nav_cols = st.columns([1, 1, 2.8])
        if nav_cols[0].button("◀", use_container_width=True):
            year = month_anchor.year if month_anchor.month > 1 else month_anchor.year - 1
            month = month_anchor.month - 1 if month_anchor.month > 1 else 12
            st.session_state["month_anchor"] = date(year, month, 1)
            month_anchor = st.session_state["month_anchor"]
        if nav_cols[1].button("▶", use_container_width=True):
            year = month_anchor.year if month_anchor.month < 12 else month_anchor.year + 1
            month = month_anchor.month + 1 if month_anchor.month < 12 else 1
            st.session_state["month_anchor"] = date(year, month, 1)
            month_anchor = st.session_state["month_anchor"]
        nav_cols[2].markdown(f"<div class='month-title' style='padding-top:6px;'>{month_anchor.year}년 {month_anchor.month}월</div>", unsafe_allow_html=True)

    with top_mid:
        view_mode = st.radio("보기", ["월", "주", "리스트"], horizontal=True, label_visibility="collapsed")
    with top_right:
        action_cols = st.columns([1.1, 1.2, 1.5])
        if action_cols[0].button("오늘", use_container_width=True):
            st.session_state["month_anchor"] = date.today().replace(day=1)
            month_anchor = st.session_state["month_anchor"]
        sort_mode = action_cols[1].selectbox("정렬", ["오픈일 순", "종료일 임박 순", "화제성 순"], label_visibility="collapsed")
        keyword = action_cols[2].text_input("검색", placeholder="검색", label_visibility="collapsed")

    month_anchor = st.session_state["month_anchor"]
    if view_mode == "월":
        current_range = (date(month_anchor.year, month_anchor.month, 1), date(month_anchor.year, month_anchor.month, calendar.monthrange(month_anchor.year, month_anchor.month)[1]))
    elif view_mode == "주":
        anchor = filter_start
        week_start = anchor - timedelta(days=anchor.weekday())
        current_range = (week_start, week_start + timedelta(days=6))
    else:
        current_range = (filter_start, filter_end)

    filtered = filter_dataframe(
        df,
        selected_types=selected_types,
        region=selected_region,
        selected_targets=selected_targets,
        start_date=max(filter_start, current_range[0]),
        end_date=min(filter_end, current_range[1]),
        keyword=keyword,
    )
    filtered = sort_events(filtered, sort_mode)
    insights = build_insights(filtered, current_range[0])
    selected_id = pick_default_selected_id(filtered)

    main_col, detail_col = st.columns([4.3, 1.35], gap="large")

    with main_col:
        st.markdown("<div class='calendar-shell'>", unsafe_allow_html=True)
        if view_mode == "월":
            render_calendar_grid(filtered, month_anchor, selected_id)
        elif view_mode == "주":
            render_week_view(filtered, current_range[0])
        else:
            render_list_view(filtered)
        render_bottom_summary(filtered, insights)
        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)
        render_report_section(filtered, insights, current_range)

    with detail_col:
        if not filtered.empty:
            options = {
                f"[{row.event_type}] {row.event_name}": str(row.id)
                for _, row in filtered.sort_values(["importance_score", "sort_start"], ascending=[False, True]).iterrows()
            }
            selected_label = st.selectbox("상세 이벤트 선택", list(options.keys()), index=list(options.values()).index(selected_id) if selected_id in options.values() else 0)
            st.session_state["selected_event_id"] = options[selected_label]
            selected_id = options[selected_label]
        render_detail_panel(filtered, selected_id)

    with st.expander("데이터 컬럼 가이드"):
        st.code(
            "id, collected_at, event_name, event_type, host_brand, venue_name, address, region, start_date, end_date, status, source_site, source_link, source_summary, ai_summary, keywords, target_estimate, importance, benchmark_value, lotte_idea, duplicate_flag, review_flag, one_line_summary, visual_feature, experience_element, buzz_basis, internal_similarity, internal_performance, key_points, main_contents, host_name, related_link",
            language="text",
        )
        export_df = filtered.copy()
        for col in ["start_date", "end_date", "sort_start", "sort_end"]:
            if col in export_df.columns:
                export_df[col] = export_df[col].astype(str)
        st.download_button(
            "현재 결과 CSV 다운로드",
            export_df.to_csv(index=False).encode("utf-8-sig"),
            file_name="event_trend_calendar_filtered.csv",
            mime="text/csv",
        )
        st.markdown("<div class='footer-note'>샘플 데이터로도 바로 실행되며, 실제 운영 시에는 Google Sheets/Airtable에서 내려받은 CSV를 연결하면 됩니다.</div>", unsafe_allow_html=True)


if __name__ == "__main__":
    main()
