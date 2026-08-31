import pandas as pd
import pymysql
import streamlit as st
import time

DB_HOST = "127.0.0.1"
DB_USER = "root"
DB_PASSWORD = ""
DB_NAME = "tambak_monitoring"
TABLE_NAME = "monitoring_air"

QOS_COLUMNS = {
    "THROUGHPUT": "FLOAT DEFAULT 0",
    "DELAY": "FLOAT DEFAULT 0",
    "BANDWIDTH": "FLOAT DEFAULT 0",
}

DISPLAY_COLUMNS = [
    "Waktu",
    "Node",
    "Suhu",
    "TDS",
    "pH",
    "Throughput",
    "Packet Loss",
    "Latency (Delay)",
    "Jitter",
    "Bandwidth",
]


st.set_page_config(
    page_title="Dashboard Monitoring Tambak",
    layout="wide",
    initial_sidebar_state="expanded"
)


st.markdown(
    """
    <style>
        /* Modern Bright UI for Streamlit */
        
        /* Import Google Fonts */
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap');

        html, body, [class*="css"] {
            font-family: 'Outfit', sans-serif;
        }

        /* Main background */
        .stApp {
            background: linear-gradient(135deg, #f0f4f8 0%, #d9e2ec 100%);
            color: #102a43;
        }

        /* Page Header */
        .page-header {
            background: rgba(255, 255, 255, 0.85);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.4);
            border-left: 8px solid #0ea5e9;
            border-radius: 12px;
            padding: 24px 30px;
            margin-bottom: 24px;
            box-shadow: 0 10px 30px rgba(16, 42, 67, 0.06);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }
        .page-header:hover {
            transform: translateY(-2px);
            box-shadow: 0 15px 35px rgba(16, 42, 67, 0.1);
        }
        .page-header h1 {
            margin: 0;
            color: #102a43;
            font-size: 32px;
            font-weight: 700;
            letter-spacing: -0.5px;
        }
        .page-header p {
            margin: 8px 0 0;
            color: #334e68;
            font-size: 16px;
            font-weight: 500;
        }

        /* Metrics Cards */
        div[data-testid="stMetric"] {
            background: rgba(255, 255, 255, 0.9);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.6);
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 8px 20px rgba(16, 42, 67, 0.04);
            transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
        }
        div[data-testid="stMetric"]:hover {
            transform: translateY(-5px);
            box-shadow: 0 12px 25px rgba(16, 42, 67, 0.1);
            border-color: #0ea5e9;
        }
        div[data-testid="stMetric"] label {
            color: #627d98 !important;
            font-weight: 600;
            font-size: 14px;
        }
        div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
            color: #102a43 !important;
            font-weight: 700;
            font-size: 28px;
        }
        
        /* Dynamic HTML Metric Cards */
        .dynamic-metric-card {
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.6);
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 8px 20px rgba(16, 42, 67, 0.04);
            transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
            margin-bottom: 1rem;
        }
        .dynamic-metric-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 12px 25px rgba(16, 42, 67, 0.1);
            border-color: #0ea5e9;
        }
        .dynamic-metric-card .label {
            color: #627d98;
            font-weight: 600;
            font-size: 14px;
            margin-bottom: 5px;
        }
        .dynamic-metric-card .value {
            color: #102a43;
            font-weight: 700;
            font-size: 28px;
        }

        /* Sidebar */
        section[data-testid="stSidebar"] {
            background: #ffffff;
            border-right: 1px solid #e4e7eb;
            box-shadow: 2px 0 20px rgba(16, 42, 67, 0.03);
        }
        section[data-testid="stSidebar"] * {
            color: #334e68;
        }
        section[data-testid="stSidebar"] h1, 
        section[data-testid="stSidebar"] h2, 
        section[data-testid="stSidebar"] h3 {
            color: #102a43;
            font-weight: 600;
        }
        .sidebar-note {
            padding: 16px;
            border-radius: 10px;
            background: linear-gradient(135deg, #e0f2fe 0%, #bae6fd 100%);
            color: #0369a1;
            font-size: 14px;
            line-height: 1.6;
            margin-bottom: 20px;
            font-weight: 500;
            border: 1px solid #7dd3fc;
            box-shadow: 0 4px 10px rgba(14, 165, 233, 0.1);
        }
        .sidebar-note * {
            color: #0369a1;
        }

        /* Headings */
        h2, h3, .stMarkdown h2, .stMarkdown h3 {
            color: #102a43 !important;
            font-weight: 600;
            margin-top: 1.5rem;
            margin-bottom: 1rem;
        }

        /* Dataframe/Table */
        div[data-testid="stDataFrame"] {
            background: #ffffff;
            border: 1px solid #e4e7eb;
            border-radius: 12px;
            padding: 12px;
            box-shadow: 0 10px 25px rgba(16, 42, 67, 0.05);
        }
        div[data-testid="stDataFrame"] * {
            color: #334e68;
        }

        /* Alerts/Info */
        div[data-testid="stAlert"] {
            border-radius: 10px;
            border: none;
            box-shadow: 0 4px 12px rgba(16, 42, 67, 0.05);
        }

        /* Inputs / Selects */
        div[data-baseweb="select"] > div,
        div[data-baseweb="input"] > div {
            border-radius: 8px;
            border: 1px solid #cbd2d9;
            background-color: #f5f7fa;
            transition: border-color 0.3s ease, box-shadow 0.3s ease;
        }
        div[data-baseweb="select"] > div:hover,
        div[data-baseweb="input"] > div:hover {
            border-color: #0ea5e9;
        }

        /* Buttons */
        .stButton > button,
        .stDownloadButton > button {
            background: linear-gradient(135deg, #0ea5e9 0%, #0284c7 100%) !important;
            color: #ffffff !important;
            border: none !important;
            border-radius: 8px !important;
            padding: 10px 24px !important;
            font-weight: 600 !important;
            letter-spacing: 0.5px !important;
            box-shadow: 0 6px 15px rgba(14, 165, 233, 0.3) !important;
            transition: all 0.3s ease !important;
        }
        .stButton > button:hover,
        .stDownloadButton > button:hover {
            background: linear-gradient(135deg, #38bdf8 0%, #0ea5e9 100%) !important;
            transform: translateY(-2px) !important;
            box-shadow: 0 8px 20px rgba(14, 165, 233, 0.4) !important;
            color: #ffffff !important;
        }
        .stButton > button:active,
        .stDownloadButton > button:active {
            transform: translateY(0) !important;
            box-shadow: 0 4px 10px rgba(14, 165, 233, 0.3) !important;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


def get_connection():
    return pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor,
    )


@st.cache_data(ttl=25)
def load_sensor_history() -> pd.DataFrame:
    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(f"SHOW COLUMNS FROM `{TABLE_NAME}`")
            existing_columns = {row["Field"].upper() for row in cursor.fetchall()}

            for column_name, column_type in QOS_COLUMNS.items():
                if column_name not in existing_columns:
                    cursor.execute(
                        f"ALTER TABLE `{TABLE_NAME}` ADD COLUMN `{column_name}` {column_type}"
                    )

        connection.commit()

        query = f"""
            SELECT
                `HARI & TANGGAL`,
                `NODE`,
                `SUHU`,
                `TDS`,
                `PH`,
                `THROUGHPUT`,
                `PACKET_LOSS`,
                COALESCE(NULLIF(`LATENCY`, 0), `DELAY`, 0) AS `LATENCY_DELAY`,
                `JITTER`,
                COALESCE(NULLIF(`BANDWIDTH`, 0), `THROUGHPUT`, 0) AS `BANDWIDTH`
            FROM `{TABLE_NAME}`
            ORDER BY `HARI & TANGGAL` DESC
        """

        with connection.cursor() as cursor:
            cursor.execute(query)
            rows = cursor.fetchall()
    finally:
        connection.close()

    data = pd.DataFrame(rows)
    if data.empty:
        return pd.DataFrame(columns=DISPLAY_COLUMNS)

    data["HARI & TANGGAL"] = pd.to_datetime(data["HARI & TANGGAL"], errors="coerce")
    return data.rename(
        columns={
            "HARI & TANGGAL": "Waktu",
            "NODE": "Node",
            "SUHU": "Suhu",
            "TDS": "TDS",
            "PH": "pH",
            "THROUGHPUT": "Throughput",
            "PACKET_LOSS": "Packet Loss",
            "LATENCY_DELAY": "Latency (Delay)",
            "JITTER": "Jitter",
            "BANDWIDTH": "Bandwidth",
        }
    )

def get_card_color(param, value):
    hijau = "rgba(16, 185, 129, 0.15)"  # Normal (Green)
    kuning = "rgba(245, 158, 11, 0.15)" # Kurang (Yellow)
    merah = "rgba(239, 68, 68, 0.15)"   # Melebihi (Red)
    
    if param == "Suhu":
        if value < 27: return kuning
        elif value > 31: return merah
        else: return hijau
    elif param == "pH":
        if value < 7.0: return kuning
        elif value > 8.5: return merah
        else: return hijau
    elif param == "TDS":
        if value <= 450: return hijau
        else: return merah
    
    return "rgba(255, 255, 255, 0.9)"


st.markdown(
    """
    <div class="page-header">
        <h1>Dashboard Monitoring Tambak Rumput Laut</h1>
        <p>Tampilan histori data sensor dan QoS MQTT yang terhubung ke database MySQL.</p>
    </div>
    """,
    unsafe_allow_html=True,
)


try:
    history = load_sensor_history()
except Exception as error:
    st.error("Gagal terhubung ke database SQL.")
    st.info("Pastikan MySQL di XAMPP aktif dan database `tambak_monitoring` berisi tabel `monitoring_air`.")
    st.code(str(error))
    st.stop()


if history.empty:
    st.warning("Belum ada data histori sensor di database. Struktur tabel tetap ditampilkan.")


with st.sidebar:
    st.title("Dashboard")
    st.markdown(
        """
        <div class="sidebar-note">
            Menu ini digunakan untuk menyaring dan mengatur tampilan tabel histori sensor.
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.header("Filter Data")

    node_list = sorted(history["Node"].dropna().unique().tolist()) if "Node" in history else []
    selected_nodes = st.multiselect("Node", node_list, default=node_list)

    date_values = history["Waktu"].dropna() if "Waktu" in history else pd.Series(dtype="datetime64[ns]")
    if date_values.empty:
        selected_range = None
        st.date_input("Rentang tanggal", value=None, disabled=True)
    else:
        selected_range = st.date_input(
            "Rentang tanggal",
            value=(date_values.min().date(), date_values.max().date()),
        )

    keyword = st.text_input("Cari node atau nilai")
    row_limit = st.slider("Jumlah baris", 10, 2000, 100, step=10)

    if st.button("Refresh Data", use_container_width=True):
        st.cache_data.clear()
        st.rerun()


filtered = history.copy()

if selected_nodes and "Node" in filtered:
    filtered = filtered[filtered["Node"].isin(selected_nodes)]

if selected_range and isinstance(selected_range, tuple) and len(selected_range) == 2 and "Waktu" in filtered:
    start_date, end_date = selected_range
    filtered = filtered[
        (filtered["Waktu"].dt.date >= start_date)
        & (filtered["Waktu"].dt.date <= end_date)
    ]

if keyword:
    keyword_lower = keyword.lower()
    filtered = filtered[
        filtered.astype(str)
        .apply(lambda row: row.str.lower().str.contains(keyword_lower, regex=False).any(), axis=1)
    ]


total_rows = len(filtered)
latest_time = filtered["Waktu"].max() if total_rows else None
first_time = filtered["Waktu"].min() if total_rows else None

col1, col2, col3 = st.columns(3)
col1.metric("Total Data Ditampilkan", f"{total_rows:,}")
col2.metric("Data Terbaru", latest_time.strftime("%d/%m/%Y %H:%M:%S") if pd.notna(latest_time) else "-")
col3.metric("Data Terlama", first_time.strftime("%d/%m/%Y %H:%M:%S") if pd.notna(first_time) else "-")

st.subheader("Hasil Sensor Terbaru")

if filtered.empty:
    st.info("Belum ada data sensor untuk ditampilkan.")
else:
    latest_sensor_data = (
        filtered.sort_values("Waktu", ascending=False)
        .drop_duplicates(subset=["Node"], keep="first")
        .sort_values("Node")
    )

    for _, row in latest_sensor_data.iterrows():
        st.markdown(f"### {row['Node']}")
        sensor_col1, sensor_col2, sensor_col3 = st.columns(3)
        
        c_suhu = get_card_color("Suhu", row['Suhu'])
        sensor_col1.markdown(f"""
        <div class="dynamic-metric-card" style="background-color: {c_suhu};">
            <div class="label">Suhu</div>
            <div class="value">{row['Suhu']:.1f} C</div>
        </div>
        """, unsafe_allow_html=True)
        
        c_tds = get_card_color("TDS", row['TDS'])
        sensor_col2.markdown(f"""
        <div class="dynamic-metric-card" style="background-color: {c_tds};">
            <div class="label">TDS</div>
            <div class="value">{row['TDS']:.1f} ppm</div>
        </div>
        """, unsafe_allow_html=True)
        
        c_ph = get_card_color("pH", row['pH'])
        sensor_col3.markdown(f"""
        <div class="dynamic-metric-card" style="background-color: {c_ph};">
            <div class="label">pH</div>
            <div class="value">{row['pH']:.2f}</div>
        </div>
        """, unsafe_allow_html=True)

st.subheader("Histori Data Sensor")

table_data = filtered.reindex(columns=DISPLAY_COLUMNS).head(row_limit)
st.dataframe(
    table_data,
    use_container_width=True,
    hide_index=True,
    column_config={
        "Waktu": st.column_config.DatetimeColumn("Waktu", format="DD/MM/YYYY HH:mm:ss"),
        "Suhu": st.column_config.NumberColumn("Suhu", format="%.1f C"),
        "TDS": st.column_config.NumberColumn("TDS", format="%.1f ppm"),
        "pH": st.column_config.NumberColumn("pH", format="%.2f"),
        "Throughput": st.column_config.NumberColumn("Throughput", format="%.1f bps"),
        "Packet Loss": st.column_config.NumberColumn("Packet Loss", format="%.1f %%"),
        "Latency (Delay)": st.column_config.NumberColumn("Latency (Delay)", format="%.1f ms"),
        "Jitter": st.column_config.NumberColumn("Jitter", format="%.1f ms"),
        "Bandwidth": st.column_config.NumberColumn("Bandwidth", format="%.1f bps"),
    },
)

csv_file = table_data.to_csv(index=False).encode("utf-8")
st.download_button(
    label="Download Tabel CSV",
    data=csv_file,
    file_name="histori_data_sensor.csv",
    mime="text/csv",
)

# Auto refresh setiap 30 detik
time.sleep(30)
st.rerun()