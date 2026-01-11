import streamlit as st
import google.generativeai as genai

# ၁။ Page Setting
st.set_page_config(page_title="Ultimate SRT Translator", page_icon="🌐", layout="wide")

# ၂။ Session State
if 'api_key' not in st.session_state:
    st.session_state['api_key'] = ""
if 'result' not in st.session_state:
    st.session_state['result'] = None

def clear_text():
    st.session_state['result'] = None

# ၃။ Sidebar Settings
with st.sidebar:
    st.title("🔑 API Access")
    user_key = st.text_input("Enter Gemini API Key:", value=st.session_state['api_key'], type="password")
    
    col_k1, col_k2 = st.columns(2)
    with col_k1:
        if st.button("💾 Save Key"):
            st.session_state['api_key'] = user_key
            st.success("Key saved!")
    with col_k2:
        if st.button("🗑️ Remove Key"):
            st.session_state['api_key'] = ""
            st.session_state['result'] = None
            st.rerun()

    st.divider()
    st.title("⚙️ Control Panel")
    lang_pair = st.selectbox(
        "Select Language Pair:",
        ["English to Myanmar", "Korea to English", "Chinese to English", "Korea to Myanmar", "Chinese to Myanmar"]
    )
    version = st.selectbox("Style Mode:", ["ဆီလျော်အောင် (Cinematic)", "တိတိကျကျ (Literal)"])
    if st.button("🗑️ CLEAR ALL", on_click=clear_text):
        st.rerun()

# ၄။ Main UI
st.title("🌐 MULTI-LANGUAGE SRT TRANSLATOR")

if not st.session_state['api_key']:
    st.warning("⚠️ Please enter and save your API Key in the sidebar.")
    st.stop()

# ၅။ Input Area
input_text = st.text_area("PASTE YOUR SRT CONTENT:", height=350, placeholder="1\n00:00:01,000 --> 00:00:04,000\nText here...")

# ၆။ Translation Engine (Gemini 2.5/2.0 & 1.5 Compatibility Fix)
def translate_engine(text, pair, mode, key):
    try:
        genai.configure(api_key=key)
        temp = 0.8 if "Cinematic" in mode else 0.2
        source_lang, target_lang = pair.split(" to ")
        
        # မော်ဒယ်နာမည်များကို အစဉ်လိုက် စမ်းသပ်ခြင်း (404 Error ကျော်လွှားရန်)
        # ၁။ ပထမဦးဆုံး gemini-1.5-flash-latest ကို စမ်းပါ
        # ၂။ မရပါက gemini-1.5-flash ကို စမ်းပါ
        model_names = ['gemini-1.5-flash-latest', 'gemini-1.5-flash', 'gemini-2.0-flash-exp']
        
        last_error = ""
        for m_name in model_names:
            try:
                model = genai.GenerativeModel(model_name=m_name, generation_config={"temperature": temp})
                prompt = f"Professional SRT Translation: {source_lang} to {target_lang}. Keep timing. Result only:\n\n{text}"
                response = model.generate_content(prompt)
                return response.text
            except Exception as e:
                last_error = str(e)
                continue # နောက်ထပ် မော်ဒယ်နာမည်တစ်ခုဖြင့် ထပ်စမ်းပါ
        
        return f"ERROR: {last_error}"
        
    except Exception as e:
        return f"ERROR: {str(e)}"

# ၇။ Start Button
if st.button("🚀 START TRANSLATING"):
    if input_text:
        with st.spinner(f"Processing with latest Gemini model..."):
            result = translate_engine(input_text, lang_pair, version, st.session_state['api_key'])
            
            if "ERROR:" in result:
                st.error(f"❌ {result}")
                st.info("API Key ကို Google AI Studio မှာ အသစ်ပြန်ထုတ်ပြီး စမ်းကြည့်ဖို့ အကြံပြုလိုပါတယ်။")
            else:
                st.session_state['result'] = result
                st.success("Done!")
    else:
        st.warning("Please paste some text.")

# ၈။ Result & Rename Download
if st.session_state['result']:
    st.divider()
    default_name = f"{lang_pair.replace(' ', '_')}_sub"
    custom_name = st.text_input("Rename File:", value=default_name)
    final_name = f"{custom_name}.srt" if not custom_name.endswith(".srt") else custom_name

    st.download_button(
        label=f"📥 DOWNLOAD {final_name}",
        data=st.session_state['result'],
        file_name=final_name,
        mime="text/plain"
    )
    with st.expander("Preview"):
        st.text(st.session_state['result'])
