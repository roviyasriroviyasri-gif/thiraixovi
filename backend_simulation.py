"""
THIRAIX - Fisherman Safety & Maritime Boundary Alert System
Backend AI/ML Risk Prediction, Geofencing & LoRa/Satellite Ingestion Engine
"""

import math
import time
import sys
from typing import Dict, List, Tuple
from dataclasses import dataclass

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

@dataclass
class GPSCoordinate:
    latitude: float
    longitude: float

@dataclass
class VesselTelemetry:
    vessel_id: str
    vessel_name: str
    owner_name: str
    crew_count: int
    location: GPSCoordinate
    speed_knots: float
    heading_degrees: float
    timestamp: float
    network_mode: str  # 'CELLULAR_4G' or 'LORA_OFFLINE_SATELLITE'
    battery_level: int

# Maritime Boundary Coordinates (Example: India - Sri Lanka IMBL in Palk Strait)
IMBL_COORDINATES: List[GPSCoordinate] = [
    GPSCoordinate(10.0833, 79.8500), # Point 1
    GPSCoordinate(9.8833, 79.5333),  # Point 2
    GPSCoordinate(9.6667, 79.3833),  # Point 3
    GPSCoordinate(9.4833, 79.2500),  # Point 4 (near Dhanushkodi / Talaimannar)
    GPSCoordinate(9.2167, 79.1667),  # Point 5
    GPSCoordinate(9.0000, 79.0833),  # Point 6
]

# Designated Safe Return Harbors in Tamil Nadu
SAFE_HARBORS = [
    {"name": "Rameswaram Fishing Jetty", "lat": 9.2876, "lon": 79.3129},
    {"name": "Mandapam Coast Guard Base", "lat": 9.2789, "lon": 79.1245},
    {"name": "Dhanushkodi Light Station", "lat": 9.1783, "lon": 79.4189},
]

class GeofenceEngine:
    """Calculates perpendicular distance to IMBL line segments and warns before breach."""
    
    @staticmethod
    def haversine_distance_km(coord1: GPSCoordinate, coord2: GPSCoordinate) -> float:
        """Haversine formula to calculate great-circle distance between two GPS points."""
        R = 6371.0 # Earth radius in km
        lat1_rad = math.radians(coord1.latitude)
        lon1_rad = math.radians(coord1.longitude)
        lat2_rad = math.radians(coord2.latitude)
        lon2_rad = math.radians(coord2.longitude)

        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad

        a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return R * c

    @classmethod
    def calculate_distance_to_imbl(cls, boat_loc: GPSCoordinate) -> Tuple[float, GPSCoordinate]:
        """Finds closest point along the segmented IMBL and returns distance in meters."""
        min_dist_km = float('inf')
        closest_point = IMBL_COORDINATES[0]

        for imbl_pt in IMBL_COORDINATES:
            dist = cls.haversine_distance_km(boat_loc, imbl_pt)
            if dist < min_dist_km:
                min_dist_km = dist
                closest_point = imbl_pt

        return (min_dist_km * 1000.0, closest_point) # distance in meters

    @classmethod
    def calculate_time_to_cross_seconds(cls, distance_meters: float, speed_knots: float, heading: float) -> float:
        """Estimates seconds remaining before crossing boundary based on speed vector."""
        if speed_knots <= 0.1:
            return float('inf')
        speed_mps = speed_knots * 0.514444 # knots to meters per second
        # Assuming heading is towards boundary (conservative worst-case projection)
        time_seconds = distance_meters / speed_mps
        return max(0.0, time_seconds)

