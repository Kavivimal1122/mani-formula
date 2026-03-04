import streamlit as st
import pandas as pd

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="91 Game Predictor Pro", layout="wide")

# Custom Styling
st.markdown("""
    <style>
    .metric-container {
        background-color: #ffffff;
        padding: 15px; border-radius: 10px; border: 1px solid #e0e0e0;
        text-align: center; box-shadow: 2px 2px 5px rgba(0,0,0,0.05);
    }
    .metric-label { font-size: 14px; font-weight: bold; color: #666; }
    .metric-value { font-size: 24px; font-weight: bold; color: #333; }
    .stButton>button { height: 60px; font-size: 22px; font-weight: bold; border-radius: 8px; }
    .predict-box { font-size: 40px; font-weight: bold; text-align: center; padding: 20px; border-radius: 12px; }
    .formula-badge { font-size: 18px; font-weight: normal; color: #eee; display: block; margin-top: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- RULE DEFINITIONS WITH NAMES ---
# Longest patterns first for priority matching
RULES = [
    {"name": "3rd FOR", "pattern": "SBBSBS", "results": ["B", "S"]},
    {"name": "2nd FOR", "pattern": "BBSSS",  "results": ["S"]},
    {"name": "1st FOR", "pattern": "BBSB",   "results": ["B", "S"]},
    {"name": "4th FOR", "pattern": "BSBB",   "results": ["S"]}
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
if 'pending_steps' not in st.session_state:
    st.session_state.pending_steps = []

# --- METRICS ---
def calculate_metrics():
    if not st.session_state.history_data:
        return {"MAX_WIN": 0, "MAX_LOSS": 0, "WINS": 0, "LOSS": 0, "WIN_RATE": 0.0}
    df = pd.DataFrame(st.session_state.history_data)
    valid = df[df['Result'] != "-"]
    wins = len(valid[valid['Result'] == "WIN ✅"])
    losses = len(valid[valid['Result'] == "LOSS ❌"])
    total = wins + losses
    win_rate = round(wins / total, 2) if total > 0 else 0.0
    return {"MAX_WIN": 0, "MAX_LOSS": 0, "WINS": wins, "LOSS": losses, "WIN_RATE": win_rate}

# --- ACTION HANDLER ---
def handle_click(num):
    current_bs = get_bs(num)
    
    # Stick Logic: =IF(A2=A1, B1+1, 1)
    if st.session_state.last_bs == current_bs:
        st.session_state.stick_count += 1
    else:
        st.session_state.stick_count = 1
    
    # Check Win/Loss
    status = "-"
    if st.session_state.next_prediction != "WAIT":
        status = "WIN ✅" if current_bs == st.session_state.next_prediction else "LOSS ❌"
    
    # Save to history including Formula Name
    st.session_state.history_data.append({
        "Number": num, 
        "B/S": current_bs, 
        "Stick": st.session_state.stick_count,
        "Formula": st.session_state.active_formula,
        "Prediction": st.session_state.next_prediction, 
        "Result": status
    })
    
    st.session_state.last_bs = current_bs
    st.session_state.pattern_chain += current_bs
    
    # --- MULTI-STEP LOGIC WITH FORMULA TRACKING ---
    if st.session_state.pending_steps:
        st.session_state.next_prediction = st.session_state.pending_steps.pop(0)
        # Formula name remains the same for 2nd step
    else:
        found_pattern = False
        for rule in RULES:
            if st.session_state.pattern_chain.endswith(rule["pattern"]):
                st.session_state.next_prediction = rule["results"][0]
                st.session_state.active_formula = rule["name"]
                if len(rule["results"]) > 1:
                    st.session_state.pending_steps = rule["results"][1:]
                found_pattern = True
                break
        
        if not found_pattern:
            st.session_state.next_prediction = "WAIT"
            st.session_state.active_formula = "-"

# --- UI ---
st.title("🕹️ 91 Game: Formula-Named Predictor")

m = calculate_metrics()
c1, c2, c3, c4, c5 = st.columns(5)
with c1: st.metric("WINS", m["WINS"])
with c2: st.metric("LOSS", m["LOSS"])
with c3: st.metric("WIN RATE", m["WIN_RATE"])
with c4: st.metric("CHAIN", len(st.session_state.pattern_chain))
with c5: st.metric("STICK", st.session_state.stick_count)

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
    f_name = st.session_state.active_formula
    
    if p == "B":
        st.markdown(f'<div class="predict-box" style="background-color: #28a745; color: white;">NEXT: BIG (B) <span class="formula-badge">{f_name}</span></div>', unsafe_allow_html=True)
    elif p == "S":
        st.markdown(f'<div class="predict-box" style="background-color: #dc3545; color: white;">NEXT: SMALL (S) <span class="formula-badge">{f_name}</span></div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="predict-box" style="background-color: #ffc107; color: black;">WAITING...</div>', unsafe_allow_html=True)

st.divider()
st.subheader("📋 Game History Log")
if st.session_state.history_data:
    df = pd.DataFrame(st.session_state.history_data)
    st.table(df.iloc[::-1])
    st.download_button("📥 Download Log", data=df.to_csv(index=False).encode('utf-8'), file_name="91_predictor_log.csv")
