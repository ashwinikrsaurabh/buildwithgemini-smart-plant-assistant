# Copyright 2026 Google LLC
# Firestore tools for Smart Plant & Greenhouse Assistant

import datetime
from google.cloud import firestore
from google.adk.tools.tool_context import ToolContext

PROJECT_ID = "qwiklabs-gcp-02-bac4296bfb63"
COLLECTION_NAME = "plants"



def _get_firestore_client() -> firestore.Client:
    """Returns a Firestore client initialized with hardcoded GCP project ID."""
    return firestore.Client(project=PROJECT_ID)


def get_plant_details(plant_id: str) -> str:
    """Retrieves detailed information for a specific plant from Firestore inventory.

    Args:
        plant_id: The unique identifier or slug of the plant (e.g., 'monstera-deliciosa', 'golden-pothos', 'peace-lily').

    Returns:
        A formatted string with plant specs, care instructions, stock level, and status.
    """
    try:
        db = _get_firestore_client()
        doc_ref = db.collection(COLLECTION_NAME).document(plant_id.lower().strip())
        doc = doc_ref.get()

        if not doc.exists:
            # Fallback search by plant name
            query = db.collection(COLLECTION_NAME).stream()
            matching_plants = [
                d.to_dict() for d in query if plant_id.lower() in d.to_dict().get("name", "").lower()
            ]
            if matching_plants:
                p = matching_plants[0]
            else:
                return f"No plant found with ID or name matching '{plant_id}' in Firestore inventory."
        else:
            p = doc.to_dict()

        return (
            f"🌿 **{p.get('name', 'Unknown')}** ({p.get('species', 'N/A')})\n"
            f"- **Plant ID**: {p.get('id', plant_id)}\n"
            f"- **Status**: {p.get('status', 'Unknown')}\n"
            f"- **Watering Frequency**: Every {p.get('water_frequency_days', 'N/A')} days\n"
            f"- **Last Watered**: {p.get('last_watered', 'N/A')}\n"
            f"- **Sunlight**: {p.get('sunlight', 'N/A')}\n"
            f"- **Stock Count**: {p.get('stock_count', 0)} in stock\n"
            f"- **Care Notes**: {p.get('care_notes', 'N/A')}"
        )
    except Exception as e:
        return f"Error retrieving plant details from Firestore: {str(e)}"


def list_plants_inventory(status_filter: str = "") -> str:
    """Lists all plants available in the greenhouse inventory from Firestore.

    Args:
        status_filter: Optional filter by plant health status (e.g. 'Healthy', 'Needs Attention'). Leave empty to list all.

    Returns:
        A formatted inventory list summary of plants.
    """
    try:
        db = _get_firestore_client()
        docs = db.collection(COLLECTION_NAME).stream()
        plants = [d.to_dict() for d in docs]

        if not plants:
            return "The Firestore plant inventory is currently empty."

        if status_filter:
            plants = [p for p in plants if p.get("status", "").lower() == status_filter.lower()]

        if not plants:
            return f"No plants found matching status filter '{status_filter}'."

        result_lines = [f"📋 **Greenhouse Inventory ({len(plants)} items)**:"]
        for p in plants:
            result_lines.append(
                f"• **{p.get('name')}** (ID: `{p.get('id')}`) - Status: {p.get('status')} | Stock: {p.get('stock_count')} | Last Watered: {p.get('last_watered')}"
            )

        return "\n".join(result_lines)
    except Exception as e:
        return f"Error listing plants from Firestore: {str(e)}"


def update_plant_care(plant_id: str, last_watered: str = None, stock_count: int = None, status: str = None) -> str:
    """Updates care log, status, or stock count for a plant in Firestore.

    Args:
        plant_id: The ID of the plant to update (e.g., 'monstera-deliciosa').
        last_watered: Updated watering date string (e.g., '2026-09-22'). If None, keeps existing.
        stock_count: Updated quantity in stock. If None, keeps existing.
        status: Updated health status (e.g., 'Healthy', 'Needs Attention'). If None, keeps existing.

    Returns:
        A confirmation message with updated plant data.
    """
    try:
        db = _get_firestore_client()
        doc_ref = db.collection(COLLECTION_NAME).document(plant_id.lower().strip())
        doc = doc_ref.get()

        if not doc.exists:
            return f"Error: Plant ID '{plant_id}' does not exist in Firestore."

        updates = {}
        if last_watered:
            updates["last_watered"] = last_watered
        if stock_count is not None:
            updates["stock_count"] = stock_count
        if status:
            updates["status"] = status

        if not updates:
            return "No fields provided to update."

        doc_ref.update(updates)
        return f"✅ Successfully updated plant '{plant_id}' in Firestore with changes: {updates}"
    except Exception as e:
        return f"Error updating plant care in Firestore: {str(e)}"


