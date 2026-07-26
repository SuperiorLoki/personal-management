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
from google.genai import types
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
        prompt = """
        You are an expert receipt analyzer for an expense tracking app. 
        Analyze the attached receipt image and extract the key information.
        
        Return EXACTLY a valid JSON object with the following keys and no other text or markdown formatting:
        {
            "amount": (The final grand total on the receipt as a float. Do not include currency symbols. Should be just the float value),
            "category": (MUST be one of: "Rent", "Shopping", "Entertainment", "Travel", "Other"),
            "store_name": (The name of the store or merchant),
            "date": (The date on the receipt in YYYY-MM-DD format. If no date is visible, use today's date)
        }
        """
        response = client.models.generate_content(
            model="gemini-3.1-flash-lite-preview",
            contents=[prompt,img]
        )
        raw_text = response.text.strip().replace("```json", "").replace("```", "").strip()

        data = json.loads(raw_text)
        if "error" in data and data["error"] == "invalid_image":
            st.error("This doesn't look like a receipt! Please upload a clear photo of your bill.")
            st.stop()
        store = data.get("store_name", "")
        date = data.get("date", datetime.today().strftime('%Y-%m-%d'))
        category_str = data.get("category", "Shopping")


        display_date = date[0] if isinstance(date, list) and date else str(date or "")
        total = data.get("amount")
        if total:
            try:
                total = float(str(total).replace("$", "").strip())
            except ValueError as e:
                st.write(e)
                total = 999.999

        st.divider()

        verify_tab, saver_tab = st.tabs(["Verify Information", "AI Price Saver"])
        with verify_tab:
            with st.form("extraction_results"):
                col1, col2, col3 = st.columns(3)

                with col1:
                    final_store = st.text_input("Store Name", value=store)
                    final_date = st.text_input("Date", value=display_date)
                with col2:
                    final_total = st.number_input("Total Cost ($)", value=float(total) if total else 0.0, step=0.01)
                with col3:
                    categories = ["Rent", "Food", "Shopping", "Entertainment", "Travel", "Other"]
                    safe_idx = categories.index(category_str) if category_str in categories else 2
                    final_category = st.selectbox("Category", options=categories, index=safe_idx)

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
                        'category': final_category,
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
                            prompt = f"""You are an expert personal finance and shopping advisor. 
                            Look at the individual items and prices listed on this receipt from {store or 'this store'}. 
                            The user lives in or near: {location}.
                            
                            CRITICAL INSTRUCTIONS: 
                            - You must provide factually accurate, hyper-local information. 
                            - Do NOT guess or hallucinate store names. 
                            - ONLY recommend alternative grocery chains or markets that you know for a fact operate in {location}.
                            
                            Please provide a clean, helpful analysis formatted in Markdown:
                            1. **Price Evaluation:** Did they pay high, average, or low prices for these types of goods in {location}? Call out 1 or 2 specific items if they seem overpriced.
                            2. **Accurate Local Alternatives:** Recommend 2 to 3 alternative stores geographically available in {location} where they could likely buy these same items for less. 
                            3. **Actionable Tip:** Give 1 quick budgeting tip specific to saving money on these specific items next time.
                            Keep the tone encouraging, concise, and easy to read."""
                            
                            price_response = client.models.generate_content(
                                model="gemini-3.1-flash-lite-preview",
                                contents=[prompt,img]
                            )

                            st.info(f"**Local Market Analysis for**: {location}")
                            st.markdown(price_response.text)
                        except Exception as e:
                            st.error(f"Failed to generate price comparison: {e}")
