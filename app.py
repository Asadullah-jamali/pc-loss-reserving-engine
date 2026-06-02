import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# --------------------------------------------------
# 1. APPLICATION SETUP & PAGE CONFIGURATION
# --------------------------------------------------
st.set_page_config(page_title="P&C Actuarial Reserving Dashboard", layout="wide")
st.title("📊 P&C Loss Reserving & IBNR Engine")
st.markdown("Analyze commercial auto claims data dynamically across 50+ insurance groups using pure mathematical matrices.")

# 2. CACHED DATA INGESTION PIPELINE
@st.cache_data  # Keeps the dataset in cloud memory for instant dropdown loading
def load_data():
    df = pd.read_csv("commercial_auto.csv")
    return df

try:
    raw_df = load_data()

    # Filter out empty records to keep the dashboard select options clean
    valid_data_df = raw_df[raw_df['CumPaidLoss'] > 0]
    company_list = sorted(valid_data_df['GRNAME'].dropna().unique())

    # 3. SIDEBAR NAVIGATION CONTROLS
    selected_company = st.sidebar.selectbox(
        "🎯 Select an Insurance Group:", 
        company_list, 
        index=company_list.index("Agway Ins Co") if "Agway Ins Co" in company_list else 0
    )
    st.sidebar.markdown("---")
    st.sidebar.subheader("🎛️ Pricing Assumptions")
    ielr = st.sidebar.slider("Initial Expected Loss Ratio (IELR)", 0.40, 0.90, 0.65, 0.01)

    # Filter data records specifically for the chosen carrier
    company_df = raw_df[raw_df['GRNAME'] == selected_company].copy()

    # --------------------------------------------------
    # 4. THE ACTUARIAL DIAGONAL FILTER 
    # --------------------------------------------------
    # Determine the actual calendar valuation year for every single data transaction row
    company_df['EvaluationYear'] = company_df['AccidentYear'] + company_df['DevelopmentLag'] - 1

    # STRIKE THE DIAGONAL: Drop future data points to simulate evaluating the portfolio in 2007
    company_df = company_df[company_df['EvaluationYear'] <= 2007]

    # Reshape the flat data table into a geometric Loss Development Triangle grid matrix
    triangle_df = company_df.pivot(
        index='AccidentYear', columns='DevelopmentLag', values='CumPaidLoss'
    ).sort_index(ascending=True)

    # Align Net Earned Premium records (Premium is captured at lag 1)
    premium_df = company_df[company_df['DevelopmentLag'] == 1].set_index('AccidentYear')['EarnedPremDIR']
    premium_series = triangle_df.index.map(premium_df).fillna(0)

    # --------------------------------------------------
    # 5. CORE ACTUARIAL MATHEMATICAL ENGINE
    # --------------------------------------------------

    # PHASE A: Calculate Age-to-Age Development Factors (Link Ratios) via volume-weighted averages
    cols = triangle_df.columns
    link_ratios = []
    for i in range(len(cols) - 1):
        col_curr, col_next = cols[i], cols[i+1]
        valid_rows = triangle_df[col_curr].notna() & triangle_df[col_next].notna()
        sum_curr = triangle_df.loc[valid_rows, col_curr].sum()
        sum_next = triangle_df.loc[valid_rows, col_next].sum()
        link_ratios.append(sum_next / sum_curr if sum_curr != 0 else 1.0)

    # PHASE B: Calculate Cumulative Development Factors (CDF) to Ultimate
    ldfs = link_ratios + [1.0] # Append terminal ultimate tail factor at maximum maturity
    cdfs = [np.prod(ldfs[i:]) for i in range(len(ldfs))]
    cdf_dict = dict(zip(cols, cdfs))

    # PHASE C: Extract Latest Observations & Compute Unreported Ratios per Accident Year
    latest_paid, cl_ultimate, percent_unreported = [], [], []
    for idx, row in triangle_df.iterrows():
        valid_vals = row.dropna()
        last_lag = valid_vals.index[-1] if len(valid_vals) > 0 else cols
        last_val = valid_vals.iloc[-1] if len(valid_vals) > 0 else 0.0

        latest_paid.append(last_val)
        cl_ultimate.append(last_val * cdf_dict[last_lag])
        percent_unreported.append(1 - (1 / cdf_dict[last_lag]))

    latest_paid = np.array(latest_paid)
    cl_ultimate = np.array(cl_ultimate)
    percent_unreported = np.array(percent_unreported)
    premiums = premium_series.values

    # PHASE D: Calculate Ultimate Claims & Required Reserves (IBNR)
    bf_ibnr = premiums * ielr * percent_unreported
    bf_ultimate = latest_paid + bf_ibnr
    cl_ibnr = cl_ultimate - latest_paid

    # Compile all calculated metrics into a clean executive ledger dataframe
    summary_df = pd.DataFrame({
        'Premium ($K)': premiums, 
        'Latest Paid ($K)': latest_paid,
        'CL Ultimate ($K)': cl_ultimate, 
        'BF Ultimate ($K)': bf_ultimate,
        'CL IBNR Reserve ($K)': cl_ibnr, 
        'BF IBNR Reserve ($K)': bf_ibnr
    }, index=triangle_df.index).round(2)

    # --------------------------------------------------
    # 6. DASHBOARD EXECUTIVE COMPONENT RENDERING
    # --------------------------------------------------
    # Top Metrics Headline Cards
    col1, col2, col3 = st.columns(3)
    col1.metric("Insurance Group Focus", selected_company)
    col2.metric("Total Chain-Ladder Reserve", f"${summary_df['CL IBNR Reserve ($K)'].sum():,.2f} K")
    col3.metric("Total Bornhuetter-Ferguson Reserve", f"${summary_df['BF IBNR Reserve ($K)'].sum():,.2f} K")

    st.markdown("---")

    # Main Visual Layout Sections (Table on Left, Bar Chart on Right)
    left_col, right_col = st.columns(2)

    with left_col:
        st.subheader("📋 Reserving Ledger Output ($ in Thousands)")
        st.dataframe(summary_df, use_container_width=True)

    with right_col:
        st.subheader("📈 Unpaid Claims (IBNR) Variance Analysis")
        fig, ax = plt.subplots(figsize=(6, 4.2))
        summary_df[['CL IBNR Reserve ($K)', 'BF IBNR Reserve ($K)']].plot(kind='bar', ax=ax, width=0.7)
        ax.set_ylabel("Losses ($K)")
        ax.set_xlabel("Accident Year")
        ax.grid(axis='y', linestyle='--', alpha=0.5)
        plt.tight_layout()
        st.pyplot(fig)

    # Bottom Expandable Option: View the underlying triangle records matrix grid
    st.markdown("---")
    with st.expander("🔍 View Raw Cumulative Loss Triangle Matrix"):
        st.dataframe(triangle_df.style.format("${:,.2f}", na_rep="-"), use_container_width=True)

except FileNotFoundError:
    st.error("⚠️ 'commercial_auto.csv' not found. Please verify that your dataset file is placed in your project folder.")
