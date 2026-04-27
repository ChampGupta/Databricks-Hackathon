def check_for_anomalies(reported_type, extracted_facts):
    anomalies = []
    risk_score = 0
    
    # Combine all extracted text to search it easily
    capabilities = " ".join(extracted_facts.get("capability", [])).lower()
    equipment = " ".join(extracted_facts.get("equipment", [])).lower()
    services = " ".join(extracted_facts.get("services", [])).lower()
    specialties = " ".join(extracted_facts.get("specialties", [])).lower()
    
    combined_text = f"{capabilities} {equipment} {services} {specialties}"
    
    # Safely handle missing types
    reported_type_str = str(reported_type).lower() if reported_type else "unknown"
    
    # RULE 1: If the registry DOES NOT explicitly say "Hospital", 
    # they shouldn't have advanced tech!
    if "hospital" not in reported_type_str:
        high_tech = ["mri", "ct scanner", "operating theater", "icu", "surgery", "ultrasound", "ecg"]
        
        for item in high_tech:
            if item in combined_text:
                anomalies.append(f"CRITICAL: Registry lists as '{reported_type_str}', but AI extracted {item.upper()}. Possible resource misallocation.")
                risk_score += 2
                
    return {
        "is_flagged": risk_score > 0,
        "risk_score": risk_score,
        "flags": anomalies
    }