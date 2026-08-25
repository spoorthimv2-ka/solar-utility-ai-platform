# Automated Utility Intelligence & Daily Report System

## Run in VS Code

1. Install Python 3.10+.
2. Open this folder in VS Code.
3. Open Terminal.
4. Run:

```bash
python -m venv .venv
```

### Windows
```bash
.venv\Scripts\activate
```

### macOS/Linux
```bash
source .venv/bin/activate
```

5. Install dependencies:

```bash
pip install -r requirements.txt
```

6. Put your Excel files inside the `data` folder.

7. Start:

```bash
streamlit run app.py
```

8. Open the local URL shown by Streamlit, usually:
`http://localhost:8501`

## What this version does

- Reads the uploaded Tata Power Excel workbooks.
- Loads real Grid, Transformer, Hexa, Vega, Solar, Air and Environment values.
- Creates a functional Streamlit dashboard.
- Generates rule-based alerts.
- Shows operational insights.
- Provides daily report and PDF summary.
- Allows new CSV/XLSX uploads and validation.
- Shows source files and SHA256 fingerprints to help prevent duplicate imports.

## Important

This is a strong functional MVP/prototype. It uses local in-memory processing for the dashboard rather than a production PostgreSQL/Supabase database. A database/API layer can be added next once the dashboard flow is validated.
