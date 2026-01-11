import streamlit as st
import google.generativeai as genai

# ၁။ Page Setting
st.set_page_config(page_title="Secure SRT Translator", page_icon="🎬", layout="wide")

# ၂။ Session State များ သတ်မှတ်ခြင်း
if 'api_key' not in st.session_state:
    st.session_state['api_key'] = ""
if 'input_content' not in st.session_state:
    st.session_state['input_content'] = ""
if 'result' not in st.session_state:
    st.session_state['result'] = None

# စာသားများ ရှင်းလင်းသည့် Function
def clear_text():
    st.session_state['input_content'] = ""
    st.session_state['result'] = None

# API Key ဖျက်သည့် Function
def remove_key():
    st.session_state['api_key'] = ""
    st.success("API Key ကို ဖယ်ရှားပြီးပါပြီ။")

# ၃။ Sidebar - API Key Management & Settings
with st.sidebar:
    st.title("🔑 API Settings")
    
    # API Key ရိုက်ထည့်ရန် နေရာ (Password type မို့လို့ အစက်လေးတွေပဲ မြင်ရမယ်၊ မျက်လုံးပုံလေးနှိပ်ရင် ပြန်မြင်ရမယ်)
    user_key = st.text_input("Enter Gemini API Key:", value=st.session_state['api_key'], type="password")
    
    col_k1, col_k2 = st.columns(2)
    with col_k1:
        if st.button("💾 Save Key"):
            st.session_state['api_key'] = user_key
            st.success("Key saved for this session!")
    with col_k2:
        if st.button("🗑️ Remove Key"):
            remove_key()
            st.rerun()

    st.divider()
    st.title("⚙️ Control Panel")
    lang_direction = st.selectbox("Direction:", ["English to Myanmar", "Myanmar to English"])
    version = st.selectbox("Mode:", ["ဆီလျော်အောင် (Cinematic)", "တိတိကျကျ (Literal)"])
    
    if st.button("🗑️ CLEAR ALL TEXT", on_click=clear_text):
        st.rerun()

# ၄။ Main UI
st.title("🎬 PROFESSIONAL SRT TRANSLATOR")

# API Key ရှိမရှိ စစ်ဆေးခြင်း
if not st.session_state['api_key']:
    st.warning("⚠️ ရှေ့ဆက်ရန် API Key ကို Sidebar တွင် အရင်ထည့်ပြီး Save နှိပ်ပေးပါ။")
    st.stop()

# ၅။ Paste Area
input_text = st.text_area(
    "PASTE YOUR SRT HERE:", 
    value=st.session_state['input_content'], 
    height=400, 
    placeholder="1\n00:00:00,300 --> 00:00:05,460\nText here...",
    key="srt_input"
)

# ၆။ Translation Logic
def translate_srt(text, direction, mode, key):
    genai.configure(api_key=key)
    temp = 0.8 if "Cinematic" in mode else 0.2
    lang_prompt = "Translate English to Myanmar." if direction == "English to Myanmar" else "Translate Myanmar to English."
    
    model = genai.GenerativeModel('gemini-1.5-flash', generation_config={"temperature": temp})
    full_prompt = f"Task: {lang_prompt} Keep timestamps. Result only:\n\n{text}"
    
    response = model.generate_content(full_prompt)
    return response.text

# ၇။ Translate Button
if st.button("🚀 START TRANSLATION"):
    if input_text:
        with st.spinner("Processing..."):
            try:
                result = translate_srt(input_text, lang_direction, version, st.session_state['api_key'])
                st.session_state['result'] = result
                st.success("ဘာသာပြန်ခြင်း ပြီးမြောက်ပါပြီ!")
            except Exception as e:
                st.error(f"Error: API Key မှားယွင်းနေပုံရပါသည်။ ({e})")
    else:
        st.warning("စာသား အရင်ထည့်ပါ။")

# ၈။ Download Section
if st.session_state['result']:
    st.divider()
    st.download_button(
        label="📥 DOWNLOAD .SRT FILE",
        data=st.session_state['result'],
        file_name="translated_subtitle.srt",
        mime="text/plain"
    )
    with st.expander("Preview"):
        st.text(st.session_state['result'])