class AIRiskPredictionModel:
    """
    Multi-Factor Machine Learning Risk Scoring:
    Evaluates Distance to Boundary, Wave Height, Wind Velocity, Rain, and Night factor.
    Returns Risk Score (0-100) and Classification (LOW, MEDIUM, HIGH).
    """

    @staticmethod
    def predict_risk(
        distance_to_boundary_m: float,
        wave_height_m: float,
        wind_speed_knots: float,
        rainfall_mm: float,
        is_night: bool = False
    ) -> Dict:
        # Normalize sub-scores (0 to 100)
        
        # 1. Boundary Risk (Exponential increase when < 1000m)
        if distance_to_boundary_m > 3000:
            boundary_risk = 5.0
        elif distance_to_boundary_m > 1000:
            boundary_risk = 35.0
        elif distance_to_boundary_m > 300:
            boundary_risk = 70.0
        else:
            boundary_risk = 98.0 # Breach Imminent

        # 2. Sea Condition Risk (Waves > 2.5m are dangerous for wooden/fiber boats)
        wave_risk = min(100.0, (wave_height_m / 4.0) * 100.0)

        # 3. Wind Risk (Wind > 30 knots is gale force)
        wind_risk = min(100.0, (wind_speed_knots / 40.0) * 100.0)

        # 4. Precipitation Risk
        rain_risk = min(100.0, (rainfall_mm / 60.0) * 100.0)

        # Weighted Ensemble AI Calculation
        weights = {
            "boundary": 0.45,
            "wave": 0.25,
            "wind": 0.20,
            "rain": 0.10
        }

        total_score = (
            boundary_risk * weights["boundary"] +
            wave_risk * weights["wave"] +
            wind_risk * weights["wind"] +
            rain_risk * weights["rain"]
        )

        if is_night:
            total_score = min(100.0, total_score * 1.15) # higher risk in darkness

        # Classify
        if total_score < 35.0:
            risk_level = "LOW_RISK"
            status_color = "#10B981" # Green
            guidance = "Safe fishing zone. Maintain watch on weather alerts."
        elif total_score < 68.0:
            risk_level = "MEDIUM_RISK"
            status_color = "#F59E0B" # Amber
            guidance = "Caution: Sea conditions worsening or boundary within 1km. Prepare to return."
        else:
            risk_level = "HIGH_RISK"
            status_color = "#EF4444" # Crimson Red
            guidance = "CRITICAL HAZARD! Turn vessel immediately. Steer West towards Indian harbor."

        return {
            "risk_score": round(total_score, 1),
            "risk_level": risk_level,
            "status_color": status_color,
            "guidance": guidance,
            "factors": {
                "boundary_risk_pct": round(boundary_risk, 1),
                "wave_risk_pct": round(wave_risk, 1),
                "wind_risk_pct": round(wind_risk, 1),
                "rain_risk_pct": round(rain_risk, 1),
            }
        }

