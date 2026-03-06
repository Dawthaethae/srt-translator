import requests
import yt_dlp
import google.generativeai as genai
from flask import Flask, render_template_string, request, jsonify
import os

app = Flask(__name__)

# --- API Keys ---
MY_GEMINI_KEY = "AIzaSyAxIDo81UMMs89glzAEN2bxClmR_2S-x0Y"
MY_SHOTSTACK_KEY = "FbS7eq7HlwFEC8UwJQF0QrYsOQyUNaa7rU6ckHDM"

@app.route('/')
def home():
    return "AI Video Cutter is Running! Send POST to /run"

@app.route('/run', methods=['POST'])
def run_app():
    data = request.json
    try:
        # YouTube ကို လူသားလို ဟန်ဆောင်ပြီး လှမ်းဖတ်မယ့် Options
        ydl_opts = {
            'format': 'best',
            'quiet': True,
            'no_warnings': True,
            'cookiefile': 'cookies.txt',  # cookies.txt ရှိဖို့ လိုပါတယ်
            'nocheckcertificate': True,
            'ignoreerrors': True,
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
        }
        
        # YouTube Link ထဲက Video URL အစစ်ကို ထုတ်ယူခြင်း
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # တိုက်ရိုက် Extract လုပ်ဖို့ ကြိုးစားမယ်
            info = ydl.extract_info(data['url'], download=False)
            if not info:
                return jsonify({"success": False, "error": "YouTube က ပိတ်ထားလို့ ဖတ်မရပါ (Captcha/Age Restricted)"})
            video_url = info['url']

        # Shotstack API သို့ ပို့ခြင်း
        ss_headers = {"x-api-key": MY_SHOTSTACK_KEY, "Content-Type": "application/json"}
        payload = {
            "timeline": {"tracks": [{"clips": [{"asset": {"type": "video", "src": video_url, "trim": 10}, "start": 0, "length": 20}]}]},
            "output": {"format": "mp4", "resolution": "sd"} # မြန်မြန်ပြီးအောင် sd နဲ့ အရင်စမ်းမယ်
        }
        
        ss_res = requests.post("https://api.shotstack.io/v1/render", json=payload, headers=ss_headers).json()
        
        return jsonify({"success": True, "id": ss_res['response']['id']})
            
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
