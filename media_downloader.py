from abc import ABC, abstractmethod
import yt_dlp
import os
import re
import time
from tqdm import tqdm
import subprocess
import mutagen
from mutagen.easyid3 import EasyID3
from mutagen.mp3 import MP3

class ProgressHook:
    def __init__(self):
        self.pbar = None

    def __call__(self, d):
        if d['status'] == 'downloading':
            if self.pbar is None:
                total = d.get('total_bytes', 0) or d.get('total_bytes_estimate', 0)
                self.pbar = tqdm(total=total, unit='B', unit_scale=True, desc="Descargando")
            
            downloaded = d.get('downloaded_bytes', 0)
            self.pbar.update(downloaded - self.pbar.n)
            
        elif d['status'] == 'finished':
            if self.pbar:
                self.pbar.close()
                self.pbar = None
            print("\nDescarga completada, procesando archivo...")

class MediaDownloader(ABC):
    def __init__(self, carpeta_destino="descargas"):
        self.carpeta_destino = carpeta_destino
        if not os.path.exists(carpeta_destino):
            os.makedirs(carpeta_destino)

    @abstractmethod
    def validar_url(self, url):
        pass

    @abstractmethod
    def descargar(self, url):
        pass

    def formatear_tamaño(self, tamaño_bytes):
        if tamaño_bytes is None:
            return "N/A"
        for unidad in ['B', 'KB', 'MB', 'GB']:
            if tamaño_bytes < 1024:
                return f"{tamaño_bytes:.1f}{unidad}"
            tamaño_bytes /= 1024
        return f"{tamaño_bytes:.1f}TB"

    def _procesar_descarga(self, url, ydl_opts, intentos_maximos):
        for intento in range(intentos_maximos):
            try:
                print(f"\nIntento {intento + 1} de {intentos_maximos}")
                
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    # Obtener información del video/audio
                    info = ydl.extract_info(url, download=False)
                    
                    # Crear diccionario con la información
                    media_info = {
                        'titulo': info['title'],
                        'duracion': info.get('duration', 'N/A'),
                        'vistas': f"{info.get('view_count', 0):,}",
                        'url': url,
                        'thumbnail': info.get('thumbnail'),
                        'formato': 'MP3' if 'audio' in ydl_opts.get('format', '') else 'MP4'
                    }
                    
                    print(f"\nTítulo: {media_info['titulo']}")
                    print(f"Duración: {media_info['duracion']} segundos")
                    if media_info['vistas'] != '0':
                        print(f"Vistas: {media_info['vistas']}")
                    
                    print("\nIniciando descarga...")
                    ydl.download([url])
                    
                    # Obtener la ruta del archivo descargado
                    extension = 'mp3' if 'audio' in ydl_opts.get('format', '') else 'mp4'
                    archivo_descargado = os.path.join(self.carpeta_destino, f"{info['title']}.{extension}")
                    
                    if os.path.exists(archivo_descargado):
                        media_info['archivo'] = archivo_descargado
                        print(f"\n¡Descarga completada! El archivo se ha guardado en la carpeta '{self.carpeta_destino}'")
                        return media_info
                    
                    return None
                
            except Exception as e:
                error_msg = str(e)
                print(f"\nError en intento {intento + 1}: {error_msg}")
                
                if intento < intentos_maximos - 1:
                    print("Reintentando en 3 segundos...")
                    time.sleep(3)
                else:
                    print("\nSe agotaron los intentos de descarga.")
                    raise e

