import streamlit as st
import pandas as pd

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="91 Game Ultimate Predictor", layout="wide")

# Custom Styling
st.markdown("""
    <style>
    .metric-container {
        background-color: #ffffff;
        padding: 10px; border-radius: 8px; border: 1px solid #e0e0e0;
        text-align: center; box-shadow: 2px 2px 5px rgba(0,0,0,0.05);
    }
    .metric-label { font-size: 12px; font-weight: bold; color: #666; text-transform: uppercase; }
    .metric-value { font-size: 20px; font-weight: bold; color: #333; }

    /* ===== BUTTON STYLE UPDATED ===== */
    .stButton > button {
        height: 60px;
        font-size: 22px;
        font-weight: 900;
        border-radius: 8px;
        color: white;
    }

    /* Alternate Red / Green Colors */
    div[data-testid="column"] button[key="btn_0"] { background-color: red !important; }
    div[data-testid="column"] button[key="btn_1"] { background-color: green !important; }
    div[data-testid="column"] button[key="btn_2"] { background-color: red !important; }
    div[data-testid="column"] button[key="btn_3"] { background-color: green !important; }
    div[data-testid="column"] button[key="btn_4"] { background-color: red !important; }
    div[data-testid="column"] button[key="btn_5"] { background-color: green !important; }
    div[data-testid="column"] button[key="btn_6"] { background-color: red !important; }
    div[data-testid="column"] button[key="btn_7"] { background-color: green !important; }
    div[data-testid="column"] button[key="btn_8"] { background-color: red !important; }
    div[data-testid="column"] button[key="btn_9"] { background-color: green !important; }

    .box-container {
        padding: 15px; border-radius: 12px; text-align: center; color: white;
        font-weight: bold; min-height: 120px; display: flex; flex-direction: column;
        justify-content: center; margin-bottom: 10px;
    }
    .label-text { font-size: 13px; margin-bottom: 5px; opacity: 0.9; }
    .result-text { font-size: 28px; }
    .bg-big { background-color: #28a745; border: 2px solid #1e7e34; }
    .bg-small { background-color: #dc3545; border: 2px solid #bd2130; }
    .bg-wait { background-color: #ffc107; color: black; border: 2px solid #e0a800; }
    </style>
    """, unsafe_allow_html=True)

# --- FORMULAS ---
RULES_4 = {"BBSB": "B", "BSBB": "S"}
RULES_5 = {"BBSBS": "S", "BBSSS": "S"}
RULES_6 = {"SBBSBS": "B", "BBSBSS": "S"}
RULES_7 = {"SBBSBSS": "S"}

def get_bs(n):
    return "B" if int(n) >= 5 else "S"

# --- STATE INITIALIZATION ---
if 'history_data' not in st.session_state:
    st.session_state.history_data = []
if 'pattern_chain' not in st.session_state:
    st.session_state.pattern_chain = ""
if 'last_bs' not in st.session_state:
    st.session_state.last_bs = None
if 'stick_count' not in st.session_state:
    st.session_state.stick_count = 0

# --- PREDICTION LOGIC ---
def check_all_patterns(chain):
    res_4 = RULES_4.get(chain[-4:], "WAIT") if len(chain) >= 4 else "WAIT"
    res_5 = RULES_5.get(chain[-5:], "WAIT") if len(chain) >= 5 else "WAIT"
    res_6 = RULES_6.get(chain[-6:], "WAIT") if len(chain) >= 6 else "WAIT"
    res_7 = RULES_7.get(chain[-7:], "WAIT") if len(chain) >= 7 else "WAIT"
    return res_4, res_5, res_6, res_7

# --- METRICS CALCULATION ---
def calculate_metrics():
    if not st.session_state.history_data:
        return {"MAX_WIN": 0, "MAX_LOSS": 0, "WINS": 0, "LOSS": 0}
    
    df = pd.DataFrame(st.session_state.history_data)
    valid = df[df['4D Pred'] != "WAIT"]
    if valid.empty:
        return {"MAX_WIN": 0, "MAX_LOSS": 0, "WINS": 0, "LOSS": 0}
    
    wins = len(valid[valid['Result'] == "WIN ✅"])
    losses = len(valid[valid['Result'] == "LOSS ❌"])
    
    res_list = valid['Result'].tolist()
    max_w, max_l, cur_w, cur_l = 0, 0, 0, 0
    
    for r in res_list:
        if "WIN" in r:
            cur_w += 1
            cur_l = 0
            max_w = max(max_w, cur_w)
        else:
            cur_l += 1
            cur_w = 0
            max_l = max(max_l, cur_l)
            
    return {"MAX_WIN": max_w, "MAX_LOSS": max_l, "WINS": wins, "LOSS": losses}

