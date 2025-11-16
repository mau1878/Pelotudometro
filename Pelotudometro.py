import streamlit as st
import pandas as pd
from datetime import datetime
import io
import plotly.express as px # <-- 1. IMPORTAR PLOTLY

# --- CONFIGURACIÓN INICIAL ---

st.set_page_config(page_title="El Pelotudómetro del Trader", layout="centered")
st.title("🇦🇷 El Pelotudómetro del Trader 🇦🇷")
st.write("""
**¿Estás para operar o para hacer cagadas?** Este test te mide el nivel de pelotudez antes de que le regales tu guita al mercado. Respondé con sinceridad.
""")

# --- INICIALIZACIÓN DEL ESTADO DE LA SESIÓN ---

if 'df_historial' not in st.session_state:
    st.session_state.df_historial = pd.DataFrame()

# --- CARGA DE HISTORIAL (OPCIONAL) ---

st.header("1. Cargá tu historial (si ya tenés)")
uploaded_file = st.file_uploader(
    "Si ya tenés un historial guardado, subilo acá para seguir tu seguimiento.",
    type=["csv"]
)

if uploaded_file is not None:
    try:
        df_cargado = pd.read_csv(uploaded_file)
        st.session_state.df_historial = df_cargado
        st.success("✅ ¡Listo! Historial cargado. Ahora respondé el test de hoy.")
    except Exception as e:
        st.error(f"Uh, algo falló al leer el archivo: {e}")

# --- CUESTIONARIO ---

st.header("2. Respondé el Cuestionario de Hoy")

preguntas = {
    "P1": "Dormí para el culo (menos de 7hs) o me desperté mil veces.",
    "P2": "Estoy quemado por quilombos personales (familia, laburo, etc.).",
    "P3": "Vengo de una pérdida y tengo una sed de revancha que me muero.",
    "P4": "Vengo de una buena racha y me siento imparable, creo que no puedo perder.",
    "P5": "Me cuesta un huevo concentrarme, hasta para leer una noticia.",
    "P6": "Estoy manija por entrar ya, sin esperar una señal clara.",
    "P7": "Hoy me pinta arriesgar más de la cuenta (más lotes, sin stop loss).",
    "P8": "Colgué y no hice mi rutina previa a la rueda (no revisé nada, no anoté en mis registros, etc.).",
    "P9": "Estoy caliente/envidioso/con FOMO por lo que veo en Twitter o por cómo se mueve el mercado.",
    "P10": "Siento el estrés en el cuerpo (dolor de cabeza, contractura, taquicardia).",
}

with st.form(key="pelotudometro_form"):
    respuestas = {}
    for key, pregunta in preguntas.items():
        respuestas[key] = st.slider(pregunta, 1, 5, 3, key=f"slider_{key}")

    submit_button = st.form_submit_button(label="Calcular Nivel de Pelotudez")

# --- CÁLCULO Y ACTUALIZACIÓN DEL HISTORIAL ---

if submit_button:
    puntaje_total = sum(respuestas.values())

    if puntaje_total <= 20:
        interpretacion = "✅ Puntaje bajo. Estás lúcido. Dale para adelante, pero no te agrandés."
        st.success(f"**Puntaje Total: {puntaje_total}**. {interpretacion}")
    elif 21 <= puntaje_total <= 30:
        interpretacion = "⚠️ Puntaje medio. Guarda. Andá con cuidado, revisá tu plan y no te zarpes con el tamaño."
        st.warning(f"**Puntaje Total: {puntaje_total}**. {interpretacion}")
    else:
        interpretacion = "🚨 ¡Puntaje alto! ALERTA ROJA. Estás a punto de hacer una macana. Apagá la compu y andá a tomar aire. En serio."
        st.error(f"**Puntaje Total: {puntaje_total}**. {interpretacion}")

    fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    nuevo_registro_dict = {"Fecha": [fecha_actual]}
    nuevo_registro_dict.update({k: [v] for k, v in respuestas.items()})
    nuevo_registro_dict["PuntajeTotal"] = [puntaje_total]
    nuevo_registro_dict["Interpretacion"] = [interpretacion.split('.')[0]]
    
    nuevo_registro_df = pd.DataFrame(nuevo_registro_dict)

    st.session_state.df_historial = pd.concat([st.session_state.df_historial, nuevo_registro_df], ignore_index=True)
    st.info("💾 Tu resultado se guardó en el historial de esta sesión. ¡No te olvides de descargarlo!")

# --- VISUALIZACIÓN Y DESCARGA DEL HISTORIAL ---

st.header("3. Tu Historial y Descarga")

if not st.session_state.df_historial.empty:
    df_display = st.session_state.df_historial.copy()
    df_display['Fecha'] = pd.to_datetime(df_display['Fecha'])
    df_display = df_display.sort_values(by="Fecha", ascending=False)

    st.write("Acá podés ver tus registros anteriores para ver si sos un pelotudo recurrente.")
    
    # --- 2. SECCIÓN DEL GRÁFICO MEJORADA ---
    st.write("#### Evolución de tu Nivel de Pelotudez")
    fig = px.line(
        df_display,
        x='Fecha',
        y='PuntajeTotal',
        markers=True,
        labels={'PuntajeTotal': 'Nivel de Pelotudez', 'Fecha': 'Día'},
        hover_data={'Interpretacion': True, 'PuntajeTotal': ':.0f'}
    )
    fig.update_traces(line=dict(color='#FF8C00', width=3), marker=dict(size=8)) # Naranja oscuro
    fig.update_layout(
        xaxis_title="Fecha de Medición",
        yaxis_title="Puntaje (más alto = más pelotudo)",
        template="streamlit" # Usa el tema de Streamlit para consistencia
    )
    st.plotly_chart(fig, use_container_width=True)
    # --- FIN DE LA SECCIÓN DEL GRÁFICO ---

    st.write("#### Datos Completos")
    st.dataframe(df_display)

    csv = st.session_state.df_historial.to_csv(index=False).encode('utf-8')
    
    st.download_button(
       label="⬇️ Descargá tu Historial Actualizado (CSV)",
       data=csv,
       file_name='mi_pelotudometro.csv',
       mime='text/csv',
    )
else:
    st.info("Todavía no tenés registros. Completá el cuestionario para empezar.")
