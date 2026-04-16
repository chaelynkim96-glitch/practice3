import calendar
from datetime import date, datetime, timedelta

import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="이벤트 트렌드 캘린더",
    page_icon="📆",
    layout="wide",
)

# =========================
# 기본 상수
# =========================
DEFAULT_TYPES = ["전시", "팝업", "경쟁사 이벤트", "지자체 행사", "협업/브랜드", "기타"]
DEFAULT_REGIONS = ["서울", "수도권", "부산", "대구", "광주", "대전", "기타"]
DEFAULT_TARGETS = ["2030", "가족", "VIP", "관광객", "지역고객", "전체"]
IMPORTANCE_SCORE = {"상": 3, "중": 2, "하": 1}

TYPE_COLOR_MAP = {
    "전시": {"bg": "#F2ECFF", "text": "#6D4CDB", "dot": "#8B5CF6"},
    "팝업": {"bg": "#FFF1E6", "text": "#E67E22", "dot": "#F59E0B"},
    "경쟁사 이벤트": {"bg": "#EAF2FF", "text": "#2563EB", "dot": "#3B82F6"},
    "지자체 행사": {"bg": "#EDF9EC", "text": "#2E9B44", "dot": "#4CAF50"},
    "협업/브랜드": {"bg": "#FCEEFF", "text": "#C442C8", "dot": "#D946EF"},
    "기타": {"bg": "#F3F4F6", "text": "#6B7280", "dot": "#9CA3AF"},
}

SIDEBAR_ITEMS = [
    "캘린더",
    "트렌드 요약",
    "인사이트 리포트",
    "아이디어 보드",
    "데이터 관리",
    "설정",
]


# =========================
# 유틸 함수
# =========================
def to_date(value):
    if pd.isna(value) or value in ("", None):
        return None
    if isinstance(value, date) and not isinstance(value, datetime):
        return value
    if isinstance(value, datetime):
        return value.date()
    try:
        return pd.to_datetime(value).date()
    except Exception:
        return None


def text_or_default(value, default="-"):
    if pd.isna(value) or value is None:
        return default
    value = str(value).strip()
    return value if value else default


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


def split_targets(value):
    if value is None or pd.isna(value):
        return []
    parts = [x.strip() for x in str(value).split(",")]
    return [p for p in parts if p]


def contains_target(cell_value, selected_targets):
    if not selected_targets:
        return True
    row_targets = split_targets(cell_value)
    return any(t in row_targets for t in selected_targets)


def type_style(event_type):
    return TYPE_COLOR_MAP.get(event_type, TYPE_COLOR_MAP["기타"])


def safe_score(value):
    return IMPORTANCE_SCORE.get(str(value).strip(), 2)


