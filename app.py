
import streamlit as st
import requests
import fitz  # PyMuPDF
import os

st.set_page_config(page_title="PDF Scholar QA", layout="centered")

st.title("📄 AI Scholar (Claude 3 PDF QA)")
st.caption("上傳一篇學術 PDF，提問問題，AI 只根據該論文回答。")

uploaded_file = st.file_uploader("請上傳 PDF 論文", type=["pdf"])

question = st.text_input("你想問這篇論文什麼問題？")

if uploaded_file and question:
    with st.spinner("正在讀取 PDF..."):
        doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
        pdf_text = ""
        for page in doc:
            pdf_text += page.get_text()

    with st.spinner("AI 正在思考中..."):
        headers = {
            "Authorization": f"Bearer {st.secrets['OPENROUTER_API_KEY']}",
            "Content-Type": "application/json"
        }

        prompt = f"""
You are an academic assistant that only answers based on the uploaded paper. Do not use external knowledge.

Rules:
- Only answer if the paper directly mentions the information.
- Use formal academic tone (like Nature, Cell, Science).
- If not found in the paper, say: "This information is not explicitly stated in the paper."
- Answer must include:
  * Reasoning logic
  * Paragraph citation (e.g., Page 4, Paragraph 3)
  * If multiple paragraphs support it, cite them all
  * Confidence score in percentage

Question:
{question}

PDF Content:
{pdf_text}
"""

        data = {
            "model": "anthropic/claude-3-sonnet",
            "messages": [
                {"role": "user", "content": prompt}
            ]
        }

        response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data)

        if response.status_code == 200:
            result = response.json()
            answer = result["choices"][0]["message"]["content"]
            st.markdown("### 🎓 Claude 回答")
            st.write(answer)
        else:
            st.error("API 請求失敗，請確認 API Key 是否正確")
