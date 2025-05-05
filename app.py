# app.py
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import yfinance as yf

# Mapping ISIN zu Yahoo Ticker (manuell gepflegt, kann ergänzt werden)
isin_to_ticker = {
    "LU1437017350": "EEM",   # iShares MSCI Emerging Markets (Beispiel)
    "IE000BI8OT95": "IWDA.AS", # iShares MSCI World (Beispiel)
    "LU0908500753": "SXR8.DE"   # iShares Core STOXX Europe 600 (Beispiel)
}

# ETF-Daten mit Investitionswert
etfs = [
    {
        "name": "Amundi MSCI Emerging Markets",
        "isin": "LU1437017350",
        "amount": 2194.36,
        "ter": 0.18,
        "initial_value": 2000.00,
        "land_allokation": {
            "China": 31.29,
            "Indien": 18.52,
            "Taiwan": 16.85,
            "Südkorea": 12.20,
            "Brasilien": 5.08,
            "Andere": 16.06,
        },
    },
    {
        "name": "Amundi MSCI World",
        "isin": "IE000BI8OT95",
        "amount": 4410.27,
        "ter": 0.12,
        "initial_value": 4000.00,
        "land_allokation": {
            "USA": 70.63,
            "Japan": 5.66,
            "UK": 3.95,
            "Kanada": 3.28,
            "Frankreich": 3.00,
            "Andere": 13.48,
        },
    },
    {
        "name": "Amundi Stoxx Europe 600",
        "isin": "LU0908500753",
        "amount": 3222.05,
        "ter": 0.07,
        "initial_value": 3000.00,
        "land_allokation": {
            "UK": 23.07,
            "Frankreich": 16.97,
            "Deutschland": 14.91,
            "Schweiz": 14.31,
            "Niederlande": 6.23,
            "Andere": 24.51,
        },
    },
]

total_invested = sum(etf["initial_value"] for etf in etfs)
total_value = sum(etf["amount"] for etf in etfs)

st.set_page_config(page_title="ETF Depot Analyse", layout="wide")
st.title("📈 ETF Depot Analyse")

# Abschnitt 1: Performance
st.header("💹 Performance Tracking")
perf_data = []
for etf in etfs:
    perf = ((etf["amount"] - etf["initial_value"]) / etf["initial_value"]) * 100
    perf_data.append({
        "ETF": etf["name"],
        "Aktueller Wert (€)": etf["amount"],
        "Investiert (€)": etf["initial_value"],
        "Performance (%)": round(perf, 2)
    })
df_perf = pd.DataFrame(perf_data)
st.dataframe(df_perf)

# Abschnitt 2: Reale Gewichtung
st.header("📊 Reale Gewichtung im Portfolio")
invest_df = pd.DataFrame([{
    "ETF": etf["name"],
    "Anteil am Depot (%)": round(etf["amount"] / total_value * 100, 2)
} for etf in etfs])
fig_invest = px.pie(invest_df, names="ETF", values="Anteil am Depot (%)", title="ETF-Gewichtung nach aktuellem Wert")
st.plotly_chart(fig_invest, use_container_width=True)

# Abschnitt 3: Länderallokation
st.header("🌍 Länder-Allokation")
land_agg = {}
for etf in etfs:
    gewicht = etf["amount"] / total_value
    for land, anteil in etf["land_allokation"].items():
        land_agg[land] = land_agg.get(land, 0) + anteil * gewicht

land_df = pd.DataFrame(list(land_agg.items()), columns=["Land", "Gewichtung (%)"])
land_df = land_df.sort_values("Gewichtung (%)", ascending=False)
fig_land = px.bar(land_df, x="Gewichtung (%)", y="Land", orientation="h")
st.plotly_chart(fig_land, use_container_width=True)

# Abschnitt 4: TER-Kosten
st.header("💸 Jährliche Kosten (TER-basiert)")
kosten_data = [{
    "ETF": etf["name"],
    "TER (%)": etf["ter"],
    "Kosten (€)": round(etf["amount"] * etf["ter"] / 100, 2)
} for etf in etfs]

ter_df = pd.DataFrame(kosten_data)
ter_df.loc["Gesamt"] = ["Gesamt", "", round(sum(row["Kosten (€)"] for row in kosten_data), 2)]
st.dataframe(ter_df)

# Abschnitt 5: Historische Kurse
st.header("📉 Historische Kursentwicklung")
start_date = st.date_input("Startdatum für Verlauf", value=datetime(2023, 1, 1))
end_date = datetime.today()
hist_data = {}
for etf in etfs:
    ticker = isin_to_ticker.get(etf["isin"])
    if ticker:
        try:
            df = yf.download(ticker, start=start_date, end=end_date)
            hist_data[etf["name"]] = df["Adj Close"]
        except:
            st.warning(f"Daten für {etf['name']} konnten nicht geladen werden.")

if hist_data:
    df_hist = pd.DataFrame(hist_data)
    st.line_chart(df_hist)

st.caption("Stand: " + datetime.now().strftime("%d.%m.%Y, %H:%M Uhr"))
