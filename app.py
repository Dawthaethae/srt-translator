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
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #0f0f0f; color: white; text-align: center; padding: 40px; margin: 0; }
        .card { background: #1a1a1a; padding: 30px; border-radius: 20px; width: 90%; max-width: 420px; margin: auto; border: 1px solid #333; box-shadow: 0 15px 35px rgba(0,0,0,0.6); }
        h2 { color: #3b82f6; margin-bottom: 10px; }
        p { color: #888; font-size: 14px; margin-bottom: 20px; }
        input { width: 100%; padding: 15px; margin: 15px 0; border-radius: 10px; border: 1px solid #333; background: #252525; color: white; box-sizing: border-box; outline: none; }
        input:focus { border-color: #3b82f6; }
        button { width: 100%; padding: 15px; background: #3b82f6; color: white; border: none; border-radius: 10px; cursor: pointer; font-size: 16px; font-weight: bold; transition: 0.3s; }
        button:hover { background: #2563eb; }
        button:disabled { background: #444; cursor: not-allowed; }
        #status { margin-top: 25px; color: #bbb; font-size: 14px; line-height: 1.6; }
        .success-box { background: #064e3b; color: #a7f3d0; padding: 15px; border-radius: 10px; margin-top: 20px; }
        .error-box { background: #450a0a; color: #fca5a5; padding: 15px; border-radius: 10px; margin-top: 20px; }
    </style>
</head>
<body>
    <div class="card">
        <h2>🎬 AI Video Cutter</h2>
        <p>Production Mode (360p Fixed)</p>
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
            status.innerHTML = "⏳ YouTube ကနေ ဗီဒီယိုကို ဖတ်နေပါပြီ...<br><small>(Format 18 ရှာဖွေနေသည်)</small>";

            try {
                const res = await fetch('/run', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({url: urlInput})
                });
                const data = await res.json();
                
                btn.disabled = false;
                if(data.success) {
                    status.innerHTML = `<div class="success-box">✅ အောင်မြင်ပါသည်!<br>Render ID: \${data.id}<br><br><small>Shotstack Dashboard မှာ ဗီဒီယိုကို စစ်ကြည့်ပါ။</small></div>`;
                } else {
                    status.innerHTML = `<div class="error-box">❌ Error:<br>\${data.error}</div>`;
                }
            } catch (e) {
                btn.disabled = false;
                status.innerHTML = `<div class="error-box">❌ စနစ်ချို့ယွင်းချက် ရှိနေသည်။</div>`;
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
        # YouTube Options - Format 18 (MP4 360p) ကို အဓိက သုံးထားသည်
        ydl_opts = {
            'format': '18/best[ext=mp4]/best', 
            'quiet': True,
            'no_warnings': True,
            'cookiefile': 'cookies.txt', 
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'nocheckcertificate': True
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # ဗီဒီယို Extract လုပ်ခြင်း
            info = ydl.extract_info(data['url'], download=False)
            video_url = info['url']

        # Shotstack API သို့ ပို့ခြင်း
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
                            "trim": 0
                        },
                        "start": 0,
                        "length": 10  # ၁၀ စက္ကန့် ဖြတ်မည်
                    }]
                }]
            },
            "output": {
                "format": "mp4",
                "resolution": "sd"
            }
        }
        
        ss_res = requests.post("https://api.shotstack.io/v1/render", json=payload, headers=ss_headers).json()
        
        if ss_res.get('success'):
            return jsonify({"success": True, "id": ss_res['response']['id']})
        else:
            return jsonify({"success": False, "error": ss_res.get('message', 'Shotstack error')})
            
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
