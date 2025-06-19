import streamlit as st
import pandas as pd
from thefuzz import fuzz
import time

# --- SETUP --- #
st.set_page_config(page_title="UFAA AutoClaim Pilot", layout="wide")

# --- DUMMY DATA --- #
@st.cache_data
def load_data():
    # UFAA records
    ufaa_data = pd.DataFrame([
        {"ufaa_id": "UF-001", "name": "John Kariuki", "id": "12345678", "phone": "0722000000", "amount": 4500},
        {"ufaa_id": "UF-002", "name": "Wanjiru Muthoni", "id": "87654321", "phone": None, "amount": 3200},
        {"ufaa_id": "UF-003", "name": "James Omondi", "id": "13579246", "phone": "0733000000", "amount": 5000}
    ])
    
    # Telco records (simulated API response)
    telco_data = pd.DataFrame([
        {"phone": "0722000000", "registered_name": "JOHN KARIUKI KAMAU", "status": "active"},
        {"phone": "0733000000", "registered_name": "JAMES OMONDI", "status": "active"}
    ])
    return ufaa_data, telco_data

ufaa_df, telco_df = load_data()

# --- AI MATCHING FUNCTION --- #
def match_ufaa_to_telco(ufaa_name, telco_name):
    """Fuzzy name matching (0-100% confidence)"""
    return fuzz.ratio(ufaa_name.upper(), telco_name.upper())

# --- STREAMLIT UI --- #
st.title("🚀 UFAA AutoClaim Pilot")
tab1, tab2 = st.tabs(["User Claim", "Admin Dashboard"])

# TAB 1: USER CLAIM FLOW
with tab1:
    st.subheader("Check for Unclaimed Assets")
    user_id = st.text_input("Enter your ID Number:")
    
    if user_id:
        # Check UFAA records
        user_data = ufaa_df[ufaa_df["id"] == user_id]
        
        if not user_data.empty:
            st.success(f"✅ Found unclaimed assets: **Sh{user_data['amount'].values[0]:,}**")
            name = user_data["name"].values[0]
            phone = user_data["phone"].values[0]
            
            # Simulate telco API check
            if phone:
                telco_record = telco_df[telco_df["phone"] == phone]
                if not telco_record.empty:
                    telco_name = telco_record["registered_name"].values[0]
                    confidence = match_ufaa_to_telco(name, telco_name)
                    
                    if confidence > 85:
                        st.markdown(f"""
                        **AI Verification Result**  
                        - UFAA Name: `{name}`  
                        - Telco Name: `{telco_name}`  
                        - **Confidence: {confidence}%**  
                        """)
                        
                        if st.button("Claim via M-Pesa"):
                            with st.spinner("Processing payment..."):
                                time.sleep(2)
                                st.success(f"✅ Sh{user_data['amount'].values[0]:,} sent to {phone}!")
                    else:
                        st.warning("Manual review needed (low confidence match).")
                else:
                    st.warning("Phone not active in telco records.")
            else:
                st.warning("No phone on record. Visit UFAA office.")
        else:
            st.error("No unclaimed assets found.")

# TAB 2: ADMIN DASHBOARD
with tab2:
    st.subheader("Pilot Performance Metrics")
    col1, col2, col3 = st.columns(3)
    
    # Simulated metrics
    col1.metric("Total Claims Processed", "1,024")
    col2.metric("Auto-Approval Rate", "88%")
    col3.metric("Avg. Processing Time", "3.2 mins")
    
    st.divider()
    st.dataframe(ufaa_df)  # Show UFAA dummy data
