import streamlit as st
import pandas as pd

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="91 Game Predictor Pro", layout="wide")

# Custom Styling for the UI
st.markdown("""
    <style>
    .metric-container {
        background-color: #ffffff;
        padding: 15px; border-radius: 10px; border: 1px solid #e0e0e0;
        text-align: center; box-shadow: 2px 2px 5px rgba(0,0,0,0.05);
    }
    .metric-value { font-size: 24px; font-weight: bold; color: #333; }
    .stButton>button { height: 60px; font-size: 22px; font-weight: bold; border-radius: 8px; }
    .predict-box { font-size: 35px; font-weight: bold; text-align: center; padding: 25px; border-radius: 12px; margin-bottom: 10px; }
    .formula-type { font-size: 16px; font-weight: normal; color: #f8f9fa; display: block; margin-bottom: 5px; opacity: 0.9; }
    </style>
    """, unsafe_allow_html=True)

# --- NEW FORMULA DEFINITIONS ---
# Priority is given to 6-digit, then 5-digit, then 4-digit
RULES = [
    # 6 Digit Patterns
    {"name": "6 Digit Result", "pattern": "SBBSBS", "results": ["B"]},
    {"name": "6 Digit Result", "pattern": "BBSBSS", "results": ["S"]},
    # 5 Digit Patterns
    {"name": "5 Digit Result", "pattern": "BBSBS",  "results": ["S"]},
    {"name": "5 Digit Result", "pattern": "BBSSS",  "results": ["S"]},
    # 4 Digit Patterns
    {"name": "4 Digit Result", "pattern": "BBSB",   "results": ["B"]},
    {"name": "4 Digit Result", "pattern": "BSBB",   "results": ["S"]}
]

def get_bs(n):
    return "B" if int(n) >= 5 else "S"

# --- STATE INITIALIZATION ---
if 'history_data' not in st.session_state:
    st.session_state.history_data = []
if 'next_prediction' not in st.session_state:
    st.session_state.next_prediction = "WAIT"
if 'active_formula' not in st.session_state:
    st.session_state.active_formula = "-"
if 'pattern_chain' not in st.session_state:
    st.session_state.pattern_chain = ""
if 'last_bs' not in st.session_state:
    st.session_state.last_bs = None
if 'stick_count' not in st.session_state:
    st.session_state.stick_count = 0

# --- METRICS ---
def calculate_metrics():
    if not st.session_state.history_data:
        return {"WINS": 0, "LOSS": 0, "WIN_RATE": 0.0}
    df = pd.DataFrame(st.session_state.history_data)
    valid = df[df['Result'] != "-"]
    wins = len(valid[valid['Result'] == "WIN ✅"])
    losses = len(valid[valid['Result'] == "LOSS ❌"])
    total = wins + losses
    win_rate = round(wins / total, 2) if total > 0 else 0.0
    return {"WINS": wins, "LOSS": losses, "WIN_RATE": win_rate}

# --- ACTION HANDLER ---
def handle_click(num):
    current_bs = get_bs(num)
    
    # Stick Logic: =IF(A2=A1, B1+1, 1)
    if st.session_state.last_bs == current_bs:
        st.session_state.stick_count += 1
    else:
        st.session_state.stick_count = 1
    
    # Win/Loss Check
    status = "-"
    if st.session_state.next_prediction != "WAIT":
        status = "WIN ✅" if current_bs == st.session_state.next_prediction else "LOSS ❌"
    
    # History Log
    st.session_state.history_data.append({
        "Number": num, 
        "B/S": current_bs, 
        "Stick": st.session_state.stick_count,
        "Formula Type": st.session_state.active_formula,
        "Prediction": st.session_state.next_prediction, 
        "Result": status
    })
    
    st.session_state.last_bs = current_bs
    st.session_state.pattern_chain += current_bs
    
    # Check Patterns (Longest first)
    found_pattern = False
    for rule in RULES:
        if st.session_state.pattern_chain.endswith(rule["pattern"]):
            st.session_state.next_prediction = rule["results"][0]
            st.session_state.active_formula = rule["name"]
            found_pattern = True
            break
    
    if not found_pattern:
        st.session_state.next_prediction = "WAIT"
        st.session_state.active_formula = "-"

# --- UI DISPLAY ---
st.title("🎲 91 Game: Pattern Matching System")

m = calculate_metrics()
c1, c2, c3, c4 = st.columns(4)
with c1: st.markdown(f'<div class="metric-container"><div class="metric-label">WINS</div><div class="metric-value">{m["WINS"]}</div></div>', unsafe_allow_html=True)
with c2: st.markdown(f'<div class="metric-container"><div class="metric-label">LOSS</div><div class="metric-value">{m["LOSS"]}</div></div>', unsafe_allow_html=True)
with c3: st.markdown(f'<div class="metric-container"><div class="metric-label">WIN RATE</div><div class="metric-value">{m["WIN_RATE"]}</div></div>', unsafe_allow_html=True)
with c4: st.markdown(f'<div class="metric-container"><div class="metric-label">STICK</div><div class="metric-value">{st.session_state.stick_count}</div></div>', unsafe_allow_html=True)

st.divider()

col_l, col_r = st.columns([1, 1])
with col_l:
    st.subheader("Click Number (0-9)")
    grid = [st.columns(5), st.columns(5)]
    for i in range(10):
        r, c = (0, i) if i < 5 else (1, i-5)
        if grid[r][c].button(str(i), key=f"btn_{i}"):
            handle_click(i); st.rerun()
    
    if st.button("🔄 Reset Data"):
        for key in st.session_state.keys(): del st.session_state[key]
        st.rerun()

with col_r:
    st.subheader("Prediction Window")
    p = st.session_state.next_prediction
    f_type = st.session_state.active_formula
    
    if p == "B":
        st.markdown(f'<div class="predict-box" style="background-color: #28a745; color: white;"><span class="formula-type">{f_type}</span>NEXT: BIG (B)</div>', unsafe_allow_html=True)
    elif p == "S":
        st.markdown(f'<div class="predict-box" style="background-color: #dc3545; color: white;"><span class="formula-type">{f_type}</span>NEXT: SMALL (S)</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="predict-box" style="background-color: #ffc107; color: black;"><span class="formula-type">NO PATTERN</span>WAIT...</div>', unsafe_allow_html=True)

st.divider()
st.subheader("📋 Game History Log")
if st.session_state.history_data:
    df = pd.DataFrame(st.session_state.history_data)
    st.table(df.iloc[::-1])
    st.download_button("📥 Download Log", data=df.to_csv(index=False).encode('utf-8'), file_name="91_predictor_log.csv")
