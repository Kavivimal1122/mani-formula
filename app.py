import streamlit as st
import pandas as pd

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="91 Game AI Master Predictor", layout="wide")

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
    
    /* PREDICTION BOXES STYLING */
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
    .bg-ai { background-color: #6f42c1; border: 2px solid #5a32a3; box-shadow: 0px 0px 15px rgba(111, 66, 193, 0.4); }

    /* BUTTON GRID STYLING */
    div.stButton > button {
        height: 60px !important;
        font-size: 24px !important;
        font-weight: bold !important;
        color: white !important;
        border-radius: 8px !important;
    }

    /* Red Background: 0, 2, 4, 6, 8 */
    button[key*="btn_0"], button[key*="btn_2"], button[key*="btn_4"], button[key*="btn_6"], button[key*="btn_8"] {
        background-color: #ff0000 !important;
        border: 2px solid #b30000 !important;
    }

    /* Green Background: 1, 3, 5, 7, 9 */
    button[key*="btn_1"], button[key*="btn_3"], button[key*="btn_5"], button[key*="btn_7"], button[key*="btn_9"] {
        background-color: #008000 !important;
        border: 2px solid #004d00 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- FORMULAS ---
RULES_4 = {"BBSB": "B", "BSBB": "S"}
RULES_5 = {"BBSBS": "S", "BBSSS": "S"}
RULES_6 = {"SBBSBS": "B", "BBSBSS": "S"}
RULES_7 = {"SBBSBSS": "S"}

def get_bs(n):
    return "B" if int(n) >= 5 else "S"

def check_all_patterns(chain):
    res_4 = RULES_4.get(chain[-4:], "WAIT") if len(chain) >= 4 else "WAIT"
    res_5 = RULES_5.get(chain[-5:], "WAIT") if len(chain) >= 5 else "WAIT"
    res_6 = RULES_6.get(chain[-6:], "WAIT") if len(chain) >= 6 else "WAIT"
    res_7 = RULES_7.get(chain[-7:], "WAIT") if len(chain) >= 7 else "WAIT"
    return res_4, res_5, res_6, res_7

def get_ai_master_logic(p4, p5, p6, p7, history):
    # Find the last R_5D result from history
    last_r5 = "-"
    if history:
        for entry in reversed(history):
            if entry['R_5D'] != "-":
                last_r5 = entry['R_5D']
                break
    
    # 1. Recovery Rule: If 5D lost, follow 6D (61.5% accuracy)
    if "LOSS" in last_r5 and p6 != "WAIT":
        return p6
    
    # 2. Accuracy Rule: 5D is most stable (52.4%)
    if p5 != "WAIT":
        return p5
    
    # 3. Fallbacks
    if p6 != "WAIT": return p6
    if p4 != "WAIT": return p4
    return "WAIT"

# --- STATE INITIALIZATION ---
if 'history_data' not in st.session_state:
    st.session_state.history_data = []
if 'pattern_chain' not in st.session_state:
    st.session_state.pattern_chain = ""
if 'last_bs' not in st.session_state:
    st.session_state.last_bs = None
if 'stick_count' not in st.session_state:
    st.session_state.stick_count = 0

# --- METRICS LOGIC ---
def calculate_metrics(df, col_pred='AI Master', col_res='R_AI'):
    if df.empty:
        return {"MAX_WIN": 0, "MAX_LOSS": 0, "WINS": 0, "LOSS": 0}
    
    valid = df[df[col_pred] != "WAIT"]
    if valid.empty: return {"MAX_WIN": 0, "MAX_LOSS": 0, "WINS": 0, "LOSS": 0}
    
    wins = len(valid[valid[col_res] == "WIN ✅"])
    losses = len(valid[valid[col_res] == "LOSS ❌"])
    
    res_list = valid[col_res].tolist()
    max_w, max_l, cur_w, cur_l = 0, 0, 0, 0
    for r in res_list:
        if "WIN" in r:
            cur_w += 1; cur_l = 0; max_w = max(max_w, cur_w)
        else:
            cur_l += 1; cur_w = 0; max_l = max(max_l, cur_l)
    return {"MAX_WIN": max_w, "MAX_LOSS": max_l, "WINS": wins, "LOSS": losses}

def handle_click(num):
    current_bs = get_bs(num)
    if st.session_state.last_bs == current_bs:
        st.session_state.stick_count += 1
    else:
        st.session_state.stick_count = 1
    
    p4, p5, p6, p7 = check_all_patterns(st.session_state.pattern_chain)
    ai_p = get_ai_master_logic(p4, p5, p6, p7, st.session_state.history_data)
    
    # Check Win/Loss
    r4 = ("WIN ✅" if current_bs == p4 else "LOSS ❌") if p4 != "WAIT" else "-"
    r5 = ("WIN ✅" if current_bs == p5 else "LOSS ❌") if p5 != "WAIT" else "-"
    r6 = ("WIN ✅" if current_bs == p6 else "LOSS ❌") if p6 != "WAIT" else "-"
    r7 = ("WIN ✅" if current_bs == p7 else "LOSS ❌") if p7 != "WAIT" else "-"
    rai = ("WIN ✅" if current_bs == ai_p else "LOSS ❌") if ai_p != "WAIT" else "-"
    
    st.session_state.history_data.append({
        "Number": num, "B/S": current_bs, "Stick": st.session_state.stick_count,
        "AI Master": ai_p, "R_AI": rai,
        "4D Pred": p4, "R_4D": r4,
        "5D Pred": p5, "R_5D": r5,
        "6D Pred": p6, "R_6D": r6,
        "7D Pred": p7, "R_7D": r7
    })
    st.session_state.last_bs = current_bs
    st.session_state.pattern_chain += current_bs

# --- UI ---
st.title("🕹️ 91 Game Predictor + AI MASTER")
tab1, tab2 = st.tabs(["🎮 Live AI Play", "📂 Bulk Evaluation"])

with tab1:
    m = calculate_metrics(pd.DataFrame(st.session_state.history_data))
    db_cols = st.columns(4)
    with db_cols[0]: st.markdown(f'<div class="metric-container"><div class="metric-label">AI MAX WIN</div><div class="metric-value">{m["MAX_WIN"]}</div></div>', unsafe_allow_html=True)
    with db_cols[1]: st.markdown(f'<div class="metric-container"><div class="metric-label">AI MAX LOSS</div><div class="metric-value">{m["MAX_LOSS"]}</div></div>', unsafe_allow_html=True)
    with db_cols[2]: st.markdown(f'<div class="metric-container"><div class="metric-label">AI TOTAL WINS</div><div class="metric-value">{m["WINS"]}</div></div>', unsafe_allow_html=True)
    with db_cols[3]: st.markdown(f'<div class="metric-container"><div class="metric-label">AI TOTAL LOSS</div><div class="metric-value">{m["LOSS"]}</div></div>', unsafe_allow_html=True)

    st.divider()
    p4, p5, p6, p7 = check_all_patterns(st.session_state.pattern_chain)
    ai_p = get_ai_master_logic(p4, p5, p6, p7, st.session_state.history_data)

    def draw_box(label, result, is_ai=False):
        style = "bg-big" if result == "B" else "bg-small" if result == "S" else "bg-wait"
        if is_ai and result != "WAIT": style = "bg-ai"
        st.markdown(f'<div class="box-container {style}"><div class="label-text">{label}</div><div class="result-text">{result if result != "WAIT" else "WAIT..."}</div></div>', unsafe_allow_html=True)

    c_ai, c1, c2, c3, c4 = st.columns([1.5, 1, 1, 1, 1])
    with c_ai: draw_box("✨ AI MASTER", ai_p, is_ai=True)
    with c1: draw_box("4D Result", p4)
    with c2: draw_box("5D Result", p5)
    with c3: draw_box("6D Result", p6)
    with c4: draw_box("7D Result", p7)

    st.divider()
    col_l, col_r = st.columns([1, 1])
    with col_l:
        st.subheader("Click Number")
        grid = [st.columns(5), st.columns(5)]
        for i in range(10):
            r, c = (0, i) if i < 5 else (1, i-5)
            if grid[r][c].button(str(i), key=f"btn_{i}"):
                handle_click(i); st.rerun()
    with col_r:
        st.subheader("System Status")
        st.info(f"Chain: `{st.session_state.pattern_chain[-15:]}`")
        if st.button("⬅️ Delete Last", type="primary", use_container_width=True):
            if st.session_state.history_data:
                st.session_state.history_data.pop(); st.session_state.pattern_chain = st.session_state.pattern_chain[:-1]
                if st.session_state.history_data:
                    st.session_state.last_bs = st.session_state.history_data[-1]["B/S"]
                    st.session_state.stick_count = st.session_state.history_data[-1]["Stick"]
                else: st.session_state.last_bs = None; st.session_state.stick_count = 0
                st.rerun()
        if st.button("🗑️ Reset All", type="secondary", use_container_width=True):
            for key in list(st.session_state.keys()): del st.session_state[key]
            st.rerun()

    st.divider()
    if st.session_state.history_data:
        df_log = pd.DataFrame(st.session_state.history_data)
        st.table(df_log.iloc[::-1])

with tab2:
    st.header("📂 Bulk Evaluation")
    uploaded_file = st.file_uploader("Upload CSV (Ser No, 0 to 9, B/S, R/G)", type="csv")
    if uploaded_file:
        data = pd.read_csv(uploaded_file)
        if '0 to 9' in data.columns:
            results, chain, prev_bs, stick, hist_temp = [], "", None, 0, []
            for _, row in data.iterrows():
                num = row['0 to 9']; curr_bs = get_bs(num)
                stick = stick + 1 if prev_bs == curr_bs else 1
                p4, p5, p6, p7 = check_all_patterns(chain)
                ai_p = get_ai_master_logic(p4, p5, p6, p7, hist_temp)
                
                res_entry = {
                    "Ser No": row.get('Ser No', '-'), "Number": num, "B/S": curr_bs, "Stick": stick,
                    "AI Master": ai_p, "R_AI": ("WIN ✅" if curr_bs == ai_p else "LOSS ❌") if ai_p != "WAIT" else "-",
                    "4D": p4, "R_4D": ("WIN ✅" if curr_bs == p4 else "LOSS ❌") if p4 != "WAIT" else "-",
                    "5D": p5, "R_5D": ("WIN ✅" if curr_bs == p5 else "LOSS ❌") if p5 != "WAIT" else "-",
                    "6D": p6, "R_6D": ("WIN ✅" if curr_bs == p6 else "LOSS ❌") if p6 != "WAIT" else "-",
                    "7D": p7, "R_7D": ("WIN ✅" if curr_bs == p7 else "LOSS ❌") if p7 != "WAIT" else "-"
                }
                results.append(res_entry)
                hist_temp.append(res_entry)
                chain += curr_bs; prev_bs = curr_bs
            
            eval_df = pd.DataFrame(results)
            m_eval = calculate_metrics(eval_df)
            st.success(f"AI MASTER Dashboard: WIN: {m_eval['WINS']} | LOSS: {m_eval['LOSS']} | MAX WIN: {m_eval['MAX_WIN']} | MAX LOSS: {m_eval['MAX_LOSS']}")
            st.dataframe(eval_df)
            st.download_button("📥 Download Evaluated CSV", data=eval_df.to_csv(index=False).encode('utf-8'), file_name="ai_master_evaluated.csv")
