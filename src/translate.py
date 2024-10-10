from googletrans import Translator
from bs4 import BeautifulSoup
import asyncio

languages = {
    "english": "en", "mandarin chinese": "zh-cn", "spanish": "es", "hindi": "hi", "arabic": "ar", "bengali": "bn",
    "portuguese": "pt", "russian": "ru", "japanese": "ja", "punjabi": "pa", "german": "de", "french": "fr",
    "turkish": "tr", "korean": "ko", "italian": "it", "vietnamese": "vi", "urdu": "ur", "javanese": "jv",
    "telugu": "te", "marathi": "mr", "tamil": "ta", "persian (farsi)": "fa", "thai": "th", "gujarati": "gu",
    "polish": "pl", "ukrainian": "uk", "dutch": "nl", "romanian": "ro", "greek": "el", "malay": "ms",
    "swahili": "sw", "hebrew": "he", "burmese": "my", "czech": "cs", "amharic": "am", "kannada": "kn",
    "somali": "so", "lao": "lo", "sinhala": "si", "azerbaijani": "az", "serbian": "sr", "hungarian": "hu",
    "pashto": "ps", "kurdish": "ku", "nepali": "ne", "finnish": "fi", "catalan": "ca", "armenian": "hy",
    "malagasy": "mg", "khmer": "km"
}


def detect_and_translate(text, target_language):
    translator = Translator()
    try:
        detected_language = translator.detect(text).lang
        if detected_language != target_language:
            translated_text = translator.translate(text, src=detected_language, dest=target_language).text
            return translated_text
        return text
    except Exception as e:
        print(f"Error during detection/translation: {e}")
        return text

async def translate_html_content(body, target_language):
    try:
        soup = BeautifulSoup(body, "html.parser")
        if target_language.lower() not in languages:
            return {"status": False, "text": f"Unsupported target language: {target_language}"}

        tasks = []
        for tag in soup.find_all(string=True):
            original_text = tag.string
            if original_text and original_text.strip():
                tasks.append(translate_tag(tag, original_text, target_language))

        await asyncio.gather(*tasks)
        return {target_language: str(soup)}
    except Exception as e:
        return {"status": False, "text": str(e)}


async def translate_tag(tag, original_text, target_language):
    target_language = languages[target_language]
    translated_text = detect_and_translate(original_text, target_language)
    tag.string.replace_with(translated_text)

