from flask import Flask, request, jsonify
from flask_cors import CORS
import yt_dlp

app = Flask(__name__)
# Ceci permet à ton site InfinityFree de parler à ce serveur Render
CORS(app) 

@app.route('/')
def home():
    return "L'API Downloader est en ligne et fonctionnelle ! V7"

@app.route('/api/process', methods=['POST'])
def process_video():
    try:
        # Récupérer les données envoyées par ton site
        content = request.json
        url = content.get('url')
        mode = content.get('mode', 'auto')

        if not url:
            return jsonify({'status': 'error', 'text': 'URL manquante'}), 400

        # Configuration de yt-dlp pour ne pas télécharger mais juste extraire le lien
        ydl_opts = {
            'format': 'bestaudio/best' if mode == 'audio' else 'best',
            'quiet': True,
            'no_warnings': True,
            'noplaylist': True,
        }

        # Extraction des infos
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            # Récupération du lien direct
            download_url = info.get('url')
            title = info.get('title', 'Vidéo sans titre')
            
            return jsonify({
                'status': 'success',
                'url': download_url,
                'title': title,
                'server': 'Render-Python'
            })

    except Exception as e:
        return jsonify({'status': 'error', 'text': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)