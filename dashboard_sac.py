import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from supabase import create_client
from datetime import datetime, timedelta
import numpy as np
import time

# Configuración de la página
st.set_page_config(
    page_title="Dashboard SAC - Métricas de Conversaciones",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Credenciales de Supabase
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

# Estilos CSS personalizados mejorados
st.markdown("""
    <style>
    /* Importar fuente moderna */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Estilos generales */
    .main {
        padding: 0rem 1rem;
        font-family: 'Inter', sans-serif;
    }
    
    /* Header principal con gradiente */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
    }
    
    .main-header h1 {
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
    }
    
    .main-header p {
        font-size: 1.1rem;
        margin: 0.5rem 0 0 0;
        opacity: 0.95;
    }
    
    /* Métricas con diseño moderno */
    [data-testid="stMetricValue"] {
        font-size: 2rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    [data-testid="stMetricLabel"] {
        font-size: 0.9rem;
        font-weight: 600;
        color: #4a5568;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    [data-testid="stMetricDelta"] {
        font-size: 0.85rem;
    }
    
    div[data-testid="metric-container"] {
        background: linear-gradient(135deg, #ffffff 0%, #f7fafc 100%);
        padding: 1.5rem;
        border-radius: 12px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05), 0 1px 3px rgba(0, 0, 0, 0.1);
        transition: all 0.3s ease;
    }
    
    div[data-testid="metric-container"]:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 20px rgba(102, 126, 234, 0.15), 0 6px 6px rgba(0, 0, 0, 0.1);
        border-color: #667eea;
    }
    
    /* Headers de secciones */
    .section-header {
        background: linear-gradient(135deg, #f7fafc 0%, #edf2f7 100%);
        padding: 1rem 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #667eea;
        margin: 2rem 0 1rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    
    .section-header h2 {
        color: #2d3748;
        font-size: 1.5rem;
        font-weight: 700;
        margin: 0;
    }
    
    /* Sidebar mejorado */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #f7fafc 0%, #edf2f7 100%);
        border-right: 1px solid #e2e8f0;
    }
    
    [data-testid="stSidebar"] h2 {
        color: #2d3748;
        font-weight: 700;
    }
    
    [data-testid="stSidebar"] h3 {
        color: #4a5568;
        font-weight: 600;
        font-size: 0.9rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-top: 1.5rem;
    }
    
    /* Botones mejorados */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.6rem 1.2rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 6px rgba(102, 126, 234, 0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(102, 126, 234, 0.4);
    }
    
    /* Selectbox mejorado */
    .stSelectbox > div > div {
        border-radius: 8px;
        border: 2px solid #e2e8f0;
        transition: all 0.3s ease;
    }
    
    .stSelectbox > div > div:hover {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
    
    /* Date input mejorado */
    .stDateInput > div > div > input {
        border-radius: 8px;
        border: 2px solid #e2e8f0;
        transition: all 0.3s ease;
    }
    
    .stDateInput > div > div > input:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
    
    /* Expander mejorado */
    .streamlit-expanderHeader {
        background: linear-gradient(135deg, #f7fafc 0%, #edf2f7 100%);
        border-radius: 8px;
        font-weight: 600;
        color: #2d3748;
        border: 1px solid #e2e8f0;
    }
    
    .streamlit-expanderHeader:hover {
        background: linear-gradient(135deg, #edf2f7 0%, #e2e8f0 100%);
        border-color: #667eea;
    }
    
    /* Info boxes */
    .stAlert {
        border-radius: 10px;
        border-left: 4px solid #667eea;
        background: linear-gradient(135deg, #ffffff 0%, #f7fafc 100%);
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    
    /* Dataframe mejorado */
    .dataframe {
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    /* Progress bar */
    .stProgress > div > div {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
    }
    
    /* Tabs mejorados */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #f7fafc;
        padding: 0.5rem;
        border-radius: 10px;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
    
    /* Separadores con estilo */
    hr {
        margin: 2rem 0;
        border: none;
        height: 2px;
        background: linear-gradient(90deg, transparent, #667eea, transparent);
        opacity: 0.3;
    }
    
    /* Animación de carga */
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }
    
    .loading {
        animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
    }
    
    /* Tarjetas de estadísticas */
    .stat-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.07);
        border: 1px solid #e2e8f0;
        transition: all 0.3s ease;
    }
    
    .stat-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 10px 20px rgba(0,0,0,0.1);
    }
    
    /* Footer mejorado */
    .footer {
        text-align: center;
        padding: 2rem;
        background: linear-gradient(135deg, #f7fafc 0%, #edf2f7 100%);
        border-radius: 10px;
        margin-top: 3rem;
        border: 1px solid #e2e8f0;
    }
    
    .footer p {
        color: #718096;
        font-size: 0.9rem;
        margin: 0.5rem 0;
    }
    
    /* Tooltips mejorados */
    .tooltip {
        position: relative;
        display: inline-block;
    }
    
    /* Efectos de hover para gráficos */
    .js-plotly-plot {
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 4px 6px rgba(0,0,0,0.07);
        transition: all 0.3s ease;
    }
    
    .js-plotly-plot:hover {
        box-shadow: 0 10px 20px rgba(0,0,0,0.1);
    }
    </style>
""", unsafe_allow_html=True)

# Tema de colores personalizado para gráficos
COLOR_PALETTE = {
    'primary': '#667eea',
    'secondary': '#764ba2',
    'success': '#10b981',
    'warning': '#f59e0b',
    'danger': '#ef4444',
    'info': '#3b82f6',
    'light': '#f7fafc',
    'dark': '#2d3748',
    'gradient': ['#667eea', '#764ba2', '#f093fb', '#4facfe']
}

# Función para crear gráficos con estilo consistente
def create_plotly_theme(fig, title="", height=400):
    """Aplica tema consistente a los gráficos de Plotly"""
    fig.update_layout(
        title={
            'text': title,
            'font': {'size': 18, 'color': COLOR_PALETTE['dark'], 'family': 'Inter'},
            'x': 0.5,
            'xanchor': 'center'
        },
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font={'family': 'Inter', 'color': COLOR_PALETTE['dark']},
        height=height,
        margin=dict(t=60, l=60, r=40, b=60),
        hovermode='x unified',
        hoverlabel=dict(
            bgcolor="white",
            font_size=12,
            font_family="Inter"
        ),
        xaxis=dict(
            showgrid=True,
            gridwidth=1,
            gridcolor='rgba(0,0,0,0.05)',
            showline=True,
            linewidth=1,
            linecolor='rgba(0,0,0,0.1)'
        ),
        yaxis=dict(
            showgrid=True,
            gridwidth=1,
            gridcolor='rgba(0,0,0,0.05)',
            showline=True,
            linewidth=1,
            linecolor='rgba(0,0,0,0.1)'
        )
    )
    return fig

# Función para cargar datos desde API con paginación
@st.cache_data(ttl=21600)  # 6 horas = 21600 segundos
def load_data():
    """Carga TODOS los datos de Supabase"""
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        all_data = []
        page_size = 5000  # Aumentado para menos requests y carga más rápida
        offset = 0
        
        # Crear barra de progreso
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Obtener el conteo total real
        try:
            count_response = supabase.table('conversation_metrics')\
                .select('id', count='exact')\
                .limit(1)\
                .execute()
            total_count = count_response.count if hasattr(count_response, 'count') else 100000
            status_text.text(f"📊 Total de registros en BD: {total_count:,}")
        except Exception as e:
            st.warning(f"No se pudo obtener el conteo: {str(e)}")
            total_count = 100000  # Estimado conservador
        
        # Paginación usando limit y offset
        iteration = 0
        while True:
            status_text.text(f"⏳ Cargando registros {offset:,} - {offset + page_size:,}... ({len(all_data):,} cargados de ~{total_count:,})")
            
            try:
                response = supabase.table('conversation_metrics')\
                    .select('*')\
                    .limit(page_size)\
                    .offset(offset)\
                    .execute()
                
                if not response.data or len(response.data) == 0:
                    status_text.text(f"✅ No hay más datos. Total cargado: {len(all_data):,}")
                    break
                
                all_data.extend(response.data)
                
                # Actualizar progreso
                if total_count > 0:
                    progress = min(len(all_data) / total_count, 0.99)
                    progress_bar.progress(progress)
                
                # Si obtuvimos menos registros que page_size, llegamos al final
                if len(response.data) < page_size:
                    status_text.text(f"✅ Última página cargada. Total: {len(all_data):,}")
                    break
                
                offset += page_size
                iteration += 1
                
                # Sin delays - cargar lo más rápido posible
                
            except Exception as e:
                st.error(f"❌ Error en offset {offset}: {str(e)}")
                st.warning("Continuando con los datos cargados hasta ahora...")
                break
        
        progress_bar.progress(1.0)
        status_text.text(f"✅ Carga completada: {len(all_data):,} registros")
        time.sleep(1.5)
        progress_bar.empty()
        status_text.empty()
        
        if not all_data:
            st.error("No se cargaron datos")
            return pd.DataFrame()
        
        df = pd.DataFrame(all_data)
        
        # Optimización: Convertir tipos de datos eficientemente
        date_columns = ['first_assignment_at', 'first_human_message_at', 
                       'last_human_message_at', 'first_ai_message_at', 
                       'last_ai_message_at', 'created_at', 'closed_at']
        
        # Conversión en batch más eficiente
        for col in date_columns:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce')
        
        # Convertir booleanos de forma eficiente
        boolean_columns = ['ai_problem_resolved', 'request_solved']
        for col in boolean_columns:
            if col in df.columns:
                df[col] = df[col].apply(lambda x: bool(x) if pd.notna(x) and x is not None else pd.NA)
        
        # Cálculos de métricas usando el closed_at real de Supabase
        df['art_hours'] = (df['closed_at'] - df['first_assignment_at']).dt.total_seconds() / 3600
        df['frt_minutes'] = (df['first_human_message_at'] - df['first_assignment_at']).dt.total_seconds() / 60
        
        # Calcular duración total de la conversación (desde created_at hasta closed_at REAL)
        df['conversation_duration_hours'] = (df['closed_at'] - df['created_at']).dt.total_seconds() / 3600
        
        # Optimización de memoria: convertir a tipos más eficientes
        for col in df.select_dtypes(include=['float64']).columns:
            df[col] = df[col].astype('float32')
        
        for col in df.select_dtypes(include=['int64']).columns:
            if df[col].max() < 2147483647:  # Max int32
                df[col] = df[col].astype('int32')
        
        return df
    except Exception as e:
        st.error(f"Error al cargar datos: {str(e)}")
        import traceback
        st.error(traceback.format_exc())
        return pd.DataFrame()
    
# Función para calcular FCR
def calculate_fcr(_df, fecha_inicio, fecha_fin, window_hours=24, debug=False):
    """Calcula First Contact Resolution.
    Devuelve FCR (float) y, si debug=True, un dict con conteos y muestras.
    """
    df = _df.copy()

    # Normalizar tipos y contact id
    for c in ['created_at', 'closed_at', 'first_assignment_at', 'last_human_message_at']:
        if c in df.columns:
            df[c] = pd.to_datetime(df[c], errors='coerce')

    if 'contact_wa_id' in df.columns:
        df['contact_wa_id'] = df['contact_wa_id'].astype(str).str.strip()
    else:
        # Si no hay contact id, no se puede calcular FCR
        if debug:
            return 0.0, {"error": "no contact_wa_id column"}
        return 0.0

    fecha_inicio_dt = pd.to_datetime(fecha_inicio)
    fecha_fin_dt = pd.to_datetime(fecha_fin) + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)

    # Filter by closed_at in range
    mask = (df['closed_at'] >= fecha_inicio_dt) & (df['closed_at'] <= fecha_fin_dt)
    conversations_in_range = df[mask].copy()

    total = len(conversations_in_range)
    if total == 0:
        if debug:
            return 0.0, {"total": 0}
        return 0.0

    # Ventana
    conversations_in_range['close_time_plus_window'] = conversations_in_range['closed_at'] + pd.Timedelta(hours=window_hours)

    # Data para futuros contactos (right side)
    df_future = df[['contact_wa_id', 'created_at', 'conversation_id']].copy()
    df_future = df_future.rename(columns={
        'created_at': 'created_at_future',
        'conversation_id': 'future_conversation_id'
    })

    # Merge: left = conversations_in_range, right = df_future
    recontacts = conversations_in_range.merge(df_future, on='contact_wa_id', how='left')

    # FILTRO CORRECTO: usar created_at_future (la creación de la posible recontact)
    recontacts = recontacts[
        (recontacts['created_at_future'].notna()) &
        (recontacts['created_at_future'] > recontacts['closed_at']) &
        (recontacts['created_at_future'] <= recontacts['close_time_plus_window']) &
        (recontacts['conversation_id'] != recontacts['future_conversation_id'])
    ]

    # Ahora queremos contar cuántas conversaciones_in_range tuvieron al menos un recontacto.
    # recontacts['conversation_id'] es la conversación original (left).
    unique_recontacts = recontacts['conversation_id'].nunique()

    fcr = (1 - unique_recontacts / total) * 100

    if debug:
        sample = recontacts[[
            'contact_wa_id', 'conversation_id', 'future_conversation_id',
            'closed_at', 'created_at_future', 'close_time_plus_window'
        ]].head(10)
        return fcr, {
            "total": total,
            "unique_recontacts": int(unique_recontacts),
            "recontacts_rows": len(recontacts),
            "sample_recontacts": sample
        }

    return fcr

