import os
import re
import sys
import argparse
import yt_dlp

def extract_youtube_id(url_or_id):
    if not url_or_id:
        return ""
    url_or_id = url_or_id.strip()
    match = re.search(r'(?:youtu\.be\/|v\/|u\/\w\/|embed\/|watch\?v=|&v=)([^#&?]{11})', url_or_id)
    if match:
        return match.group(1)
    if len(url_or_id) == 11 and not any(c in url_or_id for c in ['/', '?', '&', '=']):
        return url_or_id
    return url_or_id

def download_youtube_video(youtube_id, output_dir="downloads", subtitle_lang=None, quality="360p"):
    """
    Baixa um vídeo do YouTube.
    Por padrão em até 360p pre-muxed (para compatibilidade com o operador) ou 'best' / '1080p'.
    Também baixa legendas se subtitle_lang for especificado.
    Retorna (caminho_do_video, titulo, caminho_da_legenda)
    """
    os.makedirs(output_dir, exist_ok=True)
    clean_id = extract_youtube_id(youtube_id)
    url = f"https://www.youtube.com/watch?v={clean_id}"
    
    print(f"[{clean_id}] Verificando/Baixando arquivo...")
    output_template = os.path.join(output_dir, f"{clean_id}.%(ext)s")
    
    if quality in ("best", "1080p"):
        fmt = "bestvideo[height<=1080]+bestaudio/best[height<=1080]/best"
    else:
        fmt = "best[height<=360]"

    ydl_opts = {
        'format': fmt,
        'outtmpl': output_template,
        'quiet': False,
        'no_warnings': True,
        'merge_output_format': 'mp4',
    }
    
    if subtitle_lang:
        ydl_opts['writesubtitles'] = True
        ydl_opts['subtitleslangs'] = [subtitle_lang]
        ydl_opts['writeautomaticsub'] = True
    
    title = clean_id
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        title = info.get('title', clean_id)
        
    video_path = None
    subtitle_path = None
    
    for f in os.listdir(output_dir):
        if f.startswith(clean_id + ".") and not f.startswith(clean_id + "_") and not f.endswith(".vtt"):
            video_path = os.path.join(output_dir, f)
            
        if subtitle_lang and f.startswith(clean_id + ".") and f.endswith(".vtt") and subtitle_lang in f:
            subtitle_path = os.path.join(output_dir, f)
            
    if subtitle_lang and not subtitle_path:
        for f in os.listdir(output_dir):
            if f.startswith(clean_id + ".") and f.endswith(".vtt"):
                subtitle_path = os.path.join(output_dir, f)
                break
                
    if not video_path:
        raise Exception(f"Falha ao localizar o arquivo baixado para {clean_id}")
        
    return video_path, title, subtitle_path

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Baixar vídeo do YouTube diretamente pelo terminal.")
    parser.add_argument("url", help="URL do vídeo ou ID do YouTube")
    parser.add_argument("--dir", default="downloads", help="Diretório de destino (padrão: downloads)")
    parser.add_argument("--sub", default=None, help="Idioma da legenda (ex: pt, en)")
    parser.add_argument("--quality", default="best", choices=["best", "360p", "1080p"], help="Qualidade do vídeo (padrão: best)")
    
    args = parser.parse_args()
    v_path, v_title, s_path = download_youtube_video(args.url, output_dir=args.dir, subtitle_lang=args.sub, quality=args.quality)
    print(f"\n[Sucesso]")
    print(f"Título: {v_title}")
    print(f"Vídeo salvo em: {v_path}")
    if s_path:
        print(f"Legenda salva em: {s_path}")
