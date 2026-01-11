import streamlit as st
import google.generativeai as genai

# =========================
# 1. Page Config
# =========================
st.set_page_config(
    page_title="Ultimate SRT Translator",
    page_icon="🌐",
    layout="wide"
)

# =========================
# 2. Session State
# =========================
if "api_key" not in st.session_state:
    st.session_state.api_key = ""

if "result" not in st.session_state:
    st.session_state.result = None

def clear_all():
    st.session_state.result = None

# =========================
# 3. Sidebar
# =========================
with st.sidebar:
    st.title("🔑 Gemini API Key")
    api_key = st.text_input(
        "Enter your Gemini API Key",
        value=st.session_state.api_key,
        type="password"
    )

    col1, col2 = st.columns(2)
    with col1:
        if st.button("💾 Save"):
            st.session_state.api_key = api_key
            st.success("API Key saved!")
    with col2:
        if st.button("🗑️ Remove"):
            st.session_state.api_key = ""
            st.session_state.result = None
            st.rerun()

    st.divider()
    st.title("⚙️ Settings")
    lang_pair = st.selectbox(
        "Language Pair",
        [
            "English to Myanmar",
            "Korea to English",
            "Chinese to English",
            "Korea to Myanmar",
            "Chinese to Myanmar"
        ]
    )

    style_mode = st.selectbox(
        "Translation Style",
        [
            "ဆီလျော်အောင် (Cinematic)",
            "တိတိကျကျ (Literal)"
        ]
    )

    if st.button("🗑️ CLEAR ALL", on_click=clear_all):
        st.rerun()

# =========================
# 4. Main UI
# =========================
st.title("🌐 MULTI-LANGUAGE SRT TRANSLATOR")

if not st.session_state.api_key:
    st.warning("⚠️ Sidebar မှာ Gemini API Key ထည့်ပြီး Save လုပ်ပါ")
    st.stop()

input_text = st.text_area(
    "PASTE YOUR SRT CONTENT",
    height=350,
    placeholder="1\n00:00:01,000 --> 00:00:04,000\nText here..."
)

# =========================
# 5. Translation Engine (429-safe)
# =========================
def translate_engine(text, pair, style, api_key):
    genai.configure(api_key=api_key)

    temperature = 0.8 if "Cinematic" in style else 0.2
    source_lang, target_lang = pair.split(" to ")

    # ✅ Free Tier safe models only
    model_list = [
        "gemini-1.5-flash",  # Free Tier friendly
        "gemini-1.5-pro"     # Paid / higher quota
        # "gemini-2.0-flash-exp" # Optional, heavy quota, commented out
    ]

    prompt = f"""
You are a professional subtitle translator.

Translate SRT subtitles from {source_lang} to {target_lang}.
- Keep original timestamps
- Keep subtitle numbering
- Natural and clear translation
- Output SRT format only

SRT CONTENT:
{text}
"""

    last_error = ""
    for model_name in model_list:
        try:
            model = genai.GenerativeModel(
                model_name=model_name,
                generation_config={
                    "temperature": temperature,
                    "max_output_tokens": 8192
                }
            )
            response = model.generate_content(prompt)
            return response.text

        except Exception as e:
            last_error = str(e)
            continue  # fallback next model

    return f"ERROR: {last_error}"

# =========================
# 6. Start Button
# =========================
if st.button("🚀 START TRANSLATING"):
    if not input_text.strip():
        st.warning("SRT text ထည့်ပါ")
    else:
        with st.spinner("Translating with Gemini..."):
            result = translate_engine(
                input_text,
                lang_pair,
                style_mode,
                st.session_state.api_key
            )

            if result.startswith("ERROR:"):
                st.error(result)
                st.info("👉 Free Tier quota မကျော်မနေမီ gemini-1.5-flash သုံးပါ / Paid Key Upgrade လုပ်ပါ")
            else:
                st.session_state.result = result
                st.success("✅ Translation Complete")

# =========================
# 7. Result & Download
# =========================
if st.session_state.result:
    st.divider()

    default_name = lang_pair.replace(" ", "_") + "_sub"
    file_name = st.text_input("Rename file", value=default_name)

    if not file_name.endswith(".srt"):
        file_name += ".srt"

    st.download_button(
        label=f"📥 DOWNLOAD {file_name}",
        data=st.session_state.result,
        file_name=file_name,
        mime="text/plain"
    )

    with st.expander("👀 Preview Result"):
        st.text(st.session_state.result)
