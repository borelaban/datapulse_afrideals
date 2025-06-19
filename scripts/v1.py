import streamlit as st
import pandas as pd
from thefuzz import fuzz
import time

# --- Dummy Databases --- #
@st.cache_data
def load_dummy_data():
    # Dummy UFAA records
    ufaa_data = pd.DataFrame([
        {"ufaa_id": "UF-001", "name": "Jane Wanjiru", "id": "12345678", "kra_pin": "A001JW", "phone": "0722111222", "amount": 4500}
    ])
    
    # Dummy KRA records (simulated API)
    kra_data = pd.DataFrame([
        {"kra_pin": "A001JW", "registered_name": "J. WANJIRU"}
    ])
    
    # Dummy Telco records (simulated Safaricom API)
    telco_data = pd.DataFrame([
        {"phone": "0722111222", "registered_name": "JANE WANJIRU", "id_number": "12345678"}
    ])
    return ufaa_data, kra_data, telco_data

ufaa_df, kra_df, telco_df = load_dummy_data()

# --- AI Name Matching Function --- #
def check_name_match(name1, name2):
    """Returns True if fuzzy match confidence > 85%"""
    return fuzz.ratio(name1.upper(), name2.upper()) > 85

# --- Simulated Safaricom API Check --- #
def verify_phone(phone, id_number):
    """Check if phone is registered to the given ID in dummy telco data"""
    match = telco_df[(telco_df["phone"] == phone) & (telco_df["id_number"] == id_number)]
    return not match.empty

# --- Streamlit UI --- #
st.title("📑 UFAA Automated Claims Pilot")
st.divider()

# Step 1: User Input
id_number = st.text_input("Enter your ID Number:")
if id_number:
    user_data = ufaa_df[ufaa_df["id"] == id_number]
    
    if not user_data.empty:
        st.success(f"✅ Found unclaimed assets: **Sh{user_data['amount'].values[0]:,}**")
        name, kra_pin, phone = user_data[["name", "kra_pin", "phone"]].values[0]
        
        # --- Automated Step 1: AI Name Matching (ID vs. KRA) --- #
        kra_name = kra_df[kra_df["kra_pin"] == kra_pin]["registered_name"].values[0]
        st.write(f"**ID Name:** `{name}` | **KRA Name:** `{kra_name}`")
        
        if check_name_match(name, kra_name):
            st.success("✅ Names match (no affidavit needed).")
            
            # --- Automated Step 2: Safaricom API Check --- #
            if verify_phone(phone, id_number):
                st.success(f"✅ Phone {phone} verified with ID {id_number}.")
                
                # --- Automated Step 3: E-Signature Flow --- #
                st.divider()
                st.subheader("Step 3: Lawyer E-Signature")
                lawyer_email = st.text_input("Enter lawyer's email for Form 5 signing:")
                
                if lawyer_email:
                    if st.button("Send E-Signature Request"):
                        with st.spinner("Sending to lawyer..."):
                            time.sleep(2)
                            st.success(f"📨 Sent Form 5 to {lawyer_email} for signing.")
                            
                            # Simulate lawyer signing
                            time.sleep(3)
                            st.balloons()
                            st.success("✅ Form 5 signed! Disbursing Sh4,500 to 0722111222...")
            else:
                st.error("❌ Phone not linked to this ID. Manual review required.")
        else:
            st.warning("⚠️ Name mismatch detected. [Generate Affidavit Draft](#)")
    else:
        st.error("❌ No unclaimed assets found.")