# =========================
# 샘플 데이터
# =========================
def load_sample_data():
    sample_rows = [
        {
            "id": 1,
            "collected_at": "2026-04-03",
            "event_name": "빛의 조각들",
            "event_type": "전시",
            "host_brand": "예술의전당",
            "venue_name": "예술의전당",
            "region": "서울",
            "start_date": "2026-04-03",
            "end_date": "2026-04-20",
            "status": "진행중",
            "source_site": "공식 사이트",
            "source_link": "https://example.com/1",
            "source_summary": "현대 작가 협업 전시",
            "ai_summary": "조명과 공간 연출을 결합한 전시로 관람 동선과 포토 포인트가 잘 설계된 사례입니다.",
            "keywords": "체험형 전시, 미디어아트, 포토존",
            "target_estimate": "2030, 가족",
            "importance": "중",
            "benchmark_value": "중",
            "lotte_idea": "체험형 공간 연출과 포토존 구조를 시즌 전시에 적용",
            "duplicate_flag": False,
            "review_flag": True,
            "one_line_summary": "공간 연출형 전시, 포토 포인트 강점",
            "visual_feature": "조명 설치물, 미디어월",
            "experience_element": "포토 체험, 동선 기반 관람",
            "buzz_basis": "SNS 언급 증가",
            "internal_similarity": "2024 아트페어 연계 전시",
            "internal_performance": "체류시간 증가",
            "address": "서울 서초구 남부순환로",
            "main_content": "미디어아트, 포토존, 공간 연출",
            "related_link_label": "공식 페이지",
            "note": "",
        },
        {
            "id": 2,
            "collected_at": "2026-04-04",
            "event_name": "스누피 팝업스토어",
            "event_type": "팝업",
            "host_brand": "롯데월드몰",
            "venue_name": "롯데월드몰",
            "region": "서울",
            "start_date": "2026-04-04",
            "end_date": "2026-04-18",
            "status": "진행중",
            "source_site": "뉴스",
            "source_link": "https://example.com/2",
            "source_summary": "캐릭터 팝업 오픈 기사",
            "ai_summary": "캐릭터 IP와 굿즈 판매를 중심으로 포토존까지 결합한 체험형 팝업입니다.",
            "keywords": "캐릭터 IP, 굿즈, 체험형 팝업",
            "target_estimate": "2030, 가족",
            "importance": "상",
            "benchmark_value": "상",
            "lotte_idea": "자체 캐릭터 협업 팝업 및 굿즈존 구성 검토",
            "duplicate_flag": False,
            "review_flag": True,
            "one_line_summary": "캐릭터 굿즈 중심의 체험형 팝업",
            "visual_feature": "대형 캐릭터 조형물, 포토월",
            "experience_element": "굿즈 구매, 인증샷 동선",
            "buzz_basis": "SNS 인증 확산",
            "internal_similarity": "2023 캐릭터 팝업",
            "internal_performance": "가족 방문 비중 높음",
            "address": "서울 송파구 올림픽로 300 롯데월드몰",
            "main_content": "포토존, 굿즈, 체험존",
            "related_link_label": "공식 인스타그램",
            "note": "",
        },
        {
            "id": 3,
            "collected_at": "2026-04-07",
            "event_name": "신세계 아트페어",
            "event_type": "경쟁사 이벤트",
            "host_brand": "신세계백화점 강남",
            "venue_name": "신세계백화점 강남",
            "region": "수도권",
            "start_date": "2026-04-07",
            "end_date": "2026-04-16",
            "status": "진행중",
            "source_site": "경쟁사 페이지",
            "source_link": "https://example.com/3",
            "source_summary": "경쟁사 문화행사 안내",
            "ai_summary": "백화점 공간에서 전시와 판매를 결합한 이벤트로 VIP 유입에 유리한 구조입니다.",
            "keywords": "아트페어, VIP, 경쟁사",
            "target_estimate": "VIP",
            "importance": "중",
            "benchmark_value": "상",
            "lotte_idea": "문화홀 및 VIP 고객 대상 프리뷰 프로그램 참고",
            "duplicate_flag": False,
            "review_flag": True,
            "one_line_summary": "전시+판매 결합형 경쟁사 이벤트",
            "visual_feature": "프리미엄 부스 구성",
            "experience_element": "도슨트, 프라이빗 관람",
            "buzz_basis": "VIP 커뮤니티 반응",
            "internal_similarity": "2025 VIP 아트 나이트",
            "internal_performance": "객단가 우수",
            "address": "서울 서초구 신반포로",
            "main_content": "전시, VIP, 판매 연계",
            "related_link_label": "공식 페이지",
            "note": "",
        },
        {
            "id": 4,
            "collected_at": "2026-04-09",
            "event_name": "미디어아트 서울 2026",
            "event_type": "전시",
            "host_brand": "DDP",
            "venue_name": "DDP",
            "region": "서울",
            "start_date": "2026-04-09",
            "end_date": "2026-04-24",
            "status": "진행중",
            "source_site": "행사 페이지",
            "source_link": "https://example.com/4",
            "source_summary": "미디어아트 기획전",
            "ai_summary": "몰입형 콘텐츠와 미디어월 중심의 전시로 2030 관람객 주목도가 높은 행사입니다.",
            "keywords": "미디어아트, 몰입형, 2030",
            "target_estimate": "2030",
            "importance": "중",
            "benchmark_value": "중",
            "lotte_idea": "브랜드 캠페인과 연계한 미디어 전시 구성 검토",
            "duplicate_flag": False,
            "review_flag": False,
            "one_line_summary": "몰입형 미디어 전시",
            "visual_feature": "대형 LED, 몰입형 사운드",
            "experience_element": "인터랙티브 체험",
            "buzz_basis": "예매 반응 양호",
            "internal_similarity": "2024 미디어 파사드 행사",
            "internal_performance": "브랜드 인지도 상승",
            "address": "서울 중구 을지로",
            "main_content": "미디어월, 몰입형 체험, 디지털 전시",
            "related_link_label": "행사 안내",
            "note": "",
        },
        {
            "id": 5,
            "collected_at": "2026-04-11",
            "event_name": "나이키 러닝 팝업",
            "event_type": "협업/브랜드",
            "host_brand": "성수 @XYZ",
            "venue_name": "성수 @XYZ",
            "region": "서울",
            "start_date": "2026-04-11",
            "end_date": "2026-04-20",
            "status": "진행중",
            "source_site": "블로그",
            "source_link": "https://example.com/5",
            "source_summary": "브랜드 러닝 팝업",
            "ai_summary": "체험형 콘텐츠와 브랜드 커뮤니티 결합이 강한 팝업으로 팬덤 확장에 유리합니다.",
            "keywords": "브랜드 협업, 러닝, 커뮤니티",
            "target_estimate": "2030",
            "importance": "중",
            "benchmark_value": "중",
            "lotte_idea": "체험형 클래스 및 커뮤니티 기반 팝업 기획 참고",
            "duplicate_flag": False,
            "review_flag": True,
            "one_line_summary": "브랜드 팬덤형 체험 팝업",
            "visual_feature": "브랜드 컬러 중심 공간",
            "experience_element": "참여형 클래스",
            "buzz_basis": "커뮤니티 후기 다수",
            "internal_similarity": "2025 스포츠 브랜드 행사",
            "internal_performance": "참여 만족도 높음",
            "address": "서울 성동구 성수동",
            "main_content": "체험 클래스, 브랜드 팬덤, 협업",
            "related_link_label": "관련 기사",
            "note": "",
        },
        {
            "id": 6,
            "collected_at": "2026-04-14",
            "event_name": "키링 체험 팝업",
            "event_type": "팝업",
            "host_brand": "더현대 서울",
            "venue_name": "더현대 서울",
            "region": "서울",
            "start_date": "2026-04-14",
            "end_date": "2026-04-22",
            "status": "진행중",
            "source_site": "인스타그램",
            "source_link": "https://example.com/6",
            "source_summary": "DIY 키링 팝업",
            "ai_summary": "제작 체험과 굿즈 소비를 결합한 소형 팝업으로 MZ 고객 반응이 좋습니다.",
            "keywords": "DIY, 키링, 체험형 팝업",
            "target_estimate": "2030",
            "importance": "중",
            "benchmark_value": "중",
            "lotte_idea": "소형 제작형 체험 팝업 포맷 테스트 가능",
            "duplicate_flag": False,
            "review_flag": False,
            "one_line_summary": "제작 체험형 소형 팝업",
            "visual_feature": "컬러풀 굿즈 디스플레이",
            "experience_element": "직접 제작 체험",
            "buzz_basis": "SNS 후기 증가",
            "internal_similarity": "2024 DIY 팝업",
            "internal_performance": "참여율 양호",
            "address": "서울 영등포구 여의대로",
            "main_content": "DIY 체험, 굿즈, 인증샷",
            "related_link_label": "공식 계정",
            "note": "",
        },
        {
            "id": 7,
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
            "source_link": "https://example.com/7",
            "source_summary": "캐릭터 브랜드 팝업 오픈 기사",
            "ai_summary": "인기 캐릭터 IP를 활용한 체험형 팝업으로 포토존과 한정 굿즈 판매가 결합된 행사입니다. SNS 인증 이벤트와 연계하여 높은 참여율을 유도합니다.",
            "keywords": "캐릭터 IP, 체험형 팝업, 굿즈",
            "target_estimate": "2030, 가족",
            "importance": "상",
            "benchmark_value": "상",
            "lotte_idea": "자체 캐릭터 IP 개발 및 팝업 운영 검토",
            "duplicate_flag": False,
            "review_flag": True,
            "one_line_summary": "가족 고객 유입이 기대되는 캐릭터 체험형 팝업",
            "visual_feature": "캐릭터 조형물, 포토월",
            "experience_element": "스탬프 투어, 굿즈 판매, 인증 이벤트",
            "buzz_basis": "오픈 초기 대기줄 발생 및 SNS 인증 확산",
            "internal_similarity": "2023 캐릭터 팝업",
            "internal_performance": "매출 우수 / 가족 방문 비중 높음",
            "address": "서울 송파구 올림픽로 300 롯데월드몰 1F",
            "main_content": "포토존, 굿즈, 체험존",
            "related_link_label": "공식 인스타그램",
            "note": "",
        },
        {
            "id": 8,
            "collected_at": "2026-04-16",
            "event_name": "부산 원도심 축제",
            "event_type": "지자체 행사",
            "host_brand": "부산시",
            "venue_name": "부산 중구 일대",
            "region": "부산",
            "start_date": "2026-04-16",
            "end_date": "2026-04-23",
            "status": "진행중",
            "source_site": "지자체 사이트",
            "source_link": "https://example.com/8",
            "source_summary": "지역 문화축제 안내",
            "ai_summary": "지역 상권과 연계한 체험형 축제로 로컬 브랜딩 관점의 참고 가치가 있습니다.",
            "keywords": "지역 연계, 축제, 체험",
            "target_estimate": "지역고객, 관광객",
            "importance": "중",
            "benchmark_value": "중",
            "lotte_idea": "지역 협업 행사 및 상생 캠페인 구조 검토",
            "duplicate_flag": False,
            "review_flag": False,
            "one_line_summary": "로컬 연계형 체험 축제",
            "visual_feature": "야외 무대, 지역 부스",
            "experience_element": "체험부스, 공연",
            "buzz_basis": "지역 커뮤니티 확산",
            "internal_similarity": "2022 지역 상생 행사",
            "internal_performance": "인지도 상승",
            "address": "부산 중구",
            "main_content": "지역협업, 체험부스, 공연",
            "related_link_label": "행사 안내",
            "note": "",
        },
        {
            "id": 9,
            "collected_at": "2026-04-18",
            "event_name": "한국 현대미술 기획전",
            "event_type": "전시",
            "host_brand": "국립현대미술관",
            "venue_name": "국립현대미술관",
            "region": "서울",
            "start_date": "2026-04-18",
            "end_date": "2026-05-06",
            "status": "진행중",
            "source_site": "미술관 사이트",
            "source_link": "https://example.com/9",
            "source_summary": "현대미술 기획전",
            "ai_summary": "브랜드 협업 요소는 약하지만 큐레이션 완성도와 공간 연출 측면의 참고 가치가 높습니다.",
            "keywords": "현대미술, 큐레이션, 전시",
            "target_estimate": "2030, VIP",
            "importance": "중",
            "benchmark_value": "중",
            "lotte_idea": "큐레이션 구조와 도슨트 포맷 참고",
            "duplicate_flag": False,
            "review_flag": True,
            "one_line_summary": "큐레이션 완성도 높은 전시",
            "visual_feature": "미니멀 전시 공간",
            "experience_element": "도슨트 관람",
            "buzz_basis": "전시 리뷰 증가",
            "internal_similarity": "2024 기획전",
            "internal_performance": "브랜드 호감도 상승",
            "address": "서울 종로구",
            "main_content": "큐레이션, 도슨트, 전시",
            "related_link_label": "전시 소개",
            "note": "",
        },
        {
            "id": 10,
            "collected_at": "2026-04-21",
            "event_name": "현대백화점 문화워크",
            "event_type": "경쟁사 이벤트",
            "host_brand": "현대백화점 판교",
            "venue_name": "현대백화점 판교",
            "region": "수도권",
            "start_date": "2026-04-21",
            "end_date": "2026-04-27",
            "status": "진행중",
            "source_site": "경쟁사 페이지",
            "source_link": "https://example.com/10",
            "source_summary": "경쟁사 문화워크 프로그램",
            "ai_summary": "매장 동선과 문화 콘텐츠를 연결한 이벤트로 체류시간 확대에 유리합니다.",
            "keywords": "문화 프로그램, 백화점 동선, 경쟁사",
            "target_estimate": "가족, 2030",
            "importance": "중",
            "benchmark_value": "중",
            "lotte_idea": "매장 동선과 연계한 체험 프로그램 설계 참고",
            "duplicate_flag": False,
            "review_flag": False,
            "one_line_summary": "문화 콘텐츠 연계형 경쟁사 행사",
            "visual_feature": "매장 라운지 활용",
            "experience_element": "워크숍, 도슨트형 진행",
            "buzz_basis": "후기 콘텐츠 증가",
            "internal_similarity": "2025 문화 클래스",
            "internal_performance": "체류시간 증가",
            "address": "경기 성남시",
            "main_content": "체험 워크숍, 문화프로그램, 동선 연계",
            "related_link_label": "공식 페이지",
            "note": "",
        },
        {
            "id": 11,
            "collected_at": "2026-04-23",
            "event_name": "카카오프렌즈 팝업",
            "event_type": "협업/브랜드",
            "host_brand": "코엑스몰",
            "venue_name": "코엑스몰",
            "region": "서울",
            "start_date": "2026-04-23",
            "end_date": "2026-05-02",
            "status": "진행중",
            "source_site": "뉴스",
            "source_link": "https://example.com/11",
            "source_summary": "협업 캐릭터 팝업",
            "ai_summary": "캐릭터 팬덤과 오프라인 체험을 결합한 협업형 팝업으로 바이럴 요소가 강합니다.",
            "keywords": "캐릭터 협업, 팝업, 바이럴",
            "target_estimate": "2030, 가족",
            "importance": "중",
            "benchmark_value": "상",
            "lotte_idea": "협업 캐릭터 팝업 및 SNS 인증 이벤트 강화",
            "duplicate_flag": False,
            "review_flag": False,
            "one_line_summary": "캐릭터 협업형 바이럴 팝업",
            "visual_feature": "캐릭터 오브제, 컬러 공간",
            "experience_element": "굿즈, 포토 인증",
            "buzz_basis": "SNS 확산력 높음",
            "internal_similarity": "2024 협업 팝업",
            "internal_performance": "참여율 높음",
            "address": "서울 강남구 영동대로",
            "main_content": "캐릭터, 굿즈, 협업 바이럴",
            "related_link_label": "관련 기사",
            "note": "",
        },
        {
            "id": 12,
            "collected_at": "2026-04-25",
            "event_name": "뷰티 브랜드 체험존",
            "event_type": "팝업",
            "host_brand": "신세계백화점 대구",
            "venue_name": "신세계백화점 대구",
            "region": "대구",
            "start_date": "2026-04-25",
            "end_date": "2026-04-30",
            "status": "진행중",
            "source_site": "브랜드 페이지",
            "source_link": "https://example.com/12",
            "source_summary": "뷰티 체험존 오픈",
            "ai_summary": "테스트 체험과 포토존을 결합한 뷰티 팝업으로 제품 경험을 강화한 사례입니다.",
            "keywords": "뷰티, 체험존, 포토존",
            "target_estimate": "2030",
            "importance": "중",
            "benchmark_value": "중",
            "lotte_idea": "뷰티 카테고리 체험존 확대 검토",
            "duplicate_flag": False,
            "review_flag": False,
            "one_line_summary": "제품 체험형 뷰티 팝업",
            "visual_feature": "브랜드 포토존",
            "experience_element": "테스트 체험",
            "buzz_basis": "뷰티 커뮤니티 언급",
            "internal_similarity": "2024 뷰티 위크",
            "internal_performance": "체험 만족도 양호",
            "address": "대구 동구 동부로",
            "main_content": "뷰티체험, 포토존, 샘플링",
            "related_link_label": "공식 페이지",
            "note": "",
        },
        {
            "id": 13,
            "collected_at": "2026-04-27",
            "event_name": "전주 문화주간",
            "event_type": "지자체 행사",
            "host_brand": "전주 한옥마을",
            "venue_name": "전주 한옥마을",
            "region": "기타",
            "start_date": "2026-04-27",
            "end_date": "2026-05-05",
            "status": "진행중",
            "source_site": "지자체 사이트",
            "source_link": "https://example.com/13",
            "source_summary": "지역 문화주간 행사",
            "ai_summary": "로컬 체험과 관광 동선을 결합한 행사로 지역 연계형 콘텐츠 참고 가치가 높습니다.",
            "keywords": "로컬, 지역문화, 관광",
            "target_estimate": "관광객, 지역고객",
            "importance": "하",
            "benchmark_value": "중",
            "lotte_idea": "지역 특산/문화 연계 행사 포맷 참고",
            "duplicate_flag": False,
            "review_flag": False,
            "one_line_summary": "관광 동선 연계형 지역 문화 행사",
            "visual_feature": "전통 공간 활용",
            "experience_element": "로컬 체험",
            "buzz_basis": "지역 여행 콘텐츠 확산",
            "internal_similarity": "2023 로컬 페스티벌",
            "internal_performance": "브랜딩 효과 양호",
            "address": "전북 전주시",
            "main_content": "지역문화, 체험, 관광",
            "related_link_label": "행사 안내",
            "note": "",
        },
        {
            "id": 14,
            "collected_at": "2026-04-29",
            "event_name": "사진, 시대를 담다",
            "event_type": "전시",
            "host_brand": "서울시립미술관",
            "venue_name": "서울시립미술관",
            "region": "서울",
            "start_date": "2026-04-29",
            "end_date": "2026-05-18",
            "status": "진행중",
            "source_site": "미술관 사이트",
            "source_link": "https://example.com/14",
            "source_summary": "사진 기획전",
            "ai_summary": "대중성과 작품성을 함께 가진 전시로 큐레이션 메시지 전달이 명확한 사례입니다.",
            "keywords": "사진전, 큐레이션, 메시지",
            "target_estimate": "2030, 전체",
            "importance": "중",
            "benchmark_value": "중",
            "lotte_idea": "시즌 메시지형 전시 기획 시 참고",
            "duplicate_flag": False,
            "review_flag": True,
            "one_line_summary": "메시지 전달이 명확한 사진전",
            "visual_feature": "아카이브형 전시",
            "experience_element": "도슨트 및 감상형 관람",
            "buzz_basis": "문화 기사 노출",
            "internal_similarity": "2024 메시지형 기획전",
            "internal_performance": "브랜드 호감도 상승",
            "address": "서울 중구 덕수궁길",
            "main_content": "사진전, 감상형, 큐레이션",
            "related_link_label": "전시 정보",
            "note": "",
        },
    ]

    df = pd.DataFrame(sample_rows)
    return prepare_dataframe(df)


