
import streamlit as st
import json
import re
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path
from datetime import datetime
from io import BytesIO

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
   모바일 전용 v2.2
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
   모바일 v2.2 - 상단 진행단계 가독성 개선
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


/* v2.2 - ④ 투표록 참고표 숫자 가독성 */
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

/* v2.2 상단 제목 잘림 방지 + 진행 안내문 */
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
    content: "②[보고자료]";
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
    content: "④[참고]";
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
    content:"②[보고자료]";
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
    content:"④[참고]";
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
    content: "②[보고자료]" !important; color:#7b159d !important; font-size:20px !important; font-weight:900 !important;
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
    content: "④[참고]" !important; color:#7b159d !important; font-size:20px !important; font-weight:900 !important;
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
div[data-testid="stRadio"] label:nth-of-type(2) > div:last-child::before {content:"②[보고자료]"; color:#7b159d; font-size:20px; font-weight:900;}
div[data-testid="stRadio"] label:nth-of-type(2) > div:last-child::after  {content:" 투표진행상황"; color:#111; font-size:20px; font-weight:800;}
div[data-testid="stRadio"] label:nth-of-type(3) > div:last-child::before {content:"③[입력]"; color:#7b159d; font-size:20px; font-weight:900;}
div[data-testid="stRadio"] label:nth-of-type(3) > div:last-child::after  {content:" 투표록 기초자료"; color:#111; font-size:20px; font-weight:800;}
div[data-testid="stRadio"] label:nth-of-type(4) > div:last-child::before {content:"④[참고]"; color:#7b159d; font-size:20px; font-weight:900;}
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
    }
    return mapping.get(name, name if name.endswith("선거") else name + "선거")

def parse_uploaded_xlsx(file_bytes):
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
            dong, station, registered, received, start_no, end_no = row

            if str(dong).strip():
                current_dong = str(dong).strip()

            station_text = str(station).strip()
            # Actual polling-station rows normally contain "제...투".
            if not current_dong or not station_text or "투" not in station_text:
                continue

            try:
                reg = _to_int(registered)
                rec = _to_int(received)
                start = _to_int(start_no)
                end = _to_int(end_no)
            except Exception:
                continue

            if rec <= 0 or end < start:
                continue

            key = f"{current_dong}|{station_text}"
            ent = station_db.setdefault(
                key,
                {"dong": current_dong, "station": station_text, "registered": reg, "elections": []}
            )
            ent["registered"] = reg

            ent["elections"].append({
                "name": election_name,
                "received": rec,
                "start_no": start,
                "end_no": end,
            })
            parsed_count += 1

    if not station_db:
        raise ValueError(
            "읽을 수 있는 투표소 자료를 찾지 못했습니다. "
            "엑셀의 A~F열이 '동위원회명 / 투표소명 / 선거인명부 등재자수 / 수령매수 / 시작 No. / 끝 No.' 형식인지 확인해 주세요."
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


if "app_authenticated" not in st.session_state:
    st.session_state.app_authenticated = False

if not st.session_state.app_authenticated:
    st.markdown(
        """
        <div style="max-width:520px; margin:80px auto 20px auto; text-align:center;">
            <div style="font-size:34px; font-weight:900; margin-bottom:10px;">🗳️ 투표록 작성 보조 앱</div>
            <div style="font-size:18px; color:#666; margin-bottom:24px;">앱을 사용하려면 비밀번호를 입력해 주세요.</div>
        </div>
        """,
        unsafe_allow_html=True
    )
    access_pw = st.text_input("앱 비밀번호", type="password", key="app_access_password_input")
    if st.button("🔐 앱 열기", width="stretch"):
        if access_pw == current_app_access_password():
            st.session_state.app_authenticated = True
            st.rerun()
        else:
            st.error("비밀번호가 올바르지 않습니다.")
    st.info("초기 앱 비밀번호는 1234입니다.")
    st.stop()

# ============================================================
# v2.9 상단/메뉴: HTML 링크 카드 방식
# ============================================================
st.markdown(
    '<div class="app-main-title-v29">🗳️ 투표록 작성 보조 앱 — 모바일 전용 v2.9</div>',
    unsafe_allow_html=True
)
st.markdown(
    '<div class="workflow-guide">★ 반드시 '
    '<span class="first-step">①해당 투표소를 먼저 선택</span>하시고 '
    '<span class="next-steps">②~④ 순서대로 진행</span>하시기 바랍니다. ★</div>',
    unsafe_allow_html=True
)

WORKFLOW_LABELS = {
    "select": "①[선택]투표소",
    "report": "②[보고자료]투표진행상황",
    "input": "③[입력]투표록 기초자료",
    "reference": "④[참고] 투표록 2p 작성",
    "admin": "[관리자]",
}

# URL 쿼리 파라미터로 메뉴 상태를 관리합니다.
# Streamlit 내부 radio/button DOM에 의존하지 않아 실제 화면과 CSS가 달라지는 문제를 방지합니다.
try:
    requested_step = st.query_params.get("step", "select")
except Exception:
    requested_step = "select"
if isinstance(requested_step, list):
    requested_step = requested_step[0] if requested_step else "select"
if requested_step not in WORKFLOW_LABELS:
    requested_step = "select"
workflow_step = WORKFLOW_LABELS[requested_step]

def _nav_card(step, lead, tail, admin=False):
    selected = " selected" if requested_step == step else ""
    admin_cls = " admin" if admin else ""
    dot = '<span class="dot">●</span>' if requested_step == step else '<span class="dot">○</span>'
    return (
        f'<a class="workflow-card{admin_cls}{selected}" href="?step={step}" target="_self">'
        f'{dot}<span class="menu-text">'
        f'<span class="purple">{lead}</span>'
        f'<span class="black">{tail}</span>'
        f'</span></a>'
    )

nav_html = (
    '<div class="workflow-nav">'
    + _nav_card("select", "①[선택]", " 투표소")
    + '<div class="workflow-arrow">➜</div>'
    + _nav_card("report", "②[보고자료]", " 투표진행상황")
    + '<div class="workflow-arrow">➜</div>'
    + _nav_card("input", "③[입력]", " 투표록 기초자료")
    + '<div class="workflow-arrow">➜</div>'
    + _nav_card("reference", "④[참고]", " 투표록 2p 작성")
    + '</div>'
    + '<div class="workflow-admin-row">'
    + _nav_card("admin", "", "[관리자]", admin=True)
    + '</div>'
)
st.markdown(nav_html, unsafe_allow_html=True)

# ------------------------------------------------------------
# Current station / hourly state helpers
# ------------------------------------------------------------
selected_key = local.get("selected_key")
station = db.get(selected_key) if selected_key and selected_key in db else None

hourly_by_station = local.setdefault("hourly_by_station", {})
hourly = hourly_by_station.setdefault(selected_key, []) if selected_key else []

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

# ============================================================
# 2. Station selection
# ============================================================


if workflow_step == "①[선택]투표소":
    st.markdown(
        '<div class="section-box station-select-title">투표소 선택</div>',
        unsafe_allow_html=True
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
        dong_options = ["여기서 동을 선택하세요"] + dongs

        saved_selected_key = local.get("selected_key")
        saved_dong = None
        saved_station = None
        if saved_selected_key and saved_selected_key in db:
            saved_dong = db[saved_selected_key]["dong"]
            saved_station = db[saved_selected_key]["station"]

        dong_index = 0
        if saved_dong in dongs:
            dong_index = dong_options.index(saved_dong)

        c1, c2 = st.columns(2)
        with c1:
            selected_dong_display = st.selectbox(
                "동선택",
                dong_options,
                index=dong_index,
                key="selected_dong_placeholder"
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
            selected_station_display = st.selectbox(
                "투표소 선택",
                station_options,
                index=station_index,
                key=f"selected_station_placeholder_{selected_dong or 'none'}"
            )

        selected_station = (
            None if selected_station_display == "여기서 투표소를 선택하세요"
            else selected_station_display
        )

    # 선택 전에는 빈 괄호 안내, 동과 투표소 모두 선택 후에만 실제 투표소 표시
    if selected_dong and selected_station:
        selected_key = f"{selected_dong}|{selected_station}"
        station = db[selected_key]
        local["selected_key"] = selected_key
        save_local()

        hourly_by_station = local.setdefault("hourly_by_station", {})
        hourly = hourly_by_station.setdefault(selected_key, [])

        st.markdown(
            f'<div class="selected-station-confirm"><span class="arrow">➜</span>'
            f'선택한 투표소는 <span class="selected-name">({station["dong"]} {station["station"]}표소)</span> 입니다</div>',
            unsafe_allow_html=True
        )
    else:
        # 아직 새 선택을 하지 않았으면 기존 저장된 투표소 선택을 유지
        saved_selected_key = local.get("selected_key")
        if saved_selected_key and saved_selected_key in db:
            selected_key = saved_selected_key
            station = db[saved_selected_key]
            hourly_by_station = local.setdefault("hourly_by_station", {})
            hourly = hourly_by_station.setdefault(selected_key, [])
            st.markdown(
                f'<div class="selected-station-confirm"><span class="arrow">➜</span>'
                f'선택한 투표소는 <span class="selected-name">({station["dong"]} {station["station"]}표소)</span> 입니다</div>',
                unsafe_allow_html=True
            )
        else:
            selected_key = None
            station = None
            hourly = []
            st.markdown(
                '<div class="selected-station-confirm"><span class="arrow">➜</span>'
                '선택한 투표소는 <span class="selected-name">(<span style="display:inline-block; min-width:190px; border-bottom:2px solid #7b159d; line-height:1.05;">&nbsp;</span>)</span> 입니다</div>',
                unsafe_allow_html=True
            )

elif workflow_step == "②[보고자료]투표진행상황":
    st.markdown(
        '<div class="progress-title-row"><span class="progress-title-box">1. 투표진행상황 보고</span></div>',
        unsafe_allow_html=True
    )

    if not db or station is None:
        st.warning("투표소가 선택되지 않았습니다. 먼저 ① 투표소 선택에서 동과 투표소를 선택해 주세요.")
    else:
        station_display = f"{station['dong']} {station['station']}표소"
        st.markdown(
            f'<div class="progress-station">'
            f'<span class="station-purple" style="text-decoration:underline; text-underline-offset:4px;">{station_display}</span>'
            f'<span class="station-black"> · 선거인명부 등재자수 {station["registered"]:,}명</span>'
            f'</div>',
            unsafe_allow_html=True
        )

        if station["elections"]:
            report_elections = [station["elections"][0]]
            st.info(
                f"보고대상 선거: **{report_elections[0]['name']}** "
                "(업로드한 엑셀의 첫 번째 탭)"
            )
        else:
            report_elections = []
            st.warning("보고대상 선거 자료가 없습니다.")

        errors = []
        # 실제 Streamlit 컨테이너를 사용하여 제목/입력/산출/안내 전체가 하나의 네모박스 안에 들어가게 합니다.
        with st.container(border=True, key="report_input_calc_box"):
            st.markdown(
                '<div class="input-calc-title">[ 보고용 투표용지 교부수량 입력 / 산출 ]</div>',
                unsafe_allow_html=True
            )

            for i, e in enumerate(report_elections):
                c1, c2, c3 = st.columns([1.25, 1, 1])

                with c1:
                    st.markdown(
                        '<div class="metric-label-red">현재 잔여투표용지 첫 번호(NO.)</div>',
                        unsafe_allow_html=True
                    )
                    raw = st.text_input(
                        "현재 잔여투표용지 첫 번호(NO.)",
                        value="",
                        placeholder="여기에 입력하세요",
                        key=f"cur_text_{selected_key}_{i}",
                        label_visibility="collapsed"
                    )

                n = None
                if raw.strip():
                    try:
                        n = int(raw.replace(",", "").strip())
                    except Exception:
                        errors.append(f"{e['name']}: 숫자만 입력해 주세요.")

                cumulative = 0
                remain = e["received"]
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
                        st.markdown(
                            '<div class="metric-label-blue" style="color:blue;">[보고대상]교부수량</div>'
                            '<div class="progress-value-blue" style="color:red;">잘못된 입력</div>',
                            unsafe_allow_html=True
                        )
                    else:
                        st.markdown(
                            '<div class="metric-label-blue" style="color:blue;">[보고대상]교부수량</div>'
                            f'<div class="progress-value-blue">{cumulative:,}매</div>',
                            unsafe_allow_html=True
                        )

                with c3:
                    if invalid_input:
                        st.markdown(
                            '<div class="metric-label-black">잔여수량</div>'
                            '<div class="progress-value-black" style="color:red;">잘못된 입력</div>',
                            unsafe_allow_html=True
                        )
                    else:
                        st.markdown(
                            '<div class="metric-label-black">잔여수량</div>'
                            f'<div class="progress-value-black">{remain:,}매</div>',
                            unsafe_allow_html=True
                        )

                st.markdown(
                    '<div class="inbox-help">➡ 보고 대상 선거의 현재 '
                    '<span style="color:red;">남아 있는 투표용지 첫 번호(NO.)만</span> 입력합니다.</div>',
                    unsafe_allow_html=True
                )

            if errors:
                st.error("\n\n".join("• " + x for x in errors))

        st.markdown(
            '<div class="notice-left">★ <span style="color:blue;">투표관리관</span>은 매 35분까지 '
            '<span style="color:blue;">투표용지 교부수량</span>을 '
            '<span style="color:blue;">보고</span>합니다. ★</div>',
            unsafe_allow_html=True
        )

        st.markdown('<div class="two-line-gap"></div>', unsafe_allow_html=True)

        st.markdown(
            '<div class="reference-title-box"><span class="reference-big">2. 참고</span>'
            '<span class="reference-rest"> - 투표소에 배부된 투표용지 일련번호</span></div>',
            unsafe_allow_html=True
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
            """
            <table class="reference-table">
              <thead>
                <tr>
                  <th>선거명</th>
                  <th>수령매수</th>
                  <th>시작 No.</th>
                  <th>끝 No.</th>
                </tr>
              </thead>
              <tbody>
            """ + "".join(ref_rows) + """
              </tbody>
            </table>
            """,
            unsafe_allow_html=True
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
        station_display = f"{station['dong']} {station['station']}표소"
        st.markdown(
            f'<div class="polling-name-banner"><span class="name">({station_display})</span></div>',
            unsafe_allow_html=True
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

        # ----------------------------------------------------
        # 자. 투표용지 수령·교부상황 계산 — 먼저 입력
        # ----------------------------------------------------
        st.markdown("### 자. 투표용지 수령·교부상황 계산")
        st.caption(
            "각 선거별로 남아있는 잔여투표용지 첫 번호, 훼손 등 미교부 매수 및 "
            "훼손 등 미교부 일련번호를 입력하면 교부매수·잔여매수·잔여투표용지 일련번호가 자동 계산됩니다."
        )

        st.markdown(
            """
            <div class="entry-table-header j-grid-v20">
              <div>선거명</div>
              <div>(남아있는)<br>잔여투표용지 첫 번호(NO.)</div>
              <div>훼손 등 미교부한<br>투표용지 매수</div>
              <div>훼손 등 미교부한<br>투표용지 일련번호</div>
              <div>교부매수</div>
              <div>잔여매수</div>
              <div>잔여투표용지<br>일련번호</div>
            </div>
            """,
            unsafe_allow_html=True
        )

        j_rows = []
        for idx, e in enumerate(station["elections"]):
            start_no = int(e["start_no"])
            end_no = int(e["end_no"])
            received = int(e["received"])

            cols = st.columns([1.2, 1.2, 1.1, 1.35, 1.0, 1.0, 1.45], gap="small")

            with cols[0]:
                st.markdown(f'<div class="entry-static">{e["name"]}</div>', unsafe_allow_html=True)

            with cols[1]:
                first_raw = st.text_input(
                    "잔여투표용지 첫 번호(NO.)",
                    value=format_numeric_text(saved_j.get(str(idx), {}).get("first_raw", "")),
                    placeholder="입력",
                    key=f"j_first_{selected_key}_{idx}",
                    label_visibility="collapsed"
                )

            with cols[2]:
                damaged_raw = st.text_input(
                    "훼손 등 미교부한 투표용지 매수",
                    value=format_numeric_text(saved_j.get(str(idx), {}).get("damaged_raw", "")),
                    placeholder="입력",
                    key=f"j_damaged_{selected_key}_{idx}",
                    label_visibility="collapsed"
                )

            with cols[3]:
                damaged_serial = st.text_input(
                    "훼손 등 미교부한 투표용지 일련번호",
                    value=str(saved_j.get(str(idx), {}).get("damaged_serial", "")),
                    placeholder="예: 1502, 1503, 1505",
                    key=f"j_damaged_serial_{selected_key}_{idx}",
                    label_visibility="collapsed"
                )

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
                    # 교부매수 = 첫 잔여번호 이전까지 진행된 일련번호 수 - 훼손 등 미교부 매수
                    issued = serial_consumed - damaged

                    # 핵심 수정: 잔여매수 = 수령매수 - 교부매수
                    remaining = received - issued

                    if remaining <= 0:
                        remaining_serial = "잔여 없음"
                    elif first_remaining <= end_no:
                        remaining_serial = f"No. {first_remaining:,} ~ No. {end_no:,}"
                    else:
                        remaining_serial = "잔여 없음"

            with cols[4]:
                st.markdown(
                    f'<div class="entry-static">{"입력" if issued is None else f"{issued:,}"}</div>',
                    unsafe_allow_html=True
                )

            with cols[5]:
                st.markdown(
                    f'<div class="entry-static">{"입력" if remaining is None else f"{remaining:,}"}</div>',
                    unsafe_allow_html=True
                )

            with cols[6]:
                st.markdown(
                    f'<div class="entry-static serial-cell">{remaining_serial}</div>',
                    unsafe_allow_html=True
                )

            if calc_error:
                st.error(f"{e['name']}: {calc_error}")

            j_rows.append({
                "name": e["name"],
                "received": received,
                "issued": int(issued or 0),
                "remaining": int(remaining if remaining is not None else received),
                "first_remaining": first_remaining,
                "damaged": int(damaged_count or 0),
                "damaged_serial": str(damaged_serial or "").strip(),
                "remaining_serial": remaining_serial,
                "start_no": start_no,
                "end_no": end_no,
                "valid": issued is not None and remaining is not None and calc_error is None,
            })

            saved_j[str(idx)] = {
                "first_raw": str(first_raw),
                "damaged_raw": str(damaged_raw),
                "damaged_serial": str(damaged_serial or "").strip(),
            }

        st.markdown('<div class="section-gap"></div>', unsafe_allow_html=True)

        # ----------------------------------------------------
        # 아. 투표상황 — 자의 교부매수 연동
        # ----------------------------------------------------
        st.markdown("### 아. 투표상황")
        st.caption(
            "거소투표용지 미발송·반송자(2), 결정서 지참자(3), "
            "거소투표용지와 회송용봉투 반납자(4)를 입력하면 "
            "선거인명부 등재자(1)와 계(나)가 자동 계산됩니다."
        )

        st.markdown(
            """
            <div class="entry-table-header a-grid-v20">
              <div>선거명</div>
              <div>선거인명부 등재자수<br>(사전투표자수·거소투표신고인수 제외)<br>(가)</div>
              <div>선거인명부 등재자<br>(1)</div>
              <div>거소투표용지 미발송·반송자<br>(2)</div>
              <div>결정서 지참자<br>(3)</div>
              <div>거소투표용지와 회송용봉투 반납자<br>(4)</div>
              <div>계(나)<br>(1+2+3+4)</div>
            </div>
            """,
            unsafe_allow_html=True
        )

        a_rows = []
        for idx, e in enumerate(station["elections"]):
            issued_from_j = int(j_rows[idx]["issued"]) if idx < len(j_rows) and j_rows[idx]["valid"] else None

            cols = st.columns([1.35, 1.35, 1.1, 1.1, 1.1, 1.2, 1.0], gap="small")

            with cols[0]:
                st.markdown(f'<div class="entry-static">{e["name"]}</div>', unsafe_allow_html=True)

            with cols[1]:
                st.markdown(
                    f'<div class="entry-static">{int(station["registered"]):,}</div>',
                    unsafe_allow_html=True
                )

            with cols[3]:
                raw2 = st.text_input(
                    "거소투표용지 미발송·반송자 (2)",
                    value=format_numeric_text(saved_a.get(str(idx), {}).get("v2_raw", "")),
                    placeholder="입력",
                    key=f"a2_{selected_key}_{idx}",
                    label_visibility="collapsed"
                )
                v2 = parse_optional_int(raw2)

            with cols[4]:
                raw3 = st.text_input(
                    "결정서 지참자 (3)",
                    value=format_numeric_text(saved_a.get(str(idx), {}).get("v3_raw", "")),
                    placeholder="입력",
                    key=f"a3_{selected_key}_{idx}",
                    label_visibility="collapsed"
                )
                v3 = parse_optional_int(raw3)

            with cols[5]:
                raw4 = st.text_input(
                    "거소투표용지와 회송용봉투 반납자 (4)",
                    value=format_numeric_text(saved_a.get(str(idx), {}).get("v4_raw", "")),
                    placeholder="입력",
                    key=f"a4_{selected_key}_{idx}",
                    label_visibility="collapsed"
                )
                v4 = parse_optional_int(raw4)

            manual_inputs_complete = all(v is not None for v in (v2, v3, v4))
            v1 = None
            total_a = None

            if issued_from_j is not None and manual_inputs_complete:
                other_sum = int(v2) + int(v3) + int(v4)
                v1 = issued_from_j - other_sum
                if v1 < 0:
                    st.error(f"{e['name']}: (2)+(3)+(4)가 교부매수보다 큽니다.")
                    v1 = None
                    total_a = None
                else:
                    total_a = v1 + int(v2) + int(v3) + int(v4)

            with cols[2]:
                st.markdown(
                    f'<div class="entry-static">{"입력" if v1 is None else f"{v1:,}"}</div>',
                    unsafe_allow_html=True
                )

            with cols[6]:
                st.markdown(
                    f'<div class="entry-static">{"입력" if total_a is None else f"{total_a:,}"}</div>',
                    unsafe_allow_html=True
                )

            a_rows.append({
                "name": e["name"],
                "registered": int(station["registered"]),
                "v1": int(v1 or 0),
                "v2": int(v2 or 0),
                "v3": int(v3 or 0),
                "v4": int(v4 or 0),
                "total": int(total_a or 0),
                "has_input": total_a is not None,
            })

            saved_a[str(idx)] = {
                "v2_raw": str(raw2),
                "v3_raw": str(raw3),
                "v4_raw": str(raw4),
            }

        st.session_state[f"record_a_rows_{selected_key}"] = a_rows
        st.session_state[f"record_j_rows_{selected_key}"] = j_rows

        station_store["a_rows"] = a_rows
        station_store["j_rows"] = j_rows
        save_local()

        st.info(
            "※ 자의 교부매수와 아의 계(나)는 자동으로 연결됩니다. "
            "실제 투표록 기재 전 반드시 원자료와 대조하십시오."
        )

elif workflow_step == "④[참고] 투표록 2p 작성":
    if not db:
        st.warning("기초자료가 없습니다. [관리자] 메뉴에서 엑셀자료를 업로드해 주세요.")
    elif station is None:
        st.warning("먼저 ① 투표소 선택에서 동과 투표소를 선택해 주세요.")
    else:
        station_display = f"{station['dong']} {station['station']}표소"
        st.markdown(
            f'<div class="polling-name-banner"><span class="name">({station_display})</span></div>',
            unsafe_allow_html=True
        )

        saved_station_record = local.get("record_inputs_by_station", {}).get(selected_key, {})
        a_saved = st.session_state.get(
            f"record_a_rows_{selected_key}",
            saved_station_record.get("a_rows", [])
        )
        j_saved = st.session_state.get(
            f"record_j_rows_{selected_key}",
            saved_station_record.get("j_rows", [])
        )

        st.markdown('<div class="record-section">', unsafe_allow_html=True)
        st.markdown('<div class="record-title">아. 투표상황</div>', unsafe_allow_html=True)

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
            <table class="record-table">
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
        st.markdown('<div class="record-title">자. 투표용지 수령·교부상황</div>', unsafe_allow_html=True)

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

        st.markdown("### 아·자 수량 일치 검증")
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
            "선거 전에 제공되는 엑셀 파일을 업로드하면 해당 엑셀에서 "
            "**동위원회명, 투표소명, 선거인명부 등재자수, 투표용지 수령매수, 시작 No., 끝 No.**를 자동으로 불러옵니다."
        )
        st.info("※ 엑셀의 '비고' 열은 앱에서 읽거나 표시하지 않습니다.")

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