def add_plant_to_inventory(
    plant_id: str,
    name: str,
    species: str,
    water_frequency_days: int = 7,
    sunlight: str = "Bright indirect light",
    care_notes: str = "",
    stock_count: int = 1,
    status: str = "Healthy",
) -> str:
    """Adds a new plant to the greenhouse inventory in Firestore.

    Args:
        plant_id: Unique slug/id for the plant (e.g., 'snake-plant').
        name: Common name of the plant (e.g., 'Snake Plant').
        species: Botanical species name (e.g., 'Sansevieria trifasciata').
        water_frequency_days: Recommended interval between waterings in days.
        sunlight: Light requirement description.
        care_notes: Care instructions or tips.
        stock_count: Quantity available in inventory.
        status: Initial health status ('Healthy', 'Needs Attention').

    Returns:
        Confirmation message of plant creation.
    """
    try:
        db = _get_firestore_client()
        plant_data = {
            "id": plant_id.lower().strip(),
            "name": name,
            "species": species,
            "water_frequency_days": water_frequency_days,
            "sunlight": sunlight,
            "care_notes": care_notes,
            "stock_count": stock_count,
            "status": status,
            "last_watered": datetime.date.today().isoformat(),
        }
        db.collection(COLLECTION_NAME).document(plant_id.lower().strip()).set(plant_data)
        return f"🎉 Added new plant **{name}** (`{plant_id}`) to Firestore inventory."
    except Exception as e:
        return f"Error adding plant to Firestore: {str(e)}"


def calculate_fertilizer_dosage(
    pot_diameter_inches: float,
    pot_height_inches: float = 8.0,
    target_ppm_or_ratio: str = "standard",
) -> str:
    """Calculates soil volume, recommended water application volume, and liquid fertilizer dosage for a plant pot.

    Args:
        pot_diameter_inches: Top diameter of the container/pot in inches (e.g. 10.0 for a 10-inch pot).
        pot_height_inches: Height or depth of the pot in inches (default: 8.0 inches).
        target_ppm_or_ratio: Strength ratio ('light', 'standard', or 'heavy').

    Returns:
        A formatted summary of container volume (L & gal), recommended water volume, and liquid fertilizer dosage (ml & tsp).
    """
    import math

    # Calculate cylindrical volume in cubic inches and convert to liters & gallons
    radius_inches = pot_diameter_inches / 2.0
    volume_cu_in = math.pi * (radius_inches**2) * pot_height_inches
    volume_liters = volume_cu_in * 0.0163871
    volume_gallons = volume_liters / 3.78541

    # Recommended thorough watering is approx 20% of container volume
    water_volume_liters = volume_liters * 0.20
    water_volume_quarts = water_volume_liters * 1.05669

    # Dilution rates in ml per Liter of water
    rates = {
        "light": 2.5,
        "standard": 5.0,
        "heavy": 7.5,
    }
    ml_per_liter = rates.get(target_ppm_or_ratio.lower(), 5.0)

    fertilizer_ml = round(water_volume_liters * ml_per_liter, 2)
    fertilizer_tsp = round(fertilizer_ml / 4.92892, 2)

    return (
        f"🧪 **Fertilizer & Water Calculator ({pot_diameter_inches:g}\" pot)**\n"
        f"- **Estimated Container Volume**: {volume_liters:.2f} Liters ({volume_gallons:.2f} Gallons)\n"
        f"- **Recommended Water per Application**: {water_volume_liters:.2f} Liters ({water_volume_quarts:.2f} Quarts)\n"
        f"- **Target Strength**: {target_ppm_or_ratio.title()} ({ml_per_liter} ml/L)\n"
        f"- **Calculated Fertilizer Dosage**: **{fertilizer_ml} ml** (~{fertilizer_tsp} teaspoons) per watering"
    )