# =========================
# 데이터 전처리
# =========================
def prepare_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    working = df.copy()

    required_defaults = {
        "id": "",
        "collected_at": "",
        "event_name": "",
        "event_type": "기타",
        "host_brand": "",
        "venue_name": "",
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
        "address": "",
        "main_content": "",
        "related_link_label": "관련 링크",
        "note": "",
    }

    for col, default in required_defaults.items():
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

    text_columns = [
        "event_name",
        "event_type",
        "host_brand",
        "venue_name",
        "region",
        "status",
        "source_site",
        "source_link",
        "source_summary",
        "ai_summary",
        "keywords",
        "target_estimate",
        "importance",
        "benchmark_value",
        "lotte_idea",
        "one_line_summary",
        "visual_feature",
        "experience_element",
        "buzz_basis",
        "internal_similarity",
        "internal_performance",
        "address",
        "main_content",
        "related_link_label",
        "note",
    ]
    for col in text_columns:
        working[col] = working[col].apply(lambda x: text_or_default(x, ""))

    working["duplicate_flag"] = working["duplicate_flag"].astype(str).str.lower().isin(["true", "1", "yes", "y"])
    working["review_flag"] = working["review_flag"].astype(str).str.lower().isin(["true", "1", "yes", "y"])

    working["importance_score"] = working["importance"].apply(safe_score)
    working["benchmark_score"] = working["benchmark_value"].apply(safe_score)
    working["sort_start"] = working["start_date"].apply(lambda x: x or date.max)
    working["sort_end"] = working["end_date"].apply(lambda x: x or date.max)

    return working


