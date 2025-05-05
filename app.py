import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
import requests
import math

UBIDOTS_TOKEN = "BBUS-R2zm9miwHkGOtTp5NGFC3sfyqnLopm"
DEVICE_LABEL = "water-pump"
VARIABLE_MOIST = "soil_moisture"
VARIABLE_PUMPSTATUS = "pump_status"
UBIDOTS_MOIST = f"https://industrial.api.ubidots.com/api/v1.6/devices/{DEVICE_LABEL}/{VARIABLE_MOIST}/lv"
UBIDOTS_PUMPSTATUS = f"https://industrial.api.ubidots.com/api/v1.6/devices/{DEVICE_LABEL}/{VARIABLE_PUMPSTATUS}/lv"

# Simulasi database untuk menyimpan data kelembaban
if 'moisture_data' not in st.session_state:
    st.session_state.moisture_data = []

if 'last_update' not in st.session_state:
    st.session_state.last_update = datetime.now()

# Fungsi untuk memperbarui data
def update_data(moisture, pump_status):
    new_data = {
        'timestamp': datetime.now(),
        'moisture': moisture,
        'pump_status': pump_status
    }
    st.session_state.moisture_data.append(new_data)
    st.session_state.last_update = datetime.now()

# Antarmuka pengguna
st.title("🌱 Smart Irrigation System")
st.write("Sistem irigasi cerdas berbasis IoT dan AI untuk pertanian berkelanjutan")

# Input untuk simulasi data
if st.button("Perbarui Data"):

    headers = {"X-Auth-Token": UBIDOTS_TOKEN}
    response_moist = requests.get(UBIDOTS_MOIST, headers=headers)
    response_pumpstatus = requests.get(UBIDOTS_PUMPSTATUS, headers=headers)
    moistureValue = int(float(response_moist.text))
    pumpstatusValue = int(float(response_pumpstatus.text))
    st.success(f"Data Terakhir : {moistureValue}%, Status Pompa : {pumpstatusValue > 0 and "HIDUP" or "MATI"}")
    pump_status = pumpstatusValue > 0

    update_data(moistureValue, pump_status)
    response_moist.close()
    response_pumpstatus.close()

    moisture = np.random.uniform(20, 80)  # Simulasi kelembaban tanah
      # Pompa aktif jika kelembaban di bawah 30%
    
    
# Tampilkan data historis
if st.session_state.moisture_data:
    df = pd.DataFrame(st.session_state.moisture_data)
    st.subheader("Data Historis Kelembaban Tanah")
    st.dataframe(df)

    # Visualisasi data
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df['timestamp'], y=df['moisture'], mode='lines+markers', name='Kelembaban Tanah'))
    fig.add_hline(y=30, line_dash="dash", line_color="red", annotation_text="Ambang Minimum")
    fig.update_layout(title='Kelembaban Tanah Seiring Waktu', xaxis_title='Waktu', yaxis_title='Kelembaban (%)')
    st.plotly_chart(fig)

    # Rekomendasi irigasi
    if df['moisture'].iloc[-1] < 30:
        st.warning("Direkomendasikan untuk melakukan irigasi!")
    else:
        st.success("Kelembaban tanah dalam kondisi optimal.")
else:
    st.info("Belum ada data tersedia. Klik 'Perbarui Data' untuk mengambil data.")
