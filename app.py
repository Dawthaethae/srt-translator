import requests
import yt_dlp
import google.generativeai as genai
from flask import Flask, render_template_string, request, jsonify
import os

app = Flask(__name__)

# --- API Keys ---
MY_GEMINI_KEY = "AIzaSyAxIDo81UMMs89glzAEN2bxClmR_2S-x0Y"
MY_SHOTSTACK_KEY = "FbS7eq7HlwFEC8UwJQF0QrYsOQyUNaa7rU6ckHDM"

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="my">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Video Cutter Pro</title>
    <style>
        body { font-family: 'Segoe UI', sans-serif; background: #0f0f0f; color: white; text-align: center; padding: 50px; margin: 0; }
        .card { background: #1a1a1a; padding: 30px; border-radius: 20px; width: 90%; max-width: 400px; margin: auto; border: 1px solid #333; box-shadow: 0 10px 30px rgba(0,0,0,0.5); }
        h2 { color: #3b82f6; }
        input { width: 100%; padding: 15px; margin: 20px 0; border-radius: 10px; border: 1px solid #333; background: #252525; color: white; box-sizing: border-box; }
        button { width: 100%; padding: 15px; background: #3b82f6; color: white; border: none; border-radius: 10px; cursor: pointer; font-size: 16px; font-weight: bold; transition: 0.3s; }
        button:hover { background: #2563eb; }
        #status { margin-top: 20px; color: #bbb; font-size: 14px; line-height: 1.6; }
        .success { color: #4ade80; font-weight: bold; }
        .error { color: #f87171; }
    </style>
</head>
<body>
    <div class="card">
        <h2>🎬 AI Video Cutter</h2>
        <p>Production Mode (Fixed Format)</p>
        <input type="text" id="url" placeholder="YouTube Link ကို ထည့်ပါ...">
        <button id="btn" onclick="run()">ဗီဒီယို ဖြတ်ထုတ်မည်</button>
        <div id="status"></div>
    </div>

    <script>
        async function run() {
            const status = document.getElementById('status');
            const btn = document.getElementById('btn');
            const urlInput = document.getElementById('url').value;

            if(!urlInput) return alert("Link ထည့်ပေးပါဦး");

            btn.disabled = true;
            status.innerHTML = "⏳ YouTube ကနေ ဗီဒီယိုကို ရှာဖွေနေပါသည်...<br><small>(Format မျိုးစုံ စစ်ဆေးနေသည်)</small>";

            try {
                const res = await fetch('/run', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({url: urlInput})
                });
                const data = await res.json();
                
                btn.disabled = false;
                if(data.success) {
                    status.innerHTML = `<span class="success">✅ အောင်မြင်ပါသည်!</span><br>Render ID: \${data.id}<br><br><small>Shotstack Dashboard မှာ ဗီဒီယိုကို သွားကြည့်နိုင်ပါပြီ။</small>`;
                } else {
                    status.innerHTML = `<span class="error">❌ Error:</span><br>\${data.error}`;
                }
            } catch (e) {
                btn.disabled = false;
                status.innerHTML = `<span class="error">❌ စနစ်ချို့ယွင်းချက် ဖြစ်ပေါ်နေသည်။</span>`;
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
        # ၁။ YouTube Options (Format Error ကို ရှင်းထားသည်)
        ydl_opts = {
            # mp4 format အားလုံးကို ရှာခိုင်းပြီး အဆင်ပြေဆုံးကို ယူမည့် logic
            'format': 'best[ext=mp4]/best', 
            'quiet': True,
            'no_warnings': True,
            'cookiefile': 'cookies.txt', 
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'nocheckcertificate': True
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # ဗီဒီယို အချက်အလက်များကို ထုတ်ယူခြင်း
            info = ydl.extract_info(data['url'], download=False)
            video_url = info['url']

        # ၂။ Shotstack API (ဗီဒီယို ဖြတ်တောက်ရန်)
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
                            "trim": 0 # ဗီဒီယို အစကနေ စဖြတ်မည်
                        },
                        "start": 0,
                        "length": 15 # ၁၅ စက္ကန့် ဖြတ်ထုတ်မည်
                    }]
                }]
            },
            "output": {
                "format": "mp4",
                "resolution": "sd" # Render မြန်အောင် sd နဲ့ ထားထားသည်
            }
        }
        
        ss_res = requests.post("https://api.shotstack.io/v1/render", json=payload, headers=ss_headers).json()
        
        if ss_res.get('success'):
            return jsonify({"success": True, "id": ss_res['response']['id']})
        else:
            return jsonify({"success": False, "error": ss_res.get('message', 'Shotstack Processing Error')})
            
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
