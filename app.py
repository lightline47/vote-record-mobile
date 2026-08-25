
import streamlit as st
import json
import re
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path
from datetime import datetime
from io import BytesIO

# BUILD: vote-record-mobile v5.14 SELECT-LAYOUT-COMPACT-BODY 2026-08-25

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
        .login-wrap-v512 {
            max-width: 560px;
            margin: 72px auto 18px auto;
            text-align: center;
        }
        .login-title-v512 {
            font-size: 34px;
            font-weight: 900;
            line-height: 1.35;
            margin: 0 0 20px 0;
            color: #20232a;
        }
        .login-logo-v512 {
            display: block;
            width: min(330px, 78vw);
            height: auto;
            margin: 0 auto 26px auto;
        }
        @media (max-width: 768px) {
            .login-wrap-v512 {
                margin-top: 48px;
            }
            .login-title-v512 {
                font-size: 29px;
                margin-bottom: 18px;
            }
            .login-logo-v512 {
                width: min(300px, 82vw);
                margin-bottom: 22px;
            }
        }
        </style>
        <div class="login-wrap-v512">
            <div class="login-title-v512">투표록 작성 보조 앱(App)</div>
            <img class="login-logo-v512"
                 src="data:image/png;base64,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"
                 alt="북구선거관리위원회">
        </div>
        """,
        unsafe_allow_html=True
    )
    access_pw = st.text_input("비밀번호를 입력하세요.", type="password", key="app_access_password_input")
    if st.button("🔐 앱 열기", width="stretch"):
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
        '<div class="app-main-title-v33">🗳️ 투표록 작성 보조 앱 — <span class="mobile-version-v51">모바일 전용 v5.14</span></div>',
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
        background:#fffafa !important;
    }}
    .st-key-navcard_{_selected_v35}_v35 button::before {{
        content:"●" !important;
        color:#ff4b4b !important;
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
    c1, a1, c2, a2, c3, a3, c4 = st.columns([0.92, .10, 1.28, .10, 1.28, .10, 1.28], gap="small")
    with c1:
        st.button("투표소", key="navcard_select_v35", on_click=_go_step_v35, args=("select",), width="stretch")
    with a1:
        st.markdown('<div class="nav-arrow-v35">➜</div>', unsafe_allow_html=True)
    with c2:
        st.button("투표진행상황", key="navcard_report_v35", on_click=_go_step_v35, args=("report",), width="stretch")
    with a2:
        st.markdown('<div class="nav-arrow-v35">➜</div>', unsafe_allow_html=True)
    with c3:
        st.button("투표록 기초자료", key="navcard_input_v35", on_click=_go_step_v35, args=("input",), width="stretch")
    with a3:
        st.markdown('<div class="nav-arrow-v35">➜</div>', unsafe_allow_html=True)
    with c4:
        st.button("투표록(2p)", key="navcard_reference_v35", on_click=_go_step_v35, args=("reference",), width="stretch")


workflow_step = WORKFLOW_LABELS[st.session_state.workflow_step_v33]

# ------------------------------------------------------------
# Current station / hourly state helpers
# ------------------------------------------------------------
selected_key = st.session_state.get("session_selected_key")
station = db.get(selected_key) if selected_key and selected_key in db else None

hourly_by_station = local.setdefault("hourly_by_station", {})
hourly = hourly_by_station.setdefault(selected_key, []) if selected_key else []

# v5.10: 선택한 투표소 확인상자를 상단 진행메뉴와 같은 컨테이너 안에 배치
# 메뉴 아래의 과도한 Streamlit 블록 여백을 제거하고 위/아래 간격을 균형 있게 유지
with workflow_cluster_v59:
    if station is not None:
        st.markdown(
            f'<div class="selected-station-confirm shared-station-confirm"><span class="arrow">➜</span>'
            f'선택한 투표소는 <span class="selected-name">({station["dong"]} {station["station"]}표소)</span>입니다.</div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            '<div class="selected-station-confirm shared-station-confirm"><span class="arrow">➜</span>'
            '선택한 투표소는 <span class="selected-name">(<span style="display:inline-block; min-width:190px; border-bottom:2px solid #7b159d; line-height:1.05;">&nbsp;</span>)</span>입니다.</div>',
            unsafe_allow_html=True,
        )

    # v5.11: 선택 화면 제목을 확인상자 바로 아래 같은 컨테이너에 배치하여 과도한 공백 제거
    if workflow_step == "①[선택]투표소":
        st.markdown(
            """
            <div class="select-screen-heading-v514">
                <div class="station-select-title-v50"><span class="select-title-green">①[선택]</span> 투표소</div>
                <div class="select-instruction-v514">
                    <img src="data:image/png;base64,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" alt="터치 안내">
                    <span>먼저, 해당 <b>'동'</b>과 <b>'투표소'</b>를 선택하세요!</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

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


