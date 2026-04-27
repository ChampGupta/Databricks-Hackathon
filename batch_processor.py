import pandas as pd
import json
import time  # <-- NEW: We need this to slow down the loop!
from idp_extractor import extract_facility_data
from auditor import check_for_anomalies

def get_real_data():
    df = pd.read_csv('Virtue Foundation Ghana v0.3 - Sheet1.csv')
    df = df.dropna(subset=['description'])
    df = df[df['description'].astype(str).str.len() > 10]
    
    # Let's do exactly 5 for the demo so we stay safely under 6,000 tokens
    return df.head(900) 

def process_real_batch(df_slice):
    results = []
    
    # Optional: If you want to show progress in Streamlit
    import streamlit as st
    progress_bar = st.progress(0)
    total_rows = len(df_slice)
    
    for i, (_, row) in enumerate(df_slice.iterrows()):
        raw_text = str(row['description'])
        
        # 1. Run AI
        facts = extract_facility_data(raw_text)
        extracted_dict = json.loads(facts.model_dump_json())
        
        # 2. Run Auditor
        audit = check_for_anomalies(row['facilityTypeId'], extracted_dict)
        
        results.append({
            "facility_id": row.get('unique_id', 'N/A'),
            "name": row['name'],
            "reported_type": row['facilityTypeId'],
            "city": row.get('address_city', 'Accra'),
            "description": raw_text,
            "extracted_data": extracted_dict,
            "audit_report": audit
        })
        
        # Update progress bar
        progress_bar.progress((i + 1) / total_rows)
        
        # 3. THE MAGIC FIX: Pause for 4 seconds so Groq doesn't ban us
        time.sleep(4) 
        
    return results