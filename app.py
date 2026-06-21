import streamlit as st
import pandas as pd
import numpy as np
import joblib
import os
import plotly.express as px
import plotly.graph_objects as go
import warnings

warnings.filterwarnings("ignore")
RANDOM_STATE = 42

st.set_page_config(
    page_title='California Housing · AI Dashboard',
    page_icon='🏠',
    layout='wide',
    initial_sidebar_state='expanded'
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

/* ── PAKSA SEMUA TEKS & JUDUL UTAMA BERWARNA TERANG ── */
html, body, .stApp, .stMarkdown, p, span, label, li, h1, h2, h3, h4, h5, h6, small, caption {
    font-family: 'Inter', sans-serif !important;
    color: #e6edf3 !important;
}

/* ── FIX TEKS INPUT & DROPDOWN AGAR TERLIHAT JELAS ── */
input, select, textarea, .stNumberInput input {
    color: #e6edf3 !important;
    background-color: #0d1117 !important;
    -webkit-text-fill-color: #e6edf3 !important;
    font-weight: 600 !important;
}

/* ── FIX TEKS UTAMA TAB MENU (Mencegah Teks Tab Hilang) ── */
.stTabs button, .stTabs [data-baseweb="tab"] {
    color: #8b949e !important;
}
.stTabs button[aria-selected="true"], .stTabs [aria-selected="true"] * {
    color: #ffffff !important;
    font-weight: 700 !important;
}

/* ── FIX TEKS CAPTION KECIL (Mencegah Teks Keterangan Grafik Hilang) ── */
div[data-testid="stCaptionContainer"], div[data-testid="stCaptionContainer"] *, small {
    color: #8b949e !important;
    -webkit-text-fill-color: #8b949e !important;
}

/* ── FIX TEKS DI DALAM DATAFRAME / TABEL DATA MENTAH ── */
div[data-testid="stDataFrame"] *, table *, th, td {
    color: #e6edf3 !important;
}

/* Angka indikator kecil di bawah garis slider dan bubble slider */
div[data-testid="stSlider"] span, div[data-testid="stThumbValue"], div[class*="stSlider"] p {
    color: #e6edf3 !important;
    font-weight: 500 !important;
}

/* ── Main App Background ── */
.stApp {
    background: #0a0e1a;
    background-image: radial-gradient(ellipse at 20% 20%, rgba(88,166,255,0.06) 0%, transparent 50%),
                      radial-gradient(ellipse at 80% 80%, rgba(63,185,80,0.05) 0%, transparent 50%);
}

/* ── Sidebar Style Customization ── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0d1117 0%, #0a0e1a 100%) !important;
    border-right: 1px solid rgba(88,166,255,0.15) !important;
    box-shadow: 4px 0 24px rgba(0,0,0,0.5);
}
[data-testid="stSidebar"] * { color: #c9d1d9 !important; }

/* ── Sidebar Logo Area ── */
.sidebar-logo {
    text-align: center;
    padding: 24px 16px 16px;
    background: linear-gradient(135deg, rgba(88,166,255,0.08), rgba(63,185,80,0.05));
    border-radius: 12px;
    border: 1px solid rgba(88,166,255,0.12);
    margin-bottom: 20px;
}
.sidebar-logo h3 {
    background: linear-gradient(135deg, #58a6ff, #3fb950);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    font-size: 1.15rem;
    font-weight: 700;
    margin: 0 0 4px 0;
}
.sidebar-logo .badge {
    display: inline-block;
    background: rgba(88,166,255,0.1);
    border: 1px solid rgba(88,166,255,0.2);
    color: #58a6ff !important;
    font-size: 0.68rem;
    font-weight: 500;
    padding: 2px 10px;
    border-radius: 20px;
    letter-spacing: 0.05em;
}

/* ── Team Card ── */
.team-card {
    background: linear-gradient(135deg, rgba(33,38,45,0.8), rgba(13,17,23,0.8));
    border: 1px solid rgba(48,54,61,0.8);
    border-radius: 10px;
    padding: 14px;
    margin-top: 20px;
}
.team-card .team-title {
    font-size: 0.72rem;
    font-weight: 600;
    color: #58a6ff !important;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    margin-bottom: 10px;
}
.team-card .member {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 5px 0;
    border-bottom: 1px solid rgba(48,54,61,0.5);
    font-size: 0.78rem;
    color: #8b949e !important;
}
.team-card .member .avatar {
    width: 22px; height: 22px;
    background: linear-gradient(135deg, #58a6ff, #3fb950);
    border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 0.6rem; font-weight: 700; color: #0d1117 !important;
    flex-shrink: 0;
}

/* ── KPI & Static Overview Cards ── */
.kpi-card, .static-overview-card {
    background: linear-gradient(135deg, #161b22, #1c2128);
    border: 1px solid rgba(48,54,61,0.8);
    border-radius: 14px;
    padding: 20px 18px;
    position: relative;
    overflow: hidden;
    margin-bottom: 16px;
}
.kpi-card::before, .static-overview-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    background: linear-gradient(90deg, #58a6ff, #3fb950);
    border-radius: 14px 14px 0 0;
}
.kpi-card .kpi-icon { font-size: 1.6rem; margin-bottom: 6px; text-align: center; }
.kpi-card .kpi-label { font-size: 0.72rem; color: #8b949e !important; text-transform: uppercase; letter-spacing: 0.06em; margin-bottom: 6px; text-align: center; }
.kpi-card .kpi-value { font-size: 1.6rem; font-weight: 700; color: #e6edf3 !important; text-align: center; }
.kpi-card .kpi-sub   { font-size: 0.7rem; color: #58a6ff !important; margin-top: 4px; text-align: center; }

.static-overview-card h4 {
    margin-top: 0 !important;
    color: #58a6ff !important;
    font-weight: 700 !important;
    font-size: 1.05rem !important;
}

/* ── Result Cards ── */
.result-card {
    background: linear-gradient(135deg, #161b22, #1c2128);
    border: 1px solid rgba(48,54,61,0.8);
    border-radius: 14px;
    padding: 28px 24px;
    text-align: center;
    margin-bottom: 16px;
}
.result-card.green { border-top: 3px solid #3fb950; box-shadow: 0 4px 32px rgba(63,185,80,0.12); }
.result-card.red   { border-top: 3px solid #f85149; box-shadow: 0 4px 32px rgba(248,81,73,0.12); }
.result-card.purple { border-top: 3px solid #d2a8ff; box-shadow: 0 4px 32px rgba(210,168,255,0.12); }
.result-card.blue  { border-top: 3px solid #58a6ff; box-shadow: 0 4px 32px rgba(88,166,255,0.12); }

/* ── Section Tag & Info Banner ── */
.section-tag {
    display: inline-flex;
    background: rgba(88,166,255,0.1);
    border: 1px solid rgba(88,166,255,0.2);
    color: #58a6ff !important;
    font-size: 0.72rem;
    font-weight: 600;
    padding: 4px 12px;
    border-radius: 20px;
    text-transform: uppercase;
    margin-bottom: 8px;
}
.info-banner {
    background: linear-gradient(135deg, rgba(88,166,255,0.08), rgba(63,185,80,0.05));
    border: 1px solid rgba(88,166,255,0.15);
    border-radius: 10px;
    padding: 14px 18px;
    margin-bottom: 16px;
    font-size: 0.87rem;
}
.input-section-label {
    font-size: 0.72rem;
    font-weight: 600;
    color: #58a6ff !important;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-bottom: 10px;
    padding-bottom: 6px;
    border-bottom: 1px solid rgba(88,166,255,0.2);
}
</style>
""", unsafe_allow_html=True)

PAPER_BG = '#161b22'
PLOT_BG  = '#0d1117'

def dark_fig(fig, title=''):
    fig.update_layout(
        template='plotly_dark',
        paper_bgcolor=PAPER_BG,
        plot_bgcolor=PLOT_BG,
        font=dict(family='Inter', color='#c9d1d9', size=12),
        title=dict(text=title, font=dict(size=15, color='#79c0ff'), x=0),
        margin=dict(l=40, r=20, t=50, b=40),
        xaxis=dict(gridcolor='#21262d', zerolinecolor='#30363d'),
        yaxis=dict(gridcolor='#21262d', zerolinecolor='#30363d'),
        legend=dict(bgcolor='rgba(22,27,34,0.8)', bordercolor='#30363d', borderwidth=1)
    )
    return fig

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

@st.cache_resource
def load_assets():
    d = os.path.join(BASE_DIR, 'models')
    assets = {}
    try:
        assets['regressor']       = joblib.load(os.path.join(d, 'best_regressor.joblib'))
        assets['classifier']      = joblib.load(os.path.join(d, 'best_classifier.joblib'))
        assets['kmeans']          = joblib.load(os.path.join(d, 'kmeans_model.joblib'))
        assets['scaler_clust']    = joblib.load(os.path.join(d, 'scaler_clust.joblib'))
        assets['median_bedrooms'] = joblib.load(os.path.join(d, 'median_bedrooms.joblib'))
        assets['feature_cols']    = joblib.load(os.path.join(d, 'feature_cols.joblib'))
    except Exception as e:
        st.error(f'Gagal memuat model: {e}')
    return assets

@st.cache_data
def load_data():
    csv_path = os.path.join(BASE_DIR, 'housing.csv')
    return pd.read_csv(csv_path)

assets = load_assets()

st.sidebar.markdown("""
<div class='sidebar-logo'>
    <span class='logo-icon'>🏠</span>
    <h3>CA Housing AI</h3>
    <span class='badge'>✦ CRISP-DM &nbsp;·&nbsp; ML Dashboard</span>
</div>
""", unsafe_allow_html=True)

page = st.sidebar.radio('', [
    '📌  Overview',
    '📊  Eksplorasi Data',
    '🔬  Evaluasi & Performa',
    '📈  Prediksi Harga',
    '🏷️  Klasifikasi Rumah',
    '🗺️  Segmentasi Wilayah',
], label_visibility='collapsed')

st.sidebar.markdown("""
<div class='team-card'>
    <div class='team-title'>&#128100; Kelompok 5</div>
    <div class='member'><div class='avatar'>AS</div> Alya Salma Khoerunnisaa</div>
    <div class='member'><div class='avatar'>MC</div> Maurellio C. Yonathan</div>
    <div class='member'><div class='avatar'>JC</div> Jazzkord Cmajor Dahring</div>
    <div class='member'><div class='avatar'>CN</div> Cantika Nurul Fitri</div>
</div>
""", unsafe_allow_html=True)

def preprocess_input(d):
    df = pd.DataFrame([d])
    if df['total_bedrooms'].values[0] == 0:
        df['total_bedrooms'] = assets['median_bedrooms']

    df['rooms_per_household']      = df['total_rooms']    / df['households']
    df['bedrooms_per_room']        = df['total_bedrooms'] / df['total_rooms']
    df['population_per_household'] = df['population']     / df['households']

    lat, lon = df['latitude'].values[0], df['longitude'].values[0]

    clust_features = ['longitude', 'latitude', 'median_income', 'housing_median_age']
    X_clust_raw = df[clust_features]
    X_clust_scaled = assets['scaler_clust'].transform(X_clust_raw)
    df['cluster'] = assets['kmeans'].predict(X_clust_scaled)[0]

    enc = pd.get_dummies(df, columns=['ocean_proximity'])
    enc.columns = enc.columns.str.replace('ocean_proximity_', 'ocean_')

    feat = assets['feature_cols']
    for c in feat:
        if c not in enc.columns:
            enc[c] = 0

    return enc[feat], lat, lon

def explain_cluster(cid):
    info = {
        0: ('🏡 Perkotaan Menengah', '#58a6ff',
            'Area suburban dengan kepadatan sedang. Harga rumah berada di kisaran moderat '
            'dan biasanya dihuni oleh keluarga kelas menengah yang bekerja di kota.'),
        1: ('🏢 Pusat Kota / Padat', '#d2a8ff',
            'Area urban yang sangat padat. Banyak apartemen dan hunian vertikal. '
            'Mobilitas tinggi dengan akses ke transportasi publik.'),
        2: ('🏝️ Eksklusif / Pesisir', '#ffa657',
            'Area elit dekat pantai California. Properti di sini memiliki harga tertinggi '
            'yang didorong oleh pemandangan laut dan lingkungan premium.'),
        3: ('🏜️ Pedalaman / Terjangkau', '#3fb950',
            'Area inland yang berjarak cukup jauh dari pesisir. Harga properti jauh lebih '
            'terjangkau dibanding area coastal.'),
        4: ('🏘️ Pemukiman Tua', '#79c0ff',
            'Area dengan rata-rata usia bangunan yang tinggi. Komunitas mapan dengan '
            'karakter neighborhood yang kuat.'),
    }
    label, color, desc = info.get(cid, (f'Klaster {cid}', '#8b949e', 'Wilayah dengan karakteristik campuran.'))
    return label, color, desc

def render_input_form(key_prefix=''):
    with st.container():
        st.markdown("<div class='info-banner' style='margin-bottom:20px; font-weight:600;'>⚙️ Masukkan Karakteristik Properti Di Bawah Ini:</div>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("<div class='input-section-label'>📍 Lokasi</div>", unsafe_allow_html=True)
            longitude = st.number_input('Longitude', min_value=-125.0, max_value=-114.0, value=-122.23, step=0.01, key=f'{key_prefix}lon')
            latitude  = st.number_input('Latitude',  min_value=32.0,   max_value=42.0,   value=37.88,  step=0.01, key=f'{key_prefix}lat')
            ocean_proximity = st.selectbox('Kedekatan Laut', ['<1H OCEAN','INLAND','ISLAND','NEAR BAY','NEAR OCEAN'], index=3, key=f'{key_prefix}ocean')
        with col2:
            st.markdown("<div class='input-section-label'>🏗️ Bangunan</div>", unsafe_allow_html=True)
            housing_median_age = st.slider('Umur Rumah (Tahun)', 1, 100, 41, key=f'{key_prefix}age')
            total_rooms    = st.number_input('Total Ruangan',     min_value=1, max_value=50000, value=880, step=10, key=f'{key_prefix}rooms')
            total_bedrooms = st.number_input('Total Kamar Tidur', min_value=1, max_value=10000, value=129, step=5,  key=f'{key_prefix}beds')
        with col3:
            st.markdown("<div class='input-section-label'>👥 Demografi</div>", unsafe_allow_html=True)
            population    = st.number_input('Populasi',         min_value=1, max_value=100000, value=322, step=10, key=f'{key_prefix}pop')
            households    = st.number_input('Jumlah Keluarga',  min_value=1, max_value=50000,  value=126, step=5,  key=f'{key_prefix}hh')
            median_income = st.slider('Median Pendapatan (×$10k)', 0.0, 15.0, 8.32, step=0.1, key=f'{key_prefix}inc')

        errors = []
        if total_bedrooms > total_rooms:
            errors.append('⚠️ Kamar tidur tidak boleh lebih banyak dari total ruangan.')
        if households > population:
            errors.append('⚠️ Jumlah keluarga tidak boleh melebihi populasi.')
        for err in errors:
            st.warning(err)

    return {
        'longitude': longitude, 'latitude': latitude,
        'housing_median_age': housing_median_age,
        'total_rooms': total_rooms, 'total_bedrooms': total_bedrooms,
        'population': population, 'households': households,
        'median_income': median_income, 'ocean_proximity': ocean_proximity
    }, len(errors) == 0

# PAGE: OVERVIEW
if page == '📌  Overview':
    st.markdown("<div class='section-tag'>🏠 Dashboard Utama</div>", unsafe_allow_html=True)
    st.title('California Housing · AI Dashboard')
    st.markdown("<div class='info-banner'>Proyek sistem cerdas ini disusun mengikuti panduan standar industri <b>6 Tahap Metodologi CRISP-DM</b>. Seluruh dokumentasi sub-fitur pengerjaan dipaparkan secara langsung di bawah ini.</div>", unsafe_allow_html=True)

    df = load_data()
    c1, c2, c3, c4 = st.columns(4)
    kpis = [
        (c1, '💰', 'Rata-rata Harga', f"${df['median_house_value'].mean():,.0f}", 'USD'),
        (c2, '🏠', 'Total Properti',  f"{len(df):,}",                              'data entries'),
        (c3, '📅', 'Umur Rata-rata',  f"{df['housing_median_age'].mean():.0f} Thn", 'housing age'),
        (c4, '💵', 'Median Pendapatan', f"{df['median_income'].mean():.2f}",        '×$10,000 / yr'),
    ]
    for col, icon, label, val, sub in kpis:
        with col:
            st.markdown(f"<div class='kpi-card'><div class='kpi-icon'>{icon}</div><div class='kpi-label'>{label}</div><div class='kpi-value'>{val}</div><div class='kpi-sub'>{sub}</div></div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    lcol, rcol = st.columns([1.4, 1])

    with lcol:
        st.markdown('### 🧭 Struktur Pengerjaan Siklus CRISP-DM')

        st.markdown("""
        <div class='static-overview-card'>
            <h4>💼 1. Business Understanding — Rumusan Masalah & Objektif</h4>
            <p>• <b>Tujuan Utama Bisnis:</b> Membantu investor dan pengembang real estat memproyeksikan harga rumah secara akurat di California.<br>
            • <b>Sub-Fitur:</b> Merumuskan batasan zonasi daerah premium vs ekonomis guna meminimalkan risiko kerugian finansial salah investasi.</p>
        </div>
        <div class='static-overview-card'>
            <h4>📊 2. Data Understanding — Pengenalan & Eksplorasi Data</h4>
            <p>• <b>Karakteristik Dataset:</b> Mengolah data sensus perumahan California sebesar <b>20.640 baris</b>.<br>
            • <b>Sub-Fitur:</b> Visualisasi spasial interaktif titik koordinat peta (Mapbox), analisis histogram kemiringan data (Skewness), dan matriks korelasi antar fitur.</p>
        </div>
        <div class='static-overview-card'>
            <h4>🛠️ 3. Data Preparation — Pembersihan & Rekayasa Fitur</h4>
            <p>• <b>Metode Pemrosesan:</b> Median Imputation pada kolom kosong, pembuatan 3 fitur rasio baru, penyeimbangan data kategori via One-Hot Encoding, serta segmentasi wilayah Spasial-Ekonomi menggunakan algoritma <b>K-Means (K=5)</b>.</p>
        </div>
        <div class='static-overview-card'>
            <h4>🤖 4. Modeling — Turnamen Algoritma & Tuning</h4>
            <p>• <b>Eksperimen AI:</b> Membandingkan 6 arsitektur algoritma (Linear Regression, Ridge, Lasso, RandomForest, GradientBoosting, HistGradientBoosting). Optimalisasi performa menggunakan <b>GridSearchCV</b> dan proteksi data via Pipeline.</p>
        </div>
        <div class='static-overview-card'>
            <h4>🔬 5. Evaluation — Validasi Saintifik & Pengujian Ketat</h4>
            <p>• <b>Metrik Ukur:</b> K-Fold Cross Validation untuk keamanan training, pengujian data baru (Test Set) via RMSE & R² (Regresi) serta F1-Score (Klasifikasi), dilengkapi visualisasi Global Permutation Importance.</p>
        </div>
        <div class='static-overview-card'>
            <h4>🚀 6. Deployment — Aplikasi Web Siap Pakai</h4>
            <p>• <b>Sistem Akhir:</b> Ekstraksi berkas otak AI (.joblib), pembuatan mesin inferensi instan, dan penyediaan antarmuka web interaktif ramah pengguna berbasis Streamlit.</p>
        </div>
        """, unsafe_allow_html=True)

    with rcol:
        st.markdown('### 📋 Sekilas Proyek Kelompok 5')
        st.markdown("<div class='info-banner'>Semua tahapan CRISP-DM di samping telah selesai diolah secara matematis. Silakan gunakan menu navigasi sidebar untuk menguji keandalan sistem prediksi!</div>", unsafe_allow_html=True)
        st.image('https://images.unsplash.com/photo-1512917774080-9991f1c4c750?auto=format&fit=crop&w=800&q=80', use_container_width=True)

# PAGE: DATA EXPLORATION
elif page == '📊  Eksplorasi Data':
    st.markdown("<div class='section-tag'>📊 Eksplorasi</div>", unsafe_allow_html=True)
    st.title('Eksplorasi Data Interaktif (EDA)')
    st.markdown("<div class='info-banner'>Semua grafik bersifat <b>interaktif</b> — hover untuk detail, scroll/drag untuk zoom & pan.</div>", unsafe_allow_html=True)

    df = load_data()
    tab1, tab2, tab3, tab4 = st.tabs(['🗺️ Peta Interaktif', '📈 Distribusi & Scatter', '🔥 Heatmap Korelasi', '📋 Dataset'])

    with tab1:
        st.markdown('#### Peta Persebaran Harga Rumah California')
        st.caption('🔵 Warna titik = harga  |  ⚪ Ukuran titik = populasi  |  Hover untuk detail')
        fig = px.scatter_mapbox(
            df, lat='latitude', lon='longitude',
            color='median_house_value', size='population',
            color_continuous_scale='Plasma', size_max=18, zoom=4.5,
            mapbox_style='carto-darkmatter',
            hover_name='ocean_proximity',
            hover_data={'median_house_value': ':$,.0f', 'total_rooms': True,
                        'median_income': ':.2f', 'population': True,
                        'latitude': False, 'longitude': False},
            labels={'median_house_value': 'Harga ($)', 'median_income': 'Pendapatan'}
        )
        fig.update_layout(paper_bgcolor='#0d1117', margin=dict(r=0, t=0, l=0, b=0),
                          coloraxis_colorbar=dict(title='Harga ($)', tickfont=dict(color='#c9d1d9'), bgcolor='#161b22'))
        st.plotly_chart(fig, use_container_width=True)

    with tab2:
        ca, cb = st.columns(2)
        with ca:
            fig2 = px.histogram(df, x='median_house_value', nbins=60, marginal='violin',
                                color_discrete_sequence=['#58a6ff'],
                                labels={'median_house_value': 'Harga ($)'})
            dark_fig(fig2, 'Distribusi Harga Rumah')
            st.plotly_chart(fig2, use_container_width=True)
        with cb:
            fig3 = px.scatter(df.sample(2000, random_state=42),
                              x='median_income', y='median_house_value',
                              color='ocean_proximity', opacity=0.55, size_max=6,
                              labels={'median_income': 'Pendapatan (×$10k)', 'median_house_value': 'Harga ($)', 'ocean_proximity': 'Lokasi'})
            dark_fig(fig3, 'Harga vs Pendapatan Median')
            st.plotly_chart(fig3, use_container_width=True)

        fig4 = px.box(df, x='ocean_proximity', y='median_house_value',
                      color='ocean_proximity',
                      labels={'ocean_proximity': 'Tipe Lokasi', 'median_house_value': 'Harga ($)'},
                      color_discrete_sequence=['#58a6ff','#3fb950','#ffa657','#d2a8ff','#f85149'])
        dark_fig(fig4, 'Distribusi Harga per Tipe Lokasi (Ocean Proximity)')
        st.plotly_chart(fig4, use_container_width=True)

    with tab3:
        num_df = df.select_dtypes(include=[np.number])
        corr   = num_df.corr().round(2)
        fig5   = px.imshow(corr, text_auto=True, aspect='auto', color_continuous_scale='RdBu_r', zmin=-1, zmax=1)
        dark_fig(fig5, 'Matriks Korelasi Fitur')
        fig5.update_traces(textfont=dict(size=11))
        fig5.update_layout(height=500)
        st.plotly_chart(fig5, use_container_width=True)

    with tab4:
        st.markdown('#### Cuplikan Dataset')
        st.dataframe(df.head(20), use_container_width=True)
        st.markdown('#### Statistik Deskriptif')
        st.dataframe(df.describe().round(2), use_container_width=True)

# PAGE: EVALUATION
elif page == '🔬  Evaluasi & Performa':
    st.markdown("<div class='section-tag'>🔬 Evaluation</div>", unsafe_allow_html=True)
    st.title('Evaluasi Sains & Performa Model AI')
    tab_eval1, tab_eval2, tab_eval3 = st.tabs(['📊 Perbandingan Kandidat', '🏆 Rapor Metrik Final', '🔮 Feature Importance'])

    with tab_eval1:
        st.markdown("### ⚔️ Hasil Turnamen Model (Cross-Validation)")
        col_ev1, col_ev2 = st.columns(2)
        with col_ev1:
            st.markdown("#### 1. Performa Regresi (CV RMSE)")
            reg_perf_data = pd.DataFrame({
                'Model Kandidat': ['HistGradientBoosting (Winner)', 'RandomForest', 'GradientBoosting', 'Ridge', 'Lasso', 'LinearRegression'],
                'CV RMSE': [42105.99, 45257.75, 48021.81, 60101.59, 60102.45, 60102.64]
            })
            st.dataframe(reg_perf_data, use_container_width=True, hide_index=True)
            fig_reg_comp = px.bar(reg_perf_data, x='CV RMSE', y='Model Kandidat', orientation='h', color='CV RMSE', color_continuous_scale='Blues_r')
            dark_fig(fig_reg_comp); fig_reg_comp.update_layout(coloraxis_showscale=False); st.plotly_chart(fig_reg_comp, use_container_width=True)
        with col_ev2:
            st.markdown("#### 2. Performa Klasifikasi (CV F1-Score)")
            clf_perf_data = pd.DataFrame({
                'Model Kandidat': ['HistGradientBoosting (Winner)', 'RandomForest', 'GradientBoosting', 'SVC', 'KNN', 'LogisticRegression'],
                'CV F1-Score': [0.8976, 0.8865, 0.8797, 0.8566, 0.8407, 0.8347]
            })
            st.dataframe(clf_perf_data, use_container_width=True, hide_index=True)
            fig_clf_comp = px.bar(clf_perf_data, x='CV F1-Score', y='Model Kandidat', orientation='h', color='CV F1-Score', color_continuous_scale='Greens')
            dark_fig(fig_clf_comp); fig_clf_comp.update_layout(coloraxis_showscale=False); st.plotly_chart(fig_clf_comp, use_container_width=True)

    with tab_eval2:
        st.markdown("### 🏆 Capaian Akhir Data Uji (Test Set)")
        col_m1, col_m2 = st.columns(2)
        with col_m1:
            st.markdown("<div class='result-card blue'><h4>📈 Rapor Regresi</h4></div>", unsafe_allow_html=True)
            st.dataframe(pd.DataFrame({
                'Metrik': ['RMSE', 'MAE', 'R² Score'],
                'Nilai': ['$41,822.62', '$28,014.14', '0.8176 (81.76%)']
            }), use_container_width=True, hide_index=True)
        with col_m2:
            st.markdown("<div class='result-card purple'><h4>🏷️ Rapor Klasifikasi</h4></div>", unsafe_allow_html=True)
            st.dataframe(pd.DataFrame({
                'Metrik': ['Accuracy', 'F1-Score', 'Precision', 'Recall'],
                'Nilai': ['89.26%', '89.15%', '89.00%', '89.00%']
            }), use_container_width=True, hide_index=True)

    with tab_eval3:
        st.markdown("### 🔮 Penentu Keputusan Model (Global Permutation Importance)")
        feat_imp_data = pd.DataFrame({
            'Karakteristik Fitur': ['Median Income', 'Ocean Proximity INLAND', 'Longitude', 'Latitude', 'Bedrooms per Room', 'Rooms per Household', 'Housing Median Age'],
            'Influence Score': [0.654, 0.212, 0.145, 0.128, 0.065, 0.043, 0.021]
        }).sort_values(by='Influence Score', ascending=True)
        fig_feat = px.bar(feat_imp_data, x='Influence Score', y='Karakteristik Fitur', orientation='h', color='Influence Score', color_continuous_scale='Viridis')
        dark_fig(fig_feat); fig_feat.update_layout(coloraxis_showscale=False); st.plotly_chart(fig_feat, use_container_width=True)

# PAGE: REGRESSION PREDICTION
elif page == '📈  Prediksi Harga':
    st.markdown("<div class='section-tag'>📈 Regresi</div>", unsafe_allow_html=True)
    st.title('Prediksi Harga Rumah (Regresi Kontinu)')

    input_dict, valid = render_input_form(key_prefix='reg_')

    if st.button('🚀  Prediksi Harga Sekarang', use_container_width=True):
        if valid and assets:
            with st.spinner('Memproses...'):
                df_prep, lat, lon = preprocess_input(input_dict)
                pred = assets['regressor'].predict(df_prep)[0]

            st.balloons()
            r1, r2 = st.columns([1.2, 1])
            with r1:
                THRESHOLD_VAL = 179700
                is_mahal = pred > THRESHOLD_VAL
                badge_color = '#f85149' if is_mahal else '#3fb950'
                badge_label = 'MAHAL' if is_mahal else 'TERJANGKAU / MURAH'

                st.markdown(f"""
                <div class='result-card blue'>
                    <div style='font-size:0.75rem; color:#8b949e; text-transform:uppercase;'>Estimasi Nilai Properti</div>
                    <div style='font-size:3rem; font-weight:800; color:#58a6ff; margin:8px 0;'>${pred:,.0f}</div>
                    <div style='margin-top:14px;'>
                        <span style='padding:6px 22px; border-radius:20px; border:1.5px solid {badge_color}; color:{badge_color}; font-weight:700;'>
                            {badge_label}
                        </span>
                    </div>
                    <div style='font-size:0.76rem; color:#8b949e; margin-top:10px;'>Batas Ambang Median Data: $179,700</div>
                </div>
                """, unsafe_allow_html=True)
            with r2:
                st.map(pd.DataFrame({'lat': [lat], 'lon': [lon]}), zoom=12)

# PAGE: CLASSIFICATION
elif page == '🏷️  Klasifikasi Rumah':
    st.markdown("<div class='section-tag'>🏷️ Klasifikasi</div>", unsafe_allow_html=True)
    st.title('Klasifikasi Tingkat Nilai Rumah')
    st.markdown("<div class='info-banner'>Model <b>Klasifikasi</b> memproyeksikan status harga rumah ke dalam kategori <b>MAHAL</b> atau <b>MURAH</b> berdasarkan batas nilai tengah data latih asli ($179,700).</div>", unsafe_allow_html=True)

    input_dict, valid = render_input_form(key_prefix='cls_')

    if st.button('🔍  Klasifikasi Sekarang', use_container_width=True):
        if valid and assets:
            with st.spinner('Mengklasifikasikan...'):
                df_prep, lat, lon = preprocess_input(input_dict)
                pred_reg = assets['regressor'].predict(df_prep)[0]
                pred_cls = assets['classifier'].predict(df_prep)[0]

            st.markdown('---')
            r1, r2 = st.columns([1.2, 1])
            with r1:
                if pred_cls == 1:
                    st.markdown("""
                    <div class='result-card red'>
                        <div style='font-size:3.5rem'>💎</div>
                        <div style='font-size:2rem; font-weight:800; color:#f85149'>KATEGORI: MAHAL</div>
                        <div style='font-size:0.85rem; color:#8b949e; margin-top:4px;'>Properti diproyeksikan berada di atas batas kelas reguler</div>
                    </div>
                    """, unsafe_allow_html=True)
                    st.error(f"**Analisis Otak AI (Klasifikasi):**\n\nModel menetapkan rumah ini masuk kelompok **MAHAL** karena memiliki kombinasi karakteristik spasial-ekonomi premium. Nilai taksiran regresi fisik properti berada di kisaran **${pred_reg:,.0f}** (Garis tengah acuan dataset: $179,700).")
                else:
                    st.markdown("""
                    <div class='result-card green'>
                        <div style='font-size:3.5rem'>🏠</div>
                        <div style='font-size:2rem; font-weight:800; color:#3fb950'>KATEGORI: MURAH / TERJANGKAU</div>
                        <div style='font-size:0.85rem; color:#8b949e; margin-top:4px;'>Properti diproyeksikan berada di bawah batas kelas reguler</div>
                    </div>
                    """, unsafe_allow_html=True)
                    st.success(f"**Analisis Otak AI (Klasifikasi):**\n\nModel menetapkan rumah ini masuk kelompok **MURAH / TERJANGKAU** karena kepadatan dan spesifikasinya yang ramah anggaran. Nilai taksiran regresi fisik properti berada di kisaran **${pred_reg:,.0f}** (Garis tengah acuan dataset: $179,700).")
            with r2:
                st.map(pd.DataFrame({'lat': [lat], 'lon': [lon]}), zoom=12)

# PAGE: CLUSTERING
elif page == '🗺️  Segmentasi Wilayah':
    st.markdown("<div class='section-tag'>🗺️ Klastering</div>", unsafe_allow_html=True)
    st.title('Segmentasi Wilayah K-Means')

    input_dict, valid = render_input_form(key_prefix='clu_')

    if st.button('🔬  Analisis Klaster Sekarang', use_container_width=True):
        if valid and assets:
            with st.spinner('Menghitung klaster...'):
                df_prep, lat, lon = preprocess_input(input_dict)
                cf      = assets['scaler_clust'].feature_names_in_
                X_clust = assets['scaler_clust'].transform(df_prep[cf])
                cid     = int(assets['kmeans'].predict(X_clust)[0])
                label, color, desc = explain_cluster(cid)

            st.markdown('---')
            r1, r2 = st.columns([1.2, 1])
            with r1:
                st.markdown(f"""
                <div class='result-card purple'>
                    <div style='font-size:1.2rem; color:#8b949e;'>Zonasi Terdeteksi</div>
                    <div style='font-size:2.2rem; font-weight:700; color:{color}; margin:10px 0;'>{label}</div>
                    <div style='font-size:0.85rem; color:#8b949e;'>Hasil Segmentasi Klaster K-Means #{cid}</div>
                </div>
                """, unsafe_allow_html=True)
                st.info(f"🔎 **Profil Wilayah:** {desc}")
            with r2:
                st.map(pd.DataFrame({'lat': [lat], 'lon': [lon]}), zoom=12)