def fetch_live_greenhouse_climate(city: str) -> str:
    """Fetches real-time live environmental weather and climate data (temperature, humidity, cloud cover, precipitation) for a city.

    Args:
        city: City name to look up environmental weather data for (e.g., 'Seattle', 'San Francisco', 'Miami').

    Returns:
        Real live weather conditions and environmental care implications for plants.
    """
    import json
    import os
    import urllib.parse
    import urllib.request

    try:
        # Resolve city to coordinates using free Open-Meteo Geocoding API
        api_key = os.environ.get("OPEN_METEO_API_KEY", "")  # Optional API key support
        encoded_city = urllib.parse.quote(city.strip())
        geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={encoded_city}&count=1&language=en&format=json"

        req1 = urllib.request.Request(geo_url, headers={"User-Agent": "SmartPlantAssistant/1.0"})
        with urllib.request.urlopen(req1, timeout=5) as resp1:
            geo_res = json.loads(resp1.read().decode("utf-8"))

        if not geo_res.get("results"):
            return f"Could not find geographic coordinates for city '{city}'."

        loc = geo_res["results"][0]
        lat, lon = loc["latitude"], loc["longitude"]
        location_name = f"{loc['name']}, {loc.get('admin1', loc.get('country', ''))}"

        # Fetch current weather parameters
        weather_url = (
            f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}"
            f"&current=temperature_2m,relative_humidity_2m,precipitation,cloud_cover,wind_speed_10m"
        )
        if api_key:
            weather_url += f"&apikey={api_key}"

        req2 = urllib.request.Request(weather_url, headers={"User-Agent": "SmartPlantAssistant/1.0"})
        with urllib.request.urlopen(req2, timeout=5) as resp2:
            w_res = json.loads(resp2.read().decode("utf-8"))

        current = w_res.get("current", {})

        temp_c = current.get("temperature_2m", 20.0)
        temp_f = round((temp_c * 9 / 5) + 32, 1)
        humidity = current.get("relative_humidity_2m", 50)
        cloud_cover = current.get("cloud_cover", 0)
        precip = current.get("precipitation", 0.0)
        wind_speed = current.get("wind_speed_10m", 0.0)

        # Plant care implications based on real humidity & light
        humidity_advice = (
            "High humidity — great for tropical plants!"
            if humidity >= 60
            else "Low humidity — consider misting or using a humidifier for tropical plants."
        )
        light_advice = (
            "Overcast/Cloudy — reduced natural sunlight."
            if cloud_cover > 60
            else "Clear/Sunny — ensure shade cloth if high heat."
        )

        return (
            f"🌤️ **Live Environmental Climate for {location_name}**:\n"
            f"- **Temperature**: {temp_c}°C ({temp_f}°F)\n"
            f"- **Relative Humidity**: {humidity}%\n"
            f"- **Cloud Cover / Sunlight**: {cloud_cover}% cloud cover\n"
            f"- **Precipitation**: {precip} mm\n"
            f"- **Wind Speed**: {wind_speed} km/h\n"
            f"💡 **Greenhouse Advice**: {humidity_advice} {light_advice}"
        )
    except Exception as e:
        return f"Error fetching live climate data for '{city}': {str(e)}"


def geocode_address(address: str) -> str:
    """Converts a street address or city name into geographic latitude and longitude coordinates using Google Maps Geocoding REST API.

    Args:
        address: The address or place name to geocode (e.g. '1600 Amphitheatre Pkwy, Mountain View, CA' or 'Seattle, WA').

    Returns:
        A summary string containing formatted address, latitude, longitude, and place ID.
    """
    import json
    import os
    import urllib.parse
    import urllib.request

    api_key = os.environ.get("GOOGLE_MAPS_API_KEY", "")
    if not api_key:
        return "Error: GOOGLE_MAPS_API_KEY environment variable is not set."

    try:
        url = f"https://maps.googleapis.com/maps/api/geocode/json?address={urllib.parse.quote(address.strip())}&key={api_key}"
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode("utf-8"))

        if data.get("status") != "OK" or not data.get("results"):
            return f"Geocoding API failed to resolve address '{address}'. Status: {data.get('status')}"

        first = data["results"][0]
        loc = first["geometry"]["location"]
        formatted_address = first.get("formatted_address", address)
        place_id = first.get("place_id", "N/A")

        return (
            f"📍 **Geocoding Result**:\n"
            f"- **Address**: {formatted_address}\n"
            f"- **Location**: Latitude {loc['lat']}, Longitude {loc['lng']}\n"
            f"- **Place ID**: {place_id}"
        )
    except Exception as e:
        return f"Error calling Google Maps Geocoding API: {str(e)}"


