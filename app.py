import calendar
from datetime import date, datetime, timedelta

import pandas as pd
import streamlit as st


st.set_page_config(
    page_title="이벤트 트렌드 캘린더",
    page_icon="📅",
    layout="wide",
)

# -----------------------------
# 상수
# -----------------------------
DEFAULT_TYPES = ["전시", "팝업", "경쟁사 이벤트", "지자체 행사", "협업/브랜드", "기타"]
DEFAULT_REGIONS = ["서울", "수도권", "부산", "대구", "광주", "대전", "기타"]
DEFAULT_TARGETS = ["2030", "가족", "VIP", "관광객", "지역고객", "전체"]

TYPE_STYLES = {
    "전시": {"bg": "#F3EEFF", "text": "#6D4CDB", "dot": "#8B5CF6"},
    "팝업": {"bg": "#FFF2E8", "text": "#E67E22", "dot": "#F59E0B"},
    "경쟁사 이벤트": {"bg": "#EEF4FF", "text": "#2563EB", "dot": "#3B82F6"},
    "지자체 행사": {"bg": "#EEF9EE", "text": "#2E9B44", "dot": "#4CAF50"},
    "협업/브랜드": {"bg": "#FCEEFF", "text": "#C442C8", "dot": "#D946EF"},
    "기타": {"bg": "#F3F4F6", "text": "#6B7280", "dot": "#9CA3AF"},
}

IMPORTANCE_SCORE = {"상": 3, "중": 2, "하": 1}


# -----------------------------
# 유틸
# -----------------------------
def to_date(value):
    if pd.isna(value) or value in ("", None):
        return None
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    try:
        return pd.to_datetime(value).date()
    except Exception:
        return None


def text_or_default(value, default="-"):
    if pd.isna(value) or value is None:
        return default
    value = str(value).strip()
    return value if value else default


def split_multi(value):
    if value is None or pd.isna(value):
        return []
    return [x.strip() for x in str(value).split(",") if x.strip()]


def contains_target(value, selected_targets):
    if not selected_targets:
        return True
    row_targets = split_multi(value)
    return any(t in row_targets for t in selected_targets)


def safe_score(value):
    return IMPORTANCE_SCORE.get(str(value).strip(), 2)


def infer_status(start_date, end_date, today=None):
    today = today or date.today()
    if start_date is None or end_date is None:
        return "예정"
    if today < start_date:
        return "예정"
    if start_date <= today <= end_date:
        return "진행중"
    return "종료"


def format_period(start_date, end_date):
    if not start_date or not end_date:
        return "-"
    return f"{start_date.strftime('%Y.%m.%d')} ~ {end_date.strftime('%Y.%m.%d')}"


def short_period(start_date, end_date):
    if not start_date or not end_date:
        return "-"
    return f"{start_date.strftime('%m.%d')}~{end_date.strftime('%m.%d')}"


def event_matches_day(row, day):
    if row["start_date"] is None or row["end_date"] is None:
        return False
    return row["start_date"] <= day <= row["end_date"]


def get_type_style(event_type):
    return TYPE_STYLES.get(event_type, TYPE_STYLES["기타"])