def calculate_aged_backlog(df_filtered):
    """Calcula distribución de duración de conversaciones"""
    df_closed = df_filtered[df_filtered['conversation_duration_hours'].notna()].copy()
    
    if len(df_closed) == 0:
        return {'6h': 0, '12h': 0, '24h': 0, 'total': 0, 'avg_duration': 0}
    
    backlog_6h = (df_closed['conversation_duration_hours'] >= 6).sum()
    backlog_12h = (df_closed['conversation_duration_hours'] >= 12).sum()
    backlog_24h = (df_closed['conversation_duration_hours'] >= 24).sum()
    total_conversations = len(df_closed)
    avg_duration = df_closed['conversation_duration_hours'].mean()
    
    return {
        '6h': (backlog_6h / total_conversations * 100) if total_conversations > 0 else 0,
        '12h': (backlog_12h / total_conversations * 100) if total_conversations > 0 else 0,
        '24h': (backlog_24h / total_conversations * 100) if total_conversations > 0 else 0,
        'total': total_conversations,
        'avg_duration': avg_duration,
        'count_6h': backlog_6h,
        'count_12h': backlog_12h,
        'count_24h': backlog_24h
    }

# Cargar datos
with st.spinner('🚀 Cargando datos desde Supabase...'):
    df = load_data()