def find_nearby_places(
    latitude: float,
    longitude: float,
    place_type: str = "florist",
    radius_meters: float = 5000.0,
) -> str:
    """Finds nearby places (e.g. garden centers, florists, hardware stores) around coordinates using Google Places API (New) REST endpoint.

    Args:
        latitude: Center latitude coordinate.
        longitude: Center longitude coordinate.
        place_type: Category/type of place (e.g., 'florist', 'hardware_store', 'store', 'park').
        radius_meters: Search radius in meters (default: 5000.0 meters / 5km).

    Returns:
        A list of nearby places with name, formatted address, rating, and location coordinates.
    """
    import json
    import os
    import urllib.request

    api_key = os.environ.get("GOOGLE_MAPS_API_KEY", "")
    if not api_key:
        return "Error: GOOGLE_MAPS_API_KEY environment variable is not set."

    try:
        url = "https://places.googleapis.com/v1/places:searchNearby"
        body = {
            "includedTypes": [place_type.lower().strip()],
            "maxResultCount": 5,
            "locationRestriction": {
                "circle": {
                    "center": {"latitude": latitude, "longitude": longitude},
                    "radius": float(radius_meters),
                }
            },
        }

        req = urllib.request.Request(
            url,
            data=json.dumps(body).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "X-Goog-Api-Key": api_key,
                "X-Goog-FieldMask": "places.displayName,places.formattedAddress,places.location,places.types,places.rating",
            },
            method="POST",
        )

        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode("utf-8"))

        places = data.get("places", [])
        if not places:
            return f"No nearby places found of type '{place_type}' within {radius_meters}m of ({latitude}, {longitude})."

        results = [f"🏪 **Nearby Places ({place_type})**:"]
        for p in places:
            display_name = p.get("displayName", {}).get("text", "Unknown Place")
            address = p.get("formattedAddress", "No address provided")
            loc = p.get("location", {})
            rating = p.get("rating", "N/A")
            lat_lng_str = f"({loc.get('latitude')}, {loc.get('longitude')})" if loc else "N/A"

            results.append(
                f"• **{display_name}** (Rating: ⭐{rating})\n"
                f"  - **Address**: {address}\n"
                f"  - **Location**: {lat_lng_str}"
            )

        return "\n".join(results)
    except Exception as e:
        return f"Error calling Google Places API (New): {str(e)}"


def consult_plant_kb(query: str) -> str:
    """Search the grounded plant knowledge base RAG corpus for botanical details, plant care advice, or information from Gutenberg plant texts.

    Args:
        query: What to look up (a plant species, botanical detail, pest, or care advice).

    Returns:
        The matched passages from the corpus, or a note if none was found.
    """
    import os
    import vertexai
    from vertexai.preview import rag

    corpus_name = ""
    # Look for corpus name in data/rag_corpus_info.txt or environment variable
    info_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "rag_corpus_info.txt")
    if os.path.exists(info_path):
        with open(info_path, "r") as f:
            corpus_name = f.read().strip()
    if not corpus_name:
        corpus_name = os.environ.get("RAG_CORPUS_NAME", "")

    if not corpus_name:
        return "RAG corpus is not configured yet or name is missing."

    try:
        vertexai.init(project="qwiklabs-gcp-02-bac4296bfb63", location="us-central1")
        resp = rag.retrieval_query(
            text=query,
            rag_resources=[rag.RagResource(rag_corpus=corpus_name)],
            rag_retrieval_config=rag.RagRetrievalConfig(top_k=5),
        )
        contexts = getattr(resp.contexts, "contexts", [])
        passages = [c.text.strip() for c in contexts if getattr(c, "text", "").strip()]
        return "\n\n---\n\n".join(passages) or "No relevant passage found in knowledge base."
    except Exception as e:
        return f"Retrieval failed: {str(e)}"


