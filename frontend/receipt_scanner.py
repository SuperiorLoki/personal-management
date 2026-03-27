import streamlit as st
import requests
import pandas as pd
from PIL import Image
import pytesseract
import scanner_util
import numpy as np


API_URL = "https://personal-management-1.onrender.com"

def scanner():
    st.set_page_config(page_title="Expense Tracker", layout="centered")

    st.title("AI Expense Scanner")
    st.markdown("Upload a receipt to automatically extract the store, date, and total cost")

    uploaded_file = st.file_uploader("Choose a receipt image...", type=["jpg", "jpeg", "png"])
    if uploaded_file is not None:
        img = Image.open(uploaded_file)
        st.image(img, caption="Uploaded Receipt", use_container_width=True)

        with st.spinner("Analyzing Image..."):
            confidence, garbage_ratio = scanner_util.check_quality(img)
            if confidence < 50 or garbage_ratio > 0.3:
                st.warning(f"⚠️ Low Quality Image (Confidence: {confidence:.1f}%). Results may be inaccurate.")
            else:
                st.success("✅ Good scan quality detected.")

            text = pytesseract.image_to_string(img)

        store = scanner_util.find_store(text)
        date = scanner_util.find_date(text)
        total = scanner_util.find_total(text)

        st.subheader("Verify Information")
        with st.form("extraction_results"):
            col1, col2 = st.columns(2)

            with col1:
                final_store = st.text_input("Store Name", value=store)
                final_date = st.text_input("Date", value=str(date))

            with col2:
                final_total = st.number_input("Total Cost ($)", value=float(total) if total else 0.0, step=0.01)

            submit_button = st.form_submit_button("Save Expense")

            if submit_button:
                st.balloons()
                st.success(f"Saved: {final_store} - ${final_total}")