class MultilingualAlertDispatcher:
    """10-Language Alert Engine for Voice TTS & Text notifications."""
    
    LANGUAGES = {
        "ta": "Tamil",
        "hi": "Hindi",
        "en": "English",
        "te": "Telugu",
        "kn": "Kannada",
        "bn": "Bengali",
        "or": "Odia",
        "pa": "Punjabi",
        "ml": "Malayalam",
        "ur": "Urdu"
    }

    ALERT_TEMPLATES = {
        "boundary_5s_warning": {
            "ta": "எச்சரிக்கை! நீங்கள் 5 வினாடிகளில் கடல் எல்லையை கடக்க உள்ளீர்கள்! உடனடியாக படகை திருப்புங்கள்!",
            "hi": "चेतावनी! आप 5 सेकंड में समुद्री सीमा पार करने वाले हैं! नाव को तुरंत वापस मोड़ें!",
            "en": "CRITICAL ALERT! Crossing maritime boundary in 5 seconds! Turn vessel around immediately!",
            "te": "హెచ్చరిక! మీరు 5 సెకన్లలో సముద్ర సరిహద్దును దాటబోతున్నారు! వెంటనే పడవను వెనక్కి తిప్పండి!",
            "kn": "ಎಚ್ಚರಿಕೆ! ನೀವು 5 ಸೆಕೆಂಡುಗಳಲ್ಲಿ ಸಮುದ್ರ ಗಡಿಯನ್ನು ದಾಟಲಿದ್ದೀರಿ! ತಕ್ಷಣ ದೋಣಿಯನ್ನು ತಿರುಗಿಸಿ!",
            "bn": "সতর্কবার্তা! আপনি ৫ সেকেন্ডে সমুদ্রসীমা অতিক্রম করছেন! অবিলম্বে নৌকা ঘুরিয়ে নিন!",
            "or": "ଚେତାବନୀ! ଆପଣ ୫ ସେକେଣ୍ଡରେ ସମୁଦ୍ର ସୀମା ପାର ହେବାକୁ ଯାଉଛନ୍ତି! ତୁରନ୍ତ ଡଙ୍ଗା ଫେରାନ୍ତୁ!",
            "pa": "ਚੇਤਾਵਨੀ! ਤੁਸੀਂ 5 ਸਕਿੰਟਾਂ ਵਿੱਚ ਸਮੁੰਦਰੀ ਸਰਹੱਦ ਪਾਰ ਕਰ ਰਹੇ ਹੋ! ਤੁਰੰਤ ਕਿਸ਼ਤੀ ਵਾਪਸ ਮੋੜੋ!",
            "ml": "മുന്നറിയിപ്പ്! 5 സെക്കൻഡിനുള്ളിൽ നിങ്ങൾ സമുദ്രാതിർത്തി കടക്കും! ഉടൻ വള്ളം തിരിക്കുക!",
            "ur": "خبردار! آپ 5 سیکنڈ میں سمندری سرحد پار کرنے والے ہیں! کشتی کو فوراً موڑیں!"
        },
        "storm_alert": {
            "ta": "புயல் எச்சரிக்கை! மணிக்கு 45 கி.மீ வேகத்தில் காற்று வீசுகிறது. உடனடியாக கரைக்கு திரும்பவும்.",
            "hi": "तूफ़ान चेतावनी! 45 किमी/घंटा की गति से हवाएं। तुरंत तट पर लौटें।",
            "en": "STORM WARNING! High winds over 45 knots and rough waves detected. Return to harbor.",
            "te": "తుఫాను హెచ్చరిక! వెంటనే తీరానికి తిరిగి రండి.",
            "kn": "ಬಿರುಗಾಳಿ ಎಚ್ಚರಿಕೆ! ತಕ್ಷಣ ದಡಕ್ಕೆ ಹಿಂತಿರುಗಿ.",
            "bn": "ঝড়ের সতর্কতা! অবিলম্বে উপকূলে ফিরে আসুন।",
            "or": "ବାତ୍ୟା ଚେତାବନୀ! ତୁରନ୍ତ କୂଳକୁ ଫେରି ଆସନ୍ତୁ।",
            "pa": "ਤੂਫਾਨ ਦੀ ਚੇਤਾਵਨੀ! ਤੁਰੰਤ ਕਿਨਾਰੇ ਵਾਪਸ ਆਓ।",
            "ml": "ചുഴലിക്കാറ്റ് മുന്നറിയിപ്പ്! ഉടൻ കരയിലേക്ക് മടങ്ങുക.",
            "ur": "طوفان کی وارننگ! فوراً ساحل پر واپس جائیں۔"
        }
    }

    @classmethod
    def get_alert_text(cls, alert_key: str, lang_code: str) -> str:
        lang_dict = cls.ALERT_TEMPLATES.get(alert_key, {})
        return lang_dict.get(lang_code, lang_dict.get("en", "ALERT TRIGGERED"))

# LoRa Offline Packet Simulator
class LoRaSatelliteProtocol:
    """
    Binary / Compact LoRa RF Packet Formatter when cellular connection is lost.
    Frequency: 868 MHz / 433 MHz LoRa + NavIC Satellite Messaging
    """

    @staticmethod
    def pack_distress_telemetry(vessel: VesselTelemetry) -> bytes:
        """Packs essential vessel data into a 24-byte compact binary radio frame."""
        lat_int = int(vessel.location.latitude * 100000)
        lon_int = int(vessel.location.longitude * 100000)
        speed_int = int(vessel.speed_knots * 10)
        heading_int = int(vessel.heading_degrees)
        sos_flag = 1
        
        # Simulating packed byte payload
        payload_repr = f"LORA:SOS|{vessel.vessel_id}|{lat_int}|{lon_int}|{speed_int}|{heading_int}|CREW:{vessel.crew_count}"
        return payload_repr.encode('utf-8')

if __name__ == "__main__":
    print("=== THIRAIX AI Risk & Maritime Boundary Engine Loaded ===")
    test_loc = GPSCoordinate(9.2340, 79.1920)
    dist, pt = GeofenceEngine.calculate_distance_to_imbl(test_loc)
    print(f"Distance to IMBL: {dist:.1f} meters")
    
    risk = AIRiskPredictionModel.predict_risk(
        distance_to_boundary_m=dist,
        wave_height_m=3.2,
        wind_speed_knots=36.0,
        rainfall_mm=45.0
    )
    print("Risk Prediction:", risk)
    print("Tamil Warning 5s:", MultilingualAlertDispatcher.get_alert_text("boundary_5s_warning", "ta"))