# -----------------------------
# 샘플 데이터
# -----------------------------
def load_sample_data():
    rows = [
        {
            "id": 1,
            "event_name": "빛의 조각들",
            "event_type": "전시",
            "host_brand": "예술의전당",
            "venue_name": "예술의전당",
            "region": "서울",
            "start_date": "2026-04-03",
            "end_date": "2026-04-20",
            "status": "진행중",
            "source_link": "https://example.com/1",
            "ai_summary": "조명과 공간 연출을 결합한 전시로 포토 포인트가 강한 사례입니다.",
            "keywords": "미디어아트, 포토존, 공간 연출",
            "target_estimate": "2030, 가족",
            "importance": "중",
            "benchmark_value": "중",
            "lotte_idea": "공간 연출형 시즌 전시에 응용 가능",
            "one_line_summary": "공간 연출형 전시, 포토 포인트 강점",
            "visual_feature": "조명 설치물, 미디어월",
            "experience_element": "포토 체험, 동선 기반 관람",
            "buzz_basis": "SNS 언급 증가",
            "internal_similarity": "2024 아트페어 연계 전시",
            "internal_performance": "체류시간 증가",
            "address": "서울 서초구 남부순환로",
            "main_content": "미디어아트, 포토존, 공간 연출",
        },
        {
            "id": 2,
            "event_name": "스누피 팝업스토어",
            "event_type": "팝업",
            "host_brand": "롯데월드몰",
            "venue_name": "롯데월드몰",
            "region": "서울",
            "start_date": "2026-04-04",
            "end_date": "2026-04-18",
            "status": "진행중",
            "source_link": "https://example.com/2",
            "ai_summary": "캐릭터 IP와 굿즈 판매를 중심으로 포토존까지 결합한 체험형 팝업입니다.",
            "keywords": "캐릭터 IP, 굿즈, 체험형 팝업",
            "target_estimate": "2030, 가족",
            "importance": "상",
            "benchmark_value": "상",
            "lotte_idea": "자체 캐릭터 협업 팝업 및 굿즈존 구성 검토",
            "one_line_summary": "캐릭터 굿즈 중심의 체험형 팝업",
            "visual_feature": "대형 캐릭터 조형물, 포토월",
            "experience_element": "굿즈 구매, 인증샷 동선",
            "buzz_basis": "SNS 인증 확산",
            "internal_similarity": "2023 캐릭터 팝업",
            "internal_performance": "가족 방문 비중 높음",
            "address": "서울 송파구 올림픽로 300 롯데월드몰",
            "main_content": "포토존, 굿즈, 체험존",
        },
        {
            "id": 3,
            "event_name": "신세계 아트페어",
            "event_type": "경쟁사 이벤트",
            "host_brand": "신세계백화점 강남",
            "venue_name": "신세계백화점 강남",
            "region": "수도권",
            "start_date": "2026-04-07",
            "end_date": "2026-04-16",
            "status": "진행중",
            "source_link": "https://example.com/3",
            "ai_summary": "백화점 공간에서 전시와 판매를 결합한 이벤트로 VIP 유입에 유리한 구조입니다.",
            "keywords": "아트페어, VIP, 경쟁사",
            "target_estimate": "VIP",
            "importance": "중",
            "benchmark_value": "상",
            "lotte_idea": "문화홀 및 VIP 대상 프리뷰 프로그램 참고",
            "one_line_summary": "전시+판매 결합형 경쟁사 이벤트",
            "visual_feature": "프리미엄 부스 구성",
            "experience_element": "도슨트, 프라이빗 관람",
            "buzz_basis": "VIP 커뮤니티 반응",
            "internal_similarity": "2025 VIP 아트 나이트",
            "internal_performance": "객단가 우수",
            "address": "서울 서초구 신반포로",
            "main_content": "전시, VIP, 판매 연계",
        },
        {
            "id": 4,
            "event_name": "미디어아트 서울 2026",
            "event_type": "전시",
            "host_brand": "DDP",
            "venue_name": "DDP",
            "region": "서울",
            "start_date": "2026-04-09",
            "end_date": "2026-04-24",
            "status": "진행중",
            "source_link": "https://example.com/4",
            "ai_summary": "몰입형 콘텐츠와 미디어월 중심의 전시로 2030 관람객 주목도가 높습니다.",
            "keywords": "미디어아트, 몰입형, 2030",
            "target_estimate": "2030",
            "importance": "중",
            "benchmark_value": "중",
            "lotte_idea": "브랜드 캠페인과 연계한 미디어 전시 구성 검토",
            "one_line_summary": "몰입형 미디어 전시",
            "visual_feature": "대형 LED, 몰입형 사운드",
            "experience_element": "인터랙티브 체험",
            "buzz_basis": "예매 반응 양호",
            "internal_similarity": "2024 미디어 파사드 행사",
            "internal_performance": "브랜드 인지도 상승",
            "address": "서울 중구 을지로",
            "main_content": "미디어월, 몰입형 체험, 디지털 전시",
        },
        {
            "id": 5,
            "event_name": "나이키 러닝 팝업",
            "event_type": "협업/브랜드",
            "host_brand": "성수 @XYZ",
            "venue_name": "성수 @XYZ",
            "region": "서울",
            "start_date": "2026-04-11",
            "end_date": "2026-04-20",
            "status": "진행중",
            "source_link": "https://example.com/5",
            "ai_summary": "체험형 콘텐츠와 브랜드 커뮤니티 결합이 강한 팝업으로 팬덤 확장에 유리합니다.",
            "keywords": "브랜드 협업, 러닝, 커뮤니티",
            "target_estimate": "2030",
            "importance": "중",
            "benchmark_value": "중",
            "lotte_idea": "체험형 클래스 및 커뮤니티 기반 팝업 기획 참고",
            "one_line_summary": "브랜드 팬덤형 체험 팝업",
            "visual_feature": "브랜드 컬러 중심 공간",
            "experience_element": "참여형 클래스",
            "buzz_basis": "커뮤니티 후기 다수",
            "internal_similarity": "2025 스포츠 브랜드 행사",
            "internal_performance": "참여 만족도 높음",
            "address": "서울 성동구 성수동",
            "main_content": "체험 클래스, 브랜드 팬덤, 협업",
        },
        {
            "id": 6,
            "event_name": "키링 체험 팝업",
            "event_type": "팝업",
            "host_brand": "더현대 서울",
            "venue_name": "더현대 서울",
            "region": "서울",
            "start_date": "2026-04-14",
            "end_date": "2026-04-22",
            "status": "진행중",
            "source_link": "https://example.com/6",
            "ai_summary": "제작 체험과 굿즈 소비를 결합한 소형 팝업으로 MZ 고객 반응이 좋습니다.",
            "keywords": "DIY, 키링, 체험형 팝업",
            "target_estimate": "2030",
            "importance": "중",
            "benchmark_value": "중",
            "lotte_idea": "소형 제작형 체험 팝업 포맷 테스트 가능",
            "one_line_summary": "제작 체험형 소형 팝업",
            "visual_feature": "컬러풀 굿즈 디스플레이",
            "experience_element": "직접 제작 체험",
            "buzz_basis": "SNS 후기 증가",
            "internal_similarity": "2024 DIY 팝업",
            "internal_performance": "참여율 양호",
            "address": "서울 영등포구 여의대로",
            "main_content": "DIY 체험, 굿즈, 인증샷",
        },
        {
            "id": 7,
            "event_name": "캐릭터 브랜드 팝업",
            "event_type": "팝업",
            "host_brand": "OOO 캐릭터 컴퍼니",
            "venue_name": "롯데월드몰",
            "region": "서울",
            "start_date": "2026-04-15",
            "end_date": "2026-04-28",
            "status": "진행중",
            "source_link": "https://example.com/7",
            "ai_summary": "인기 캐릭터 IP를 활용한 체험형 팝업으로 포토존과 한정 굿즈 판매가 결합된 행사입니다.",
            "keywords": "캐릭터 IP, 체험형 팝업, 굿즈",
            "target_estimate": "2030, 가족",
            "importance": "상",
            "benchmark_value": "상",
            "lotte_idea": "자체 캐릭터 IP 개발 및 팝업 운영 검토",
            "one_line_summary": "가족 고객 유입이 기대되는 캐릭터 체험형 팝업",
            "visual_feature": "캐릭터 조형물, 포토월",
            "experience_element": "스탬프 투어, 굿즈 판매, 인증 이벤트",
            "buzz_basis": "오픈 초기 대기줄 발생 및 SNS 인증 확산",
            "internal_similarity": "2023 캐릭터 팝업",
            "internal_performance": "매출 우수 / 가족 방문 비중 높음",
            "address": "서울 송파구 올림픽로 300 롯데월드몰 1F",
            "main_content": "포토존, 굿즈, 체험존",
        },
        {
            "id": 8,
            "event_name": "부산 원도심 축제",
            "event_type": "지자체 행사",
            "host_brand": "부산시",
            "venue_name": "부산 중구 일대",
            "region": "부산",
            "start_date": "2026-04-16",
            "end_date": "2026-04-23",
            "status": "진행중",
            "source_link": "https://example.com/8",
            "ai_summary": "지역 상권과 연계한 체험형 축제로 로컬 브랜딩 관점의 참고 가치가 있습니다.",
            "keywords": "지역 연계, 축제, 체험",
            "target_estimate": "지역고객, 관광객",
            "importance": "중",
            "benchmark_value": "중",
            "lotte_idea": "지역 협업 행사 및 상생 캠페인 구조 검토",
            "one_line_summary": "로컬 연계형 체험 축제",
            "visual_feature": "야외 무대, 지역 부스",
            "experience_element": "체험부스, 공연",
            "buzz_basis": "지역 커뮤니티 확산",
            "internal_similarity": "2022 지역 상생 행사",
            "internal_performance": "인지도 상승",
            "address": "부산 중구",
            "main_content": "지역협업, 체험부스, 공연",
        },
        {
            "id": 9,
            "event_name": "한국 현대미술 기획전",
            "event_type": "전시",
            "host_brand": "국립현대미술관",
            "venue_name": "국립현대미술관",
            "region": "서울",
            "start_date": "2026-04-18",
            "end_date": "2026-05-06",
            "status": "진행중",
            "source_link": "https://example.com/9",
            "ai_summary": "큐레이션 완성도와 공간 연출 측면의 참고 가치가 높은 기획전입니다.",
            "keywords": "현대미술, 큐레이션, 전시",
            "target_estimate": "2030, VIP",
            "importance": "중",
            "benchmark_value": "중",
            "lotte_idea": "큐레이션 구조와 도슨트 포맷 참고",
            "one_line_summary": "큐레이션 완성도 높은 전시",
            "visual_feature": "미니멀 전시 공간",
            "experience_element": "도슨트 관람",
            "buzz_basis": "전시 리뷰 증가",
            "internal_similarity": "2024 기획전",
            "internal_performance": "브랜드 호감도 상승",
            "address": "서울 종로구",
            "main_content": "큐레이션, 도슨트, 전시",
        },
        {
            "id": 10,
            "event_name": "현대백화점 문화워크",
            "event_type": "경쟁사 이벤트",
            "host_brand": "현대백화점 판교",
            "venue_name": "현대백화점 판교",
            "region": "수도권",
            "start_date": "2026-04-21",
            "end_date": "2026-04-27",
            "status": "진행중",
            "source_link": "https://example.com/10",
            "ai_summary": "매장 동선과 문화 콘텐츠를 연결한 이벤트로 체류시간 확대에 유리합니다.",
            "keywords": "문화 프로그램, 백화점 동선, 경쟁사",
            "target_estimate": "가족, 2030",
            "importance": "중",
            "benchmark_value": "중",
            "lotte_idea": "매장 동선과 연계한 체험 프로그램 설계 참고",
            "one_line_summary": "문화 콘텐츠 연계형 경쟁사 행사",
            "visual_feature": "매장 라운지 활용",
            "experience_element": "워크숍, 도슨트형 진행",
            "buzz_basis": "후기 콘텐츠 증가",
            "internal_similarity": "2025 문화 클래스",
            "internal_performance": "체류시간 증가",
            "address": "경기 성남시",
            "main_content": "체험 워크숍, 문화프로그램, 동선 연계",
        },
        {
            "id": 11,
            "event_name": "카카오프렌즈 팝업",
            "event_type": "협업/브랜드",
            "host_brand": "코엑스몰",
            "venue_name": "코엑스몰",
            "region": "서울",
            "start_date": "2026-04-23",
            "end_date": "2026-05-02",
            "status": "진행중",
            "source_link": "https://example.com/11",
            "ai_summary": "캐릭터 팬덤과 오프라인 체험을 결합한 협업형 팝업으로 바이럴 요소가 강합니다.",
            "keywords": "캐릭터 협업, 팝업, 바이럴",
            "target_estimate": "2030, 가족",
            "importance": "중",
            "benchmark_value": "상",
            "lotte_idea": "협업 캐릭터 팝업 및 SNS 인증 이벤트 강화",
            "one_line_summary": "캐릭터 협업형 바이럴 팝업",
            "visual_feature": "캐릭터 오브제, 컬러 공간",
            "experience_element": "굿즈, 포토 인증",
            "buzz_basis": "SNS 확산력 높음",
            "internal_similarity": "2024 협업 팝업",
            "internal_performance": "참여율 높음",
            "address": "서울 강남구 영동대로",
            "main_content": "캐릭터, 굿즈, 협업 바이럴",
        },
        {
            "id": 12,
            "event_name": "뷰티 브랜드 체험존",
            "event_type": "팝업",
            "host_brand": "신세계백화점 대구",
            "venue_name": "신세계백화점 대구",
            "region": "대구",
            "start_date": "2026-04-25",
            "end_date": "2026-04-30",
            "status": "진행중",
            "source_link": "https://example.com/12",
            "ai_summary": "테스트 체험과 포토존을 결합한 뷰티 팝업으로 제품 경험을 강화한 사례입니다.",
            "keywords": "뷰티, 체험존, 포토존",
            "target_estimate": "2030",
            "importance": "중",
            "benchmark_value": "중",
            "lotte_idea": "뷰티 카테고리 체험존 확대 검토",
            "one_line_summary": "제품 체험형 뷰티 팝업",
            "visual_feature": "브랜드 포토존",
            "experience_element": "테스트 체험",
            "buzz_basis": "뷰티 커뮤니티 언급",
            "internal_similarity": "2024 뷰티 위크",
            "internal_performance": "체험 만족도 양호",
            "address": "대구 동구 동부로",
            "main_content": "뷰티체험, 포토존, 샘플링",
        },
        {
            "id": 13,
            "event_name": "전주 문화주간",
            "event_type": "지자체 행사",
            "host_brand": "전주 한옥마을",
            "venue_name": "전주 한옥마을",
            "region": "기타",
            "start_date": "2026-04-27",
            "end_date": "2026-05-05",
            "status": "진행중",
            "source_link": "https://example.com/13",
            "ai_summary": "로컬 체험과 관광 동선을 결합한 행사로 지역 연계형 콘텐츠 참고 가치가 높습니다.",
            "keywords": "로컬, 지역문화, 관광",
            "target_estimate": "관광객, 지역고객",
            "importance": "하",
            "benchmark_value": "중",
            "lotte_idea": "지역 특산/문화 연계 행사 포맷 참고",
            "one_line_summary": "관광 동선 연계형 지역 문화 행사",
            "visual_feature": "전통 공간 활용",
            "experience_element": "로컬 체험",
            "buzz_basis": "지역 여행 콘텐츠 확산",
            "internal_similarity": "2023 로컬 페스티벌",
            "internal_performance": "브랜딩 효과 양호",
            "address": "전북 전주시",
            "main_content": "지역문화, 체험, 관광",
        },
        {
            "id": 14,
            "event_name": "사진, 시대를 담다",
            "event_type": "전시",
            "host_brand": "서울시립미술관",
            "venue_name": "서울시립미술관",
            "region": "서울",
            "start_date": "2026-04-29",
            "end_date": "2026-05-18",
            "status": "진행중",
            "source_link": "https://example.com/14",
            "ai_summary": "메시지 전달이 명확한 전시로 기획 의도 전달 방식이 참고할 만합니다.",
            "keywords": "사진전, 큐레이션, 메시지",
            "target_estimate": "2030, 전체",
            "importance": "중",
            "benchmark_value": "중",
            "lotte_idea": "시즌 메시지형 전시 기획 시 참고",
            "one_line_summary": "메시지 전달이 명확한 사진전",
            "visual_feature": "아카이브형 전시",
            "experience_element": "도슨트 및 감상형 관람",
            "buzz_basis": "문화 기사 노출",
            "internal_similarity": "2024 메시지형 기획전",
            "internal_performance": "브랜드 호감도 상승",
            "address": "서울 중구 덕수궁길",
            "main_content": "사진전, 감상형, 큐레이션",
        },
    ]
    df = pd.DataFrame(rows)
    return prepare_dataframe(df)


