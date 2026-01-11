import streamlit as st
import google.generativeai as genai

# ၁။ Page Setting
st.set_page_config(page_title="Professional SRT Translator", page_icon="🌐", layout="wide")

# ၂။ Session State
if 'api_key' not in st.session_state:
    st.session_state['api_key'] = ""
if 'result' not in st.session_state:
    st.session_state['result'] = None

# အပေါ်က စာကိုပဲ ရှင်းလင်းသည့် Function
def clear_input_only():
    st.session_state['srt_input'] = "" # Input box ကိုပဲ ရှင်းမည်
    # Result ကို မဖျက်ပါ

# ၃။ Sidebar - API Settings
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
    
    # ဘာသာစကားတွဲများ
    lang_pair = st.selectbox(
        "Select Language Pair:",
        ["English to Myanmar", "Korea to English", "Chinese to English", "Korea to Myanmar", "Chinese to Myanmar"]
    )
    
    # Version ရွေးချယ်မှု (မင်းလိုချင်တဲ့ အပိုင်း)
    st.write("**Translation Version:**")
    mode = st.radio(
        "Choose Mode:",
        ["ဆီလျော်အောင် (Cinematic)", "တိတိကျကျ (Literal)"],
        horizontal=True
    )

# ၄။ Main UI
st.title("🌐 MULTI-LANGUAGE SRT TRANSLATOR")

if not st.session_state['api_key']:
    st.warning("⚠️ Please enter and save your API Key in the sidebar first.")
    st.stop()

# ၅။ Input Area
input_text = st.text_area("PASTE YOUR SRT CONTENT:", height=350, placeholder="1\n00:00:01,000 --> 00:00:04,000\nText here...", key="srt_input")

# ၆။ Buttons Row
col_btn1, col_btn2 = st.columns([1, 4])

with col_btn1:
    start_btn = st.button("🚀 START TRANSLATING")

with col_btn2:
    if st.button("🗑️ CLEAR TEXT"):
        clear_input_only()
        st.rerun()

# ၇။ Smart Translation Engine
def translate_engine(text, pair, mode, key):
    try:
        genai.configure(api_key=key)
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        
        selected_model = ""
        for m in available_models:
            if "flash" in m:
                selected_model = m
                break
        if not selected_model:
            selected_model = available_models[0] if available_models else "models/gemini-1.5-flash"

        # Version အလိုက် Temperature ကို ချိန်ညှိခြင်း
        temp = 0.8 if "ဆီလျော်အောင်" in mode else 0.2
        source_lang, target_lang = pair.split(" to ")
        
        model = genai.GenerativeModel(model_name=selected_model, generation_config={"temperature": temp})
        
        # Version အလိုက် prompt ညွှန်ကြားချက် ပြောင်းလဲခြင်း
        if "ဆီလျော်အောင်" in mode:
            style_inst = "Make it cinematic, natural, and emotionally resonant for movies."
        else:
            style_inst = "Make it literal, precise, and strictly accurate to the original words."
            
        prompt = f"Professional SRT Translation: {source_lang} to {target_lang}. {style_inst} Keep timing tags. Result only:\n\n{text}"
        
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"ERROR: {str(e)}"

# Start ခလုတ် နှိပ်သည့်အခါ
if start_btn:
    if input_text:
        with st.spinner(f"Translating in {mode} mode..."):
            result = translate_engine(input_text, lang_pair, mode, st.session_state['api_key'])
            if "ERROR:" in result:
                st.error(f"❌ {result}")
            else:
                st.session_state['result'] = result
                st.success(f"Done! ({mode} version applied)")
    else:
        st.warning("Please paste some text first.")

# ၈။ Result & Download Section
if st.session_state['result']:
    st.divider()
    st.subheader("✅ Translation Ready")
    
    default_name = f"{lang_pair.replace(' ', '_')}_translated"
    custom_name = st.text_input("Rename your file:", value=default_name)
    final_name = f"{custom_name}.srt" if not custom_name.endswith(".srt") else custom_name

    st.download_button(
        label=f"📥 DOWNLOAD {final_name}",
        data=st.session_state['result'],
        file_name=final_name,
        mime="text/plain"
    )
    
    with st.expander("Preview Translated Text"):
        st.text(st.session_state['result'])
