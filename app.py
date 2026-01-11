import streamlit as st
import google.generativeai as genai
import time

# ၁။ Page Setting
st.set_page_config(page_title="Pro SRT Translator", page_icon="🌐", layout="wide")

# ၂။ Session State
if 'api_key' not in st.session_state:
    st.session_state['api_key'] = ""
if 'result' not in st.session_state:
    st.session_state['result'] = None
if 'input_reset_key' not in st.session_state:
    st.session_state['input_reset_key'] = 0

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
    lang_pair = st.selectbox(
        "Select Language Pair:",
        ["English to Myanmar", "Korea to English", "Chinese to English", "Korea to Myanmar", "Chinese to Myanmar"]
    )
    st.write("**Translation Version:**")
    mode = st.radio("Choose Mode:", ["ဆီလျော်အောင် (Cinematic)", "တိတိကျကျ (Literal)"], horizontal=True)

# ၄။ Main UI
st.title("🌐 MULTI-LANGUAGE SRT TRANSLATOR")

if not st.session_state['api_key']:
    st.warning("⚠️ Please enter and save your API Key in the sidebar first.")
    st.stop()

# ၅။ Input Area
input_text = st.text_area(
    "PASTE YOUR SRT CONTENT:", 
    height=350, 
    placeholder="Paste long SRT text here (e.g. 11 mins video content)...",
    key=f"srt_input_{st.session_state['input_reset_key']}"
)

# ၆။ Buttons Row
col1, col2 = st.columns([1, 1])
with col1:
    start_btn = st.button("🚀 START TRANSLATING")
with col2:
    st.markdown('<div style="text-align: right;">', unsafe_allow_html=True)
    if st.button("🗑️ CLEAR TEXT"):
        st.session_state['input_reset_key'] += 1
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# ၇။ Smart Translation Engine (Long Context Support)
def translate_engine(text, pair, mode, key):
    try:
        genai.configure(api_key=key)
        
        # အလုပ်လုပ်သော Model ကို ရှာဖွေခြင်း
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        selected_model = next((m for m in available_models if "flash" in m), available_models[0])

        source_lang, target_lang = pair.split(" to ")
        temp = 0.8 if "ဆီလျော်အောင်" in mode else 0.2
        
        # စာကြောင်းရေများပါက အပိုင်းလိုက်ခွဲရန် (SRT တစ်ခုကို စာကြောင်းရေ ၈၀ ခန့်စီ ခွဲမည်)
        lines = text.strip().split('\n\n')
        chunks = [lines[i:i + 80] for i in range(0, len(lines), 80)]
        
        full_translation = []
        progress_bar = st.progress(0)
        
        model = genai.GenerativeModel(model_name=selected_model, generation_config={"temperature": temp})
        
        # ဇာတ်လမ်း Context မပျောက်စေရန် အပိုင်းတိုင်းတွင် ညွှန်ကြားချက် ထပ်ထည့်မည်
        for index, chunk in enumerate(chunks):
            chunk_text = '\n\n'.join(chunk)
            context_prompt = f"""
            Task: Professional Movie Subtitle Translation ({pair}).
            Mode: {mode}.
            Note: This is part {index+1} of a long movie script. Keep consistency with previous parts.
            Instruction: Keep timing tags. Translate dialogue only. Result only:
            
            {chunk_text}
            """
            
            response = model.generate_content(context_prompt)
            full_translation.append(response.text)
            
            # Progress bar update
            progress_bar.progress((index + 1) / len(chunks))
            time.sleep(1) # API Rate limit မကျော်အောင် ခဏနားခြင်း
            
        return '\n\n'.join(full_translation)
        
    except Exception as e:
        return f"ERROR: {str(e)}"

# Start Logic
if start_btn:
    if input_text:
        with st.spinner(f"Analyzing and Translating in {mode} version..."):
            result = translate_engine(input_text, lang_pair, mode, st.session_state['api_key'])
            if "ERROR:" in result:
                st.error(f"❌ {result}")
            else:
                st.session_state['result'] = result
                st.success("Done!")
    else:
        st.warning("Please paste some text first.")

# ၈။ Result & Download Section
if st.session_state['result']:
    st.divider()
    default_name = f"{lang_pair.replace(' ', '_')}_translated"
    custom_name = st.text_input("Rename your file:", value=default_name)
    final_name = f"{custom_name}.srt" if not custom_name.endswith(".srt") else custom_name

    st.download_button(label=f"📥 DOWNLOAD {final_name}", data=st.session_state['result'], file_name=final_name, mime="text/plain")
    with st.expander("Preview Translated Text"):
        st.text(st.session_state['result'])