if df.empty:
    st.error("❌ No se pudieron cargar los datos.")
    st.stop()

# Header principal con diseño mejorado
st.markdown(f"""
    <div class='main-header'>
        <h1>📊 Dashboard SAC - Métricas de Conversaciones</h1>
        <p>✅ {len(df):,} conversaciones cargadas | 🔄 Actualizado cada 6 horas | 📅 Datos hasta {(df["closed_at"].max() - timedelta(hours=5)).strftime("%d/%m/%Y %H:%M")}</p>
    </div>
""", unsafe_allow_html=True)

# Sidebar con diseño mejorado
st.sidebar.markdown("## 🔍 Filtros de Análisis")

df_with_dates = df[df['closed_at'].notna()].copy()

if len(df_with_dates) == 0:
    st.error("No hay datos con fechas válidas.")
    st.stop()

min_date = df_with_dates['closed_at'].min().date()
max_date = df_with_dates['closed_at'].max().date()

default_start = max_date - timedelta(days=30)
if default_start < min_date:
    default_start = min_date

st.sidebar.markdown("### 📅 Período de Análisis")

col_date1, col_date2 = st.sidebar.columns(2)

with col_date1:
    fecha_inicio = st.date_input("Desde", value=default_start, min_value=min_date, max_value=max_date, key="fecha_inicio")

with col_date2:
    fecha_fin = st.date_input("Hasta", value=max_date, min_value=min_date, max_value=max_date, key="fecha_fin")

if fecha_inicio > fecha_fin:
    st.sidebar.error("⚠️ La fecha 'Desde' debe ser menor o igual a 'Hasta'")
    st.stop()

dias_seleccionados = (fecha_fin - fecha_inicio).days + 1
st.sidebar.info(f"📊 **{dias_seleccionados}** días seleccionados")

st.sidebar.markdown("---")

# Filtros adicionales con mejor diseño
st.sidebar.markdown("### 👤 Responsable")
responsables = ['Todos'] + sorted(df['responsible_email'].dropna().unique().tolist())
responsable_seleccionado = st.sidebar.selectbox("", responsables, label_visibility="collapsed", key="responsable")

st.sidebar.markdown("### 📋 Cola de Atención")
colas = ['Todas'] + sorted(df['queue_name'].dropna().unique().tolist())
cola_seleccionada = st.sidebar.selectbox("", colas, label_visibility="collapsed", key="cola")

st.sidebar.markdown("### 🏷️ Categoría")
categorias = ['Todas'] + sorted(df['category_name'].dropna().unique().tolist())
categoria_seleccionada = st.sidebar.selectbox("", categorias, label_visibility="collapsed", key="categoria")

