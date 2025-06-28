import sys
import os
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agents.price_agent import fetch_price_with_fallback, compute_deltas, check_alert_enriched

# App title
st.title("Agentic Finance — Price Monitoring")

# Sidebar inputs
st.sidebar.header("Settings")
ticker = st.sidebar.text_input("Stock Ticker", value="AAPL")
static_oc = st.sidebar.slider("Static Open-Close threshold (%)", min_value=1, max_value=20, value=5)
static_hl = st.sidebar.slider("Static High-Low threshold (%)", min_value=1, max_value=20, value=7)
dynamic_window = st.sidebar.slider("Dynamic window (periods)", min_value=2, max_value=10, value=3)
std_multiplier = st.sidebar.slider("Std deviation multiplier", min_value=1, max_value=5, value=2)

# Fetch + check button
if st.button("Fetch Data & Check Alert"):
    data = fetch_price_with_fallback(ticker)

    if data is None or data.empty:
        st.error("No data fetched for this ticker.")
    else:
        # Ensure index is datetime
        if not pd.api.types.is_datetime64_any_dtype(data.index):
            if len(data) == 1:
                data = data.copy()
                data.index = [datetime.now()]
            else:
                data.index = pd.to_datetime(data.index, errors='coerce').fillna(datetime.now())

        data = compute_deltas(data)
        alert = check_alert_enriched(
            data,
            static_oc=static_oc,
            static_hl=static_hl,
            dynamic_window=dynamic_window,
            std_multiplier=std_multiplier
        )

        # Latest deltas display
        if 'Delta_OC' in data.columns and 'Delta_HL' in data.columns:
            latest_row = data.iloc[-1]

            delta_oc = latest_row.get('Delta_OC', float('nan'))
            delta_hl = latest_row.get('Delta_HL', float('nan'))

            try:
                delta_oc_val = float(delta_oc)
            except (TypeError, ValueError):
                delta_oc_val = float('nan')

            try:
                delta_hl_val = float(delta_hl)
            except (TypeError, ValueError):
                delta_hl_val = float('nan')

            st.subheader("Latest Metrics")
            st.write(f"**Delta Open-Close:** {delta_oc_val:.2f} %")
            st.write(f"**Delta High-Low:** {delta_hl_val:.2f} %")
        else:
            st.warning("Delta data unavailable. Check if price data was valid.")

        if alert:
            st.error("🚨 ALERT: Movement exceeded thresholds!")
        else:
            st.success("✅ No alert triggered.")

        # Plot
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=data.index,
            y=data['Close'],
            mode='lines+markers',
            name='Close Price'
        ))

        if alert:
            fig.add_trace(go.Scatter(
                x=[data.index[-1]],
                y=[data['Close'].iloc[-1]],
                mode='markers',
                marker=dict(size=12, color='red'),
                name='Alert Triggered'
            ))

        fig.update_layout(
            title=f"{ticker} Closing Prices",
            xaxis_title="Date",
            yaxis_title="Price (USD)",
            xaxis=dict(
                tickformat="%Y-%m-%d %H:%M",
                tickangle=-45
            ),
            template="simple_white",
            margin=dict(l=40, r=40, t=40, b=80)
        )

        st.plotly_chart(fig, use_container_width=True)
