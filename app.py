import streamlit as st
import google.generativeai as genai

# ၁။ Page Setting
st.set_page_config(page_title="Professional SRT Translator", page_icon="🌐", layout="wide")

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

# ၆။ Smart Translation Engine (Auto-Model Finder)
def translate_engine(text, pair, mode, key):
    try:
        genai.configure(api_key=key)
        
        # မင်းရဲ့ API က သုံးလို့ရတဲ့ Model list ကို အလိုအလျောက် ဆွဲထုတ်ခြင်း
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        
        if not available_models:
            return "ERROR: No models available for this API Key."

        # Flash model ကို အရင်ရှာပြီး သုံးမယ်၊ မရှိရင် ပထမဆုံးတွေ့တဲ့ model ကို သုံးမယ်
        selected_model = ""
        for m in available_models:
            if "flash" in m:
                selected_model = m
                break
        if not selected_model:
            selected_model = available_models[0]

        temp = 0.8 if "Cinematic" in mode else 0.2
        source_lang, target_lang = pair.split(" to ")
        
        model = genai.GenerativeModel(model_name=selected_model, generation_config={"temperature": temp})
        prompt = f"Professional SRT Translation: {source_lang} to {target_lang}. Keep timing tags. Result only:\n\n{text}"
        
        response = model.generate_content(prompt)
        return response.text
        
    except Exception as e:
        return f"ERROR: {str(e)}"

# ၇။ Start Button
if st.button("🚀 START TRANSLATING"):
    if input_text:
        with st.spinner(f"Detecting best model and translating..."):
            result = translate_engine(input_text, lang_pair, version, st.session_state['api_key'])
            
            if "ERROR:" in result:
                st.error(f"❌ {result}")
                st.info("အကြံပြုချက်: API Key သည် Google AI Studio (aistudio.google.com) မှ ထုတ်ထားသော Key ဖြစ်ရပါမည်။")
            else:
                st.session_state['result'] = result
                st.success("Translation Complete!")
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
