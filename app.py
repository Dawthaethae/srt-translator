
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
<html>
<head>
    <meta charset="UTF-8">
    <title>AI Video Cutter</title>
    <style>
        body { font-family: sans-serif; background: #121212; color: white; text-align: center; padding: 50px; }
        .card { background: #1e1e1e; padding: 30px; border-radius: 15px; max-width: 400px; margin: auto; border: 1px solid #333; }
        input { width: 90%; padding: 12px; margin: 20px 0; border-radius: 8px; border: 1px solid #444; background: #222; color: white; outline: none; }
        button { width: 95%; padding: 12px; background: #007bff; color: white; border: none; border-radius: 8px; cursor: pointer; font-weight: bold; }
        button:hover { background: #0056b3; }
        #status { margin-top: 20px; color: #aaa; font-size: 14px; }
    </style>
</head>
<body>
    <div class="card">
        <h2>🎬 AI Video Cutter</h2>
        <input type="text" id="url" placeholder="YouTube Link ထည့်ပါ...">
        <button onclick="run()">ဗီဒီယို ဖြတ်မည်</button>
        <div id="status"></div>
    </div>
    <script>
        async function run() {
            const status = document.getElementById('status');
            const urlInput = document.getElementById('url').value;
            if(!urlInput) return alert("Link ထည့်ပေးပါဦး");
            
            status.innerHTML = "⏳ YouTube ကနေ ဖတ်နေပါပြီ...";
            try {
                const res = await fetch('/run', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({url: urlInput})
                });
                const data = await res.json();
                if(data.success) {
                    status.innerHTML = "✅ အောင်မြင်ပါသည်!<br>Render ID: " + data.id + "<br>Shotstack မှာ စစ်ကြည့်ပါ။";
                } else {
                    status.innerHTML = "❌ Error: " + data.error;
                }
            } catch (e) {
                status.innerHTML = "❌ ဆာဗာ ချိတ်ဆက်မှု မရပါ။";
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
        ydl_opts = {
            'format': 'best',
            'quiet': True,
            'cookiefile': 'cookies.txt', # GitHub မှာ cookies.txt ဖိုင် ရှိရပါမည်
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(data['url'], download=False)
            video_url = info['url']

        ss_headers = {"x-api-key": MY_SHOTSTACK_KEY, "Content-Type": "application/json"}
        payload = {
            "timeline": {"tracks": [{"clips": [{"asset": {"type": "video", "src": video_url, "trim": 5}, "start": 0, "length": 15}]}]},
            "output": {"format": "mp4", "resolution": "sd"}
        }
        
        ss_res = requests.post("https://api.shotstack.io/v1/render", json=payload, headers=ss_headers).json()
        
        if 'response' in ss_res:
            return jsonify({"success": True, "id": ss_res['response']['id']})
        else:
            return jsonify({"success": False, "error": ss_res.get('message', 'Shotstack API error')})
            
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

if __name__ == '__main__':
    # Render အတွက် Port dynamic ဖြစ်အောင် ပြင်ထားသည်
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
