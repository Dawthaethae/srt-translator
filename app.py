
import streamlit as st
import google.generativeai as genai
import time

# ၁။ Page Setting
st.set_page_config(page_title="Pro Movie SRT Translator", page_icon="🎬", layout="wide")

# ၂။ Session State
if 'api_key' not in st.session_state:
    st.session_state['api_key'] = ""
if 'result' not in st.session_state:
    st.session_state['result'] = None
if 'input_reset_key' not in st.session_state:
    st.session_state['input_reset_key'] = 0

# ၃။ Sidebar - API Settings
with st.sidebar:
    st.title("🔑 API Settings")
    user_key = st.text_input("Enter API Key:", value=st.session_state['api_key'], type="password")
    
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
        ["English to Myanmar", "Korea to Myanmar", "Chinese to Myanmar", "Korea to English", "Chinese to English"]
    )
    st.write("**Translation Version:**")
    mode = st.radio("Choose Mode:", ["ဆီလျော်အောင် (Cinematic)", "တိတိကျကျ (Literal)"], horizontal=True)

# ၄။ Main UI
st.title("🎬 MOVIE RECAP SRT TRANSLATOR")

if not st.session_state['api_key']:
    st.warning("⚠️ Please enter and save your API Key in the sidebar.")
    st.stop()

# ၅။ Input Area
input_text = st.text_area(
    "PASTE YOUR SRT CONTENT:", 
    height=350, 
    placeholder="၁၁ မိနစ်စာ အရှည်ကြီးလည်း ထည့်လို့ရပါတယ်...",
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

# ၇။ Cinematic Engine (Gemini App ကဲ့သို့ Style ရအောင် ပြင်ဆင်ထားသည်)
def translate_engine(text, pair, mode, key):
    try:
        genai.configure(api_key=key)
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        selected_model = next((m for m in available_models if "flash" in m), available_models[0])

        source_lang, target_lang = pair.split(" to ")
        
        # အပိုင်းလိုက်ခွဲခြင်း (Long Video များအတွက်)
        lines = text.strip().split('\n\n')
        chunks = [lines[i:i + 60] for i in range(0, len(lines), 60)]
        
        full_translation = []
        progress_bar = st.progress(0)
        model = genai.GenerativeModel(model_name=selected_model)
        
        # --- PROMPT IMPROVEMENT ---
        if "ဆီလျော်အောင်" in mode:
            # Gemini App ရဲ့ Style အတိုင်း ရအောင် ညွှန်ကြားချက်ကို အသေးစိတ်ပေးခြင်း
            style_instruction = """
            - Role: You are a professional movie subtitle translator and storyteller.
            - Style: Translate into natural, cinematic, and conversational Myanmar Burmese.
            - Vocabulary: Use engaging words like 'မိစ္ဆာ', 'သေမင်း', 'ရိုမန်းတစ်', 'အတင်းအဓမ္မ' instead of simple dictionary words.
            - Sentence Flow: Make it sound like a movie recap narrator is telling a story. Avoid stiff or formal dictionary translations.
            - Formatting: Keep SRT numbers and timing tags exactly the same.
            """
            temp = 0.9 # ဖန်တီးနိုင်စွမ်းကို မြှင့်တင်သည်
        else:
            style_instruction = "Translate literally and accurately. Keep it formal and precise. Keep timing tags."
            temp = 0.2

        for index, chunk in enumerate(chunks):
            chunk_text = '\n\n'.join(chunk)
            context_prompt = f"""
            {style_instruction}
            
            Task: Translate from {source_lang} to {target_lang}.
            Part: {index+1} of {len(chunks)}.
            
            Text to translate:
            {chunk_text}
            
            Return ONLY the translated SRT content.
            """
            
            response = model.generate_content(context_prompt, generation_config={"temperature": temp})
            full_translation.append(response.text)
            progress_bar.progress((index + 1) / len(chunks))
            time.sleep(1)
            
        return '\n\n'.join(full_translation)
        
    except Exception as e:
        return f"ERROR: {str(e)}"

# Start Logic
if start_btn:
    if input_text:
        with st.spinner(f"Gemini App Style ဖြင့် ဘာသာပြန်နေသည်..."):
            result = translate_engine(input_text, lang_pair, mode, st.session_state['api_key'])
            if "ERROR:" in result:
                st.error(f"❌ {result}")
            else:
                st.session_state['result'] = result
                st.success("ဘာသာပြန်ခြင်း အောင်မြင်ပါသည်။")
    else:
        st.warning("စာသား အရင်ထည့်ပါ။")

# ၈။ Result & Download Section
if st.session_state['result']:
    st.divider()
    custom_name = st.text_input("Rename File:", value="translated_subtitle")
    final_name = f"{custom_name}.srt" if not custom_name.endswith(".srt") else custom_name

    st.download_button("📥 DOWNLOAD SRT", data=st.session_state['result'], file_name=final_name)
    with st.expander("Preview"):
        st.text(st.session_state['result'])
