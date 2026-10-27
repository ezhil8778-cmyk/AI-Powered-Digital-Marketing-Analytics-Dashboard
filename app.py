import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

st.set_page_config(page_title="AI-Powered Digital Marketing Analytics Dashboard", layout="wide")
st.title("AI-Powered Digital Marketing Analytics Dashboard")
st.caption("Explore customer, purchase and campaign data with interactive analytics.")

DATA_PATH = Path(__file__).parent / "data" / "marketing_customers.csv"

@st.cache_data
def load_sample():
    return pd.read_csv(DATA_PATH)

def detect_column(df, keywords, numeric=None):
    for col in df.columns:
        name = str(col).lower().replace("_", " ")
        if any(k in name for k in keywords):
            if numeric is True and not pd.api.types.is_numeric_dtype(df[col]):
                continue
            return col
    return None

uploaded = st.sidebar.file_uploader("Upload marketing/customer data (CSV)", type=["csv"])
try:
    df = pd.read_csv(uploaded) if uploaded else load_sample()
except Exception as exc:
    st.error(f"Could not read the CSV file: {exc}")
    st.stop()

if df.empty:
    st.warning("The selected dataset has no rows.")
    st.stop()

df.columns = [str(c).strip() for c in df.columns]
numeric_cols = df.select_dtypes(include=np.number).columns.tolist()
categorical_cols = df.select_dtypes(exclude=np.number).columns.tolist()

st.sidebar.subheader("Filters")
filtered = df.copy()
for col in categorical_cols[:2]:
    options = sorted(filtered[col].dropna().astype(str).unique().tolist())
    if options:
        chosen = st.sidebar.multiselect(f"{col}", options, default=options)
        filtered = filtered[filtered[col].astype(str).isin(chosen)]
income_col = detect_column(filtered, ["income", "annual income", "salary"], True)
if income_col:
    vals = pd.to_numeric(filtered[income_col], errors="coerce").dropna()
    if not vals.empty and vals.min() < vals.max():
        lo, hi = st.sidebar.slider(f"{income_col} range", float(vals.min()), float(vals.max()), (float(vals.min()), float(vals.max())))
        filtered = filtered[pd.to_numeric(filtered[income_col], errors="coerce").between(lo, hi)]

if filtered.empty:
    st.warning("No rows match the current filters. Change the filters in the sidebar.")
    st.stop()

spend_cols = [c for c in numeric_cols if any(k in c.lower() for k in ["spend", "amount", "revenue", "sales"])]
purchase_cols = [c for c in numeric_cols if any(k in c.lower() for k in ["purchase", "orders", "transactions"])]
c1,c2,c3,c4 = st.columns(4)
c1.metric("Records", f"{len(filtered):,}")
c2.metric("Numeric fields", len(numeric_cols))
c3.metric("Total spend / sales", f"{filtered[spend_cols].sum(numeric_only=True).sum():,.2f}" if spend_cols else "Not detected")
c4.metric("Average income", f"{pd.to_numeric(filtered[income_col], errors='coerce').mean():,.2f}" if income_col else "Not detected")

tabs = st.tabs(["Overview", "Customer Demographics", "Purchase Analysis", "Campaign Analysis", "Insights", "Download"])
with tabs[0]:
    st.subheader("Dataset overview")
    st.write(f"Showing **{len(filtered):,}** of **{len(df):,}** records.")
    st.dataframe(filtered.head(100), use_container_width=True)
    if numeric_cols:
        selected_num = st.selectbox("Numeric field to summarise", numeric_cols)
        st.write(filtered[selected_num].describe().to_frame("Summary"))
with tabs[1]:
    st.subheader("Customer demographics")
    if categorical_cols:
        cat = st.selectbox("Category", categorical_cols, key="democat")
        counts = filtered[cat].fillna("Missing").astype(str).value_counts().head(15)
        fig, ax = plt.subplots()
        counts.plot(kind="bar", ax=ax)
        ax.set_ylabel("Records")
        ax.set_xlabel(cat)
        plt.xticks(rotation=35, ha="right")
        st.pyplot(fig)
    else:
        st.info("No categorical columns were detected.")
with tabs[2]:
    st.subheader("Purchase and spending analysis")
    candidates = spend_cols or purchase_cols or numeric_cols
    if candidates:
        col = st.selectbox("Metric", candidates, key="purchase_metric")
        fig, ax = plt.subplots()
        pd.to_numeric(filtered[col], errors="coerce").dropna().plot(kind="hist", bins=20, ax=ax)
        ax.set_xlabel(col)
        st.pyplot(fig)
        st.write("Average:", round(float(pd.to_numeric(filtered[col], errors="coerce").mean()), 2))
    else:
        st.info("No numeric fields are available for analysis.")
with tabs[3]:
    st.subheader("Campaign analysis")
    campaign_cols = [c for c in filtered.columns if any(k in c.lower() for k in ["campaign", "response", "accepted", "conversion", "complain"])]
    if campaign_cols:
        camp = st.selectbox("Campaign-related field", campaign_cols)
        st.dataframe(filtered[camp].fillna("Missing").astype(str).value_counts().rename_axis(camp).reset_index(name="Count"), use_container_width=True)
    else:
        st.info("No campaign-related columns were detected. Upload a dataset containing campaign or response fields.")
with tabs[4]:
    st.subheader("Quick insights")
    st.write(f"- **Rows after filtering:** {len(filtered):,}")
    st.write(f"- **Columns:** {len(filtered.columns)}")
    if numeric_cols:
        means = filtered[numeric_cols].mean(numeric_only=True).sort_values(ascending=False)
        st.write("- Highest average numeric fields:")
        st.dataframe(means.head(5).rename("Average"))
    st.caption("Column detection uses simple name patterns. Verify interpretations before making business decisions.")
with tabs[5]:
    st.subheader("Download filtered data")
    st.download_button("Download filtered CSV", filtered.to_csv(index=False).encode("utf-8"), "filtered_marketing_data.csv", "text/csv")
    st.write("Use the sidebar to adjust filters before exporting.")

st.sidebar.caption("Demo data is synthetic. Do not upload confidential customer information to a public deployment.")
