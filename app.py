import streamlit as st
import requests
import fitz  # PyMuPDF

st.set_page_config(page_title="PDF AI Reader", layout="centered")

st.title("📄 AI Academic PDF Q&A (GPT 3.5)")
st.markdown("上傳一份 PDF 論文 → 輸入問題 → AI 僅根據該論文內容作答")

# Step 1: 上傳 PDF 並轉成文字
uploaded_file = st.file_uploader("請上傳 PDF 論文", type=["pdf"])
pdf_text = ""

if uploaded_file:
    with fitz.open(stream=uploaded_file.read(), filetype="pdf") as doc:
        for page in doc:
            pdf_text += page.get_text()

    st.success("✅ 論文已成功解析")

# Step 2: 使用者輸入問題
user_question = st.text_input("請輸入你對論文的問題（英文或中文皆可）")

# Step 3: 點按按鈕送出問題給 GPT
if st.button("🤖 開始問 AI"):
    if not uploaded_file or not user_question:
        st.warning("請先上傳 PDF 並輸入問題")
    else:
        # 組 prompt 給 GPT
        prompt = f"""
You are an expert academic assistant. Only answer based on the provided paper content below.
Do not use any external knowledge or assumptions.

📌 Rules:
- Answer in professional academic English (e.g., Nature, Science tone)
- Only use information found in the paper.
- If the answer is not clearly stated, say: "This information is not explicitly stated in the paper."
- Include reasoning logic, citation of the source paragraph (e.g., Page 4, Paragraph 2), and confidence in %.

--- START OF PAPER ---
{pdf_text}
--- END OF PAPER ---

Question: {user_question}
Answer:
"""

        # 使用免費的 GPT 3.5 (openrouter.run)
        try:
            response = requests.post(
                "https://openrouter.run/api/v1/chat/completions",
                headers={"Content-Type": "application/json"},
                json={
                    "model": "openai/gpt-3.5-turbo",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.3,
                },
                timeout=30,
            )

            answer = response.json()["choices"][0]["message"]["content"]
            st.markdown("### 🧠 AI 回答：")
            st.markdown(answer)

        except Exception as e:
            st.error("❌ 發生錯誤，請稍後再試，或 API 無法連線")
            st.exception(e)
