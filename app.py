import streamlit as st
import yt_dlp
import os
import re
from datetime import datetime
from PIL import Image
import io
import base64
from pathlib import Path

# Configuración de la página
st.set_page_config(
    page_title="TubeGrab - Descarga Videos de YouTube",
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
    </style>
    """, unsafe_allow_html=True)

def validar_url_youtube(url):
    """Valida si la URL es de YouTube"""
    patron_youtube = r'(https?://)?(www\.)?(youtube\.com|youtu\.be)/.+'
    return bool(re.match(patron_youtube, url))

def normalizar_url(url):
    """Normaliza la URL de YouTube"""
    if 'youtu.be' in url:
        video_id = url.split('/')[-1]
        return f'https://www.youtube.com/watch?v={video_id}'
    return url

def formatear_tamaño(tamaño_bytes):
    """Formatea el tamaño en bytes a una cadena legible"""
    if tamaño_bytes is None:
        return "N/A"
    for unidad in ['B', 'KB', 'MB', 'GB']:
        if tamaño_bytes < 1024:
            return f"{tamaño_bytes:.1f}{unidad}"
        tamaño_bytes /= 1024
    return f"{tamaño_bytes:.1f}TB"

def formatear_duracion(segundos):
    """Formatea la duración en segundos a formato legible"""
    if not segundos:
        return "N/A"
    minutos, segundos = divmod(segundos, 60)
    horas, minutos = divmod(minutos, 60)
    if horas > 0:
        return f"{int(horas)}:{int(minutos):02d}:{int(segundos):02d}"
    return f"{int(minutos):02d}:{int(segundos):02d}"

def descargar_video(url, carpeta_destino="descargas"):
    try:
        # Normalizar la URL
        url = normalizar_url(url)
        
        # Validar la URL
        if not validar_url_youtube(url):
            st.error("La URL proporcionada no es válida para YouTube")
            return None

        # Crear la carpeta de destino si no existe
        if not os.path.exists(carpeta_destino):
            os.makedirs(carpeta_destino)

        # Configurar opciones de yt-dlp
        ydl_opts = {
            'format': 'best[ext=mp4]/best',
            'outtmpl': os.path.join(carpeta_destino, '%(title)s.%(ext)s'),
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Obtener información del video
            info = ydl.extract_info(url, download=False)
            
            # Crear un diccionario con la información del video
            video_info = {
                'titulo': info['title'],
                'duracion': formatear_duracion(info.get('duration')),
                'vistas': f"{info.get('view_count', 0):,}",
                'formato': 'MP4',
                'url': url,
                'thumbnail': info.get('thumbnail'),
                'formats': []
            }
            
            # Obtener formatos disponibles
            formatos_mp4 = [f for f in info['formats'] if f.get('ext') == 'mp4' and f.get('format_note')]
            for f in formatos_mp4:
                tamaño = f.get('filesize', 0) or f.get('filesize_approx', 0)
                video_info['formats'].append({
                    'calidad': f.get('format_note', 'N/A'),
                    'tamaño': formatear_tamaño(tamaño)
                })
            
            # Descargar el video
            ydl.download([url])
            
            # Obtener la ruta del archivo descargado
            archivo_descargado = os.path.join(carpeta_destino, f"{info['title']}.mp4")
            if os.path.exists(archivo_descargado):
                video_info['archivo'] = archivo_descargado
                return video_info
            
            return None
            
    except Exception as e:
        st.error(f"Error al descargar el video: {str(e)}")
        return None

def main():
    # Título y descripción
    st.markdown('<div class="app-title">🎯 TubeGrab</div>', unsafe_allow_html=True)
    st.markdown('<div class="app-subtitle">Tu herramienta favorita para descargar videos de YouTube</div>', unsafe_allow_html=True)
    
    # Sidebar con información
    with st.sidebar:
        st.header("ℹ️ Acerca de TubeGrab")
        st.markdown("""
        ### Características:
        - Descarga videos en la mejor calidad disponible
        - Soporta videos públicos de YouTube
        - Formato de salida: MP4
        - Interfaz amigable y fácil de usar
        
        ### Notas:
        - Asegúrate de tener una buena conexión a internet
        - Los videos se guardan en la carpeta 'descargas'
        - El tiempo de descarga depende del tamaño del video
        """)
        
        st.markdown("---")
        st.markdown("### 📝 Instrucciones")
        st.markdown("""
        1. Copia la URL del video de YouTube
        2. Pégala en el campo de texto
        3. Haz clic en 'Descargar'
        4. ¡Listo! Tu video estará disponible
        """)
        
        st.markdown("---")
        st.markdown("### 🌟 ¿Por qué TubeGrab?")
        st.markdown("""
        - Rápido y eficiente
        - Interfaz intuitiva
        - Sin anuncios molestos
        - Totalmente gratuito
        """)

    # Campo para la URL
    url = st.text_input("URL del video de YouTube", placeholder="https://www.youtube.com/watch?v=...")
    
    # Botón de descarga
    if st.button("Descargar Video", type="primary"):
        if url:
            with st.spinner("Procesando video..."):
                # Mostrar información del video
                video_info = descargar_video(url)
                
                if video_info:
                    # Crear dos columnas para la información
                    col1, col2 = st.columns([1, 2])
                    
                    with col1:
                        # Mostrar thumbnail si está disponible
                        if video_info['thumbnail']:
                            st.image(video_info['thumbnail'], caption="Miniatura del video")
                    
                    with col2:
                        # Mostrar información del video
                        st.markdown(f"### {video_info['titulo']}")
                        st.markdown(f"""
                        <div class="info-box">
                            <p>📺 Duración: {video_info['duracion']}</p>
                            <p>👁️ Vistas: {video_info['vistas']}</p>
                            <p>📁 Formato: {video_info['formato']}</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Mostrar formatos disponibles
                        st.markdown("### Formatos disponibles:")
                        for formato in video_info['formats']:
                            st.markdown(f"- {formato['calidad']} ({formato['tamaño']})")
                        
                        # Botón de descarga
                        if 'archivo' in video_info:
                            with open(video_info['archivo'], 'rb') as f:
                                st.download_button(
                                    label="⬇️ Descargar MP4",
                                    data=f,
                                    file_name=os.path.basename(video_info['archivo']),
                                    mime="video/mp4"
                                )
                            
                            st.markdown("""
                            <div class="success-box">
                                ✅ Video descargado exitosamente
                            </div>
                            """, unsafe_allow_html=True)
        else:
            st.warning("Por favor, ingresa una URL de YouTube válida")

if __name__ == "__main__":
    main() 