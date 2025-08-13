# server.py

from flask import Flask, request, send_file, jsonify
from gevent.pywsgi import WSGIServer
from dotenv import load_dotenv
import os
import traceback
from xml.etree import ElementTree as ET

from config import DEFAULT_CONFIGS
from handle_text import prepare_tts_input_with_context
from tts_handler import generate_speech, get_voices
from utils import getenv_bool, require_api_key, AUDIO_FORMAT_MIME_TYPES, DETAILED_ERROR_LOGGING

app = Flask(__name__)
load_dotenv()

API_KEY = os.getenv('API_KEY', DEFAULT_CONFIGS["API_KEY"])
PORT = int(os.getenv('PORT', str(DEFAULT_CONFIGS["PORT"])))

DEFAULT_VOICE = os.getenv('DEFAULT_VOICE', DEFAULT_CONFIGS["DEFAULT_VOICE"])
DEFAULT_RESPONSE_FORMAT = os.getenv('DEFAULT_RESPONSE_FORMAT', DEFAULT_CONFIGS["DEFAULT_RESPONSE_FORMAT"])
DEFAULT_SPEED = float(os.getenv('DEFAULT_SPEED', str(DEFAULT_CONFIGS["DEFAULT_SPEED"])))

REMOVE_FILTER = getenv_bool('REMOVE_FILTER', DEFAULT_CONFIGS["REMOVE_FILTER"])


@app.route('/cognitiveservices/v1', methods=['POST'])
@require_api_key
def azure_tts():
    """Endpoint compatible with Microsoft Azure text-to-speech API."""
    try:
        ssml_data = request.data.decode('utf-8')
        if not ssml_data:
            return jsonify({"error": "Missing SSML payload"}), 400

        try:
            root = ET.fromstring(ssml_data)
            voice_node = root.find('.//{http://www.w3.org/2001/10/synthesis}voice')
            if voice_node is None:
                return jsonify({"error": "Invalid SSML payload"}), 400
            text = voice_node.text or ""
            voice = voice_node.get('name', DEFAULT_VOICE)
        except Exception as e:
            return jsonify({"error": f"Invalid SSML payload: {e}"}), 400

        if not REMOVE_FILTER:
            text = prepare_tts_input_with_context(text)

        # Map Azure output format header to local response formats
        output_format_header = request.headers.get(
            'X-Microsoft-OutputFormat', 'audio-24khz-48kbitrate-mono-mp3'
        ).lower()

        if 'wav' in output_format_header:
            response_format = 'wav'
        elif 'flac' in output_format_header:
            response_format = 'flac'
        elif 'opus' in output_format_header or 'ogg' in output_format_header:
            response_format = 'opus'
        elif 'aac' in output_format_header:
            response_format = 'aac'
        else:
            response_format = 'mp3'

        mime_type = AUDIO_FORMAT_MIME_TYPES.get(response_format, 'audio/mpeg')

        speed = DEFAULT_SPEED

        output_file_path = generate_speech(text, voice, response_format, speed)
        return send_file(output_file_path, mimetype=mime_type)

    except Exception as e:
        if DETAILED_ERROR_LOGGING:
            app.logger.error(f"Error in azure_tts: {str(e)}\n{traceback.format_exc()}")
        else:
            app.logger.error(f"Error in azure_tts: {str(e)}")
        return jsonify({"error": "An internal server error occurred", "details": str(e)}), 500


@app.route('/cognitiveservices/voices/list', methods=['GET'])
@require_api_key
def azure_voices_list():
    """Return available voices in Azure format."""
    language = request.args.get('language') or request.args.get('locale')
    voices = get_voices(language if language else None)
    return jsonify(voices)


print("Azure Voices API compatible server")
print(f" * Server running on http://localhost:{PORT}")
print(f" * Voice list: http://localhost:{PORT}/cognitiveservices/voices/list")
print(f" * TTS endpoint: http://localhost:{PORT}/cognitiveservices/v1")

if __name__ == '__main__':
    http_server = WSGIServer(('0.0.0.0', PORT), app)
    http_server.serve_forever()