st.sidebar.markdown("### ⏱️ Ventana FCR")
fcr_window_options = {
    "12 horas": 12,
    "24 horas": 24,
    "48 horas": 48,
    "7 días": 168
}
fcr_window_label = st.sidebar.selectbox(
    "", 
    list(fcr_window_options.keys()), 
    index=2,  # 48 horas por defecto
    label_visibility="collapsed", 
    key="fcr_window",
    help="Tiempo máximo para considerar un recontacto en el cálculo de FCR"
)
fcr_window_hours = fcr_window_options[fcr_window_label]

st.sidebar.markdown("### 🔄 Transferencias")
transferencias_options = ['Todas', '0', '1', '2', '3', '>3']
transferencias_seleccionadas = st.sidebar.multiselect(
    "",
    transferencias_options,
    default=['Todas'],
    label_visibility="collapsed",
    key="transferencias",
    help="Filtra conversaciones por número de transferencias"
)

st.sidebar.markdown("---")

# Botones de acción
col_btn1, col_btn2 = st.sidebar.columns(2)
with col_btn1:
    if st.button("🔄 Limpiar", use_container_width=True):
        st.rerun()
with col_btn2:
    if st.button("♻️ Refrescar", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

# Información adicional en sidebar
st.sidebar.markdown("---")
st.sidebar.markdown("""
    <div style='padding: 1rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
    border-radius: 10px; color: white; text-align: center;'>
        <p style='margin: 0; font-size: 0.9rem; font-weight: 600;'>💡 Tips</p>
        <p style='margin: 0.5rem 0 0 0; font-size: 0.8rem;'>
            Usa los filtros para analizar períodos específicos y responsables individuales
        </p>
    </div>
""", unsafe_allow_html=True)

# Aplicar filtros
df_filtered = df.copy()

mask = (df_filtered['closed_at'].dt.date >= fecha_inicio) & (df_filtered['closed_at'].dt.date <= fecha_fin)
df_filtered = df_filtered[mask]

if responsable_seleccionado != 'Todos':
    df_filtered = df_filtered[df_filtered['responsible_email'] == responsable_seleccionado]

if cola_seleccionada != 'Todas':
    df_filtered = df_filtered[df_filtered['queue_name'] == cola_seleccionada]

if categoria_seleccionada != 'Todas':
    df_filtered = df_filtered[df_filtered['category_name'] == categoria_seleccionada]

# Filtro de transferencias
if 'Todas' not in transferencias_seleccionadas and len(transferencias_seleccionadas) > 0:
    # Crear máscaras para cada opción seleccionada
    transfer_masks = []
    
    for opcion in transferencias_seleccionadas:
        if opcion == '0':
            transfer_masks.append(df_filtered['total_transferences'] == 0)
        elif opcion == '1':
            transfer_masks.append(df_filtered['total_transferences'] == 1)
        elif opcion == '2':
            transfer_masks.append(df_filtered['total_transferences'] == 2)
        elif opcion == '3':
            transfer_masks.append(df_filtered['total_transferences'] == 3)
        elif opcion == '>3':
            transfer_masks.append(df_filtered['total_transferences'] > 3)
    
    # Combinar todas las máscaras con OR
    if transfer_masks:
        combined_mask = transfer_masks[0]
        for mask in transfer_masks[1:]:
            combined_mask = combined_mask | mask
        df_filtered = df_filtered[combined_mask]

if len(df_filtered) == 0:
    st.warning("⚠️ No hay datos para los filtros seleccionados.")
    st.stop()

# KPIs Principales con diseño mejorado
st.markdown("<div class='section-header'><h2>📈 Indicadores Clave de Desempeño (KPIs)</h2></div>", unsafe_allow_html=True)

# --- KPIs principales reordenados ---

col1, col2, col3, col4, col5 = st.columns(5)

# ⭐ CSAT Cliente
with col1:
    client_resolved_data = df_filtered['request_solved'].dropna()
    surveys_sent = df_filtered[df_filtered['sended_templates'].str.contains('survey_closing_message', case=False, na=False)]
    total_surveys_sent = len(surveys_sent)
    total_responses = len(client_resolved_data)
    response_rate = (total_responses / total_surveys_sent * 100) if total_surveys_sent > 0 else 0

    if len(client_resolved_data) > 0:
        csat_client = (client_resolved_data.sum() / len(client_resolved_data) * 100)
        st.metric(
            "⭐ CSAT Cliente",
            f"{csat_client:.2f}%",
            delta=f"{response_rate:.1f}% resp.",  # corto, visible siempre
            help=(
                f"Customer Satisfaction (CSAT)\n\n"
                f"📊 {csat_client:.2f}% de clientes marcaron su problema como resuelto.\n"
                f"📬 Encuestas enviadas: {total_surveys_sent:,}\n"
                f"🗳️ Respuestas recibidas: {total_responses:,}\n"
                f"📈 Tasa de respuesta: {response_rate:.1f}%"
            )
        )
    else:
        st.metric("⭐ CSAT Cliente", "N/A", help="No hay datos de encuestas disponibles.")

# 🤖 Auditoría AI
with col2:
    ai_resolved_data = df_filtered['ai_problem_resolved'].dropna()
    if len(ai_resolved_data) > 0:
        csat_ai = (ai_resolved_data.sum() / len(ai_resolved_data) * 100)
        st.metric(
            "🤖 Auditoría AI",
            f"{csat_ai:.2f}%",
            delta=f"{len(ai_resolved_data):,}/{len(df_filtered):,}",
            help=(
                "Evaluación automática del desempeño del agente IA.\n\n"
                f"📊 {csat_ai:.2f}% de conversaciones fueron clasificadas como *resueltas* por IA.\n"
                f"🧠 Total auditadas: {len(ai_resolved_data):,}\n"
                f"💬 Total conversaciones: {len(df_filtered):,}"
            )
        )
    else:
        st.metric("🤖 Auditoría AI", "N/A", help="No hay datos de auditoría de IA disponibles.")

# 🚀 FRT Promedio
with col3:
    frt_avg = df_filtered['frt_minutes'].mean()
    st.metric(
        "🚀 FRT Promedio",
        f"{frt_avg:.2f}min" if not pd.isna(frt_avg) else "N/A",
        help=(
            "First Response Time - Tiempo promedio hasta la primera respuesta del agente.\n\n"
            "🕒 Mide la rapidez de atención inicial al cliente.\n"
            f"📉 Promedio actual: {frt_avg:.2f} minutos."
        )
    )

# ⚡ ART Promedio
with col4:
    art_avg = df_filtered['art_hours'].mean()
    st.metric(
        "⚡ ART Promedio",
        f"{art_avg:.2f}h" if not pd.isna(art_avg) else "N/A",
        help=(
            "Average Resolution Time - Tiempo promedio desde asignación hasta el cierre del ticket.\n\n"
            "📈 Mide la eficiencia del flujo interno de resolución.\n"
            f"🕒 Promedio actual: {art_avg:.2f} horas."
        )
    )

# ⏱️ MTTR Promedio
with col5:
    mttr_avg = df_filtered['mttr_hours'].mean()
    st.metric(
        "⏱️ MTTR Promedio",
        f"{mttr_avg:.2f}h" if not pd.isna(mttr_avg) else "N/A",
        help=(
            "Mean Time To Resolution - Tiempo total promedio desde la creación hasta el cierre.\n\n"
            "📊 Mide el rendimiento general del ciclo de resolución.\n"
            f"🕒 Promedio actual: {mttr_avg:.2f} horas."
        )
    )

st.markdown("<br>", unsafe_allow_html=True)

# --- Fila 2 de KPIs ---
col6, col7, col8 = st.columns(3)

# 🎯 FCR
with col6:
    with st.spinner('Calculando FCR...'):
        fcr_value = calculate_fcr(df_filtered, fecha_inicio, fecha_fin, window_hours=fcr_window_hours)
    st.metric(
        f"🎯 FCR ({fcr_window_label})",
        f"{fcr_value:.2f}%" if not pd.isna(fcr_value) else "N/A",
        help=(
            "First Contact Resolution - Porcentaje de conversaciones resueltas en un solo contacto.\n\n"
            f"📊 Ventana de análisis: {fcr_window_label}\n"
            f"🎯 FCR actual: {fcr_value:.2f}%"
        )
    )

# 💬 Total Conversaciones
with col7:
    total_conv = len(df_filtered)
    perc_total = (total_conv / len(df) * 100) if len(df) > 0 else 0
    st.metric(
        "💬 Total Conversaciones",
        f"{total_conv:,}",
        delta=f"{perc_total:.1f}% del total",
        help=(
            "Cantidad total de conversaciones incluidas en el rango de fechas seleccionado.\n\n"
            f"💬 Conversaciones filtradas: {total_conv:,}\n"
            f"📅 Porcentaje sobre el total disponible: {perc_total:.1f}%"
        )
    )

# 📊 Complejidad Promedio
with col8:
    if 'difficulty_index' in df_filtered.columns and not df_filtered['difficulty_index'].dropna().empty:
        avg_complexity = df_filtered['difficulty_index'].mean()
        min_complexity = df_filtered['difficulty_index'].min()
        max_complexity = df_filtered['difficulty_index'].max()
        st.metric(
            "📊 Complejidad Promedio",
            f"{avg_complexity:.2f}",
            delta=f"{min_complexity:.1f}–{max_complexity:.1f}",
            help=(
                "Índice de dificultad de los casos analizados.\n\n"
                f"📉 Mínimo: {min_complexity:.2f}\n"
                f"📈 Máximo: {max_complexity:.2f}\n"
                f"⚖️ Promedio general: {avg_complexity:.2f}"
            )
        )
    else:
        st.metric("📊 Complejidad Promedio", "N/A", help="No hay datos de complejidad disponibles.")


st.markdown("<hr>", unsafe_allow_html=True)

# Aged Backlog con diseño mejorado
st.markdown("<div class='section-header'><h2>⏱️ Distribución de Duración de Conversaciones</h2></div>", unsafe_allow_html=True)

backlog_data = calculate_aged_backlog(df_filtered)

col_b1, col_b2, col_b3, col_b4 = st.columns(4)

with col_b1:
    st.metric(
        "⌛ Duración Promedio",
        f"{backlog_data['avg_duration']:.2f}h",
        help="Duración promedio desde creación hasta cierre"
    )

with col_b2:
    st.metric(
        "🕐 Duraron +6h",
        f"{backlog_data['6h']:.2f}%",
        delta=f"{backlog_data['count_6h']:,} conversaciones",
        delta_color="inverse",
        help="Porcentaje de conversaciones que duraron más de 6 horas"
    )

with col_b3:
    st.metric(
        "🕑 Duraron +12h",
        f"{backlog_data['12h']:.2f}%",
        delta=f"{backlog_data['count_12h']:,} conversaciones",
        delta_color="inverse",
        help="Porcentaje de conversaciones que duraron más de 12 horas"
    )

with col_b4:
    st.metric(
        "🕒 Duraron +24h",
        f"{backlog_data['24h']:.2f}%",
        delta=f"{backlog_data['count_24h']:,} conversaciones",
        delta_color="inverse",
        help="Porcentaje de conversaciones que duraron más de 24 horas"
    )

st.markdown("<hr>", unsafe_allow_html=True)

# Gráficos principales con diseño mejorado
st.markdown("<div class='section-header'><h2>📊 Análisis Visual Detallado</h2></div>", unsafe_allow_html=True)

# Tabs para mejor organización
tab1, tab2, tab3, tab4 = st.tabs(["📈 Tendencias", "👥 Agentes & Categorías", "😊 Satisfacción", "🕐 Análisis Temporal"])

with tab1:
    col_g1, col_g2 = st.columns(2)
    
    with col_g1:
        # Tendencia de conversaciones
        df_daily = df_filtered.groupby(df_filtered['closed_at'].dt.date).size().reset_index()
        df_daily.columns = ['Fecha', 'Conversaciones']
        
        fig_trend = px.area(
            df_daily,
            x='Fecha',
            y='Conversaciones',
            title="📈 Volumen Diario de Conversaciones"
        )
        fig_trend.update_traces(
            fill='tozeroy',
            fillcolor='rgba(102, 126, 234, 0.3)',
            line=dict(color=COLOR_PALETTE['primary'], width=3)
        )
        fig_trend = create_plotly_theme(fig_trend, height=400)
        st.plotly_chart(fig_trend, use_container_width=True)
    
    with col_g2:
        # Distribución por complejidad
        difficulty_dist = df_filtered['difficulty_category'].value_counts().reset_index()
        difficulty_dist.columns = ['Complejidad', 'Cantidad']
        
        difficulty_order = ['Easy', 'Medium', 'Hard', 'Very Hard']
        difficulty_dist['Complejidad'] = pd.Categorical(
            difficulty_dist['Complejidad'],
            categories=difficulty_order,
            ordered=True
        )
        difficulty_dist = difficulty_dist.sort_values('Complejidad')
        
        fig_difficulty = px.pie(
            difficulty_dist,
            values='Cantidad',
            names='Complejidad',
            title="🎯 Distribución por Complejidad",
            color='Complejidad',
            color_discrete_map={
                'Easy': COLOR_PALETTE['success'],
                'Medium': COLOR_PALETTE['warning'],
                'Hard': '#f97316',
                'Very Hard': COLOR_PALETTE['danger']
            },
            hole=0.5
        )
        fig_difficulty.update_traces(
            textposition='inside',
            textinfo='percent+label',
            textfont_size=12
        )
        fig_difficulty = create_plotly_theme(fig_difficulty, height=400)
        st.plotly_chart(fig_difficulty, use_container_width=True)

with tab2:
    col_g3, col_g4 = st.columns(2)
    
    with col_g3:
        # Top categorías
        top_categories = df_filtered['category_name'].value_counts().head(10).reset_index()
        top_categories.columns = ['Categoría', 'Cantidad']
        
        fig_categories = px.bar(
            top_categories,
            y='Categoría',
            x='Cantidad',
            orientation='h',
            title="🏆 Top 10 Categorías Más Frecuentes",
            text='Cantidad'
        )
        fig_categories.update_traces(
            marker_color=COLOR_PALETTE['gradient'],
            textposition='outside',
            textfont_size=11
        )
        fig_categories.update_layout(yaxis={'categoryorder': 'total ascending'})
        fig_categories = create_plotly_theme(fig_categories, height=500)
        st.plotly_chart(fig_categories, use_container_width=True)
    
    with col_g4:
        # Utilización de agentes
        agent_metrics = df_filtered.groupby('responsible_email').agg({
            'conversation_id': 'count',
            'difficulty_index': 'mean'
        }).reset_index()
        agent_metrics.columns = ['Agente', 'Conversaciones', 'Complejidad Promedio']
        
        # Normalizar complejidad a escala 0-1 para mejor visualización
        agent_metrics['Complejidad Normalizada'] = (
            (agent_metrics['Complejidad Promedio'] - agent_metrics['Complejidad Promedio'].min()) / 
            (agent_metrics['Complejidad Promedio'].max() - agent_metrics['Complejidad Promedio'].min())
        )
        
        agent_metrics = agent_metrics.sort_values('Conversaciones', ascending=False).head(10)
        
        fig_agents = go.Figure()
        
        # Barra principal: conversaciones
        fig_agents.add_trace(go.Bar(
            y=agent_metrics['Agente'],
            x=agent_metrics['Conversaciones'],
            orientation='h',
            name='Conversaciones',
            marker_color=agent_metrics['Complejidad Promedio'],
            marker_colorscale='RdYlGn_r',
            marker_colorbar=dict(title="Complejidad<br>Promedio"),
            text=agent_metrics['Conversaciones'],
            textposition='outside',
            hovertemplate='<b>%{y}</b><br>' +
                        'Conversaciones: %{x:,}<br>' +
                        'Complejidad: %{marker.color:.2f}<br>' +
                        '<extra></extra>'
        ))
        
        fig_agents.update_layout(
            title="👥 Top 10 Agentes por Volumen (Color = Complejidad)",
            yaxis={'categoryorder': 'total ascending'},
            showlegend=False
        )
        fig_agents = create_plotly_theme(fig_agents, height=500)
        st.plotly_chart(fig_agents, use_container_width=True)

with tab3:
    col_g5, col_g6 = st.columns(2)
    
    with col_g5:
        # Comparación CSAT
        ai_evaluated = df_filtered['ai_problem_resolved'].dropna()
        ai_resolved = int(ai_evaluated.sum()) if len(ai_evaluated) > 0 else 0
        ai_not_resolved = len(ai_evaluated) - ai_resolved if len(ai_evaluated) > 0 else 0
        
        client_evaluated = df_filtered['request_solved'].dropna()
        client_resolved = int(client_evaluated.sum()) if len(client_evaluated) > 0 else 0
        client_not_resolved = len(client_evaluated) - client_resolved if len(client_evaluated) > 0 else 0
        
        csat_comparison = pd.DataFrame({
            'Tipo': ['Auditoría AI', 'CSAT Cliente'],
            'Resuelto': [ai_resolved, client_resolved],
            'No Resuelto': [ai_not_resolved, client_not_resolved],
            'Sin Evaluar': [
                len(df_filtered) - len(ai_evaluated),
                len(df_filtered) - len(client_evaluated)
            ]
        })
        
        fig_csat = go.Figure()
        fig_csat.add_trace(go.Bar(
            name='✅ Resuelto',
            x=csat_comparison['Tipo'],
            y=csat_comparison['Resuelto'],
            marker_color=COLOR_PALETTE['success'],
            text=csat_comparison['Resuelto'],
            textposition='auto',
            textfont=dict(size=12, color='white')
        ))
        fig_csat.add_trace(go.Bar(
            name='❌ No Resuelto',
            x=csat_comparison['Tipo'],
            y=csat_comparison['No Resuelto'],
            marker_color=COLOR_PALETTE['danger'],
            text=csat_comparison['No Resuelto'],
            textposition='auto',
            textfont=dict(size=12, color='white')
        ))
        fig_csat.add_trace(go.Bar(
            name='⚪ Sin Evaluar',
            x=csat_comparison['Tipo'],
            y=csat_comparison['Sin Evaluar'],
            marker_color='#9ca3af',
            text=csat_comparison['Sin Evaluar'],
            textposition='auto',
            textfont=dict(size=12)
        ))
        
        fig_csat.update_layout(barmode='stack', title="🤖 vs ⭐ Comparación CSAT")
        fig_csat = create_plotly_theme(fig_csat, height=400)
        st.plotly_chart(fig_csat, use_container_width=True)
    
    with col_g6:
        # Distribución de sentimiento
        df_sentiment = df_filtered[df_filtered['ai_sentiment_score'].notna()].copy()
        
        if len(df_sentiment) > 0:
            df_sentiment['sentiment_range'] = pd.cut(
                df_sentiment['ai_sentiment_score'],
                bins=[-1, -0.6, -0.2, 0.2, 0.6, 1],
                labels=[
                    '😡 Terrible',
                    '🙁 Malo',
                    '😐 Normal',
                    '🙂 Bueno',
                    '🤩 Excelente'
                ],
                include_lowest=True
            )
            
            sentiment_dist = df_sentiment['sentiment_range'].value_counts().reset_index()
            sentiment_dist.columns = ['Sentimiento', 'Cantidad']
            sentiment_dist = sentiment_dist.sort_values('Sentimiento')  # Para mantener el orden lógico
            
            fig_sentiment = px.bar(
                sentiment_dist,
                x='Sentimiento',
                y='Cantidad',
                title=f"😊 Distribución del Sentimiento ({len(df_sentiment):,} evaluados)",
                color='Sentimiento',
                color_discrete_map={
                    '😡 Terrible': '#991b1b',
                    '🙁 Malo': '#f87171',
                    '😐 Normal': '#d4d4d4',
                    '🙂 Bueno': '#86efac',
                    '🤩 Excelente': '#166534'
                },
                text='Cantidad'
            )
            fig_sentiment.update_traces(textposition='outside', textfont_size=12)
            fig_sentiment = create_plotly_theme(fig_sentiment, height=400)
            st.plotly_chart(fig_sentiment, use_container_width=True)
        else:
            st.info("ℹ️ No hay datos de sentimiento disponibles para el período seleccionado")

with tab4:
    col_h1, col_h2 = st.columns(2)
    
    with col_h1:
        # Heatmap temporal
        temp_df = df_filtered[['created_at']].copy()
        temp_df['day_of_week'] = temp_df['created_at'].dt.day_name()
        temp_df['hour'] = temp_df['created_at'].dt.hour
        
        heatmap_data = temp_df.groupby(['day_of_week', 'hour']).size().reset_index(name='count')
        heatmap_pivot = heatmap_data.pivot(index='day_of_week', columns='hour', values='count').fillna(0)
        
        days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        heatmap_pivot = heatmap_pivot.reindex([day for day in days_order if day in heatmap_pivot.index])
        
        fig_heatmap = px.imshow(
            heatmap_pivot,
            labels=dict(x="Hora del Día", y="Día de la Semana", color="Conversaciones"),
            title="🗓️ Mapa de Calor: Volumen por Día y Hora",
            color_continuous_scale='Purples',
            aspect='auto'
        )
        fig_heatmap = create_plotly_theme(fig_heatmap, height=450)
        st.plotly_chart(fig_heatmap, use_container_width=True)
    
    with col_h2:
        # MTTR por día
        temp_df2 = df_filtered[['created_at', 'mttr_hours']].copy()
        temp_df2['day_of_week'] = temp_df2['created_at'].dt.day_name()
        
        mttr_by_day = temp_df2.groupby('day_of_week')['mttr_hours'].mean().reset_index()
        
        days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        mttr_by_day['day_of_week'] = pd.Categorical(
            mttr_by_day['day_of_week'],
            categories=days_order,
            ordered=True
        )
        mttr_by_day = mttr_by_day.sort_values('day_of_week')
        
        fig_mttr_day = px.line(
            mttr_by_day,
            x='day_of_week',
            y='mttr_hours',
            title="📅 MTTR Promedio por Día de la Semana",
            markers=True,
            text=mttr_by_day['mttr_hours'].apply(lambda x: f'{x:.1f}h')
        )
        fig_mttr_day.update_traces(
            line=dict(color=COLOR_PALETTE['secondary'], width=4),
            marker=dict(size=10, color=COLOR_PALETTE['primary']),
            textposition='top center',
            textfont=dict(size=11, color=COLOR_PALETTE['dark'])
        )
        fig_mttr_day.update_layout(xaxis_title="Día de la Semana", yaxis_title="MTTR (horas)")
        fig_mttr_day = create_plotly_theme(fig_mttr_day, height=450)
        st.plotly_chart(fig_mttr_day, use_container_width=True)

st.markdown("<hr>", unsafe_allow_html=True)

# Gráficos adicionales
st.markdown("<div class='section-header'><h2>📊 Análisis Complementario</h2></div>", unsafe_allow_html=True)

col_extra1, col_extra2 = st.columns(2)

with col_extra1:
    # Tiempos de respuesta
    response_times = pd.DataFrame({
        'Métrica': ['Agente→Cliente P75', 'Agente→Cliente P95', 'Cliente→Agente P75', 'Cliente→Agente P95'],
        'Minutos': [
            df_filtered['agent_to_client_p75_minutes'].mean(),
            df_filtered['agent_to_client_p95_minutes'].mean(),
            df_filtered['client_to_agent_p75_minutes'].mean(),
            df_filtered['client_to_agent_p95_minutes'].mean()
        ]
    })
    
    fig_response = px.bar(
        response_times,
        x='Métrica',
        y='Minutos',
        title="⏱️ Tiempos de Respuesta (Promedios)",
        color='Minutos',
        color_continuous_scale='Viridis',
        text=response_times['Minutos'].apply(lambda x: f'{x:.1f}' if not pd.isna(x) else 'N/A')
    )
    fig_response.update_traces(textposition='outside', textfont_size=11)
    fig_response = create_plotly_theme(fig_response, height=400)
    st.plotly_chart(fig_response, use_container_width=True)

with col_extra2:
    # Análisis de transferencias
    transfer_analysis = df_filtered['total_transferences'].value_counts().reset_index()
    transfer_analysis.columns = ['Número de Transferencias', 'Cantidad']
    transfer_analysis = transfer_analysis.sort_values('Número de Transferencias')
    
    fig_transfers = px.bar(
        transfer_analysis,
        x='Número de Transferencias',
        y='Cantidad',
        title="🔄 Frecuencia de Transferencias",
        color='Cantidad',
        color_continuous_scale='Reds',
        text='Cantidad'
    )
    fig_transfers.update_traces(textposition='outside', textfont_size=11)
    fig_transfers = create_plotly_theme(fig_transfers, height=400)
    st.plotly_chart(fig_transfers, use_container_width=True)

st.markdown("<hr>", unsafe_allow_html=True)

# Histograma de duración
st.markdown("<div class='section-header'><h2>📊 Distribución Detallada de Duración</h2></div>", unsafe_allow_html=True)

df_duration = df_filtered[df_filtered['conversation_duration_hours'].notna()].copy()

if len(df_duration) > 0:
    fig_duration = px.histogram(
        df_duration,
        x='conversation_duration_hours',
        nbins=50,
        title="⏳ Histograma de Duración de Conversaciones",
        labels={'conversation_duration_hours': 'Duración (horas)', 'count': 'Frecuencia'},
        color_discrete_sequence=[COLOR_PALETTE['primary']]
    )
    fig_duration.update_traces(marker_line_color='white', marker_line_width=1.5)
    fig_duration = create_plotly_theme(fig_duration, height=400)
    st.plotly_chart(fig_duration, use_container_width=True)
else:
    st.info("No hay datos de duración disponibles")

st.markdown("<hr>", unsafe_allow_html=True)

# Tabla de datos detallados con diseño mejorado
st.markdown("<div class='section-header'><h2>📋 Datos Detallados</h2></div>", unsafe_allow_html=True)

with st.expander("🔍 Ver tabla de datos", expanded=False):
    display_columns = [
        'conversation_id', 'responsible_email', 'queue_name', 'category_name',
        'mttr_hours', 'art_hours', 'frt_minutes', 'ai_summary',
        'difficulty_category', 'ai_problem_resolved', 'request_solved',
        'ai_sentiment_score', 'total_transferences','time_losted_in_transferences_minutes',
        'all_responsibles', 'sended_templates', 'closed_at', 'agent_to_client_avg_minutes',
        'agent_to_client_p75_minutes', 'agent_to_client_p95_minutes'
    ]
    
    df_display = df_filtered[display_columns].copy()
    
    numeric_cols = df_display.select_dtypes(include=[np.number]).columns
    df_display[numeric_cols] = df_display[numeric_cols].round(2)
    
    st.dataframe(
        df_display.sort_values('closed_at', ascending=False),
        use_container_width=True,
        height=400
    )
    
    st.info(f"ℹ️ Mostrando {len(df_filtered):,} conversaciones totales")

st.markdown("<hr>", unsafe_allow_html=True)

# Footer con diseño mejorado
st.markdown(f"""
    <div class='footer'>
        <h3 style='color: {COLOR_PALETTE["dark"]}; margin-bottom: 1rem;'>📊 Resumen del Dashboard</h3>
        <div style='display: flex; justify-content: space-around; margin: 1rem 0;'>
            <div>
                <p style='font-size: 1.2rem; font-weight: 700; color: {COLOR_PALETTE["primary"]};'>{len(df):,}</p>
                <p style='font-size: 0.85rem;'>Registros Totales</p>
            </div>
            <div>
                <p style='font-size: 1.2rem; font-weight: 700; color: {COLOR_PALETTE["secondary"]};'>{len(df_filtered):,}</p>
                <p style='font-size: 0.85rem;'>Registros Filtrados</p>
            </div>
            <div>
                <p style='font-size: 1.2rem; font-weight: 700; color: {COLOR_PALETTE["success"]};'>{(datetime.now() + timedelta(hours=6)).strftime("%H:%M")}</p>
                <p style='font-size: 0.85rem;'>Caché Válido Hasta</p>
            </div>
        </div>
        <hr style='margin: 1.5rem 0; opacity: 0.2;'>
        <p style='margin: 0.5rem 0;'><strong>Dashboard SAC - Métricas de Conversaciones</strong></p>
        <p style='margin: 0.5rem 0;'>🔄 Actualizado automáticamente cada 6 horas | 📅 ETL ejecutado diariamente</p>
        <p style='margin: 0.5rem 0; font-size: 0.85rem;'>💡 Tip: Los datos se cachean por 6 horas. Usa el botón "♻️ Refrescar" para forzar una actualización</p>
        <p style='margin: 1rem 0 0 0; font-size: 0.8rem; opacity: 0.7;'>Desarrollado con ❤️ usando Streamlit + Plotly + Supabase</p>
    </div>
""", unsafe_allow_html=True)