# --- ACTION HANDLER ---
def handle_click(num):
    current_bs = get_bs(num)
    
    if st.session_state.last_bs == current_bs:
        st.session_state.stick_count += 1
    else:
        st.session_state.stick_count = 1
    
    p4, p5, p6, p7 = check_all_patterns(st.session_state.pattern_chain)
    
    status = "-"
    if p4 != "WAIT":
        status = "WIN ✅" if current_bs == p4 else "LOSS ❌"
    
    st.session_state.history_data.append({
        "Number": num,
        "B/S": current_bs,
        "Stick": st.session_state.stick_count,
        "4D Pred": p4,
        "5D Pred": p5,
        "6D Pred": p6,
        "7D Pred": p7,
        "Result": status
    })
    
    st.session_state.last_bs = current_bs
    st.session_state.pattern_chain += current_bs

# --- UI DISPLAY ---
st.title("🕹️ 91 Game Predictor + Dashboard")

# DASHBOARD
m = calculate_metrics()
db_cols = st.columns(4)

with db_cols[0]:
    st.markdown(f'<div class="metric-container"><div class="metric-label">MAX WIN</div><div class="metric-value">{m["MAX_WIN"]}</div></div>', unsafe_allow_html=True)
with db_cols[1]:
    st.markdown(f'<div class="metric-container"><div class="metric-label">MAX LOSS</div><div class="metric-value">{m["MAX_LOSS"]}</div></div>', unsafe_allow_html=True)
with db_cols[2]:
    st.markdown(f'<div class="metric-container"><div class="metric-label">WINS</div><div class="metric-value">{m["WINS"]}</div></div>', unsafe_allow_html=True)
with db_cols[3]:
    st.markdown(f'<div class="metric-container"><div class="metric-label">LOSS</div><div class="metric-value">{m["LOSS"]}</div></div>', unsafe_allow_html=True)

st.divider()

# PREDICTION BOXES
p4, p5, p6, p7 = check_all_patterns(st.session_state.pattern_chain)

def draw_box(label, result):
    style = "bg-big" if result == "B" else "bg-small" if result == "S" else "bg-wait"
    display_res = "BIG (B)" if result == "B" else "SMALL (S)" if result == "S" else "WAIT..."
    st.markdown(f'<div class="box-container {style}"><div class="label-text">{label}</div><div class="result-text">{display_res}</div></div>', unsafe_allow_html=True)

c1, c2, c3, c4 = st.columns(4)
with c1: draw_box("4 Digit Result", p4)
with c2: draw_box("5 Digit Result", p5)
with c3: draw_box("6 Digit Result", p6)
with c4: draw_box("7 Digit Result", p7)

st.divider()

# INPUT GRID
col_l, col_r = st.columns([1, 1])

with col_l:
    st.subheader("Click Number (0-9)")
    grid = [st.columns(5), st.columns(5)]
    for i in range(10):
        r, c = (0, i) if i < 5 else (1, i-5)
        if grid[r][c].button(str(i), key=f"btn_{i}"):
            handle_click(i)
            st.rerun()

with col_r:
    st.subheader("Session Status")
    st.info(f"**Current Chain:** `{st.session_state.pattern_chain[-20:]}`")
    
    col_del1, col_del2 = st.columns(2)
    
    with col_del1:
        if st.button("⬅️ Delete Last Entry", type="primary", use_container_width=True):
            if st.session_state.history_data:
                st.session_state.history_data.pop()
                st.session_state.pattern_chain = st.session_state.pattern_chain[:-1]
                
                if st.session_state.history_data:
                    last_entry = st.session_state.history_data[-1]
                    st.session_state.last_bs = last_entry["B/S"]
                    st.session_state.stick_count = last_entry["Stick"]
                else:
                    st.session_state.last_bs = None
                    st.session_state.stick_count = 0
                st.rerun()
    
    with col_del2:
        if st.button("🗑️ Reset All Data", type="secondary", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

st.divider()

# HISTORY LOG
st.subheader("📋 Game History Log")

if st.session_state.history_data:
    df = pd.DataFrame(st.session_state.history_data)
    st.table(df.iloc[::-1])
    st.download_button(
        "📥 Download Log CSV",
        data=df.to_csv(index=False).encode('utf-8'),
        file_name="91_predictor_log.csv"
    )
