from googletrans import Translator
from bs4 import BeautifulSoup

def detect_and_translate(text, target_language="en"):
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

async def translate_html_content(body):
    try:
        target_language = "en"
        soup = BeautifulSoup(body, "html.parser")
        for tag in soup.find_all(string=True):
            original_text = tag.string
            if original_text and original_text.strip():
                translated_text = detect_and_translate(original_text, target_language)
                tag.string.replace_with(translated_text)
        return {"status": True, "text": str(soup)}
    except Exception as e:
        return {"status": False, "text": str(e)}