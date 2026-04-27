import pandas as pd
import json
import time
from idp_extractor import extract_facility_data
from auditor import check_for_anomalies

def build_full_registry():
    print("🚀 Initializing Full-Scale Extraction (988 Rows)...")
    df = pd.read_csv('Virtue Foundation Ghana v0.3 - Sheet1.csv')
    
    # Cleaning: Remove rows with no descriptions or very short text
    df = df.dropna(subset=['description'])
    df = df[df['description'].astype(str).str.len() > 15]
    
    processed_results = []
    
    for i, (_, row) in enumerate(df.iterrows()):
        name = row['name']
        print(f"[{i+1}/{len(df)}] Analyzing {name}...")
        
        try:
            # 1. AI Extraction
            facts = extract_facility_data(str(row['description']))
            extracted_dict = json.loads(facts.model_dump_json())
            
            # 2. Anomaly Auditing
            audit = check_for_anomalies(row['facilityTypeId'], extracted_dict)
            
            processed_results.append({
                "unique_id": row.get('unique_id', i),
                "name": name,
                "type": row['facilityTypeId'],
                "city": row.get('address_city', 'Accra'),
                "description": row['description'],
                "facts": extracted_dict,
                "audit": audit
            })
            
            # Save progress every 5 rows in case of internet flicker
            if i % 5 == 0:
                with open("processed_ghana_data.json", "w") as f:
                    json.dump(processed_results, f, indent=4)
            
            # Pacing: 8 seconds ensures we stay under the 6,000 TPM limit
            time.sleep(8)
            
        except Exception as e:
            print(f"❌ Error on {name}: {e}")
            continue

    print("✅ Database built: processed_ghana_data.json")

if __name__ == "__main__":
    build_full_registry()