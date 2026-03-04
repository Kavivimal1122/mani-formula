import streamlit as st
import pandas as pd

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="91 Game 4-Step Predictor", layout="wide")

# Custom Styling for the Boxes
st.markdown("""
    <style>
    .stButton>button { height: 60px; font-size: 22px; font-weight: bold; border-radius: 8px; }
    .box-container {
        padding: 15px;
        border-radius: 12px;
        text-align: center;
        color: white;
        font-weight: bold;
        min-height: 130px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        margin-bottom: 10px;
    }
    .label-text { font-size: 14px; margin-bottom: 5px; opacity: 0.9; text-transform: uppercase; }
    .result-text { font-size: 30px; }
    .bg-big { background-color: #28a745; border: 2px solid #1e7e34; }
    .bg-small { background-color: #dc3545; border: 2px solid #bd2130; }
    .bg-wait { background-color: #ffc107; color: black; border: 2px solid #e0a800; }
    </style>
    """, unsafe_allow_html=True)

# --- YOUR UPDATED FORMULAS ---
RULES_4 = {"BBSB": "B", "BSBB": "S"}
RULES_5 = {"BBSBS": "S", "BBSSS": "S"}
RULES_6 = {"SBBSBS": "B", "BBSBSS": "S"}
RULES_7 = {"SBBSBSS": "S"}  # Added 7-Digit formula

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

# --- ACTION HANDLER ---
def handle_click(num):
    current_bs = get_bs(num)
    
    # Stick Logic: =IF(A2=A1, B1+1, 1)
    if st.session_state.last_bs == current_bs:
        st.session_state.stick_count += 1
    else:
        st.session_state.stick_count = 1
    
    # Capture predictions BEFORE the new input for history logging
    p4, p5, p6, p7 = check_all_patterns(st.session_state.pattern_chain)
    
    st.session_state.history_data.append({
        "Number": num, 
        "B/S": current_bs, 
        "Stick": st.session_state.stick_count,
        "4D Pred": p4,
        "5D Pred": p5,
        "6D Pred": p6,
        "7D Pred": p7
    })
    
    st.session_state.last_bs = current_bs
    st.session_state.pattern_chain += current_bs

# --- UI DISPLAY ---
st.title("🎲 91 Game: 4-Step Pattern Predictor")

# Prediction Row: 4 Boxes side-by-side
p4, p5, p6, p7 = check_all_patterns(st.session_state.pattern_chain)

def draw_box(label, result):
    style = "bg-big" if result == "B" else "bg-small" if result == "S" else "bg-wait"
    display_res = "BIG (B)" if result == "B" else "SMALL (S)" if result == "S" else "WAIT..."
    st.markdown(f"""
        <div class="box-container {style}">
            <div class="label-text">{label}</div>
            <div class="result-text">{display_res}</div>
        </div>
    """, unsafe_allow_html=True)

c1, c2, c3, c4 = st.columns(4)
with c1: draw_box("4 Digit Result", p4)
with c2: draw_box("5 Digit Result", p5)
with c3: draw_box("6 Digit Result", p6)
with c4: draw_box("7 Digit Result", p7)

st.divider()

# Input Row
col_l, col_r = st.columns([1, 1])
with col_l:
    st.subheader("Click Latest Number (0-9)")
    grid = [st.columns(5), st.columns(5)]
    for i in range(10):
        r, col = (0, i) if i < 5 else (1, i-5)
        if grid[r][col].button(str(i), key=f"btn_{i}"):
            handle_click(i)
            st.rerun()

with col_r:
    st.subheader("Dashboard")
    st.info(f"**Current Chain:** `{st.session_state.pattern_chain[-20:]}`")
    st.write(f"**Current Stick:** `{st.session_state.stick_count}`")
    if st.button("🗑️ Reset All Data"):
        for key in list(st.session_state.keys()): del st.session_state[key]
        st.rerun()

st.divider()
st.subheader("📋 Game History Log")
if st.session_state.history_data:
    df = pd.DataFrame(st.session_state.history_data)
    # Latest result at the top
    st.table(df.iloc[::-1])
    
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Download Log CSV", data=csv, file_name="91_game_4step_log.csv")
else:
    st.info("Start clicking numbers to see predictions and history.")
