import requests
import yt_dlp
import google.generativeai as genai
from flask import Flask, render_template_string, request, jsonify

app = Flask(__name__)

# API Keys များ (Production Version)
MY_GEMINI_KEY = "AIzaSyAxIDo81UMMs89glzAEN2bxClmR_2S-x0Y"
MY_SHOTSTACK_KEY = "FbS7eq7HlwFEC8UwJQF0QrYsOQyUNaa7rU6ckHDM"
MY_TWELVE_LABS_KEY = "tl_01j74z96sytm6n0pnd33y7x2v1"

genai.configure(api_key=MY_GEMINI_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>AI Video Cutter Pro</title>
    <style>
        body { font-family: sans-serif; background: #121212; color: white; text-align: center; padding: 50px; }
        .card { background: #1e1e1e; padding: 30px; border-radius: 15px; max-width: 400px; margin: auto; border: 1px solid #333; }
        input { width: 100%; padding: 12px; margin: 20px 0; border-radius: 8px; border: 1px solid #444; background: #222; color: white; box-sizing: border-box; }
        button { width: 100%; padding: 12px; background: #007bff; color: white; border: none; border-radius: 8px; cursor: pointer; font-weight: bold; }
        #status { margin-top: 20px; color: #aaa; }
    </style>
</head>
<body>
    <div class="card">
        <h2>🎬 AI Production Cutter</h2>
        <p>YouTube Link ထည့်ပြီး ခလုတ်နှိပ်ပါ</p>
        <input type="text" id="url" placeholder="https://www.youtube.com/watch?v=...">
        <button onclick="run()">ဗီဒီယို ဖြတ်မည်</button>
        <div id="status"></div>
    </div>
    <script>
        async function run() {
            const status = document.getElementById('status');
            status.innerHTML = "⏳ AI စတင်အလုပ်လုပ်နေပါပြီ (Production)...";
            const res = await fetch('/run', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({url: document.getElementById('url').value})
            });
            const data = await res.json();
            status.innerHTML = data.success ? "✅ အောင်မြင်ပါသည်! Shotstack Dashboard မှာ သွားကြည့်ပါ။" : "❌ Error: " + data.error;
        }
    </script>
</body>
</html>
"""

@app.route('/')
def home(): return render_template_string(HTML_TEMPLATE)

@app.route('/run', methods=['POST'])
def run_app():
    try:
        data = request.json
        with yt_dlp.YoutubeDL({'format': 'best', 'quiet': True}) as ydl:
            info = ydl.extract_info(data['url'], download=False)
            v_url = info['url']
        
        headers = {"x-api-key": MY_SHOTSTACK_KEY, "Content-Type": "application/json"}
        payload = {
            "timeline": {"tracks": [{"clips": [{"asset": {"type": "video", "src": v_url, "trim": 2100}, "start": 0, "length": 60}]}]},
            "output": {"format": "mp4", "resolution": "hd"}
        }
        res = requests.post("https://api.shotstack.io/v1/render", json=payload, headers=headers).json()
        return jsonify({"success": True, "id": res['response']['id']})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
