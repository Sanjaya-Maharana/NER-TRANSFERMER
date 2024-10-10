import asyncio
from googletrans import Translator
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor

languages = {
    "english": "en", "mandarin chinese": "zh-cn", "spanish": "es", "hindi": "hi", "arabic": "ar", "bengali": "bn",
    "portuguese": "pt", "russian": "ru", "japanese": "ja", "punjabi": "pa", "german": "de", "french": "fr",
    "turkish": "tr", "korean": "ko", "italian": "it", "vietnamese": "vi", "urdu": "ur", "javanese": "jv",
    "telugu": "te", "marathi": "mr", "tamil": "ta", "persian (farsi)": "fa", "thai": "th", "gujarati": "gu",
    "polish": "pl", "ukrainian": "uk", "dutch": "nl", "romanian": "ro", "greek": "el", "malay": "ms",
    "swahili": "sw", "hebrew": "he", "burmese": "my", "czech": "cs", "amharic": "am", "kannada": "kn",
    "somali": "so", "lao": "lo", "sinhala": "si", "azerbaijani": "az", "serbian": "sr", "hungarian": "hu",
    "pashto": "ps", "kurdish": "ku", "nepali": "ne", "finnish": "fi", "catalan": "ca", "armenian": "hy",
    "malagasy": "mg", "khmer": "km", 'odia':'or'
}


def detect_and_translate(text, target_language_code):
    """Detect the language and translate the text if needed."""
    translator = Translator()
    try:
        detected_language = translator.detect(text).lang
        if detected_language != target_language_code:
            translated_text = translator.translate(text, src=detected_language, dest=target_language_code).text
            return translated_text
        return text
    except Exception as e:
        print(f"Error during detection/translation: {e}")
        return text


async def translate_tag(tag, original_text, target_language_code):
    """Wrapper to translate the text of the tag asynchronously."""
    loop = asyncio.get_event_loop()
    with ThreadPoolExecutor() as pool:
        translated_text = await loop.run_in_executor(pool, detect_and_translate, original_text, target_language_code)
        tag.string.replace_with(translated_text)


async def translate_html_content(body, target_language):
    """Translate the HTML content to the target language asynchronously."""
    try:
        soup = BeautifulSoup(body, "html.parser")
        if target_language.lower() not in languages:
            return {"status": False, "text": f"Unsupported target language: {target_language}"}
        target_language_code = languages[target_language.lower()]
        tasks = []
        for tag in soup.find_all(string=True):
            original_text = tag.string
            if original_text and original_text.strip():
                tasks.append(translate_tag(tag, original_text, target_language_code))
        await asyncio.gather(*tasks)

        return {"status": True, "text": str(soup)}

    except Exception as e:
        return {"status": False, "text": str(e)}


# Example usage of the asynchronous translation function
async def main():
    html_body = """
    <html>
        <head><title>Test Page</title></head>
        <body>
            <h1>This is a test heading</h1>
            <p>This is a test paragraph. It should be translated.</p>
        </body>
    </html>
    """

    translated_html = await translate_html_content(html_body, "odia")
    print(translated_html["text"])

# # Running the async translation
# asyncio.run(main())
