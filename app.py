import streamlit as st
import os
import re
from datetime import datetime
from PIL import Image
import io
import base64
from pathlib import Path
from media_downloader import YouTubeVideoDownloader, YouTubeAudioDownloader, SoundCloudDownloader

# Configuración de la página
st.set_page_config(
    page_title="TubeGrab - Descarga Videos y Audio",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS personalizados
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stButton>button {
        width: 100%;
        background-color: #FF0000;
        color: white;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 5px;
        font-size: 1.1rem;
    }
    .stButton>button:hover {
        background-color: #CC0000;
    }
    .info-box {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    .success-box {
        background-color: #d4edda;
        color: #155724;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    .error-box {
        background-color: #f8d7da;
        color: #721c24;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    .app-title {
        font-size: 2.5rem;
        font-weight: bold;
        color: #FF0000;
        text-align: center;
        margin-bottom: 1rem;
    }
    .app-subtitle {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .tab-content {
        padding: 1rem 0;
    }
    </style>
    """, unsafe_allow_html=True)

def formatear_duracion(segundos):
    """Formatea la duración en segundos a formato legible"""
    if not segundos:
        return "N/A"
    minutos, segundos = divmod(segundos, 60)
    horas, minutos = divmod(minutos, 60)
    if horas > 0:
        return f"{int(horas)}:{int(minutos):02d}:{int(segundos):02d}"
    return f"{int(minutos):02d}:{int(segundos):02d}"

def main():
    # Título y descripción
    st.markdown('<div class="app-title">🎯 TubeGrab</div>', unsafe_allow_html=True)
    st.markdown('<div class="app-subtitle">Tu herramienta favorita para descargar videos y audio</div>', unsafe_allow_html=True)
    
    # Sidebar con información
    with st.sidebar:
        st.header("ℹ️ Acerca de TubeGrab")
        st.markdown("""
        ### Características:
        - Descarga videos de YouTube en MP4
        - Descarga audio de YouTube en MP3
        - Descarga audio de SoundCloud en MP3
        - Soporta videos y audios públicos
        - Interfaz amigable y fácil de usar
        
        ### Notas:
        - Asegúrate de tener una buena conexión a internet
        - Los archivos se guardan en la carpeta 'descargas'
        - El tiempo de descarga depende del tamaño del archivo
        """)
        
        st.markdown("---")
        st.markdown("### 📝 Instrucciones")
        st.markdown("""
        1. Selecciona el tipo de descarga
        2. Copia la URL del video o audio
        3. Pégala en el campo de texto
        4. Haz clic en 'Descargar'
        5. ¡Listo! Tu archivo estará disponible
        """)
        
        st.markdown("---")
        st.markdown("### 🌟 ¿Por qué TubeGrab?")
        st.markdown("""
        - Rápido y eficiente
        - Interfaz intuitiva
        - Sin anuncios molestos
        - Totalmente gratuito
        - Soporte para múltiples plataformas
        """)

    # Crear pestañas para diferentes tipos de descarga
    tab1, tab2, tab3 = st.tabs(["🎥 YouTube Video", "🎵 YouTube Audio", "🎧 SoundCloud"])

    with tab1:
        st.markdown("### Descargar Video de YouTube")
        url_video = st.text_input("URL del video de YouTube", placeholder="https://www.youtube.com/watch?v=...", key="video_url")
        
        if st.button("Descargar Video", type="primary", key="download_video"):
            if url_video:
                with st.spinner("Procesando video..."):
                    downloader = YouTubeVideoDownloader()
                    try:
                        video_info = downloader.descargar(url_video)
                        if video_info:
                            st.success("¡Video descargado exitosamente!")
                            # Mostrar información y botón de descarga
                            mostrar_info_archivo(video_info, "video")
                    except Exception as e:
                        st.error(f"Error al descargar el video: {str(e)}")

    with tab2:
        st.markdown("### Descargar Audio de YouTube")
        url_audio = st.text_input("URL del video de YouTube", placeholder="https://www.youtube.com/watch?v=...", key="audio_url")
        
        if st.button("Descargar Audio", type="primary", key="download_audio"):
            if url_audio:
                with st.spinner("Procesando audio..."):
                    downloader = YouTubeAudioDownloader()
                    try:
                        audio_info = downloader.descargar(url_audio)
                        if audio_info:
                            st.success("¡Audio descargado exitosamente!")
                            # Mostrar información y botón de descarga
                            mostrar_info_archivo(audio_info, "audio")
                    except Exception as e:
                        st.error(f"Error al descargar el audio: {str(e)}")

    with tab3:
        st.markdown("### Descargar Audio de SoundCloud")
        url_soundcloud = st.text_input("URL de SoundCloud", placeholder="https://soundcloud.com/...", key="soundcloud_url")
        
        if st.button("Descargar Audio", type="primary", key="download_soundcloud"):
            if url_soundcloud:
                with st.spinner("Procesando audio de SoundCloud..."):
                    downloader = SoundCloudDownloader()
                    try:
                        audio_info = downloader.descargar(url_soundcloud)
                        if audio_info:
                            st.success("¡Audio descargado exitosamente!")
                            # Mostrar información y botón de descarga
                            mostrar_info_archivo(audio_info, "audio")
                    except Exception as e:
                        st.error(f"Error al descargar el audio: {str(e)}")

def mostrar_info_archivo(info, tipo):
    """Muestra la información del archivo descargado y el botón de descarga"""
    col1, col2 = st.columns([1, 2])
    
    with col1:
        if info.get('thumbnail'):
            st.image(info['thumbnail'], caption="Miniatura")
    
    with col2:
        st.markdown(f"### {info['titulo']}")
        st.markdown(f"""
        <div class="info-box">
            <p>⏱️ Duración: {info.get('duracion', 'N/A')}</p>
            <p>👁️ Vistas: {info.get('vistas', 'N/A')}</p>
            <p>📁 Formato: {info.get('formato', 'MP3' if tipo == 'audio' else 'MP4')}</p>
        </div>
        """, unsafe_allow_html=True)
        
        if 'archivo' in info:
            with open(info['archivo'], 'rb') as f:
                mime_type = "audio/mp3" if tipo == "audio" else "video/mp4"
                st.download_button(
                    label=f"⬇️ Descargar {info.get('formato', 'MP3' if tipo == 'audio' else 'MP4')}",
                    data=f,
                    file_name=os.path.basename(info['archivo']),
                    mime=mime_type
                )

if __name__ == "__main__":
    main() 