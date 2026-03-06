import requests
import yt_dlp
import google.generativeai as genai
from flask import Flask, render_template_string, request, jsonify
import os

app = Flask(__name__)

# --- API Keys Configuration ---
MY_GEMINI_KEY = "AIzaSyAxIDo81UMMs89glzAEN2bxClmR_2S-x0Y"
MY_SHOTSTACK_KEY = "FbS7eq7HlwFEC8UwJQF0QrYsOQyUNaa7rU6ckHDM"
MY_TWELVE_LABS_KEY = "tl_01j74z96sytm6n0pnd33y7x2v1"

# AI Setup
genai.configure(api_key=MY_GEMINI_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="my">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Video Cutter Pro</title>
    <style>
        body { font-family: 'Segoe UI', sans-serif; background: #0f0f0f; color: white; display: flex; justify-content: center; align-items: center; min-height: 100vh; margin: 0; }
        .card { background: #1a1a1a; padding: 30px; border-radius: 20px; width: 90%; max-width: 400px; box-shadow: 0 15px 35px rgba(0,0,0,0.7); text-align: center; border: 1px solid #333; }
        h2 { color: #3b82f6; margin-bottom: 5px; }
        p { color: #888; font-size: 14px; margin-bottom: 25px; }
        input { width: 100%; padding: 15px; margin-bottom: 20px; border: 1px solid #333; border-radius: 10px; background: #252525; color: white; box-sizing: border-box; outline: none; }
        input:focus { border-color: #3b82f6; }
        button { width: 100%; padding: 15px; background: #3b82f6; color: white; border: none; border-radius: 10px; cursor: pointer; font-size: 16px; font-weight: bold; transition: 0.3s; }
        button:hover { background: #2563eb; }
        button:disabled { background: #555; cursor: not-allowed; }
        #status { margin-top: 20px; font-size: 14px; color: #bbb; line-height: 1.5; }
        .success-box { background: #064e3b; color: #a7f3d0; padding: 15px; border-radius: 10px; margin-top: 20px; display: none; font-size: 13px; }
        a { color: #60a5fa; text-decoration: none; font-weight: bold; }
    </style>
</head>
<body>
    <div class="card">
        <h2>🎬 AI Video Cutter</h2>
        <p>Production Mode (With Cookies)</p>
        
        <input type="text" id="ytUrl" placeholder="YouTube Link ကို ထည့်ပါ...">
        <button id="btn" onclick="process()">ဗီဒီယို ဖြတ်ထုတ်မည်</button>
        
        <div id="status"></div>
        <div id="result" class="success-box">
            <b>✅ ဖြတ်တောက်မှု အောင်မြင်သည်!</b><br>
            <span id="renderId"></span><br><br>
            <a href="https://dashboard.shotstack.io/renders" target="_blank">Shotstack Dashboard မှာ ဗီဒီယိုရယူပါ ➔</a>
        </div>
    </div>

    <script>
        async function process() {
            const status = document.getElementById('status');
            const result = document.getElementById('result');
            const btn = document.getElementById('btn');
            const url = document.getElementById('ytUrl').value;

            if(!url) return alert("Link ထည့်ပေးပါဦး");

            btn.disabled = true;
            status.innerHTML = "⏳ YouTube ကနေ ဗီဒီယိုဖတ်နေပါတယ်...<br><small>(Cookies သုံးပြီး Captcha ကျော်နေသည်)</small>";
            result.style.display = 'none';

            try {
                const res = await fetch('/run', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ url: url })
                });
                const data = await res.json();
                
                btn.disabled = false;
                if(data.success) {
                    status.innerHTML = "";
                    result.style.display = 'block';
                    document.getElementById('renderId').innerText = "Render ID: " + data.id;
                } else {
                    status.innerHTML = "❌ Error: " + data.error;
                }
            } catch (e) {
                btn.disabled = false;
                status.innerHTML = "❌ စနစ်ချို့ယွင်းချက် ရှိနေပါသည်။";
            }
        }
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/run', methods=['POST'])
def run_app():
    data = request.json
    try:
        # ၁။ YouTube Link မှ Video URL ကို Cookies သုံး၍ ယူခြင်း
        ydl_opts = {
            'format': 'best',
            'quiet': True,
            'no_warnings': True,
            'cookiefile': 'cookies.txt', # GitHub ထဲရှိ cookies.txt ဖိုင်ကို သုံးမည်
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(data['url'], download=False)
            video_url = info['url']

        # ၂။ Shotstack Production API သို့ ပို့ခြင်း
        # မှတ်ချက် - ဒီနေရာမှာ နမူနာအနေနဲ့ ၂ မိနစ်ကနေ စဖြတ်ထားပါတယ် (trim: 120)
        ss_headers = {
            "x-api-key": MY_SHOTSTACK_KEY,
            "Content-Type": "application/json"
        }
        
        payload = {
            "timeline": {
                "tracks": [{
                    "clips": [{
                        "asset": {
                            "type": "video",
                            "src": video_url,
                            "trim": 120  # ဗီဒီယို စဖြတ်မည့် စက္ကန့် (လိုအပ်သလို ပြင်နိုင်သည်)
                        },
                        "start": 0,
                        "length": 30   # ဗီဒီယို အရှည် (စက္ကန့် ၃၀ ဖြတ်မည်)
                    }]
                }]
            },
            "output": {
                "format": "mp4",
                "resolution": "hd"
            }
        }
        
        # Shotstack Production Endpoint
        ss_res = requests.post("https://api.shotstack.io/v1/render", json=payload, headers=ss_headers).json()
        
        if ss_res.get('success'):
            return jsonify({"success": True, "id": ss_res['response']['id']})
        else:
            return jsonify({"success": False, "error": ss_res.get('message', 'Shotstack API Error')})
            
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

if __name__ == '__main__':
    # Render အတွက် Port ပေးခြင်း
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