# =========================
# 필터 / 정렬
# =========================
def filter_dataframe(
    df: pd.DataFrame,
    view_type: str,
    selected_date: date,
    selected_types,
    selected_regions,
    selected_targets,
    date_range,
    keyword,
):
    filtered = df.copy()

    if selected_types:
        filtered = filtered[filtered["event_type"].isin(selected_types)]

    if selected_regions and "전체 지역" not in selected_regions:
        filtered = filtered[filtered["region"].isin(selected_regions)]

    if selected_targets:
        filtered = filtered[filtered["target_estimate"].apply(lambda x: contains_target(x, selected_targets))]

    if keyword.strip():
        kw = keyword.strip().lower()
        search_cols = [
            "event_name",
            "venue_name",
            "host_brand",
            "ai_summary",
            "one_line_summary",
            "keywords",
            "lotte_idea",
            "main_content",
        ]
        mask = False
        for col in search_cols:
            mask = mask | filtered[col].str.lower().str.contains(kw, na=False)
        filtered = filtered[mask]

    if date_range and len(date_range) == 2:
        start_range = date_range[0]
        end_range = date_range[1]
        filtered = filtered[
            (filtered["start_date"] <= end_range) &
            (filtered["end_date"] >= start_range)
        ]

    if view_type == "월":
        month_start = selected_date.replace(day=1)
        month_end = date(
            selected_date.year,
            selected_date.month,
            calendar.monthrange(selected_date.year, selected_date.month)[1],
        )
        filtered = filtered[
            (filtered["start_date"] <= month_end) &
            (filtered["end_date"] >= month_start)
        ]

    elif view_type == "주":
        week_start = selected_date - timedelta(days=selected_date.weekday())
        week_end = week_start + timedelta(days=6)
        filtered = filtered[
            (filtered["start_date"] <= week_end) &
            (filtered["end_date"] >= week_start)
        ]

    return filtered


