import streamlit as st
import pandas as pd

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="91 Game Predictor Pro", layout="wide")

# Custom Styling
st.markdown("""
    <style>
    .metric-container {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #e0e0e0;
        text-align: center;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.05);
    }
    .metric-label { font-size: 14px; font-weight: bold; color: #666; }
    .metric-value { font-size: 24px; font-weight: bold; color: #333; }
    .stButton>button { height: 60px; font-size: 20px; font-weight: bold; border-radius: 8px; }
    .predict-box { font-size: 40px; font-weight: bold; text-align: center; padding: 20px; border-radius: 12px; }
    </style>
    """, unsafe_allow_html=True)

# --- LOGIC SETTINGS ---
RULES = {
    "BBSB": ["B", "S"],
    "BBSSS": ["S", None],
    "SBBSBS": ["B", "S"],
    "BSBB": ["S", None]
}

def get_bs(n):
    return "B" if int(n) >= 5 else "S"

def get_rule_prediction(sequence):
    for pattern, results in RULES.items():
        if sequence.endswith(pattern):
            return results
    return None

# --- STATE INITIALIZATION ---
if 'history_data' not in st.session_state:
    st.session_state.history_data = []
if 'next_prediction' not in st.session_state:
    st.session_state.next_prediction = "WAIT"
if 'pattern_chain' not in st.session_state:
    st.session_state.pattern_chain = ""
if 'current_stick' not in st.session_state:
    st.session_state.current_stick = 1

# --- CALCULATION HELPERS ---
def calculate_metrics():
    if not st.session_state.history_data:
        return {"MAX_WIN": 0, "MAX_LOSS": 0, "WINS": 0, "LOSS": 0, "WIN_RATE": 0.0}
    
    df = pd.DataFrame(st.session_state.history_data)
    valid_games = df[df['Result'] != "-"]
    
    wins = len(valid_games[valid_games['Result'] == "WIN ✅"])
    losses = len(valid_games[valid_games['Result'] == "LOSS ❌"])
    total = wins + losses
    win_rate = round(wins / total, 2) if total > 0 else 0.0
    
    # Calculate Max Streaks
    results = valid_games['Result'].tolist()
    max_win = 0
    max_loss = 0
    curr_win = 0
    curr_loss = 0
    
    for r in results:
        if "WIN" in r:
            curr_win += 1
            curr_loss = 0
            max_win = max(max_win, curr_win)
        else:
            curr_loss += 1
            curr_win = 0
            max_loss = max(max_loss, curr_loss)
            
    return {"MAX_WIN": max_win, "MAX_LOSS": max_loss, "WINS": wins, "LOSS": losses, "WIN_RATE": win_rate}

# --- ACTION ---
def handle_click(num):
    current_bs = get_bs(num)
    
    status = "-"
    stick_to_record = ""
    
    if st.session_state.next_prediction != "WAIT":
        if current_bs == st.session_state.next_prediction:
            status = "WIN ✅"
            stick_to_record = st.session_state.current_stick
            st.session_state.current_stick = 1 # Reset stick on win
        else:
            status = "LOSS ❌"
            stick_to_record = st.session_state.current_stick
            st.session_state.current_stick += 1 # Increase stick on loss
    
    # Save entry
    st.session_state.history_data.append({
        "Number": num,
        "B/S": current_bs,
        "Prediction": st.session_state.next_prediction,
        "Result": status,
        "Stick": stick_to_record
    })
    
    st.session_state.pattern_chain += current_bs
    pred_res = get_rule_prediction(st.session_state.pattern_chain)
    st.session_state.next_prediction = pred_res[0] if pred_res else "WAIT"

# --- UI DISPLAY ---
st.title("📊 91 Game Predictor + Stick Counter")

# Dashboard Row
m = calculate_metrics()
c1, c2, c3, c4, c5 = st.columns(5)
with c1: st.markdown(f'<div class="metric-container"><div class="metric-label">MAX WIN</div><div class="metric-value">{m["MAX_WIN"]}</div></div>', unsafe_allow_html=True)
with c2: st.markdown(f'<div class="metric-container"><div class="metric-label">MAX LOSS</div><div class="metric-value">{m["MAX_LOSS"]}</div></div>', unsafe_allow_html=True)
with c3: st.markdown(f'<div class="metric-container"><div class="metric-label">WINS</div><div class="metric-value">{m["WINS"]}</div></div>', unsafe_allow_html=True)
with c4: st.markdown(f'<div class="metric-container"><div class="metric-label">LOSS</div><div class="metric-value">{m["LOSS"]}</div></div>', unsafe_allow_html=True)
with c5: st.markdown(f'<div class="metric-container"><div class="metric-label">WIN RATE</div><div class="metric-value">{m["WIN_RATE"]}</div></div>', unsafe_allow_html=True)

st.divider()

col_left, col_right = st.columns([1, 1])

with col_left:
    st.subheader("Input Result")
    grid = [st.columns(5), st.columns(5)]
    for i in range(10):
        row, col = (0, i) if i < 5 else (1, i-5)
        if grid[row][col].button(str(i), key=f"grid_{i}"):
            handle_click(i)
            st.rerun()
    
    if st.button("🗑️ Reset Data"):
        st.session_state.history_data = []
        st.session_state.pattern_chain = ""
        st.session_state.next_prediction = "WAIT"
        st.session_state.current_stick = 1
        st.rerun()

with col_right:
    st.subheader("Current Prediction")
    p = st.session_state.next_prediction
    if p == "B":
        st.markdown(f'<div class="predict-box" style="background-color: #28a745; color: white;">NEXT: BIG (Stick {st.session_state.current_stick})</div>', unsafe_allow_html=True)
    elif p == "S":
        st.markdown(f'<div class="predict-box" style="background-color: #dc3545; color: white;">NEXT: SMALL (Stick {st.session_state.current_stick})</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="predict-box" style="background-color: #ffc107; color: black;">WAITING...</div>', unsafe_allow_html=True)

st.divider()

# History Table
st.subheader("📈 Game Log")
if st.session_state.history_data:
    df = pd.DataFrame(st.session_state.history_data)
    # Applying table formatting
    st.table(df.iloc[::-1]) # Table style like your image
    
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Download Excel/CSV", data=csv, file_name="91_prediction_log.csv")