async def generate_plant_image(prompt: str, tool_context: ToolContext) -> str:
    """Generates an image of a plant, greenhouse scene, or botanical visualization using Gemini 3.1 Flash Lite Image model in global region.

    Saves the image as an artifact in the Playground Artifacts panel and uploads image bytes directly to the public Cloud Storage bucket.

    Args:
        prompt: Detailed description of the plant or greenhouse image to generate.
        tool_context: ToolContext automatically injected by ADK to save artifacts.

    Returns:
        A message containing the public Cloud Storage HTTPS URL of the generated image.
    """
    import inspect
    import uuid
    from google import genai
    from google.genai import types
    from google.cloud import storage

    try:
        genai_client = genai.Client(
            vertexai=True,
            project="qwiklabs-gcp-02-bac4296bfb63",
            location="global",
        )
        res = genai_client.models.generate_content(
            model="gemini-3.1-flash-lite-image",
            contents=prompt.strip(),
            config=types.GenerateContentConfig(response_modalities=["IMAGE"]),
        )

        if not res.candidates or not res.candidates[0].content.parts:
            return "Failed to generate image: No image parts returned by Gemini model."

        part = res.candidates[0].content.parts[0]
        if not hasattr(part, "inline_data") or not part.inline_data:
            return "Failed to generate image: Part did not contain inline image data."

        img_bytes = part.inline_data.data
        mime_type = part.inline_data.mime_type or "image/jpeg"
        ext = "png" if "png" in mime_type else "jpg"
        filename = f"plant_{uuid.uuid4().hex[:8]}.{ext}"

        # 1. Save artifact so it shows up in Playground's Artifacts panel
        artifact_part = types.Part.from_bytes(data=img_bytes, mime_type=mime_type)
        if tool_context:
            res_artifact = tool_context.save_artifact(filename=filename, artifact=artifact_part)
            if inspect.isawaitable(res_artifact):
                await res_artifact


        # 2. Upload image bytes directly to public Cloud Storage bucket (hardcoded bucket string)
        storage_client = storage.Client(project="qwiklabs-gcp-02-bac4296bfb63")
        bucket = storage_client.bucket("smart-plant-assistant-assets-bac4296b")
        blob = bucket.blob(filename)
        blob.upload_from_string(img_bytes, content_type=mime_type)

        public_url = f"https://storage.googleapis.com/smart-plant-assistant-assets-bac4296b/{filename}"

        return (
            f"🖼️ **Generated Plant Image Successfully**:\n"
            f"- **Artifact Name**: `{filename}` (saved to Playground Artifacts panel)\n"
            f"- **Public URL**: {public_url}"
        )
    except Exception as e:
        return f"Error generating plant image: {str(e)}"


async def generate_plant_video(prompt: str, tool_context: ToolContext) -> str:
    """Generates a short video clip for an item in the plant or greenhouse domain using Google's Omni model (gemini-omni-flash-preview) in the global region.

    Saves the video as an artifact in the Playground Artifacts panel and uploads video bytes directly to the public Cloud Storage bucket.

    Args:
        prompt: Text description of the plant or greenhouse video to generate (e.g. 'A 5-second video of a Monstera opening a new leaf in a sunny greenhouse').
        tool_context: ToolContext automatically injected by ADK to save artifacts.

    Returns:
        A message containing the public Cloud Storage HTTPS URL of the generated video.
    """
    import base64
    import inspect
    import uuid
    from google import genai
    from google.genai import types
    from google.cloud import storage

    try:
        genai_client = genai.Client(
            vertexai=True,
            project="qwiklabs-gcp-02-bac4296bfb63",
            location="global",
        )

        response = genai_client.interactions.create(
            model="gemini-omni-flash-preview",
            input=f"Generate a short video clip of {prompt.strip()}",
        )

        if not response.output_video or not response.output_video.data:
            return "Failed to generate video: No video returned by gemini-omni-flash-preview model."

        vid_data = response.output_video.data
        if isinstance(vid_data, str):
            video_bytes = base64.b64decode(vid_data)
        else:
            video_bytes = vid_data

        mime_type = getattr(response.output_video, "mime_type", None) or "video/mp4"
        filename = f"plant_video_{uuid.uuid4().hex[:8]}.mp4"

        # 1. Save artifact so it shows up in Playground's Artifacts panel
        artifact_part = types.Part.from_bytes(data=video_bytes, mime_type=mime_type)
        if tool_context:
            res_artifact = tool_context.save_artifact(filename=filename, artifact=artifact_part)
            if inspect.isawaitable(res_artifact):
                await res_artifact

        # 2. Upload video bytes directly to public Cloud Storage bucket (hardcoded bucket string)
        storage_client = storage.Client(project="qwiklabs-gcp-02-bac4296bfb63")
        bucket = storage_client.bucket("smart-plant-assistant-assets-bac4296b")
        blob = bucket.blob(filename)
        blob.upload_from_string(video_bytes, content_type=mime_type)

        public_url = f"https://storage.googleapis.com/smart-plant-assistant-assets-bac4296b/{filename}"

        return (
            f"🎬 **Generated Plant Video Successfully**:\n"
            f"- **Artifact Name**: `{filename}` (saved to Playground Artifacts panel)\n"
            f"- **Public URL**: {public_url}"
        )
    except Exception as e:
        return f"Error generating plant video: {str(e)}"