def sort_dataframe(df: pd.DataFrame, sort_by: str):
    if sort_by == "오픈일 순":
        return df.sort_values(["sort_start", "importance_score"], ascending=[True, False])
    if sort_by == "종료일 임박 순":
        return df.sort_values(["sort_end", "importance_score"], ascending=[True, False])
    return df.sort_values(["importance_score", "benchmark_score", "sort_start"], ascending=[False, False, True])


def matches_day(row, target_day):
    if row["start_date"] is None or row["end_date"] is None:
        return False
    return row["start_date"] <= target_day <= row["end_date"]


# =========================
# 인사이트
# =========================
def build_insights(df: pd.DataFrame, selected_date: date):
    if df.empty:
        return {
            "summary_lines": ["조건에 맞는 데이터가 없어 인사이트를 생성할 수 없습니다."],
            "top_refs": df,
            "weekly_open": df,
            "ending_soon": df,
            "next_two_weeks": df,
            "keywords": [],
        }

    week_start = selected_date - timedelta(days=selected_date.weekday())
    week_end = week_start + timedelta(days=6)
    next_two_weeks_end = week_end + timedelta(days=14)

    weekly_open = df[(df["start_date"] >= week_start) & (df["start_date"] <= week_end)].copy()
    ending_soon = df[(df["end_date"] >= selected_date) & (df["end_date"] <= selected_date + timedelta(days=7))].copy()
    next_two_weeks = df[(df["start_date"] > week_end) & (df["start_date"] <= next_two_weeks_end)].copy()
    top_refs = df.sort_values(["importance_score", "benchmark_score", "sort_start"], ascending=[False, False, True]).head(5)

    type_counts = df["event_type"].value_counts()
    region_counts = df["region"].value_counts()

    experiential_keywords = ["체험", "포토", "굿즈", "인증", "몰입", "클래스"]
    experiential_count = df["ai_summary"].str.contains("|".join(experiential_keywords), case=False, na=False).sum()

    lines = [
        f"{selected_date.month}월은 '{type_counts.index[0]}' 유형이 가장 활발하게 관측되고 있어요.",
        f"체험형 요소가 언급된 행사는 총 {experiential_count}건으로, 참여형 콘텐츠 선호가 이어지고 있습니다.",
        f"{region_counts.index[0]} 권역 중심으로 행사 밀집도가 높습니다.",
    ]

    keyword_pool = []
    for val in df["keywords"].tolist():
        keyword_pool.extend([x.strip() for x in str(val).split(",") if x.strip()])

    keyword_series = pd.Series(keyword_pool)
    top_keywords = keyword_series.value_counts().head(6).index.tolist() if not keyword_series.empty else []

    return {
        "summary_lines": lines,
        "top_refs": top_refs,
        "weekly_open": weekly_open,
        "ending_soon": ending_soon.sort_values(["sort_end", "importance_score"], ascending=[True, False]),
        "next_two_weeks": next_two_weeks.sort_values(["sort_start", "importance_score"], ascending=[True, False]),
        "keywords": top_keywords,
    }


