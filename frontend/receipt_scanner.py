import streamlit as st
import requests
import pandas as pd
from PIL import Image
import pytesseract
import numpy as np
import cv2
import re
from datetime import datetime
import json
import PIL.Image
from google import genai


API_URL = "https://personal-management-1.onrender.com"

def scanner():

    st.title("AI Expense Scanner")
    st.markdown("Upload a receipt to automatically extract the store, date, and total cost")

    uploaded_file = st.file_uploader("Choose a receipt image...", type=["jpg", "jpeg", "png", "pdf", "webp", "heic"])
    
    if uploaded_file is not None:
        api_key = st.secrets["GEMINI_API_KEY"]
        client = genai.Client(api_key=api_key)
        img = PIL.Image.open(uploaded_file)
        st.image(img, caption="Uploaded Receipt", use_column_width=True)
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[
                """Extract store_name, date, and total_cost from this receipt as JSON. For total_cost, extract 
                only numerical value. Default values of Unkown, 99/99/9999, and 0.00, if any values are missing. 
                If the image is NOT a receipt (e.g., a person, a pet, or a random object), return only this 
                JSON: {"error": "invalid_image"}""",
                img
            ]
        )
        raw_text = response.text.strip().replace("```json", "").replace("```", "").strip()

        data = json.loads(raw_text)
        if "error" in data and data["error"] == "invalid_image":
            st.error("This doesn't look like a receipt! Please upload a clear photo of your bill.")
            st.stop()
        store = data.get("store_name")
        date = data.get("date")
        total = data.get("total_cost")

        if isinstance(date, list) and len(date) > 0:
            display_date = date[0]
        elif isinstance(date, str):
            display_date = date
        else:
            display_date = ""


        st.subheader("Verify Information")
        with st.form("extraction_results"):
            col1, col2 = st.columns(2)

            with col1:
                final_store = st.text_input("Store Name", value=store)
                final_date = st.text_input("Date", value=display_date)

            with col2:
                final_total = st.number_input("Total Cost ($)", value=float(total) if total else 0.0, step=0.01)

            submit_button = st.form_submit_button("Save Expense")

            if submit_button:
                filtered_expenses = {
                    'amount': final_total,
                    'category': 'Shopping',
                    'notes': final_store
                }
                try:
                    response = requests.post(f"{API_URL}/expenses/{final_date}", json=[filtered_expenses])
                    # st.write(filtered_expenses)
                    if response.status_code == 200:
                        st.balloons()
                        st.success(f"Saved: {final_store} - ${final_total}")
                    else:
                        st.error("Failed to update expenses.")
                except requests.exceptions.RequestException as e:
                    st.error(f"Connection failed: {e}")








