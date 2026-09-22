# Smart Plant & Greenhouse Assistant 🌿

An intelligent, full-stack AI agent built with Google's **Agent Development Kit (ADK)**, **Vertex AI Agent Engine**, and **A2UI v0.8**. The Smart Plant Assistant helps nursery managers, greenhouse operators, and indoor plant enthusiasts manage inventory, query grounded botanical knowledge, generate plant media, calculate care schedules, and execute code safely in a sandbox environment.

![Smart Plant Assistant Demo](demo.gif)

---

## 🚀 Features & Implemented Capabilities

The Smart Plant Assistant implements a modular suite of tools and GCP integrations wired directly into the ADK agent engine:

### 🧠 Core Agent & Memory
- **Vertex AI Memory Bank**: Integrates `PreloadMemoryTool` and an `after_agent_callback` memory callback to persist user preferences, garden collections, and care notes across sessions.
- **AgentEngine Sandbox Code Execution**: Evaluates mathematical formulas and custom Python calculations safely inside `AgentEngineSandboxCodeExecutor`.
- **A2UI v0.8 Rich Card Rendering**: Transforms agent responses into lightweight, structured UI cards using `A2uiSchemaManager` (v0.8) and `BasicCatalog`.

### 📦 Plant Inventory & Care (Google Cloud Firestore)
- **Document Lookup & Search**: `get_plant_details` and `list_plants_inventory` fetch species specifications, stock levels, and care instructions from Firestore.
- **Inventory & Log Updates**: `update_plant_care` and `add_plant_to_inventory` log watering dates, stock changes, and new botanical entries directly in Firestore.

### 📚 Grounded Botanical Knowledge (Vertex AI RAG Engine)
- **Grounded Search**: `consult_plant_kb` searches a grounded Vertex AI RAG corpus built on curated botanical texts to deliver verified plant care recommendations.

### 🎨 Media Generation & Public Cloud Storage
- **Image Generation**: `generate_plant_image` leverages Gemini 3.1 Flash Lite Image (`gemini-3.1-flash-lite-image`) in the global region, uploads generated images to a public Google Cloud Storage bucket, and saves them to the Playground Artifacts panel.
- **Video Generation**: `generate_plant_video` utilizes Google's Omni model (`gemini-omni-flash-preview`) in the global region via the Interactions API to produce short plant clips, saving them both as ADK artifacts and public Cloud Storage assets.

### 📍 Maps & Location Services
- **Google Maps Geocoding**: `geocode_address` converts street addresses to precise geographic coordinates.
- **Google Places API (New)**: `find_nearby_places` locates nearby garden centers, nurseries, and florists.

### 📊 Calculations & Greenhouse Climate
- **Dosage Calculator**: `calculate_fertilizer_dosage` computes custom water and fertilizer requirements based on plant species and container volume.
- **Greenhouse Climate Sensors**: `fetch_live_greenhouse_climate` reports real-time temperature, humidity, and light levels across greenhouse sections.

---

## 🛠️ Architecture

```
 smart-plant-assistant/
 ├── app/                      # Main ADK Agent Package
 │   ├── agent.py              # Root agent definition, Memory Bank & A2UI callback setup
 │   ├── tools.py              # Firestore, RAG, Image/Video, Places, & Sandbox tools
 │   ├── a2ui_utils.py         # A2UI schema manager & payload formatting
 │   └── fast_api_app.py       # FastAPI application wrapper for ADK agent
 ├── frontend/                 # Web UI & Proxy Server
 │   ├── main.py               # FastAPI proxy forwarding requests to Agent Engine
 │   ├── static/index.html     # Rebranded botanical chat UI with prompt chips
 │   └── Dockerfile            # Container configuration for frontend deployment
 ├── scripts/                  # Utility & Seeding Scripts
 │   ├── seed_firestore.py     # Populates Firestore plant inventory
 │   └── create_rag_corpus.py  # Creates and grounds Vertex AI RAG corpus
 ├── agents-cli-manifest.yaml  # ADK deployment & project configuration
 ├── pyproject.toml            # Dependencies and environment definition
 └── demo.gif                  # Inline demo recording
```

---

## 💻 Local Setup & Development

Follow these steps to run the agent and frontend locally:

### Prerequisites
- Python 3.11+
- `uv` package manager (`pip install uv`)
- Google Cloud project with Vertex AI, Firestore, and Cloud Storage APIs enabled
- Authenticated GCP credentials (`gcloud auth application-default login`)

### 1. Install Dependencies
```bash
uv sync
```

### 2. Set Environment Variables
Copy `.env.example` to `.env` and fill in your GCP project settings:
```bash
cp .env.example .env
```
Key variables:
```env
GOOGLE_CLOUD_PROJECT=your-gcp-project-id
GOOGLE_CLOUD_REGION=us-east1
```

### 3. Seed Firestore Database & RAG Corpus
```bash
uv run python scripts/seed_firestore.py
uv run python scripts/create_rag_corpus.py
```

### 4. Run the Agent Server Locally
```bash
uv run python main.py
```

### 5. Run the Frontend Proxy Locally
Open a new terminal, navigate to `frontend/`, and start the web UI proxy:
```bash
cd frontend
pip install -r requirements.txt
python main.py
```

Open your browser to the local port displayed in your terminal (default port 8080).

---

## 🧪 Testing

Run unit and integration test suites:
```bash
uv run pytest tests/unit tests/integration
```

---

## 📄 License
Apache License 2.0
