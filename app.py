
import streamlit as st
import json
import re
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path
from datetime import datetime
from io import BytesIO

# BUILD: vote-record-mobile v5.53 FIVE-SPACING-ADJUSTMENTS 2026-08-25

st.set_page_config(page_title="투표록 작성 보조 앱 - 모바일", layout="centered")

DEFAULT_DB = {}
DB_FILE = Path("uploaded_station_db.json")
LOCAL_FILE = Path("polling_record_local.json")
ADMIN_FILE = Path("admin_settings.json")
APP_ACCESS_FILE = Path("app_access_settings.json")

def load_admin_password():
    if ADMIN_FILE.exists():
        try:
            data = json.loads(ADMIN_FILE.read_text(encoding="utf-8"))
            pw = str(data.get("password", "")).strip()
            if pw:
                return pw
        except Exception:
            pass
    return "1234"

def save_admin_password(password):
    ADMIN_FILE.write_text(
        json.dumps({"password": str(password)}, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )

def current_admin_password():
    return load_admin_password()

def load_app_access_password():
    if APP_ACCESS_FILE.exists():
        try:
            data = json.loads(APP_ACCESS_FILE.read_text(encoding="utf-8"))
            pw = str(data.get("password", "")).strip()
            if pw:
                return pw
        except Exception:
            pass
    return "1234"

def current_app_access_password():
    return load_app_access_password()

def save_app_access_password(password):
    APP_ACCESS_FILE.write_text(
        json.dumps({"password": str(password)}, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )

st.markdown("""
<style>
.block-container {max-width: 1380px; padding-top: 1.0rem;}
h1 {font-size: 2rem !important;}
div[data-testid="stMetricValue"] {font-size: 1.9rem;}

/* Top menu: larger boxed tabs */
button[data-baseweb="tab"] {
    border: 2px solid #222 !important;
    border-radius: 7px !important;
    padding: 10px 18px !important;
    margin-right: 8px !important;
    min-height: 52px !important;
}
button[data-baseweb="tab"] p {
    font-size: 25px !important;
    font-weight: 800 !important;
}
.stButton button {min-height: 3rem; font-size: 1.05rem; font-weight: 700;}

/* Selection labels */
div[data-testid="stSelectbox"] label p {
    color: #7b159d !important;
    font-size: 20px !important;
    font-weight: 800 !important;
}

/* Custom section boxes */
.section-row {display:flex; align-items:center; gap:18px; margin:12px 0 14px 0; flex-wrap:wrap;}
.section-box {
    display:inline-block; border:2px solid #111; border-radius:6px;
    padding:6px 14px; font-size:26px; line-height:1.15; font-weight:900; color:#111;
}
.must-select {font-size:24px; font-weight:900;}
.must-red {color:#ff1111;}
.must-blue {color:#142bdb;}
.station-name {font-size:23px; font-weight:900; color:#7b159d; margin:5px 0 10px 10px;}

/* Main data tables */
.pretty-table {width:100%; border-collapse:collapse; margin:4px 0 22px 0; table-layout:fixed;}
.pretty-table th, .pretty-table td {border:1px solid #c8c8c8; padding:8px 10px; text-align:center;}
.pretty-table th {font-size:21px; font-weight:900; background:#fafafa; color:#111;}
.pretty-table th .sub {display:block; margin-top:4px; font-size:18px; font-weight:800;}
.pretty-table td {font-size:18px; color:#111;}
.pretty-table td.election {font-weight:800;}
.pretty-table td.reg {font-size:22px; font-weight:900; color:red;}
.pretty-table td.received {font-size:22px; font-weight:900; color:blue;}
.ref-table th {font-size:18px;}
.ref-table td {font-size:18px; color:#111 !important;}
.ref-title-small {font-size:22px;}

/* Progress report screen */
.progress-title-row {display:flex; align-items:center; gap:24px; flex-wrap:wrap; margin:10px 0 18px 0;}
.progress-title-box {display:inline-block; border:2px solid #111; border-radius:6px; padding:7px 18px; font-size:28px; font-weight:900; color:#111;}
.progress-notice {font-size:24px; font-weight:900; color:#7b159d;}
.report-help {font-size:23px; font-weight:700; margin:10px 0 16px 0;}
.metric-label-red {font-size:22px; font-weight:900; color:red; margin-bottom:5px;}
.metric-label-black {font-size:22px; font-weight:900; color:#111; margin-bottom:5px;}
.metric-label-blue {font-size:22px; font-weight:900; color:#111; margin-bottom:5px;}
.progress-value-blue {font-size:34px; font-weight:900; color:blue; line-height:1.2;}
.progress-value-black {font-size:34px; font-weight:900; color:#111; line-height:1.2;}
div[data-testid="stNumberInput"] input {font-size:22px !important; font-weight:900 !important; color:red !important;}
div[data-testid="stTextInput"] input {font-size:22px !important; font-weight:900 !important; color:red !important;}


/* v1.7 final UI refinements */
div[data-baseweb="select"] > div {font-size:24px !important;}
div[data-baseweb="select"] span {font-size:24px !important;}
div[role="option"] {font-size:24px !important;}
.progress-station {font-size:25px; font-weight:900; margin:16px 0;}
.progress-station .station-purple {color:#7b159d;}
.progress-station .station-black {color:#111;}
.report-instruction {font-size:23px; font-weight:900; color:#111; margin:24px 0;}
.report-instruction .red-part {color:red;}
.bottom-report-notice {font-size:23px; font-weight:900; color:#111; margin:28px 0 12px 0;}
.bottom-report-notice .blue-part {color:blue;}


/* v1.8 - top navigation enlarged */
div[data-testid="stTabs"] button[data-baseweb="tab"],
div[data-testid="stTabs"] button[data-baseweb="tab"] *,
div[data-testid="stTabs"] [role="tab"],
div[data-testid="stTabs"] [role="tab"] * {
    font-size: 24px !important;
    font-weight: 800 !important;
    line-height: 1.35 !important;
}
div[data-testid="stTabs"] button[data-baseweb="tab"] {
    padding: 12px 15px !important;
    min-height: 58px !important;
}


/* v1.9 moved reference section */
.reference-title-box {
    display:inline-block;
    border:2px solid #111;
    border-radius:6px;
    padding:7px 16px;
    margin-bottom:14px;
    color:#111;
    font-weight:900;
}
.reference-title-box .reference-big {
    font-size:28px;
}
.reference-title-box .reference-rest {
    font-size:22px;
}
.reference-table {
    width:100%;
    border-collapse:collapse;
    font-size:18px;
    color:#111;
}
.reference-table th, .reference-table td {
    border:1px solid #c7c7c7;
    padding:10px 12px;
    text-align:center;
}
.reference-table th {
    font-weight:900;
}
.reference-table td:first-child {
    font-weight:800;
}


/* v1.9.3 */
.selected-station-confirm {
    margin-top:18px;
    padding:16px 20px;
    border:2px solid #7b159d;
    border-radius:8px;
    background:#f7f2fb;
    font-size:22px;
    font-weight:800;
}
.selected-station-confirm .arrow {
    color:#7b159d;
    font-size:30px;
    margin-right:10px;
}
.selected-station-confirm .selected-name {
    color:#7b159d;
    font-size:25px;
    font-weight:900;
    text-decoration:underline;
    text-underline-offset:4px;
}
.input-calc-box {
    border:2px solid #1836d8;
    border-radius:8px;
    padding:18px 20px 14px 20px;
    margin-top:12px;
}
.input-calc-title {
    text-align:center;
    font-size:24px;
    font-weight:900;
    margin-bottom:14px;
}
.inbox-help {
    margin-top:12px;
    font-size:19px;
    font-weight:800;
}
.notice-left {
    text-align:left !important;
    font-size:21px;
    font-weight:900;
    margin-top:16px;
}
.two-line-gap {height:3.2rem;}
.polling-name-banner {
    border:2px solid #1836d8;
    border-radius:8px;
    padding:10px 16px;
    margin:4px 0 16px 0;
    font-size:22px;
    font-weight:900;
}
.polling-name-banner .name {
    color:#7b159d;
    font-size:25px;
    text-decoration:underline;
    text-underline-offset:4px;
}
.record-section {
    border:1.5px solid #8abf72;
    border-radius:8px;
    padding:10px 12px;
    margin-bottom:16px;
}
.record-section.blue { border-color:#6aa0ff; }
.record-title {
    font-size:23px;
    font-weight:900;
    margin-bottom:10px;
}
.record-table {
    width:100%;
    border-collapse:collapse;
    table-layout:fixed;
    font-size:15px;
}
.record-table th, .record-table td {
    border:1px solid #c8c8c8;
    padding:8px 7px;
    text-align:center;
    vertical-align:middle;
}
.record-table th {font-weight:900; background:#fafafa;}


/* v1.9.5 실제 Streamlit 입력/산출 컨테이너 */
.st-key-report_input_calc_box {
    border: 2px solid #1836d8 !important;
    border-radius: 8px !important;
    padding: 18px 20px 14px 20px !important;
    margin-top: 12px !important;
    margin-bottom: 8px !important;
}
.st-key-report_input_calc_box > div {
    border: none !important;
}



/* v1.9.8 상단 진행단계 */
div[data-testid="stRadio"] > div[role="radiogroup"] {
    display:flex !important;
    align-items:center !important;
    gap:18px !important;
    flex-wrap:wrap !important;
}

/* 모든 라디오 기본 */
div[data-testid="stRadio"] label {
    position:relative !important;
    font-size:24px !important;
    font-weight:900 !important;
    line-height:1.25 !important;
    white-space:nowrap !important;
}

/* ①~④만 네모박스 */
div[data-testid="stRadio"] label:nth-of-type(1),
div[data-testid="stRadio"] label:nth-of-type(2),
div[data-testid="stRadio"] label:nth-of-type(3),
div[data-testid="stRadio"] label:nth-of-type(4) {
    border:2px solid #7b159d !important;
    border-radius:8px !important;
    padding:12px 18px !important;
    background:white !important;
}

/* 선택된 ①~④ */
div[data-testid="stRadio"] label:nth-of-type(1):has(input:checked),
div[data-testid="stRadio"] label:nth-of-type(2):has(input:checked),
div[data-testid="stRadio"] label:nth-of-type(3):has(input:checked),
div[data-testid="stRadio"] label:nth-of-type(4):has(input:checked) {
    border-color:#ff3b30 !important;
    color:#ff3b30 !important;
    background:#fff7f6 !important;
}

/* ①→②→③→④ 사이 화살표 */
div[data-testid="stRadio"] label:nth-of-type(1)::after,
div[data-testid="stRadio"] label:nth-of-type(2)::after,
div[data-testid="stRadio"] label:nth-of-type(3)::after {
    content:"➜";
    position:absolute;
    right:-36px;
    top:50%;
    transform:translateY(-50%);
    color:#7b159d;
    font-size:28px;
    font-weight:900;
    pointer-events:none;
}

/* 관리자: 박스/화살표 없음 */
div[data-testid="stRadio"] label:nth-of-type(5) {
    border:none !important;
    background:transparent !important;
    padding:10px 4px !important;
    color:#111 !important;
}
div[data-testid="stRadio"] label:nth-of-type(5)::after {
    content:none !important;
}

/* radio 원형 버튼은 작게 */
div[data-testid="stRadio"] label > div:first-child {
    transform:scale(1.08);
}


/* v1.9.9 기초자료 입력 표 */
.entry-table-header {
    display:grid;
    border:1px solid #b9b9b9;
    border-bottom:none;
    background:#fafafa;
    font-weight:900;
    font-size:15px;
    text-align:center;
    align-items:stretch;
    margin-top:8px;
}
.entry-table-header > div {
    border-right:1px solid #c7c7c7;
    padding:10px 6px;
    display:flex;
    align-items:center;
    justify-content:center;
    min-height:72px;
}
.entry-table-header > div:last-child {border-right:none;}
.a-grid {grid-template-columns:1.35fr 1.35fr 1.1fr 1.1fr 1.1fr 1.2fr 1fr;}
.j-grid {grid-template-columns:1.25fr 1.2fr 1.15fr 1.35fr 1fr 1fr 1.45fr;}
.entry-static {
    min-height:42px;
    border:1px solid #c8c8c8;
    display:flex;
    align-items:center;
    justify-content:center;
    font-weight:700;
    background:white;
    padding:5px 4px;
    text-align:center;
}
.serial-cell {font-size:14px;}
.section-gap {height:24px;}


/* v2.0 입력표 */
.j-grid-v20 {
    grid-template-columns:1.2fr 1.2fr 1.1fr 1.35fr 1fr 1fr 1.45fr;
}
.a-grid-v20 {
    grid-template-columns:1.35fr 1.35fr 1.1fr 1.1fr 1.1fr 1.2fr 1fr;
}

/* 훼손 등 미교부 일련번호 입력칸: 다른 입력란보다 2px 작게 */
div[data-testid="stTextInput"]:has(input[aria-label="훼손 등 미교부한 투표용지 일련번호"]) input {
    font-size:20px !important;
}


/* v2.0.4 진행단계 화살표 가시성 수정 */
div[data-testid="stRadio"] > div[role="radiogroup"] {
    overflow: visible !important;
    column-gap: 34px !important;
}
div[data-testid="stRadio"] label:nth-of-type(1),
div[data-testid="stRadio"] label:nth-of-type(2),
div[data-testid="stRadio"] label:nth-of-type(3),
div[data-testid="stRadio"] label:nth-of-type(4) {
    overflow: visible !important;
    position: relative !important;
}
div[data-testid="stRadio"] label:nth-of-type(1)::after,
div[data-testid="stRadio"] label:nth-of-type(2)::after,
div[data-testid="stRadio"] label:nth-of-type(3)::after {
    content: "➜" !important;
    display: block !important;
    position: absolute !important;
    right: -31px !important;
    left: auto !important;
    top: 50% !important;
    transform: translateY(-52%) !important;
    width: 27px !important;
    height: 30px !important;
    line-height: 30px !important;
    text-align: center !important;
    color: #7b159d !important;
    background: #ffffff !important;
    font-size: 27px !important;
    font-weight: 900 !important;
    z-index: 9999 !important;
    opacity: 1 !important;
    visibility: visible !important;
    overflow: visible !important;
}
div[data-testid="stRadio"] label:nth-of-type(4)::after,
div[data-testid="stRadio"] label:nth-of-type(5)::before,
div[data-testid="stRadio"] label:nth-of-type(5)::after {
    content: none !important;
    display: none !important;
}
/* 관리자는 박스/화살표 없이 굵은 글자만 */
div[data-testid="stRadio"] label:nth-of-type(5) {
    border: none !important;
    background: transparent !important;
    box-shadow: none !important;
    padding-left: 0 !important;
    padding-right: 0 !important;
    font-weight: 900 !important;
}


/* ============================================================
   모바일 전용 legacy-mobile
   ============================================================ */
@media (max-width: 768px) {
    .stApp {
        min-width: 0 !important;
    }

    .block-container {
        max-width: 100% !important;
        padding-top: 0.75rem !important;
        padding-left: 0.65rem !important;
        padding-right: 0.65rem !important;
        padding-bottom: 2rem !important;
    }

    h1 {
        font-size: 25px !important;
        line-height: 1.25 !important;
        margin-bottom: 0.25rem !important;
    }

    h2 {
        font-size: 23px !important;
        line-height: 1.3 !important;
    }

    h3 {
        font-size: 21px !important;
    }

    p, .stCaption, div[data-testid="stCaptionContainer"] {
        font-size: 14px !important;
        line-height: 1.45 !important;
    }

    /* 상단 ①~④ 진행단계 */
    div[data-testid="stRadio"] > div[role="radiogroup"] {
        display: grid !important;
        grid-template-columns: 1fr 1fr !important;
        gap: 9px !important;
        overflow: visible !important;
        margin-bottom: 12px !important;
    }

    div[data-testid="stRadio"] label {
        width: 100% !important;
        min-width: 0 !important;
        justify-content: center !important;
        font-size: 16px !important;
        line-height: 1.25 !important;
        padding: 10px 7px !important;
        text-align: center !important;
    }

    div[data-testid="stRadio"] label:nth-of-type(1)::after,
    div[data-testid="stRadio"] label:nth-of-type(2)::after,
    div[data-testid="stRadio"] label:nth-of-type(3)::after {
        content: none !important;
        display: none !important;
    }

    /* [관리자]는 모바일에서 별도 한 줄 */
    div[data-testid="stRadio"] label:nth-of-type(5) {
        grid-column: 1 / -1 !important;
        width: auto !important;
        justify-self: end !important;
        font-size: 16px !important;
        padding: 5px 3px !important;
    }

    /* 투표소명 */
    .polling-name-banner,
    .selected-station-confirm,
    .progress-station {
        font-size: 19px !important;
        padding: 11px 12px !important;
        margin-top: 9px !important;
        margin-bottom: 12px !important;
    }

    .polling-name-banner .name,
    .selected-station-confirm .selected-name,
    .progress-station .station-purple {
        font-size: 21px !important;
    }

    .section-box,
    .progress-title-box,
    .reference-title-box {
        font-size: 20px !important;
        padding: 7px 11px !important;
    }

    .must-select,
    .must-red,
    .must-blue {
        font-size: 17px !important;
        line-height: 1.45 !important;
    }

    /* selectbox / text input */
    div[data-baseweb="select"] > div,
    div[data-baseweb="select"] span,
    div[role="option"] {
        font-size: 18px !important;
    }

    div[data-testid="stTextInput"] input,
    div[data-testid="stNumberInput"] input {
        font-size: 18px !important;
        min-height: 44px !important;
    }

    /* 보고용 박스 */
    .st-key-report_input_calc_box {
        padding: 12px 10px !important;
        border-width: 2px !important;
    }

    .input-calc-title {
        font-size: 20px !important;
        line-height: 1.3 !important;
    }

    .metric-label-red,
    .metric-label-blue,
    .metric-label-black {
        font-size: 17px !important;
    }

    .progress-value-blue,
    .progress-value-black {
        font-size: 28px !important;
    }

    .inbox-help,
    .notice-left,
    .bottom-report-notice {
        font-size: 16px !important;
        line-height: 1.45 !important;
    }

    /* ③ 입력 화면: 각 선거별 입력행을 모바일 카드처럼 보이게 */
    div[data-testid="stHorizontalBlock"] {
        gap: 0.35rem !important;
    }

    div[data-testid="column"] {
        min-width: 0 !important;
    }

    .entry-table-header {
        display: none !important;
    }

    .entry-static {
        min-height: 42px !important;
        font-size: 15px !important;
        padding: 6px 4px !important;
    }

    .serial-cell {
        font-size: 13px !important;
    }

    /* 표는 모바일에서 좌우 스크롤 */
    .record-section,
    .record-section.blue {
        overflow-x: auto !important;
        -webkit-overflow-scrolling: touch !important;
        padding: 7px !important;
    }

    .record-table {
        min-width: 760px !important;
        width: 760px !important;
        font-size: 13px !important;
    }

    .record-table th,
    .record-table td {
        padding: 6px 5px !important;
    }

    .reference-table {
        min-width: 620px !important;
        width: 620px !important;
        font-size: 13px !important;
    }

    /* Streamlit markdown 내부 표도 좌우 스크롤 */
    div[data-testid="stMarkdownContainer"]:has(table) {
        overflow-x: auto !important;
        -webkit-overflow-scrolling: touch !important;
    }

    /* 버튼 터치 영역 */
    .stButton button {
        min-height: 44px !important;
        font-size: 17px !important;
        font-weight: 800 !important;
    }

    /* 관리자 화면 */
    div[data-testid="stFileUploader"] {
        font-size: 15px !important;
    }

    /* 알림 */
    div[data-testid="stAlert"] {
        font-size: 15px !important;
    }
}

/* 모바일 전용에서는 데스크톱에서도 화면 폭을 과도하게 넓히지 않음 */
.block-container {
    max-width: 860px;
}


/* ============================================================
   모바일 legacy-mobile - 상단 진행단계 가독성 개선
   ============================================================ */
@media (max-width: 768px) {
    div[data-testid="stRadio"] > div[role="radiogroup"] {
        display:grid !important;
        grid-template-columns:1fr 1fr !important;
        gap:10px 12px !important;
        overflow:visible !important;
        padding:2px 0 6px 0 !important;
    }

    div[data-testid="stRadio"] label {
        width:100% !important;
        min-width:0 !important;
        min-height:58px !important;
        justify-content:center !important;
        align-items:center !important;
        border-radius:8px !important;
        padding:10px 8px !important;
        font-size:18px !important;
        font-weight:900 !important;
        line-height:1.35 !important;
        white-space:normal !important;
        text-align:center !important;
        overflow:visible !important;
    }

    div[data-testid="stRadio"] label *,
    div[data-testid="stRadio"] label p,
    div[data-testid="stRadio"] label span {
        font-size:18px !important;
        font-weight:900 !important;
        line-height:1.35 !important;
        white-space:normal !important;
        overflow:visible !important;
        text-overflow:clip !important;
    }

    /* 모바일은 2열 배치이므로 화살표는 겹치지 않도록 숨김 */
    div[data-testid="stRadio"] label:nth-of-type(1)::after,
    div[data-testid="stRadio"] label:nth-of-type(2)::after,
    div[data-testid="stRadio"] label:nth-of-type(3)::after,
    div[data-testid="stRadio"] label:nth-of-type(4)::after {
        content:none !important;
        display:none !important;
    }

    /* 관리자: 네모박스 없이 오른쪽 정렬 */
    div[data-testid="stRadio"] label:nth-of-type(5) {
        grid-column:1 / -1 !important;
        justify-self:end !important;
        width:auto !important;
        min-height:36px !important;
        border:none !important;
        background:transparent !important;
        box-shadow:none !important;
        padding:4px 2px !important;
        font-size:18px !important;
        font-weight:900 !important;
    }

    div[data-testid="stRadio"] label:nth-of-type(5) * {
        font-size:18px !important;
        font-weight:900 !important;
    }
}


/* legacy-mobile - ④ 투표록 참고표 숫자 가독성 */
.record-table tbody td {
    font-size:16px !important;
    font-weight:700 !important;
}
.record-table tbody td:first-child {
    font-weight:800 !important;
}
@media (max-width:768px) {
    .record-table tbody td {
        font-size:14px !important;
        font-weight:700 !important;
    }
}

/* legacy-mobile 상단 제목 잘림 방지 + 진행 안내문 */
.block-container {
    overflow: visible !important;
}
h1, h1 * {
    line-height: 1.35 !important;
    overflow: visible !important;
    padding-top: 0.12em !important;
    padding-bottom: 0.12em !important;
}
.workflow-guide {
    margin: 8px 0 16px 0;
    padding: 10px 12px;
    border: 1px solid #f0d98b;
    border-radius: 8px;
    background: #fffbea;
    font-size: 20px;
    line-height: 1.45;
    font-weight: 800;
    text-align: center;
}
.workflow-guide .first-step {
    color: red;
    font-weight: 900;
}
.workflow-guide .next-steps {
    color: blue;
    font-weight: 900;
}


/* v2.3 상단 메뉴: 동그라미 번호 + [ ] 강조(보라색), [관리자]는 검정색 */
div[data-testid="stRadio"] label:nth-of-type(1) p,
div[data-testid="stRadio"] label:nth-of-type(2) p,
div[data-testid="stRadio"] label:nth-of-type(3) p,
div[data-testid="stRadio"] label:nth-of-type(4) p,
div[data-testid="stRadio"] label:nth-of-type(5) p {
    font-size: 0 !important;
    line-height: 1.25 !important;
}

div[data-testid="stRadio"] label:nth-of-type(1) p::before {
    content: "①[선택]";
    color: #7b159d;
    font-size: 24px;
    font-weight: 900;
}
div[data-testid="stRadio"] label:nth-of-type(1) p::after {
    content: " 투표소";
    color: #111;
    font-size: 24px;
    font-weight: 800;
}

div[data-testid="stRadio"] label:nth-of-type(2) p::before {
    content: "②[보고]";
    color: #7b159d;
    font-size: 24px;
    font-weight: 900;
}
div[data-testid="stRadio"] label:nth-of-type(2) p::after {
    content: " 투표진행상황";
    color: #111;
    font-size: 24px;
    font-weight: 800;
}

div[data-testid="stRadio"] label:nth-of-type(3) p::before {
    content: "③[입력]";
    color: #7b159d;
    font-size: 24px;
    font-weight: 900;
}
div[data-testid="stRadio"] label:nth-of-type(3) p::after {
    content: " 투표록 기초자료";
    color: #111;
    font-size: 24px;
    font-weight: 800;
}

div[data-testid="stRadio"] label:nth-of-type(4) p::before {
    content: "④[작성참고]";
    color: #7b159d;
    font-size: 24px;
    font-weight: 900;
}
div[data-testid="stRadio"] label:nth-of-type(4) p::after {
    content: " 투표록 2p 작성";
    color: #111;
    font-size: 24px;
    font-weight: 800;
}

div[data-testid="stRadio"] label:nth-of-type(5) p::before {
    content: "[관리자]";
    color: #111;
    font-size: 24px;
    font-weight: 900;
}

@media (max-width: 768px) {
    div[data-testid="stRadio"] label:nth-of-type(1) p::before,
    div[data-testid="stRadio"] label:nth-of-type(1) p::after,
    div[data-testid="stRadio"] label:nth-of-type(2) p::before,
    div[data-testid="stRadio"] label:nth-of-type(2) p::after,
    div[data-testid="stRadio"] label:nth-of-type(3) p::before,
    div[data-testid="stRadio"] label:nth-of-type(3) p::after,
    div[data-testid="stRadio"] label:nth-of-type(4) p::before,
    div[data-testid="stRadio"] label:nth-of-type(4) p::after,
    div[data-testid="stRadio"] label:nth-of-type(5) p::before {
        font-size: 18px !important;
        font-weight: 900 !important;
        line-height: 1.35 !important;
    }
}

@media (max-width: 768px) {
    .block-container {
        padding-top: 1.15rem !important;
    }
    h1, h1 * {
        line-height: 1.4 !important;
        overflow: visible !important;
        padding-top: 0.16em !important;
        padding-bottom: 0.16em !important;
    }
    .workflow-guide {
        font-size: 16px !important;
        line-height: 1.5 !important;
        padding: 9px 10px !important;
        margin-top: 6px !important;
        margin-bottom: 14px !important;
    }
}


/* v2.4 최종 보정: Streamlit 상단 툴바에 제목이 가려지지 않도록 충분한 여백 확보 */
.block-container {
    padding-top: 4.25rem !important;
    overflow: visible !important;
}
div[data-testid="stAppViewContainer"] > .main {
    overflow: visible !important;
}
h1, h1 *, div[data-testid="stHeadingWithActionElements"] h1 {
    line-height: 1.5 !important;
    overflow: visible !important;
    padding-top: 0.18em !important;
    padding-bottom: 0.18em !important;
    margin-top: 0 !important;
}

/* v2.4 메뉴 강조색 강제 적용 */
div[data-testid="stRadio"] label:nth-of-type(1) p::before,
div[data-testid="stRadio"] label:nth-of-type(2) p::before,
div[data-testid="stRadio"] label:nth-of-type(3) p::before,
div[data-testid="stRadio"] label:nth-of-type(4) p::before {
    color: #7b159d !important;
    font-weight: 900 !important;
}
div[data-testid="stRadio"] label:nth-of-type(1) p::after,
div[data-testid="stRadio"] label:nth-of-type(2) p::after,
div[data-testid="stRadio"] label:nth-of-type(3) p::after,
div[data-testid="stRadio"] label:nth-of-type(4) p::after {
    color: #111 !important;
    font-weight: 800 !important;
}
div[data-testid="stRadio"] label:nth-of-type(5) p::before {
    color: #111 !important;
    font-weight: 900 !important;
}

@media (max-width: 768px) {
    .block-container {
        padding-top: 4.6rem !important;
    }
    h1, h1 *, div[data-testid="stHeadingWithActionElements"] h1 {
        line-height: 1.5 !important;
        padding-top: 0.2em !important;
        padding-bottom: 0.2em !important;
    }
}


/* ============================================================
   v2.5 최종 화면 보정
   - Streamlit 고정 툴바와 무관한 사용자 정의 제목
   - 메뉴 ①~④ + [ ] 문구 보라색/굵게 강제 표시
   - [관리자] 검정색
   ============================================================ */
.app-main-title {
    display:block !important;
    position:relative !important;
    z-index:1 !important;
    margin:0 0 12px 0 !important;
    padding:8px 0 6px 0 !important;
    font-size:34px !important;
    line-height:1.45 !important;
    font-weight:900 !important;
    color:#20232a !important;
    overflow:visible !important;
    white-space:normal !important;
}

/* 상단 고정 툴바 아래로 본문을 충분히 내림 */
.block-container {
    padding-top:5.4rem !important;
    overflow:visible !important;
}

/* 기존 Streamlit 라디오 원문을 숨기고 원하는 문구를 재구성 */
div[data-testid="stRadio"] label:nth-of-type(1) div[data-testid="stMarkdownContainer"] p,
div[data-testid="stRadio"] label:nth-of-type(2) div[data-testid="stMarkdownContainer"] p,
div[data-testid="stRadio"] label:nth-of-type(3) div[data-testid="stMarkdownContainer"] p,
div[data-testid="stRadio"] label:nth-of-type(4) div[data-testid="stMarkdownContainer"] p,
div[data-testid="stRadio"] label:nth-of-type(5) div[data-testid="stMarkdownContainer"] p {
    font-size:0 !important;
    color:transparent !important;
    white-space:nowrap !important;
}

div[data-testid="stRadio"] label:nth-of-type(1) div[data-testid="stMarkdownContainer"] p::before {
    content:"①[선택]";
    color:#7b159d !important;
    font-size:24px !important;
    font-weight:900 !important;
}
div[data-testid="stRadio"] label:nth-of-type(1) div[data-testid="stMarkdownContainer"] p::after {
    content:" 투표소";
    color:#111 !important;
    font-size:24px !important;
    font-weight:800 !important;
}

div[data-testid="stRadio"] label:nth-of-type(2) div[data-testid="stMarkdownContainer"] p::before {
    content:"②[보고]";
    color:#7b159d !important;
    font-size:24px !important;
    font-weight:900 !important;
}
div[data-testid="stRadio"] label:nth-of-type(2) div[data-testid="stMarkdownContainer"] p::after {
    content:" 투표진행상황";
    color:#111 !important;
    font-size:24px !important;
    font-weight:800 !important;
}

div[data-testid="stRadio"] label:nth-of-type(3) div[data-testid="stMarkdownContainer"] p::before {
    content:"③[입력]";
    color:#7b159d !important;
    font-size:24px !important;
    font-weight:900 !important;
}
div[data-testid="stRadio"] label:nth-of-type(3) div[data-testid="stMarkdownContainer"] p::after {
    content:" 투표록 기초자료";
    color:#111 !important;
    font-size:24px !important;
    font-weight:800 !important;
}

div[data-testid="stRadio"] label:nth-of-type(4) div[data-testid="stMarkdownContainer"] p::before {
    content:"④[작성참고]";
    color:#7b159d !important;
    font-size:24px !important;
    font-weight:900 !important;
}
div[data-testid="stRadio"] label:nth-of-type(4) div[data-testid="stMarkdownContainer"] p::after {
    content:" 투표록 2p 작성";
    color:#111 !important;
    font-size:24px !important;
    font-weight:800 !important;
}

div[data-testid="stRadio"] label:nth-of-type(5) div[data-testid="stMarkdownContainer"] p::before {
    content:"[관리자]";
    color:#111 !important;
    font-size:24px !important;
    font-weight:900 !important;
}
div[data-testid="stRadio"] label:nth-of-type(5) div[data-testid="stMarkdownContainer"] p::after {
    content:"";
}

@media (max-width:768px) {
    .block-container {
        padding-top:5.0rem !important;
    }
    .app-main-title {
        font-size:27px !important;
        line-height:1.45 !important;
        padding-top:10px !important;
        padding-bottom:8px !important;
    }
    div[data-testid="stRadio"] label:nth-of-type(1) div[data-testid="stMarkdownContainer"] p::before,
    div[data-testid="stRadio"] label:nth-of-type(1) div[data-testid="stMarkdownContainer"] p::after,
    div[data-testid="stRadio"] label:nth-of-type(2) div[data-testid="stMarkdownContainer"] p::before,
    div[data-testid="stRadio"] label:nth-of-type(2) div[data-testid="stMarkdownContainer"] p::after,
    div[data-testid="stRadio"] label:nth-of-type(3) div[data-testid="stMarkdownContainer"] p::before,
    div[data-testid="stRadio"] label:nth-of-type(3) div[data-testid="stMarkdownContainer"] p::after,
    div[data-testid="stRadio"] label:nth-of-type(4) div[data-testid="stMarkdownContainer"] p::before,
    div[data-testid="stRadio"] label:nth-of-type(4) div[data-testid="stMarkdownContainer"] p::after,
    div[data-testid="stRadio"] label:nth-of-type(5) div[data-testid="stMarkdownContainer"] p::before {
        font-size:18px !important;
        line-height:1.35 !important;
        font-weight:900 !important;
    }
}


/* ============================================================
   v2.6 강제 보정
   1) 상단 제목 잘림 방지
   2) ①~④ + [ ] 보라색/굵게, 나머지 메뉴명 검정
   3) [관리자] 검정/굵게
   ============================================================ */

/* Streamlit 상단 툴바가 제목을 덮지 않도록 본문 시작 위치를 충분히 확보 */
.block-container {
    padding-top: 7.0rem !important;
    overflow: visible !important;
}
.app-main-title {
    margin-top: 0 !important;
    padding-top: 12px !important;
    padding-bottom: 10px !important;
    line-height: 1.55 !important;
    overflow: visible !important;
    font-size: 34px !important;
}

/* 라디오의 실제 문자열은 숨기고 같은 위치에 원하는 색상으로 재표시 */
div[data-testid="stRadio"] label:nth-of-type(1) p,
div[data-testid="stRadio"] label:nth-of-type(2) p,
div[data-testid="stRadio"] label:nth-of-type(3) p,
div[data-testid="stRadio"] label:nth-of-type(4) p,
div[data-testid="stRadio"] label:nth-of-type(5) p {
    font-size: 0 !important;
    color: transparent !important;
    line-height: 1.35 !important;
    white-space: nowrap !important;
}

div[data-testid="stRadio"] label:nth-of-type(1) p::before {
    content: "①[선택]" !important; color:#7b159d !important; font-size:20px !important; font-weight:900 !important;
}
div[data-testid="stRadio"] label:nth-of-type(1) p::after {
    content: " 투표소" !important; color:#111 !important; font-size:20px !important; font-weight:800 !important;
}
div[data-testid="stRadio"] label:nth-of-type(2) p::before {
    content: "②[보고]" !important; color:#7b159d !important; font-size:20px !important; font-weight:900 !important;
}
div[data-testid="stRadio"] label:nth-of-type(2) p::after {
    content: " 투표진행상황" !important; color:#111 !important; font-size:20px !important; font-weight:800 !important;
}
div[data-testid="stRadio"] label:nth-of-type(3) p::before {
    content: "③[입력]" !important; color:#7b159d !important; font-size:20px !important; font-weight:900 !important;
}
div[data-testid="stRadio"] label:nth-of-type(3) p::after {
    content: " 투표록 기초자료" !important; color:#111 !important; font-size:20px !important; font-weight:800 !important;
}
div[data-testid="stRadio"] label:nth-of-type(4) p::before {
    content: "④[작성참고]" !important; color:#7b159d !important; font-size:20px !important; font-weight:900 !important;
}
div[data-testid="stRadio"] label:nth-of-type(4) p::after {
    content: " 투표록 2p 작성" !important; color:#111 !important; font-size:20px !important; font-weight:800 !important;
}
div[data-testid="stRadio"] label:nth-of-type(5) p::before {
    content: "[관리자]" !important; color:#111 !important; font-size:20px !important; font-weight:900 !important;
}
div[data-testid="stRadio"] label:nth-of-type(5) p::after { content:"" !important; }

/* 선택 상태가 되어도 번호/[ ] 색상은 보라색 유지 */
div[data-testid="stRadio"] label:nth-of-type(-n+4):has(input:checked) p::before {
    color:#7b159d !important;
}

@media (max-width:768px) {
    .block-container { padding-top: 6.2rem !important; }
    .app-main-title {
        font-size: 27px !important;
        line-height: 1.55 !important;
        padding-top: 12px !important;
        padding-bottom: 9px !important;
    }
    div[data-testid="stRadio"] label:nth-of-type(1) p::before,
    div[data-testid="stRadio"] label:nth-of-type(1) p::after,
    div[data-testid="stRadio"] label:nth-of-type(2) p::before,
    div[data-testid="stRadio"] label:nth-of-type(2) p::after,
    div[data-testid="stRadio"] label:nth-of-type(3) p::before,
    div[data-testid="stRadio"] label:nth-of-type(3) p::after,
    div[data-testid="stRadio"] label:nth-of-type(4) p::before,
    div[data-testid="stRadio"] label:nth-of-type(4) p::after,
    div[data-testid="stRadio"] label:nth-of-type(5) p::before {
        font-size:18px !important;
        font-weight:900 !important;
    }
}


/* ============================================================
   v2.7 구조 보정 — Streamlit DOM 변경에도 대응
   ============================================================ */
.top-safe-spacer {
    display:block !important;
    height:54px !important;
    width:100% !important;
}
.app-main-title {
    display:block !important;
    position:relative !important;
    margin:0 0 14px 0 !important;
    padding:4px 0 8px 0 !important;
    font-size:34px !important;
    line-height:1.35 !important;
    font-weight:900 !important;
    overflow:visible !important;
    white-space:normal !important;
}
/* block-container의 과도한 상단 이동값은 무효화하고 실제 spacer로 확보 */
.block-container {
    padding-top:0.5rem !important;
    overflow:visible !important;
}

/* ①~④ 메뉴 라벨: 실제 원문은 숨기고 text wrapper에 두 색상으로 재구성 */
div[data-testid="stRadio"] label:nth-of-type(-n+5) > div:last-child,
div[data-testid="stRadio"] label:nth-of-type(-n+5) > div:last-child p,
div[data-testid="stRadio"] label:nth-of-type(-n+5) div[data-testid="stMarkdownContainer"],
div[data-testid="stRadio"] label:nth-of-type(-n+5) div[data-testid="stMarkdownContainer"] p {
    font-size:0 !important;
    color:transparent !important;
    line-height:1.30 !important;
    white-space:nowrap !important;
}
/* p가 존재하는 Streamlit 버전에서는 p 자체를 숨겨 중복문자 방지 */
div[data-testid="stRadio"] label:nth-of-type(-n+5) > div:last-child p {
    display:none !important;
}
/* 실제 표시문자 */
div[data-testid="stRadio"] label:nth-of-type(1) > div:last-child::before {content:"①[선택]"; color:#7b159d; font-size:20px; font-weight:900;}
div[data-testid="stRadio"] label:nth-of-type(1) > div:last-child::after  {content:" 투표소"; color:#111; font-size:20px; font-weight:800;}
div[data-testid="stRadio"] label:nth-of-type(2) > div:last-child::before {content:"②[보고]"; color:#7b159d; font-size:20px; font-weight:900;}
div[data-testid="stRadio"] label:nth-of-type(2) > div:last-child::after  {content:" 투표진행상황"; color:#111; font-size:20px; font-weight:800;}
div[data-testid="stRadio"] label:nth-of-type(3) > div:last-child::before {content:"③[입력]"; color:#7b159d; font-size:20px; font-weight:900;}
div[data-testid="stRadio"] label:nth-of-type(3) > div:last-child::after  {content:" 투표록 기초자료"; color:#111; font-size:20px; font-weight:800;}
div[data-testid="stRadio"] label:nth-of-type(4) > div:last-child::before {content:"④[작성참고]"; color:#7b159d; font-size:20px; font-weight:900;}
div[data-testid="stRadio"] label:nth-of-type(4) > div:last-child::after  {content:" 투표록 2p 작성"; color:#111; font-size:20px; font-weight:800;}
div[data-testid="stRadio"] label:nth-of-type(5) > div:last-child::before {content:"[관리자]"; color:#111; font-size:20px; font-weight:900;}
div[data-testid="stRadio"] label:nth-of-type(5) > div:last-child::after  {content:"";}

/* 선택되어도 ①~④/[ ]는 항상 보라색 */
div[data-testid="stRadio"] label:nth-of-type(-n+4):has(input:checked) > div:last-child::before {
    color:#7b159d !important;
    font-weight:900 !important;
}
/* 투표소 선택 제목 옆에는 어떤 안내문도 표시하지 않음 */
.station-select-title { margin:12px 0 14px 0 !important; }
.section-row .must-select, .section-row .must-red, .section-row .must-blue {display:none !important;}

@media (max-width:768px) {
    .top-safe-spacer {height:58px !important;}
    .app-main-title {font-size:27px !important; line-height:1.40 !important;}
    div[data-testid="stRadio"] label:nth-of-type(1) > div:last-child::before,
    div[data-testid="stRadio"] label:nth-of-type(1) > div:last-child::after,
    div[data-testid="stRadio"] label:nth-of-type(2) > div:last-child::before,
    div[data-testid="stRadio"] label:nth-of-type(2) > div:last-child::after,
    div[data-testid="stRadio"] label:nth-of-type(3) > div:last-child::before,
    div[data-testid="stRadio"] label:nth-of-type(3) > div:last-child::after,
    div[data-testid="stRadio"] label:nth-of-type(4) > div:last-child::before,
    div[data-testid="stRadio"] label:nth-of-type(4) > div:last-child::after,
    div[data-testid="stRadio"] label:nth-of-type(5) > div:last-child::before {
        font-size:18px !important;
    }
}



/* ============================================================
   v2.9 확정형 상단 UI
   - Streamlit radio/button DOM 스타일에 의존하지 않음
   - HTML 링크 카드로 메뉴를 직접 렌더링하여 부분 색상/굵기 확정
   - Streamlit 고정 헤더 아래 충분한 상단 여백 확보
   ============================================================ */
header[data-testid="stHeader"] { background: rgba(255,255,255,.98) !important; }
.block-container {
    max-width: 1380px !important;
    padding-top: 5.4rem !important;
    padding-left: 1rem !important;
    padding-right: 1rem !important;
    overflow: visible !important;
}
.app-main-title-v29 {
    margin: 0 0 18px 0 !important;
    padding: 4px 0 8px 0 !important;
    color:#111 !important;
    font-size: 34px !important;
    line-height: 1.35 !important;
    font-weight: 900 !important;
    white-space: normal !important;
    overflow: visible !important;
}
.workflow-guide {
    margin: 0 0 16px 0 !important;
    padding: 12px 14px !important;
    border: 1px solid #f0c85a !important;
    border-radius: 9px !important;
    background: #fffbea !important;
    color:#182235 !important;
    font-size: 20px !important;
    line-height: 1.45 !important;
    font-weight: 850 !important;
    text-align:center !important;
}
.workflow-guide .first-step { color:#ff1717 !important; font-weight:950 !important; }
.workflow-guide .next-steps { color:#102ed7 !important; font-weight:950 !important; }

.workflow-nav {
    display:grid;
    grid-template-columns: minmax(160px,1fr) 34px minmax(210px,1.35fr) 34px minmax(210px,1.35fr) 34px minmax(210px,1.35fr);
    gap:8px;
    align-items:center;
    margin: 10px 0 10px 0;
}
.workflow-card {
    min-height:76px;
    border:2px solid #7b159d;
    border-radius:9px;
    background:#fff;
    text-decoration:none !important;
    display:flex;
    align-items:center;
    justify-content:center;
    padding:10px 10px;
    box-sizing:border-box;
    color:#111 !important;
}
.workflow-card:hover { background:#faf7fc; text-decoration:none !important; }
.workflow-card.selected { border-color:#ff3434 !important; background:#fffafa !important; }
.workflow-card .dot {
    font-size:26px; line-height:1; color:#d5d8dc; margin-right:8px; flex:0 0 auto;
}
.workflow-card.selected .dot { color:#ff4b4b; }
.workflow-card .menu-text { line-height:1.25; text-align:center; }
.workflow-card .purple { color:#7b159d !important; font-weight:950 !important; font-size:19px; }
.workflow-card .black { color:#111 !important; font-weight:800 !important; font-size:17px; }
.workflow-arrow { color:#7b159d; font-size:30px; font-weight:950; text-align:center; }
.workflow-admin-row { display:flex; margin:6px 0 18px 0; }
.workflow-card.admin { min-height:54px; width:190px; border:none; justify-content:flex-start; padding-left:4px; }
.workflow-card.admin .black { font-size:18px; font-weight:900 !important; }
.workflow-card.admin.selected { border:2px solid #ff3434; padding-left:10px; }

.section-box.station-select-title {
    margin:18px 0 14px 0 !important;
    font-size:26px !important;
    padding:7px 14px !important;
    border:2px solid #111 !important;
    color:#111 !important;
}
.selected-station-confirm {
    margin-top:18px !important;
    padding:18px 20px !important;
    font-size:22px !important;
    border:2px solid #7b159d !important;
    background:#f8f4fb !important;
}
.selected-station-confirm .selected-name { font-size:22px !important; }

@media (max-width: 900px) {
    .block-container { padding-top:5.0rem !important; padding-left:.7rem !important; padding-right:.7rem !important; }
    .app-main-title-v29 { font-size:27px !important; }
    .workflow-guide { font-size:17px !important; }
    .workflow-nav {
        grid-template-columns: minmax(130px,1fr) 24px minmax(175px,1.35fr) 24px minmax(175px,1.35fr) 24px minmax(175px,1.35fr);
        gap:4px;
        overflow-x:auto;
        padding-bottom:3px;
    }
    .workflow-card { min-height:62px; padding:8px 6px; }
    .workflow-card .dot { font-size:20px; margin-right:5px; }
    .workflow-card .purple { font-size:15px; }
    .workflow-card .black { font-size:13px; }
    .workflow-arrow { font-size:24px; }
}
</style>
""", unsafe_allow_html=True)

# ------------------------------------------------------------
# XLSX parser (same format as the supplied election worksheet)
# ------------------------------------------------------------
NS_MAIN = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
NS_REL = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
NS_PKG_REL = "http://schemas.openxmlformats.org/package/2006/relationships"

def _cell_col(cell_ref):
    m = re.match(r"([A-Z]+)", cell_ref or "")
    if not m:
        return 0
    letters = m.group(1)
    n = 0
    for ch in letters:
        n = n * 26 + (ord(ch) - 64)
    return n

def _read_shared_strings(z):
    try:
        root = ET.fromstring(z.read("xl/sharedStrings.xml"))
    except KeyError:
        return []
    out = []
    for si in root.findall(f"{{{NS_MAIN}}}si"):
        parts = []
        for t in si.iter(f"{{{NS_MAIN}}}t"):
            parts.append(t.text or "")
        out.append("".join(parts))
    return out

def _sheet_paths(z):
    wb_root = ET.fromstring(z.read("xl/workbook.xml"))
    rel_root = ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))
    rel_map = {}
    for rel in rel_root.findall(f"{{{NS_PKG_REL}}}Relationship"):
        rel_map[rel.attrib["Id"]] = rel.attrib["Target"]

    result = []
    sheets = wb_root.find(f"{{{NS_MAIN}}}sheets")
    for s in sheets:
        name = s.attrib.get("name", "")
        rid = s.attrib.get(f"{{{NS_REL}}}id")
        target = rel_map.get(rid, "")
        if target.startswith("/"):
            path = target.lstrip("/")
        else:
            path = "xl/" + target.replace("../", "")
        result.append((name, path))
    return result

