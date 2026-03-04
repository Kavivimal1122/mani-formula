import streamlit as st
import pandas as pd

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="91 Game Predictor", layout="wide")

# Custom CSS for the UI
st.markdown("""
    <style>
    .main { background-color: #f0f2f6; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #007bff; color: white; }
    .predict-text { font-size: 40px; font-weight: bold; text-align: center; padding: 20px; border-radius: 10px; }
    .big-style { background-color: #28a745; color: white; }
    .small-style { background-color: #dc3545; color: white; }
    .wait-style { background-color: #ffc107; color: black; }
    </style>
    """, unsafe_allow_html=True)

# --- PREDICTION LOGIC ---
# Defined patterns based on your rules
RULES = {
    "BBSB": ["B", "S"],       # 1st: Big, 2nd: Small
    "BBSSS": ["S", None],     # 1st: Small
    "SBBSBS": ["B", "S"],     # 1st: Big, 2nd: Small
    "BSBB": ["S", None]       # 1st: Small
}

def get_prediction(sequence):
    """Checks the end of the sequence against the rules."""
    for pattern, results in RULES.items():
        if sequence.endswith(pattern):
            return results
    return None

def number_to_bs(n):
    return "B" if int(n) >= 5 else "S"

# --- APP UI ---
st.title("🎮 91 Game Pattern Prediction Tool")
st.divider()

# TAB 1: Real-time Manual Entry
# TAB 2: CSV/Excel Batch Processing
tab1, tab2 = st.tabs(["Manual Prediction", "Bulk CSV Upload"])

with tab1:
    st.header("Step-by-Step Entry")
    
    if 'history' not in st.session_state:
        st.session_state.history = ""

    col1, col2 = st.columns([1, 2])
    
    with col1:
        num_input = st.number_input("Enter Result (0-9)", min_value=0, max_value=9, step=1, key="manual_num")
        if st.button("Add to Sequence"):
            st.session_state.history += number_to_bs(num_input)

    with col2:
        st.subheader("Current Pattern Chain")
        st.code(st.session_state.history if st.session_state.history else "No data entered yet")
        
        if st.button("Clear Chain"):
            st.session_state.history = ""
            st.rerun()

    # Calculate Prediction
    prediction = get_prediction(st.session_state.history)
    
    st.markdown("### Next Move:")
    if prediction:
        res1, res2 = prediction
        style = "big-style" if res1 == "B" else "small-style"
        st.markdown(f'<div class="predict-text {style}">PLAY: {res1} (1st Result)</div>', unsafe_allow_html=True)
        if res2:
            st.info(f"If 1st hits, wait. If 1st fails, 2nd Result is: {res2}")
    else:
        st.markdown('<div class="predict-text wait-style">WAITING FOR PATTERN...</div>', unsafe_allow_html=True)

with tab2:
    st.header("Upload CSV for Prediction")
    uploaded_file = st.file_uploader("Choose your CSV or Excel file", type=['csv', 'xlsx'])
    
    if uploaded_file:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
            
        # Ensure column for B/S exists
        if '0 to 9' in df.columns:
            df['Calculated_BS'] = df['0 to 9'].apply(number_to_bs)
            
            # Create a full string of the history
            full_history = "".join(df['Calculated_BS'].astype(str).tolist())
            
            # Generate predictions for the whole file
            predictions_list = []
            temp_history = ""
            for char in full_history:
                temp_history += char
                res = get_prediction(temp_history)
                predictions_list.append(res[0] if res else "WAIT")
            
            df['Prediction'] = predictions_list
            
            st.write("Preview of predictions:")
            st.dataframe(df.tail(10))
            
            # Download Button
            csv_data = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download Predicted CSV",
                data=csv_data,
                file_name="91_game_predicted.csv",
                mime="text/csv"
            )
        else:
            st.error("Error: CSV must have a column named '0 to 9'")
