import os
from typing import Dict
from dotenv import load_dotenv
from app.db.enums import AvailableDialect, AvailableLanguage


# Env Variables
load_dotenv()
VOICE_ID = os.getenv("ELEVEN_LABS_VOICE_ID")


#API URLs
PRONOUNCIATION_BASE_URL = "https://eastus.stt.speech.microsoft.com/speech/recognition/conversation/cognitiveservices/v1"
TTS_BASE_URL = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"


# Resource Maps    
AZURE_LANGUAGE_CODE: Dict[AvailableLanguage, Dict[AvailableDialect, str] | str] = {
    AvailableLanguage.ARABIC: {
        AvailableDialect.MSA: "ar-SA",
        AvailableDialect.LEVANTINE: "ar-SY",
        AvailableDialect.EGYPTIAN: "ar-EG"
    },
    AvailableLanguage.FRENCH: "fr-FR",
    AvailableLanguage.SPANISH: "es-MX"
}

TARGET_IMAGE_NAME: Dict[AvailableLanguage, Dict[str, str]] = {
    AvailableLanguage.ARABIC: {
        "ا": "Alif",
        "ع": "Ayn",
        "ب": "",
        "د": "",
        "ض": "",
        "ذ": "",
        "ف": "",
        "غ": "",
        "ح": "",
        "ه": "",
        "ء": "",
        "ج": "",
        "ك": "",
        "خ": "",
        "ل": "",
        "م": "",
        "ن": "",
        "ق": "",
        "ر": "",
        "ص": "",
        "س": "",
        "ش": "",
        "ط": "",
        "ت": "",
        "ث": "",
        "و": "",
        "ي": "",
        "ظ": "",
        "ز": "",
    }
}