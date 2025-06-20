import streamlit as st
import pandas as pd
import joblib
import base64
import json
from pathlib import Path
import xgboost as xgb

# === Page Configuration ===
st.set_page_config(
    page_title="1. FC Köln Transfer Dashboard",
    page_icon="⚽",
    layout="wide"
)

# === GLOBAL DESIGN STYLES ===
st.markdown(
    """
    <style>
    header {visibility: hidden;}
    footer {visibility: hidden;}
    .block-container {
        padding-top: 0rem;
    }

    /* Button style: Predict – visible, bold, gradient */
    .stButton > button:first-child {
        background: linear-gradient(to right, #ba0c2f, #a5002a);
        color: white;
        font-weight: 700;
        font-size: 1.2rem;
        height: 80px;
        width: 100%;
        border: none;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(255, 0, 0, 0.4);
        transition: all 0.3s ease;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    .stButton > button:first-child:hover {
        background: linear-gradient(to right, #ff3344, #cc0022);
        box-shadow: 0 6px 20px rgba(255, 0, 0, 0.6);
        transform: scale(1.03);
        cursor: pointer;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# === BACKGROUND FUNCTION WITH OVERLAY ===
stadium_background = "stadium.jpg"
logo_fc = "1-fc-koln-logo-png_seeklogo-266469.png"
logo_uni = "Uni_blau2.png"

def set_bg_image_with_overlay(image_path):
    with open(image_path, "rb") as img_file:
        img_base64 = base64.b64encode(img_file.read()).decode()

    st.markdown(
    f"""
    <style>
    @keyframes fadeIn {{
        from {{opacity: 0;}}
        to {{opacity: 1;}}
    }}

    .stApp {{
        background: linear-gradient(rgba(0,0,0,0.7), rgba(0,0,0,0.7)),
                    url("data:image/png;base64,{img_base64}");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
        background-repeat: no-repeat;
        color: #f9f9f9 !important;
        font-family: 'Segoe UI', 'Roboto', sans-serif;
        font-weight: 500;
    }}

    h1, h2, h3, h4, h5, p, label, .stSlider span {{
        color: #f9f9f9 !important;
        font-weight: 600 !important;
    }}

    .stSlider > div[data-baseweb='slider'] span {{
        background-color: transparent !important;
        font-weight: bold;
    }}

    .stSelectbox, .stNumberInput, .stTextInput, .stMarkdown {{
        font-weight: 500;
    }}

    .block-container {{
        max-width: 1100px;
        margin: auto;
        padding-top: 2rem;
    }}
    </style>
    """,
    unsafe_allow_html=True
)

# === BACKGROUND INIT ===
set_bg_image_with_overlay(stadium_background)




# === HEADER SECTION WITH LOGOS AND TITLE ===
col_fc, col_title, col_uni = st.columns([2, 6, 2])

with col_title:
    st.markdown("""
        <h1 style='text-align: center; margin-bottom: 0.3rem;'>1. FC Köln Transfer Success Predictor</h1>
        <p style='text-align: center; color: white; font-size: 0.9rem;'>
            Developed in cooperation with the University of Cologne – estimate expected playing percentage for potential transfers.
        </p>
    """, unsafe_allow_html=True)

with col_fc:
    st.markdown("<div style='margin-top: 1.5rem;'>", unsafe_allow_html=True)
    st.image(logo_fc, width=90)
    st.markdown("</div>", unsafe_allow_html=True)

with col_uni:
    st.markdown(
        f"""
        <div style='text-align: right;'>
            <img src="data:image/png;base64,{base64.b64encode(open(logo_uni, "rb").read()).decode()}" width="150">
        </div>
        """,
        unsafe_allow_html=True
    )

# === CARD STYLE HELPER ===
def card_start(title):
    st.markdown(f"""
    <div style='background-color: rgba(255, 255, 255, 0.08); 
                padding: 1.2rem 1.5rem; 
                border-radius: 12px; 
                margin-bottom: 1rem;
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);'>
    <h4 style='color: white;'>{title}</h4>
    """, unsafe_allow_html=True)

def card_end():
    st.markdown("</div>", unsafe_allow_html=True)


# === Load Model and Mappings ===
model = xgb.XGBRegressor()
model.load_model("model2.json")

@st.cache_data
def load_mapping():
    with open("category_mappings.json") as f:
        return json.load(f)
category_mappings = load_mapping()



valid_areas = category_mappings["from_competition_competition_area"]
valid_to_areas = category_mappings["to_competition_competition_area"]
valid_position_groups = category_mappings["positionGroup"]
valid_main_positions = category_mappings["mainPosition"]
valid_feet = category_mappings["foot"]
valid_clean_sheets = category_mappings["clean_sheets_before_grouped_new"]

# Dynamic mapping from real data
position_group_to_main = pd.read_csv("xgboost_predictions_test.csv").groupby("positionGroup")["mainPosition"].unique().apply(list).to_dict()

area_to_levels = {
    'Austria': [1, 2], 'Belgium': [1, 2], 'Bosnia-Herzegovina': [1], 'Bulgaria': [1], 'Canada': [1],
    'Croatia': [1, 2], 'Czech Republic': [1], 'Denmark': [1, 2], 'England': [1, 2, 3, 4], 'Estonia': [1],
    'Finland': [1, 2], 'France': [1, 2, 3], 'Georgia': [1], 'Germany': [1, 2, 3, 4], 'Greece': [1],
    'Hungary': [1], 'Ireland': [1], 'Israel': [1], 'Italy': [1, 2], 'Japan': [1], 'Korea, South': [1],
    'Latvia': [1], 'Lithuania': [1], 'Luxembourg': [1], 'Malta': [1], 'Moldova': [1], 'Montenegro': [1],
    'Netherlands': [1, 2], 'Northern Ireland': [1], 'Norway': [1, 2], 'Poland': [1], 'Portugal': [1, 2],
    'Romania': [1], 'Russia': [1], 'Saudi Arabia': [1], 'Scotland': [1], 'Serbia': [1], 'Slovakia': [1],
    'Slovenia': [1], 'Spain': [1, 2], 'Sweden': [1, 2], 'Switzerland': [1, 2], 'Türkiye': [1],
    'Ukraine': [1], 'United States': [1, 2, 3], 'Wales': [1]
}


# === Inputs ===
col1, col2 = st.columns(2)
with col1:

    card_start("🧍 Player Profile")
    height = st.slider("Height (cm)", 150, 220, 180)
    transfer_age = st.slider("Transfer Age", 16, 40, 25)
    position_group = st.selectbox("Position Group", valid_position_groups)
    main_position = st.selectbox("Main Position", position_group_to_main.get(position_group, []))
    foot = st.selectbox("Preferred Foot", valid_feet)
    market_value = st.number_input("Player Market Value (€M)", 0.0, 200.0, 15.0)

    card_end()
    
    card_start("📊 Performance Details")
    percentage_played_before = st.slider("Playing % Before", 0.0, 100.0, 50.0)
    
    # Conditional scorer selection
    if position_group.lower() in ['defender', 'goalkeeper']:
        scorer_raw = 0
        st.markdown("**Scorer (Goals + Assists)**: Automatically ignored for defenders and goalkeepers")
    else:
        scorer_raw = st.number_input("Scorer Value (Goals + Assists)", 0, 50, 5)
    
    clean_sheets_grouped = st.selectbox("Clean Sheets Grouped", valid_clean_sheets)

    card_end()
with col2:
    card_start("🔄 Transfer Details")
    from_team_market_value = st.number_input("From Team Market Value (€M)", 0.0, 1000.0, 61.7)
    to_team_market_value = st.number_input("To Team Market Value (€M)", 0.0, 1000.0, 61.7)
    
    from_area = st.selectbox("From Area", valid_areas, index=valid_areas.index("Germany") if "Germany" in valid_areas else 0)
    from_level = st.selectbox("From Level", area_to_levels.get(from_area, [1, 2, 3, 4]), index=(area_to_levels.get(from_area, [1, 2, 3, 4]).index(1) if 1 in area_to_levels.get(from_area, [1, 2, 3, 4]) else 0), key="from_level")
    
    to_area = st.selectbox("To Area", valid_to_areas, index=valid_to_areas.index("Germany") if "Germany" in valid_to_areas else 0)
    to_level = st.selectbox("To Level", area_to_levels.get(to_area, [1, 2, 3, 4]), index=(area_to_levels.get(to_area, [1, 2, 3, 4]).index(1) if 1 in area_to_levels.get(to_area, [1, 2, 3, 4]) else 0), key="to_level")
    card_end()
    with st.expander("⚙️ Further Transfer Details"):
        isLoan = st.checkbox("Loan Transfer")
        wasLoan = st.checkbox("Was Loan Before")
        was_joker = st.checkbox("Was Joker Substitute")


# === Foreign Transfer Logic ===
foreign_transfer = int((from_area != to_area))


data = {col: 0 for col in model.feature_names_in_}
data.update({
    'height': height,
    'transferAge': transfer_age,
    'isLoan': int(isLoan),
    'wasLoan': int(wasLoan),
    'was_joker': bool(was_joker),
    'foreign_transfer': foreign_transfer,
    'percentage_played_before': percentage_played_before,
    'scorer_before': scorer_raw,
    'clean_sheets_before_grouped_new': clean_sheets_grouped,
    'fromTeam_marketValue': from_team_market_value,
    'toTeam_marketValue': to_team_market_value,
    'marketvalue_closest': market_value,
    'from_competition_competition_level': from_level,
    'to_competition_competition_level': to_level,
    'foot': foot,
    'mainPosition': main_position,
    'positionGroup': position_group,
    'from_competition_competition_area': from_area,
    'to_competition_competition_area': to_area,
    'value_per_age': market_value / transfer_age if transfer_age > 0 else 0,
    'value_age_product': transfer_age * market_value
})


input_df = pd.DataFrame([data])

# Category typing
for col, cats in category_mappings.items():
    if col in input_df.columns:
        input_df[col] = pd.Categorical(input_df[col], categories=cats)



# === ACTION BUTTONS & OUTPUT ===
col_l, col_m = st.columns([1, 6])

with col_l:
    predict_clicked = st.button("🔮 Predict")
   

# Hilfsfunktion, um HEX → RGBA umzuwandeln
def hex_to_rgba(hex_color, alpha=0.5):
    hex_color = hex_color.lstrip("#")
    r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    return f"rgba({r}, {g}, {b}, {alpha})"

# Prediction
if predict_clicked:
    with st.spinner("Running prediction..."):
        pred = model.predict(input_df)[0]
        if pred < 40:
            msg, color, emoji = "Not Recommended", "#FF4B4B", "🚫"
        elif pred < 55:
            msg, color, emoji = "Uncertain", "#FFA500", "⚠️"
        elif pred < 70:
            msg, color, emoji = "Worth a Try", "#FFD700", "🤔"
        elif pred < 80:
            msg, color, emoji = "Good Transfer", "#90EE90", "✅"
        elif pred < 90:
            msg, color, emoji = "Very Good", "#32CD32", "💎"
        else:
            msg, color, emoji = "Superstar", "#008000", "🌟"

        rgba_bg = hex_to_rgba(color, alpha=0.6)  # 0.6 ist die Transparenz

        with col_m:
            st.markdown(f"""
            <div style='
                background-color: {rgba_bg};
                height: 80px;
                display: flex;
                flex-direction: column;
                justify-content: center;
                border-radius: 12px;
                text-align: center;
                letter-spacing: 0.5px;
                box-shadow: 0 4px 12px rgba(0,0,0,0.3);'>
                <span style='color: white; font-size: 1.3rem; font-weight: 600;'>
                    {emoji} {msg} – Expected Playing Time: <strong>{pred:.2f}%</strong>
                </span>
            </div>
            """, unsafe_allow_html=True)

        
if st.checkbox("Show feature vector"):
    st.write({k: v for k, v in data.items() if v != 0})


# === Feature Importances ===

import matplotlib.pyplot as plt
import numpy as np

with st.expander("📈 Show Feature Importances"):
    fig, ax = plt.subplots()
    importances = model.feature_importances_
    indices = np.argsort(importances)[::-1][:10]  # top 10
    features = np.array(model.feature_names_in_)[indices]

    ax.barh(features[::-1], importances[indices][::-1])
    ax.set_title("Top 10 Feature Importances")
    ax.set_xlabel("Importance")
    st.pyplot(fig)

# === Footer Section ===
st.markdown("""
    <div style='text-align: center; margin-top: 2rem; color: #f9f9f9; font-size: 0.8rem;'>
        © 2025 1. FC Köln & University of Cologne – All rights reserved.
        <br>
        <a href='https://www.fc-koeln.de'>1. FC Köln</a> | <a href='https://www.uni-koeln.de'>University of Cologne</a>
    </div>
    """, unsafe_allow_html=True)

