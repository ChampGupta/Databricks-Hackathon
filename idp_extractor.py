import streamlit as st
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from agent_schema import FacilityFacts

api_key = st.secrets["GROQ_API_KEY"]

llm = ChatGroq(
    model="llama-3.1-8b-instant", 
    temperature=0, 
    groq_api_key=api_key
)

structured_llm = llm.with_structured_output(FacilityFacts)

# NEW: We are giving the AI very strict rules so it doesn't return empty lists
prompt = ChatPromptTemplate.from_messages([
    ("system", """You are an expert medical data extractor. You MUST meticulously extract all medical entities from the text into the JSON.
    - specialties: Fields of medicine (e.g., Pediatrics, Gynecology, Obstetrics, Eye Care).
    - services: Treatments/Care (e.g., Pharmacy, Laboratory, Outpatient, Consultation, Prevention).
    - equipment: Physical machines (e.g., Ultrasound, ECG, X-Ray, Scan).
    - capability: Facility level descriptors (e.g., Primary hospital, 24-hour service).
    Do NOT return empty lists if the information exists in the text. Extract EVERYTHING."""),
    ("human", "Medical note: {medical_note}")
])

extraction_chain = prompt | structured_llm

def extract_facility_data(medical_note: str):
    if not medical_note or str(medical_note).lower() == "nan":
        return FacilityFacts()
    try:
        return extraction_chain.invoke({"medical_note": medical_note})
    except Exception as e:
        print(f"Extraction Error: {e}")
        return FacilityFacts()