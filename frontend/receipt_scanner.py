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
import pandas as pd


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
            model="gemini-3.1-flash-lite-preview",
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
        AI_total = data.get("total_cost")

        display_date = date[0] if isinstance(date, list) and date else str(date or "")
        total = 0.0
        if total:
            try:
                total = float(str(total).replace("$", "").strip())
            except ValueError:
                total = 0.0

        st.divider()

        verify_tab, saver_tab = st.tabs(["Verify Information", "AI Price Saver"])
        with verify_tab:
            with st.form("extraction_results"):
                col1, col2 = st.columns(2)

                with col1:
                    final_store = st.text_input("Store Name", value=store)
                    final_date = st.text_input("Date", value=display_date)

                with col2:
                    final_total = st.number_input("Total Cost ($)", value=float(total) if total else 0.0, step=0.01)

                submit_button = st.form_submit_button("Save Expense")

                if submit_button:
                    headers = {"Authorization": f"Bearer {st.session_state.get('token')}"}
                    try:
                        api_date_format = pd.to_datetime(final_date).strftime('%Y-%m-%d')
                    except:
                        st.error("Invalid date format")
                        st.stop()

                    filtered_expenses = {
                        'amount': final_total,
                        'category': 'Shopping',
                        'notes': final_store
                    }
                    try:
                        response = requests.post(f"{API_URL}/expenses/{api_date_format}", json=[filtered_expenses], headers=headers)
                        # st.write(filtered_expenses)
                        if response.status_code == 200:
                            st.balloons()
                            st.success(f"Saved: {final_store} - ${final_total}")
                        else:
                            st.error(f"Failed to update expenses. Status Code: {response.status_code}")
                    except requests.exceptions.RequestException as e:
                        st.error(f"Connection failed: {e}")
        with saver_tab:
            st.markdown("Did you overpay?")
            st.write("Enter your location below. Our AI will re-examine the items and give you cheaper prices from other stores in your area!")
            col_loc, col_btn = st.columns([2,1])
            with col_loc:
                location = st.text_input("City or Zip Code", placeholder="e.g., San Diego, CA or 92101")
            with col_btn:
                check_prices = st.button("Find Cheaper Prices Nearby", use_container_width=True)

            if check_prices:
                if not location:
                    st.warning("Please enter a city name or Zip code")
                else:
                    with st.spinner(f"Analyzing individual items and checking prices..."):
                        try:
                            price_response = client.models.generate_content(
                                model="gemini-3.1-flash-lite-preview",
                                contents=[
                                    f"""You are a concise, smart local shopping assistant. 
                                    Read the individual items and prices on this receipt from {store or 'this store'}. 
                                    The user lives in or near: {location}.
                                    
                                    Provide a brief, scannable Markdown response with NO introductory filler:
                                    
                                    1. **⚡ Quick Verdict:** 1 simple sentence stating if they overpaid for this area and naming the single most overpriced item on the receipt.
                                    2. **📍 Where to Buy Cheaper in {location}:** A bulleted list of the top 2-3 alternative grocery stores or retail chains near them (e.g., Aldi, Trader Joe's, WinCo, Walmart, local markets). For each store, include:
                                       - **The Store Name** (bolded)
                                       - **What to buy there:** Which specific items from their receipt to switch to this store.
                                       - **Estimated Price:** What those items typically cost there compared to what they just paid.
                                    
                                    Keep the entire response short, direct, and focused 100% on the local store alternatives.""",
                                    img
                                ]
                            )
                            st.info(f"**Local Market Analysis for**: {location}")
                            st.markdown(price_response.text)
                        except Exception as e:
                            st.error(f"Failed to generate price comparison: {e}")





