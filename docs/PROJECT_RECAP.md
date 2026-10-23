# Chandigarh City Crash Test (C3T) — Comprehensive Project Architecture & Technical Recap

**Document Purpose:** Complete technical briefing of the codebase, tech stack, architecture, implemented systems, synthetic/simulated components, and remaining roadmap. Suitable for sharing with engineers or external LLMs (such as ChatGPT) for full context handoff.

---

## 1. System Overview & Problem Statement
* **Project Name:** Chandigarh City Crash Test (C3T)
* **Goal:** A digital twin and urban stress-testing simulation platform for the city of Chandigarh, India. It simulates how extreme external stresses (e.g., monsoon flash flooding, power grid trips, heatwaves, and civic protests) trigger cascading failures across interdependent municipal sectors, and leverages **Google Gemini AI** to produce plain-English executive summaries, mitigation playbooks, and grievance triage.
* **Current Active Branch:** `feature/gemini-integration` (Tracking `OverClock-Force/chandigarh-city-crash-test`)

---

## 2. Complete Technology Stack

### Frontend
* **Core Framework:** React 18+ (SPA)
* **Build Tooling:** Vite (ES modules, fast HMR)
* **Styling:** Custom Vanilla CSS with responsive design system, dark-mode styling, glassmorphism cards, and dynamic visual states (no Tailwind dependency).
* **Icons:** Lucide React (`lucide-react`)
* **State Management:** React native hooks (`useState`, `useEffect`, `useCallback`)
* **API Communication:** Fetch wrapper in `src/api/client.js` with unified error handling and backend payload adapters.

### Backend
* **Runtime & Framework:** Python 3.11+, FastAPI (`fastapi>=0.110.0`)
* **ASGI Server:** Uvicorn (`uvicorn>=0.28.0`)
* **Data Validation & Schemas:** Pydantic v2 (`pydantic>=2.6.0`)
* **Environment Configuration:** `python-dotenv` reading local `.env`
* **Test Suite:** `pytest` + FastAPI `TestClient` (HTTPX)

### AI & Intelligence
* **SDK:** `google-generativeai>=0.8.0` (Google AI Studio / Gemini API)
* **Model Used:** `gemini-1.5-flash`
* **Fallback Strategy:** Deterministic offline heuristics rule engine (so the app never crashes even if the API key is missing or quota is exhausted).

---

## 3. Detailed Component Breakdown

### A. The Risk Simulation Engine (`/risk_engine/`)
* **Files:** `risk_engine/calculator.py`, `risk_engine/rules.py`, `risk_engine/cascade.py`, `risk_engine/models.py`
* **What it does:**
  * Implements an algorithmic cascading failure model across municipal networks:
    1. **Direct Shock:** Applies hazard parameters (Rainfall in mm/hr, Grid load in %, Ambient Temperature in °C, Civic protest events).
    2. **Cascading Propagation:** If Sector A's power grid collapses (>85% load), downstream water pumping stations in Sector B fail, reducing drainage by 40%, which then inundates arterial roads (Sector C) causing traffic throughput to drop to 15%.
    3. **Composite Scoring:** Calculates a weighted composite vulnerability index (0 to 100) per sector and across the entire city:
       * **Critical (Score >= 75):** Immediate systemic collapse danger.
       * **Vulnerable (50 <= Score < 75):** Impaired infrastructure operating at reduced capacity.
       * **Moderate (25 <= Score < 50):** Stressed but stable.
       * **Resilient (Score < 25):** Fully operational.
* **Mitigation Optimizer (`/backend/app/routers/optimize.py`):**
  * Evaluates sector deficits and returns prioritized actionable recommendations (e.g., dispatch 5 mobile dewatering pumps to Sector 17, reroute Madhya Marg traffic, load-shed 15MW from commercial zones to support PGIMER hospital).

### B. Gemini AI Integration (`backend/app/services/gemini_service.py` & `backend/app/routers/ai.py`)
* **1. Risk Narrative Generation (`POST /api/ai/analyze`):**
  * **Input:** Raw JSON output from the simulation engine (composite score, list of critical sectors, cascading failure pathways).
  * **Prompt Strategy:** Structured system prompt instructing Gemini to act as an Urban Disaster Management Specialist.
  * **Output:** A multi-paragraph briefing: Executive Summary, Root Cause Cascades, High-Risk Critical Hotspots, and Immediate Operational Directives.
* **2. Conversational Agent — C3T-AI (`POST /api/ai/chat`):**
  * **Input:** User natural language question + optional active simulation context.
  * **Output:** Context-aware explanation of city behavior (e.g., *"What happens if Sector 22 power fails during 80mm/hr rain?"*).
