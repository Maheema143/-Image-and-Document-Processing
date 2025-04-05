import streamlit as st
import google.generativeai as genai
import json
import re

# Configure Gemini API
genai.configure(api_key="AIzaSyCc4B5Og2hOxnERFBSp95iQ9aT-urSCKM8")
model = genai.GenerativeModel("gemini-1.5-pro-latest")  # Ensure correct model version

def preprocess_text(text: str) -> str:
    """Preprocess text by removing punctuation, numbers, and extra spaces."""
    text = text.lower()
    text = re.sub(r'[^\w\s]', '', text)  # Remove punctuation
    text = re.sub(r'\d+', '', text)  # Remove numbers
    text = re.sub(r'\s+', ' ', text).strip()  # Remove extra spaces
    return text

def extract_json(response_text):
    """Extract valid JSON from Gemini's response using regex."""
    try:
        match = re.search(r"\{.*\}", response_text, re.DOTALL)  # Extract JSON block
        if match:
            return json.loads(match.group())  # Convert string to JSON
        else:
            st.error("⚠️ No valid JSON found in Gemini's response.")
            return None
    except json.JSONDecodeError as e:
        st.error(f"⚠️ JSON Parsing Error: {str(e)}")
        return None

def classify_complaint(complaint: str, user_type: str):
    """Classify the complaint using Gemini API."""
    prompt = f"""
    Classify the following food complaint:
    
    Complaint: "{complaint}"
    User Type: {user_type}
    
    Return the response as valid JSON **only**, following this structure:
    {{
        "department": "Predicted Department",
        "category": "User-Specific Category",
        "priority": "Priority Level (HIGH, MEDIUM, LOW, URGENT)",
        "keywords": ["List of related keywords"],
        "emergency_flag": true/false
    }}
    """

    try:
        response = model.generate_content(prompt)
        
        if not response or not response.text.strip():  # Check for empty response
            st.error("⚠️ Empty response from Gemini API. Please try again.")
            return None

        raw_text = response.text.strip()
        
        # Debugging output
        st.write("🔍 **Raw Response from Gemini:**")
        st.code(raw_text, language="json")  

        # Extract and return JSON data
        return extract_json(raw_text)

    except Exception as e:
        st.error(f"❌ Error communicating with Gemini API: {str(e)}")
        return None

# Streamlit UI
st.title("🔍 Food Complaint Classifier")
st.write("🚀 Automated Mapping and Categorization for Food Industry Complaints")

# User input
default_text = "Describe your complaint here..."
complaint = st.text_area("📝 Enter Complaint:", value="", placeholder=default_text, height=150)
user_type = st.selectbox("👤 Select User Type:", ["Consumer", "Retailer", "Supplier"])

# Button to classify complaint
if st.button("🔎 Classify Complaint"):
    if complaint.strip():  # Ensure valid input
        complaint = preprocess_text(complaint)
        
        with st.spinner("Processing... 🔄"):
            result = classify_complaint(complaint, user_type)

        if result:
            st.success("✅ Classification Results:")
            st.markdown(f"""
            - **🏢 Department:** {result.get('department', 'N/A')}
            - **📌 Category:** {result.get('category', 'N/A')}
            - **⚡ Priority Level:** {result.get('priority', 'N/A')}
            - **🔑 Keywords:** {', '.join(result.get('keywords', []))}
            - **🚨 Emergency Alert:** {'✅ Yes' if result.get('emergency_flag') else '❌ No'}
            """)
        else:
            st.error("❌ Failed to classify complaint. Please try again.")

    else:
        st.warning("⚠️ Please enter a valid complaint.")
