# Azure Voices API Wrapper

This project exposes Microsoft Edge's free text-to-speech service with endpoints that follow the Microsoft Azure voices API standard.

## Features

- **Azure-Compatible Endpoints**
  - `POST /cognitiveservices/v1` for text-to-speech using SSML.
  - `GET /cognitiveservices/voices/list` to retrieve available voices.
  - `POST /sts/v1.0/issueToken` to exchange an API key for a short‑lived bearer token.
- **Multiple Audio Formats** – Specify the desired format using the `X-Microsoft-OutputFormat` header (mp3, wav, flac, opus, aac).
- **Runs with Python** – No Docker required. Uses the `edge-tts` library under the hood.

## Setup

### Prerequisites

- Python 3.8+
- `ffmpeg` (optional, required for formats other than mp3)

### Installation

```bash
git clone <repository>
cd az-edge-tts
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Create a `.env` file in the project root:

```env
API_KEY=your_api_key_here
PORT=5050

DEFAULT_VOICE=en-US-AvaNeural
DEFAULT_RESPONSE_FORMAT=mp3
DEFAULT_SPEED=1.0
DEFAULT_LANGUAGE=en-US

REQUIRE_API_KEY=True
REMOVE_FILTER=False
DETAILED_ERROR_LOGGING=True
```

Run the server:

```bash
python app/server.py
```

## Usage

### Retrieve an Access Token

```bash
TOKEN=$(curl -s -X POST \
  -H "Ocp-Apim-Subscription-Key: YOUR_KEY" \
  http://localhost:5050/sts/v1.0/issueToken)
```

### List Voices

```bash
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:5050/cognitiveservices/voices/list
```

### Text to Speech

```bash
curl -X POST "http://localhost:5050/cognitiveservices/v1" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/ssml+xml" \
  -H "X-Microsoft-OutputFormat: audio-24khz-48kbitrate-mono-mp3" \
  -d '<speak version="1.0" xml:lang="en-US"><voice name="en-US-AvaNeural">Hello from Azure compatible API</voice></speak>' \
  --output speech.mp3
```

## License

MIT