def _sheet_rows(z, path, shared):
    root = ET.fromstring(z.read(path))
    data = root.find(f"{{{NS_MAIN}}}sheetData")
    rows = []
    if data is None:
        return rows
    for row in data.findall(f"{{{NS_MAIN}}}row"):
        values = {}
        for c in row.findall(f"{{{NS_MAIN}}}c"):
            ref = c.attrib.get("r", "")
            col = _cell_col(ref)
            typ = c.attrib.get("t")
            value = ""
            if typ == "inlineStr":
                is_node = c.find(f"{{{NS_MAIN}}}is")
                if is_node is not None:
                    texts = [t.text or "" for t in is_node.iter(f"{{{NS_MAIN}}}t")]
                    value = "".join(texts)
            else:
                v = c.find(f"{{{NS_MAIN}}}v")
                if v is not None and v.text is not None:
                    raw = v.text
                    if typ == "s":
                        try:
                            value = shared[int(raw)]
                        except Exception:
                            value = raw
                    else:
                        value = raw
            values[col] = value
        if values:
            max_col = max(values.keys())
            rows.append([values.get(i, "") for i in range(1, max_col + 1)])
    return rows

def _to_int(v):
    if v is None:
        raise ValueError
    s = str(v).strip().replace(",", "")
    if not s:
        raise ValueError
    return int(float(s))

def election_name_from_sheet(sheet_name):
    name = str(sheet_name).strip()
    mapping = {
        "대구광역시장": "대구광역시장선거",
        "북구청장": "북구청장선거",
        "대구시의회의원": "대구시의회의원선거",
        "북구의회의원": "북구의회의원선거",
        "비례대구시의원": "대구시비례의원선거",
        "교육감": "교육감선거",
        "비례대표국회의원": "비례대표국회의원선거",
        "지역구국회의원": "지역구국회의원선거",
    }
    return mapping.get(name, name if name.endswith("선거") else name + "선거")

def _split_polling_district_name(value):
    """
    국선용 새 엑셀의 A열 예: '갑1동제1투' -> ('갑1동', '제1투')
    공백이 포함된 경우도 허용합니다.
    """
    s = re.sub(r"\s+", "", str(value or "").strip())
    if not s:
        return None, None

    m = re.match(r"^(.*?)(제\d+투(?:표소)?)$", s)
    if not m:
        return None, None

    dong = m.group(1).strip()
    station = m.group(2).strip()
    if station.endswith("투표소"):
        station = station[:-2]  # 앱 내부 기존 형식('제1투')과 맞춤
    return dong, station


def parse_uploaded_xlsx(file_bytes):
    """
    두 가지 엑셀 형식을 모두 지원합니다.

    [기존 형식]
    A 동위원회명 / B 투표소명 / C 선거인명부 등재자수 /
    D 수령매수 / E 시작 No. / F 끝 No.

    [국선 새 형식]
    A 투표구명(예: 갑1동제1투) / B 선거인명부 등재자수 /
    C 수령매수 / D 시작번호 / E 끝번호 / F 비고
    """
    z = zipfile.ZipFile(BytesIO(file_bytes))
    shared = _read_shared_strings(z)
    station_db = {}
    parsed_count = 0

    for sheet_name, sheet_path in _sheet_paths(z):
        try:
            rows = _sheet_rows(z, sheet_path, shared)
        except Exception:
            continue

        election_name = election_name_from_sheet(sheet_name)
        current_dong = None

        for row in rows:
            row = (row + [""] * 6)[:6]
            a, b, c, d, e, f = row

            # ----------------------------------------------------
            # 국선 새 형식 우선 판별
            # A=투표구명, B=등재자수, C=수령매수, D=시작, E=끝
            # ----------------------------------------------------
            new_dong, new_station = _split_polling_district_name(a)
            if new_dong and new_station:
                try:
                    reg = _to_int(b)
                    rec = _to_int(c)
                    start_no = _to_int(d)
                    end_no = _to_int(e)
                except Exception:
                    continue

                if rec <= 0 or end_no < start_no:
                    continue

                key = f"{new_dong}|{new_station}"
                ent = station_db.setdefault(
                    key,
                    {
                        "dong": new_dong,
                        "station": new_station,
                        "registered": reg,
                        "elections": [],
                    },
                )
                ent["registered"] = reg
                ent["elections"].append(
                    {
                        "name": election_name,
                        "received": rec,
                        "start_no": start_no,
                        "end_no": end_no,
                    }
                )
                parsed_count += 1
                continue

            # ----------------------------------------------------
            # 기존 형식
            # A=동위원회명, B=투표소명, C=등재자수,
            # D=수령매수, E=시작, F=끝
            # ----------------------------------------------------
            dong, station, registered, received, start_no, end_no = row

            if str(dong).strip():
                current_dong = str(dong).strip()

            station_text = str(station).strip()
            if not current_dong or not station_text or "투" not in station_text:
                continue

            try:
                reg = _to_int(registered)
                rec = _to_int(received)
                start_num = _to_int(start_no)
                end_num = _to_int(end_no)
            except Exception:
                continue

            if rec <= 0 or end_num < start_num:
                continue

            key = f"{current_dong}|{station_text}"
            ent = station_db.setdefault(
                key,
                {
                    "dong": current_dong,
                    "station": station_text,
                    "registered": reg,
                    "elections": [],
                },
            )
            ent["registered"] = reg
            ent["elections"].append(
                {
                    "name": election_name,
                    "received": rec,
                    "start_no": start_num,
                    "end_no": end_num,
                }
            )
            parsed_count += 1

    if not station_db:
        raise ValueError(
            "읽을 수 있는 투표소 자료를 찾지 못했습니다. "
            "기존 형식 또는 국선용 새 형식인지 확인해 주세요."
        )

    return station_db, parsed_count

