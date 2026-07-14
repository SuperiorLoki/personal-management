import streamlit as st
import requests
import pandas as pd
from google import genai

API_URL = "https://personal-management-1.onrender.com"

def ai_chat():
    st.header("Manage your Expenses")
    st.write("Ask our AI assistant anything about your spending habits, trends, or specific purchases!")

    if "chat_messages" not in st.session_state:
        st.session_state["chat_messages"] = [
            {"role": "assistant", "content": "Hi! I'm your personal financial analyst. Ask me questions like: *'How much did I spend on Food this month?'* or *'What is my single most expensive purchase?'*"}
        ]
    
    for message in st.session_state["chat_messages"]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if user_question := st.chat_input("Ask a question about your spending..."):
        st.session_state["chat_messages"].append({"role": "user", "content": user_question})
        with st.chat_message("user"):
            st.markdown(user_question)

        headers = {"Authorization": f"Bearer {st.session_state.get('token')}"}
        response = requests.get(f"{API_URL}/report", headers=headers)

        if response.status_code == 200 and response.json():
            df = pd.DataFrame(response.json())
            if 'id' in df.columns:
                df = df.drop('id', axis=1)
            data_context = df.to_string(index=False)
        else:
            data_context = "No expense data recorded yet for this user."

        with st.chat_message("assistant"):
            with st.spinner("Analyzing your financial records..."):
                try:
                    api_key = st.secrets["GEMINI_API_KEY"]
                    client = genai.Client(api_key=api_key)
                    
                    # Build the RAG prompt combining their data + their question
                    prompt = f"""
                    You are a friendly, highly intelligent financial assistant for an expense tracking app.
                    
                    Here is the user's complete expense history database:
                    {data_context}
                    
                    The user asks: "{user_question}"
                    
                    Instructions:
                    - Answer their question accurately using ONLY the data provided above.
                    - Do not mention the word "dataframe" or "string". Talk like a real human analyst.
                    - If they ask for advice or trends, give proactive, helpful money-saving tips.
                    - Keep your response formatted cleanly with Markdown bold text and bullet points where helpful.
                    """
                    
                    ai_response = client.models.generate_content(
                        model="gemini-3.1-flash-lite-preview",
                        contents=prompt
                    )

                    reply_text = ai_response.text
                    st.markdown(reply_text)

                    st.session_state["chat_messages"].append({"role": "assistant", "content": reply_text})
                except Exception as e:
                    error_msg = f"Sorry, I ran into an error connecting to Gemini: {e}"
                    st.error(error_msg)