# -----------------------------
# 데이터 전처리
# -----------------------------
def prepare_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    working = df.copy()

    defaults = {
        "id": "",
        "event_name": "",
        "event_type": "기타",
        "host_brand": "",
        "venue_name": "",
        "region": "기타",
        "start_date": "",
        "end_date": "",
        "status": "",
        "source_link": "",
        "ai_summary": "",
        "keywords": "",
        "target_estimate": "전체",
        "importance": "중",
        "benchmark_value": "중",
        "lotte_idea": "",
        "one_line_summary": "",
        "visual_feature": "",
        "experience_element": "",
        "buzz_basis": "",
        "internal_similarity": "",
        "internal_performance": "",
        "address": "",
        "main_content": "",
    }

    for col, default in defaults.items():
        if col not in working.columns:
            working[col] = default

    working["start_date"] = working["start_date"].apply(to_date)
    working["end_date"] = working["end_date"].apply(to_date)

    working["status"] = working.apply(
        lambda row: infer_status(row["start_date"], row["end_date"])
        if text_or_default(row["status"], "") == ""
        else text_or_default(row["status"]),
        axis=1,
    )

    text_cols = [
        "event_name", "event_type", "host_brand", "venue_name", "region",
        "status", "source_link", "ai_summary", "keywords", "target_estimate",
        "importance", "benchmark_value", "lotte_idea", "one_line_summary",
        "visual_feature", "experience_element", "buzz_basis",
        "internal_similarity", "internal_performance", "address", "main_content",
    ]
    for col in text_cols:
        working[col] = working[col].apply(lambda x: text_or_default(x, ""))

    working["importance_score"] = working["importance"].apply(safe_score)
    working["benchmark_score"] = working["benchmark_value"].apply(safe_score)
    working["sort_start"] = working["start_date"].apply(lambda x: x or date.max)
    working["sort_end"] = working["end_date"].apply(lambda x: x or date.max)

    return working


