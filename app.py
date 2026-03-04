import streamlit as st
import pandas as pd

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="91 Game Clicker", layout="wide")

# Custom Styling for the Grid and Predictions
st.markdown("""
    <style>
    .stButton>button {
        height: 60px;
        font-size: 24px;
        font-weight: bold;
        border-radius: 10px;
    }
    .predict-box {
        font-size: 45px;
        font-weight: bold;
        text-align: center;
        padding: 30px;
        border-radius: 15px;
        margin-bottom: 20px;
    }
    .win-text { color: #28a745; font-weight: bold; }
    .loss-text { color: #dc3545; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- LOGIC ---
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

# --- STATE MANAGEMENT ---
if 'history_data' not in st.session_state:
    st.session_state.history_data = []
if 'next_prediction' not in st.session_state:
    st.session_state.next_prediction = "WAIT"
if 'pattern_chain' not in st.session_state:
    st.session_state.pattern_chain = ""

# --- ACTION FUNCTION ---
def handle_click(num):
    current_bs = get_bs(num)
    
    # 1. Check Win/Loss of the prediction that was active
    status = "-"
    if st.session_state.next_prediction != "WAIT":
        status = "WIN ✅" if current_bs == st.session_state.next_prediction else "LOSS ❌"
    
    # 2. Save result
    st.session_state.history_data.append({
        "Number": num,
        "B/S": current_bs,
        "Prediction": st.session_state.next_prediction,
        "Result": status
    })
    
    # 3. Update Chain and get NEXT prediction
    st.session_state.pattern_chain += current_bs
    pred_res = get_rule_prediction(st.session_state.pattern_chain)
    st.session_state.next_prediction = pred_res[0] if pred_res else "WAIT"

# --- UI LAYOUT ---
st.title("🎯 91 Game: Instant Clicker")

col_left, col_right = st.columns([1, 1])

with col_left:
    st.subheader("Select Result Number")
    # Creating a 2x5 Grid for numbers 0-9
    grid = [st.columns(5), st.columns(5)]
    
    for i in range(10):
        row = 0 if i < 5 else 1
        col_idx = i % 5
        if grid[row][col_idx].button(str(i), key=f"btn_{i}"):
            handle_click(i)
            st.rerun()

    if st.button("🗑️ Reset All Data", type="secondary"):
        st.session_state.history_data = []
        st.session_state.pattern_chain = ""
        st.session_state.next_prediction = "WAIT"
        st.rerun()

with col_right:
    st.subheader("Next Prediction")
    curr_pred = st.session_state.next_prediction
    
    if curr_pred == "B":
        st.markdown('<div class="predict-box" style="background-color: #28a745; color: white;">NEXT: BIG (B)</div>', unsafe_allow_html=True)
    elif curr_pred == "S":
        st.markdown('<div class="predict-box" style="background-color: #dc3545; color: white;">NEXT: SMALL (S)</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="predict-box" style="background-color: #ffc107; color: black;">WAIT...</div>', unsafe_allow_html=True)
    
    st.write(f"**Current Chain:** `{st.session_state.pattern_chain}`")

st.divider()

# --- TABLE ---
st.subheader("📊 Live History Log")
if st.session_state.history_data:
    df = pd.DataFrame(st.session_state.history_data)
    # Reverse to show latest first
    st.dataframe(df.iloc[::-1], use_container_width=True)
    
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Download This Session (.csv)", data=csv, file_name="91_game_session.csv")
else:
    st.info("Click a number above to start tracking.")