# =========================
# 스타일
# =========================
def inject_global_css():
    st.markdown(
        """
        <style>
        .stApp {
            background-color: #F7F7FA;
        }
        .block-container {
            padding-top: 1.2rem;
            padding-bottom: 1.2rem;
            max-width: 1600px;
        }
        .ux-card {
            background: #FFFFFF;
            border: 1px solid #E5E7EB;
            border-radius: 14px;
            padding: 16px;
        }
        .metric-card {
            background: #FFFFFF;
            border: 1px solid #E5E7EB;
            border-radius: 14px;
            padding: 18px;
            min-height: 150px;
        }
        .metric-number {
            font-size: 42px;
            font-weight: 700;
            line-height: 1.1;
            color: #111827;
        }
        .section-title {
            font-size: 15px;
            font-weight: 700;
            color: #111827;
            margin-bottom: 8px;
        }
        .small-muted {
            color: #6B7280;
            font-size: 12px;
        }
        .calendar-cell {
            background: #FFFFFF;
            border: 1px solid #E5E7EB;
            min-height: 132px;
            border-radius: 0;
            padding: 10px 8px;
        }
        .calendar-cell-out {
            background: #F3F4F6;
            border: 1px solid #E5E7EB;
            min-height: 132px;
            border-radius: 0;
            padding: 10px 8px;
        }
        .day-num {
            font-size: 14px;
            font-weight: 700;
            margin-bottom: 10px;
            color: #111827;
        }
        .legend-dot {
            display: inline-block;
            width: 10px;
            height: 10px;
            border-radius: 999px;
            margin-right: 6px;
            vertical-align: middle;
        }
        .pill {
            display: inline-block;
            background: #F3F0FF;
            color: #6D4CDB;
            padding: 7px 12px;
            border-radius: 10px;
            font-size: 13px;
            font-weight: 600;
            margin-right: 8px;
            margin-bottom: 8px;
        }
        .note-box textarea {
            min-height: 120px !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


# =========================
# 렌더 함수
# =========================
def render_top_header(selected_date, view_type):
    prev_month = (selected_date.replace(day=1) - timedelta(days=1)).replace(day=1)
    next_month = (selected_date.replace(day=28) + timedelta(days=4)).replace(day=1)

    col1, col2, col3, col4 = st.columns([0.55, 3, 2, 2])
    with col1:
        if st.button("‹", use_container_width=True):
            st.session_state["selected_date"] = prev_month
            st.rerun()

    with col2:
        st.markdown(
            f"""
            <div style="font-size:20px; font-weight:700; padding-top:8px;">
                {selected_date.year}년 {selected_date.month}월
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col3:
        view_map = {"월": 0, "주": 1, "리스트": 2}
        selected = st.radio(
            "보기",
            ["월", "주", "리스트"],
            index=view_map.get(view_type, 0),
            horizontal=True,
            label_visibility="collapsed",
        )
        st.session_state["view_type"] = selected

    with col4:
        sub1, sub2, sub3 = st.columns([1, 1, 1])
        with sub1:
            if st.button("오늘", use_container_width=True):
                st.session_state["selected_date"] = date(2026, 4, 15)
                st.rerun()
        with sub2:
            st.button("필터", use_container_width=True, disabled=True)
        with sub3:
            st.button("검색", use_container_width=True, disabled=True)

    nav_col1, nav_col2 = st.columns([0.55, 9.45])
    with nav_col1:
        if st.button("›", use_container_width=True):
            st.session_state["selected_date"] = next_month
            st.rerun()


def render_sidebar(df):
    with st.sidebar:
        st.markdown("## 이벤트 트렌드 캘린더")
        st.caption("AI 기반 이벤트·전시·팝업 트렌드 분석")

        st.markdown("---")
        for i, item in enumerate(SIDEBAR_ITEMS):
            prefix = "📅" if i == 0 else "▫️"
            if item == "캘린더":
                st.markdown(
                    f"""
                    <div style="
                        background:#ECE9FF;
                        padding:10px 14px;
                        border-radius:10px;
                        font-weight:700;
                        color:#4F46E5;
                        margin-bottom:8px;">
                        {prefix} {item}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    f"""
                    <div style="
                        padding:10px 14px;
                        border-radius:10px;
                        color:#4B5563;
                        margin-bottom:4px;">
                        {prefix} {item}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

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
        selected_regions = st.multiselect(
            "지역",
            options=all_regions,
            default=["전체 지역"],
            label_visibility="visible",
        )

        st.markdown("")
        all_targets = ["2030", "가족", "VIP", "관광객", "지역고객", "전체"]
        selected_targets = []
        for t in all_targets:
            checked = st.checkbox(t, value=False, key=f"target_{t}")
            if checked:
                selected_targets.append(t)

        st.markdown("")
        month_start = st.session_state.get("selected_date", date(2026, 4, 15)).replace(day=1)
        month_end = date(
            month_start.year,
            month_start.month,
            calendar.monthrange(month_start.year, month_start.month)[1],
        )
        date_range = st.date_input(
            "기간",
            value=(month_start, month_end),
            format="YYYY-MM-DD",
        )

        st.markdown("")
        keyword = st.text_input("검색", placeholder="행사명, 장소, 키워드 검색")

        st.markdown("")
        sort_by = st.selectbox("정렬 기준", ["화제성 순", "오픈일 순", "종료일 임박 순"])

        st.markdown("")
        uploaded_file = st.file_uploader("CSV 업로드", type=["csv"])
        uploaded_df = None

        if uploaded_file is not None:
            try:
                uploaded_df = pd.read_csv(uploaded_file, encoding="utf-8-sig")
            except Exception:
                uploaded_file.seek(0)
                uploaded_df = pd.read_csv(uploaded_file, encoding="cp949")
            st.success(f"업로드 완료: {len(uploaded_df)}건")

        return selected_types, selected_regions, selected_targets, date_range, keyword, sort_by, uploaded_df


def render_calendar(df, selected_date):
    year = selected_date.year
    month = selected_date.month

    header_cols = st.columns(7)
    weekday_names = ["월", "화", "수", "목", "금", "토", "일"]
    weekday_colors = ["#111827", "#111827", "#111827", "#111827", "#111827", "#2563EB", "#DC2626"]
    for idx, wd in enumerate(weekday_names):
        header_cols[idx].markdown(
            f"<div style='text-align:center; font-weight:700; color:{weekday_colors[idx]}; padding:8px 0;'>{wd}</div>",
            unsafe_allow_html=True,
        )

    cal = calendar.Calendar(firstweekday=0)
    weeks = cal.monthdatescalendar(year, month)

    for week in weeks:
        cols = st.columns(7)
        for idx, day in enumerate(week):
            daily = df[df.apply(lambda row: matches_day(row, day), axis=1)]
            in_month = day.month == month
            box_cls = "calendar-cell" if in_month else "calendar-cell-out"

            with cols[idx]:
                st.markdown(
                    f"""
                    <div class="{box_cls}">
                        <div class="day-num" style="color:{weekday_colors[idx]};">{day.day}</div>
                    """,
                    unsafe_allow_html=True,
                )

                if not daily.empty:
                    daily = daily.sort_values(["importance_score", "sort_end"], ascending=[False, True]).head(2)
                    for _, row in daily.iterrows():
                        style = type_style(row["event_type"])
                        st.markdown(
                            f"""
                            <div style="
                                background:{style['bg']};
                                border-radius:8px;
                                padding:8px 8px;
                                margin-bottom:8px;">
                                <div style="font-size:11px; font-weight:700; color:{style['text']}; margin-bottom:4px;">
                                    {row['event_type']}
                                </div>
                                <div style="font-size:13px; font-weight:700; color:#111827; line-height:1.25; margin-bottom:4px;">
                                    {row['event_name']}
                                </div>
                                <div style="font-size:11px; color:#4B5563; line-height:1.3;">
                                    {row['venue_name']}
                                </div>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )

                st.markdown("</div>", unsafe_allow_html=True)


def render_week_view(df, selected_date):
    week_start = selected_date - timedelta(days=selected_date.weekday())
    week_days = [week_start + timedelta(days=i) for i in range(7)]

    cols = st.columns(7)
    weekday_names = ["월", "화", "수", "목", "금", "토", "일"]

    for idx, day in enumerate(week_days):
        with cols[idx]:
            st.markdown(f"**{day.strftime('%m.%d')} ({weekday_names[idx]})**")
            daily = df[df.apply(lambda row: matches_day(row, day), axis=1)].sort_values(
                ["importance_score", "sort_end"], ascending=[False, True]
            )
            if daily.empty:
                st.caption("일정 없음")
            else:
                for _, row in daily.iterrows():
                    style = type_style(row["event_type"])
                    st.markdown(
                        f"""
                        <div style="
                            background:#FFFFFF;
                            border:1px solid #E5E7EB;
                            border-radius:12px;
                            padding:10px;
                            margin-bottom:8px;">
                            <div style="font-size:11px; font-weight:700; color:{style['text']}; margin-bottom:4px;">
                                {row['event_type']}
                            </div>
                            <div style="font-size:13px; font-weight:700; color:#111827;">
                                {row['event_name']}
                            </div>
                            <div style="font-size:11px; color:#6B7280;">
                                {row['venue_name']}
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )


def render_list_view(df):
    if df.empty:
        st.info("조건에 맞는 행사가 없습니다.")
        return

    for _, row in df.iterrows():
        style = type_style(row["event_type"])
        st.markdown(
            f"""
            <div style="
                background:#FFFFFF;
                border:1px solid #E5E7EB;
                border-radius:14px;
                padding:14px;
                margin-bottom:10px;">
                <div style="display:flex; justify-content:space-between; align-items:start; gap:10px;">
                    <div>
                        <div style="font-size:12px; font-weight:700; color:{style['text']}; margin-bottom:6px;">
                            {row['event_type']}
                        </div>
                        <div style="font-size:18px; font-weight:700; color:#111827; margin-bottom:4px;">
                            {row['event_name']}
                        </div>
                        <div style="font-size:13px; color:#6B7280; margin-bottom:6px;">
                            {row['venue_name']} · {row['region']} · {short_period(row['start_date'], row['end_date'])}
                        </div>
                        <div style="font-size:13px; color:#374151;">
                            {text_or_default(row['one_line_summary'])}
                        </div>
                    </div>
                    <div style="font-size:12px; color:#6B7280;">
                        중요도 {row['importance']}
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_legend():
    legend_html = "<div style='text-align:center; margin-top:10px; margin-bottom:8px;'>"
    for label in ["전시", "팝업", "경쟁사 이벤트", "지자체 행사", "협업/브랜드"]:
        style = type_style(label)
        legend_html += (
            f"<span style='margin-right:24px; font-size:13px; color:#374151;'>"
            f"<span class='legend-dot' style='background:{style['dot']};'></span>{label}</span>"
        )
    legend_html += "</div>"
    st.markdown(legend_html, unsafe_allow_html=True)


def render_bottom_cards(df, insights):
    total_count = len(df)
    exhibition_count = (df["event_type"] == "전시").sum()
    popup_count = (df["event_type"] == "팝업").sum()
    municipal_count = (df["event_type"] == "지자체 행사").sum()
    competitor_count = (df["event_type"] == "경쟁사 이벤트").sum()

    c1, c2, c3 = st.columns([1.15, 1.15, 1.15])

    with c1:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="section-title">🗓 이번 달 한눈에 보기</div>
                <div style="display:flex; align-items:end; gap:18px; margin-top:20px;">
                    <div>
                        <div class="metric-number">{total_count}</div>
                        <div class="small-muted">전체 이벤트</div>
                    </div>
                    <div>
                        <div style="font-size:22px; font-weight:700; color:#8B5CF6;">{exhibition_count}</div>
                        <div class="small-muted">전시</div>
                    </div>
                    <div>
                        <div style="font-size:22px; font-weight:700; color:#F59E0B;">{popup_count}</div>
                        <div class="small-muted">팝업</div>
                    </div>
                    <div>
                        <div style="font-size:22px; font-weight:700; color:#4CAF50;">{municipal_count}</div>
                        <div class="small-muted">지자체/축제</div>
                    </div>
                    <div>
                        <div style="font-size:22px; font-weight:700; color:#3B82F6;">{competitor_count}</div>
                        <div class="small-muted">경쟁사 이벤트</div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with c2:
        lines_html = "".join([f"<li style='margin-bottom:8px;'>{line}</li>" for line in insights["summary_lines"]])
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="section-title">⚙️ AI 트렌드 요약</div>
                <ul style="padding-left:18px; margin-top:14px; color:#374151; font-size:14px;">
                    {lines_html}
                </ul>
                <div style="margin-top:18px;">
                    <span style="
                        display:inline-block;
                        background:#EEF2FF;
                        color:#4F46E5;
                        padding:10px 14px;
                        border-radius:10px;
                        font-size:13px;
                        font-weight:700;">
                        트렌드 리포트 보기 →
                    </span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with c3:
        keyword_html = "".join([f"<span class='pill'># {kw}</span>" for kw in insights["keywords"][:6]])
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="section-title">✦ 주목할 만한 키워드</div>
                <div style="margin-top:18px;">
                    {keyword_html}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_right_detail_panel(df, selected_date):
    st.markdown("")

    if df.empty:
        st.info("선택 가능한 행사가 없습니다.")
        return

    default_idx = 0
    exact_matches = df[df["event_name"] == "캐릭터 브랜드 팝업"]
    if not exact_matches.empty:
        default_idx = exact_matches.index[0]

    options = {f"{row['event_name']} | {row['venue_name']}": idx for idx, row in df.iterrows()}
    option_labels = list(options.keys())

    default_position = 0
    for pos, label in enumerate(option_labels):
        if options[label] == default_idx:
            default_position = pos
            break

    selected_label = st.selectbox("행사 선택", option_labels, index=default_position, label_visibility="collapsed")
    row = df.loc[options[selected_label]]

    style = type_style(row["event_type"])

    st.markdown(
        f"""
        <div style="display:inline-block; background:{style['bg']}; color:{style['text']};
            padding:6px 10px; border-radius:10px; font-size:12px; font-weight:700; margin-bottom:10px;">
            {row['event_type']}
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(f"## {row['event_name']}")
    st.markdown(f"**{row['venue_name']}**")
    st.markdown(f"{format_period(row['start_date'], row['end_date'])}")
    st.markdown(f"📍 {text_or_default(row['address'])}")

    st.markdown("---")
    st.markdown("### 핵심 요약")
    st.write(text_or_default(row["ai_summary"]))

    st.markdown("---")
    st.markdown("### 상세 정보")

    info_rows = [
        ("유형", row["event_type"]),
        ("타깃", row["target_estimate"]),
        ("주요 콘텐츠", row["main_content"]),
        ("주최/브랜드", row["host_brand"]),
    ]

    for k, v in info_rows:
        left, right = st.columns([1, 2.2])
        with left:
            st.markdown(
                f"""
                <div style="
                    display:inline-block;
                    background:#F3F4F6;
                    color:#374151;
                    padding:5px 9px;
                    border-radius:8px;
                    font-size:12px;
                    font-weight:700;">
                    {k}
                </div>
                """,
                unsafe_allow_html=True,
            )
        with right:
            st.write(v)

    if text_or_default(row["source_link"], ""):
        left, right = st.columns([1, 2.2])
        with left:
            st.markdown(
                """
                <div style="
                    display:inline-block;
                    background:#F3F4F6;
                    color:#374151;
                    padding:5px 9px;
                    border-radius:8px;
                    font-size:12px;
                    font-weight:700;">
                    관련 링크
                </div>
                """,
                unsafe_allow_html=True,
            )
        with right:
            st.markdown(f"[{text_or_default(row['related_link_label'], '공식 링크')}]({row['source_link']})")

    st.markdown("---")
    st.markdown("### AI 인사이트")
    st.write("최근 캐릭터 IP 팝업의 증가와 체험형 콘텐츠 선호 트렌드가 뚜렷해요.")
    st.write("롯데월드몰의 높은 유동인구와 시너지가 기대됩니다.")

    st.markdown("---")
    st.markdown("### 롯데 적용 아이디어")
    idea_lines = [
        "자체 캐릭터 IP 개발 및 팝업 운영 검토",
        "한정 굿즈 + 체험형 콘텐츠 결합 강화",
        "SNS 인증 이벤트를 통한 바이럴 극대화",
    ]
    for line in idea_lines:
        st.write(f"✓ {line}")

    st.markdown("---")
    st.markdown("### 메모")
    memo_key = f"memo_{row['id']}"
    current_note = st.session_state.get(memo_key, row.get("note", ""))
    updated = st.text_area(
        "메모 입력",
        value=current_note,
        placeholder="메모를 입력하세요...",
        key=f"textarea_{row['id']}",
        label_visibility="collapsed",
    )
    st.session_state[memo_key] = updated

    c1, c2 = st.columns([5, 1])
    with c1:
        st.button("아이디어 보드에 추가", use_container_width=True)
    with c2:
        st.button("🔖", use_container_width=True)


def render_weekly_report(df, insights, selected_date):
    st.markdown("## 인사이트 리포트")
    week_start = selected_date - timedelta(days=selected_date.weekday())
    week_end = week_start + timedelta(days=6)

    st.markdown(f"**기준 주차:** {week_start.strftime('%Y-%m-%d')} ~ {week_end.strftime('%Y-%m-%d')}")
    st.markdown(f"**작성일:** {date.today().strftime('%Y-%m-%d')}")
    st.markdown("**작성 담당:** AI 초안")

    st.markdown("### 1) 한 주 요약")
    st.write(f"- 이번 주 신규 포착 행사 수: {len(insights['weekly_open'])}건")
    for line in insights["summary_lines"]:
        st.write(f"- {line}")

    st.markdown("### 2) 캘린더 핵심 일정")
    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown("**이번 주 오픈**")
        if insights["weekly_open"].empty:
            st.caption("없음")
        else:
            for _, row in insights["weekly_open"].head(5).iterrows():
                st.write(f"- {row['event_name']} / {row['venue_name']} / {short_period(row['start_date'], row['end_date'])}")

    with c2:
        st.markdown("**이번 주 종료 임박**")
        if insights["ending_soon"].empty:
            st.caption("없음")
        else:
            for _, row in insights["ending_soon"].head(5).iterrows():
                st.write(f"- {row['event_name']} / 종료일 {row['end_date']} / 벤치마킹 {row['benchmark_value']}")

    with c3:
        st.markdown("**다음 2주 내 예정**")
        if insights["next_two_weeks"].empty:
            st.caption("없음")
        else:
            for _, row in insights["next_two_weeks"].head(5).iterrows():
                st.write(f"- {row['event_name']} / 예정일 {row['start_date']} / {row['event_type']}")

    st.markdown("### 3) 주목할 레퍼런스 TOP 5")
    if insights["top_refs"].empty:
        st.info("추천 레퍼런스가 없습니다.")
    else:
        for i, (_, row) in enumerate(insights["top_refs"].iterrows(), start=1):
            with st.expander(f"TOP {i}. {row['event_name']}"):
                st.write(f"**유형:** {row['event_type']}")
                st.write(f"**장소:** {row['venue_name']} / {row['region']}")
                st.write(f"**기간:** {format_period(row['start_date'], row['end_date'])}")
                st.write(f"**주최:** {row['host_brand']}")
                st.write(f"**핵심 포인트:** {row['ai_summary']}")
                st.write(f"**왜 주목해야 하는가:** {row['buzz_basis']}")
                st.write(f"**롯데 적용 아이디어:** {row['lotte_idea']}")

    st.markdown("### 4) 액션 제안")
    top3 = insights["top_refs"].head(3)
    for _, row in top3.iterrows():
        st.write(f"- 바로 검토할 행사: {row['event_name']} / 이유: {row['lotte_idea']}")


def download_csv(df):
    export_df = df.copy()
    for col in ["start_date", "end_date", "sort_start", "sort_end"]:
        if col in export_df.columns:
            export_df[col] = export_df[col].astype(str)
    csv_bytes = export_df.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        "현재 결과 CSV 다운로드",
        csv_bytes,
        file_name="event_trend_calendar_export.csv",
        mime="text/csv",
    )


# =========================
# 메인
# =========================
def main():
    inject_global_css()

    if "selected_date" not in st.session_state:
        st.session_state["selected_date"] = date(2026, 4, 15)
    if "view_type" not in st.session_state:
        st.session_state["view_type"] = "월"

    base_df = load_sample_data()

    selected_types, selected_regions, selected_targets, date_range, keyword, sort_by, uploaded_df = render_sidebar(base_df)

    if uploaded_df is not None:
        try:
            base_df = prepare_dataframe(uploaded_df)
        except Exception as e:
            st.error(f"업로드한 CSV 처리 중 오류가 발생했습니다: {e}")
            st.stop()

    selected_date = st.session_state["selected_date"]
    view_type = st.session_state["view_type"]

    filtered = filter_dataframe(
        df=base_df,
        view_type=view_type,
        selected_date=selected_date,
        selected_types=selected_types,
        selected_regions=selected_regions,
        selected_targets=selected_targets,
        date_range=date_range,
        keyword=keyword,
    )
    filtered = sort_dataframe(filtered, sort_by)
    insights = build_insights(filtered, selected_date)

    left, center, right = st.columns([1.1, 4.3, 1.35], gap="large")

    with left:
        st.empty()

    with center:
        render_top_header(selected_date, view_type)

        if view_type == "월":
            render_calendar(filtered, selected_date)
            render_legend()
        elif view_type == "주":
            render_week_view(filtered, selected_date)
        else:
            render_list_view(filtered)

        st.markdown("<div style='height:14px;'></div>", unsafe_allow_html=True)
        render_bottom_cards(filtered, insights)

        st.markdown("<div style='height:22px;'></div>", unsafe_allow_html=True)
        with st.expander("인사이트 리포트 보기"):
            render_weekly_report(filtered, insights, selected_date)

        st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)
        with st.expander("데이터 테이블 / 다운로드"):
            show_cols = [
                "event_name", "event_type", "venue_name", "region",
                "start_date", "end_date", "target_estimate",
                "importance", "benchmark_value"
            ]
            st.dataframe(filtered[show_cols], use_container_width=True, hide_index=True)
            download_csv(filtered)

    with right:
        render_right_detail_panel(filtered, selected_date)


if __name__ == "__main__":
    main()
