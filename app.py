"""
THIRAIX - Integrated Fullstack Web & API Server
Includes Multi-lingual Neural TTS Audio Proxy for 10 Indian Languages
Run this file directly with Python:
    python app.py
Then open:
    http://localhost:8080
"""

import http.server
import socketserver
import json
import urllib.parse
import urllib.request
import sys
import os

# Import our backend prediction logic
from backend_simulation import GeofenceEngine, AIRiskPredictionModel, MultilingualAlertDispatcher, GPSCoordinate

PORT = 8080
DIRECTORY = os.path.dirname(os.path.abspath(__file__))

class ThiraixRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def do_GET(self):
        parsed_path = urllib.parse.urlparse(self.path)
        
        # API Endpoint: Predict Risk
        if parsed_path.path == '/api/risk':
            query = urllib.parse.parse_qs(parsed_path.query)
            dist = float(query.get('dist', [1850])[0])
            wave = float(query.get('wave', [1.3])[0])
            wind = float(query.get('wind', [18.5])[0])
            rain = float(query.get('rain', [2.0])[0])
            
            result = AIRiskPredictionModel.predict_risk(dist, wave, wind, rain)
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(result).encode('utf-8'))
            return
            
        # API Endpoint: Check Boundary Distance
        elif parsed_path.path == '/api/boundary':
            query = urllib.parse.parse_qs(parsed_path.query)
            lat = float(query.get('lat', [9.2950])[0])
            lon = float(query.get('lon', [79.3060])[0])
            
            dist, pt = GeofenceEngine.calculate_distance_to_imbl(GPSCoordinate(lat, lon))
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({
                "distance_meters": round(dist, 1),
                "is_breach_imminent": dist < 300,
                "closest_imbl_point": {"lat": pt.latitude, "lon": pt.longitude}
            }).encode('utf-8'))
            return

        # API Endpoint: Multi-Lingual Audio Stream (Speaks 10 Languages: Tamil, Hindi, Telugu, etc.)
        elif parsed_path.path == '/api/tts':
            query = urllib.parse.parse_qs(parsed_path.query)
            text = query.get('q', ['Hello'])[0]
            lang = query.get('lang', ['en'])[0]
            
            # Map languages for optimal TTS voice
            lang_map = {
                'ta': 'ta', 'hi': 'hi', 'te': 'te', 'kn': 'kn', 'ml': 'ml',
                'bn': 'bn', 'or': 'hi', 'pa': 'pa', 'ur': 'ur', 'en': 'en'
            }
            target_lang = lang_map.get(lang, 'en')
            
            tts_url = f"https://translate.google.com/translate_tts?ie=UTF-8&q={urllib.parse.quote(text[:200])}&tl={target_lang}&client=tw-ob"
            req = urllib.request.Request(tts_url, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
            try:
                with urllib.request.urlopen(req, timeout=6) as resp:
                    audio_data = resp.read()
                    self.send_response(200)
                    self.send_header('Content-Type', 'audio/mpeg')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.send_header('Content-Length', str(len(audio_data)))
                    self.end_headers()
                    self.wfile.write(audio_data)
                    return
            except Exception as e:
                print(f"TTS Proxy Error: {e}")
                self.send_response(500)
                self.end_headers()
                return

        # Default: Serve static files
        return super().do_GET()

def main():
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    
    with socketserver.TCPServer(("", PORT), ThiraixRequestHandler) as httpd:
        print(f"===============================================================")
        print(f" THIRAIX - Fullstack Maritime Safety Server Running! ")
        print(f" Features: 10-Language Neural Voice Audio Stream (/api/tts)")
        print(f" Open in Browser: http://localhost:{PORT}")
        print(f" Root Directory : {DIRECTORY}")
        print(f" Press Ctrl+C to stop.")
        print(f"===============================================================")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down server gracefully.")

if __name__ == '__main__':
    main()
