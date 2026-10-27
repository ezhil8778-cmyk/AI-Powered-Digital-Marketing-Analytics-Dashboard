# AI-Powered Digital Marketing Analytics Dashboard

A Streamlit dashboard for exploring customer and digital marketing CSV data.

## Features
- Upload a CSV file or use the bundled synthetic sample.
- Basic KPI cards and dataset preview.
- Category and income-range filters.
- Demographic, spending, and campaign-related summaries.
- Export filtered records to CSV.

## Run locally
```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

## Deploy
1. Create a GitHub repository and upload `app.py`, `requirements.txt`, `README.md`, and the `data/` folder.
2. In Streamlit Community Cloud, choose **Create app**, select the repository and branch, and set the main file path to `app.py`.
3. Deploy, test the public app, then copy the real GitHub and Streamlit URLs into Chapter 8 of the report.

**Important:** This package does not itself create or publish accounts/repositories. Use your own accounts and insert only the real URLs after deployment. The bundled dataset is synthetic.
