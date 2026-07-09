# AI BSP Merge Copilot 🚀

**AI BSP Merge Copilot** is a state-of-the-art, AI-powered Board Support Package (BSP) migration and 3-way conflict analysis assistant. It automates analysis between:
* **Base BSP** (Reference kernel/dts)
* **Silicon Vendor BSP** (New platform upgrades)
* **Customer BSP** (Product-specific peripheral customization)

Designed specifically for semiconductor vendors, device manufacturers, and embedded Linux platform teams to dramatically accelerate hardware porting cycles.

---

## 📌 Architecture & Design

Rather than checking files sequentially—which creates massive API latency and triggers rate-limits—AI BSP Merge Copilot processes conflicts in **parallel agent stages** with **batched LLM queries**. It compiles all conflict details, formats a unified payload, and queries Gemini exactly once per agent stage.

```text
                  Dataset / Uploaded ZIP
                            │
                            ▼
                     Dataset Loader
                            │
                            ▼
                       FileBundle[]
                            │
                            ▼
                       Diff Engine
                            │
                            ▼
                        Comparator
                            │
                            ▼
                [AI_REVIEW Candidates Filter]
                            │
                            ▼
          ┌─────────────────┼─────────────────┐
          │                 │                 │
    Engineer Agent    Reviewer Agent      PM Agent
    (Batch Prompt)    (Batch Prompt)   (Batch Prompt)
          │                 │                 │
          └─────────────────┼─────────────────┘
                            │
                            ▼
                   Streamlit Dashboard
                 (Interactive Inspector)
```

### The Three-Agent Synthesis:
1. **Engineer Agent**: Performs initial code analysis, isolates conflicting node allocations/properties, and recommends a specific merge resolution.
2. **Reviewer Agent**: Validates safety, compiles warnings (e.g. pin mismatches, electrical configuration issues like RMII vs RGMII), and calculates validation confidence.
3. **PM (Manager) Agent**: Assesses business and hardware system impact, grades complexity (LOW/MEDIUM/HIGH), and estimates developer integration time in hours.

---

## 🛠️ Prerequisites

* **Python 3.13+**
* [**uv**](https://github.com/astral-sh/uv) (Recommended: extremely fast package and virtualenv manager)

---

## 🚀 Setup Instructions

### 1. Clone the Repository
```bash
git clone https://github.com/Kartik-Burele/Ai-luminati_AutoBSP.git
cd Ai-luminati_AutoBSP
```

### 2. Configure Environment & API Key
Create a `.env` file in the project root directory. Do not commit this file to Git (it is already blacklisted in `.gitignore`).

Add your Gemini API Key:
```env
GEMINI_API_KEY=your_actual_gemini_api_key_here
```

### 3. Install Dependencies
If you have `uv` installed, it will automatically bootstrap and install the packages listed in `pyproject.toml` when you run commands. 
Otherwise, create a virtual environment manually:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows use: .venv\Scripts\activate
pip install -r pyproject.toml
```

---

## 💻 Running the Project

### A. Run CLI Analysis
Run the main script to execute a command-line pipeline run on the pre-loaded `complex` dataset:
```bash
# Using uv (recommended)
uv run python main.py

# Using standard virtualenv
python main.py
```

### B. Run Streamlit Interactive Dashboard
Launch the premium web interface:
```bash
# Using uv (recommended)
uv run streamlit run app.py

# Using standard virtualenv
streamlit run app.py
```

Open `http://localhost:8501` in your browser to view the application.

---

## 📊 Pre-Loaded Datasets

The repository includes mock datasets located in the `datasets/` directory:
1. **`sample`**: A minimal device tree configuration for initial verification.
2. **`complex`**: A realistic platform migration with complex conflicts in UART current-speed, Ethernet PHY modes (RMII vs RGMII), and overlapping subnode attachments.
3. **`large`**: Benchmark dataset containing 10 DTS/DTSI files to test batch execution capabilities under load.

---

## 📁 Folder Structure

```text
Ai-luminati_AutoBSP/
├── agents/             # Multi-agent layers (Engineer, Reviewer, PM/Manager, Prompts)
├── core/               # Loader, Diff Engine, Comparator, and Pipeline Orchestration
├── datasets/           # Pre-loaded mock BSP datasets for validation
├── models/             # Shared Pydantic/dataclass models
├── utils/              # Debugging and utility modules
├── app.py              # Streamlit Web App entry point
├── main.py             # CLI Pipeline runner
├── pyproject.toml      # Dependency & Project settings
└── README.md           # This documentation
```