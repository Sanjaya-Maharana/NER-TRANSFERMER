import openai

openai.api_type = "azure"
openai.api_base = "https://extractinfo.openai.azure.com/"
openai.api_version = "2023-07-01-preview"
openai.api_key = "30363b3002684528a6af160e7cb7ae31"



async def detect_and_translate_html(data):
    text = data['text']
    if not text.strip():
        raise HTTPException(status_code=400, detail="No text provided")
    try:
        response = openai.ChatCompletion.create(
            engine="gpt-35-turbo",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an AI assistant that detects and translates the text to English while preserving the HTML structure. "
                        "Translate any non-English text within the HTML content but ensure the HTML tags remain unchanged."
                        "Response must have only html no other text"
                    )
                },
                {
                    "role": "user",
                    "content": f"Here is the HTML content to translate:\n\n{text}"
                }
            ],
            temperature=0.2,
            top_p=0.95,
            frequency_penalty=0,
            presence_penalty=0,
            stop=None
        )

        if response and "choices" in response and response["choices"]:
            translated_content = response["choices"][0]["message"]["content"]
            return {"translated_text": translated_content}
        else:
            return {"translated_text": text, 'response': response}
    except Exception as e:
        return {"translated_text": text, "error": str(e)}