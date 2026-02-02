import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import st_folium
import json
import requests

st.set_page_config(
    page_title="Dashboard Kebakaran Hutan 2012",
    layout="wide"
)

st.title("🔥 Dashboard Kebakaran Hutan Amerika Serikat (2012)")

# ===============================
# UPLOAD DATASET
# ===============================
uploaded_file = st.file_uploader(
    "Upload file wildfires_2012_data.csv",
    type=["csv"]
)

if uploaded_file is None:
    st.info("Silakan upload dataset untuk memulai visualisasi.")
    st.stop()

df = pd.read_csv(uploaded_file)
st.success("Dataset berhasil dimuat")
st.dataframe(df.head())

# ===============================
# BERSIHKAN DATA KOORDINAT
# ===============================
df = df.dropna(subset=["LATITUDE", "LONGITUDE"])

center_lat = df_map["LATITUDE"].mean()
center_lon = df_map["LONGITUDE"].mean()


# ===============================
# BAR CHART – JUMLAH KEBAKARAN PER STATE
# ===============================
st.subheader("📊 Jumlah Kebakaran per Negara Bagian")

state_counts = df["STATE"].value_counts().reset_index()
state_counts.columns = ["STATE", "Jumlah_Kebakaran"]

fig_bar = px.bar(
    state_counts,
    x="STATE",
    y="Jumlah_Kebakaran",
    title="Jumlah Kebakaran Hutan per Negara Bagian (2012)",
    labels={
        "STATE": "Negara Bagian",
        "Jumlah_Kebakaran": "Jumlah Kebakaran"
    }
)

st.plotly_chart(fig_bar, use_container_width=True)
st.write("Jumlah data setelah drop NA:", len(df))


# ===============================
# PIE CHART – PENYEBAB KEBAKARAN
# ===============================
st.subheader("🥧 Persentase Penyebab Kebakaran")

cause_counts = df["STAT_CAUSE_DESCR"].value_counts().reset_index()
cause_counts.columns = ["STAT_CAUSE_DESCR", "Jumlah"]

fig_pie = px.pie(
    cause_counts,
    names="STAT_CAUSE_DESCR",
    values="Jumlah",
    title="Persentase Penyebab Kebakaran Hutan (2012)",
    hole=0.4
)

st.plotly_chart(fig_pie, use_container_width=True)

# ===============================
# PETA MARKER CLUSTER (FOLIUM)
# ===============================
st.subheader("🗺️ Peta Lokasi Kebakaran")

# Bersihkan & batasi data
df_map = df.dropna(subset=["LATITUDE", "LONGITUDE"]).sample(3000, random_state=42)

center_lat = df_map["LATITUDE"].mean()
center_lon = df_map["LONGITUDE"].mean()

m = folium.Map(location=[center_lat, center_lon], zoom_start=5)
marker_cluster = MarkerCluster().add_to(m)

for _, row in df_map.iterrows():
    folium.Marker(
        location=[row["LATITUDE"], row["LONGITUDE"]],
        popup=(
            f"State: {row['STATE']}<br>"
            f"Penyebab: {row['STAT_CAUSE_DESCR']}<br>"
            f"Fire Size: {row['FIRE_SIZE']}"
        ),
        icon=folium.Icon(color="red", icon="fire")
    ).add_to(marker_cluster)

st_folium(m, width=1000, height=600)

# ===============================
# LOAD GEOJSON (CACHE)
# ===============================
@st.cache_data
def load_geojson(url):
    return json.loads(requests.get(url).text)

us_states_url = (
    "https://raw.githubusercontent.com/"
    "python-visualization/folium-example-data/main/us_states.json"
)
us_states = load_geojson(us_states_url)

# ===============================
# CHOROPLETH MAP
# ===============================
st.subheader("🗺️ Choropleth Jumlah Kebakaran per Negara Bagian")

state_counts_choro = (
    df.groupby("STATE")
    .size()
    .reset_index(name="count")
)

m2 = folium.Map(location=[center_lat, center_lon], zoom_start=4)

folium.Choropleth(
    geo_data=us_states,
    data=state_counts_choro,
    columns=["STATE", "count"],
    key_on="feature.id",
    fill_color="YlOrRd",
    fill_opacity=0.7,
    line_opacity=0.2,
    legend_name="Jumlah Kebakaran per Negara Bagian (2012)"
).add_to(m2)

st_folium(m2, width=1000, height=600)

st.caption("📌 Sumber data: Wildfires 2012 Dataset")

m_test = folium.Map(location=[37, -95], zoom_start=4)
st_folium(m_test, width=800, height=500)

