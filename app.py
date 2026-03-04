import streamlit as st
import pandas as pd

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="91 Game Triple Predictor", layout="wide")

# Custom Styling
st.markdown("""
    <style>
    .stButton>button { height: 60px; font-size: 22px; font-weight: bold; border-radius: 8px; }
    .box-container {
        padding: 20px;
        border-radius: 15px;
        text-align: center;
        color: white;
        font-weight: bold;
        min-height: 150px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        margin-bottom: 20px;
    }
    .label-text { font-size: 18px; margin-bottom: 10px; opacity: 0.9; text-transform: uppercase; }
    .result-text { font-size: 38px; }
    .bg-big { background-color: #28a745; border: 2px solid #1e7e34; }
    .bg-small { background-color: #dc3545; border: 2px solid #bd2130; }
    .bg-wait { background-color: #ffc107; color: black; border: 2px solid #e0a800; }
    </style>
    """, unsafe_allow_html=True)

# --- FORMULA DEFINITIONS ---
RULES_4 = {"BBSB": "B", "BSBB": "S"}
RULES_5 = {"BBSBS": "S", "BBSSS": "S"}
RULES_6 = {"SBBSBS": "B", "BBSBSS": "S"}

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
def check_patterns(chain):
    res_4 = RULES_4.get(chain[-4:], "WAIT") if len(chain) >= 4 else "WAIT"
    res_5 = RULES_5.get(chain[-5:], "WAIT") if len(chain) >= 5 else "WAIT"
    res_6 = RULES_6.get(chain[-6:], "WAIT") if len(chain) >= 6 else "WAIT"
    return res_4, res_5, res_6

# --- ACTION HANDLER ---
def handle_click(num):
    current_bs = get_bs(num)
    
    # Stick Logic: =IF(A2=A1, B1+1, 1)
    if st.session_state.last_bs == current_bs:
        st.session_state.stick_count += 1
    else:
        st.session_state.stick_count = 1
    
    # Record history (Recording the state BEFORE this new input for prediction tracking)
    p4, p5, p6 = check_patterns(st.session_state.pattern_chain)
    
    st.session_state.history_data.append({
        "Number": num, 
        "B/S": current_bs, 
        "Stick": st.session_state.stick_count,
        "Pred 4D": p4,
        "Pred 5D": p5,
        "Pred 6D": p6
    })
    
    st.session_state.last_bs = current_bs
    st.session_state.pattern_chain += current_bs

# --- UI DISPLAY ---
st.title("📊 91 Game Triple-Box Predictor")

# Prediction Row: 3 Boxes
p4, p5, p6 = check_patterns(st.session_state.pattern_chain)

def draw_box(label, result):
    style = "bg-big" if result == "B" else "bg-small" if result == "S" else "bg-wait"
    display_res = "BIG (B)" if result == "B" else "SMALL (S)" if result == "S" else "WAIT..."
    st.markdown(f"""
        <div class="box-container {style}">
            <div class="label-text">{label}</div>
            <div class="result-text">{display_res}</div>
        </div>
    """, unsafe_allow_html=True)

c1, c2, c3 = st.columns(3)
with c1: draw_box("4 Digit Result", p4)
with c2: draw_box("5 Digit Result", p5)
with c3: draw_box("6 Digit Result", p6)

st.divider()

# Input Row
col_l, col_r = st.columns([1, 1])
with col_l:
    st.subheader("Click Latest Number (0-9)")
    grid = [st.columns(5), st.columns(5)]
    for i in range(10):
        r, c = (0, i) if i < 5 else (1, i-5)
        if grid[r][c].button(str(i), key=f"btn_{i}"):
            handle_click(i)
            st.rerun()

with col_r:
    st.subheader("Current Status")
    st.info(f"**Chain History:** `{st.session_state.pattern_chain[-15:]}`")
    st.write(f"**Current Stick:** `{st.session_state.stick_count}`")
    if st.button("🔄 Reset All Data"):
        for key in list(st.session_state.keys()): del st.session_state[key]
        st.rerun()

st.divider()
st.subheader("📋 Game History Log")
if st.session_state.history_data:
    df = pd.DataFrame(st.session_state.history_data)
    st.table(df.iloc[::-1])
    st.download_button("📥 Download Excel/CSV", data=df.to_csv(index=False).encode('utf-8'), file_name="91_triple_log.csv")