def load_db():
    if DB_FILE.exists():
        try:
            return json.loads(DB_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {}

def save_db(db):
    DB_FILE.write_text(json.dumps(db, ensure_ascii=False, indent=2), encoding="utf-8")

def load_local():
    if LOCAL_FILE.exists():
        try:
            return json.loads(LOCAL_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"selected_key": None, "hourly_by_station": {}, "record_inputs_by_station": {}}

if "station_db" not in st.session_state:
    st.session_state.station_db = load_db()
if "local_data" not in st.session_state:
    st.session_state.local_data = load_local()

def save_local():
    LOCAL_FILE.write_text(
        json.dumps(st.session_state.local_data, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )

db = st.session_state.station_db
local = st.session_state.local_data
local.setdefault("hourly_by_station", {})
local.setdefault("record_inputs_by_station", {})

def station_number(s):
    m = re.search(r"(\d+)", str(s))
    return int(m.group(1)) if m else 999

def format_numeric_text(value):
    """숫자 문자열을 천단위 콤마 형식으로 표시. 빈값/비숫자는 원문 유지."""
    txt = str(value or "").replace(",", "").strip()
    if txt == "":
        return ""
    if re.fullmatch(r"\d+", txt):
        try:
            return f"{int(txt):,}"
        except Exception:
            return str(value)
    return str(value)


def format_numeric_session_value(key):
    """숫자 입력란을 rerun 시 천단위 콤마 형식으로 정규화합니다."""
    raw = str(st.session_state.get(key, "") or "").strip()
    if not raw:
        return
    compact = raw.replace(",", "").replace(" ", "")
    if re.fullmatch(r"\d+", compact):
        st.session_state[key] = f"{int(compact):,}"


def format_serial_list_session_value(key):
    """복수 일련번호 입력을 각 번호별 천단위 콤마 형식으로 정규화합니다."""
    raw = str(st.session_state.get(key, "") or "").strip()
    if not raw:
        return
    tokens = re.findall(r"\d{1,3}(?:,\d{3})+|\d+", raw)
    if not tokens:
        return
    try:
        st.session_state[key] = ", ".join(f"{int(t.replace(',', '')):,}" for t in tokens)
    except Exception:
        pass


if "app_authenticated" not in st.session_state:
    st.session_state.app_authenticated = False

if not st.session_state.app_authenticated:
    st.markdown(
        """
        <style>
        .login-wrap-v536 {
            max-width: 560px;
            margin: 72px auto 14px auto;
            text-align: center;
        }
        .login-title-v536 {
            font-size: 34px;
            font-weight: 900;
            line-height: 1.25;
            margin: 0 0 5px 0;
            color: #20232a;
        }
        .login-logo-v536 {
            display: block;
            width: min(330px, 78vw);
            height: auto;
            margin: 0 auto 20px auto;
        }
        @media (max-width: 768px) {
            .login-wrap-v536 {
                margin-top: 48px;
            }
            .login-title-v536 {
                font-size: 29px;
                margin-bottom: 3px;
            }
            .login-logo-v536 {
                width: min(300px, 82vw);
                margin-bottom: 18px;
            }
        }
        </style>
        <div class="login-wrap-v536">
            <div class="login-title-v536">투표록 작성 보조 앱(App)</div>
            <img class="login-logo-v536"
                 src="data:image/png;base64,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"
                 alt="북구선거관리위원회">
        </div>
        """,
        unsafe_allow_html=True
    )

    # form 안에 두면 비밀번호 입력 후 Enter 키로도 제출됩니다.
    with st.form("app_login_form_v536", clear_on_submit=False):
        access_pw = st.text_input(
            "비밀번호를 입력하세요.",
            type="password",
            key="app_access_password_input_v536"
        )
        login_submit = st.form_submit_button("🔐 앱 열기", width="stretch")

    if login_submit:
        if access_pw == current_app_access_password():
            st.session_state.app_authenticated = True
            st.session_state.session_selected_key = None
            st.rerun()
        else:
            st.error("비밀번호가 올바르지 않습니다.")
    st.stop()

# ============================================================
# v3.4 상단/메뉴 - 전체 메뉴를 실제 Streamlit 버튼으로 구성
# - 메뉴의 동그라미/보라색 강조부/검정색 설명부를 각각 실제 버튼으로 만듦
# - 카드 안 어느 글자를 눌러도 같은 콜백이 실행되어 메뉴 전환 가능
# - URL 이동을 사용하지 않아 로그인 session_state 유지
# ============================================================
st.markdown(
    r"""
    <style>
    .block-container {
        max-width: 1380px !important;
        padding-top: 5.2rem !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
        overflow: visible !important;
    }
    .app-main-title-v33 {
        margin: 0 0 18px 0 !important;
        padding: 6px 0 8px 0 !important;
        color: #111 !important;
        font-size: 34px !important;
        line-height: 1.35 !important;
        font-weight: 900 !important;
        white-space: normal !important;
    }
    .workflow-guide-v33 {
        margin: 0 0 18px 0 !important;
        padding: 12px 14px !important;
        border: 1px solid #f0c85a !important;
        border-radius: 9px !important;
        background: #fffbea !important;
        color: #182235 !important;
        font-size: 20px !important;
        line-height: 1.45 !important;
        font-weight: 850 !important;
        text-align: center !important;
    }
    .workflow-guide-v33 .first-step {color:#ff1717 !important; font-weight:950 !important;}
    .workflow-guide-v33 .next-steps {color:#102ed7 !important; font-weight:950 !important;}

    .st-key-nav_select_v33,
    .st-key-nav_report_v33,
    .st-key-nav_input_v33,
    .st-key-nav_reference_v33 {
        border: 2px solid #7b159d !important;
        border-radius: 9px !important;
        padding: 7px 8px !important;
        background: #fff !important;
        min-height: 68px !important;
    }
    .st-key-nav_admin_v33 {
        border: none !important;
        padding: 4px 0 !important;
        background: transparent !important;
    }

    /* 카드 안 버튼은 테두리 없이 한 덩어리처럼 보이게 */
    [class*="st-key-navdot_"] button,
    [class*="st-key-navlead_"] button,
    [class*="st-key-navtail_"] button {
        border: none !important;
        background: transparent !important;
        box-shadow: none !important;
        padding: 0 3px !important;
        min-height: 48px !important;
        height: 48px !important;
        width: 100% !important;
        white-space: nowrap !important;
    }
    [class*="st-key-navdot_"] button:hover,
    [class*="st-key-navlead_"] button:hover,
    [class*="st-key-navtail_"] button:hover {
        background: #faf7fc !important;
    }
    [class*="st-key-navdot_"] button p {
        color:#cfd3d8 !important;
        font-size:23px !important;
        font-weight:900 !important;
    }
    [class*="st-key-navlead_"] button p {
        color:#7b159d !important;
        font-size:18px !important;
        font-weight:950 !important;
    }
    [class*="st-key-navtail_"] button p {
        color:#111 !important;
        font-size:16px !important;
        font-weight:850 !important;
    }
    .st-key-navtail_admin_v33 button p {
        color:#111 !important;
        font-size:18px !important;
        font-weight:950 !important;
    }
    .nav-arrow-v33 {
        min-height:68px;
        display:flex;
        align-items:center;
        justify-content:center;
        color:#7b159d;
        font-size:30px;
        font-weight:950;
    }

    /* 과거의 투표소 선택 옆 안내문 제거 */
    .section-row .must-select, .section-row .must-red, .section-row .must-blue {display:none !important;}

    @media (max-width: 900px) {
        .block-container {padding-top:4.6rem !important; padding-left:.7rem !important; padding-right:.7rem !important;}
        .app-main-title-v33 {font-size:27px !important;}
        .workflow-guide-v33 {font-size:17px !important;}
        [class*="st-key-navlead_"] button p {font-size:14px !important;}
        [class*="st-key-navtail_"] button p {font-size:12px !important;}
        [class*="st-key-navdot_"] button p {font-size:20px !important;}
        .nav-arrow-v33 {font-size:25px !important; min-height:62px !important;}
    }
    </style>
    """,
    unsafe_allow_html=True,
)

if "session_selected_key" not in st.session_state:
    st.session_state.session_selected_key = None

title_col_v50, admin_title_col_v50 = st.columns([8.6, 1.4], gap="small")
with title_col_v50:
    st.markdown(
        '<div class="app-main-title-v33">🗳️ 투표록 작성 보조 앱 — <span class="mobile-version-v51">모바일 전용 v5.53</span></div>',
        unsafe_allow_html=True,
    )
with admin_title_col_v50:
    st.button("관리자", key="title_admin_v52", on_click=lambda: st.session_state.update(workflow_step_v33="admin"), width="stretch")

# v5.11: 상단 [관리자] 네모상자 대신 북구선거관리위원회 로고를 클릭형 관리자 버튼으로 사용
st.markdown(
    """
    <style>
    .st-key-title_admin_v52 button {
        border: none !important;
        background-color: transparent !important;
        background-image: url('data:image/png;base64,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') !important;
        background-repeat: no-repeat !important;
        background-position: center center !important;
        background-size: contain !important;
        box-shadow: none !important;
        min-height: 42px !important;
        height: 42px !important;
        padding: 0 !important;
        margin: 0 !important;
        cursor: pointer !important;
    }
    .st-key-title_admin_v52 button p {
        font-size: 0 !important;
        color: transparent !important;
        line-height: 0 !important;
    }
    .st-key-title_admin_v52 button:hover,
    .st-key-title_admin_v52 button:focus,
    .st-key-title_admin_v52 button:active {
        border: none !important;
        background-color: transparent !important;
        box-shadow: none !important;
        outline: none !important;
    }
    @media (max-width: 768px) {
        .st-key-title_admin_v52 button {
            min-height: 34px !important;
            height: 34px !important;
            background-size: contain !important;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)
workflow_cluster_v59 = st.container(key="workflow_cluster_v59")
with workflow_cluster_v59:
    st.markdown(
        '<div class="workflow-guide-v33">★ 반드시 '
        '<span class="first-step">①해당 투표소를 먼저 선택 후</span> '
        '<span class="next-steps">②~④ 순서대로 진행</span>하시기 바랍니다. ★</div>',
        unsafe_allow_html=True,
    )

WORKFLOW_LABELS = {
    "select": "①[선택]투표소",
    "report": "②[보고]투표진행상황",
    "input": "③[입력]투표록 기초자료",
    "reference": "④[작성참고] 투표록(2p)",
    "admin": "[관리자]",
}

if "workflow_step_v33" not in st.session_state:
    # 이전 버전에서 선택한 메뉴가 있으면 이어받음
    old_step = st.session_state.get("workflow_step_v32", "select")
    st.session_state.workflow_step_v33 = old_step if old_step in WORKFLOW_LABELS else "select"
if st.session_state.workflow_step_v33 not in WORKFLOW_LABELS:
    st.session_state.workflow_step_v33 = "select"


def _go_step_v35(step):
    st.session_state.workflow_step_v33 = step


# ============================================================
# v4.0 메뉴: 카드 폭/내부 간격 축소 (카드 하나 = Streamlit 버튼 하나)
# - 카드 위에 별도 버튼이 겹쳐 보이던 v3.4 구조 제거
# - 버튼 전체가 클릭 영역이므로 메뉴 전환이 확실히 동작
# - ::before = 선택표시, ::after = 보라색 ①[선택] 등
# - 실제 버튼 글자(p) = 검정색 메뉴명
# ============================================================
st.markdown(
    r"""
    <style>
    [class*="st-key-navcard_"] button {
        position: relative !important;
        width: 100% !important;
        min-height: 70px !important;
        height: 70px !important;
        border: 2px solid #7b159d !important;
        border-radius: 9px !important;
        background: #ffffff !important;
        box-shadow: none !important;
        padding: 8px !important;
        overflow: visible !important;
    }
    [class*="st-key-navcard_"] button:hover {
        background: #faf7fc !important;
        border-color: #7b159d !important;
    }
    [class*="st-key-navcard_"] button p {
        position: absolute !important;
        left: 30px !important;
        right: 5px !important;
        top: 40px !important;
        color: #111111 !important;
        font-size: 16px !important;
        font-weight: 850 !important;
        line-height: 1.15 !important;
        white-space: nowrap !important;
        margin: 0 !important;
        text-align: center !important;
    }

    /* 왼쪽 선택 동그라미 */
    [class*="st-key-navcard_"] button::before {
        content: "○";
        position: absolute;
        left: 8px;
        top: 50%;
        transform: translateY(-52%);
        color: #cfd3d8;
        font-size: 24px;
        font-weight: 950;
        line-height: 1;
    }

    /* 보라색 단계명 */
    .st-key-navcard_select_v35 button::after {content:"①[선택]";}
    .st-key-navcard_report_v35 button::after {content:"②[보고]";}
    .st-key-navcard_input_v35 button::after {content:"③[입력]";}
    .st-key-navcard_reference_v35 button::after {content:"④[작성참고]";}

    .st-key-navcard_select_v35 button::after,
    .st-key-navcard_report_v35 button::after,
    .st-key-navcard_input_v35 button::after,
    .st-key-navcard_reference_v35 button::after {
        position: absolute;
        left: 30px;
        right: 5px;
        top: 13px;
        transform: none;
        text-align: center;
        color: #7b159d;
        font-size: 18px;
        font-weight: 950;
        line-height: 1;
        white-space: nowrap;
    }

    /* 관리자 */
    .st-key-navcard_admin_v35 button {
        width: 190px !important;
        min-height: 54px !important;
        height: 54px !important;
        border: none !important;
        padding-left: 42px !important;
        background: transparent !important;
    }
    .st-key-navcard_admin_v35 button p {
        position: static !important;
        font-size: 18px !important;
        font-weight: 950 !important;
        color: #111 !important;
        text-align: left !important;
    }
    .st-key-navcard_admin_v35 button::before {left: 10px;}
    .st-key-navcard_admin_v35 button::after {content:none !important;}

    .nav-arrow-v35 {
        min-height: 70px;
        display:flex;
        align-items:center;
        justify-content:center;
        color:#7b159d;
        font-size:30px;
        font-weight:950;
    }

    @media (max-width: 900px) {
        [class*="st-key-navcard_"] button {
            min-height: 74px !important;
            height: 74px !important;
            padding-left: 0 !important;
        }
        [class*="st-key-navcard_"] button p {
            left: 25px !important;
            right: 4px !important;
            top: 43px !important;
            font-size: 13px !important;
            text-align: center !important;
        }
        .st-key-navcard_select_v35 button::after,
        .st-key-navcard_report_v35 button::after,
        .st-key-navcard_input_v35 button::after,
        .st-key-navcard_reference_v35 button::after {
            left: 25px;
            right: 4px;
            top: 14px;
            font-size: 15px;
            text-align:center;
        }
        [class*="st-key-navcard_"] button::before {left: 7px; font-size:20px;}
        .nav-arrow-v35 {font-size:24px; min-height:74px;}
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ============================================================
# v4.0 UI 미세조정
# - 메뉴 선택점과 글자 간격 축소 + 메뉴 내용 좌측정렬
# - [관리자] 좌측정렬 및 간격 축소
# - 상단 안내상자 / 선택투표소 확인상자 폭 축소 및 좌측정렬
# ============================================================
st.markdown(
    r"""
    <style>
    /* 상단 안내상자: 내용 길이만큼만 표시하고 좌측 정렬 */
    .workflow-guide-v33 {
        display: inline-block !important;
        width: auto !important;
        max-width: 760px !important;
        margin: 0 0 4px 0 !important;
        padding: 10px 16px !important;
        text-align: left !important;
        box-sizing: border-box !important;
    }

    /* 상단 안내상자와 바로 아래 메뉴 사이 세로 간격 최소화 */
    div[data-testid="stMarkdownContainer"]:has(.workflow-guide-v33) {
        margin-bottom: -8px !important;
        padding-bottom: 0 !important;
    }

    /* ①~④ 카드: 선택점 바로 옆에서 2줄 내용을 좌측 정렬 */
    [class*="st-key-navcard_"] button p {
        left: 38px !important;
        right: 8px !important;
        top: 40px !important;
        text-align: left !important;
    }
    [class*="st-key-navcard_"] button::before {
        left: 10px !important;
        font-size: 20px !important;
    }
    .st-key-navcard_select_v35 button::after,
    .st-key-navcard_report_v35 button::after,
    .st-key-navcard_input_v35 button::after,
    .st-key-navcard_reference_v35 button::after {
        left: 38px !important;
        right: 8px !important;
        top: 13px !important;
        text-align: left !important;
    }

    /* 관리자도 선택점과 글자를 붙이고 전체를 좌측 정렬 */
    .st-key-navcard_admin_v35 button {
        width: 155px !important;
        min-height: 48px !important;
        height: 48px !important;
        padding: 0 4px 0 34px !important;
        justify-content: flex-start !important;
    }
    .st-key-navcard_admin_v35 button::before {
        left: 7px !important;
        font-size: 20px !important;
    }
    .st-key-navcard_admin_v35 button p {
        position: static !important;
        margin: 0 !important;
        text-align: left !important;
        font-size: 18px !important;
    }

    /* 선택한 투표소 확인상자도 좌측에서 내용 길이에 맞게 축소 */
    .selected-station-confirm {
        display: inline-flex !important;
        align-items: center !important;
        width: auto !important;
        min-width: 0 !important;
        max-width: 720px !important;
        padding: 14px 18px !important;
        margin: 18px 0 0 0 !important;
        box-sizing: border-box !important;
    }

    @media (max-width: 900px) {
        .workflow-guide-v33 {
            display: inline-block !important;
            width: auto !important;
            max-width: calc(100vw - 1.4rem) !important;
            text-align: left !important;
            padding: 9px 12px !important;
        }
        [class*="st-key-navcard_"] button p {
            left: 32px !important;
            right: 4px !important;
            text-align: left !important;
        }
        [class*="st-key-navcard_"] button::before {
            left: 7px !important;
            font-size: 18px !important;
        }
        .st-key-navcard_select_v35 button::after,
        .st-key-navcard_report_v35 button::after,
        .st-key-navcard_input_v35 button::after,
        .st-key-navcard_reference_v35 button::after {
            left: 32px !important;
            right: 4px !important;
            text-align: left !important;
        }
        .selected-station-confirm {
            max-width: calc(100vw - 1.4rem) !important;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ============================================================
# v4.4 입력화면 콤보박스/표시 구조 보정
# - 상단 안내상자와 메뉴 카드 사이 간격 축소
# - 보고 입력/산출 박스 하단 안내문 잘림 방지
# - 보고화면 구성의 여백/정렬을 기준 이미지에 맞게 보정
# ============================================================
st.markdown(
    r"""
    <style>
    /* 안내상자 바로 아래에 메뉴가 오도록 실제 Streamlit 블록 간격을 줄임 */
    div[data-testid="stMarkdownContainer"]:has(.workflow-guide-v33) {
        margin-bottom: -18px !important;
        padding-bottom: 0 !important;
    }
    div[data-testid="stHorizontalBlock"]:has(.st-key-navcard_select_v35) {
        margin-top: -10px !important;
        margin-bottom: -6px !important;
    }
    div[data-testid="stHorizontalBlock"]:has(.st-key-navcard_admin_v35) {
        margin-top: -4px !important;
        margin-bottom: 2px !important;
    }

    /* ①~④ 메뉴 카드 내부를 좌측에 밀착 */
    [class*="st-key-navcard_"] button p {
        left: 31px !important;
        right: 5px !important;
        text-align: left !important;
    }
    [class*="st-key-navcard_"] button::before {
        left: 7px !important;
    }
    .st-key-navcard_select_v35 button::after,
    .st-key-navcard_report_v35 button::after,
    .st-key-navcard_input_v35 button::after,
    .st-key-navcard_reference_v35 button::after {
        left: 31px !important;
        right: 5px !important;
        text-align: left !important;
    }


    /* v4.5 투표소 선택 입력영역 */
    .st-key-station_choice_input_box {
        border:2px solid #7b159d !important; border-radius:8px !important;
        padding:14px 14px 10px 14px !important; margin-top:8px !important; margin-bottom:12px !important;
    }
    .station-choice-label {color:#7b159d; font-size:20px; font-weight:900; margin:0 0 7px 0; line-height:1.25;}
    .station-choice-label .star {margin-right:2px;}
    .station-choice-label .hint {color:#111; font-size:18px; font-weight:800;}
    .station-choice-label .hint .em {color:#e11; font-weight:900;}
    .shared-station-confirm {margin-top:8px !important; margin-bottom:12px !important;}

    /* v4.5 아/자 입력 제목과 선거명 선택 안내 */
    .record-input-title {font-size:28px; font-weight:900; line-height:1.25; margin:10px 0 14px 0; color:#17233c;}
    .record-input-title .small {font-size:26px; font-weight:900;}
    .election-choice-label {color:#7b159d; font-size:22px; font-weight:900; margin:12px 0 7px 0; line-height:1.3;}
    .election-choice-label span {color:red; font-size:21px; font-weight:900;}

        /* 보고 입력/산출 박스는 내용 높이에 맞게 늘어나고 잘리지 않게 */
    .st-key-report_input_calc_box {
        padding: 12px 14px 16px 14px !important;
        margin-bottom: 2px !important;
        overflow: visible !important;
        min-height: 0 !important;
        height: auto !important;
    }
    .st-key-report_input_calc_box > div,
    .st-key-report_input_calc_box div[data-testid="stVerticalBlock"],
    .st-key-report_input_calc_box div[data-testid="stElementContainer"] {
        overflow: visible !important;
        height: auto !important;
        min-height: 0 !important;
    }
    .report-v41-box-title {
        margin-bottom: 14px !important;
    }
    .report-v41-help {
        display: block !important;
        margin-top: 14px !important;
        margin-bottom: 5px !important;
        padding-bottom: 2px !important;
        line-height: 1.45 !important;
        white-space: normal !important;
        overflow: visible !important;
    }
    .report-v41-notice {
        margin-top: 2px !important;
        margin-bottom: 22px !important;
    }

    @media (max-width: 768px) {
        div[data-testid="stMarkdownContainer"]:has(.workflow-guide-v33) {
            margin-bottom: -14px !important;
        }
        div[data-testid="stHorizontalBlock"]:has(.st-key-navcard_select_v35) {
            margin-top: -8px !important;
        }
        .st-key-report_input_calc_box {
            padding: 11px 10px 15px 10px !important;
        }
        .report-v41-help {
            font-size: 14px !important;
            margin-top: 12px !important;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# v4.6 최종 UI 보정
st.markdown(
    r"""
    <style>
    /* 메뉴: 기본 회색 테두리, 선택 메뉴만 아래 동적 CSS에서 빨간색 */
    .st-key-navcard_select_v35 button,
    .st-key-navcard_report_v35 button,
    .st-key-navcard_input_v35 button,
    .st-key-navcard_reference_v35 button {
        border-color:#9a9a9a !important;
    }

    /* 상단 안내문과 메뉴의 세로 간격 축소 */
    div[data-testid="stMarkdownContainer"]:has(.workflow-guide-v33) { margin-bottom:-46px !important; }
    div[data-testid="stHorizontalBlock"]:has(.st-key-navcard_select_v35) { margin-top:-30px !important; }

    /* 선택 투표소 확인상자: 낮은 높이 + 진한 회색 테두리 */
    .selected-station-confirm {
        border:2px solid #555 !important;
        background:#fafafa !important;
        padding:7px 14px !important;
        margin:6px 0 10px 0 !important;
        min-height:0 !important;
        line-height:1.25 !important;
    }
    .selected-station-confirm .selected-name {
        font-size:23px !important;
        color:#7b159d !important;
        font-weight:950 !important;
        text-decoration:underline !important;
        text-underline-offset:3px !important;
    }

    /* 입력 기초자료 제목과 안내 크기 */
    .record-input-title .small { font-size:26px !important; }
    .record-input-title .record-under { color:#111 !important; text-decoration:underline !important; text-decoration-color:#111 !important; text-underline-offset:4px !important; }
    .election-choice-label span { font-size:21px !important; }
    .record-field-label { color:#1037d7; font-size:17px; font-weight:900; line-height:1.3; margin:0 0 5px 1px; }
    .input-inline-note { background:#f0f0f0; border-radius:6px; padding:8px 11px; color:#222; font-size:14px; line-height:1.45; margin:8px 0 10px 0; }
    .input-auto-note { background:#f1f1f1; border-radius:6px; padding:8px 11px; color:#555; font-size:14px; line-height:1.45; margin:8px 0 16px 0; }

    /* 입력 완료 안내 */
    .record-final-notice { background:#e5e5e5; color:#111; border-radius:7px; padding:12px 16px; font-size:15px; line-height:1.45; margin-top:12px; }
    .record-final-notice .warn { color:#e11; font-size:16px; font-weight:950; }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# v4.9 최종 화면 정리
# - 상단 진행 안내: 박스/배경 제거, 메뉴 바로 위에 밀착
# - 메뉴 1행 단계명 녹색 + 1pt 축소, 2행 메뉴명 2pt 확대
# - 보고 제목/참고 제목 테두리 제거, 보고 안내를 입력박스에 밀착
# ============================================================
st.markdown(
    r"""
    <style>
    /* 상단 안내문: 테두리/배경/박스감 제거 */
    .workflow-guide-v33 {
        display:block !important;
        width:auto !important;
        max-width:none !important;
        border:none !important;
        background:transparent !important;
        box-shadow:none !important;
        border-radius:0 !important;
        padding:0 !important;
        margin:0 !important;
        text-align:left !important;
        line-height:1.15 !important;
    }
    div[data-testid="stMarkdownContainer"]:has(.workflow-guide-v33) {
        margin:0 0 -58px 0 !important;
        padding:0 !important;
    }
    div[data-testid="stHorizontalBlock"]:has(.st-key-navcard_select_v35) {
        margin-top:-42px !important;
    }

    /* 메뉴 단계명: 녹색, 기존 대비 1pt 작게 */
    .st-key-navcard_select_v35 button::after,
    .st-key-navcard_report_v35 button::after,
    .st-key-navcard_input_v35 button::after,
    .st-key-navcard_reference_v35 button::after {
        color:#22a83a !important;
        font-size:17px !important;
        font-weight:950 !important;
    }
    /* 메뉴 본문: 2pt 크게 */
    .st-key-navcard_select_v35 button p,
    .st-key-navcard_report_v35 button p,
    .st-key-navcard_input_v35 button p,
    .st-key-navcard_reference_v35 button p {
        font-size:18px !important;
        font-weight:950 !important;
    }

    /* 보고 화면 제목과 참고 제목은 글자만 표시 */
    .report-v41-title,
    .report-v41-ref-title {
        border:none !important;
        background:transparent !important;
        box-shadow:none !important;
        border-radius:0 !important;
        padding:0 !important;
    }
    .report-v41-headrow { margin-bottom:4px !important; }
    .report-v41-notice {
        margin-top:-2px !important;
        margin-bottom:12px !important;
        padding-top:0 !important;
    }
    /* 보고 입력 박스와 하단 35분 안내를 바짝 붙임 */
    .st-key-report_input_calc_box { margin-bottom:0 !important; }
    div[data-testid="stMarkdownContainer"]:has(.report-v41-notice) {
        margin-top:-8px !important;
        padding-top:0 !important;
    }

    @media (max-width:900px) {
        div[data-testid="stMarkdownContainer"]:has(.workflow-guide-v33) {
            margin-bottom:-54px !important;
        }
        div[data-testid="stHorizontalBlock"]:has(.st-key-navcard_select_v35) {
            margin-top:-40px !important;
        }
        .st-key-navcard_select_v35 button::after,
        .st-key-navcard_report_v35 button::after,
        .st-key-navcard_input_v35 button::after,
        .st-key-navcard_reference_v35 button::after {
            font-size:14px !important;
        }
        .st-key-navcard_select_v35 button p,
        .st-key-navcard_report_v35 button p,
        .st-key-navcard_input_v35 button p,
        .st-key-navcard_reference_v35 button p {
            font-size:15px !important;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    r"""
    <style>
    /* v5.0: 제목의 모바일 버전 표시는 본 제목보다 4pt 작게 */
    .mobile-version-v51 {font-size:calc(1em - 4px) !important;}
    /* 제목 옆 관리자 버튼: 목록에서는 제거하고 여기서만 선택 */
    .st-key-title_admin_v51 button {
        border:none !important; background:transparent !important; box-shadow:none !important;
        min-height:34px !important; height:34px !important; padding:0 2px !important; margin-top:5px !important;
    }
    .st-key-title_admin_v52 button p {color:#111 !important; font-weight:900 !important; font-size:16px !important; white-space:nowrap !important;}
    /* 반드시 안내와 진행목록을 최대한 밀착 */
    div[data-testid="stMarkdownContainer"]:has(.workflow-guide-v33) {margin-bottom:-72px !important; padding-bottom:0 !important;}
    div[data-testid="stHorizontalBlock"]:has(.st-key-navcard_select_v35) {margin-top:-52px !important; padding-top:0 !important;}
    /* 1. 투표소 선택: 테두리 없는 제목 */
    .station-select-title-v50 {font-size:28px !important; font-weight:950 !important; color:#111 !important; margin:6px 0 8px 0 !important; padding:0 !important;}
    @media (max-width:900px) {
        .st-key-title_admin_v52 button p {font-size:13px !important;}
        div[data-testid="stMarkdownContainer"]:has(.workflow-guide-v33) {margin-bottom:-68px !important;}
        div[data-testid="stHorizontalBlock"]:has(.st-key-navcard_select_v35) {margin-top:-50px !important;}
        .station-select-title-v50 {font-size:24px !important;}
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ============================================================
# v5.4 모바일 가독성/반응형 최적화
# - 휴대전화 세로 화면에서 제목/안내/메뉴/입력/표 가독성 개선
# - 기능/계산 로직은 변경하지 않음
# ============================================================
st.markdown(
    r"""
    <style>
    /* 터치/가독성 공통 */
    @media (max-width: 768px) {
        .block-container {
            padding-left: 0.45rem !important;
            padding-right: 0.45rem !important;
            padding-top: 3.7rem !important;
            max-width: 100% !important;
        }

        /* 앱 제목: 한 줄에 최대한 유지하되 작은 화면에서는 자연스럽게 줄바꿈 */
        .app-main-title-v33 {
            font-size: 23px !important;
            line-height: 1.16 !important;
            letter-spacing: -0.5px !important;
            white-space: normal !important;
            margin-bottom: 2px !important;
        }
        .mobile-version-v51 { font-size: 18px !important; }
        .st-key-title_admin_v52 button {
            margin-top: 0 !important;
            min-height: 28px !important;
            height: 28px !important;
            padding: 0 !important;
        }
        .st-key-title_admin_v52 button p {
            font-size: 12px !important;
            line-height: 1 !important;
        }

        /* 안내문은 메뉴 바로 위, 읽기 쉬운 크기 */
        .workflow-guide-v33 {
            font-size: 15.5px !important;
            line-height: 1.2 !important;
            letter-spacing: -0.35px !important;
            white-space: nowrap !important;
            transform: scale(0.96);
            transform-origin: left center;
        }
        div[data-testid="stMarkdownContainer"]:has(.workflow-guide-v33) {
            margin-bottom: -44px !important;
        }
        div[data-testid="stHorizontalBlock"]:has(.st-key-navcard_select_v35) {
            margin-top: -28px !important;
            column-gap: 2px !important;
            gap: 2px !important;
        }

        /* 4개 메뉴가 모바일 한 화면 폭을 효율적으로 사용 */
        [class*="st-key-navcard_"] button {
            min-height: 64px !important;
            height: 64px !important;
            border-width: 1.5px !important;
            border-radius: 7px !important;
            padding: 0 2px !important;
        }
        .st-key-navcard_select_v35 button::after,
        .st-key-navcard_report_v35 button::after,
        .st-key-navcard_input_v35 button::after,
        .st-key-navcard_reference_v35 button::after {
            left: 23px !important;
            right: 1px !important;
            top: 10px !important;
            font-size: 12.5px !important;
            line-height: 1 !important;
            white-space: nowrap !important;
            text-align: center !important;
        }
        .st-key-navcard_select_v35 button p,
        .st-key-navcard_report_v35 button p,
        .st-key-navcard_input_v35 button p,
        .st-key-navcard_reference_v35 button p {
            left: 23px !important;
            right: 1px !important;
            top: 35px !important;
            font-size: 13.5px !important;
            line-height: 1.05 !important;
            white-space: nowrap !important;
            text-align: center !important;
            letter-spacing: -0.45px !important;
        }
        [class*="st-key-navcard_"] button::before {
            left: 5px !important;
            font-size: 17px !important;
        }
        .nav-arrow-v35 {
            min-height: 64px !important;
            font-size: 20px !important;
            padding: 0 !important;
        }

        /* 선택 투표소 표시: 높이/여백 절약 */
        .selected-station-confirm {
            max-width: 100% !important;
            padding: 7px 10px !important;
            margin: 7px 0 9px 0 !important;
            line-height: 1.15 !important;
        }
        .selected-station-confirm, .selected-station-confirm * {
            font-size: 17px !important;
        }
        .selected-station-confirm .selected-name {
            font-size: 19px !important;
        }

        /* 섹션 제목 */
        .station-select-title-v50 {
            font-size: 23px !important;
            line-height: 1.15 !important;
            margin: 8px 0 7px 0 !important;
        }
        .record-input-title {
            font-size: 23px !important;
            line-height: 1.18 !important;
            margin: 8px 0 8px 0 !important;
            letter-spacing: -0.45px !important;
        }
        .record-input-title .small { font-size: 18px !important; }
        .election-choice-label {
            font-size: 18px !important;
            margin: 7px 0 4px 0 !important;
            line-height: 1.2 !important;
        }
        .election-choice-label span { font-size: 16px !important; }
        .record-field-label {
            font-size: 15px !important;
            line-height: 1.2 !important;
            margin-bottom: 3px !important;
        }

        /* 콤보/입력칸: 손가락 터치에 충분한 높이 + 글자 확대 */
        div[data-baseweb="select"] > div,
        div[data-testid="stTextInput"] input,
        div[data-testid="stNumberInput"] input {
            min-height: 42px !important;
            font-size: 16px !important;
        }
        div[data-testid="stTextInput"] input::placeholder,
        div[data-testid="stNumberInput"] input::placeholder {
            font-size: 16px !important;
            opacity: 0.9 !important;
        }

        /* 안내 박스는 휴대폰에서 너무 크지 않게 */
        .input-inline-note, .input-auto-note, .record-final-notice {
            font-size: 13.5px !important;
            line-height: 1.35 !important;
            padding: 7px 9px !important;
            margin: 6px 0 8px 0 !important;
        }

        /* 표: 내용은 축소하지 않고 가로 스크롤 허용 */
        div[data-testid="stTable"],
        div[data-testid="stDataFrame"] {
            overflow-x: auto !important;
            -webkit-overflow-scrolling: touch !important;
        }
        div[data-testid="stTable"] table {
            min-width: 760px !important;
        }
        div[data-testid="stTable"] table th,
        div[data-testid="stTable"] table td {
            font-size: 13px !important;
            line-height: 1.22 !important;
            padding: 7px 6px !important;
            white-space: nowrap !important;
        }

        /* 보고 화면 */
        .report-v41-headrow { margin-bottom: 2px !important; }
        .st-key-report_input_calc_box {
            padding: 9px 8px 10px 8px !important;
        }
        .report-v41-help {
            font-size: 13.5px !important;
            line-height: 1.35 !important;
            margin-top: 8px !important;
        }
        .report-v41-notice {
            font-size: 14px !important;
            line-height: 1.25 !important;
            margin-top: 2px !important;
            margin-bottom: 14px !important;
        }
    }

    /* 아주 좁은 휴대전화(약 360px 이하) */
    @media (max-width: 390px) {
        .app-main-title-v33 {font-size:21px !important;}
        .workflow-guide-v33 {font-size:14px !important; transform:scale(0.93);}
        .st-key-navcard_select_v35 button::after,
        .st-key-navcard_report_v35 button::after,
        .st-key-navcard_input_v35 button::after,
        .st-key-navcard_reference_v35 button::after {font-size:11.5px !important;}
        .st-key-navcard_select_v35 button p,
        .st-key-navcard_report_v35 button p,
        .st-key-navcard_input_v35 button p,
        .st-key-navcard_reference_v35 button p {font-size:12px !important;}
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# 선택 카드 강조
_selected_v35 = st.session_state.workflow_step_v33
st.markdown(
    f"""
    <style>
    .st-key-navcard_{_selected_v35}_v35 button {{
        border-color:#ff3434 !important;
        border-width:3px !important;
        background:#fffafa !important;
    }}
    /* 선택 표시: 기존 빨간 점 대신 하단 파란 밑줄 */
    .st-key-navcard_{_selected_v35}_v35 button::before {{
        content:"" !important;
        display:none !important;
    }}
    .st-key-navcard_{_selected_v35}_v35 button p {{
        border-bottom:3px solid #1557ff !important;
        padding-bottom:3px !important;
        width:max-content !important;
        max-width:92% !important;
        margin-left:auto !important;
        margin-right:auto !important;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

# 실제 카드 버튼. 각 메뉴는 버튼 1개만 사용합니다.
# ============================================================
# v5.5 휴대전화 실화면 보정
# ============================================================
st.markdown(
    r"""
    <style>
    @media (max-width: 768px) {
        div[data-testid="stHorizontalBlock"]:has(.st-key-title_admin_v52) {display:flex !important; flex-wrap:nowrap !important; align-items:center !important; gap:3px !important; width:100% !important;}
        div[data-testid="stHorizontalBlock"]:has(.st-key-title_admin_v52) > div[data-testid="stColumn"]:first-child {flex:1 1 auto !important; width:auto !important; min-width:0 !important;}
        div[data-testid="stHorizontalBlock"]:has(.st-key-title_admin_v52) > div[data-testid="stColumn"]:last-child {flex:0 0 54px !important; width:54px !important; min-width:54px !important;}
        .app-main-title-v33 {font-size:20px !important; line-height:1.08 !important; white-space:nowrap !important; letter-spacing:-0.8px !important;}
        .mobile-version-v51 {font-size:16px !important;}
        .st-key-title_admin_v52 button {border:none !important; background:transparent !important; min-height:24px !important; height:24px !important; padding:0 !important; margin:0 !important;}
        .st-key-title_admin_v52 button p {font-size:11px !important; color:#111 !important; white-space:nowrap !important;}
        .workflow-guide-v33 {font-size:12.5px !important; line-height:1.18 !important; white-space:normal !important; transform:none !important; margin:7px 0 2px 0 !important;}
        div[data-testid="stMarkdownContainer"]:has(.workflow-guide-v33) {margin-bottom:0 !important; padding-bottom:0 !important;}
        div[data-testid="stHorizontalBlock"]:has(.st-key-navcard_select_v35) {display:grid !important; grid-template-columns:minmax(0,.90fr) 13px minmax(0,1.22fr) 13px minmax(0,1.22fr) 13px minmax(0,1.22fr) !important; gap:1px !important; margin:0 !important; padding:0 !important; width:100% !important; align-items:center !important;}
        div[data-testid="stHorizontalBlock"]:has(.st-key-navcard_select_v35) > div[data-testid="stColumn"] {width:auto !important; min-width:0 !important; flex:none !important; padding:0 !important;}
        [class*="st-key-navcard_"] button {min-height:58px !important; height:58px !important; padding:0 1px !important; border-radius:6px !important;}
        .st-key-navcard_select_v35 button::after,.st-key-navcard_report_v35 button::after,.st-key-navcard_input_v35 button::after,.st-key-navcard_reference_v35 button::after {left:15px !important; right:0 !important; top:8px !important; font-size:9.7px !important; white-space:nowrap !important; letter-spacing:-.5px !important;}
        .st-key-navcard_select_v35 button p,.st-key-navcard_report_v35 button p,.st-key-navcard_input_v35 button p,.st-key-navcard_reference_v35 button p {left:15px !important; right:0 !important; top:32px !important; font-size:10.3px !important; line-height:1.02 !important; white-space:nowrap !important; letter-spacing:-.7px !important;}
        [class*="st-key-navcard_"] button::before {left:3px !important; font-size:13px !important;}
        .nav-arrow-v35 {min-height:58px !important; height:58px !important; font-size:17px !important; display:flex !important; align-items:center !important; justify-content:center !important; padding:0 !important; margin:0 !important;}
        .selected-station-confirm {margin:7px 0 8px 0 !important; padding:7px 9px !important; min-height:auto !important;}
        .selected-station-confirm,.selected-station-confirm * {font-size:15px !important;}
        .selected-station-confirm .selected-name {font-size:16px !important;}
        .st-key-station_choice_input_box div[data-testid="stHorizontalBlock"] {display:grid !important; grid-template-columns:minmax(0,1fr) minmax(0,1fr) !important; gap:8px !important;}
        .st-key-station_choice_input_box div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"] {width:auto !important; min-width:0 !important; flex:none !important;}
        .station-choice-label {font-size:15px !important; margin-bottom:3px !important;}
        .st-key-station_choice_input_box div[data-baseweb="select"] > div {font-size:15px !important; min-height:40px !important;}
        .record-input-title {font-size:20px !important; line-height:1.2 !important;}
        .record-input-title .small {font-size:14px !important;}
        .input-summary-wrap {overflow-x:auto !important; -webkit-overflow-scrolling:touch !important;}
        .input-summary-table {min-width:650px !important;}
        .input-summary-table th,.input-summary-table td {font-size:12px !important; padding:6px 5px !important;}
    }
    @media (max-width: 390px) {
        .app-main-title-v33 {font-size:18px !important;} .mobile-version-v51 {font-size:14px !important;} .workflow-guide-v33 {font-size:11.5px !important;}
        .st-key-navcard_select_v35 button::after,.st-key-navcard_report_v35 button::after,.st-key-navcard_input_v35 button::after,.st-key-navcard_reference_v35 button::after {font-size:8.8px !important;}
        .st-key-navcard_select_v35 button p,.st-key-navcard_report_v35 button p,.st-key-navcard_input_v35 button p,.st-key-navcard_reference_v35 button p {font-size:9.2px !important;}
    }
    </style>
    """, unsafe_allow_html=True)

with workflow_cluster_v59:
    c1, c2, c3, c4 = st.columns([1, 1, 1, 1], gap="small")
    with c1:
        st.button("투표소", key="navcard_select_v35", on_click=_go_step_v35, args=("select",), width="stretch")
    with c2:
        st.button("투표진행상황", key="navcard_report_v35", on_click=_go_step_v35, args=("report",), width="stretch")
    with c3:
        st.button("투표록 기초자료", key="navcard_input_v35", on_click=_go_step_v35, args=("input",), width="stretch")
    with c4:
        st.button("투표록(2p)", key="navcard_reference_v35", on_click=_go_step_v35, args=("reference",), width="stretch")
    st.markdown(
        '''
        <div class="workflow-progress-arrow-v527" aria-hidden="true">
            <svg viewBox="0 0 1000 26" preserveAspectRatio="none">
                <line x1="4" y1="13" x2="962" y2="13" stroke="#111" stroke-width="4" stroke-linecap="round"/>
                <polygon points="958,2 998,13 958,24" fill="#111"/>
            </svg>
        </div>
        ''',
        unsafe_allow_html=True,
    )


workflow_step = WORKFLOW_LABELS[st.session_state.workflow_step_v33]

# ------------------------------------------------------------
# Current station / hourly state helpers
# ------------------------------------------------------------
selected_key = st.session_state.get("session_selected_key")
station = db.get(selected_key) if selected_key and selected_key in db else None

hourly_by_station = local.setdefault("hourly_by_station", {})
hourly = hourly_by_station.setdefault(selected_key, []) if selected_key else []

# 선택 투표소 확인 HTML
if station is not None:
    selected_station_confirm_html_v530 = (
        '<div class="selected-station-confirm shared-station-confirm">'
        '<span class="confirm-check-v524">☑</span>'
        f'선택한 투표소는 <span class="selected-name">({station["dong"]} {station["station"]}표소)</span>입니다.'
        '</div>'
    )
else:
    selected_station_confirm_html_v530 = (
        '<div class="selected-station-confirm shared-station-confirm">'
        '<span class="confirm-check-v524">☑</span>'
        '선택한 투표소는 <span class="selected-name">('
        '<span style="display:inline-block; min-width:190px; border-bottom:2px solid #7b159d; line-height:1.05;">&nbsp;</span>'
        ')</span>입니다.</div>'
    )

# ③~④는 공통 확인상자를 상단 진행영역 아래 표시
# ①과 ②는 각각 본문 제목과 한 HTML 블록으로 묶어 동일한 줄간격으로 렌더링합니다.
if workflow_step not in ("①[선택]투표소", "②[보고]투표진행상황"):
    with workflow_cluster_v59:
        st.markdown(selected_station_confirm_html_v530, unsafe_allow_html=True)


if workflow_step == "①[선택]투표소":
    # v5.31: 선택 본문을 상단 진행영역과 동일한 workflow_cluster 안에 직접 추가.
    # top-level Streamlit 블록 사이의 자동 공백을 원천적으로 제거한다.
    with workflow_cluster_v59:
        with st.container(key="selection_body_v531"):
                # 확인상자 → 10px → 제목/안내를 한 HTML 블록으로 묶음
            # Streamlit 외부 컨테이너 gap이 끼어들지 않도록 함.
            st.markdown(
                f"""
                <div class="step1-fixed-layout-v531">
                    {selected_station_confirm_html_v530}
                    <div class="confirm-to-title-gap-v531"></div>
                    <div class="station-select-title-v531"><span class="select-title-green">①[선택]</span> 투표소</div>
                    <div class="select-instruction-v531">
                        <span class="tap-finger-v531" aria-hidden="true">👆</span>
                        <span class="select-guide-text-v531">해당 <span class="select-keyword-v531">'동'</span>과 <span class="select-keyword-v531">'투표소'</span>를 선택하세요!</span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            dongs = []
            for v in db.values():
                if v["dong"] not in dongs:
                    dongs.append(v["dong"])

            if not dongs:
                st.warning("현재 등록된 자료가 없습니다. [관리자]에서 엑셀 기초자료를 먼저 업로드해 주세요.")
                selected_dong = None
                selected_station = None
            else:
                # 기존 저장 선택값이 있어도 앱을 새로 열면 먼저 선택하도록 초기 상태는 빈 값으로 시작
                dong_options = ["동을 선택하세요"] + dongs

                saved_selected_key = st.session_state.get("session_selected_key")
                saved_dong = None
                saved_station = None
                if saved_selected_key and saved_selected_key in db:
                    saved_dong = db[saved_selected_key]["dong"]
                    saved_station = db[saved_selected_key]["station"]

                dong_index = dong_options.index(saved_dong) if saved_dong in dongs else 0

                with st.container(border=True, key="station_choice_input_box"):
                    c1, c2 = st.columns(2, gap="medium")
                    with c1:
                        st.markdown(
                            '<div class="station-choice-label"><span class="star">★</span> 동 선택</div>',
                            unsafe_allow_html=True,
                        )
                        selected_dong_display = st.selectbox(
                            "동선택",
                            dong_options,
                            index=dong_index,
                            key="selected_dong_placeholder",
                            label_visibility="collapsed",
                        )

                    selected_dong = None if selected_dong_display == "동을 선택하세요" else selected_dong_display

                    if selected_dong:
                        stations = sorted(
                            [v["station"] for v in db.values() if v["dong"] == selected_dong],
                            key=station_number
                        )
                        station_options = ["투표소를 선택하세요"] + stations
                    else:
                        stations = []
                        station_options = ["투표소를 선택하세요"]

                    station_index = 0
                    if saved_dong == selected_dong and saved_station in stations:
                        station_index = station_options.index(saved_station)

                    with c2:
                        st.markdown(
                            '<div class="station-choice-label"><span class="star">★</span> 투표소 선택</div>',
                            unsafe_allow_html=True,
                        )
                        selected_station_display = st.selectbox(
                            "투표소 선택",
                            station_options,
                            index=station_index,
                            key=f"selected_station_placeholder_{selected_dong or 'none'}",
                            label_visibility="collapsed",
                        )

                selected_station = (
                    None if selected_station_display == "투표소를 선택하세요"
                    else selected_station_display
                )

            # 선택값 저장. 새 투표소가 선택되면 한 번 rerun하여 상단 공통 확인상자도 즉시 갱신합니다.
            if selected_dong and selected_station:
                new_selected_key = f"{selected_dong}|{selected_station}"
                changed = st.session_state.get("session_selected_key") != new_selected_key
                selected_key = new_selected_key
                station = db[selected_key]
                st.session_state.session_selected_key = selected_key
                local["selected_key"] = selected_key
                save_local()
                hourly_by_station = local.setdefault("hourly_by_station", {})
                hourly = hourly_by_station.setdefault(selected_key, [])
                if changed:
                    st.rerun()
            else:
                saved_selected_key = st.session_state.get("session_selected_key")
                if saved_selected_key and saved_selected_key in db:
                    selected_key = saved_selected_key
                    station = db[saved_selected_key]
                    hourly_by_station = local.setdefault("hourly_by_station", {})
                    hourly = hourly_by_station.setdefault(selected_key, [])
                else:
                    selected_key = None
                    station = None
                    hourly = []


    def used_count(election, first_remaining_no):
        if first_remaining_no is None:
            return 0
        return int(first_remaining_no) - int(election["start_no"])

    def remaining_count(election, first_remaining_no):
        if first_remaining_no is None:
            return int(election["received"])
        return int(election["received"]) - used_count(election, first_remaining_no)

    def valid_no(election, number):
        if number is None:
            return True
        return int(election["start_no"]) <= int(number) <= int(election["end_no"]) + 1

    def last_serial(election_name):
        for row in reversed(hourly):
            if election_name in row.get("serials", {}):
                try:
                    return int(row["serials"][election_name])
                except Exception:
                    return None
        return None

    st.markdown(
        r"""
        <style>
        /* v5.2 최종 보정 */
        /* 전체 앱 제목을 v5.0보다 4px 작게, 관리자도 2px 작게 */
        .app-main-title-v33 {font-size:30px !important; white-space:nowrap !important;}
        .mobile-version-v51 {font-size:1em !important;}
        .st-key-title_admin_v52 button p {color:#111 !important; font-size:14px !important; font-weight:900 !important;}

        /* 반드시 안내와 네비게이션 카드 사이를 최대한 밀착 */
        div[data-testid="stMarkdownContainer"]:has(.workflow-guide-v33) {margin-bottom:-64px !important; padding-bottom:0 !important;}
        div[data-testid="stHorizontalBlock"]:has(.st-key-navcard_select_v35) {margin-top:-54px !important; padding-top:0 !important;}

        /* 투표소 선택 콤보박스의 표시 글자 1px 확대 */
        .st-key-station_choice_input_box div[data-baseweb="select"] > div {font-size:17px !important;}

        /* (투표록2p)은 제목보다 3px 작게 */
        .record-input-title .small {font-size:25px !important;}

        /* ④ 작성참고 화면의 초록/파란 외곽 박스 제거 */
        .record-section, .record-section.blue {border:none !important; border-radius:0 !important; padding:0 !important; margin-bottom:18px !important;}
        .reference-main-title-v51 {font-size:25px !important; font-weight:950 !important; color:#17233c !important; margin:6px 0 16px 0 !important;}

        /* '아. 투표상황' 표의 선거명은 한 줄 표시 */
        .reference-a-table tbody td:first-child, .reference-a-table thead th:first-child {white-space:nowrap !important;}
        .reference-a-table tbody td:first-child {font-size:13px !important;}

        @media (max-width:900px) {
            .app-main-title-v33 {font-size:23px !important;}
            .st-key-title_admin_v52 button p {font-size:11px !important;}
            div[data-testid="stMarkdownContainer"]:has(.workflow-guide-v33) {margin-bottom:-60px !important;}
            div[data-testid="stHorizontalBlock"]:has(.st-key-navcard_select_v35) {margin-top:-50px !important;}
            .record-input-title .small {font-size:21px !important;}
            .reference-main-title-v51 {font-size:22px !important;}
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        r"""
        <style>
        /* v5.3 최종 간격/폭 보정 */
        /* 안내문과 메뉴 사이의 빈 줄을 없애되 겹치지 않도록 밀착 */
        div[data-testid="stMarkdownContainer"]:has(.workflow-guide-v33) {
            margin-bottom:-70px !important;
            padding-bottom:0 !important;
        }
        div[data-testid="stHorizontalBlock"]:has(.st-key-navcard_select_v35) {
            margin-top:-58px !important;
            margin-right:0 !important;
            padding-top:0 !important;
            padding-right:0 !important;
            width:100% !important;
        }
        /* 마지막 메뉴까지 화면 우측을 고르게 사용 */
        div[data-testid="stHorizontalBlock"]:has(.st-key-navcard_select_v35) > div[data-testid="stColumn"] {
            padding-right:0 !important;
        }
        /* 35분 안내와 2. 참고 제목 사이에 한 줄 정도의 여백 */
        .report-v41-notice {
            margin-bottom:32px !important;
        }
        @media (max-width:900px) {
            div[data-testid="stMarkdownContainer"]:has(.workflow-guide-v33) {margin-bottom:-66px !important;}
            div[data-testid="stHorizontalBlock"]:has(.st-key-navcard_select_v35) {margin-top:-56px !important;}
            .report-v41-notice {margin-bottom:28px !important;}
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


    st.markdown(
        r"""
        <style>
        /* =========================================================
           v5.14 선택화면 배열 + ②~④ 본문 간격 통일
           ========================================================= */

        /* ① 선택 화면: 상단 확인상자와 본문 제목 사이 과도한 공백 제거 */
        .shared-station-confirm {
            margin-bottom: 10px !important;
        }
        div[data-testid="stMarkdownContainer"]:has(.select-screen-heading-v514) {
            margin-top: 0 !important;
            margin-bottom: 4px !important;
            padding-top: 0 !important;
            padding-bottom: 0 !important;
        }
        .select-screen-heading-v514 {
            margin: 0 !important;
            padding: 0 !important;
        }

        /* 화면 예시처럼 제목 위 짧은 검정선 */
        .station-select-title-v50 {
            display: block !important;
            width: 245px !important;
            box-sizing: border-box !important;
            border-top: 3px solid #111 !important;
            margin: 0 0 6px 0 !important;
            padding: 6px 0 0 0 !important;
            font-size: 28px !important;
            line-height: 1.2 !important;
        }
        .station-select-title-v50 .select-title-green {
            color: #00a43c !important;
            font-weight: 950 !important;
        }

        /* 손가락 그림 + 선택 안내 */
        .select-instruction-v514 {
            display: flex !important;
            align-items: center !important;
            gap: 8px !important;
            margin: 0 0 4px 0 !important;
            padding: 0 6px 0 4px !important;
            min-height: 62px !important;
            color: #111 !important;
            font-size: 20px !important;
            line-height: 1.25 !important;
            font-weight: 800 !important;
        }
        .select-instruction-v514 img {
            width: 62px !important;
            height: 62px !important;
            object-fit: cover !important;
            object-position: center !important;
            flex: 0 0 62px !important;
        }

        /* 선택 콤보 상자를 안내문 바로 아래 배치 */
        .st-key-station_choice_input_box {
            margin-top: 0 !important;
            padding-top: 8px !important;
            padding-bottom: 8px !important;
        }
        .st-key-station_choice_input_box > div[data-testid="stVerticalBlock"] {
            gap: 0.35rem !important;
        }

        /* ②~④ 화면 본문의 Streamlit 기본 세로 간격을 ① 화면 수준으로 통일 */
        div[data-testid="stVerticalBlock"] {
            gap: 0.55rem !important;
        }
        .report-v41-headrow,
        .record-input-title,
        .reference-main-title-v51,
        .record-title {
            margin-top: 0 !important;
            margin-bottom: 6px !important;
        }
        .report-v41-help,
        .input-inline-note,
        .input-section-note {
            margin-top: 4px !important;
            margin-bottom: 6px !important;
            line-height: 1.35 !important;
        }
        .section-gap {
            height: 12px !important;
        }
        .record-section,
        .record-section.blue {
            margin-bottom: 10px !important;
        }

        @media (max-width: 900px) {
            .shared-station-confirm {
                margin-bottom: 8px !important;
            }
            .station-select-title-v50 {
                width: 235px !important;
                font-size: 24px !important;
                margin-bottom: 4px !important;
                padding-top: 5px !important;
            }
            .select-instruction-v514 {
                gap: 6px !important;
                min-height: 56px !important;
                font-size: 18px !important;
                margin-bottom: 2px !important;
            }
            .select-instruction-v514 img {
                width: 56px !important;
                height: 56px !important;
                flex-basis: 56px !important;
            }
            div[data-testid="stVerticalBlock"] {
                gap: 0.45rem !important;
            }
            .section-gap {
                height: 10px !important;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # ============================================================
    # 2. Station selection
    # ============================================================



if workflow_step == "②[보고]투표진행상황":
    with workflow_cluster_v59:
        # ①페이지와 동일하게 workflow_cluster 안에 nested container를 사용합니다.
        with st.container(key="report_body_v551"):
            st.markdown(
                f"""
                <div class="step1-fixed-layout-v531 report-page2-layout-v551">
                    {selected_station_confirm_html_v530}
                    <div class="confirm-to-title-gap-v531"></div>
                    <div class="station-select-title-v531">
                        <span class="select-title-green">②[보고]</span> 투표진행상황
                    </div>
                    <div class="report-subtitle-gap-v551"></div>
                    <div class="report-subtitle-v551">1.투표진행상황 보고(투표용지 교부수량 산출)</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            # v4.1 - 요청 이미지와 동일한 구성의 보고 화면
            st.markdown(
                """
                <style>
                .report-v41-headrow{display:flex;align-items:center;gap:12px;flex-wrap:wrap;margin:2px 0 8px 0;}
                .report-v41-title{display:inline-block;border:none;border-radius:0;padding:0;font-size:24px;font-weight:900;line-height:1.2;background:transparent;}
                .report-v41-target{display:none !important;}
                .report-v41-station{font-size:22px;font-weight:900;color:#7b159d;text-decoration:underline;text-underline-offset:4px;margin:0;}
                .report-v41-box-title{text-align:center;font-size:21px;font-weight:900;margin:0 0 10px 0;}
                .report-v41-label-red{color:red;font-size:22px;font-weight:900;line-height:1.22;margin-bottom:5px;} .report-v41-election{color:#1768b3;font-size:16px;font-weight:900;margin-left:6px;}
                .report-v41-label-blue{color:blue;font-size:22px;font-weight:900;line-height:1.22;margin-bottom:5px;text-align:center;}
                .report-v41-label-black{color:#111;font-size:18px;font-weight:900;line-height:1.22;margin-bottom:5px;text-align:center;}
                .report-v41-value-blue{color:blue;font-size:31px;font-weight:900;text-align:center;line-height:1.1;margin-top:6px;}
                .report-v41-value-black{color:#111;font-size:31px;font-weight:900;text-align:center;line-height:1.1;margin-top:6px;}
                .report-v41-help{font-size:15px;font-weight:800;margin-top:8px;line-height:1.35;}
                .report-v41-help .red{color:red;font-weight:900;}
                .report-v41-help .blue{color:blue;font-weight:900;}
                .report-v41-notice{font-size:18px;font-weight:900;margin:-2px 0 24px 0;line-height:1.4;}
                .report-v41-notice .blue{color:blue;font-weight:900;}
                .report-v41-ref-title{display:inline-block;border:none;border-radius:0;padding:0;font-size:20px;font-weight:900;line-height:1.25;margin:0 0 10px 0;background:transparent;}
                .report-v41-ref-title .station{color:#7b159d;text-decoration:underline;text-underline-offset:3px;}
                .st-key-report_input_calc_box{border:2px solid #7b159d !important;border-radius:6px !important;padding:10px 12px 9px 12px !important;margin:0 0 2px 0 !important;}
                .st-key-report_input_calc_box div[data-testid="stTextInput"] input{font-size:18px !important;font-weight:800 !important;color:#333 !important;background:#f1f3f6 !important;border-radius:6px !important;min-height:40px !important;}
                .st-key-report_input_calc_box div[data-testid="stTextInput"] input::placeholder{color:#777 !important;opacity:1 !important;font-weight:800 !important;}
                .report-v41-table{width:100%;border-collapse:collapse;table-layout:fixed;margin-top:2px;color:#111;}
                .report-v41-table th,.report-v41-table td{border:1px solid #c9c9c9;padding:8px 6px;text-align:center;font-size:15px;}
                .report-v41-table th{font-weight:900;background:#fff;}
                .report-v41-table td:first-child{font-weight:800;}
                @media(max-width:768px){
                  .report-v41-title{font-size:20px;padding:6px 9px;}
                  .report-v41-target{font-size:12px;}
                  .report-v41-station{font-size:19px;}
                  .report-v41-box-title{font-size:18px;}
                  .report-v41-label-red,.report-v41-label-blue{font-size:19px;} .report-v41-label-black{font-size:15px;}
                  .report-v41-value-blue,.report-v41-value-black{font-size:26px;}
                  .report-v41-notice{font-size:15px;}
                  .report-v41-ref-title{font-size:17px;}
                  .report-v41-table th,.report-v41-table td{font-size:13px;padding:7px 4px;}
                }
                </style>
                """,
                unsafe_allow_html=True,
            )

            if not db or station is None:
                st.warning("투표소가 선택되지 않았습니다. 먼저 ①[선택] 투표소에서 동과 투표소를 선택해 주세요.")
            else:
                station_display = f"{station['dong']} {station['station']}표소"

                if station["elections"]:
                    report_elections = [station["elections"][0]]
                    report_target_name = report_elections[0]["name"]
                else:
                    report_elections = []
                    report_target_name = "자료 없음"


                if not report_elections:
                    st.warning("보고대상 선거 자료가 없습니다.")

                errors = []
                with st.container(border=True, key="report_input_calc_box"):
                    for i, e in enumerate(report_elections):
                        c1, c2, c3 = st.columns([1.35, 0.95, 0.95], gap="small")

                        with c1:
                            st.markdown(
                                f'<div class="report-v41-label-red">[입력] <span class="report-v41-election">{e["name"]}</span><br>'
                                '잔여투표용지 첫 번호(NO.)</div>',
                                unsafe_allow_html=True,
                            )
                            cur_key = f"cur_text_{selected_key}_{i}"
                            raw = st.text_input(
                                "현재 잔여투표용지 첫 번호(NO.)",
                                value="",
                                placeholder="여기에 입력하세요",
                                key=cur_key,
                                on_change=format_numeric_session_value,
                                args=(cur_key,),
                                label_visibility="collapsed",
                            )

                        n = None
                        if raw.strip():
                            try:
                                n = int(raw.replace(",", "").strip())
                            except Exception:
                                errors.append(f"{e['name']}: 숫자만 입력해 주세요.")

                        cumulative = 0
                        remain = int(e["received"])
                        invalid_input = False
                        if raw.strip():
                            if n is None:
                                invalid_input = True
                            elif not valid_no(e, n):
                                invalid_input = True
                                errors.append(f"{e['name']}: 허용범위 {e['start_no']:,} ~ {e['end_no']+1:,}")
                            else:
                                cumulative = used_count(e, n)
                                remain = remaining_count(e, n)

                        with c2:
                            if invalid_input:
                                issued_value_html_v544 = '<div class="report-v41-value-blue" style="color:red; font-size:20px;">잘못된 입력</div>'
                            else:
                                issued_value_html_v544 = f'<div class="report-v41-value-blue">{cumulative:,}매</div>'
                            st.markdown(
                                '<div class="report-issued-highlight-v544">'
                                '<div class="report-v41-label-blue report-issued-label-one-line-v546">[보고] 교부수량</div>'
                                + issued_value_html_v544 +
                                '</div>',
                                unsafe_allow_html=True,
                            )

                        with c3:
                            st.markdown('<div class="report-v41-label-black"><br>잔여수량</div>', unsafe_allow_html=True)
                            if invalid_input:
                                st.markdown('<div class="report-v41-value-black" style="color:red; font-size:20px;">잘못된 입력</div>', unsafe_allow_html=True)
                            else:
                                st.markdown(f'<div class="report-v41-value-black">{remain:,}매</div>', unsafe_allow_html=True)

                        st.markdown(
                            '<div class="report-v544-help">'
                            '<span class="report-v544-help-mark">※</span>'
                            '<span class="report-v544-help-text">'
                            '보고대상 선거의 현재 남아 있는 '
                            '<span class="red">투표용지 첫 번호(NO.)를 [입력]란에</span><br>'
                            '기재 후 지금까지 <span class="blue">교부된 투표용지 수량을 산출</span>하여 보고합니다.'
                            '</span>'
                            '</div>',
                            unsafe_allow_html=True,
                        )

                    if errors:
                        st.error("\n\n".join("• " + x for x in errors))

                st.markdown(
                    '<div class="report-v41-notice">★ <span class="blue">투표관리관</span>은 매 35분까지 '
                    '<span class="blue">투표용지 교부수량</span>을 <span class="blue">보고</span>합니다. ★</div>',
                    unsafe_allow_html=True,
                )

                st.markdown(
                    f'<div class="report-v41-ref-title">2. 참고 - <span class="station">{station_display}</span> 에 배부된 투표용지 일련번호</div>',
                    unsafe_allow_html=True,
                )

                ref_rows = []
                for e in station["elections"]:
                    ref_rows.append(
                        "<tr>"
                        f"<td>{e['name']}</td>"
                        f"<td>{e['received']:,}</td>"
                        f"<td>{e['start_no']:,}</td>"
                        f"<td>{e['end_no']:,}</td>"
                        "</tr>"
                    )

                st.markdown(
                    '<table class="report-v41-table">'
                    '<thead><tr><th>선거명</th><th>수령매수</th><th>시작 No.</th><th>끝 No.</th></tr></thead>'
                    '<tbody>' + "".join(ref_rows) + '</tbody></table>',
                    unsafe_allow_html=True,
                )

            # ============================================================
            # 4. Record helper
            # ============================================================

elif workflow_step == "③[입력]투표록 기초자료":
    if not db:
        st.warning("기초자료가 없습니다. [관리자] 메뉴에서 엑셀자료를 업로드해 주세요.")
    elif station is None:
        st.warning("먼저 ① 투표소 선택에서 동과 투표소를 선택해 주세요.")
    else:
        # v4.4 입력 화면: 선거를 콤보박스로 선택하여 필요한 기초자료만 입력하고,
        # 자동 계산값은 내부에 유지하되 입력 화면에서는 숨깁니다.
        st.markdown(
            """
            <style>
            .input-summary-wrap {overflow-x:auto; -webkit-overflow-scrolling:touch; margin:10px 0 18px 0;}
            .input-summary-table {width:100%; border-collapse:collapse; table-layout:auto;}
            .input-summary-table th, .input-summary-table td {
                border:1px solid #c8c8c8; padding:8px 9px; text-align:center; vertical-align:middle;
                font-size:15px; font-weight:700;
            }
            .input-summary-table th {background:#fafafa; font-weight:900;}
            .input-summary-table th:first-child,
            .input-summary-table td:first-child {white-space:nowrap; min-width:145px;}
            .input-section-note {font-size:15px; line-height:1.55; color:#555; margin-bottom:10px;}
            @media (max-width:768px) {
                .input-summary-table {min-width:690px;}
                .input-summary-table th, .input-summary-table td {font-size:14px; padding:7px 7px;}
                .input-summary-table th:first-child,
                .input-summary-table td:first-child {min-width:140px;}
            }
            </style>
            """,
            unsafe_allow_html=True,
        )

        def parse_optional_int(value):
            txt = str(value or "").replace(",", "").strip()
            if txt == "":
                return None
            try:
                return int(txt)
            except Exception:
                return None

        record_store = local.setdefault("record_inputs_by_station", {})
        station_store = record_store.setdefault(selected_key, {})
        saved_j = station_store.setdefault("j_inputs", {})
        saved_a = station_store.setdefault("a_inputs", {})
        elections = station.get("elections", [])
        election_names = [e["name"] for e in elections]

        def compute_j_rows():
            rows = []
            for idx, e in enumerate(elections):
                start_no = int(e["start_no"])
                end_no = int(e["end_no"])
                received = int(e["received"])
                saved = saved_j.get(str(idx), {})
                first_raw = str(saved.get("first_raw", ""))
                damaged_raw = str(saved.get("damaged_raw", ""))
                damaged_serial = str(saved.get("damaged_serial", "") or "").strip()

                first_remaining = parse_optional_int(first_raw)
                damaged_count = parse_optional_int(damaged_raw)
                calc_error = None

                if first_raw.strip() and first_remaining is None:
                    calc_error = "잔여투표용지 첫 번호는 숫자로 입력해 주세요."
                elif first_remaining is not None and not (start_no <= first_remaining <= end_no + 1):
                    calc_error = f"잔여 첫 번호 허용범위: {start_no:,} ~ {end_no + 1:,}"

                if damaged_raw.strip() and damaged_count is None:
                    calc_error = "훼손 등 미교부 매수는 숫자로 입력해 주세요."
                elif damaged_count is not None and damaged_count < 0:
                    calc_error = "훼손 등 미교부 매수는 0 이상이어야 합니다."

                if first_remaining is None or calc_error:
                    issued = None
                    remaining = None
                    remaining_serial = "입력"
                else:
                    damaged = int(damaged_count or 0)
                    serial_consumed = first_remaining - start_no
                    if damaged > serial_consumed:
                        calc_error = "훼손 등 미교부 매수가 현재까지 진행된 일련번호 수보다 많습니다."
                        issued = None
                        remaining = None
                        remaining_serial = "입력"
                    else:
                        issued = serial_consumed - damaged
                        remaining = received - issued
                        if remaining <= 0:
                            remaining_serial = "잔여 없음"
                        elif first_remaining <= end_no:
                            remaining_serial = f"No. {first_remaining:,} ~ No. {end_no:,}"
                        else:
                            remaining_serial = "잔여 없음"

                rows.append({
                    "name": e["name"],
                    "received": received,
                    "issued": int(issued or 0),
                    "remaining": int(remaining if remaining is not None else received),
                    "first_remaining": first_remaining,
                    "damaged": int(damaged_count or 0),
                    "damaged_serial": damaged_serial,
                    "remaining_serial": remaining_serial,
                    "start_no": start_no,
                    "end_no": end_no,
                    "valid": issued is not None and remaining is not None and calc_error is None,
                    "error": calc_error,
                })
            return rows

        def compute_a_rows(j_rows):
            rows = []
            for idx, e in enumerate(elections):
                saved = saved_a.get(str(idx), {})
                raw2 = str(saved.get("v2_raw", ""))
                raw3 = str(saved.get("v3_raw", ""))
                raw4 = str(saved.get("v4_raw", ""))
                v2 = parse_optional_int(raw2)
                v3 = parse_optional_int(raw3)
                v4 = parse_optional_int(raw4)
                issued_from_j = int(j_rows[idx]["issued"]) if idx < len(j_rows) and j_rows[idx]["valid"] else None
                manual_inputs_complete = all(v is not None for v in (v2, v3, v4))
                v1 = None
                total_a = None
                calc_error = None

                if issued_from_j is not None and manual_inputs_complete:
                    other_sum = int(v2) + int(v3) + int(v4)
                    v1 = issued_from_j - other_sum
                    if v1 < 0:
                        calc_error = "(2)+(3)+(4)가 교부매수보다 큽니다."
                        v1 = None
                    else:
                        total_a = v1 + int(v2) + int(v3) + int(v4)

                rows.append({
                    "name": e["name"],
                    "registered": int(station["registered"]),
                    "v1": int(v1 or 0),
                    "v2": int(v2 or 0),
                    "v3": int(v3 or 0),
                    "v4": int(v4 or 0),
                    "total": int(total_a or 0),
                    "has_input": total_a is not None,
                    "error": calc_error,
                })
            return rows

        # 자의 자동 계산값을 먼저 내부에서 준비합니다. 화면에는 숨깁니다.
        j_rows = compute_j_rows()

        # ----------------------------------------------------
        # 아. 관련 기초자료 입력 — 먼저 배치
        # ----------------------------------------------------
        st.markdown(
            '<div class="record-input-title"><span class="num">1.</span> ' 
            '<span class="small">(투표록2p)</span> <span class="record-under">&apos;아. 투표상황&apos;</span> 기초자료 입력</div>',
            unsafe_allow_html=True,
        )

        st.markdown(
            '<div class="election-choice-label">★ 선거명 선택 '
            '<span>(아래 콤보박스에서 선거명 선택 후 입력)</span></div>',
            unsafe_allow_html=True,
        )
        a_choice = st.selectbox(
            "선거명",
            ["여기서 선거명을 선택하세요"] + election_names,
            index=0,
            key=f"a_election_select_{selected_key}",
            label_visibility="collapsed",
        )

        if a_choice != "여기서 선거명을 선택하세요":
            a_idx = election_names.index(a_choice)
            a_saved = saved_a.setdefault(str(a_idx), {})
            ac1, ac2, ac3 = st.columns(3, gap="small")
            with ac1:
                st.markdown('<div class="record-field-label">거소투표용지 미발송·반송자</div>', unsafe_allow_html=True)
                a2_key = f"a2_{selected_key}_{a_idx}"
                raw2 = st.text_input(
                    "거소투표용지 미발송·반송자",
                    value=format_numeric_text(a_saved.get("v2_raw", "")),
                    placeholder="여기에 입력하세요",
                    key=a2_key,
                    on_change=format_numeric_session_value,
                    args=(a2_key,),
                    label_visibility="collapsed",
                )
            with ac2:
                st.markdown('<div class="record-field-label">결정서 지참자</div>', unsafe_allow_html=True)
                a3_key = f"a3_{selected_key}_{a_idx}"
                raw3 = st.text_input(
                    "결정서 지참자",
                    value=format_numeric_text(a_saved.get("v3_raw", "")),
                    placeholder="여기에 입력하세요",
                    key=a3_key,
                    on_change=format_numeric_session_value,
                    args=(a3_key,),
                    label_visibility="collapsed",
                )
            with ac3:
                st.markdown('<div class="record-field-label">거소투표용지와 회송용봉투 반납자</div>', unsafe_allow_html=True)
                a4_key = f"a4_{selected_key}_{a_idx}"
                raw4 = st.text_input(
                    "거소투표용지와 회송용봉투 반납자",
                    value=format_numeric_text(a_saved.get("v4_raw", "")),
                    placeholder="여기에 입력하세요",
                    key=a4_key,
                    on_change=format_numeric_session_value,
                    args=(a4_key,),
                    label_visibility="collapsed",
                )
            a_saved["v2_raw"] = str(raw2)
            a_saved["v3_raw"] = str(raw3)
            a_saved["v4_raw"] = str(raw4)

            st.markdown(
                '<div class="input-inline-note">※ 투표 중 위 3가지 사유에 해당하는 선거인 수를 각각 입력합니다.</div>',
                unsafe_allow_html=True,
            )

        a_rows = compute_a_rows(j_rows)
        for idx, ar in enumerate(a_rows):
            if ar.get("error"):
                st.error(f"{ar['name']}: {ar['error']}")

        a_summary_rows = []
        for idx, e in enumerate(elections):
            saved = saved_a.get(str(idx), {})
            d2 = format_numeric_text(saved.get("v2_raw", "")) or "미입력"
            d3 = format_numeric_text(saved.get("v3_raw", "")) or "미입력"
            d4 = format_numeric_text(saved.get("v4_raw", "")) or "미입력"
            a_summary_rows.append(
                f"<tr><td>{e['name']}</td><td>{d2}</td><td>{d3}</td><td>{d4}</td></tr>"
            )
        st.markdown(
            '<div class="input-summary-wrap"><table class="input-summary-table">'
            '<thead><tr><th>선거명</th><th>거소투표용지 미발송·반송자(2)</th>'
            '<th>결정서 지참자(3)</th><th>거소투표용지와 회송용봉투 반납자(4)</th></tr></thead>'
            f'<tbody>{"".join(a_summary_rows)}</tbody></table></div>',
            unsafe_allow_html=True,
        )

        st.markdown('<div class="section-gap"></div>', unsafe_allow_html=True)

        # ----------------------------------------------------
        # 자. 관련 기초자료 입력 — 아 다음에 배치
        # ----------------------------------------------------
        st.markdown(
            '<div class="record-input-title"><span class="num">2.</span> ' 
            '<span class="small">(투표록2p)</span> <span class="record-under">&apos;자. 투표용지 수령·교부상황&apos;</span> 기초자료 입력</div>',
            unsafe_allow_html=True,
        )

        st.markdown(
            '<div class="election-choice-label">★ 선거명 선택 '
            '<span>(아래 콤보박스에서 선거명 선택 후 입력)</span></div>',
            unsafe_allow_html=True,
        )
        j_choice = st.selectbox(
            "선거명 ",
            ["여기서 선거명을 선택하세요"] + election_names,
            index=0,
            key=f"j_election_select_{selected_key}",
            label_visibility="collapsed",
        )

        selected_j_idx = None
        if j_choice != "여기서 선거명을 선택하세요":
            selected_j_idx = election_names.index(j_choice)
            j_saved = saved_j.setdefault(str(selected_j_idx), {})
            jc1, jc2, jc3 = st.columns([1.0, 1.0, 1.35], gap="small")
            with jc1:
                st.markdown('<div class="record-field-label">(남아있는) 잔여투표용지 첫 번호(NO.)</div>', unsafe_allow_html=True)
                j_first_key = f"j_first_{selected_key}_{selected_j_idx}"
                first_raw = st.text_input(
                    "(남아있는) 잔여투표용지 첫 번호(NO.)",
                    value=format_numeric_text(j_saved.get("first_raw", "")),
                    placeholder="여기에 입력하세요",
                    key=j_first_key,
                    on_change=format_numeric_session_value,
                    args=(j_first_key,),
                    label_visibility="collapsed",
                )
            with jc2:
                st.markdown('<div class="record-field-label">훼손 등 미교부한 투표용지 매수</div>', unsafe_allow_html=True)
                j_damaged_key = f"j_damaged_{selected_key}_{selected_j_idx}"
                damaged_raw = st.text_input(
                    "훼손 등 미교부한 투표용지 매수",
                    value=format_numeric_text(j_saved.get("damaged_raw", "")),
                    placeholder="여기에 입력하세요",
                    key=j_damaged_key,
                    on_change=format_numeric_session_value,
                    args=(j_damaged_key,),
                    label_visibility="collapsed",
                )
            with jc3:
                st.markdown('<div class="record-field-label">훼손 등 미교부한 투표용지 일련번호</div>', unsafe_allow_html=True)
                j_serial_key = f"j_damaged_serial_{selected_key}_{selected_j_idx}"
                damaged_serial = st.text_input(
                    "훼손 등 미교부한 투표용지 일련번호",
                    value=str(j_saved.get("damaged_serial", "")),
                    placeholder="입력예시: 1,501, 1,503, 1,504,",
                    key=j_serial_key,
                    on_change=format_serial_list_session_value,
                    args=(j_serial_key,),
                    label_visibility="collapsed",
                )
            j_saved["first_raw"] = str(first_raw)
            j_saved["damaged_raw"] = str(damaged_raw)
            j_saved["damaged_serial"] = str(damaged_serial or "").strip()

            st.markdown(
                '<div class="input-inline-note">※ 훼손등 미교부한 투표용지 : 투표용지 교부과정에서 선거인에게 교부하지 않고 투표용지 맨 뒤로 돌린 미교부 투표용지</div>',
                unsafe_allow_html=True,
            )

        # 방금 입력값으로 자의 자동 계산값을 갱신합니다.
        j_rows = compute_j_rows()
        if selected_j_idx is not None and j_rows[selected_j_idx].get("error"):
            st.error(f"{j_rows[selected_j_idx]['name']}: {j_rows[selected_j_idx]['error']}")

        j_summary_rows = []
        for idx, e in enumerate(elections):
            saved = saved_j.get(str(idx), {})
            d_first = format_numeric_text(saved.get("first_raw", "")) or "미입력"
            d_damaged = format_numeric_text(saved.get("damaged_raw", "")) or "미입력"
            d_serial = str(saved.get("damaged_serial", "") or "").strip() or "미입력"
            j_summary_rows.append(
                f"<tr><td>{e['name']}</td><td>{d_first}</td><td>{d_damaged}</td><td>{d_serial}</td></tr>"
            )
        st.markdown(
            '<div class="input-summary-wrap"><table class="input-summary-table">'
            '<thead><tr><th>선거명</th><th>(남아있는) 잔여투표용지 첫 번호(NO.)</th>'
            '<th>훼손 등 미교부한 투표용지 매수</th><th>훼손 등 미교부한 투표용지 일련번호</th></tr></thead>'
            f'<tbody>{"".join(j_summary_rows)}</tbody></table></div>',
            unsafe_allow_html=True,
        )

        # 자 입력이 바뀌면 아의 자동 계산값도 같은 실행에서 다시 계산합니다.
        a_rows = compute_a_rows(j_rows)
        st.session_state[f"record_a_rows_{selected_key}"] = a_rows
        st.session_state[f"record_j_rows_{selected_key}"] = j_rows
        station_store["a_rows"] = a_rows
        station_store["j_rows"] = j_rows
        save_local()

        st.markdown(
            '<div class="record-final-notice">각 선거의 입력된 내용을 기준으로 투표록 2p 작성 참고자료가 자동 계산됩니다. '
            '<span class="warn">자료 입력시 정확하게 입력하시기 바랍니다.</span></div>',
            unsafe_allow_html=True,
        )

elif workflow_step == "④[작성참고] 투표록(2p)":
    if not db:
        st.warning("기초자료가 없습니다. [관리자] 메뉴에서 엑셀자료를 업로드해 주세요.")
    elif station is None:
        st.warning("먼저 ① 투표소 선택에서 동과 투표소를 선택해 주세요.")
    else:
        station_display = f"{station['dong']} {station['station']}표소"

        saved_station_record = local.get("record_inputs_by_station", {}).get(selected_key, {})
        a_saved = st.session_state.get(
            f"record_a_rows_{selected_key}",
            saved_station_record.get("a_rows", [])
        )
        j_saved = st.session_state.get(
            f"record_j_rows_{selected_key}",
            saved_station_record.get("j_rows", [])
        )

        st.markdown('<div class="reference-main-title-v51">1. 투표록(2p) 작성 참고자료</div>', unsafe_allow_html=True)
        st.markdown('<div class="record-section">', unsafe_allow_html=True)
        st.markdown('<div class="record-title">&apos;아. 투표상황&apos;</div>', unsafe_allow_html=True)

        a_html = []
        for idx, e in enumerate(station["elections"]):
            if idx < len(a_saved):
                ar = a_saved[idx]
            else:
                ar = {
                    "registered": int(station["registered"]),
                    "v1": 0, "v2": 0, "v3": 0, "v4": 0, "total": 0,
                    "has_input": False
                }

            has_input = bool(ar.get("has_input", False))
            def disp(v):
                return f"{int(v):,}" if has_input else "입력"

            a_html.append(
                "<tr>"
                f"<td>{e['name']}</td>"
                f"<td>{int(ar['registered']):,}</td>"
                f"<td>{disp(ar['v1'])}</td>"
                f"<td>{disp(ar['v2'])}</td>"
                f"<td>{disp(ar['v3'])}</td>"
                f"<td>{disp(ar['v4'])}</td>"
                f"<td>{disp(ar['total'])}</td>"
                "</tr>"
            )

        st.markdown(
            """
            <table class="record-table reference-a-table">
              <thead>
                <tr>
                  <th rowspan="2">선거명</th>
                  <th rowspan="2">선거인명부<br>등재자수<br>(사전투표자수·<br>거소투표신고인수 제외)<br>(가)</th>
                  <th colspan="5">투표자수</th>
                </tr>
                <tr>
                  <th>선거인명부<br>등재자<br>(1)</th>
                  <th>거소투표용지<br>미발송·반송자<br>(2)</th>
                  <th>결정서<br>지참자<br>(3)</th>
                  <th>거소투표용지와<br>회송용봉투 반납자<br>(4)</th>
                  <th>계<br>(나)<br>(1+2+3+4)</th>
                </tr>
              </thead>
              <tbody>
            """ + "".join(a_html) + """
              </tbody>
            </table>
            """,
            unsafe_allow_html=True
        )
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="record-section blue">', unsafe_allow_html=True)
        st.markdown('<div class="record-title">&apos;자. 투표용지 수령교부상황&apos;</div>', unsafe_allow_html=True)

        j_html = []
        validation_rows = []

        for idx, e in enumerate(station["elections"]):
            if idx < len(j_saved):
                jr = j_saved[idx]
            else:
                jr = {
                    "received": int(e["received"]),
                    "issued": 0,
                    "remaining": int(e["received"]),
                    "first_remaining": None,
                    "damaged_serial": "",
                    "valid": False,
                }

            valid = bool(jr.get("valid", False))
            first_remaining = jr.get("first_remaining")
            remaining = int(jr.get("remaining", int(e["received"])))
            issued_val = int(jr.get("issued", 0))

            damaged_serial = str(jr.get("damaged_serial", "") or "").strip()

            if not valid:
                serial_text = "입력"
            elif remaining <= 0:
                serial_text = "잔여 없음"
            else:
                remain_range = f"No. {int(first_remaining):,} ~ No. {int(e['end_no']):,}"
                if damaged_serial:
                    # ③에서 입력한 훼손 등 미교부 일련번호도 ④의 같은 칸에 함께 표시
                    serial_text = (
                        f"{remain_range}"
                        f"<br><span style='font-size:13px;'>{damaged_serial}</span>"
                    )
                else:
                    serial_text = remain_range

            j_html.append(
                "<tr>"
                f"<td>{e['name']}</td>"
                f"<td>{int(e['received']):,}</td>"
                f"<td>{issued_val:,}</td>"
                f"<td>{remaining:,}</td>"
                f"<td>{serial_text}</td>"
                "</tr>"
            )

            a_total = int(a_saved[idx]["total"]) if idx < len(a_saved) else 0
            a_has = bool(a_saved[idx].get("has_input", False)) if idx < len(a_saved) else False
            matched = a_has and valid and a_total == issued_val
            validation_rows.append((e["name"], a_total, issued_val, matched, a_has, valid))

        st.markdown(
            """
            <table class="record-table">
              <thead>
                <tr>
                  <th>선거명</th>
                  <th>수령매수<br>(다)</th>
                  <th>교부매수<br>(라)</th>
                  <th>잔여매수<br>(마=다-라)</th>
                  <th>잔여 투표용지 일련번호<br><span style="font-size:12px;">(훼손 등 미교부 일련번호 포함)</span></th>
                </tr>
              </thead>
              <tbody>
            """ + "".join(j_html) + """
              </tbody>
            </table>
            """,
            unsafe_allow_html=True
        )
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("### 2. 검증('아','자' 일치 여부)")
        all_match = True
        any_ready = False

        for name, a_total, issued_val, matched, a_has, j_valid in validation_rows:
            if not a_has or not j_valid:
                all_match = False
                st.warning(f"○ {name}: 검증을 위해 ③ 기초자료 입력을 완료해 주세요.")
                continue

            any_ready = True
            all_match = all_match and matched

            if matched:
                st.success(f"✓ {name}: 계(나) {a_total:,} = 교부매수(라) {issued_val:,}")
            else:
                diff = abs(a_total - issued_val)
                st.error(
                    f"⚠ {name}: 계(나) {a_total:,} ≠ 교부매수(라) {issued_val:,} "
                    f"(차이 {diff:,})"
                )

        if validation_rows and any_ready:
            if all_match:
                st.success("✓ 모든 선거에서 아. 계(나)와 자. 교부매수(라)가 일치합니다.")
            else:
                st.error("⚠ 미입력 또는 불일치 항목이 있습니다. 투표록 작성 전 확인하세요.")

        st.info("※ 본 화면은 투표록 2p 작성 참고용입니다. 실제 기재 전 원자료와 반드시 대조하십시오.")

elif workflow_step == "[관리자]":
    st.subheader("[관리자]")
    st.caption("기초자료 업로드 및 변경은 관리자 비밀번호 확인 후 사용할 수 있습니다.")

    if "admin_authenticated" not in st.session_state:
        st.session_state.admin_authenticated = False

    if not st.session_state.admin_authenticated:
        admin_pw = st.text_input("관리자 비밀번호", type="password", key="admin_password_input")
        c1, c2 = st.columns([1, 2])
        with c1:
            if st.button("🔐 관리자 로그인", width="stretch"):
                if admin_pw == current_admin_password():
                    st.session_state.admin_authenticated = True
                    st.success("관리자 인증이 완료되었습니다.")
                    st.rerun()
                else:
                    st.error("비밀번호가 올바르지 않습니다.")
        st.info("최초 실행 시 기본 관리자 비밀번호는 1234입니다. 로그인 후 비밀번호를 변경할 수 있습니다.")
    else:
        c1, c2 = st.columns([3, 1])
        with c1:
            st.success("관리자 인증 상태입니다.")
        with c2:
            if st.button("로그아웃", width="stretch"):
                st.session_state.admin_authenticated = False
                st.rerun()

        st.divider()
        st.subheader("엑셀 기초자료 업로드")
        st.write(
            "국선용 엑셀 파일을 업로드하면 **투표구명, 선거인명부 등재자수, "
            "투표용지 수령매수, 시작번호, 끝번호**를 자동으로 불러옵니다."
        )
        st.info(
            "※ 새 국선 형식(A열 투표구명 / B열 등재자수 / C열 수령매수 / "
            "D열 시작번호 / E열 끝번호 / F열 비고)을 지원합니다. "
            "'비고' 열은 앱에서 읽거나 표시하지 않습니다."
        )

        uploaded = st.file_uploader("기초자료 엑셀 파일 선택", type=["xlsx"])

        if uploaded is not None:
            st.caption(f"선택된 파일: {uploaded.name}")
            if st.button("📥 엑셀자료 불러오기", width="stretch"):
                try:
                    new_db, count = parse_uploaded_xlsx(uploaded.getvalue())
                    st.session_state.station_db = new_db
                    save_db(new_db)
                    local["selected_key"] = None
                    save_local()
                    st.success(
                        f"엑셀자료를 정상적으로 불러왔습니다. "
                        f"투표소 {len(new_db):,}개, 선거별 기초자료 {count:,}건을 등록했습니다."
                    )
                    st.rerun()
                except Exception as e:
                    st.error(f"엑셀자료를 불러오지 못했습니다.\n\n{e}")

        st.divider()
        st.subheader("현재 등록 상태")
        total_elections = sum(len(v.get("elections", [])) for v in db.values())
        c1, c2 = st.columns(2)
        c1.metric("등록 투표소", f"{len(db):,}개")
        c2.metric("선거별 기초자료", f"{total_elections:,}건")

        if db:
            with st.expander("현재 등록자료 보기", expanded=False):
                preview_rows = []
                for key, v in db.items():
                    for e in v.get("elections", []):
                        preview_rows.append({
                            "동위원회명": v["dong"],
                            "투표소명": v["station"],
                            "선거인명부 등재자수": v["registered"],
                            "선거명": e["name"],
                            "수령매수": e["received"],
                            "시작 No.": e["start_no"],
                            "끝 No.": e["end_no"],
                        })
                st.dataframe(preview_rows, width="stretch", hide_index=True)

        st.divider()
        st.subheader("등록자료 삭제")
        st.warning("등록자료 삭제는 별도의 비밀번호 확인 후 진행됩니다.")

        if "delete_confirm_mode" not in st.session_state:
            st.session_state.delete_confirm_mode = False

        if not st.session_state.delete_confirm_mode:
            if st.button("🗑️ 현재 등록자료 삭제", width="stretch"):
                st.session_state.delete_confirm_mode = True
                st.rerun()
        else:
            delete_pw = st.text_input(
                "삭제 확인 비밀번호",
                type="password",
                key="delete_password_input"
            )
            c1, c2 = st.columns(2)
            with c1:
                if st.button("삭제 실행", width="stretch"):
                    if delete_pw == current_admin_password():
                        st.session_state.station_db = {}
                        save_db({})
                        local["selected_key"] = None
                        save_local()
                        st.session_state.delete_confirm_mode = False
                        st.success("현재 등록된 기초자료를 삭제했습니다.")
                        st.rerun()
                    else:
                        st.error("비밀번호가 올바르지 않습니다.")
            with c2:
                if st.button("삭제 취소", width="stretch"):
                    st.session_state.delete_confirm_mode = False
                    st.rerun()

        st.divider()
        st.subheader("초기화면 로그인 비밀번호 변경")
        st.caption("앱을 처음 열 때 사용하는 로그인 비밀번호를 변경합니다.")

        current_access_pw = st.text_input(
            "현재 로그인 비밀번호",
            type="password",
            key="change_access_current_pw"
        )
        new_access_pw = st.text_input(
            "새 로그인 비밀번호",
            type="password",
            key="change_access_new_pw"
        )
        new_access_pw_confirm = st.text_input(
            "새 로그인 비밀번호 확인",
            type="password",
            key="change_access_new_pw_confirm"
        )

        if st.button("🔑 로그인 비밀번호 변경", width="stretch"):
            if current_access_pw != current_app_access_password():
                st.error("현재 로그인 비밀번호가 올바르지 않습니다.")
            elif len(new_access_pw) < 4:
                st.error("새 로그인 비밀번호는 4자리 이상으로 설정해 주세요.")
            elif new_access_pw != new_access_pw_confirm:
                st.error("새 로그인 비밀번호와 확인 비밀번호가 일치하지 않습니다.")
            elif new_access_pw == current_access_pw:
                st.error("새 로그인 비밀번호가 현재 비밀번호와 같습니다.")
            else:
                save_app_access_password(new_access_pw)
                st.success("초기화면 로그인 비밀번호가 변경되었습니다. 다음 실행부터 새 비밀번호를 사용해 주세요.")

        st.divider()
        st.subheader("관리자 비밀번호 변경")
        st.caption("현재 비밀번호를 확인한 후 새 비밀번호로 변경합니다.")

        current_pw_input = st.text_input(
            "현재 비밀번호",
            type="password",
            key="change_current_pw"
        )
        new_pw_input = st.text_input(
            "새 비밀번호",
            type="password",
            key="change_new_pw"
        )
        new_pw_confirm = st.text_input(
            "새 비밀번호 확인",
            type="password",
            key="change_new_pw_confirm"
        )

        if st.button("🔑 비밀번호 변경", width="stretch"):
            if current_pw_input != current_admin_password():
                st.error("현재 비밀번호가 올바르지 않습니다.")
            elif len(new_pw_input) < 4:
                st.error("새 비밀번호는 4자리 이상으로 설정해 주세요.")
            elif new_pw_input != new_pw_confirm:
                st.error("새 비밀번호와 확인 비밀번호가 일치하지 않습니다.")
            elif new_pw_input == current_pw_input:
                st.error("새 비밀번호가 현재 비밀번호와 같습니다.")
            else:
                save_admin_password(new_pw_input)
                st.success("관리자 비밀번호가 변경되었습니다. 앞으로 새 비밀번호를 사용해 주세요.")


# ============================================================
# v5.6 휴대전화 실제 화면 최종 보정
# - 휴대폰 캡처(세로 화면) 기준 제목/관리자/안내/메뉴/보고영역 재배치
# - 기존 계산/저장/메뉴 기능은 변경하지 않음
# ============================================================
st.markdown(
    r"""
    <style>
    @media (max-width: 768px) {
        /* 화면 좌우 여백 최소화 */
        .block-container {
            padding-left: .42rem !important;
            padding-right: .42rem !important;
            max-width: 100% !important;
        }

        /* 제목 + 관리자: 한 줄 유지, 겹침 방지 */
        div[data-testid="stHorizontalBlock"]:has(.st-key-title_admin_v52) {
            display: grid !important;
            grid-template-columns: minmax(0,1fr) 48px !important;
            gap: 2px !important;
            align-items: center !important;
            width: 100% !important;
        }
        div[data-testid="stHorizontalBlock"]:has(.st-key-title_admin_v52) > div[data-testid="stColumn"] {
            width: auto !important; min-width: 0 !important; flex: none !important;
        }
        .app-main-title-v33 {
            font-size: 19px !important;
            line-height: 1.08 !important;
            letter-spacing: -1px !important;
            white-space: nowrap !important;
            margin: 0 !important;
        }
        .mobile-version-v51 {font-size: 15px !important;}
        .st-key-title_admin_v52 button {
            min-height: 23px !important; height: 23px !important;
            border: none !important; background: transparent !important;
            padding: 0 !important; margin: 0 !important;
        }
        .st-key-title_admin_v52 button p {
            font-size: 10px !important; color: #111 !important;
            font-weight: 900 !important; white-space: nowrap !important;
        }

        /* 안내문과 ①~④ 메뉴: 실제 휴대폰 화면에서 자연스럽게 바로 이어지도록 */
        .workflow-guide-v33 {
            display: block !important;
            width: 100% !important;
            max-width: 100% !important;
            font-size: 12.2px !important;
            line-height: 1.15 !important;
            letter-spacing: -.5px !important;
            white-space: nowrap !important;
            transform: none !important;
            padding: 0 !important;
            margin: 8px 0 5px 0 !important;
        }
        div[data-testid="stMarkdownContainer"]:has(.workflow-guide-v33) {
            margin: 0 !important; padding: 0 !important;
        }
        div[data-testid="stHorizontalBlock"]:has(.st-key-navcard_select_v35) {
            display: grid !important;
            grid-template-columns: minmax(0,.92fr) 12px minmax(0,1.22fr) 12px minmax(0,1.22fr) 12px minmax(0,1.20fr) !important;
            gap: 1px !important;
            align-items: center !important;
            width: 100% !important;
            margin: 0 !important;
            padding: 0 !important;
        }
        div[data-testid="stHorizontalBlock"]:has(.st-key-navcard_select_v35) > div[data-testid="stColumn"] {
            width: auto !important; min-width: 0 !important; flex: none !important; padding: 0 !important;
        }
        [class*="st-key-navcard_"] button {
            min-height: 64px !important; height: 64px !important;
            padding: 0 1px !important; border-radius: 6px !important;
        }
        .st-key-navcard_select_v35 button::after,
        .st-key-navcard_report_v35 button::after,
        .st-key-navcard_input_v35 button::after,
        .st-key-navcard_reference_v35 button::after {
            left: 16px !important; right: 1px !important; top: 9px !important;
            font-size: 9.5px !important; text-align: center !important;
            white-space: nowrap !important; letter-spacing: -.45px !important;
        }
        .st-key-navcard_select_v35 button p,
        .st-key-navcard_report_v35 button p,
        .st-key-navcard_input_v35 button p,
        .st-key-navcard_reference_v35 button p {
            left: 16px !important; right: 1px !important; top: 35px !important;
            font-size: 10.2px !important; line-height: 1.02 !important;
            text-align: center !important; white-space: nowrap !important;
            letter-spacing: -.65px !important;
        }
        [class*="st-key-navcard_"] button::before {left: 3px !important; font-size: 13px !important;}
        .nav-arrow-v35 {
            min-height: 64px !important; height: 64px !important;
            font-size: 18px !important; margin: 0 !important; padding: 0 !important;
            display: flex !important; align-items: center !important; justify-content: center !important;
        }

        /* 선택 투표소 확인문 */
        .selected-station-confirm {
            width: fit-content !important; max-width: 100% !important;
            min-height: 0 !important; margin: 7px 0 10px 0 !important;
            padding: 7px 10px !important; line-height: 1.12 !important;
        }
        .selected-station-confirm, .selected-station-confirm * {font-size: 14px !important;}
        .selected-station-confirm .selected-name {font-size: 16px !important;}

        /* 보고 화면: 입력은 위 1줄, 보고/잔여수량은 아래 2열 */
        .report-v41-title {
            font-size: 19px !important; line-height: 1.15 !important;
            letter-spacing: -.55px !important; white-space: nowrap !important;
        }
        .st-key-report_input_calc_box {
            padding: 9px 9px 10px 9px !important;
            margin-bottom: 2px !important;
        }
        .st-key-report_input_calc_box div[data-testid="stHorizontalBlock"] {
            display: grid !important;
            grid-template-columns: 1fr 1fr !important;
            gap: 5px 8px !important;
            align-items: start !important;
        }
        .st-key-report_input_calc_box div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"] {
            width: auto !important; min-width: 0 !important; flex: none !important;
        }
        .st-key-report_input_calc_box div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"]:first-child {
            grid-column: 1 / -1 !important;
        }
        .report-v41-label-red {font-size: 18px !important; line-height: 1.16 !important; margin-bottom: 4px !important;}
        .report-v41-election {font-size: 14px !important;}
        .report-v41-label-blue {font-size: 18px !important; line-height: 1.12 !important; margin: 2px 0 0 0 !important;}
        .report-v41-label-black {font-size: 15px !important; line-height: 1.12 !important; margin: 2px 0 0 0 !important;}
        .report-v41-value-blue,.report-v41-value-black {font-size: 26px !important; margin-top: 5px !important;}
        .st-key-report_input_calc_box div[data-testid="stTextInput"] input {
            min-height: 44px !important; height: 44px !important; font-size: 17px !important;
        }
        .report-v41-help {font-size: 12.5px !important; line-height: 1.35 !important; margin-top: 7px !important;}
        .report-v41-notice {font-size: 13.5px !important; line-height: 1.25 !important; margin: 5px 0 20px 0 !important;}
        .report-v41-ref-title {font-size: 16px !important; line-height: 1.2 !important;}

        /* 모바일 표는 내용 가독성을 우선하고 가로 스크롤 */
        .report-v41-table {min-width: 620px !important;}
        .report-v41-table th,.report-v41-table td {font-size: 12px !important; padding: 6px 4px !important;}
    }

    @media (max-width: 390px) {
        .app-main-title-v33 {font-size: 17px !important;}
        .mobile-version-v51 {font-size: 13.5px !important;}
        .workflow-guide-v33 {font-size: 11.2px !important;}
        .st-key-navcard_select_v35 button::after,
        .st-key-navcard_report_v35 button::after,
        .st-key-navcard_input_v35 button::after,
        .st-key-navcard_reference_v35 button::after {font-size: 8.5px !important;}
        .st-key-navcard_select_v35 button p,
        .st-key-navcard_report_v35 button p,
        .st-key-navcard_input_v35 button p,
        .st-key-navcard_reference_v35 button p {font-size: 9px !important;}
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ============================================================
# v5.7 모바일 메뉴 최종 보정
# - '★ 반드시~바랍니다. ★'와 ①~④ 메뉴 사이 세로 공백 최소화
# - 각 메뉴 카드 내부 글자 좌측 정렬
# - 카드 폭 안에서 단계명/메뉴명을 가능한 크게 표시
# ============================================================
st.markdown(
    r"""
    <style>
    @media (max-width: 768px) {
        /* 안내문 바로 아래 메뉴가 이어지도록 Streamlit 기본 block gap 상쇄 */
        div[data-testid="stMarkdownContainer"]:has(.workflow-guide-v33) {
            margin-bottom: -24px !important;
            padding-bottom: 0 !important;
        }
        .workflow-guide-v33 {
            margin-bottom: 0 !important;
            padding-bottom: 0 !important;
        }
        div[data-testid="stHorizontalBlock"]:has(.st-key-navcard_select_v35) {
            margin-top: -22px !important;
            margin-bottom: 0 !important;
            padding-top: 0 !important;
        }

        /* 카드 내부: 왼쪽 정렬 + 사용할 수 있는 폭 최대 활용 */
        [class*="st-key-navcard_"] button {
            min-height: 64px !important;
            height: 64px !important;
            padding: 0 !important;
            overflow: hidden !important;
        }
        [class*="st-key-navcard_"] button::before {
            left: 3px !important;
            font-size: 13px !important;
        }
        .st-key-navcard_select_v35 button::after,
        .st-key-navcard_report_v35 button::after,
        .st-key-navcard_input_v35 button::after,
        .st-key-navcard_reference_v35 button::after {
            left: 17px !important;
            right: 1px !important;
            top: 8px !important;
            text-align: left !important;
            font-size: 11.5px !important;
            line-height: 1 !important;
            letter-spacing: -0.7px !important;
            white-space: nowrap !important;
        }
        .st-key-navcard_select_v35 button p,
        .st-key-navcard_report_v35 button p,
        .st-key-navcard_input_v35 button p,
        .st-key-navcard_reference_v35 button p {
            left: 17px !important;
            right: 1px !important;
            top: 35px !important;
            text-align: left !important;
            font-size: 12.2px !important;
            font-weight: 900 !important;
            line-height: 1 !important;
            letter-spacing: -0.9px !important;
            white-space: nowrap !important;
        }
        /* 폭이 가장 좁은 ①은 글자를 조금 더 크게 유지 */
        .st-key-navcard_select_v35 button::after {font-size: 12px !important;}
        .st-key-navcard_select_v35 button p {font-size: 13px !important;}
    }

    @media (max-width: 390px) {
        div[data-testid="stMarkdownContainer"]:has(.workflow-guide-v33) {margin-bottom:-22px !important;}
        div[data-testid="stHorizontalBlock"]:has(.st-key-navcard_select_v35) {margin-top:-20px !important;}
        .st-key-navcard_select_v35 button::after,
        .st-key-navcard_report_v35 button::after,
        .st-key-navcard_input_v35 button::after,
        .st-key-navcard_reference_v35 button::after {font-size:10.4px !important; letter-spacing:-0.8px !important;}
        .st-key-navcard_select_v35 button p,
        .st-key-navcard_report_v35 button p,
        .st-key-navcard_input_v35 button p,
        .st-key-navcard_reference_v35 button p {font-size:11px !important; letter-spacing:-1px !important;}
        .st-key-navcard_select_v35 button::after {font-size:11px !important;}
        .st-key-navcard_select_v35 button p {font-size:12px !important;}
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# v5.9 상단 안내문/메뉴 간격 구조 고정
# - 안내문과 ①~④ 메뉴를 같은 keyed container 안에 배치
# - 실제 간격을 5mm로 고정하고 이전 음수 margin 규칙을 최종 override
# - 메뉴 글자는 카드 안에서 좌측 정렬 + 모바일 폭 내 최대 크기
# ============================================================
st.markdown(
    r"""
    <style>
    /* 같은 컨테이너 내부의 두 요소 간격을 정확히 5mm로 고정 */
    .st-key-workflow_cluster_v59 > div[data-testid="stVerticalBlock"],
    .st-key-workflow_cluster_v59 div[data-testid="stVerticalBlock"]:first-child {
        gap: 5mm !important;
        row-gap: 5mm !important;
    }
    .st-key-workflow_cluster_v59 div[data-testid="stMarkdownContainer"]:has(.workflow-guide-v33) {
        margin: 0 !important;
        padding: 0 !important;
    }
    .st-key-workflow_cluster_v59 .workflow-guide-v33 {
        margin: 0 !important;
        padding-top: 0 !important;
        padding-bottom: 0 !important;
    }
    .st-key-workflow_cluster_v59 div[data-testid="stHorizontalBlock"]:has(.st-key-navcard_select_v35) {
        margin: 0 !important;
        padding: 0 !important;
    }

    @media (max-width: 768px) {
        /* Streamlit 자체 element wrapper 여백도 제거 */
        .st-key-workflow_cluster_v59 > div[data-testid="stVerticalBlock"] > div[data-testid="stElementContainer"] {
            margin: 0 !important;
            padding: 0 !important;
        }
        .st-key-workflow_cluster_v59 > div[data-testid="stVerticalBlock"] {
            gap: 5mm !important;
            row-gap: 5mm !important;
        }

        /* 네비게이션 한 줄 고정 */
        .st-key-workflow_cluster_v59 div[data-testid="stHorizontalBlock"]:has(.st-key-navcard_select_v35) {
            display: grid !important;
            grid-template-columns: minmax(0,.92fr) 12px minmax(0,1.22fr) 12px minmax(0,1.22fr) 12px minmax(0,1.20fr) !important;
            gap: 1px !important;
            width: 100% !important;
            align-items: center !important;
        }
        .st-key-workflow_cluster_v59 div[data-testid="stHorizontalBlock"]:has(.st-key-navcard_select_v35) > div[data-testid="stColumn"] {
            width: auto !important;
            min-width: 0 !important;
            flex: none !important;
            padding: 0 !important;
        }

        /* 제한된 카드 폭 내에서 최대한 크게 + 좌측 정렬 */
        .st-key-workflow_cluster_v59 [class*="st-key-navcard_"] button {
            min-height: 66px !important;
            height: 66px !important;
            padding: 0 !important;
            overflow: hidden !important;
        }
        .st-key-workflow_cluster_v59 [class*="st-key-navcard_"] button::before {
            left: 3px !important;
            font-size: 13px !important;
        }
        .st-key-workflow_cluster_v59 .st-key-navcard_select_v35 button::after,
        .st-key-workflow_cluster_v59 .st-key-navcard_report_v35 button::after,
        .st-key-workflow_cluster_v59 .st-key-navcard_input_v35 button::after,
        .st-key-workflow_cluster_v59 .st-key-navcard_reference_v35 button::after {
            left: 17px !important;
            right: 1px !important;
            top: 8px !important;
            text-align: left !important;
            font-size: 12px !important;
            line-height: 1 !important;
            letter-spacing: -0.8px !important;
            white-space: nowrap !important;
        }
        .st-key-workflow_cluster_v59 .st-key-navcard_select_v35 button p,
        .st-key-workflow_cluster_v59 .st-key-navcard_report_v35 button p,
        .st-key-workflow_cluster_v59 .st-key-navcard_input_v35 button p,
        .st-key-workflow_cluster_v59 .st-key-navcard_reference_v35 button p {
            left: 17px !important;
            right: 1px !important;
            top: 36px !important;
            text-align: left !important;
            font-size: 12.8px !important;
            font-weight: 950 !important;
            line-height: 1 !important;
            letter-spacing: -1px !important;
            white-space: nowrap !important;
        }
        .st-key-workflow_cluster_v59 .st-key-navcard_select_v35 button::after {font-size: 12.6px !important;}
        .st-key-workflow_cluster_v59 .st-key-navcard_select_v35 button p {font-size: 13.8px !important;}
        .st-key-workflow_cluster_v59 .nav-arrow-v35 {
            min-height: 66px !important;
            height: 66px !important;
            font-size: 18px !important;
            margin: 0 !important;
            padding: 0 !important;
        }
    }

    @media (max-width: 390px) {
        .st-key-workflow_cluster_v59 .st-key-navcard_select_v35 button::after,
        .st-key-workflow_cluster_v59 .st-key-navcard_report_v35 button::after,
        .st-key-workflow_cluster_v59 .st-key-navcard_input_v35 button::after,
        .st-key-workflow_cluster_v59 .st-key-navcard_reference_v35 button::after {font-size:10.7px !important;}
        .st-key-workflow_cluster_v59 .st-key-navcard_select_v35 button p,
        .st-key-workflow_cluster_v59 .st-key-navcard_report_v35 button p,
        .st-key-workflow_cluster_v59 .st-key-navcard_input_v35 button p,
        .st-key-workflow_cluster_v59 .st-key-navcard_reference_v35 button p {font-size:11.4px !important;}
        .st-key-workflow_cluster_v59 .st-key-navcard_select_v35 button::after {font-size:11.3px !important;}
        .st-key-workflow_cluster_v59 .st-key-navcard_select_v35 button p {font-size:12.4px !important;}
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# v5.10 선택한 투표소 확인상자 상단 여백 균형 보정
# ============================================================
st.markdown(
    r"""
    <style>
    /* 진행메뉴 다음 확인상자까지의 간격을 컨테이너 기본 5mm 간격으로 통일 */
    .st-key-workflow_cluster_v59 .selected-station-confirm {
        margin: 0 !important;
    }
    .st-key-workflow_cluster_v59 div[data-testid="stMarkdownContainer"]:has(.selected-station-confirm) {
        margin: 0 !important;
        padding: 0 !important;
    }
    @media (max-width: 768px) {
        .st-key-workflow_cluster_v59 > div[data-testid="stVerticalBlock"] {
            gap: 5mm !important;
            row-gap: 5mm !important;
        }
        .st-key-workflow_cluster_v59 .selected-station-confirm {
            margin: 0 !important;
            padding: 7px 9px !important;
        }
        /* 컨테이너 종료 뒤 다음 본문과의 간격도 확인상자 위쪽과 비슷하게 유지 */
        .st-key-workflow_cluster_v59 {
            margin-bottom: 5mm !important;
            padding-bottom: 0 !important;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# v5.11 최종 UI 보정
# - 선택한 투표소 확인상자 ↔ ①[선택] 투표소 제목 간격 축소
# - ①[선택]은 초록색, 투표소는 검정색
# - 북구선거관리위원회 로고형 관리자 버튼의 테두리 완전 제거
# ============================================================
st.markdown(
    r"""
    <style>
    .st-key-workflow_cluster_v59 > div[data-testid="stVerticalBlock"] {
        gap: 10px !important;
        row-gap: 10px !important;
    }
    .st-key-workflow_cluster_v59 .selected-station-confirm {
        margin: 0 !important;
    }
    .st-key-workflow_cluster_v59 div[data-testid="stMarkdownContainer"]:has(.station-select-title-v50) {
        margin: 0 !important;
        padding: 0 !important;
    }
    .station-select-title-v50 {
        margin: 0 !important;
        padding: 0 !important;
        font-size: 28px !important;
        font-weight: 950 !important;
        line-height: 1.25 !important;
        color: #111 !important;
    }
    .station-select-title-v50 .select-title-green {
        color: #00a83b !important;
        font-weight: 950 !important;
    }
    .st-key-title_admin_v52,
    .st-key-title_admin_v52 > div {
        border: none !important;
        box-shadow: none !important;
        background: transparent !important;
    }
    .st-key-title_admin_v52 button {
        border: none !important;
        box-shadow: none !important;
        background-color: transparent !important;
        background-image: url('data:image/png;base64,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') !important;
        background-repeat: no-repeat !important;
        background-position: center center !important;
        background-size: contain !important;
        min-height: 38px !important;
        height: 38px !important;
        padding: 0 !important;
        margin: 0 !important;
    }
    .st-key-title_admin_v52 button p {
        font-size: 0 !important;
        line-height: 0 !important;
        color: transparent !important;
    }
    @media (max-width: 768px) {
        div[data-testid="stHorizontalBlock"]:has(.st-key-title_admin_v52) {
            grid-template-columns: minmax(0,1fr) 105px !important;
        }
        .st-key-title_admin_v52 button {
            min-height: 28px !important;
            height: 28px !important;
            background-image: url('data:image/png;base64,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') !important;
            background-size: contain !important;
        }
        .st-key-title_admin_v52 button p {font-size:0 !important; color:transparent !important;}
        .st-key-workflow_cluster_v59 > div[data-testid="stVerticalBlock"] {
            gap: 8px !important;
            row-gap: 8px !important;
        }
        .station-select-title-v50 {font-size: 22px !important;}
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# v5.15 최종 UI 오버라이드
# - 확인상자 아래 전체 폭 구분선
# - 구분선과 ① 본문 제목 사이 한 줄 여백
# - 투명 배경 터치 손가락 아이콘 축소
# - '동'/'투표소' 보라색 + 본문보다 2px 확대
# - 안내문과 선택박스 간격 축소
# - 상단 ①~④ 메뉴 글자 최대 확대
# - 선택 메뉴 빨간 테두리 강화
# ============================================================
st.markdown(
    r"""
    <style>
    /* 확인 상자 하단의 전체 폭 구분선 */
    div[data-testid="stMarkdownContainer"]:has(.station-section-divider-v515) {
        width:100% !important;
        margin:0 !important;
        padding:0 !important;
    }
    .station-section-divider-v515 {
        display:block !important;
        width:100% !important;
        height:0 !important;
        border-top:3px solid #111 !important;
        margin:2px 0 0 0 !important;
        padding:0 !important;
    }

    /* 구분선 다음 본문 제목은 한 줄 정도 띄움 */
    div[data-testid="stMarkdownContainer"]:has(.select-screen-heading-v514) {
        margin-top:16px !important;
        margin-bottom:0 !important;
        padding:0 !important;
    }

    /* 기존 짧은 제목선 제거 */
    .station-select-title-v50 {
        width:auto !important;
        border-top:none !important;
        margin:0 0 5px 0 !important;
        padding:0 !important;
    }

    /* 안내문: 작고 단순한 투명 배경 터치 아이콘 */
    .select-instruction-v514 {
        display:flex !important;
        align-items:center !important;
        gap:6px !important;
        min-height:0 !important;
        margin:0 !important;
        padding:0 4px 0 6px !important;
        color:#111 !important;
        font-size:18px !important;
        line-height:1.18 !important;
        font-weight:850 !important;
    }
    .tap-icon-v515 {
        display:inline-flex !important;
        align-items:center !important;
        justify-content:center !important;
        width:40px !important;
        height:40px !important;
        flex:0 0 40px !important;
        background:transparent !important;
    }
    .tap-icon-v515 svg {
        display:block !important;
        width:40px !important;
        height:40px !important;
        background:transparent !important;
    }
    .select-guide-text-v515 {
        display:inline-block !important;
        white-space:nowrap !important;
    }
    .select-keyword-v515 {
        color:#7b159d !important;
        font-size:20px !important; /* 본문보다 2px 크게 */
        font-weight:950 !important;
    }

    /* 안내문과 선택 네모상자 사이 간격 최소화 */
    .st-key-station_choice_input_box {
        margin-top:2px !important;
        padding-top:6px !important;
        padding-bottom:7px !important;
    }
    div[data-testid="stMarkdownContainer"]:has(.select-screen-heading-v514) + div {
        margin-top:0 !important;
        padding-top:0 !important;
    }

    /* 상단 메뉴: 가능한 범위에서 글자를 최대한 크게 */
    .st-key-workflow_cluster_v59 .st-key-navcard_select_v35 button::after,
    .st-key-workflow_cluster_v59 .st-key-navcard_report_v35 button::after,
    .st-key-workflow_cluster_v59 .st-key-navcard_input_v35 button::after,
    .st-key-workflow_cluster_v59 .st-key-navcard_reference_v35 button::after {
        font-size:18px !important;
        font-weight:950 !important;
        letter-spacing:-0.65px !important;
    }
    .st-key-workflow_cluster_v59 .st-key-navcard_select_v35 button p,
    .st-key-workflow_cluster_v59 .st-key-navcard_report_v35 button p,
    .st-key-workflow_cluster_v59 .st-key-navcard_input_v35 button p,
    .st-key-workflow_cluster_v59 .st-key-navcard_reference_v35 button p {
        font-size:19px !important;
        font-weight:950 !important;
        letter-spacing:-0.75px !important;
    }

    /* 선택된 메뉴 빨간 테두리 */
    .st-key-navcard_select_v35 button,
    .st-key-navcard_report_v35 button,
    .st-key-navcard_input_v35 button,
    .st-key-navcard_reference_v35 button {
        box-sizing:border-box !important;
    }

    @media (max-width:768px) {
        .station-section-divider-v515 {
            border-top-width:3px !important;
            margin-top:1px !important;
        }
        div[data-testid="stMarkdownContainer"]:has(.select-screen-heading-v514) {
            margin-top:14px !important;
        }
        .station-select-title-v50 {
            margin-bottom:4px !important;
        }
        .select-instruction-v514 {
            gap:5px !important;
            padding-left:5px !important;
            font-size:16px !important;
            line-height:1.15 !important;
        }
        .tap-icon-v515,
        .tap-icon-v515 svg {
            width:32px !important;
            height:32px !important;
        }
        .tap-icon-v515 {
            flex-basis:32px !important;
        }
        .select-keyword-v515 {
            font-size:18px !important; /* 모바일 본문보다 2px 크게 */
        }
        .st-key-station_choice_input_box {
            margin-top:0 !important;
            padding-top:3px !important;
        }

        /* 휴대전화 폭 내에서 잘리지 않는 최대 크기 */
        .st-key-workflow_cluster_v59 .st-key-navcard_select_v35 button::after,
        .st-key-workflow_cluster_v59 .st-key-navcard_report_v35 button::after,
        .st-key-workflow_cluster_v59 .st-key-navcard_input_v35 button::after,
        .st-key-workflow_cluster_v59 .st-key-navcard_reference_v35 button::after {
            font-size:13.5px !important;
            letter-spacing:-0.85px !important;
        }
        .st-key-workflow_cluster_v59 .st-key-navcard_select_v35 button p,
        .st-key-workflow_cluster_v59 .st-key-navcard_report_v35 button p,
        .st-key-workflow_cluster_v59 .st-key-navcard_input_v35 button p,
        .st-key-workflow_cluster_v59 .st-key-navcard_reference_v35 button p {
            font-size:14.5px !important;
            letter-spacing:-1px !important;
        }
        .st-key-workflow_cluster_v59 .st-key-navcard_select_v35 button::after {
            font-size:14.2px !important;
        }
        .st-key-workflow_cluster_v59 .st-key-navcard_select_v35 button p {
            font-size:15.2px !important;
        }
    }

    @media (max-width:390px) {
        .st-key-workflow_cluster_v59 .st-key-navcard_select_v35 button::after,
        .st-key-workflow_cluster_v59 .st-key-navcard_report_v35 button::after,
        .st-key-workflow_cluster_v59 .st-key-navcard_input_v35 button::after,
        .st-key-workflow_cluster_v59 .st-key-navcard_reference_v35 button::after {
            font-size:11.3px !important;
            letter-spacing:-0.95px !important;
        }
        .st-key-workflow_cluster_v59 .st-key-navcard_select_v35 button p,
        .st-key-workflow_cluster_v59 .st-key-navcard_report_v35 button p,
        .st-key-workflow_cluster_v59 .st-key-navcard_input_v35 button p,
        .st-key-workflow_cluster_v59 .st-key-navcard_reference_v35 button p {
            font-size:12.2px !important;
            letter-spacing:-1px !important;
        }
        .st-key-workflow_cluster_v59 .st-key-navcard_select_v35 button::after {font-size:12px !important;}
        .st-key-workflow_cluster_v59 .st-key-navcard_select_v35 button p {font-size:13px !important;}
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# v5.16 최종 간격/강조 보정
# ============================================================
st.markdown(
    r"""
    <style>
    /* 구분선과 ① 본문 제목 사이 여백을 조금 더 확보 */
    div[data-testid="stMarkdownContainer"]:has(.select-screen-heading-v514) {
        margin-top: 22px !important;
    }

    /* 손가락 터치 아이콘은 글자와 균형이 맞도록 약간 확대 */
    .tap-icon-v515 {
        width: 36px !important;
        height: 36px !important;
        flex-basis: 36px !important;
    }
    .tap-icon-v515 svg {
        width: 36px !important;
        height: 36px !important;
    }

    /* 안내문과 선택 네모상자 사이 큰 공백 제거 */
    div[data-testid="stMarkdownContainer"]:has(.select-screen-heading-v514) {
        margin-bottom: 0 !important;
        padding-bottom: 0 !important;
    }
    .select-instruction-v514 {
        margin-bottom: -2px !important;
        padding-bottom: 0 !important;
    }
    .st-key-station_choice_input_box {
        margin-top: 0 !important;
        padding-top: 1px !important;
    }

    /* 선택된 상단 메뉴 빨간 테두리를 한 단계 더 강조 */
    .st-key-navcard_select_v35 button,
    .st-key-navcard_report_v35 button,
    .st-key-navcard_input_v35 button,
    .st-key-navcard_reference_v35 button {
        transition: none !important;
    }

    @media (max-width:768px) {
        div[data-testid="stMarkdownContainer"]:has(.select-screen-heading-v514) {
            margin-top: 18px !important;
        }
        .tap-icon-v515,
        .tap-icon-v515 svg {
            width: 34px !important;
            height: 34px !important;
        }
        .tap-icon-v515 {
            flex-basis: 34px !important;
        }
        .st-key-station_choice_input_box {
            padding-top: 0 !important;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# v5.17 ① 선택화면 큰 공백 제거
# ============================================================
st.markdown(
    r"""
    <style>
    /* ① 선택화면의 안내문/입력영역 주변 Streamlit wrapper 간격 강제 축소 */
    div[data-testid="stMarkdownContainer"]:has(.select-screen-heading-v514) {
        margin-bottom: 0 !important;
        padding-bottom: 0 !important;
    }

    div[data-testid="stMarkdownContainer"]:has(.select-screen-heading-v514)
    + div[data-testid="stElementContainer"] {
        margin-top: 0 !important;
        padding-top: 0 !important;
        min-height: 0 !important;
    }

    .st-key-station_choice_input_box {
        margin-top: -8px !important;
        padding-top: 0 !important;
    }

    .st-key-station_choice_input_box > div {
        margin-top: 0 !important;
        padding-top: 0 !important;
    }

    .st-key-station_choice_input_box div[data-testid="stHorizontalBlock"] {
        margin-top: 0 !important;
        padding-top: 0 !important;
        gap: 0.45rem !important;
    }

    .select-instruction-v514 {
        margin-bottom: 0 !important;
        padding-bottom: 0 !important;
    }

    /* 불필요한 빈 블록이 끼는 Streamlit 버전 대응 */
    div[data-testid="stVerticalBlock"]:has(.select-screen-heading-v514) {
        gap: 0.15rem !important;
    }

    @media (max-width:768px) {
        .st-key-station_choice_input_box {
            margin-top: -12px !important;
        }
        div[data-testid="stVerticalBlock"]:has(.select-screen-heading-v514) {
            gap: 0.05rem !important;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# v5.18 최종 상단 메뉴/진행방향/간격 보정
# ============================================================
st.markdown(
    r"""
    <style>
    /* 기존 사이 화살표 완전 제거 */
    .nav-arrow-v35, .workflow-arrow, [class*="nav-arrow"] {
        display:none !important;
    }

    /* 4개 메뉴를 화면 폭에 균등하게 배치 */
    .st-key-workflow_cluster_v59 div[data-testid="stHorizontalBlock"]:has(.st-key-navcard_select_v35) {
        display:grid !important;
        grid-template-columns:repeat(4, minmax(0, 1fr)) !important;
        gap:6px !important;
        width:100% !important;
        margin:0 !important;
        padding:0 !important;
        align-items:stretch !important;
    }
    .st-key-workflow_cluster_v59 div[data-testid="stHorizontalBlock"]:has(.st-key-navcard_select_v35) > div[data-testid="stColumn"] {
        width:auto !important;
        min-width:0 !important;
        flex:none !important;
        padding:0 !important;
    }

    /* 메뉴 박스 높이와 글자 확대 */
    .st-key-workflow_cluster_v59 .st-key-navcard_select_v35 button,
    .st-key-workflow_cluster_v59 .st-key-navcard_report_v35 button,
    .st-key-workflow_cluster_v59 .st-key-navcard_input_v35 button,
    .st-key-workflow_cluster_v59 .st-key-navcard_reference_v35 button {
        width:100% !important;
        min-height:74px !important;
        padding:7px 4px !important;
        border-radius:8px !important;
    }
    .st-key-workflow_cluster_v59 .st-key-navcard_select_v35 button::after,
    .st-key-workflow_cluster_v59 .st-key-navcard_report_v35 button::after,
    .st-key-workflow_cluster_v59 .st-key-navcard_input_v35 button::after,
    .st-key-workflow_cluster_v59 .st-key-navcard_reference_v35 button::after {
        font-size:17px !important;
        font-weight:950 !important;
        letter-spacing:-0.8px !important;
        white-space:nowrap !important;
    }
    .st-key-workflow_cluster_v59 .st-key-navcard_select_v35 button p,
    .st-key-workflow_cluster_v59 .st-key-navcard_report_v35 button p,
    .st-key-workflow_cluster_v59 .st-key-navcard_input_v35 button p,
    .st-key-workflow_cluster_v59 .st-key-navcard_reference_v35 button p {
        font-size:18px !important;
        font-weight:950 !important;
        letter-spacing:-0.9px !important;
        white-space:nowrap !important;
    }

    /* 선택된 메뉴 빨간 테두리 강화 */
    .st-key-workflow_cluster_v59 .st-key-navcard_select_v35 button,
    .st-key-workflow_cluster_v59 .st-key-navcard_report_v35 button,
    .st-key-workflow_cluster_v59 .st-key-navcard_input_v35 button,
    .st-key-workflow_cluster_v59 .st-key-navcard_reference_v35 button {
        box-sizing:border-box !important;
    }

    /* 메뉴 아래 긴 검정 진행 화살표 */
    .workflow-progress-arrow-v518 {
        position:relative !important;
        width:100% !important;
        height:20px !important;
        margin:5px 0 11px 0 !important;
    }
    .workflow-progress-arrow-v518::before {
        content:"" !important;
        position:absolute !important;
        left:1.5% !important;
        right:4.5% !important;
        top:8px !important;
        height:4px !important;
        background:#111 !important;
        border-radius:4px !important;
    }
    .workflow-progress-arrow-v518::after {
        content:"" !important;
        position:absolute !important;
        right:1.5% !important;
        top:1px !important;
        width:14px !important;
        height:14px !important;
        border-top:4px solid #111 !important;
        border-right:4px solid #111 !important;
        transform:rotate(45deg) !important;
    }

    /* 기존 확인상자 아래 검정 실선 제거 */
    .station-section-divider-v515 {
        display:none !important;
        border:none !important;
        height:0 !important;
        margin:0 !important;
    }

    /* 선택한 투표소 확인상자와 [선택] 투표소 사이 간격 확대 */
    div[data-testid="stMarkdownContainer"]:has(.select-screen-heading-v514) {
        margin-top:30px !important;
    }

    /* 손가락 아이콘: 검지가 분명하게 보이도록 적정 크기 */
    .tap-icon-v515,
    .tap-icon-v515 svg {
        width:40px !important;
        height:40px !important;
    }
    .tap-icon-v515 {
        flex-basis:40px !important;
    }

    @media (max-width:768px) {
        .st-key-workflow_cluster_v59 div[data-testid="stHorizontalBlock"]:has(.st-key-navcard_select_v35) {
            gap:5px !important;
        }

        .st-key-workflow_cluster_v59 .st-key-navcard_select_v35 button,
        .st-key-workflow_cluster_v59 .st-key-navcard_report_v35 button,
        .st-key-workflow_cluster_v59 .st-key-navcard_input_v35 button,
        .st-key-workflow_cluster_v59 .st-key-navcard_reference_v35 button {
            min-height:68px !important;
            padding:5px 2px !important;
        }

        .st-key-workflow_cluster_v59 .st-key-navcard_select_v35 button::after,
        .st-key-workflow_cluster_v59 .st-key-navcard_report_v35 button::after,
        .st-key-workflow_cluster_v59 .st-key-navcard_input_v35 button::after,
        .st-key-workflow_cluster_v59 .st-key-navcard_reference_v35 button::after {
            font-size:13px !important;
            letter-spacing:-0.9px !important;
        }

        .st-key-workflow_cluster_v59 .st-key-navcard_select_v35 button p,
        .st-key-workflow_cluster_v59 .st-key-navcard_report_v35 button p,
        .st-key-workflow_cluster_v59 .st-key-navcard_input_v35 button p,
        .st-key-workflow_cluster_v59 .st-key-navcard_reference_v35 button p {
            font-size:14px !important;
            letter-spacing:-1px !important;
        }

        .workflow-progress-arrow-v518 {
            height:16px !important;
            margin:4px 0 9px 0 !important;
        }
        .workflow-progress-arrow-v518::before {
            top:6px !important;
            height:3px !important;
        }
        .workflow-progress-arrow-v518::after {
            top:0 !important;
            width:11px !important;
            height:11px !important;
            border-top-width:3px !important;
            border-right-width:3px !important;
        }

        div[data-testid="stMarkdownContainer"]:has(.select-screen-heading-v514) {
            margin-top:26px !important;
        }

        .tap-icon-v515,
        .tap-icon-v515 svg {
            width:38px !important;
            height:38px !important;
        }
        .tap-icon-v515 {
            flex-basis:38px !important;
        }
    }

    @media (max-width:390px) {
        .st-key-workflow_cluster_v59 .st-key-navcard_select_v35 button::after,
        .st-key-workflow_cluster_v59 .st-key-navcard_report_v35 button::after,
        .st-key-workflow_cluster_v59 .st-key-navcard_input_v35 button::after,
        .st-key-workflow_cluster_v59 .st-key-navcard_reference_v35 button::after {
            font-size:11.2px !important;
        }
        .st-key-workflow_cluster_v59 .st-key-navcard_select_v35 button p,
        .st-key-workflow_cluster_v59 .st-key-navcard_report_v35 button p,
        .st-key-workflow_cluster_v59 .st-key-navcard_input_v35 button p,
        .st-key-workflow_cluster_v59 .st-key-navcard_reference_v35 button p {
            font-size:12px !important;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# v5.19 선택 라벨-콤보박스 간격 보정
# ============================================================
st.markdown(
    r"""
    <style>
    /* 동 선택 / 투표소 선택 라벨과 실제 콤보박스 사이 간격 확대 */
    .st-key-station_choice_input_box div[data-testid="stSelectbox"] > label {
        display:block !important;
        margin-bottom: 8px !important;
        padding-bottom: 0 !important;
    }

    .st-key-station_choice_input_box div[data-testid="stSelectbox"] > div {
        margin-top: 0 !important;
    }

    /* 두 콤보박스가 들어 있는 보라색 박스 내부 여백도 약간 정돈 */
    .st-key-station_choice_input_box {
        padding-top: 9px !important;
        padding-bottom: 9px !important;
    }

    @media (max-width:768px) {
        .st-key-station_choice_input_box div[data-testid="stSelectbox"] > label {
            margin-bottom: 7px !important;
        }
        .st-key-station_choice_input_box {
            padding-top: 8px !important;
            padding-bottom: 8px !important;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# v5.20 상단 간격 + 진행화살표 + 선택라벨 정리
# ============================================================
st.markdown(
    r"""
    <style>
    /* 1) 앱 제목과 '★ 반드시~바랍니다. ★' 사이 간격 확대 */
    .app-title-row-v31 {
        margin-bottom: 14px !important;
    }
    .workflow-guide {
        margin-top: 10px !important;
        margin-bottom: 18px !important;
    }

    /* 2) '★ 반드시~바랍니다. ★'와 메뉴 네모상자 사이 간격 확대 */
    .st-key-workflow_cluster_v59 {
        margin-top: 12px !important;
    }

    /* 3) 메뉴 아래 긴 검정 화살표: 끝부분을 단순 삼각 화살촉으로 안정화 */
    .workflow-progress-arrow-v518 {
        position: relative !important;
        width: 100% !important;
        height: 22px !important;
        margin: 8px 0 18px 0 !important; /* 아래 확인상자와 간격 확대 */
        overflow: visible !important;
    }
    .workflow-progress-arrow-v518::before {
        content: "" !important;
        position: absolute !important;
        left: 1.5% !important;
        right: 5.2% !important;
        top: 9px !important;
        height: 4px !important;
        background: #111 !important;
        border-radius: 3px !important;
    }
    .workflow-progress-arrow-v518::after {
        content: "" !important;
        position: absolute !important;
        right: 1.3% !important;
        top: 2px !important;
        width: 0 !important;
        height: 0 !important;
        border-top: 9px solid transparent !important;
        border-bottom: 9px solid transparent !important;
        border-left: 16px solid #111 !important;
        transform: none !important;
    }

    /* 4) 진행 화살표와 '선택한 투표소는~입니다.' 네모상자 사이 간격 */
    div[data-testid="stMarkdownContainer"]:has(.shared-station-confirm) {
        margin-top: 6px !important;
    }

    /* 5) 확인상자와 ①[선택] 투표소 사이 간격을 조금 더 확대 */
    div[data-testid="stMarkdownContainer"]:has(.select-screen-heading-v514) {
        margin-top: 34px !important;
    }

    /* 6) ★동 선택 / ★투표소 선택 아래 중복 라벨 숨김
          (라벨 자체는 유지하되 내부 중복 텍스트만 숨기고 콤보박스 간격 확보) */
    .st-key-station_choice_input_box div[data-testid="stSelectbox"] > label {
        margin-bottom: 10px !important;
    }
    .st-key-station_choice_input_box div[data-testid="stSelectbox"] > label div[data-testid="stMarkdownContainer"] p {
        font-size: 0 !important;
        line-height: 0 !important;
        height: 0 !important;
        overflow: hidden !important;
        margin: 0 !important;
        padding: 0 !important;
    }
    .st-key-station_choice_input_box div[data-testid="stSelectbox"] > label div[data-testid="stMarkdownContainer"] p::before {
        content: "" !important;
    }

    @media (max-width:768px) {
        .app-title-row-v31 {
            margin-bottom: 12px !important;
        }
        .workflow-guide {
            margin-top: 8px !important;
            margin-bottom: 15px !important;
        }
        .st-key-workflow_cluster_v59 {
            margin-top: 10px !important;
        }
        .workflow-progress-arrow-v518 {
            height: 19px !important;
            margin-top: 7px !important;
            margin-bottom: 16px !important;
        }
        .workflow-progress-arrow-v518::before {
            top: 8px !important;
            height: 3px !important;
            right: 5.5% !important;
        }
        .workflow-progress-arrow-v518::after {
            top: 2px !important;
            right: 1.2% !important;
            border-top-width: 7px !important;
            border-bottom-width: 7px !important;
            border-left-width: 13px !important;
        }
        div[data-testid="stMarkdownContainer"]:has(.select-screen-heading-v514) {
            margin-top: 30px !important;
        }
        .st-key-station_choice_input_box div[data-testid="stSelectbox"] > label {
            margin-bottom: 9px !important;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# v5.21 선택화면 세부 간격 보정
# ============================================================
st.markdown(
    r"""
    <style>
    /* 1) '선택한 투표소는~입니다.' 상자와 ①[선택] 투표소 사이를 약 10px 더 넓힘 */
    div[data-testid="stMarkdownContainer"]:has(.select-screen-heading-v514) {
        margin-top: 40px !important;
    }

    /* 2) '해당 동과 투표소를 선택하세요!'와 아래 보라색 선택상자 사이 간격 축소 */
    .select-instruction-v514 {
        margin-bottom: -6px !important;
    }
    .st-key-station_choice_input_box {
        margin-top: -5px !important;
        padding-top: 6px !important;
    }

    /* 3) 보라색 상자 안의 제목은 '동 선택' / '투표소 선택' 형태로 표시 */
    .st-key-station_choice_input_box div[data-testid="stSelectbox"] > label {
        margin-bottom: 4px !important;
        padding-bottom: 0 !important;
    }

    /* label 내부 실제 문구를 다시 표시하되 원하는 형식으로 재구성 */
    .st-key-station_choice_input_box div[data-testid="stSelectbox"]:nth-of-type(1) > label div[data-testid="stMarkdownContainer"] p,
    .st-key-station_choice_input_box div[data-testid="stSelectbox"]:nth-of-type(2) > label div[data-testid="stMarkdownContainer"] p {
        font-size: 0 !important;
        line-height: 1 !important;
        height: auto !important;
        overflow: visible !important;
        margin: 0 !important;
        padding: 0 !important;
    }
    .st-key-station_choice_input_box div[data-testid="stSelectbox"]:nth-of-type(1) > label div[data-testid="stMarkdownContainer"] p::before {
        content: "★ 동 선택" !important;
        color: #7b159d !important;
        font-size: 18px !important;
        font-weight: 900 !important;
        line-height: 1.1 !important;
    }
    .st-key-station_choice_input_box div[data-testid="stSelectbox"]:nth-of-type(2) > label div[data-testid="stMarkdownContainer"] p::before {
        content: "★ 투표소 선택" !important;
        color: #7b159d !important;
        font-size: 18px !important;
        font-weight: 900 !important;
        line-height: 1.1 !important;
    }

    /* 4) 제목과 콤보박스 사이 간격 축소 */
    .st-key-station_choice_input_box div[data-testid="stSelectbox"] > div {
        margin-top: 0 !important;
    }

    @media (max-width:768px) {
        div[data-testid="stMarkdownContainer"]:has(.select-screen-heading-v514) {
            margin-top: 36px !important;
        }

        .select-instruction-v514 {
            margin-bottom: -7px !important;
        }

        .st-key-station_choice_input_box {
            margin-top: -6px !important;
            padding-top: 5px !important;
        }

        .st-key-station_choice_input_box div[data-testid="stSelectbox"] > label {
            margin-bottom: 3px !important;
        }

        .st-key-station_choice_input_box div[data-testid="stSelectbox"]:nth-of-type(1) > label div[data-testid="stMarkdownContainer"] p::before,
        .st-key-station_choice_input_box div[data-testid="stSelectbox"]:nth-of-type(2) > label div[data-testid="stMarkdownContainer"] p::before {
            font-size: 16px !important;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# v5.24 최종 오버라이드
# - 메뉴 글자 확대
# - 선택 표시: 파란 밑줄 + 기존 빨간 테두리
# - 선택 투표소 앞 체크박스
# - 확인상자와 [선택] 투표소 사이 한 줄 더 띄움
# - 중복 선택라벨 제거
# - 콤보 '여기서' 제거
# - 손가락 아이콘 가시성 개선
# - 라벨/콤보 간격 축소
# ============================================================
st.markdown(
    r"""
    <style>
    /* ---------- 상단 메뉴 글자: 화면 폭 안에서 최대 확대 ---------- */
    .st-key-workflow_cluster_v59 .st-key-navcard_select_v35 button::after,
    .st-key-workflow_cluster_v59 .st-key-navcard_report_v35 button::after,
    .st-key-workflow_cluster_v59 .st-key-navcard_input_v35 button::after,
    .st-key-workflow_cluster_v59 .st-key-navcard_reference_v35 button::after {
        font-size:18px !important;
        font-weight:950 !important;
        letter-spacing:-0.8px !important;
        white-space:nowrap !important;
    }

    .st-key-workflow_cluster_v59 .st-key-navcard_select_v35 button p,
    .st-key-workflow_cluster_v59 .st-key-navcard_report_v35 button p,
    .st-key-workflow_cluster_v59 .st-key-navcard_input_v35 button p,
    .st-key-workflow_cluster_v59 .st-key-navcard_reference_v35 button p {
        font-size:19px !important;
        font-weight:950 !important;
        letter-spacing:-0.9px !important;
        white-space:nowrap !important;
        line-height:1.05 !important;
    }

    /* 선택된 카드의 기존 점은 완전히 숨기고 파란 밑줄만 사용 */
    .st-key-navcard_select_v35 button::before,
    .st-key-navcard_report_v35 button::before,
    .st-key-navcard_input_v35 button::before,
    .st-key-navcard_reference_v35 button::before {
        opacity:0 !important;
    }

    /* ---------- 선택한 투표소 확인상자 앞 체크박스 ---------- */
    .confirm-check-v524 {
        display:inline-flex !important;
        align-items:center !important;
        justify-content:center !important;
        width:27px !important;
        min-width:27px !important;
        height:27px !important;
        margin-right:10px !important;
        color:#7b159d !important;
        font-size:26px !important;
        line-height:1 !important;
        font-weight:950 !important;
        vertical-align:middle !important;
    }

    /* 확인상자와 ①[선택] 투표소 사이: 기존보다 한 줄 더 */
    div[data-testid="stMarkdownContainer"]:has(.select-screen-heading-v514) {
        margin-top:52px !important;
    }

    /* ---------- 손가락 터치 아이콘 가시성 ---------- */
    .tap-icon-v515 {
        display:inline-flex !important;
        visibility:visible !important;
        opacity:1 !important;
        width:44px !important;
        height:44px !important;
        flex:0 0 44px !important;
        overflow:visible !important;
        align-items:center !important;
        justify-content:center !important;
    }
    .tap-icon-v515 svg {
        display:block !important;
        visibility:visible !important;
        opacity:1 !important;
        width:44px !important;
        height:44px !important;
        overflow:visible !important;
    }

    /* 안내문과 보라색 선택 박스는 가깝게 */
    .select-instruction-v514 {
        margin-bottom:-8px !important;
        padding-bottom:0 !important;
    }
    .st-key-station_choice_input_box {
        margin-top:-5px !important;
        padding-top:6px !important;
        padding-bottom:8px !important;
    }

    /* ---------- 보라색 박스 안 라벨은 기존 HTML 1개만 표시 ---------- */
    .station-choice-label {
        display:block !important;
        color:#7b159d !important;
        font-size:18px !important;
        font-weight:950 !important;
        line-height:1.05 !important;
        margin:0 0 3px 0 !important;
        padding:0 !important;
    }
    .station-choice-label .star {
        margin-right:1px !important;
    }

    /* selectbox 자체 Streamlit label은 완전히 숨김 */
    .st-key-station_choice_input_box div[data-testid="stSelectbox"] > label {
        display:none !important;
        height:0 !important;
        min-height:0 !important;
        margin:0 !important;
        padding:0 !important;
        overflow:hidden !important;
    }
    .st-key-station_choice_input_box div[data-testid="stSelectbox"] > label * {
        display:none !important;
    }

    /* 이전 v5.21에서 넣은 pseudo label 무효화 */
    .st-key-station_choice_input_box div[data-testid="stSelectbox"] > label p::before,
    .st-key-station_choice_input_box div[data-testid="stSelectbox"] > label p::after {
        content:"" !important;
        display:none !important;
    }

    /* 라벨과 콤보박스 사이 간격 최소화 */
    .st-key-station_choice_input_box div[data-testid="stSelectbox"] {
        margin-top:0 !important;
        padding-top:0 !important;
    }
    .st-key-station_choice_input_box div[data-baseweb="select"] {
        margin-top:0 !important;
    }

    @media (max-width:768px) {
        /* 실제 모바일 폭에서 가능한 최대 크기 */
        .st-key-workflow_cluster_v59 .st-key-navcard_select_v35 button::after,
        .st-key-workflow_cluster_v59 .st-key-navcard_report_v35 button::after,
        .st-key-workflow_cluster_v59 .st-key-navcard_input_v35 button::after,
        .st-key-workflow_cluster_v59 .st-key-navcard_reference_v35 button::after {
            font-size:13.2px !important;
            letter-spacing:-1px !important;
        }

        .st-key-workflow_cluster_v59 .st-key-navcard_select_v35 button p,
        .st-key-workflow_cluster_v59 .st-key-navcard_report_v35 button p,
        .st-key-workflow_cluster_v59 .st-key-navcard_input_v35 button p,
        .st-key-workflow_cluster_v59 .st-key-navcard_reference_v35 button p {
            font-size:14.5px !important;
            letter-spacing:-1.1px !important;
        }

        .confirm-check-v524 {
            width:23px !important;
            min-width:23px !important;
            height:23px !important;
            font-size:22px !important;
            margin-right:7px !important;
        }

        div[data-testid="stMarkdownContainer"]:has(.select-screen-heading-v514) {
            margin-top:48px !important;
        }

        .tap-icon-v515,
        .tap-icon-v515 svg {
            width:40px !important;
            height:40px !important;
        }
        .tap-icon-v515 {
            flex-basis:40px !important;
        }

        .station-choice-label {
            font-size:15.5px !important;
            margin-bottom:2px !important;
        }
    }

    @media (max-width:390px) {
        .st-key-workflow_cluster_v59 .st-key-navcard_select_v35 button::after,
        .st-key-workflow_cluster_v59 .st-key-navcard_report_v35 button::after,
        .st-key-workflow_cluster_v59 .st-key-navcard_input_v35 button::after,
        .st-key-workflow_cluster_v59 .st-key-navcard_reference_v35 button::after {
            font-size:12px !important;
            letter-spacing:-1.1px !important;
        }

        .st-key-workflow_cluster_v59 .st-key-navcard_select_v35 button p,
        .st-key-workflow_cluster_v59 .st-key-navcard_report_v35 button p,
        .st-key-workflow_cluster_v59 .st-key-navcard_input_v35 button p,
        .st-key-workflow_cluster_v59 .st-key-navcard_reference_v35 button p {
            font-size:13.3px !important;
            letter-spacing:-1.15px !important;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# v5.25 상단 메뉴 중앙정렬 + 선택영역 라벨 간격 보정
# ============================================================
st.markdown(
    r"""
    <style>
    /* 상단 4개 메뉴 카드 내부 전체 중앙정렬 */
    .st-key-workflow_cluster_v59 .st-key-navcard_select_v35 button,
    .st-key-workflow_cluster_v59 .st-key-navcard_report_v35 button,
    .st-key-workflow_cluster_v59 .st-key-navcard_input_v35 button,
    .st-key-workflow_cluster_v59 .st-key-navcard_reference_v35 button {
        display:flex !important;
        flex-direction:column !important;
        align-items:center !important;
        justify-content:center !important;
        text-align:center !important;
    }

    .st-key-workflow_cluster_v59 .st-key-navcard_select_v35 button p,
    .st-key-workflow_cluster_v59 .st-key-navcard_report_v35 button p,
    .st-key-workflow_cluster_v59 .st-key-navcard_input_v35 button p,
    .st-key-workflow_cluster_v59 .st-key-navcard_reference_v35 button p {
        width:100% !important;
        margin-left:auto !important;
        margin-right:auto !important;
        text-align:center !important;
        justify-content:center !important;
    }

    .st-key-workflow_cluster_v59 .st-key-navcard_select_v35 button::after,
    .st-key-workflow_cluster_v59 .st-key-navcard_report_v35 button::after,
    .st-key-workflow_cluster_v59 .st-key-navcard_input_v35 button::after,
    .st-key-workflow_cluster_v59 .st-key-navcard_reference_v35 button::after {
        display:block !important;
        width:100% !important;
        text-align:center !important;
        margin-left:auto !important;
        margin-right:auto !important;
    }

    /* 선택 메뉴의 파란 밑줄도 가운데 정렬 */
    .st-key-workflow_cluster_v59 .st-key-navcard_select_v35 button p,
    .st-key-workflow_cluster_v59 .st-key-navcard_report_v35 button p,
    .st-key-workflow_cluster_v59 .st-key-navcard_input_v35 button p,
    .st-key-workflow_cluster_v59 .st-key-navcard_reference_v35 button p {
        box-sizing:border-box !important;
    }

    /* 동 선택 / 투표소 선택 라벨이 잘리지 않도록 라인 높이 및 아래 간격 확보 */
    .station-choice-label {
        line-height:1.25 !important;
        min-height:1.35em !important;
        overflow:visible !important;
        margin-bottom:7px !important;
        padding-top:1px !important;
        padding-bottom:1px !important;
    }

    /* 라벨과 회색 콤보박스 사이 간격 */
    .st-key-station_choice_input_box div[data-baseweb="select"] {
        margin-top:0 !important;
    }

    @media (max-width:768px) {
        .station-choice-label {
            line-height:1.25 !important;
            min-height:1.3em !important;
            margin-bottom:6px !important;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# v5.26 누적 수정 최종 반영
# - 상단 메뉴 실제 중앙정렬
# - 선택 확인상자와 ①[선택] 투표소 사이 고정 1줄 여백
# - 손가락 아이콘 가시성 개선
# - 안내문과 보라색 선택상자 사이 2px
# ============================================================
st.markdown(
    r"""
    <style>
    /* 상단 4개 메뉴: 가상요소 포함 완전 중앙정렬 */
    .st-key-workflow_cluster_v59 .st-key-navcard_select_v35 button,
    .st-key-workflow_cluster_v59 .st-key-navcard_report_v35 button,
    .st-key-workflow_cluster_v59 .st-key-navcard_input_v35 button,
    .st-key-workflow_cluster_v59 .st-key-navcard_reference_v35 button {
        position: relative !important;
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
        justify-content: center !important;
        text-align: center !important;
        padding-left: 4px !important;
        padding-right: 4px !important;
    }

    .st-key-workflow_cluster_v59 .st-key-navcard_select_v35 button p,
    .st-key-workflow_cluster_v59 .st-key-navcard_report_v35 button p,
    .st-key-workflow_cluster_v59 .st-key-navcard_input_v35 button p,
    .st-key-workflow_cluster_v59 .st-key-navcard_reference_v35 button p {
        display: block !important;
        width: auto !important;
        max-width: 96% !important;
        margin-left: auto !important;
        margin-right: auto !important;
        text-align: center !important;
        position: static !important;
        left: auto !important;
        right: auto !important;
        transform: none !important;
    }

    .st-key-workflow_cluster_v59 .st-key-navcard_select_v35 button::after,
    .st-key-workflow_cluster_v59 .st-key-navcard_report_v35 button::after,
    .st-key-workflow_cluster_v59 .st-key-navcard_input_v35 button::after,
    .st-key-workflow_cluster_v59 .st-key-navcard_reference_v35 button::after {
        display: block !important;
        position: static !important;
        width: auto !important;
        max-width: 96% !important;
        margin-left: auto !important;
        margin-right: auto !important;
        text-align: center !important;
        left: auto !important;
        right: auto !important;
        transform: none !important;
    }

    /* 선택한 투표소 확인상자 다음 실제 고정 1줄 여백 */
    .after-confirm-spacer-v526 {
        display: block !important;
        width: 100% !important;
        height: 24px !important;
        margin: 0 !important;
        padding: 0 !important;
    }
    div[data-testid="stMarkdownContainer"]:has(.select-screen-heading-v514) {
        margin-top: 0 !important;
    }

    /* 손가락 아이콘을 더 단순하고 크게 보이도록 */
    .tap-icon-v515 {
        display: inline-flex !important;
        width: 44px !important;
        height: 44px !important;
        flex: 0 0 44px !important;
        overflow: visible !important;
        margin-right: 2px !important;
    }
    .tap-icon-v515 svg {
        width: 44px !important;
        height: 44px !important;
        overflow: visible !important;
        transform: scale(1.08) !important;
        transform-origin: center !important;
    }

    /* 안내문과 보라색 선택상자 사이 여백 정확히 2px */
    .select-instruction-v514 {
        margin-bottom: 0 !important;
        padding-bottom: 0 !important;
    }
    .st-key-station_choice_input_box {
        margin-top: 2px !important;
        padding-top: 6px !important;
    }

    /* 라벨과 회색 콤보박스 사이 간격은 글자 잘림 없이 적당히 */
    .station-choice-label {
        line-height: 1.25 !important;
        min-height: 1.3em !important;
        overflow: visible !important;
        margin-bottom: 6px !important;
        padding-top: 1px !important;
        padding-bottom: 1px !important;
    }

    @media (max-width: 768px) {
        .after-confirm-spacer-v526 {
            height: 22px !important;
        }

        .tap-icon-v515,
        .tap-icon-v515 svg {
            width: 40px !important;
            height: 40px !important;
        }
        .tap-icon-v515 {
            flex-basis: 40px !important;
        }

        .st-key-station_choice_input_box {
            margin-top: 2px !important;
        }

        .station-choice-label {
            margin-bottom: 5px !important;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# v5.27 다섯 항목 통합 수정
# ① 상단 메뉴: 초록 단계명 위 / 검정 메뉴명 아래 / 정확한 중앙정렬
# ② 진행 화살표: 정상적인 검정 선 + 삼각 화살촉
# ③ 확인상자 ↔ ①[선택] 투표소: 정확히 10px
# ④ 안내문 ↔ 보라색 선택상자: 정확히 2px
# ⑤ 손가락: 검지가 확실히 보이는 ☝️ 아이콘
# ============================================================
st.markdown(
    r"""
    <style>
    /* ---------- ① 상단 메뉴 ---------- */
    .st-key-workflow_cluster_v59 .st-key-navcard_select_v35 button,
    .st-key-workflow_cluster_v59 .st-key-navcard_report_v35 button,
    .st-key-workflow_cluster_v59 .st-key-navcard_input_v35 button,
    .st-key-workflow_cluster_v59 .st-key-navcard_reference_v35 button {
        display:flex !important;
        flex-direction:column !important;
        align-items:center !important;
        justify-content:center !important;
        text-align:center !important;
        padding-left:3px !important;
        padding-right:3px !important;
    }

    /* 초록 단계명(::after)을 반드시 위쪽 */
    .st-key-workflow_cluster_v59 .st-key-navcard_select_v35 button::after,
    .st-key-workflow_cluster_v59 .st-key-navcard_report_v35 button::after,
    .st-key-workflow_cluster_v59 .st-key-navcard_input_v35 button::after,
    .st-key-workflow_cluster_v59 .st-key-navcard_reference_v35 button::after {
        order:-1 !important;
        display:block !important;
        position:static !important;
        width:100% !important;
        margin:0 auto 7px auto !important;
        text-align:center !important;
        left:auto !important;
        right:auto !important;
        transform:none !important;
    }

    /* 검정 메뉴명(p)을 반드시 아래쪽 */
    .st-key-workflow_cluster_v59 .st-key-navcard_select_v35 button p,
    .st-key-workflow_cluster_v59 .st-key-navcard_report_v35 button p,
    .st-key-workflow_cluster_v59 .st-key-navcard_input_v35 button p,
    .st-key-workflow_cluster_v59 .st-key-navcard_reference_v35 button p {
        order:1 !important;
        display:block !important;
        position:static !important;
        width:max-content !important;
        max-width:96% !important;
        margin:0 auto !important;
        text-align:center !important;
        left:auto !important;
        right:auto !important;
        transform:none !important;
    }

    /* 선택된 메뉴의 파란 밑줄은 검정 글자 바로 아래 중앙 */
    .st-key-workflow_cluster_v59 [class*="st-key-navcard_"] button p {
        padding-left:0 !important;
        padding-right:0 !important;
    }

    /* ---------- ② 진행 화살표 ---------- */
    .workflow-progress-arrow-v518 {
        display:none !important;
    }
    .workflow-progress-arrow-v527 {
        display:block !important;
        width:100% !important;
        height:20px !important;
        margin:7px 0 10px 0 !important;
        padding:0 !important;
        overflow:visible !important;
    }
    .workflow-progress-arrow-v527 svg {
        display:block !important;
        width:100% !important;
        height:20px !important;
        overflow:visible !important;
    }

    /* ---------- ③ 확인상자와 선택 본문 사이 정확히 10px ---------- */
    .after-confirm-spacer-v526 {
        display:none !important;
        height:0 !important;
        margin:0 !important;
        padding:0 !important;
    }
    .st-key-selection_body_v527 {
        margin-top:10px !important;
        padding-top:0 !important;
    }
    .st-key-selection_body_v527 > div[data-testid="stVerticalBlock"] {
        gap:2px !important;
    }
    .select-screen-heading-v527 {
        margin:0 !important;
        padding:0 !important;
    }
    .station-select-title-v50 {
        margin-top:0 !important;
    }

    /* ---------- ⑤ 손가락 ---------- */
    .select-instruction-v527 {
        display:flex !important;
        align-items:center !important;
        gap:7px !important;
        margin:0 !important;
        padding:0 4px !important;
        min-height:36px !important;
        line-height:1.15 !important;
        font-weight:850 !important;
    }
    .tap-finger-v527 {
        display:inline-flex !important;
        align-items:center !important;
        justify-content:center !important;
        flex:0 0 34px !important;
        width:34px !important;
        height:36px !important;
        font-size:30px !important;
        line-height:1 !important;
        overflow:visible !important;
        visibility:visible !important;
        opacity:1 !important;
    }
    .select-guide-text-v527 {
        display:inline-block !important;
        line-height:1.15 !important;
    }
    .select-keyword-v527 {
        color:#7b159d !important;
        font-size:calc(1em + 2px) !important;
        font-weight:950 !important;
    }

    /* ---------- ④ 안내문과 보라색 상자 사이 정확히 2px ---------- */
    .st-key-selection_body_v527 > div[data-testid="stVerticalBlock"] {
        row-gap:2px !important;
    }
    .st-key-selection_body_v527 div[data-testid="stMarkdownContainer"]:has(.select-screen-heading-v527) {
        margin:0 !important;
        padding:0 !important;
    }
    .st-key-station_choice_input_box {
        margin-top:0 !important;
        padding-top:6px !important;
    }

    /* 선택 라벨은 잘리지 않게, 콤보와는 적당한 간격 */
    .station-choice-label {
        line-height:1.25 !important;
        min-height:1.3em !important;
        overflow:visible !important;
        margin:0 0 5px 0 !important;
        padding:1px 0 !important;
    }

    @media (max-width:768px) {
        .st-key-selection_body_v527 {
            margin-top:10px !important;
        }
        .st-key-selection_body_v527 > div[data-testid="stVerticalBlock"] {
            gap:2px !important;
            row-gap:2px !important;
        }

        .workflow-progress-arrow-v527,
        .workflow-progress-arrow-v527 svg {
            height:18px !important;
        }

        .tap-finger-v527 {
            flex-basis:32px !important;
            width:32px !important;
            height:34px !important;
            font-size:28px !important;
        }

        .select-instruction-v527 {
            min-height:34px !important;
            gap:6px !important;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# v5.28 구조 기반 간격 수정
# ============================================================
st.markdown(
    r"""
    <style>
    /* v5.27 규칙 중 선택 본문 간격에 영향을 주는 값 무효화 */
    .st-key-selection_body_v527 {
        margin-top:0 !important;
        padding-top:0 !important;
    }

    /* 확인상자 다음 Streamlit 요소가 만드는 기본 간격을 제거 */
    div[data-testid="stMarkdownContainer"]:has(.shared-station-confirm) {
        margin-bottom:0 !important;
        padding-bottom:0 !important;
    }

    /* 선택 본문 첫 요소의 시작점을 확인상자 아래 정확히 10px로 */
    .st-key-selection_body_v527 {
        position:relative !important;
        top:0 !important;
        margin-top:10px !important;
    }
    .st-key-selection_body_v527 > div[data-testid="stVerticalBlock"] {
        gap:0 !important;
        row-gap:0 !important;
    }

    .select-screen-heading-v528 {
        margin:0 !important;
        padding:0 !important;
    }

    .select-screen-heading-v528 .station-select-title-v50 {
        margin:0 0 4px 0 !important;
        padding:0 !important;
    }

    /* 안내문 자체의 하단 여백은 0 */
    .select-instruction-v528 {
        display:flex !important;
        align-items:center !important;
        gap:6px !important;
        min-height:36px !important;
        margin:0 !important;
        padding:0 4px !important;
        line-height:1.15 !important;
        font-weight:850 !important;
    }

    /* 손가락: 검지와 터치 원이 분명하게 보이도록 */
    .tap-finger-v528 {
        position:relative !important;
        display:inline-flex !important;
        align-items:flex-end !important;
        justify-content:center !important;
        width:36px !important;
        min-width:36px !important;
        height:38px !important;
        overflow:visible !important;
    }
    .finger-glyph-v528 {
        display:block !important;
        font-size:31px !important;
        line-height:31px !important;
        transform:translateY(2px) !important;
        font-family:"Segoe UI Symbol","Noto Sans Symbols 2",sans-serif !important;
    }
    .tap-ring-v528 {
        position:absolute !important;
        left:50% !important;
        top:0 !important;
        width:12px !important;
        height:12px !important;
        transform:translateX(-50%) !important;
        border:2px solid #2f80ed !important;
        border-radius:50% !important;
        box-sizing:border-box !important;
    }
    .tap-ring-v528::after {
        content:"" !important;
        position:absolute !important;
        left:50% !important;
        top:50% !important;
        width:4px !important;
        height:4px !important;
        transform:translate(-50%,-50%) !important;
        background:#2f80ed !important;
        border-radius:50% !important;
    }

    .select-guide-text-v528 {
        display:inline-block !important;
        line-height:1.15 !important;
    }
    .select-keyword-v528 {
        color:#7b159d !important;
        font-size:calc(1em + 2px) !important;
        font-weight:950 !important;
    }

    /* 안내문 다음 보라색 선택상자는 정확히 2px 뒤에 시작 */
    .st-key-selection_body_v527 div[data-testid="stMarkdownContainer"]:has(.select-screen-heading-v528) {
        margin:0 !important;
        padding:0 !important;
    }
    .st-key-station_choice_input_box {
        margin-top:2px !important;
        padding-top:6px !important;
    }

    /* 상단 메뉴: 순서와 중앙정렬 고정 */
    .st-key-workflow_cluster_v59 [class*="st-key-navcard_"] button {
        display:flex !important;
        flex-direction:column !important;
        align-items:center !important;
        justify-content:center !important;
        text-align:center !important;
    }
    .st-key-workflow_cluster_v59 [class*="st-key-navcard_"] button::after {
        order:-1 !important;
        position:static !important;
        display:block !important;
        width:100% !important;
        margin:0 0 6px 0 !important;
        text-align:center !important;
        transform:none !important;
    }
    .st-key-workflow_cluster_v59 [class*="st-key-navcard_"] button p {
        order:1 !important;
        position:static !important;
        display:block !important;
        width:max-content !important;
        max-width:96% !important;
        margin:0 auto !important;
        text-align:center !important;
        transform:none !important;
    }

    /* 새 SVG 진행 화살표만 사용 */
    .workflow-progress-arrow-v527 {
        width:100% !important;
        height:20px !important;
        margin:7px 0 10px 0 !important;
        overflow:visible !important;
    }
    .workflow-progress-arrow-v527 svg {
        width:100% !important;
        height:20px !important;
        display:block !important;
        overflow:visible !important;
    }

    @media (max-width:768px) {
        .st-key-selection_body_v527 {
            margin-top:10px !important;
        }
        .st-key-station_choice_input_box {
            margin-top:2px !important;
        }
        .tap-finger-v528 {
            width:34px !important;
            min-width:34px !important;
            height:36px !important;
        }
        .finger-glyph-v528 {
            font-size:29px !important;
            line-height:29px !important;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# v5.29 구조 정리 최종 보정
# 핵심: 선택 본문을 확인상자 바로 다음 코드 위치로 이동
# ============================================================
st.markdown(
    r"""
    <style>
    /* ---------------------------------------------------------
       1) 확인상자 -> ①[선택] 투표소 : 정확히 10px
       --------------------------------------------------------- */
    .shared-station-confirm {
        margin-bottom: 0 !important;
    }
    div[data-testid="stMarkdownContainer"]:has(.shared-station-confirm) {
        margin-bottom: 0 !important;
        padding-bottom: 0 !important;
    }

    .st-key-selection_body_v527 {
        margin-top: 10px !important;
        padding-top: 0 !important;
    }
    .st-key-selection_body_v527 > div[data-testid="stVerticalBlock"] {
        gap: 0 !important;
        row-gap: 0 !important;
    }
    .st-key-selection_body_v527 > div[data-testid="stVerticalBlock"] > div[data-testid="stElementContainer"] {
        margin-top: 0 !important;
        margin-bottom: 0 !important;
        padding-top: 0 !important;
        padding-bottom: 0 !important;
    }

    .select-screen-heading-v529 {
        margin: 0 !important;
        padding: 0 !important;
    }
    .select-screen-heading-v529 .station-select-title-v50 {
        margin: 0 0 4px 0 !important;
        padding: 0 !important;
    }

    /* ---------------------------------------------------------
       2) 손가락: 하나의 이모지 glyph로 표시
       --------------------------------------------------------- */
    .select-instruction-v529 {
        display: flex !important;
        align-items: center !important;
        gap: 6px !important;
        margin: 0 !important;
        padding: 0 4px !important;
        min-height: 34px !important;
        line-height: 1.15 !important;
        font-weight: 850 !important;
    }
    .tap-finger-v529 {
        display: inline-flex !important;
        align-items: center !important;
        justify-content: center !important;
        width: 34px !important;
        min-width: 34px !important;
        height: 34px !important;
        font-size: 29px !important;
        line-height: 1 !important;
        overflow: visible !important;
        visibility: visible !important;
        opacity: 1 !important;
        font-family: "Apple Color Emoji","Segoe UI Emoji","Noto Color Emoji",sans-serif !important;
    }
    .select-guide-text-v529 {
        display: inline-block !important;
        line-height: 1.15 !important;
    }
    .select-keyword-v529 {
        color: #7b159d !important;
        font-size: calc(1em + 2px) !important;
        font-weight: 950 !important;
    }

    /* ---------------------------------------------------------
       3) 안내문 -> 보라색 선택상자 : 정확히 2px
       --------------------------------------------------------- */
    div[data-testid="stMarkdownContainer"]:has(.select-screen-heading-v529) {
        margin: 0 !important;
        padding: 0 !important;
    }

    .st-key-station_choice_input_box {
        margin-top: 2px !important;
        margin-bottom: 12px !important;
        padding-top: 6px !important;
    }

    /* 선택상자 라벨은 잘리지 않게 */
    .station-choice-label {
        line-height: 1.25 !important;
        min-height: 1.3em !important;
        overflow: visible !important;
        margin: 0 0 5px 0 !important;
        padding: 1px 0 !important;
    }

    /* ---------------------------------------------------------
       4) 상단 메뉴는 현재 정상 상태 유지
       --------------------------------------------------------- */
    .st-key-workflow_cluster_v59 [class*="st-key-navcard_"] button {
        display:flex !important;
        flex-direction:column !important;
        align-items:center !important;
        justify-content:center !important;
        text-align:center !important;
    }
    .st-key-workflow_cluster_v59 [class*="st-key-navcard_"] button::after {
        order:-1 !important;
        position:static !important;
        display:block !important;
        width:100% !important;
        margin:0 0 6px 0 !important;
        text-align:center !important;
        transform:none !important;
    }
    .st-key-workflow_cluster_v59 [class*="st-key-navcard_"] button p {
        order:1 !important;
        position:static !important;
        display:block !important;
        width:max-content !important;
        max-width:96% !important;
        margin:0 auto !important;
        text-align:center !important;
        transform:none !important;
    }

    /* ---------------------------------------------------------
       5) 진행 화살표는 v5.27 SVG 유지
       --------------------------------------------------------- */
    .workflow-progress-arrow-v527 {
        width:100% !important;
        height:20px !important;
        margin:7px 0 10px 0 !important;
        overflow:visible !important;
    }
    .workflow-progress-arrow-v527 svg {
        display:block !important;
        width:100% !important;
        height:20px !important;
        overflow:visible !important;
    }

    @media (max-width:768px) {
        .st-key-selection_body_v527 {
            margin-top:10px !important;
        }
        .st-key-station_choice_input_box {
            margin-top:2px !important;
        }
        .tap-finger-v529 {
            width:32px !important;
            min-width:32px !important;
            height:32px !important;
            font-size:27px !important;
        }
        .select-instruction-v529 {
            min-height:32px !important;
            gap:5px !important;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# v5.30 ①화면 단일 HTML 블록 구조
# ============================================================
st.markdown(
    r"""
    <style>
    /* 이전 버전에서 남아 있던 workflow container 하단 여백 제거 */
    .st-key-workflow_cluster_v59 {
        margin-bottom: 0 !important;
        padding-bottom: 0 !important;
    }

    /* ① 화면 컨테이너 자체의 Streamlit 간격 제거 */
    .st-key-selection_body_v531 {
        margin: 0 !important;
        padding: 0 !important;
    }
    .st-key-selection_body_v531 > div[data-testid="stVerticalBlock"] {
        gap: 0 !important;
        row-gap: 0 !important;
        margin: 0 !important;
        padding: 0 !important;
    }
    .st-key-selection_body_v531 > div[data-testid="stVerticalBlock"] > div[data-testid="stElementContainer"] {
        margin: 0 !important;
        padding: 0 !important;
    }

    /* ① 화면 첫 블록 전체 */
    .step1-fixed-layout-v531 {
        margin: 0 !important;
        padding: 0 !important;
    }

    /* 확인상자 자체는 하단 margin 0 */
    .step1-fixed-layout-v531 .shared-station-confirm {
        margin: 0 !important;
    }

    /* 요청한 실제 10px 빈 공간 */
    .confirm-to-title-gap-v531 {
        display: block !important;
        height: 10px !important;
        min-height: 10px !important;
        max-height: 10px !important;
        margin: 0 !important;
        padding: 0 !important;
    }

    /* ①[선택] 투표소 */
    .station-select-title-v531 {
        margin: 0 0 3px 0 !important;
        padding: 0 !important;
        color: #111 !important;
        font-size: 28px !important;
        font-weight: 950 !important;
        line-height: 1.2 !important;
    }
    .station-select-title-v531 .select-title-green {
        color: #00a83b !important;
        font-weight: 950 !important;
    }

    /* 안내문 */
    .select-instruction-v531 {
        display: flex !important;
        align-items: center !important;
        gap: 6px !important;
        margin: 0 !important;
        padding: 0 4px !important;
        min-height: 34px !important;
        font-weight: 850 !important;
        line-height: 1.15 !important;
    }
    .tap-finger-v531 {
        display: inline-flex !important;
        align-items: center !important;
        justify-content: center !important;
        width: 34px !important;
        min-width: 34px !important;
        height: 34px !important;
        font-size: 30px !important;
        line-height: 1 !important;
        visibility: visible !important;
        opacity: 1 !important;
        overflow: visible !important;
        font-family: "Apple Color Emoji","Segoe UI Emoji","Noto Color Emoji",sans-serif !important;
    }
    .select-guide-text-v531 {
        display: inline-block !important;
        line-height: 1.15 !important;
    }
    .select-keyword-v531 {
        color: #7b159d !important;
        font-size: calc(1em + 2px) !important;
        font-weight: 950 !important;
    }

    /* 안내문 다음 선택상자: 실제 2px */
    .st-key-selection_body_v531 .st-key-station_choice_input_box {
        margin-top: 2px !important;
        padding-top: 6px !important;
    }

    /* 보라색 상자 라벨은 잘리지 않게 */
    .st-key-selection_body_v531 .station-choice-label {
        line-height: 1.25 !important;
        min-height: 1.3em !important;
        overflow: visible !important;
        margin: 0 0 5px 0 !important;
        padding: 1px 0 !important;
    }

    /* 상단 메뉴/화살표는 현재 정상 상태를 그대로 유지 */
    .st-key-workflow_cluster_v59 [class*="st-key-navcard_"] button {
        display:flex !important;
        flex-direction:column !important;
        align-items:center !important;
        justify-content:center !important;
        text-align:center !important;
    }
    .st-key-workflow_cluster_v59 [class*="st-key-navcard_"] button::after {
        order:-1 !important;
        position:static !important;
        display:block !important;
        width:100% !important;
        margin:0 0 6px 0 !important;
        text-align:center !important;
        transform:none !important;
    }
    .st-key-workflow_cluster_v59 [class*="st-key-navcard_"] button p {
        order:1 !important;
        position:static !important;
        display:block !important;
        width:max-content !important;
        max-width:96% !important;
        margin:0 auto !important;
        text-align:center !important;
        transform:none !important;
    }

    @media (max-width: 768px) {
        .station-select-title-v531 {
            font-size: 22px !important;
        }
        .tap-finger-v531 {
            width: 32px !important;
            min-width: 32px !important;
            height: 32px !important;
            font-size: 28px !important;
        }
        .select-instruction-v531 {
            min-height: 32px !important;
            gap: 5px !important;
        }
        .st-key-selection_body_v531 .st-key-station_choice_input_box {
            margin-top: 2px !important;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# v5.31 실제 원인 제거: ① 본문을 workflow_cluster 내부로 이동
# ============================================================
st.markdown(
    r"""
    <style>
    /* workflow_cluster의 Streamlit 자동 세로 gap을 제거 */
    .st-key-workflow_cluster_v59 > div[data-testid="stVerticalBlock"] {
        gap: 0 !important;
        row-gap: 0 !important;
        margin: 0 !important;
        padding: 0 !important;
    }
    .st-key-workflow_cluster_v59 > div[data-testid="stVerticalBlock"] > div[data-testid="stElementContainer"] {
        margin: 0 !important;
        padding: 0 !important;
    }

    /* 상단 안내문 → 메뉴 : 기존 가독성 유지 */
    .st-key-workflow_cluster_v59 div[data-testid="stMarkdownContainer"]:has(.workflow-guide-v33) {
        margin: 0 0 10px 0 !important;
        padding: 0 !important;
    }

    /* 메뉴 카드 행 → 진행 화살표 */
    .st-key-workflow_cluster_v59 div[data-testid="stHorizontalBlock"]:has(.st-key-navcard_select_v35) {
        margin: 0 0 5px 0 !important;
        padding: 0 !important;
    }

    /* 검정 진행 화살표 → 확인상자 */
    .workflow-progress-arrow-v527 {
        width: 100% !important;
        height: 18px !important;
        margin: 0 0 8px 0 !important;
        padding: 0 !important;
        overflow: visible !important;
    }
    .workflow-progress-arrow-v527 svg {
        display: block !important;
        width: 100% !important;
        height: 18px !important;
        overflow: visible !important;
    }

    /* ① 선택 본문 컨테이너: 상위 자동 간격 완전 제거 */
    .st-key-selection_body_v531 {
        margin: 0 !important;
        padding: 0 !important;
    }
    .st-key-selection_body_v531 > div[data-testid="stVerticalBlock"] {
        gap: 2px !important;
        row-gap: 2px !important;
        margin: 0 !important;
        padding: 0 !important;
    }
    .st-key-selection_body_v531 > div[data-testid="stVerticalBlock"] > div[data-testid="stElementContainer"] {
        margin: 0 !important;
        padding: 0 !important;
    }

    /* 확인상자 */
    .step1-fixed-layout-v531,
    .step1-fixed-layout-v531 .shared-station-confirm {
        margin: 0 !important;
        padding-top: 0 !important;
        padding-bottom: 0 !important;
    }
    .step1-fixed-layout-v531 .shared-station-confirm {
        padding: 7px 9px !important;
    }

    /* 요청사항: 확인상자 아래 정확히 10px */
    .confirm-to-title-gap-v531 {
        display: block !important;
        height: 10px !important;
        min-height: 10px !important;
        max-height: 10px !important;
        margin: 0 !important;
        padding: 0 !important;
    }

    /* ①[선택] 투표소 */
    .station-select-title-v531 {
        margin: 0 0 3px 0 !important;
        padding: 0 !important;
        color: #111 !important;
        font-size: 28px !important;
        font-weight: 950 !important;
        line-height: 1.2 !important;
    }
    .station-select-title-v531 .select-title-green {
        color: #00a83b !important;
        font-weight: 950 !important;
    }

    /* 안내문 */
    .select-instruction-v531 {
        display: flex !important;
        align-items: center !important;
        gap: 5px !important;
        margin: 0 !important;
        padding: 0 4px !important;
        min-height: 32px !important;
        line-height: 1.15 !important;
        font-weight: 850 !important;
    }
    .tap-finger-v531 {
        display: inline-flex !important;
        align-items: center !important;
        justify-content: center !important;
        width: 32px !important;
        min-width: 32px !important;
        height: 32px !important;
        font-size: 28px !important;
        line-height: 1 !important;
        overflow: visible !important;
        visibility: visible !important;
        opacity: 1 !important;
        font-family: "Apple Color Emoji","Segoe UI Emoji","Noto Color Emoji",sans-serif !important;
    }
    .select-guide-text-v531 {
        display: inline-block !important;
        line-height: 1.15 !important;
    }
    .select-keyword-v531 {
        color: #7b159d !important;
        font-size: calc(1em + 2px) !important;
        font-weight: 950 !important;
    }

    /* 요청사항: 안내문 → 보라색 선택상자 정확히 2px */
    .st-key-selection_body_v531 .st-key-station_choice_input_box {
        margin: 0 !important;
        padding-top: 6px !important;
        padding-bottom: 8px !important;
    }

    /* 첫 markdown 요소와 다음 선택상자 사이를 2px로 고정 */
    .st-key-selection_body_v531 > div[data-testid="stVerticalBlock"] {
        gap: 2px !important;
        row-gap: 2px !important;
    }

    /* 동 선택 / 투표소 선택 라벨 가독성 */
    .st-key-selection_body_v531 .station-choice-label {
        line-height: 1.25 !important;
        min-height: 1.3em !important;
        overflow: visible !important;
        margin: 0 0 5px 0 !important;
        padding: 1px 0 !important;
    }

    /* 상단 메뉴는 현재 정상 중앙정렬 유지 */
    .st-key-workflow_cluster_v59 [class*="st-key-navcard_"] button {
        display:flex !important;
        flex-direction:column !important;
        align-items:center !important;
        justify-content:center !important;
        text-align:center !important;
    }
    .st-key-workflow_cluster_v59 [class*="st-key-navcard_"] button::after {
        order:-1 !important;
        position:static !important;
        display:block !important;
        width:100% !important;
        margin:0 0 6px 0 !important;
        text-align:center !important;
        transform:none !important;
    }
    .st-key-workflow_cluster_v59 [class*="st-key-navcard_"] button p {
        order:1 !important;
        position:static !important;
        display:block !important;
        width:max-content !important;
        max-width:96% !important;
        margin:0 auto !important;
        text-align:center !important;
        transform:none !important;
    }

    @media (max-width:768px) {
        .station-select-title-v531 {
            font-size: 22px !important;
        }
        .tap-finger-v531 {
            width: 30px !important;
            min-width: 30px !important;
            height: 30px !important;
            font-size: 27px !important;
        }
        .select-instruction-v531 {
            min-height: 30px !important;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# v5.35 최종 줄간격 고정
# - 메뉴 네모상자 → 검정 화살표: 최대한 좁게
# - 검정 화살표 → 선택한 투표소 상자: 약 6px
# - 선택한 투표소 상자 → ①[선택] 투표소: 10px
# - 안내문 → 보라색 선택상자: 2px
# - 손가락/상단 메뉴/기능은 그대로 유지
# ============================================================
st.markdown(
    r"""
    <style>
    /* workflow 영역에 Streamlit이 넣는 자동 세로 간격을 제거 */
    .st-key-workflow_cluster_v59 > div[data-testid="stVerticalBlock"] {
        gap: 0 !important;
        row-gap: 0 !important;
    }
    .st-key-workflow_cluster_v59 > div[data-testid="stVerticalBlock"] > div[data-testid="stElementContainer"] {
        margin-top: 0 !important;
        margin-bottom: 0 !important;
        padding-top: 0 !important;
        padding-bottom: 0 !important;
    }

    /* ① 메뉴 상자 → 화살표: 화살표 블록 자체 높이를 줄여 실제 시각 간격 최소화 */
    .st-key-workflow_cluster_v59 div[data-testid="stHorizontalBlock"]:has(.st-key-navcard_select_v35) {
        margin-bottom: 0 !important;
        padding-bottom: 0 !important;
    }
    .workflow-progress-arrow-v527 {
        display: block !important;
        width: 100% !important;
        height: 8px !important;
        margin: 0 0 2px 0 !important;
        padding: 0 !important;
        overflow: visible !important;
    }
    .workflow-progress-arrow-v527 svg {
        display: block !important;
        width: 100% !important;
        height: 8px !important;
        overflow: visible !important;
    }

    /* ② 화살표 → 확인상자:
       8px 화살표의 중앙선에서 아래 4px + block margin 2px = 실제 약 6px */
    div[data-testid="stMarkdownContainer"]:has(.shared-station-confirm) {
        margin: 0 !important;
        padding: 0 !important;
    }
    .shared-station-confirm {
        margin: 0 !important;
    }

    /* ③ 확인상자 → ①[선택] 투표소 = 코드에 삽입된 고정 10px */
    .confirm-to-title-gap-v531 {
        display: block !important;
        height: 10px !important;
        min-height: 10px !important;
        max-height: 10px !important;
        margin: 0 !important;
        padding: 0 !important;
    }

    /* 선택 본문의 Markdown wrapper 여백까지 제거 */
    .st-key-selection_body_v531 {
        margin: 0 !important;
        padding: 0 !important;
    }
    .st-key-selection_body_v531 > div[data-testid="stVerticalBlock"] {
        gap: 2px !important;
        row-gap: 2px !important;
        margin: 0 !important;
        padding: 0 !important;
    }
    .st-key-selection_body_v531 > div[data-testid="stVerticalBlock"] > div[data-testid="stElementContainer"] {
        margin: 0 !important;
        padding: 0 !important;
    }
    .st-key-selection_body_v531 div[data-testid="stMarkdownContainer"]:has(.step1-fixed-layout-v531) {
        margin: 0 !important;
        padding: 0 !important;
    }

    .station-select-title-v531 {
        margin-top: 0 !important;
        margin-bottom: 3px !important;
        padding: 0 !important;
    }

    /* 손가락은 그대로 두고 안내문 wrapper의 불필요 높이만 제거 */
    .select-instruction-v531 {
        margin: 0 !important;
        padding-top: 0 !important;
        padding-bottom: 0 !important;
        min-height: 0 !important;
        height: auto !important;
    }

    /* ④ 안내문 → 보라색 선택상자 = 2px */
    .st-key-selection_body_v531 .st-key-station_choice_input_box {
        margin-top: 2px !important;
        margin-bottom: 0 !important;
        padding-top: 6px !important;
    }

    @media (max-width: 768px) {
        .workflow-progress-arrow-v527,
        .workflow-progress-arrow-v527 svg {
            height: 8px !important;
        }
        .workflow-progress-arrow-v527 {
            margin-bottom: 2px !important;
        }

        .confirm-to-title-gap-v531 {
            height: 10px !important;
            min-height: 10px !important;
            max-height: 10px !important;
        }

        .st-key-selection_body_v531 .st-key-station_choice_input_box {
            margin-top: 2px !important;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# v5.36 실제 모바일 화면 기준 추가 보정
# ============================================================
st.markdown(
    r"""
    <style>
    /* 메뉴 네모상자 → 화살표:
       v5.35 실제 화면보다 위로 당겨 메뉴에 더 붙임 */
    .workflow-progress-arrow-v527 {
        margin-top: -13px !important;
        margin-bottom: 8px !important;
        padding: 0 !important;
    }

    /* 메뉴 행 자체의 아래 기본 여백 제거 */
    .st-key-workflow_cluster_v59 div[data-testid="stHorizontalBlock"]:has(.st-key-navcard_select_v35) {
        margin-bottom: 0 !important;
        padding-bottom: 0 !important;
    }

    /* 화살표 → 선택한 투표소 상자:
       화살표 아래는 8px 확보 */
    div[data-testid="stMarkdownContainer"]:has(.shared-station-confirm) {
        margin-top: 0 !important;
        padding-top: 0 !important;
    }

    /* 이미 맞춘 확인상자 → ①[선택] 투표소 간격은 유지 */
    .confirm-to-title-gap-v531 {
        height: 10px !important;
        min-height: 10px !important;
        max-height: 10px !important;
    }

    /* 손가락/안내문은 그대로 유지 */
    .select-instruction-v531 {
        margin-bottom: 0 !important;
        padding-bottom: 0 !important;
    }

    /* 손가락 표시 줄 → 보라색 선택상자:
       v5.35 실제 화면의 빈 공간을 줄여 시각적으로 거의 붙도록 보정 */
    .st-key-selection_body_v531 .st-key-station_choice_input_box {
        margin-top: -18px !important;
        padding-top: 6px !important;
    }

    @media (max-width: 768px) {
        .workflow-progress-arrow-v527 {
            margin-top: -13px !important;
            margin-bottom: 8px !important;
        }

        .st-key-selection_body_v531 .st-key-station_choice_input_box {
            margin-top: -18px !important;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# v5.37 요청사항 반영
# 1) 검정 진행 화살표 굵기 증가
# 2) 화살표 → '선택한 투표소는~입니다.' 상자 = 10px
# 3) 확인상자 → ①[선택] 투표소 = 15px
# 기존 정상 영역은 유지
# ============================================================
st.markdown(
    r"""
    <style>
    /* 1. 화살표를 조금 더 굵게 */
    .workflow-progress-arrow-v527 {
        margin-top: -13px !important;
        margin-bottom: 10px !important;   /* 2. 확인상자까지 10px */
        height: 10px !important;
        padding: 0 !important;
        overflow: visible !important;
    }

    .workflow-progress-arrow-v527 svg {
        width: 100% !important;
        height: 10px !important;
        display: block !important;
        overflow: visible !important;
    }

    /* 기존 SVG 선/화살촉 굵기 보강 */
    .workflow-progress-arrow-v527 svg line {
        stroke-width: 6 !important;
    }

    /* 화살촉은 조금 더 두껍게 보이도록 확대 */
    .workflow-progress-arrow-v527 svg polygon {
        transform-box: fill-box !important;
        transform-origin: center !important;
        transform: scale(1.08) !important;
    }

    /* 확인상자 위쪽 기본 여백 제거 */
    div[data-testid="stMarkdownContainer"]:has(.shared-station-confirm) {
        margin-top: 0 !important;
        padding-top: 0 !important;
    }

    /* 3. 확인상자 → ①[선택] 투표소 = 15px */
    .confirm-to-title-gap-v531 {
        display: block !important;
        height: 15px !important;
        min-height: 15px !important;
        max-height: 15px !important;
        margin: 0 !important;
        padding: 0 !important;
    }

    @media (max-width: 768px) {
        .workflow-progress-arrow-v527 {
            margin-bottom: 10px !important;
            height: 10px !important;
        }

        .workflow-progress-arrow-v527 svg {
            height: 10px !important;
        }

        .confirm-to-title-gap-v531 {
            height: 15px !important;
            min-height: 15px !important;
            max-height: 15px !important;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# v5.38 요청사항 반영
# 1) 메뉴 네모상자 → 화살표: 3px
# 2) 화살표 굵기 조금 더 증가
# 3) 화살표 → 선택한 투표소 상자: 15px
# 4) 선택한 투표소 상자 → ①[선택] 투표소: 30px
# 5) 손가락 아이콘 조금 축소
# ============================================================
st.markdown(
    r"""
    <style>
    /* 메뉴 행 하단 기본 여백 제거 */
    .st-key-workflow_cluster_v59 div[data-testid="stHorizontalBlock"]:has(.st-key-navcard_select_v35) {
        margin-bottom: 0 !important;
        padding-bottom: 0 !important;
    }

    /* 1 + 2 + 3: 화살표 위치/굵기/아래 간격 */
    .workflow-progress-arrow-v527 {
        margin-top: 3px !important;      /* 메뉴 네모상자와 3px */
        margin-bottom: 15px !important;  /* 아래 확인상자와 15px */
        height: 12px !important;
        padding: 0 !important;
        overflow: visible !important;
    }

    .workflow-progress-arrow-v527 svg {
        display: block !important;
        width: 100% !important;
        height: 12px !important;
        overflow: visible !important;
    }

    .workflow-progress-arrow-v527 svg line {
        stroke-width: 7 !important;      /* 기존보다 조금 더 굵게 */
    }

    .workflow-progress-arrow-v527 svg polygon {
        transform-box: fill-box !important;
        transform-origin: center !important;
        transform: scale(1.12) !important;
    }

    /* 확인상자 위쪽 자동 여백 제거 */
    div[data-testid="stMarkdownContainer"]:has(.shared-station-confirm) {
        margin-top: 0 !important;
        padding-top: 0 !important;
    }

    /* 4: 확인상자 → ①[선택] 투표소 = 30px */
    .confirm-to-title-gap-v531 {
        display: block !important;
        height: 30px !important;
        min-height: 30px !important;
        max-height: 30px !important;
        margin: 0 !important;
        padding: 0 !important;
    }

    /* 5: 손가락 아이콘 조금 축소 */
    .tap-finger-v531 {
        width: 26px !important;
        min-width: 26px !important;
        height: 26px !important;
        font-size: 23px !important;
    }

    @media (max-width: 768px) {
        .workflow-progress-arrow-v527 {
            margin-top: 3px !important;
            margin-bottom: 15px !important;
            height: 12px !important;
        }

        .workflow-progress-arrow-v527 svg {
            height: 12px !important;
        }

        .confirm-to-title-gap-v531 {
            height: 30px !important;
            min-height: 30px !important;
            max-height: 30px !important;
        }

        .tap-finger-v531 {
            width: 24px !important;
            min-width: 24px !important;
            height: 24px !important;
            font-size: 21px !important;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# v5.39 ②[보고] 화면 제목 추가 + 본문 간격 통일
# ============================================================
st.markdown(
    r"""
    <style>
    /* ② 화면 상단 제목 */
    .report-screen-heading-v539 {
        margin: 0 0 6px 0 !important;
        padding: 0 !important;
        font-size: 22px !important;
        line-height: 1.2 !important;
        font-weight: 950 !important;
        color: #111 !important;
    }
    .report-title-green-v539 {
        color: #00a83b !important;
        font-weight: 950 !important;
    }

    /* ② 화면 본문을 ① 화면과 비슷하게 조밀하게 */
    .st-key-report_body_v41 > div[data-testid="stVerticalBlock"],
    .st-key-report_body_v41 div[data-testid="stVerticalBlock"] {
        gap: 0.35rem !important;
        row-gap: 0.35rem !important;
    }

    .report-v41-headrow,
    .report-v41-help,
    .report-section,
    .report-subsection,
    .report-table-wrap {
        margin-top: 0 !important;
        margin-bottom: 6px !important;
    }

    /* 기존 '1.투표진행상황보고...' 제목 위 여백 축소 */
    div[data-testid="stMarkdownContainer"]:has(.report-v41-headrow) {
        margin-top: 0 !important;
        padding-top: 0 !important;
    }

    /* 안내/경고 박스와 제목 사이 간격 축소 */
    div[data-testid="stAlert"] {
        margin-top: 4px !important;
        margin-bottom: 6px !important;
    }

    @media (max-width: 768px) {
        .report-screen-heading-v539 {
            font-size: 20px !important;
            margin-bottom: 5px !important;
        }

        .st-key-report_body_v41 > div[data-testid="stVerticalBlock"],
        .st-key-report_body_v41 div[data-testid="stVerticalBlock"] {
            gap: 0.28rem !important;
            row-gap: 0.28rem !important;
        }

        .report-v41-headrow,
        .report-v41-help,
        .report-section,
        .report-subsection,
        .report-table-wrap {
            margin-bottom: 5px !important;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# v5.40 ②[보고] 화면 구조/줄간격 수정
# ============================================================
st.markdown(
    r"""
    <style>
    .st-key-workflow_cluster_v59 > div[data-testid="stVerticalBlock"] {
        gap: 0 !important;
        row-gap: 0 !important;
    }

    .report-screen-heading-v539 {
        margin-top: 10px !important;
        margin-bottom: 5px !important;
        padding: 0 !important;
        font-size: 22px !important;
        line-height: 1.2 !important;
        font-weight: 950 !important;
    }

    .report-v41-headrow {
        margin-top: 0 !important;
        margin-bottom: 5px !important;
    }

    .report-v41-title {
        margin: 0 !important;
        padding: 0 !important;
    }

    .st-key-report_input_calc_box {
        margin-top: 2px !important;
        margin-bottom: 4px !important;
    }

    .report-v41-help {
        margin-top: 4px !important;
        margin-bottom: 4px !important;
    }

    .report-v41-notice {
        margin-top: 2px !important;
        margin-bottom: 8px !important;
    }

    .report-v41-ref-title {
        margin-top: 4px !important;
        margin-bottom: 5px !important;
    }

    div[data-testid="stAlert"] {
        margin-top: 3px !important;
        margin-bottom: 5px !important;
    }

    @media (max-width: 768px) {
        .report-screen-heading-v539 {
            margin-top: 10px !important;
            margin-bottom: 4px !important;
            font-size: 20px !important;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# v5.41 ②페이지 상단 줄간격 = ①페이지와 동일
# ============================================================
st.markdown(
    r"""
    <style>
    /* 모든 페이지에서 상단 메뉴 행의 자동 아래 여백 제거 */
    .st-key-workflow_cluster_v59 div[data-testid="stHorizontalBlock"]:has(.st-key-navcard_select_v35),
    .st-key-workflow_cluster_v59 div[data-testid="stHorizontalBlock"]:has(.st-key-navcard_report_v35),
    .st-key-workflow_cluster_v59 div[data-testid="stHorizontalBlock"]:has(.st-key-navcard_input_v35),
    .st-key-workflow_cluster_v59 div[data-testid="stHorizontalBlock"]:has(.st-key-navcard_reference_v35) {
        margin-bottom: 0 !important;
        padding-bottom: 0 !important;
    }

    /* ①페이지와 동일: 메뉴 네모상자 → 화살표 3px */
    .workflow-progress-arrow-v527 {
        margin-top: 3px !important;
        margin-bottom: 15px !important;
        height: 12px !important;
        padding: 0 !important;
        overflow: visible !important;
    }

    .workflow-progress-arrow-v527 svg {
        display: block !important;
        width: 100% !important;
        height: 12px !important;
        overflow: visible !important;
    }

    /* ①페이지와 동일: 화살표 → 확인상자 15px */
    div[data-testid="stMarkdownContainer"]:has(.shared-station-confirm) {
        margin-top: 0 !important;
        padding-top: 0 !important;
    }

    @media (max-width: 768px) {
        .workflow-progress-arrow-v527 {
            margin-top: 3px !important;
            margin-bottom: 15px !important;
            height: 12px !important;
        }

        .workflow-progress-arrow-v527 svg {
            height: 12px !important;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# v5.42 ②페이지 상단 실제 간격 보정
# ①페이지의 보이는 간격과 동일하게 맞추기 위한 컨테이너 기본여백 제거
# ============================================================
st.markdown(
    r"""
    <style>
    /* workflow 공통 블록의 Streamlit 자동 gap 제거 */
    .st-key-workflow_cluster_v59 > div[data-testid="stVerticalBlock"] {
        gap: 0 !important;
        row-gap: 0 !important;
    }

    .st-key-workflow_cluster_v59 > div[data-testid="stVerticalBlock"]
    > div[data-testid="stElementContainer"] {
        margin-top: 0 !important;
        margin-bottom: 0 !important;
        padding-top: 0 !important;
        padding-bottom: 0 !important;
    }

    /* 메뉴 카드 행 자체의 바깥 여백 제거 */
    .st-key-workflow_cluster_v59 div[data-testid="stHorizontalBlock"] {
        margin-bottom: 0 !important;
        padding-bottom: 0 !important;
    }

    /* ①페이지에서 확정한 실제 상단 간격 */
    .workflow-progress-arrow-v527 {
        margin-top: 3px !important;
        margin-bottom: 15px !important;
        padding-top: 0 !important;
        padding-bottom: 0 !important;
        height: 12px !important;
    }

    /* 화살표를 감싼 markdown wrapper의 기본 여백 제거 */
    div[data-testid="stMarkdownContainer"]:has(.workflow-progress-arrow-v527) {
        margin: 0 !important;
        padding: 0 !important;
    }

    /* 확인상자 wrapper 기본 여백 제거 */
    div[data-testid="stMarkdownContainer"]:has(.shared-station-confirm) {
        margin: 0 !important;
        padding: 0 !important;
    }

    /* 확인상자 자체에는 추가 상하 margin을 주지 않음 */
    .shared-station-confirm {
        margin-top: 0 !important;
        margin-bottom: 0 !important;
    }

    @media (max-width: 768px) {
        .st-key-workflow_cluster_v59 > div[data-testid="stVerticalBlock"] {
            gap: 0 !important;
            row-gap: 0 !important;
        }

        .workflow-progress-arrow-v527 {
            margin-top: 3px !important;
            margin-bottom: 15px !important;
            height: 12px !important;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# v5.43 [보고] 교부수량 강조
# ============================================================
st.markdown(
    r"""
    <style>
    /* [보고] 교부수량 영역만 연미색 배경으로 강조 */
    .report-issued-qty-v41,
    .report-issued-qty,
    .report-v41-issued,
    .report-v41-issued-box {
        background: #fff9e8 !important;
        border-radius: 8px !important;
        padding: 8px 10px !important;
        box-sizing: border-box !important;
    }

    /* 파란색 글자는 그대로 유지 */
    .report-issued-qty-v41,
    .report-issued-qty-v41 *,
    .report-issued-qty,
    .report-issued-qty *,
    .report-v41-issued,
    .report-v41-issued *,
    .report-v41-issued-box,
    .report-v41-issued-box * {
        color: #0000ff !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# v5.44 ②페이지 간격 / 교부수량 강조 / 안내문 정렬
# ============================================================
st.markdown(
    r"""
    <style>
    /* ②페이지 확인상자+제목 블록 */
    .report-fixed-layout-v544 {
        margin: 0 !important;
        padding: 0 !important;
    }
    .report-fixed-layout-v544 .shared-station-confirm {
        margin: 0 !important;
    }

    /* ①페이지와 동일한 confirm-to-title-gap-v531을 그대로 사용 */
    .report-screen-heading-v544 {
        margin: 0 0 6px 0 !important;
        padding: 0 !important;
        font-size: 22px !important;
        line-height: 1.2 !important;
        font-weight: 950 !important;
        color: #111 !important;
    }
    .report-title-green-v544 {
        color: #00a83b !important;
        font-weight: 950 !important;
    }

    /* ②제목과 기존 1. 제목 사이의 불필요한 Streamlit 여백 축소 */
    div[data-testid="stMarkdownContainer"]:has(.report-fixed-layout-v544) {
        margin-bottom: 0 !important;
        padding-bottom: 0 !important;
    }
    .report-v41-headrow {
        margin-top: 0 !important;
        margin-bottom: 5px !important;
    }

    /* [보고] 교부수량 연미색 강조 */
    .report-issued-highlight-v544 {
        background: #fff7df !important;
        border-radius: 8px !important;
        padding: 8px 8px 7px 8px !important;
        margin: 0 !important;
        box-sizing: border-box !important;
    }

    /* 안내문 2줄 정렬:
       ※를 별도 칸으로 두어 둘째 줄의 '기재 후'가 첫째 줄 '보고대상'의 '보' 아래에 오게 함 */
    .report-v544-help {
        display: flex !important;
        align-items: flex-start !important;
        gap: 4px !important;
        margin: 8px 0 0 0 !important;
        padding: 0 !important;
        font-size: 15px !important;
        line-height: 1.35 !important;
        font-weight: 800 !important;
    }
    .report-v544-help-mark {
        flex: 0 0 auto !important;
    }
    .report-v544-help-text {
        display: inline-block !important;
        flex: 1 1 auto !important;
        min-width: 0 !important;
    }
    .report-v544-help .red {
        color: red !important;
        font-weight: 900 !important;
    }
    .report-v544-help .blue {
        color: blue !important;
        font-weight: 900 !important;
    }

    @media (max-width: 768px) {
        .report-screen-heading-v544 {
            font-size: 20px !important;
            margin-bottom: 5px !important;
        }
        .report-issued-highlight-v544 {
            padding: 7px 6px 6px 6px !important;
        }
        .report-v544-help {
            gap: 3px !important;
            font-size: 13px !important;
            line-height: 1.32 !important;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# v5.45 ②페이지 상단 줄간격 = ①페이지와 동일
# ============================================================
st.markdown(
    r"""
    <style>
    /* ①페이지와 동일한 상단 간격값 사용 */
    .workflow-progress-arrow-v527 {
        margin-top: 3px !important;
        margin-bottom: 15px !important;
        height: 12px !important;
        padding: 0 !important;
    }

    .workflow-progress-arrow-v527 svg {
        height: 12px !important;
    }

    /* ②페이지 확인상자와 본문 제목 사이를 ①페이지와 동일한 30px로 */
    .report-fixed-layout-v544 .confirm-to-title-gap-v531 {
        height: 30px !important;
        min-height: 30px !important;
        max-height: 30px !important;
        margin: 0 !important;
        padding: 0 !important;
    }

    /* ②페이지 확인상자와 제목을 감싼 블록의 외부 여백 제거 */
    .report-fixed-layout-v544 {
        margin: 0 !important;
        padding: 0 !important;
    }

    div[data-testid="stMarkdownContainer"]:has(.report-fixed-layout-v544) {
        margin: 0 !important;
        padding: 0 !important;
    }

    /* ② 제목 자체의 위쪽 추가 여백 제거 */
    .report-screen-heading-v544 {
        margin-top: 0 !important;
    }

    @media (max-width: 768px) {
        .workflow-progress-arrow-v527 {
            margin-top: 3px !important;
            margin-bottom: 15px !important;
            height: 12px !important;
        }

        .report-fixed-layout-v544 .confirm-to-title-gap-v531 {
            height: 30px !important;
            min-height: 30px !important;
            max-height: 30px !important;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# v5.46 ②페이지 = ①페이지 실제 상단 구조 그대로 재사용
# ============================================================
st.markdown(
    r"""
    <style>
    /* ②페이지 wrapper는 추가 여백을 전혀 만들지 않음 */
    .report-page2-fixed-v546 {
        margin: 0 !important;
        padding: 0 !important;
    }

    /* ①페이지와 동일한 shared confirm / gap / title 규칙을 그대로 적용 */
    .report-page2-fixed-v546 .shared-station-confirm {
        margin: 0 !important;
    }

    .report-page2-fixed-v546 .confirm-to-title-gap-v531 {
        margin: 0 !important;
        padding: 0 !important;
    }

    .report-page2-fixed-v546 .station-select-title-v531 {
        margin-top: 0 !important;
    }

    /* 이 블록을 감싸는 Streamlit markdown의 추가 여백도 제거 */
    div[data-testid="stMarkdownContainer"]:has(.report-page2-fixed-v546) {
        margin: 0 !important;
        padding: 0 !important;
    }

    /* [보고] 교부수량은 반드시 한 줄 */
    .report-issued-label-one-line-v546 {
        white-space: nowrap !important;
        word-break: keep-all !important;
        overflow-wrap: normal !important;
        line-height: 1.15 !important;
    }

    @media (max-width: 768px) {
        .report-issued-label-one-line-v546 {
            font-size: 18px !important;
            letter-spacing: -0.6px !important;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# v5.47 ②페이지 확인상자→본문 제목 간격을
# 사용자가 제시한 ①페이지 실제 화면과 시각적으로 동일하게 보정
# ============================================================
st.markdown(
    r"""
    <style>
    /* ②페이지 전용: 기존 30px gap이 실제 화면에서 더 크게 보여
       ①페이지 캡처와 동일하게 보이도록 15px로 보정 */
    .report-page2-fixed-v546 .confirm-to-title-gap-v531 {
        height: 15px !important;
        min-height: 15px !important;
        max-height: 15px !important;
        margin: 0 !important;
        padding: 0 !important;
    }

    /* ②페이지 제목 자체의 추가 위 여백 제거 */
    .report-page2-fixed-v546 .station-select-title-v531 {
        margin-top: 0 !important;
        padding-top: 0 !important;
    }

    /* ②페이지 HTML 블록 wrapper의 추가 여백 제거 */
    div[data-testid="stMarkdownContainer"]:has(.report-page2-fixed-v546) {
        margin-top: 0 !important;
        margin-bottom: 0 !important;
        padding-top: 0 !important;
        padding-bottom: 0 !important;
    }

    @media (max-width: 768px) {
        .report-page2-fixed-v546 .confirm-to-title-gap-v531 {
            height: 15px !important;
            min-height: 15px !important;
            max-height: 15px !important;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# v5.48 ②페이지를 ①페이지 방식으로 구조 재정리
# ============================================================
st.markdown(
    r"""
    <style>
    /* ②페이지 상단: 하나의 연속 HTML 블록 */
    .report-page2-shell-v548 {
        margin: 0 !important;
        padding: 0 !important;
    }

    .report-page2-shell-v548 .shared-station-confirm {
        margin: 0 !important;
    }

    /* 사용자가 기준으로 잡은 실제 화면 간격 */
    .report-gap-after-confirm-v548 {
        height: 30px !important;
        min-height: 30px !important;
        max-height: 30px !important;
        margin: 0 !important;
        padding: 0 !important;
    }

    .report-page2-title-v548 {
        margin: 0 !important;
        padding: 0 !important;
        font-size: 22px !important;
        line-height: 1.2 !important;
        font-weight: 950 !important;
        color: #111 !important;
    }

    .report-page2-title-green-v548 {
        color: #00a83b !important;
        font-weight: 950 !important;
    }

    .report-gap-after-title-v548 {
        height: 12px !important;
        min-height: 12px !important;
        max-height: 12px !important;
        margin: 0 !important;
        padding: 0 !important;
    }

    .report-page2-subtitle-v548 {
        margin: 0 !important;
        padding: 0 !important;
        font-size: 18px !important;
        line-height: 1.25 !important;
        font-weight: 900 !important;
        color: #222 !important;
    }

    /* shell을 감싸는 Streamlit markdown 기본 여백 제거 */
    div[data-testid="stMarkdownContainer"]:has(.report-page2-shell-v548) {
        margin: 0 !important;
        padding: 0 !important;
    }

    /* 기존 ②페이지 상단 margin 보정 규칙 무효화 */
    .report-screen-heading-v539,
    .report-screen-heading-v544,
    .report-v41-headrow {
        margin-top: 0 !important;
        padding-top: 0 !important;
    }

    /* 보고 입력 보라색 상자:
       안내문 2줄 포함 내용만큼 자동으로 높이 증가 */
    .st-key-report_input_calc_box,
    .st-key-report_input_calc_box > div[data-testid="stVerticalBlock"] {
        height: auto !important;
        min-height: 0 !important;
        max-height: none !important;
        overflow: visible !important;
    }

    .st-key-report_input_calc_box {
        padding-bottom: 14px !important;
        box-sizing: border-box !important;
    }

    .st-key-report_input_calc_box > div[data-testid="stVerticalBlock"] {
        gap: 4px !important;
        row-gap: 4px !important;
    }

    /* 안내문 2줄이 보라색 테두리와 겹치지 않도록 */
    .report-v544-help {
        margin-bottom: 2px !important;
        padding-bottom: 0 !important;
    }

    /* [보고] 교부수량 한 줄 유지 */
    .report-issued-label-one-line-v546 {
        white-space: nowrap !important;
        word-break: keep-all !important;
        overflow-wrap: normal !important;
    }

    @media (max-width: 768px) {
        .report-gap-after-confirm-v548 {
            height: 30px !important;
            min-height: 30px !important;
            max-height: 30px !important;
        }

        .report-page2-title-v548 {
            font-size: 20px !important;
        }

        .report-gap-after-title-v548 {
            height: 10px !important;
            min-height: 10px !important;
            max-height: 10px !important;
        }

        .report-page2-subtitle-v548 {
            font-size: 17px !important;
        }

        .st-key-report_input_calc_box {
            padding-bottom: 14px !important;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# v5.49 ②페이지 = ①페이지 실제 구조/간격 그대로
# ============================================================
st.markdown(
    r"""
    <style>
    /* ②페이지는 report 전용 gap을 사용하지 않고
       ①페이지와 같은 step1-fixed-layout / confirm-to-title-gap /
       station-select-title 규칙만 사용합니다. */
    .step1-fixed-layout-v531 {
        margin: 0 !important;
        padding: 0 !important;
    }

    .step1-fixed-layout-v531 .shared-station-confirm {
        margin: 0 !important;
        padding: 7px 9px !important;
    }

    /* ①페이지에 현재 적용되는 실제 간격값을 그대로 사용 */
    .confirm-to-title-gap-v531 {
        display: block !important;
        height: 30px !important;
        min-height: 30px !important;
        max-height: 30px !important;
        margin: 0 !important;
        padding: 0 !important;
    }

    .station-select-title-v531 {
        margin: 0 0 3px 0 !important;
        padding: 0 !important;
        color: #111 !important;
        font-size: 28px !important;
        font-weight: 950 !important;
        line-height: 1.2 !important;
    }

    .station-select-title-v531 .select-title-green {
        color: #00a83b !important;
        font-weight: 950 !important;
    }

    /* 해당 HTML 블록을 감싸는 Streamlit markdown 자체 여백 제거 */
    div[data-testid="stMarkdownContainer"]:has(.step1-fixed-layout-v531) {
        margin: 0 !important;
        padding: 0 !important;
    }

    /* ②제목 뒤 기존 1.제목까지 불필요한 큰 간격 제거 */
    .report-v41-headrow {
        margin-top: 6px !important;
        margin-bottom: 5px !important;
    }

    /* 보라색 보고 입력상자는 내용에 따라 자동으로 늘어남 */
    .st-key-report_input_calc_box {
        height: auto !important;
        min-height: 0 !important;
        max-height: none !important;
        overflow: visible !important;
        padding-bottom: 16px !important;
        box-sizing: border-box !important;
    }

    .st-key-report_input_calc_box > div[data-testid="stVerticalBlock"] {
        height: auto !important;
        min-height: 0 !important;
        max-height: none !important;
        overflow: visible !important;
    }

    /* 안내문 2줄이 하단 테두리에 닿지 않도록 */
    .report-v544-help {
        margin-bottom: 4px !important;
        padding-bottom: 0 !important;
    }

    /* [보고] 교부수량 한 줄 유지 */
    .report-issued-label-one-line-v546 {
        white-space: nowrap !important;
        word-break: keep-all !important;
        overflow-wrap: normal !important;
    }

    @media (max-width: 768px) {
        .confirm-to-title-gap-v531 {
            height: 30px !important;
            min-height: 30px !important;
            max-height: 30px !important;
        }

        .station-select-title-v531 {
            font-size: 22px !important;
        }

        .st-key-report_input_calc_box {
            padding-bottom: 16px !important;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# v5.50 ②페이지 상단 줄간격 원인 제거
# ============================================================
st.markdown(
    r"""
    <style>
    /* ②페이지 상단은 하나의 HTML 블록이므로 외부 Streamlit 간격 0 */
    .report-top-shell-v550 {
        margin: 0 !important;
        padding: 0 !important;
    }

    div[data-testid="stMarkdownContainer"]:has(.report-top-shell-v550) {
        margin: 0 !important;
        padding: 0 !important;
    }

    .report-top-shell-v550 .shared-station-confirm {
        margin: 0 !important;
    }

    /* 사용자가 제시한 ①페이지 실제 화면과 비슷한 시각 간격 */
    .report-confirm-gap-v550 {
        display: block !important;
        height: 15px !important;
        min-height: 15px !important;
        max-height: 15px !important;
        margin: 0 !important;
        padding: 0 !important;
    }

    .report-title-v550 {
        margin: 0 !important;
        padding: 0 !important;
        color: #111 !important;
        font-size: 22px !important;
        line-height: 1.2 !important;
        font-weight: 950 !important;
    }

    .report-title-green-v550 {
        color: #00a83b !important;
        font-weight: 950 !important;
    }

    /* ②제목 → 1.투표진행상황 보고 간격 */
    .report-title-gap-v550 {
        display: block !important;
        height: 8px !important;
        min-height: 8px !important;
        max-height: 8px !important;
        margin: 0 !important;
        padding: 0 !important;
    }

    .report-subtitle-v550 {
        margin: 0 !important;
        padding: 0 !important;
        color: #222 !important;
        font-size: 18px !important;
        line-height: 1.25 !important;
        font-weight: 900 !important;
    }

    /* 뒤쪽 누적 CSS의 공용 gap 규칙이 ②페이지에 영향을 주지 않도록 함 */
    .report-top-shell-v550 .confirm-to-title-gap-v531,
    .report-top-shell-v550 .station-select-title-v531 {
        display: none !important;
    }

    /* 보라색 입력상자는 기존 정상 동작 유지 + 하단 안내문 여유 확보 */
    .st-key-report_input_calc_box {
        height: auto !important;
        min-height: 0 !important;
        max-height: none !important;
        overflow: visible !important;
        padding-bottom: 18px !important;
        box-sizing: border-box !important;
    }

    .st-key-report_input_calc_box > div[data-testid="stVerticalBlock"] {
        height: auto !important;
        min-height: 0 !important;
        max-height: none !important;
        overflow: visible !important;
    }

    .report-v544-help {
        margin-bottom: 4px !important;
    }

    @media (max-width: 768px) {
        .report-confirm-gap-v550 {
            height: 15px !important;
            min-height: 15px !important;
            max-height: 15px !important;
        }

        .report-title-v550 {
            font-size: 20px !important;
        }

        .report-title-gap-v550 {
            height: 7px !important;
            min-height: 7px !important;
            max-height: 7px !important;
        }

        .report-subtitle-v550 {
            font-size: 17px !important;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# v5.51 ②페이지 상단 = ①페이지의 실제 컨테이너 구조 그대로
# ============================================================
st.markdown(
    r"""
    <style>
    /* ①페이지 selection_body_v531과 동일:
       nested container의 Streamlit 자동 세로 gap 제거 */
    .st-key-report_body_v551 {
        margin: 0 !important;
        padding: 0 !important;
    }

    .st-key-report_body_v551 > div[data-testid="stVerticalBlock"] {
        gap: 0 !important;
        row-gap: 0 !important;
        margin: 0 !important;
        padding: 0 !important;
    }

    .st-key-report_body_v551 > div[data-testid="stVerticalBlock"]
    > div[data-testid="stElementContainer"] {
        margin-top: 0 !important;
        margin-bottom: 0 !important;
        padding-top: 0 !important;
        padding-bottom: 0 !important;
    }

    /* ②페이지 상단은 ①페이지와 동일한
       step1-fixed-layout-v531 / confirm-to-title-gap-v531 /
       station-select-title-v531을 그대로 사용 */
    .report-page2-layout-v551 {
        margin: 0 !important;
        padding: 0 !important;
    }

    div[data-testid="stMarkdownContainer"]:has(.report-page2-layout-v551) {
        margin: 0 !important;
        padding: 0 !important;
    }

    .report-page2-layout-v551 .shared-station-confirm {
        margin: 0 !important;
    }

    /* 공용 confirm-to-title-gap-v531 값은 ①페이지에서 쓰는 현재 값을 그대로 상속 */
    .report-page2-layout-v551 .confirm-to-title-gap-v531 {
        margin: 0 !important;
        padding: 0 !important;
    }

    .report-page2-layout-v551 .station-select-title-v531 {
        margin-top: 0 !important;
        padding-top: 0 !important;
    }

    /* ②[보고] 제목 다음 1.제목만 별도 최소 간격 */
    .report-subtitle-gap-v551 {
        display: block !important;
        height: 8px !important;
        min-height: 8px !important;
        max-height: 8px !important;
        margin: 0 !important;
        padding: 0 !important;
    }

    .report-subtitle-v551 {
        margin: 0 !important;
        padding: 0 !important;
        font-size: 18px !important;
        line-height: 1.25 !important;
        font-weight: 900 !important;
        color: #222 !important;
    }

    /* 보고용 내부 style markdown도 별도 빈 공간을 만들지 않도록 */
    .st-key-report_body_v551 div[data-testid="stMarkdownContainer"] {
        margin-top: 0 !important;
        margin-bottom: 0 !important;
    }

    /* 보고 입력 보라색 상자: 내용에 따라 자동 높이 */
    .st-key-report_input_calc_box,
    .st-key-report_input_calc_box > div[data-testid="stVerticalBlock"] {
        height: auto !important;
        min-height: 0 !important;
        max-height: none !important;
        overflow: visible !important;
    }

    .st-key-report_input_calc_box {
        padding-bottom: 18px !important;
        box-sizing: border-box !important;
    }

    /* [보고] 교부수량 한 줄/연미색 배경 유지 */
    .report-issued-label-one-line-v546 {
        white-space: nowrap !important;
        word-break: keep-all !important;
        overflow-wrap: normal !important;
    }

    @media (max-width:768px) {
        .report-subtitle-gap-v551 {
            height: 7px !important;
            min-height: 7px !important;
            max-height: 7px !important;
        }

        .report-subtitle-v551 {
            font-size: 17px !important;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# v5.52 ②페이지 줄간격 최종 보정
# - 기존 구조는 유지
# - ②페이지에만 공용 30px gap을 10px로 축소
# - ②제목→1.제목도 4px로 축소
# ============================================================
st.markdown(
    r"""
    <style>
    /* ②페이지 확인상자 → ②[보고] 투표진행상황 */
    .report-page2-layout-v551 .confirm-to-title-gap-v531 {
        height: 10px !important;
        min-height: 10px !important;
        max-height: 10px !important;
        margin: 0 !important;
        padding: 0 !important;
    }

    /* ②페이지 제목 자체의 불필요한 위/아래 여백 제거 */
    .report-page2-layout-v551 .station-select-title-v531 {
        margin: 0 !important;
        padding: 0 !important;
        line-height: 1.2 !important;
    }

    /* ②제목 → 1.투표진행상황 보고 */
    .report-page2-layout-v551 .report-subtitle-gap-v551 {
        height: 4px !important;
        min-height: 4px !important;
        max-height: 4px !important;
        margin: 0 !important;
        padding: 0 !important;
    }

    .report-page2-layout-v551 .report-subtitle-v551 {
        margin: 0 !important;
        padding: 0 !important;
        line-height: 1.2 !important;
    }

    /* ②페이지 nested container가 만드는 추가 간격 제거 */
    .st-key-report_body_v551 {
        margin: 0 !important;
        padding: 0 !important;
    }

    .st-key-report_body_v551 > div[data-testid="stVerticalBlock"] {
        gap: 0 !important;
        row-gap: 0 !important;
        margin: 0 !important;
        padding: 0 !important;
    }

    .st-key-report_body_v551 > div[data-testid="stVerticalBlock"]
    > div[data-testid="stElementContainer"] {
        margin-top: 0 !important;
        margin-bottom: 0 !important;
        padding-top: 0 !important;
        padding-bottom: 0 !important;
    }

    /* 1.제목 → 보라색 입력상자 */
    .st-key-report_body_v551 .st-key-report_input_calc_box {
        margin-top: 4px !important;
    }

    /* 기존 정상 적용 부분 유지 */
    .st-key-report_input_calc_box {
        height: auto !important;
        min-height: 0 !important;
        max-height: none !important;
        overflow: visible !important;
        padding-bottom: 18px !important;
        box-sizing: border-box !important;
    }

    .report-issued-label-one-line-v546 {
        white-space: nowrap !important;
        word-break: keep-all !important;
        overflow-wrap: normal !important;
    }

    @media (max-width: 768px) {
        .report-page2-layout-v551 .confirm-to-title-gap-v531 {
            height: 10px !important;
            min-height: 10px !important;
            max-height: 10px !important;
        }

        .report-page2-layout-v551 .report-subtitle-gap-v551 {
            height: 4px !important;
            min-height: 4px !important;
            max-height: 4px !important;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# v5.53 사용자가 지정한 ②페이지 5개 줄간격 최종 조정
# ============================================================
st.markdown(
    r"""
    <style>
    /* 1. 상단 안내문 → ①~④ 메뉴 네모상자 : 간격 축소 */
    .workflow-guide-v527,
    .workflow-guide-v531 {
        margin-bottom: 2px !important;
        padding-bottom: 0 !important;
    }

    /* 안내문을 감싸는 Streamlit 요소의 아래 여백도 제거 */
    div[data-testid="stMarkdownContainer"]:has(.workflow-guide-v527),
    div[data-testid="stMarkdownContainer"]:has(.workflow-guide-v531) {
        margin-bottom: 0 !important;
        padding-bottom: 0 !important;
    }

    /* 2. 메뉴 네모상자 → 화살표 : 간격 축소 */
    .workflow-progress-arrow-v527 {
        margin-top: 1px !important;
        padding-top: 0 !important;
    }

    div[data-testid="stMarkdownContainer"]:has(.workflow-progress-arrow-v527) {
        margin-top: 0 !important;
        padding-top: 0 !important;
    }

    /* 3. 선택한 투표소 상자 → ②[보고] 투표진행상황 : 간격 확대 */
    .report-page2-layout-v551 .confirm-to-title-gap-v531 {
        height: 18px !important;
        min-height: 18px !important;
        max-height: 18px !important;
        margin: 0 !important;
        padding: 0 !important;
    }

    /* ②제목과 1.제목 사이는 현재의 조밀한 상태 유지 */
    .report-page2-layout-v551 .report-subtitle-gap-v551 {
        height: 4px !important;
        min-height: 4px !important;
        max-height: 4px !important;
        margin: 0 !important;
        padding: 0 !important;
    }

    /* 4. 1.투표진행상황 보고 → 보라색 입력상자 : 간격 크게 축소 */
    .st-key-report_body_v551 .st-key-report_input_calc_box {
        margin-top: 1px !important;
        padding-top: 0 !important;
    }

    .report-subtitle-v551 {
        margin-bottom: 0 !important;
        padding-bottom: 0 !important;
    }

    /* report_body 안 element 기본 gap도 최소화 */
    .st-key-report_body_v551 > div[data-testid="stVerticalBlock"] {
        gap: 1px !important;
        row-gap: 1px !important;
    }

    /* 5. 보라색 입력상자 → 하단 ★ 투표관리관 안내문 : 간격 축소 */
    .st-key-report_input_calc_box {
        margin-bottom: 1px !important;
    }

    .report-v41-notice {
        margin-top: 1px !important;
        padding-top: 0 !important;
    }

    div[data-testid="stMarkdownContainer"]:has(.report-v41-notice) {
        margin-top: 0 !important;
        padding-top: 0 !important;
    }

    /* 기존 정상 부분 유지: 보라색 상자는 안내문 2줄이 들어가도록 자동 높이 */
    .st-key-report_input_calc_box {
        height: auto !important;
        min-height: 0 !important;
        max-height: none !important;
        overflow: visible !important;
        padding-bottom: 18px !important;
        box-sizing: border-box !important;
    }

    /* [보고] 교부수량 한 줄 유지 */
    .report-issued-label-one-line-v546 {
        white-space: nowrap !important;
        word-break: keep-all !important;
        overflow-wrap: normal !important;
    }

    @media (max-width: 768px) {
        .workflow-progress-arrow-v527 {
            margin-top: 1px !important;
        }

        .report-page2-layout-v551 .confirm-to-title-gap-v531 {
            height: 18px !important;
            min-height: 18px !important;
            max-height: 18px !important;
        }

        .st-key-report_body_v551 > div[data-testid="stVerticalBlock"] {
            gap: 1px !important;
            row-gap: 1px !important;
        }

        .st-key-report_input_calc_box {
            margin-top: 1px !important;
            margin-bottom: 1px !important;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

