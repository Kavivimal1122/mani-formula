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
    .metric-label { font-size: 14px; font-weight: bold; color: #666; }
    .metric-value { font-size: 24px; font-weight: bold; color: #333; }
    .stButton>button { height: 60px; font-size: 22px; font-weight: bold; border-radius: 8px; }
    .predict-box { font-size: 40px; font-weight: bold; text-align: center; padding: 20px; border-radius: 12px; }
    </style>
    """, unsafe_allow_html=True)

# --- YOUR SPECIFIC PATTERNS ---
# Ordered by length (longest first) to ensure correct matching
RULES = [
    {"pattern": "SBBSBS", "results": ["B", "S"]},
    {"pattern": "BBSSS",  "results": ["S"]},
    {"pattern": "BBSB",   "results": ["B", "S"]},
    {"pattern": "BSBB",   "results": ["S"]}
]

def get_bs(n):
    return "B" if int(n) >= 5 else "S"

# --- STATE INITIALIZATION ---
if 'history_data' not in st.session_state:
    st.session_state.history_data = []
if 'next_prediction' not in st.session_state:
    st.session_state.next_prediction = "WAIT"
if 'pattern_chain' not in st.session_state:
    st.session_state.pattern_chain = ""
if 'last_bs' not in st.session_state:
    st.session_state.last_bs = None
if 'stick_count' not in st.session_state:
    st.session_state.stick_count = 0
if 'pending_steps' not in st.session_state:
    st.session_state.pending_steps = []

# --- METRICS CALCULATION ---
def calculate_metrics():
    if not st.session_state.history_data:
        return {"MAX_WIN": 0, "MAX_LOSS": 0, "WINS": 0, "LOSS": 0, "WIN_RATE": 0.0}
    df = pd.DataFrame(st.session_state.history_data)
    valid = df[df['Result'] != "-"]
    wins = len(valid[valid['Result'] == "WIN ✅"])
    losses = len(valid[valid['Result'] == "LOSS ❌"])
    total = wins + losses
    win_rate = round(wins / total, 2) if total > 0 else 0.0
    
    res_list = valid['Result'].tolist()
    max_w, max_l, cur_w, cur_l = 0, 0, 0, 0
    for r in res_list:
        if "WIN" in r:
            cur_w += 1; cur_l = 0; max_w = max(max_w, cur_w)
        else:
            cur_l += 1; cur_w = 0; max_l = max(max_l, cur_l)
    return {"MAX_WIN": max_w, "MAX_LOSS": max_l, "WINS": wins, "LOSS": losses, "WIN_RATE": win_rate}

# --- ACTION HANDLER ---
def handle_click(num):
    current_bs = get_bs(num)
    
    # Correct Stick Logic: =IF(A2=A1, B1+1, 1)
    if st.session_state.last_bs == current_bs:
        st.session_state.stick_count += 1
    else:
        st.session_state.stick_count = 1
    
    # Check Win/Loss for the current prediction
    status = "-"
    if st.session_state.next_prediction != "WAIT":
        status = "WIN ✅" if current_bs == st.session_state.next_prediction else "LOSS ❌"
    
    # Record history
    st.session_state.history_data.append({
        "Number": num, 
        "B/S": current_bs, 
        "Stick": st.session_state.stick_count,
        "Prediction": st.session_state.next_prediction, 
        "Result": status
    })
    
    st.session_state.last_bs = current_bs
    st.session_state.pattern_chain += current_bs
    
    # --- MULTI-STEP LOGIC ---
    # 1. Check if we have a 2nd result already queued from a previous match
    if st.session_state.pending_steps:
        st.session_state.next_prediction = st.session_state.pending_steps.pop(0)
    else:
        # 2. Look for a new pattern (Check Longest Patterns First)
        found_pattern = False
        for rule in RULES:
            if st.session_state.pattern_chain.endswith(rule["pattern"]):
                results = rule["results"]
                st.session_state.next_prediction = results[0] # 1st Result
                if len(results) > 1:
                    st.session_state.pending_steps = results[1:] # Store 2nd Result
                found_pattern = True
                break
        
        if not found_pattern:
            st.session_state.next_prediction = "WAIT"

# --- UI DISPLAY ---
st.title("🕹️ 91 Game: Advanced Sequence Predictor")

m = calculate_metrics()
c1, c2, c3, c4, c5 = st.columns(5)
with c1: st.markdown(f'<div class="metric-container"><div class="metric-label">MAX WIN</div><div class="metric-value">{m["MAX_WIN"]}</div></div>', unsafe_allow_html=True)
with c2: st.markdown(f'<div class="metric-container"><div class="metric-label">MAX LOSS</div><div class="metric-value">{m["MAX_LOSS"]}</div></div>', unsafe_allow_html=True)
with c3: st.markdown(f'<div class="metric-container"><div class="metric-label">WINS</div><div class="metric-value">{m["WINS"]}</div></div>', unsafe_allow_html=True)
with c4: st.markdown(f'<div class="metric-container"><div class="metric-label">LOSS</div><div class="metric-value">{m["LOSS"]}</div></div>', unsafe_allow_html=True)
with c5: st.markdown(f'<div class="metric-container"><div class="metric-label">WIN RATE</div><div class="metric-value">{m["WIN_RATE"]}</div></div>', unsafe_allow_html=True)

st.divider()

col_l, col_r = st.columns([1, 1])
with col_l:
    st.subheader("Click Number (0-9)")
    grid = [st.columns(5), st.columns(5)]
    for i in range(10):
        r, c = (0, i) if i < 5 else (1, i-5)
        if grid[r][c].button(str(i), key=f"btn_{i}"):
            handle_click(i)
            st.rerun()
    
    if st.button("🔄 Reset All Data"):
        for key in st.session_state.keys(): del st.session_state[key]
        st.rerun()

with col_r:
    st.subheader("Prediction Window")
    p = st.session_state.next_prediction
    if p == "B":
        st.markdown('<div class="predict-box" style="background-color: #28a745; color: white;">NEXT: BIG (B)</div>', unsafe_allow_html=True)
    elif p == "S":
        st.markdown('<div class="predict-box" style="background-color: #dc3545; color: white;">NEXT: SMALL (S)</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="predict-box" style="background-color: #ffc107; color: black;">WAITING...</div>', unsafe_allow_html=True)
    
    if st.session_state.pending_steps:
        st.info(f"Queued Follow-up: {st.session_state.pending_steps[0]}")

st.divider()
st.subheader("📋 Game History Log")
if st.session_state.history_data:
    df = pd.DataFrame(st.session_state.history_data)
    st.table(df.iloc[::-1])
    st.download_button("📥 Download History", data=df.to_csv(index=False).encode('utf-8'), file_name="91_predictor_log.csv")