# -----------------------------
# 필터 / 인사이트
# -----------------------------
def filter_dataframe(df, view_type, selected_date, selected_types, selected_regions, selected_targets, keyword):
    filtered = df.copy()

    if selected_types:
        filtered = filtered[filtered["event_type"].isin(selected_types)]

    if selected_regions and "전체 지역" not in selected_regions:
        filtered = filtered[filtered["region"].isin(selected_regions)]

    if selected_targets:
        filtered = filtered[filtered["target_estimate"].apply(lambda x: contains_target(x, selected_targets))]

    if keyword.strip():
        kw = keyword.strip().lower()
        search_cols = ["event_name", "venue_name", "host_brand", "ai_summary", "keywords", "lotte_idea", "main_content"]
        mask = False
        for col in search_cols:
            mask = mask | filtered[col].str.lower().str.contains(kw, na=False)
        filtered = filtered[mask]

    if view_type == "월":
        month_start = selected_date.replace(day=1)
        month_end = date(selected_date.year, selected_date.month, calendar.monthrange(selected_date.year, selected_date.month)[1])
        filtered = filtered[(filtered["start_date"] <= month_end) & (filtered["end_date"] >= month_start)]
    elif view_type == "주":
        week_start = selected_date - timedelta(days=selected_date.weekday())
        week_end = week_start + timedelta(days=6)
        filtered = filtered[(filtered["start_date"] <= week_end) & (filtered["end_date"] >= week_start)]

    return filtered.sort_values(["importance_score", "benchmark_score", "sort_start"], ascending=[False, False, True])