* **3. Citizen Complaint NLP Triage (`POST /api/ai/complaint`):**
  * **Input:** Free-form unstructured complaint text from a resident (e.g., *"Huge waterlogging near Piccadilly round-about, cars are stuck and transformer is sparking"*).
  * **Output:** Extracted structured JSON containing:
    * `category`: Waterlogging / Power Outage / Traffic Gridlock / Structural.
    * `severity`: Low / Medium / High / Critical.
    * `sector_id`: Tagged sector (e.g., `SEC-22` or `SEC-35`).
    * `confidence`: 0.0 – 1.0 confidence score.
    * `user_must_confirm`: Boolean flag indicating if human verification is required.
* **4. Health & Status Check (`GET /api/ai/status`):**
  * Reports whether `GEMINI_API_KEY` is present and active.

### C. Frontend User Experience (`src/App.jsx`)
* **Interactive Control Deck:** Sliders to tune simulation parameters (Rainfall intensity, Temperature, Grid Load, Event Overrides).
* **City Matrix & Heatmap:** Sector-by-sector visualization showing color-coded risk levels (Green = Resilient, Yellow = Moderate, Orange = Vulnerable, Red = Critical).
* **AI Insights Deck:** Automatically renders the Gemini narrative analysis with markdown formatting as soon as a stress test completes.
* **C3T-AI Interactive Chat Tab:** Chatbot drawer with conversation history for asking ad-hoc urban planning queries.
* **Citizen Grievance Tab:** Complaint submission portal utilizing the AI intake extraction endpoint.

---

## 4. What Is Simulated / Fake (Synthetic Data Details)

To ensure the demo runs reliably without third-party network bottlenecks, several parts currently use **synthetic mock data**:

1. **Sector Baseline Master Data (`data/sectors.json`):**
   * *Real Aspect:* Sector numbering, names, physical layout, and geographical coordinate boundaries represent genuine Chandigarh sectors (Sector 1 to 60, PGIMER, Panjab University).
   * *Synthetic Aspect:* Baseline electrical consumption (in MW), exact stormwater drain flow capacity (cubic meters/sec), live hospital bed occupancy counts, and vehicle density numbers are **statistically generated mock numbers** calibrated to simulate realistic urban behavior.
2. **Hazard Event Data (`data/events.json`):**
   * Pre-configured disaster profiles (e.g., *"Monsoon Cloudburst 2024"*, *"Northern Grid Failure"*, *"May Heatwave Shock"*) are hardcoded historical/simulated scenario templates rather than live sensor feeds.
3. **API Data Status Flag:**
   * All backend responses deliberately return `"data_status": "synthetic_demo"` to maintain transparency regarding data provenance.
4. **Data Storage & State:**
   * User-created scenarios and citizen grievance submissions are stored in **backend in-memory memory dictionaries** (resetting on server restart) rather than a persistent cloud database.

---

## 5. Automated Tests & Quality Assurance
* **Test Location:** `tests/` and `risk_engine/tests/`
* **Test Count:** 21 automated tests (`pytest`)
  * `test_rules.py`: Mathematical rules and risk scoring boundary tests.
  * `test_health_api.py`: Backend root and health status checks.
  * `test_sectors_api.py`: Sector registry integrity and querying.
  * `test_events_api.py`: Disaster event template loading.
  * `test_stress_test_api.py`: Simulation engine execution and validation.
  * `test_optimize_api.py`: Mitigation recommendation engine tests.
  * `test_scenarios_api.py`: Scenario storage and retrieval tests.
  * `test_ai_api.py`: Gemini status, risk analysis, chat assistant, and complaint extraction endpoint verification.
  * `test_e2e_integration.py`: Full end-to-end flow from shock injection to mitigation.
* **Current Test Result:** `21 passed, 0 failed` (100% pass rate).
* **Production Build:** `npm run build` generates clean minified bundles in `dist/` with zero linting/build errors.

---

## 6. What Is Remaining (Roadmap & Unfinished Tech Requirements)

Based on official hackathon criteria and production hardening, the following components are remaining:

| Component | Current State | What Needs to be Implemented |
| :--- | :--- | :--- |
| **1. Cloud Database (Firebase / Firestore)** | In-memory Python dictionaries | Replace in-memory state with **Google Firebase Firestore** to store citizen complaints and saved stress-test scenarios persistently in the cloud. Add **Firebase Auth** for citizen vs. municipal admin roles. |
| **2. Real Public Datasets** | Synthetic JSON mocks | Integrate with **data.gov.in** API or **IMD (India Meteorological Department)** / OpenWeather live API to fetch real-time rainfall, temperature, and AQI for Chandigarh. |
| **3. Multimodal Vision AI** | Text-only Gemini | Implement **Gemini Multimodal Vision** to allow citizens to upload photos of broken water pipes, flooded underpasses, or fallen trees, having AI detect the issue and estimate hazard severity. |
| **4. Real Geospatial Mapping** | Custom SVG / CSS grid | Replace or layer the custom grid with **Google Maps Platform (Maps JavaScript API)** or **Google Earth Engine** satellite layers for genuine GIS coordinates. |
| **5. Cloud Deployment** | Local host only | Create a `Dockerfile` for the FastAPI backend and deploy to **Google Cloud Run**; deploy the React frontend to **Firebase Hosting**. |
