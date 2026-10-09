from flask import Flask, render_template, request, jsonify
from urllib.parse import quote

app = Flask(__name__)

# Tamil Nadu's 38 districts
DISTRICTS = [
    "Ariyalur", "Chengalpattu", "Chennai", "Coimbatore", "Cuddalore",
    "Dharmapuri", "Dindigul", "Erode", "Kallakurichi", "Kancheepuram",
    "Kanniyakumari", "Karur", "Krishnagiri", "Madurai", "Mayiladuthurai",
    "Nagapattinam", "Namakkal", "Nilgiris", "Perambalur", "Pudukkottai",
    "Ramanathapuram", "Ranipet", "Salem", "Sivaganga", "Tenkasi",
    "Thanjavur", "Theni", "Thoothukudi", "Tiruchirappalli", "Tirunelveli",
    "Tirupathur", "Tiruppur", "Tiruvallur", "Tiruvannamalai",
    "Tiruvarur", "Vellore", "Viluppuram", "Virudhunagar"
]

ACCESSIBILITY_LABELS = {
    "wheelchair": "Wheelchair user",
    "visual": "Visual impairment",
    "hearing": "Hearing impairment",
    "mobility": "Limited mobility / less walking",
    "elderly": "Elderly traveller",
    "other": "Other accessibility needs"
}

CONCERN_LABELS = {
    "less_walking": "Short walking distances",
    "ramps": "Ramps / step-free access",
    "accessible_bathroom": "Accessible bathrooms",
    "quiet_breaks": "Frequent rest breaks",
    "visual_guidance": "Clear visual / audio guidance",
    "hearing_support": "Written instructions",
    "lift": "Lift / elevator access",
    "accessible_transport": "Accessible transport"
}

def maps_search(query):
    return "https://www.google.com/maps/search/?api=1&query=" + quote(query)

def build_plan(data):
    district = data.get("district", "Chennai")
    days = max(1, min(int(data.get("days", 2)), 14))
    accessibility = data.get("accessibility", [])
    concerns = data.get("concerns", [])
    start = data.get("start", district)
    pace = data.get("pace", "relaxed")

    # These are planning prompts, not verified accessibility claims.
    day_plans = []
    for day in range(1, days + 1):
        day_plans.append({
            "day": day,
            "title": f"Day {day} — {district} at your pace",
            "morning": f"Choose one nearby attraction in {district}; contact the venue before travelling to confirm step-free entry, seating and toilet access.",
            "afternoon": "Plan a nearby meal and a long rest break. Keep a flexible return option.",
            "evening": "Choose a low-effort local activity or return to your accommodation early.",
        })

    hotel_query = f"hotels in {district} Tamil Nadu with accessibility facilities"
    attraction_query = f"tourist attractions in {district} Tamil Nadu"
    transport_query = f"accessible transport in {district} Tamil Nadu"

    return {
        "district": district,
        "days": days,
        "accessibility": [ACCESSIBILITY_LABELS.get(x, x) for x in accessibility],
        "concerns": [CONCERN_LABELS.get(x, x) for x in concerns],
        "pace": pace,
        "start": start,
        "day_plans": day_plans,
        "hotel_url": maps_search(hotel_query),
        "attractions_url": maps_search(attraction_query),
        "transport_url": maps_search(transport_query),
        "map_embed": "https://www.google.com/maps?q=" + quote(district + ", Tamil Nadu") + "&output=embed"
    }

@app.route("/")
def home():
    return render_template("index.html", districts=DISTRICTS)

@app.route("/plan", methods=["POST"])
def plan():
    data = request.get_json(silent=True) or {}
    if data.get("district") not in DISTRICTS:
        return jsonify({"error": "Please choose a district in Tamil Nadu."}), 400
    try:
        days = int(data.get("days", 1))
    except (TypeError, ValueError):
        return jsonify({"error": "Choose a valid number of days."}), 400
    if not 1 <= days <= 14:
        return jsonify({"error": "Trip duration must be between 1 and 14 days."}), 400
    data["days"] = days
    return jsonify(build_plan(data))

if __name__ == "__main__":
    app.run(debug=True)
