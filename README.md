# DataPulse — Streamlit Data Analysis Dashboard

A production-ready, modular Streamlit dashboard engineered for exploratory data analysis (EDA), executive KPI monitoring, and interactive business intelligence.

---

## 🏗️ Architecture & Project Structure

The project strictly decouples business and analytical logic from Streamlit's UI rendering pipeline:

```
MK6-Week3/
├── .streamlit/
│   └── config.toml           # Theme configuration, server port (8501), headless setup
├── data/
│   └── sample_sales_data.csv # Multi-dimensional sample dataset
├── src/
│   ├── __init__.py
│   ├── config.py             # Dashboard metadata, paths, colorways, schema definitions
│   ├── components/           # Reusable UI widgets and presentation elements
│   │   ├── charts.py         # Plotly interactive visualizers (line, bar, pie, heatmap, scatter)
│   │   ├── filters.py        # Centralized sidebar filtering controls
│   │   └── metrics.py        # Responsive top-level KPI metric cards
│   ├── services/             # Pure analytical logic and data processing
│   │   ├── analyzer.py       # Metrics calculation, aggregations, correlation matrix
│   │   └── data_loader.py    # Cached data ingestion (`@st.cache_data`) & schema validation
│   └── views/                # Multi-page dashboard views (via st.navigation)
│       ├── overview.py       # Executive summary, KPIs, category & regional breakdown
│       ├── eda.py            # Descriptive stats, univariate/bivariate analysis, raw data
│       └── trends.py         # Multi-cadence time series (D/W/M) & correlation analysis
├── tests/                    # Automated unit tests (pytest)
│   ├── test_analyzer.py      # Tests for analytical aggregations and filters
│   └── test_data_loader.py   # Tests for CSV parsing, caching, and data preprocessing
├── app.py                    # Main application entry point and navigation routing
├── Dockerfile                # Multi-stage/clean container definition with healthchecks
├── docker-compose.yml        # Docker Compose configuration with volume hot-reloading
├── requirements.txt          # Python dependencies
├── .dockerignore
├── .gitignore
└── README.md
```

---

## 🚀 Quickstart with Docker Compose

As per engineering protocol, you can build, run, and test the entire containerized environment with:

```bash
# Clean up any existing instances
docker compose down

# Build and start container in detached mode
docker compose up --build -d
```

Open your browser and navigate to:
👉 **[http://localhost:8501](http://localhost:8501)**

To inspect container logs:
```bash
docker compose logs -f dashboard
```

To stop the dashboard:
```bash
docker compose down
```

---

## 💻 Local Development Setup

If running directly in Python:

1. **Create and activate a virtual environment**:
   ```bash
   python -m venv .venv
   # Windows PowerShell
   .venv\Scripts\Activate.ps1
   # Linux / macOS
   source .venv/bin/activate
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Launch the Streamlit app**:
   ```bash
   streamlit run app.py
   ```

---

## 🧪 Running Automated Tests

Run the test suite using `pytest`:

```bash
# Run tests locally
pytest tests/ -v

# Or run tests inside the running Docker container
docker compose exec dashboard pytest tests/ -v
```

---

## ✨ Features

- **Executive KPI Dashboard**: Instant visibility into Revenue, Profit, Margin %, Units Sold, and Average Rating.
- **Exploratory Data Analysis (EDA)**:
  - Univariate distribution histograms with marginal box plots.
  - Bivariate scatter exploration with categorical color grouping.
  - Descriptive statistics table.
  - Filtered raw data table with one-click CSV download.
- **Trends & Correlation**:
  - Dynamic time-series resampling (Daily, Weekly, Monthly).
  - Pearson correlation matrix heatmap.
- **Custom CSV Upload**: Seamlessly switch between the bundled sample dataset and your own CSV file.
- **Performance Optimized**: Data preprocessing and caching powered by `@st.cache_data`.