def build_insights(df, selected_date):
    if df.empty:
        return {
            "summary_lines": ["조건에 맞는 데이터가 없습니다."],
            "keywords": [],
        }

    type_counts = df["event_type"].value_counts()
    region_counts = df["region"].value_counts()

    experiential_keywords = ["체험", "포토", "굿즈", "인증", "몰입", "클래스"]
    experiential_count = df["ai_summary"].str.contains("|".join(experiential_keywords), case=False, na=False).sum()

    summary_lines = [
        f"{selected_date.month}월 기준 가장 활발한 유형은 '{type_counts.index[0]}'입니다.",
        f"체험형 요소가 언급된 행사는 총 {experiential_count}건입니다.",
        f"행사 밀집 권역은 '{region_counts.index[0]}'입니다.",
    ]

    keyword_pool = []
    for val in df["keywords"].tolist():
        keyword_pool.extend([x.strip() for x in str(val).split(",") if x.strip()])
    keyword_series = pd.Series(keyword_pool)
    top_keywords = keyword_series.value_counts().head(6).index.tolist() if not keyword_series.empty else []

    return {
        "summary_lines": summary_lines,
        "keywords": top_keywords,
    }


# -----------------------------
# 스타일
# -----------------------------
def inject_css():
    st.markdown(
        """
        <style>
        .stApp {
            background: #F7F7FA;
        }
        .block-container {
            max-width: 1600px;
            padding-top: 1rem;
            padding-bottom: 1rem;
        }

        .top-title {
            font-size: 30px;
            font-weight: 800;
            color: #111827;
            margin: 0;
        }

        .sub-muted {
            color: #6B7280;
            font-size: 13px;
        }

        .week-header {
            display: grid;
            grid-template-columns: repeat(7, 1fr);
            gap: 0;
            border: 1px solid #E5E7EB;
            border-bottom: none;
            border-radius: 14px 14px 0 0;
            overflow: hidden;
            background: #FFFFFF;
        }

        .week-header-cell {
            text-align: center;
            padding: 14px 0;
            font-weight: 700;
            font-size: 15px;
            border-right: 1px solid #F1F5F9;
        }

        .calendar-grid {
            display: grid;
            grid-template-columns: repeat(7, 1fr);
            gap: 0;
            border-left: 1px solid #E5E7EB;
            border-right: 1px solid #E5E7EB;
            border-bottom: 1px solid #E5E7EB;
            border-radius: 0 0 14px 14px;
            overflow: hidden;
            background: #FFFFFF;
        }

        .calendar-cell {
            min-height: 170px;
            padding: 10px 8px;
            border-top: 1px solid #E5E7EB;
            border-right: 1px solid #E5E7EB;
            background: #FFFFFF;
        }

        .calendar-cell.out-month {
            background: #F3F4F6;
        }

        .day-number {
            font-size: 14px;
            font-weight: 800;
            color: #111827;
            margin-bottom: 10px;
        }

        .event-chip {
            border-radius: 10px;
            padding: 7px 8px;
            margin-bottom: 6px;
            line-height: 1.25;
        }

        .event-type {
            font-size: 11px;
            font-weight: 800;
            margin-bottom: 3px;
        }

        .event-title {
            font-size: 12px;
            font-weight: 700;
            color: #111827;
            margin-bottom: 2px;
        }

        .event-meta {
            font-size: 11px;
            color: #4B5563;
        }

        .panel-card {
            background: #FFFFFF;
            border: 1px solid #E5E7EB;
            border-radius: 16px;
            padding: 18px;
        }

        .mini-card {
            background: #FFFFFF;
            border: 1px solid #E5E7EB;
            border-radius: 14px;
            padding: 16px;
            height: 100%;
        }

        .pill {
            display: inline-block;
            padding: 6px 11px;
            border-radius: 999px;
            font-size: 12px;
            font-weight: 700;
            margin-right: 8px;
            margin-bottom: 8px;
            background: #F3F0FF;
            color: #6D4CDB;
        }

        .legend-wrap {
            text-align: center;
            margin-top: 10px;
            margin-bottom: 4px;
        }

        .legend-item {
            display: inline-block;
            margin-right: 22px;
            color: #374151;
            font-size: 13px;
        }

        .legend-dot {
            display: inline-block;
            width: 10px;
            height: 10px;
            border-radius: 999px;
            margin-right: 6px;
            vertical-align: middle;
        }

        .info-label {
            display: inline-block;
            background: #F3F4F6;
            color: #374151;
            padding: 5px 9px;
            border-radius: 8px;
            font-size: 12px;
            font-weight: 700;
        }

        .day-events-box {
            background: #FFFFFF;
            border: 1px solid #E5E7EB;
            border-radius: 16px;
            padding: 16px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


# -----------------------------
# 사이드바
# -----------------------------
def render_sidebar(df):
    with st.sidebar:
        st.markdown("## 이벤트 트렌드 캘린더")
        st.caption("AI 기반 이벤트·전시·팝업 트렌드 분석")

        uploaded_file = st.file_uploader("CSV 업로드", type=["csv"])
        uploaded_df = None
        if uploaded_file is not None:
            try:
                uploaded_df = pd.read_csv(uploaded_file, encoding="utf-8-sig")
            except Exception:
                uploaded_file.seek(0)
                uploaded_df = pd.read_csv(uploaded_file, encoding="cp949")
            st.success(f"업로드 완료: {len(uploaded_df)}건")

        st.markdown("---")
        st.markdown("### 필터")

        all_types = sorted(set(DEFAULT_TYPES) | set(df["event_type"].dropna().tolist()))
        selected_types = []
        for t in all_types:
            checked = st.checkbox(t, value=(t != "기타"), key=f"type_{t}")
            if checked:
                selected_types.append(t)

        st.markdown("")
        all_regions = ["전체 지역"] + sorted(set(DEFAULT_REGIONS) | set(df["region"].dropna().tolist()))
        selected_regions = st.multiselect("지역", all_regions, default=["전체 지역"])

        st.markdown("")
        all_targets = DEFAULT_TARGETS
        selected_targets = []
        for t in all_targets:
            checked = st.checkbox(t, value=False, key=f"target_{t}")
            if checked:
                selected_targets.append(t)

        st.markdown("")
        keyword = st.text_input("검색", placeholder="행사명, 장소, 키워드")

        return selected_types, selected_regions, selected_targets, keyword, uploaded_df


# -----------------------------
# 캘린더 렌더
# -----------------------------
def build_month_calendar_html(df, selected_date):
    year = selected_date.year
    month = selected_date.month
    cal = calendar.Calendar(firstweekday=0)
    weeks = cal.monthdatescalendar(year, month)

    weekday_names = ["월", "화", "수", "목", "금", "토", "일"]
    weekday_colors = ["#111827", "#111827", "#111827", "#111827", "#111827", "#2563EB", "#DC2626"]

    header_html = '<div class="week-header">'
    for i, wd in enumerate(weekday_names):
        header_html += f'<div class="week-header-cell" style="color:{weekday_colors[i]};">{wd}</div>'
    header_html += "</div>"

    grid_html = '<div class="calendar-grid">'
    for week in weeks:
        for i, day in enumerate(week):
            daily = df[df.apply(lambda row: event_matches_day(row, day), axis=1)].sort_values(
                ["importance_score", "benchmark_score", "sort_end"], ascending=[False, False, True]
            )

            cell_class = "calendar-cell" if day.month == month else "calendar-cell out-month"
            day_color = weekday_colors[i]

            grid_html += f'<div class="{cell_class}">'
            grid_html += f'<div class="day-number" style="color:{day_color};">{day.day}</div>'

            if daily.empty:
                grid_html += ""
            else:
                for _, row in daily.head(3).iterrows():
                    style = get_type_style(row["event_type"])
                    grid_html += f"""
                    <div class="event-chip" style="background:{style['bg']};">
                        <div class="event-type" style="color:{style['text']};">{row['event_type']}</div>
                        <div class="event-title">{row['event_name']}</div>
                        <div class="event-meta">{row['venue_name']}</div>
                    </div>
                    """
                extra = len(daily) - 3
                if extra > 0:
                    grid_html += f'<div class="event-meta">+ {extra}건 더 있음</div>'

            grid_html += "</div>"

    grid_html += "</div>"
    return header_html + grid_html


def render_month_calendar(df, selected_date):
    st.markdown(build_month_calendar_html(df, selected_date), unsafe_allow_html=True)

    legend_html = '<div class="legend-wrap">'
    for label in ["전시", "팝업", "경쟁사 이벤트", "지자체 행사", "협업/브랜드"]:
        style = get_type_style(label)
        legend_html += (
            f'<span class="legend-item"><span class="legend-dot" style="background:{style["dot"]};"></span>{label}</span>'
        )
    legend_html += "</div>"
    st.markdown(legend_html, unsafe_allow_html=True)


def render_week_view(df, selected_date):
    week_start = selected_date - timedelta(days=selected_date.weekday())
    days = [week_start + timedelta(days=i) for i in range(7)]
    cols = st.columns(7)

    for idx, day in enumerate(days):
        with cols[idx]:
            st.markdown(f"**{day.strftime('%m.%d')}**")
            daily = df[df.apply(lambda row: event_matches_day(row, day), axis=1)]
            if daily.empty:
                st.caption("일정 없음")
            else:
                for _, row in daily.iterrows():
                    style = get_type_style(row["event_type"])
                    st.markdown(
                        f"""
                        <div style="background:{style['bg']}; border-radius:10px; padding:8px; margin-bottom:8px;">
                            <div style="font-size:11px; font-weight:800; color:{style['text']};">{row['event_type']}</div>
                            <div style="font-size:12px; font-weight:700;">{row['event_name']}</div>
                            <div style="font-size:11px; color:#4B5563;">{row['venue_name']}</div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )


def render_list_view(df):
    if df.empty:
        st.info("조건에 맞는 행사가 없습니다.")
        return

    for _, row in df.iterrows():
        style = get_type_style(row["event_type"])
        st.markdown(
            f"""
            <div class="panel-card" style="margin-bottom:10px;">
                <div style="font-size:12px; font-weight:800; color:{style['text']}; margin-bottom:5px;">{row['event_type']}</div>
                <div style="font-size:18px; font-weight:800; color:#111827;">{row['event_name']}</div>
                <div style="font-size:13px; color:#6B7280; margin-top:4px;">
                    {row['venue_name']} · {row['region']} · {short_period(row['start_date'], row['end_date'])}
                </div>
                <div style="font-size:13px; color:#374151; margin-top:8px;">
                    {text_or_default(row['one_line_summary'])}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


# -----------------------------
# 하단/우측 패널
# -----------------------------
def render_day_events_center(df, selected_day):
    daily = df[df.apply(lambda row: event_matches_day(row, selected_day), axis=1)].sort_values(
        ["importance_score", "benchmark_score", "sort_end"], ascending=[False, False, True]
    )

    st.markdown("### 선택 날짜 일정")
    st.markdown(f'<div class="sub-muted">{selected_day.strftime("%Y.%m.%d")} 기준</div>', unsafe_allow_html=True)

    if daily.empty:
        st.info("선택한 날짜에 진행 중인 일정이 없습니다.")
        return daily

    st.markdown('<div class="day-events-box">', unsafe_allow_html=True)
    for _, row in daily.iterrows():
        style = get_type_style(row["event_type"])
        st.markdown(
            f"""
            <div style="padding:10px 0; border-bottom:1px solid #F1F5F9;">
                <div style="font-size:12px; font-weight:800; color:{style['text']}; margin-bottom:4px;">
                    {row['event_type']}
                </div>
                <div style="font-size:16px; font-weight:800; color:#111827;">{row['event_name']}</div>
                <div style="font-size:13px; color:#6B7280; margin-top:4px;">
                    {row['venue_name']} · {row['region']} · {short_period(row['start_date'], row['end_date'])}
                </div>
                <div style="font-size:13px; color:#374151; margin-top:8px;">
                    {text_or_default(row['one_line_summary'])}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    st.markdown("</div>", unsafe_allow_html=True)
    return daily


def render_bottom_cards(df, insights):
    total_count = len(df)
    exhibition_count = (df["event_type"] == "전시").sum()
    popup_count = (df["event_type"] == "팝업").sum()
    municipal_count = (df["event_type"] == "지자체 행사").sum()
    competitor_count = (df["event_type"] == "경쟁사 이벤트").sum()

    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown(
            f"""
            <div class="mini-card">
                <div style="font-size:15px; font-weight:800; margin-bottom:16px;">이번 달 한눈에 보기</div>
                <div style="display:flex; gap:16px; align-items:end; flex-wrap:wrap;">
                    <div><div style="font-size:40px; font-weight:800;">{total_count}</div><div class="sub-muted">전체 이벤트</div></div>
                    <div><div style="font-size:24px; font-weight:800; color:#8B5CF6;">{exhibition_count}</div><div class="sub-muted">전시</div></div>
                    <div><div style="font-size:24px; font-weight:800; color:#F59E0B;">{popup_count}</div><div class="sub-muted">팝업</div></div>
                    <div><div style="font-size:24px; font-weight:800; color:#4CAF50;">{municipal_count}</div><div class="sub-muted">지자체</div></div>
                    <div><div style="font-size:24px; font-weight:800; color:#3B82F6;">{competitor_count}</div><div class="sub-muted">경쟁사</div></div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with c2:
        lines = "".join([f"<li style='margin-bottom:8px;'>{line}</li>" for line in insights["summary_lines"]])
        st.markdown(
            f"""
            <div class="mini-card">
                <div style="font-size:15px; font-weight:800; margin-bottom:16px;">AI 트렌드 요약</div>
                <ul style="padding-left:18px; margin:0; color:#374151; font-size:14px;">
                    {lines}
                </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with c3:
        pills = "".join([f"<span class='pill'># {kw}</span>" for kw in insights["keywords"]])
        st.markdown(
            f"""
            <div class="mini-card">
                <div style="font-size:15px; font-weight:800; margin-bottom:16px;">주목할 키워드</div>
                <div>{pills}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_right_panel(filtered_df, selected_day):
    st.markdown("### 상세 이벤트")

    daily = filtered_df[filtered_df.apply(lambda row: event_matches_day(row, selected_day), axis=1)].sort_values(
        ["importance_score", "benchmark_score", "sort_end"], ascending=[False, False, True]
    )

    if daily.empty:
        st.info("선택 날짜에 표시할 상세 이벤트가 없습니다.")
        return

    options = {f"[{row['event_type']}] {row['event_name']}": idx for idx, row in daily.iterrows()}
    selected_label = st.selectbox("상세 이벤트 선택", list(options.keys()), label_visibility="collapsed")
    row = daily.loc[options[selected_label]]

    style = get_type_style(row["event_type"])

    st.markdown(
        f"""
        <div class="panel-card">
            <div style="display:inline-block; background:{style['bg']}; color:{style['text']}; padding:6px 10px; border-radius:999px; font-size:12px; font-weight:800; margin-bottom:10px;">
                {row['event_type']}
            </div>
            <div style="font-size:20px; font-weight:800; color:#111827; margin-bottom:6px;">{row['event_name']}</div>
            <div style="font-size:14px; color:#374151; margin-bottom:6px;">{row['venue_name']}</div>
            <div style="font-size:13px; color:#6B7280; margin-bottom:6px;">{format_period(row['start_date'], row['end_date'])}</div>
            <div style="font-size:13px; color:#6B7280; margin-bottom:18px;">📍 {text_or_default(row['address'])}</div>

            <div style="font-size:15px; font-weight:800; margin-bottom:8px;">핵심 요약</div>
            <div style="font-size:14px; color:#374151; line-height:1.6; margin-bottom:18px;">{text_or_default(row['ai_summary'])}</div>

            <div style="font-size:15px; font-weight:800; margin-bottom:10px;">상세 정보</div>
            <div style="margin-bottom:8px;"><span class="info-label">유형</span> <span style="margin-left:10px;">{row['event_type']}</span></div>
            <div style="margin-bottom:8px;"><span class="info-label">타깃</span> <span style="margin-left:10px;">{row['target_estimate']}</span></div>
            <div style="margin-bottom:8px;"><span class="info-label">주요 콘텐츠</span> <span style="margin-left:10px;">{row['main_content']}</span></div>
            <div style="margin-bottom:8px;"><span class="info-label">주최/브랜드</span> <span style="margin-left:10px;">{row['host_brand']}</span></div>

            <div style="font-size:15px; font-weight:800; margin:20px 0 8px;">AI 인사이트</div>
            <div style="font-size:14px; color:#374151; line-height:1.6; margin-bottom:18px;">
                최근 {row['event_type']} 유형의 증가와 체험형 콘텐츠 선호가 함께 나타납니다.
                롯데백화점 행사 기획에 바로 참고할 수 있는 레퍼런스입니다.
            </div>

            <div style="font-size:15px; font-weight:800; margin-bottom:8px;">롯데 적용 아이디어</div>
            <div style="font-size:14px; color:#374151; line-height:1.7;">✓ {text_or_default(row['lotte_idea'])}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# -----------------------------
# 상단 바
# -----------------------------
def render_top_controls():
    selected_date = st.session_state["selected_date"]
    view_type = st.session_state["view_type"]

    c1, c2, c3, c4, c5 = st.columns([0.7, 2.4, 2.2, 1.2, 1.2])

    prev_month = (selected_date.replace(day=1) - timedelta(days=1)).replace(day=1)
    next_month = (selected_date.replace(day=28) + timedelta(days=4)).replace(day=1)

    with c1:
        if st.button("‹", use_container_width=True):
            st.session_state["selected_date"] = prev_month
            st.rerun()

    with c2:
        st.markdown(f'<div class="top-title">{selected_date.year}년 {selected_date.month}월</div>', unsafe_allow_html=True)

    with c3:
        current_index = ["월", "주", "리스트"].index(view_type)
        selected_view = st.radio(
            "보기",
            ["월", "주", "리스트"],
            index=current_index,
            horizontal=True,
            label_visibility="collapsed",
        )
        st.session_state["view_type"] = selected_view

    with c4:
        if st.button("오늘", use_container_width=True):
            st.session_state["selected_date"] = date(2026, 4, 15)
            st.session_state["selected_day"] = date(2026, 4, 15)
            st.rerun()

    with c5:
        if st.button("›", use_container_width=True):
            st.session_state["selected_date"] = next_month
            st.rerun()

    selected_day = st.date_input("선택 날짜", value=st.session_state["selected_day"])
    st.session_state["selected_day"] = selected_day


# -----------------------------
# 메인
# -----------------------------
def main():
    inject_css()

    if "selected_date" not in st.session_state:
        st.session_state["selected_date"] = date(2026, 4, 15)
    if "view_type" not in st.session_state:
        st.session_state["view_type"] = "월"
    if "selected_day" not in st.session_state:
        st.session_state["selected_day"] = date(2026, 4, 15)

    df = load_sample_data()

    selected_types, selected_regions, selected_targets, keyword, uploaded_df = render_sidebar(df)

    if uploaded_df is not None:
        try:
            df = prepare_dataframe(uploaded_df)
        except Exception as e:
            st.error(f"업로드한 CSV 처리 중 오류가 발생했습니다: {e}")
            st.stop()

    filtered = filter_dataframe(
        df=df,
        view_type=st.session_state["view_type"],
        selected_date=st.session_state["selected_date"],
        selected_types=selected_types,
        selected_regions=selected_regions,
        selected_targets=selected_targets,
        keyword=keyword,
    )

    insights = build_insights(filtered, st.session_state["selected_date"])

    main_col, right_col = st.columns([4.8, 1.7], gap="large")

    with main_col:
        render_top_controls()

        if st.session_state["view_type"] == "월":
            render_month_calendar(filtered, st.session_state["selected_date"])
        elif st.session_state["view_type"] == "주":
            render_week_view(filtered, st.session_state["selected_date"])
        else:
            render_list_view(filtered)

        st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)
        render_day_events_center(filtered, st.session_state["selected_day"])

        st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)
        render_bottom_cards(filtered, insights)

        with st.expander("데이터 테이블 보기"):
            show_cols = [
                "event_name", "event_type", "venue_name", "region",
                "start_date", "end_date", "target_estimate",
                "importance", "benchmark_value"
            ]
            st.dataframe(filtered[show_cols], use_container_width=True, hide_index=True)

    with right_col:
        render_right_panel(filtered, st.session_state["selected_day"])


if __name__ == "__main__":
    main()
