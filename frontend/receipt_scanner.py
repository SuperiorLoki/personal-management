import streamlit as st
import requests
import pandas as pd
from PIL import Image
import pytesseract
import numpy as np
import cv2
import re
from datetime import datetime

def preprocess_image(img):
    # convert to grayscale image

    # gray = cv2.cvtColor(np.array(img), cv2.COLOR_BGR2GRAY)
    # denoised = cv2.bilateralFilter(gray, 9, 75, 75)
    # clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    # contrast = clahe.apply(denoised)
    # resized_image = cv2.resize(denoised, None, fx=1.5,fy=1.5, interpolation=cv2.INTER_LINEAR)
    # new_img = cv2.adaptiveThreshold(resized_image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 51, 11)

    # 1. Grayscale & 2x Resize (Cubic is best for text)
    gray = cv2.cvtColor(np.array(img), cv2.COLOR_BGR2GRAY)
    resized = cv2.resize(gray, None, fx=2.0, fy=2.0, interpolation=cv2.INTER_CUBIC)

    # 2. Light Blur (This "blends" the faint ghosting into the background)
    blurred = cv2.GaussianBlur(resized, (3, 3), 0)

    # 3. Aggressive Noise Gate
    # This forces light grays/ghosting to white so CLAHE doesn't amplify them
    _, gate = cv2.threshold(blurred, 180, 255, cv2.THRESH_TRUNC)

    # 4. CLAHE (Keep limit low to avoid over-amplifying noise)
    clahe = cv2.createCLAHE(clipLimit=1.5, tileGridSize=(8, 8))
    contrast = clahe.apply(gate)

    # 5. Adaptive Threshold with higher Constant C
    # Increased 11 -> 21 (block size) and 2 -> 10 (constant)
    new_img = cv2.adaptiveThreshold(
        contrast, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY, 21, 10
    )

    kernel = np.ones((2, 2), np.uint8)
    new_img = cv2.erode(new_img, kernel, iterations=1)

    return new_img


def find_total(text):
    pattern = r"\d+\.\d{2}"
    matches = re.findall(pattern, text, re.IGNORECASE | re.MULTILINE)

    if matches:
        return max([float(x) for x in matches])

    return 0.0


def find_date(text):
    # day_pattern = r"(\d{1,2})[/.-]\d{1,2}[./-]\d{2,4}"
    # month_pattern = r"\d{1,2}[/.-](\d{1,2})[./-]\d{2,4}"
    # year_pattern = r"\d{1,2}[/.-]\d{1,2}[./-](\d{2,4})"

    # day = re.findall(day_pattern, text)
    # month = re.findall(month_pattern, text)
    # year = re.findall(year_pattern, text)

    # return day, month, year

    date_pattern = r"(\d{1,2}[/.-]\d{1,2}[./-]\d{2,4})"

    raw_matches = re.findall(date_pattern, text)
    valid_dates = []

    for date_str in raw_matches:
        clean_date = date_str.replace('.', '/').replace('-','/')

        for fmt in ("%m/%d/%y", "%d/%m/%y", "%m/%d/%Y", "%d/%m/%Y"):
            try:
                date_obj = datetime.strptime(clean_date, fmt)

                if 2000 <= date_obj.year <= 2030 or 10<= date_obj.year <= 99:
                    valid_dates.append(date_obj.strftime("%Y-%m-%d"))
                    break
            except ValueError:
                continue
    return list(set(valid_dates))


def find_store(text, known=["Walmart", "Target", "Safeway", "Shell", "Sprouts"]):
    for store in known:
        if store.lower() in text.lower():
            return store
    return text.splitlines()[0]

def check_quality(processed_img):
    # gets data with detailed confidence scores
    data = pytesseract.image_to_data(processed_img, output_type=pytesseract.Output.DATAFRAME)
    valid_conf = data[data.conf != -1]

    if valid_conf.empty:
        return 0, 1.0

    avg_confidence = valid_conf.conf.mean()

    raw_text = "".join(valid_conf['text'].astype(str))
    if len(raw_text)==0: return 0,1.0

    special_chars = sum(1 for char in raw_text if not char.isalnum())
    garbage_ratio = special_chars / len(raw_text)

    return avg_confidence, garbage_ratio


API_URL = "https://personal-management-1.onrender.com"

def scanner():

    st.title("AI Expense Scanner")
    st.markdown("Upload a receipt to automatically extract the store, date, and total cost")

    uploaded_file = st.file_uploader("Choose a receipt image...", type=["jpg", "jpeg", "png"])
    if uploaded_file is not None:
        img = Image.open(uploaded_file)
        st.image(img, caption="Uploaded Receipt", use_container_width=True)

        with st.spinner("Analyzing Image..."):
            confidence, garbage_ratio = check_quality(img)
            if confidence < 50 or garbage_ratio > 0.3:
                st.warning(f"⚠️ Low Quality Image (Confidence: {confidence:.1f}%). Results may be inaccurate.")
            else:
                st.success("✅ Good scan quality detected.")

            text = pytesseract.image_to_string(img)

        store = find_store(text)
        date = find_date(text)
        total = find_total(text)

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