if workflow_step == "①[선택]투표소":
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
        dong_options = ["여기서 동을 선택하세요"] + dongs

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
                    '<div class="station-choice-label"><span class="star">★</span>동선택</div>',
                    unsafe_allow_html=True,
                )
                selected_dong_display = st.selectbox(
                    "동선택",
                    dong_options,
                    index=dong_index,
                    key="selected_dong_placeholder",
                    label_visibility="collapsed",
                )

            selected_dong = None if selected_dong_display == "여기서 동을 선택하세요" else selected_dong_display

            if selected_dong:
                stations = sorted(
                    [v["station"] for v in db.values() if v["dong"] == selected_dong],
                    key=station_number
                )
                station_options = ["여기서 투표소를 선택하세요"] + stations
            else:
                stations = []
                station_options = ["여기서 투표소를 선택하세요"]

            station_index = 0
            if saved_dong == selected_dong and saved_station in stations:
                station_index = station_options.index(saved_station)

            with c2:
                st.markdown(
                    '<div class="station-choice-label"><span class="star">★</span>투표소 선택</div>',
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
            None if selected_station_display == "여기서 투표소를 선택하세요"
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

elif workflow_step == "②[보고]투표진행상황":
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
        st.markdown('<div class="report-v41-headrow"><span class="report-v41-title">1.투표진행상황 보고(투표용지 교부수량 산출)</span></div>', unsafe_allow_html=True)
        st.warning("투표소가 선택되지 않았습니다. 먼저 ①[선택] 투표소에서 동과 투표소를 선택해 주세요.")
    else:
        station_display = f"{station['dong']} {station['station']}표소"

        if station["elections"]:
            report_elections = [station["elections"][0]]
            report_target_name = report_elections[0]["name"]
        else:
            report_elections = []
            report_target_name = "자료 없음"

        st.markdown(
            '<div class="report-v41-headrow"><span class="report-v41-title">1.투표진행상황 보고(투표용지 교부수량 산출)</span></div>',
            unsafe_allow_html=True,
        )

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
                    st.markdown('<div class="report-v41-label-blue">[보고]<br>교부수량</div>', unsafe_allow_html=True)
                    if invalid_input:
                        st.markdown('<div class="report-v41-value-blue" style="color:red; font-size:20px;">잘못된 입력</div>', unsafe_allow_html=True)
                    else:
                        st.markdown(f'<div class="report-v41-value-blue">{cumulative:,}매</div>', unsafe_allow_html=True)

                with c3:
                    st.markdown('<div class="report-v41-label-black"><br>잔여수량</div>', unsafe_allow_html=True)
                    if invalid_input:
                        st.markdown('<div class="report-v41-value-black" style="color:red; font-size:20px;">잘못된 입력</div>', unsafe_allow_html=True)
                    else:
                        st.markdown(f'<div class="report-v41-value-black">{remain:,}매</div>', unsafe_allow_html=True)

                st.markdown(
                    '<div class="report-v41-help">※ 보고대상 선거의 현재 남아 있는 '
                    '<span class="red">투표용지 첫 번호(NO.)를 [입력]란에 기재</span> 후 지금까지 '
                    '<span class="blue">교부된 투표용지 수량을 산출</span>하여 보고합니다.</div>',
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
        background-image: url('data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAM8AAAAeCAYAAACL40rVAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAA8YSURBVHhe7ZxrbBtXdsd/Q1IPynrYkizHY8qMLUu27CTOxgwcl0E3m7b7rexqhSKKuy3STdMUZbVbKERRFu0iLZBV0QpsAy+BzYcNtptCVVuoSoVsjGbbzWYRVvGGjR+K35bkEZlJbEmRLFkSRYkz/cDXcDSkhn5kbYA/YADxzszhnXvv/9xzzx1KUFVVpUSJEkVj0RfcbeLxOIqi6ItLlLjv+ELFs7Bwk48+Os3Y2IT+VIkS9x2mxaOqMD6zzORcTH/KFAsLC4x+fI7PZ+cYm7jK5StjqJQixhL3L6bFgwBrisoPf/Epb348xdKq+dBrfn6Bj06eJr4a54nDLlp2Pcjly2NcunSF0pKrxP2KUEzCYE1R+fG5aYY+vk6DvYxvHNrOlxw1+stymJub59Tp04DAowcfZvPmOlRF4dKVMcbGrrJ7l5O9e1sRBEF/a4kS9zRFiQdgeVXhlf+e4EcffsoWu43fPtjEs4e209Jg11/K3NwNTp46g9Ui8Oijj1BbW5s5p6gKY1cmuDI2jtO5k/Z9bSUBlbivsL788ssv6wsLUWYViCUUPozMc3JijvevzBGOzrO5sozWpiosKQF8/vksJ0+NYiuzrRMOgCAI1NdvQbAIjI9fJb66SmNDfUlAJe4bzK95NLgcdRxoqgYVVoH3L87y/Buj/PXxMWaXV4ktzHH69CjlFWU89ujD1NYYh3aCILCnZTdtrXuYlCKcPXeBRCKhv6xEiXuSosO2NEOjU/zOP51heXkV7GUQSwACv+vaynMtyzxQU87O1naqN1XpbzVkfELi4sVL7BC3s3//Pmw2m/6SEiXuKW5p5gF4um0rLz6xG2HVBnEF7BawCbzxvzKvfLBMXXOraeEA7N7lpH3fXqKyzNlzF1hdW9NfUqLEPUX+NY+yBPExWItAYg7UGKgroMyDskildZHHdlczs7yJUxNroFigTIEygYlplU8XFZ5q3UJVuVVvOS+bN9dRXl7O+PhVlpaWaWyox2o1f3+J+wxZRl5YoCZPWG+KO2BDlmUWbsFG/rBNWYLlMCy9hxo/D0ocQYmjqgkQQFAtUF3D9Mp2/vydJl4/cwB1rQEsKrAMsTjf/o1d9HW0YbMmJzh1cQllMoJycwHL1q1YHTvAIDyLRD/h0sXL1DfU09a6h01FzGBJZIb9PgYkcHb10esR9RdkkIf9+JIX0tfrIXulzHDwGCPRnMsL4zhCt1drQ4M8jN83gAS4e/rxuvSnU/XATU+/l8zpcBD/YP5KODp7M7Zu1QY4ONLtxSNCOHiUQIj17SEPEzw2Qn4rWRt56wGZdh0ISTmlON30dHtxpb7w1mw4cXd2400ZKWwjRTjI0eQD09XXi36oFLKxfuSmsVRBlRtsD0DsQ1g+iTr3zxC7hpAO9uah0Q7f/ZValjY/yb9ceQpmW2BpGwg2vv/+Jxxoa+CFplXiQz8m9u57JM6PgqWc8q95sHtfxNLUpPtiaHbsYG52jivjEzQ2NtyCeLJIA8fwj+hLNUi6DtASlQqeXs8RfUEWOUJRpjRIBSrh0BfkoZANCtc8Q1SSCj7DxjayTg2cON0OHEA0GkKSQgR8UcMBnEuY4NEAodQnp9utsSERCviIbuAwMw4iB4kB31EGMp+TYslvpZB4AAQrVLQhVLRBzdeh+qsw+xrMD4GgggDEoal8nr79bzNTNc07n7XD7G649igry9v4t9fDdEwMUPXufxJbWKD8V7+M/flvYj1wAKHaeJqcnIxyfWqaPXvbaNzaqD/9BSHi6e3Hoy82IOudzBGVZch0i4wsg6y7JoPLS3+/N7dMM4uZwsgGWq9rAtFDb79BaxRjIzyUEU6uSDpSopIYGArj0U/LGuThwZRw9Da8GVFIA0OEPfkHvtjsxu1O/p0UXfqME7c77Y6a896fxnzCwGJPikd8DUX8HjH1AIk4oAArIArQ98A5DtRPwI4wHPwPmirCPH48wuX/mSKxEqPqhRepHein4ve+ge3QlxCqcjdWFWDsE5mz4xNsc+ygvdmBfXYONbaSc10xOLu66e3tzXt0dzn1t9wVwieyA0yKZKUSDvrw+XwEihDf/Yosp4M+B2LOyBQR02M2Kud3JDnobYDYbK4vRY8X72GIhrTCAZAIhaLQ3IE3X/itwbx40lgbmbz5LB9c+y7Xyv8e6jvBthVWBB6uuMnLjZeotypgm2Hhsw8YtVzncuU+Yk93sOk7PizbH9BbBFVFWVomeuoM0Z/8lJ2Li7RFo/Dvg6xFogi2W08aSCNDBIPBvMfQyO0PWjmykY0wGu1AaJDh1AhJekE3bnP9fhvIDAf9+P1+gukvL4Q0wlAwyHDYxLUmEbMKQc4xK5PVlVhw0IquIySbKkTAn6yfLMuEh4McSzsg92Hj9U0aeRh/IIQEON099PX109/fR1+XOymgAR/BsP6m9RQtHmkywvlzZ6htfIiGlh4QfwjOn0DTX4Gtnc7NMzxTfwkmN7Es2Xl7i8ybtSpz7b+GsLke9eYi6vw8ytQ0a+cvsPLWcZb/to+55/6QhP87tLx1nAeH3mTt+Dsk6uuxPrTfMKlQGBHRkRqNUohQqMCx0bi/A4SD6RjdidNJMr4eSvaO6PHi9XrpOHJr6gkFkoLw+/3ZwZOPqIQkSQaL/vVePOmFQ4zcOe2Aq4PkRJ9cX/hTDsx/NLsO6uooOOxB9NDd404KSAoxEEjP3GkxdNFXIOwDCA+lQl5nF91eV+rZRUSPl55UOBcaHN5wBjQ9KlVVRZIinL9wEVHczoH9O7HZLEA12A+C/RHY8gcIi2/wx9Yf8dY7N4ksbkWxx/n5NoUPf/4L9nS9zc1NVSiLS6hzN1BnZ1FnZlGXYyBAndWCpa4O5bGDVDz7DOVf+TJYitY3AC5vL/0dZkMAko2nLyoWA68pD/tTi9NUjE5qvRIK4G8uvLA1R7FJjSyZMMppEN873XR1HkZMq6rYdZYhIp7ePsTgMQZDElIoOeABnE43nZpsWyFEl5fefi9yOIyMzIkTcPiwiCimhWASg/5Khn4SSBG0K1MjTIlHVVUmJiQuXrqMY4dIe/s+bOtCKQHKm6H8L3io+iscpp/I6jJU2ZipFPhodoZnfhZiTVhDsZSB1YJgtYKtDKFmE+ryMspKHGvrHipf+lPKjhzW2TePcTbFBO4e+jNeK7mQ3xg5E5I5m0VNg8uEg8cIhCTd4tZDbx/JgTjgwx/porNj4/g6h0zmLjd9apy4yKbc0yJLZyAzGThpgGOplGRWiM24XC7Dejmdbhzr0nwGAjRExOXtxeUl1cZiEQNem63LJXQr/R06QdjrygnxMiG4kUPRsaF4VFVlfPwqFy9fYWezg/3tbVgseuHkMpc4wsLmEVDPwEo5VKoolatY66rBIiBkct3AShz1xhzU1lHxtd+k8o9eoOzxQ1pzt0A6PMpFm651Gl2gIRz0FS1AacCHL5IWoJj0YM4uero9uR5V9NDbJzI8NMhAlCIGT5JM8sFEB4NRyl3/eeNUthZHp3fdPtXGFLlvlq8+DmdqzYPuOQz6PE9q3dXRhTM0gESIgB+6OjtwiTLhoUEGUk3r7kw6tEL+s6B44vE4V6VJJClKy64Had3TgqVAGBWLwWl5kR9c/S/eEz+AJyrgjEr1tWs8ee08idg0akUVNosFZXWVRDyOarNh3d9O5fPPUfn130LYtn7fp1hc3l7DBWNmRnL30LtB72vTmVqi6VDD6SaT1dTSnB3OLm8//TknNYguPF5XJhVeqJNyySYf0h1cGPMpd25n1jbDOhEXi4jH25t9lpyN5/RmsUw4leSQTwwiGS1qRQ+9PZFk0kAKMRAIafZ3nLi7uk05h4LiWVlZQZIiWCwWdu9+EEvqTQEt8TWFE9ISP72S4PSnUf5v8WdMlr0LdfPwZJyqXSLfmtrLVy8orE7JWNfWWIitQE0N1a0tVDx+CNvTT2F7+CG96dsiGQ/rytJeLyoTDuvTKSIuzfQgerys3xmRGU7tCziPdOA1s16RZcKp+E/MEwYVQyb54Oxio7V1DvIwwaEI0MzhDt1M+IWwXsRaZ5YNl5MYh6BZ5HybY3KYwYCJtVlm3RTkWDrztsHmqp71atBgt9tp39cGAox+fI6VlfX7LYIAsaUpLo29SvTm79PU8HccajzHk/YE32xp5wfPPYP/b75F9WuvIrz+GpN/6efSn72EGnyV6u/9I5Xf/pM7LhyQCQ8GCARyj0xfSAPrzgUG14vtjiAPpb5jkMJZXwdOp0HokUHWzApOurrNzDoa5EgqwzhS8DnFjh56enro6bx9od81wkF8Ph++wAiOrmR9O9KVFV109iTLukzk/0WxOfO3o8j4Of+7bRpk+VNGPz5Hff0WHnn4ABUVFTnnlbUZbtz4V26unWE1UcUq2yizH2Jr1X5qKpIVWgPOX5WIfHadttYWnA31lOVYubMYzTxGyCcGk+9I6d/lMsT8O3MZNnh3yhRymOCxQCqtnt9OofewbrseOdm2QiLXrjUM6qHB3MxjYMPss8jhlMMSEV3rM2uQ+1xFvXO40cyTRhS3c/CRh5idvcGZ0bPEYrn/Qcdia2BLw/M0b/sHdouvsFd8id1bfj0jnNXVVc6eGeWTi5fZv72JPXdZOKRCJJeZI+t47knkYT9HfUnhON099PUXGCx3E9FDZ+ZtjOR+Ud5Dd+svDTHdz1rhyAz7j3L0aOrQpN9DAU156igUOq6beRRFScZiGtKfpqamGT17jtqaGg7sb8dur9T886j1P58WUInH45y/cJHpqRn27mtjh7gdQRCM/+mUqiIIwhf6U+z8b1UbcTszj1n03lQmPBwG18brlEJesuh6mGoPYwrWQ8Ptzzxm0bZp8Vm/fLNoRjzxeJxo9BPmF24aZtQEQcBqsTDz+efM3ZinoX4LNTU1Bf91lAAsLi0xPT1DTU0tjY31KIqS9x5VVbHZbOzYIVJXW/OFiEgeDnJsJFr45wQZsg3vONJtLmGQ+o6hSJSoqQ7LvtpfLJlnwUFn7/pBW1Q9TLWHMRvVI02yPiTfJdM98EY2inqWu9SmGfFcvz6NJEkoKe9vhICAxWpBEAQSSgJVMRaBFkEQsFisyXsSa3mFQ0o8qqKytakR587m0k+xS9zTZMSTSCgIAoazjhGqYaB2+6iqmhGY2bqUKPHL4P8Bru5byxRg5ggAAAAASUVORK5CYII=') !important;
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
