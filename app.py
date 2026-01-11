import streamlit as st
import google.generativeai as genai

# ၁။ Page Setting
st.set_page_config(page_title="Pro Multi-Lang SRT Master", page_icon="🌐", layout="wide")

# ၂။ Session State (Data သိမ်းဆည်းရန်)
if 'api_key' not in st.session_state:
    st.session_state['api_key'] = ""
if 'result' not in st.session_state:
    st.session_state['result'] = None

def clear_text():
    st.session_state['result'] = None

# ၃။ Sidebar - API Settings & Control Panel
with st.sidebar:
    st.title("🔑 API Settings")
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
    
    # ဘာသာစကား ရွေးချယ်မှုများ
    lang_pair = st.selectbox(
        "Select Language Pair:",
        [
            "English to Myanmar",
            "Korea to English",
            "Chinese to English",
            "Korea to Myanmar",
            "Chinese to Myanmar"
        ]
    )
    
    version = st.selectbox("Style Mode:", ["ဆီလျော်အောင် (Cinematic)", "တိတိကျကျ (Literal)"])
    
    if st.button("🗑️ CLEAR ALL", on_click=clear_text):
        st.rerun()

# ၄။ Main UI
st.title("🌐 MULTI-LANGUAGE SRT TRANSLATOR")

if not st.session_state['api_key']:
    st.warning("⚠️ Please enter and save your API Key in the sidebar first.")
    st.stop()

# ၅။ Input Area
input_text = st.text_area("PASTE YOUR SRT CONTENT:", height=350, placeholder="1\n00:00:01,000 --> 00:00:04,000\nText here...")

# ၆။ Translation Engine (404 Error Fix ပါဝင်ပြီးသား)
def translate_engine(text, pair, mode, key):
    try:
        genai.configure(api_key=key)
        # API Key မှန်မမှန် အရင်စစ်ဆေးခြင်း
        list(genai.list_models()) 
    except Exception:
        return "ERROR_API_INVALID"

    temp = 0.8 if "Cinematic" in mode else 0.2
    source_lang, target_lang = pair.split(" to ")
    style_desc = "cinematic and natural" if temp == 0.8 else "literal and accurate"
    
    # 404 Error မတက်စေရန် models/ prefix အသုံးပြုခြင်း
    model = genai.GenerativeModel(
        model_name='models/gemini-1.5-flash', 
        generation_config={"temperature": temp}
    )
    
    prompt = f"Task: Translate {source_lang} to {target_lang}. Style: {style_desc}. Keep SRT tags and timing. Result only:\n\n{text}"
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        # အကယ်၍ models/ နဲ့ Error တက်နေသေးပါက gemini-1.5-flash နဲ့ ထပ်စမ်းခြင်း
        try:
            model_alt = genai.GenerativeModel(model_name='gemini-1.5-flash')
            response = model_alt.generate_content(prompt)
            return response.text
        except:
            return f"ERROR_GEN: {str(e)}"

# ၇။ Start Button
if st.button("🚀 START TRANSLATING"):
    if input_text:
        with st.spinner(f"Processing {lang_pair}..."):
            result = translate_engine(input_text, lang_pair, version, st.session_state['api_key'])
            
            if result == "ERROR_API_INVALID":
                st.error("❌ Invalid API Key! Please check your key in Google AI Studio.")
            elif result.startswith("ERROR_GEN"):
                st.error(f"❌ {result}")
            else:
                st.session_state['result'] = result
                st.success("Done!")
    else:
        st.warning("Please paste your text first.")

# ၈။ Result & Custom Rename Section
if st.session_state['result']:
    st.divider()
    st.subheader("💾 Download Result")
    
    # ဖိုင်နာမည် စိတ်ကြိုက် Rename ပေးရန်
    default_name = f"{lang_pair.replace(' ', '_')}_translated"
    custom_name = st.text_input("Rename File:", value=default_name)
    
    # .srt extension သေချာစေရန်
    final_name = f"{custom_name}.srt" if not custom_name.endswith(".srt") else custom_name

    st.download_button(
        label=f"📥 DOWNLOAD {final_name}",
        data=st.session_state['result'],
        file_name=final_name,
        mime="text/plain"
    )
    
    with st.expander("Show Preview"):
        st.text(st.session_state['result'])

st.markdown("<br><center><small>Powered by Gemini 1.5 Flash API</small></center>", unsafe_allow_html=True)
