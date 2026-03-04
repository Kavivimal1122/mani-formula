import streamlit as st
import pandas as pd

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="91 Game Predictor Pro", layout="wide")

# Custom Styling
st.markdown("""
    <style>
    .predict-text { font-size: 40px; font-weight: bold; text-align: center; padding: 20px; border-radius: 10px; border: 2px solid #ddd; }
    .win { color: #ffffff; background-color: #28a745; padding: 5px 10px; border-radius: 5px; }
    .loss { color: #ffffff; background-color: #dc3545; padding: 5px 10px; border-radius: 5px; }
    </style>
    """, unsafe_allow_html=True)

# --- LOGIC CONFIGURATION ---
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

# --- SESSION STATE INITIALIZATION ---
if 'history_data' not in st.session_state:
    st.session_state.history_data = [] # Stores rows of dicts
if 'next_prediction' not in st.session_state:
    st.session_state.next_prediction = "WAIT"
if 'pattern_chain' not in st.session_state:
    st.session_state.pattern_chain = ""

# --- UI ---
st.title("🎲 91 Game: Win/Loss Tracker & Predictor")
st.write("Enter numbers one by one. The app tracks patterns and calculates Win/Loss automatically.")

col1, col2 = st.columns([1, 2])

with col1:
    st.header("Input Data")
    num_input = st.number_input("Enter Number (0-9)", min_value=0, max_value=9, step=1)
    
    if st.button("Submit Result"):
        current_bs = get_bs(num_input)
        
        # 1. Determine Win/Loss for the PREVIOUS prediction
        status = "-"
        if st.session_state.next_prediction != "WAIT":
            status = "WIN ✅" if current_bs == st.session_state.next_prediction else "LOSS ❌"
        
        # 2. Add current entry to history
        new_entry = {
            "Number": num_input,
            "B/S": current_bs,
            "Prediction Followed": st.session_state.next_prediction,
            "Result": status
        }
        st.session_state.history_data.append(new_entry)
        
        # 3. Update the pattern chain string
        st.session_state.pattern_chain += current_bs
        
        # 4. Calculate prediction for the NEXT round
        pred_res = get_rule_prediction(st.session_state.pattern_chain)
        if pred_res:
            st.session_state.next_prediction = pred_res[0] # Set next prediction
        else:
            st.session_state.next_prediction = "WAIT"

    if st.button("Reset Everything"):
        st.session_state.history_data = []
        st.session_state.pattern_chain = ""
        st.session_state.next_prediction = "WAIT"
        st.rerun()

with col2:
    st.header("Live Prediction")
    curr_pred = st.session_state.next_prediction
    
    if curr_pred == "B":
        st.markdown('<div class="predict-text" style="background-color: #28a745; color: white;">NEXT: BIG (B)</div>', unsafe_allow_html=True)
    elif curr_pred == "S":
        st.markdown('<div class="predict-text" style="background-color: #dc3545; color: white;">NEXT: SMALL (S)</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="predict-text" style="background-color: #ffc107; color: black;">WAITing for Pattern...</div>', unsafe_allow_html=True)
    
    st.write(f"**Current Pattern Chain:** `{st.session_state.pattern_chain}`")

st.divider()

# --- HISTORY TABLE ---
st.subheader("📊 Performance History")
if st.session_state.history_data:
    df_history = pd.DataFrame(st.session_state.history_data)
    
    # Show the table
    st.table(df_history.iloc[::-1]) # Show latest on top
    
    # Download History
    csv = df_history.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Download History CSV", data=csv, file_name="91_game_history.csv", mime="text/csv")
else:
    st.info("No data yet. Enter a number to start tracking.")