class YouTubeVideoDownloader(MediaDownloader):
    def validar_url(self, url):
        patron_youtube = r'(https?://)?(www\.)?(youtube\.com|youtu\.be)/.+'
        return bool(re.match(patron_youtube, url))

    def normalizar_url(self, url):
        if 'youtu.be' in url:
            video_id = url.split('/')[-1]
            return f'https://www.youtube.com/watch?v={video_id}'
        return url

    def _listar_formatos(self, url):
        """Lista los formatos disponibles para el video."""
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'skip_download': True,
        }
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                print("\nFormatos disponibles:")
                for f in info['formats']:
                    if f.get('vcodec', 'none') != 'none':  # Solo formatos con video
                        print(f"Formato: {f['format_id']} - {f.get('ext', 'N/A')} - {f.get('height', 'N/A')}p - {f.get('format_note', '')}")
        except Exception as e:
            print(f"Error al listar formatos: {str(e)}")

    def descargar(self, url, intentos_maximos=3):
        url = self.normalizar_url(url)
        if not self.validar_url(url):
            raise ValueError("URL de YouTube no válida")

        # Primero intentamos con el formato más simple
        ydl_opts = {
            'format': 'best',  # Usamos el mejor formato disponible
            'merge_output_format': 'mp4',
            'outtmpl': os.path.join(self.carpeta_destino, '%(title)s.%(ext)s'),
            'progress_hooks': [ProgressHook()],
            'quiet': True,
            'no_warnings': True,
            'postprocessors': [{
                'key': 'FFmpegVideoConvertor',
                'preferedformat': 'mp4',
            }],
            'writethumbnail': True,
            'noplaylist': True,
        }

        try:
            return self._procesar_descarga(url, ydl_opts, intentos_maximos)
        except Exception as e:
            print(f"\nError con el formato predeterminado: {str(e)}")
            print("\nIntentando listar formatos disponibles...")
            self._listar_formatos(url)
            
            # Intentamos con un formato alternativo
            print("\nIntentando con formato alternativo...")
            ydl_opts['format'] = 'bestvideo+bestaudio/best'
            try:
                return self._procesar_descarga(url, ydl_opts, intentos_maximos)
            except Exception as e2:
                print(f"\nError con formato alternativo: {str(e2)}")
                raise Exception("No se pudo descargar el video. Por favor, revisa los formatos disponibles arriba.")

class YouTubeAudioDownloader(MediaDownloader):
    def validar_url(self, url):
        patron_youtube = r'(https?://)?(www\.)?(youtube\.com|youtu\.be)/.+'
        return bool(re.match(patron_youtube, url))

    def normalizar_url(self, url):
        if 'youtu.be' in url:
            video_id = url.split('/')[-1]
            return f'https://www.youtube.com/watch?v={video_id}'
        return url

    def descargar(self, url, intentos_maximos=3):
        url = self.normalizar_url(url)
        if not self.validar_url(url):
            raise ValueError("URL de YouTube no válida")

        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'outtmpl': os.path.join(self.carpeta_destino, '%(title)s.%(ext)s'),
            'progress_hooks': [ProgressHook()],
            'quiet': True,
            'no_warnings': True,
            'writethumbnail': True,
        }

        media_info = self._procesar_descarga(url, ydl_opts, intentos_maximos)
        if media_info and 'archivo' in media_info:
            self._agregar_metadatos(media_info['archivo'], media_info)
        return media_info

    def _agregar_metadatos(self, archivo_mp3, info):
        try:
            audio = MP3(archivo_mp3, ID3=EasyID3)
            audio['title'] = info['titulo']
            audio['artist'] = info.get('uploader', 'Unknown Artist')
            audio['album'] = info.get('album', 'YouTube Audio')
            audio['date'] = str(info.get('upload_date', ''))[:4]
            audio.save()
        except Exception as e:
            print(f"Error al agregar metadatos: {str(e)}")

class SoundCloudDownloader(MediaDownloader):
    def validar_url(self, url):
        patron_soundcloud = r'(https?://)?(www\.)?soundcloud\.com/.+'
        return bool(re.match(patron_soundcloud, url))

    def descargar(self, url, intentos_maximos=3):
        if not self.validar_url(url):
            raise ValueError("URL de SoundCloud no válida")

        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'outtmpl': os.path.join(self.carpeta_destino, '%(title)s.%(ext)s'),
            'progress_hooks': [ProgressHook()],
            'quiet': True,
            'no_warnings': True,
        }

        return self._procesar_descarga(url, ydl_opts, intentos_maximos) 