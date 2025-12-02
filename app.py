from flask import Flask, request, jsonify
from flask_cors import CORS
import yt_dlp

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return "API Downloader V9 (Anti-Bot Edition) is running!"

@app.route('/get-link', methods=['POST'])
def get_link():
    # Gestion JSON ou Form Data
    if request.is_json:
        data = request.get_json()
        url = data.get('url')
    else:
        url = request.form.get('url')

    if not url:
        return jsonify({'error': 'Pas d\'URL fournie'}), 400

    # OPTIONS ANTI-BOT PUISSANTES
    ydl_opts = {
        'format': 'best',
        'quiet': True,
        'no_warnings': True,
        'noplaylist': True,
        # C'est ici que la magie opère :
        'extractor_args': {
            'youtube': {
                'player_client': ['android', 'ios'], # On se fait passer pour un mobile
                'player_skip': ['webpage', 'configs', 'js'], # On saute les étapes inutiles qui déclenchent les bots
            }
        },
        # Forcer l'IPv4 car l'IPv6 de Render est souvent bloquée par YT
        'source_address': '0.0.0.0', 
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # On extrait les infos sans télécharger
            info = ydl.extract_info(url, download=False)
            
            return jsonify({
                'status': 'success',
                'title': info.get('title', 'Vidéo'),
                'url': info.get('url'), # Le lien direct vidéo
                'thumbnail': info.get('thumbnail'),
                'server': 'Render-Bypass'
            })

    except Exception as e:
        # On renvoie l'erreur exacte pour debug
        return jsonify({'status': 'error', 'text': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
