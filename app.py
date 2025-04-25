import streamlit as st
import requests
import fitz  # PyMuPDF

st.set_page_config(page_title="PDF AI Reader", layout="centered")

st.title("📄 AI Academic PDF Q&A (Claude 3 Sonnet)")
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

# Step 3: 點按按鈕送出問題給 Claude
if st.button("🤖 開始問 AI"):
    if not uploaded_file or not user_question:
        st.warning("請先上傳 PDF 並輸入問題")
    else:
        # 組 prompt 給 Claude
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

        # 呼叫 Claude 3 Sonnet via OpenRouter
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": "Bearer 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",  # ← 可改為你自己的 OpenRouter API Key
                "Content-Type": "application/json",
            },
            json={
                "model": "anthropic/claude-3-sonnet",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.2,
            },
        )

        try:
            response_json = response.json()

            if "choices" in response_json and len(response_json["choices"]) > 0:
                answer = response_json["choices"][0]["message"]["content"]
                st.markdown("### 🧠 AI 回答：")
                st.markdown(answer)
            else:
                st.error("❌ Claude 回傳格式錯誤，請稍後再試或檢查 API 金鑰與模型名稱是否正確")
                st.json(response_json)

        except Exception as e:
            st.error("❌ 發生錯誤，請確認 API 金鑰或 Claude 回應格式")
            st.exception(e)
