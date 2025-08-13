# config.py

DEFAULT_CONFIGS = {
    # Server settings
    "PORT": 5050,
    "SUBSCRIPTION_KEY": 'your_subscription_key_here',  # Fallback Ocp-Apim-Subscription-Key

    # TTS settings
    "DEFAULT_VOICE": 'en-US-AvaNeural',
    "DEFAULT_RESPONSE_FORMAT": 'mp3',
    "DEFAULT_SPEED": 1.0,
    "DEFAULT_LANGUAGE": 'en-US',

    # Feature flags
    "REQUIRE_API_KEY": True,
    "REMOVE_FILTER": False,
    "DETAILED_ERROR_LOGGING": True,
}

