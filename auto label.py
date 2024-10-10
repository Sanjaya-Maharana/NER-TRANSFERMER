import time
import traceback
import openai

openai.api_type = "azure"
openai.api_base = "https://extractinfo.openai.azure.com/"
openai.api_version = "2023-07-01-preview"
openai.api_key = "30363b3002684528a6af160e7cb7ae31"

def openai_fun(url):
    try:
        response = openai.ChatCompletion.create(
            engine="gpt-4o",
            messages = [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Extract license plate Number from this image?"},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": url,
                            },
                        }
                    ],
                },
            ],
            temperature=0.2,
            top_p=0.95,
            frequency_penalty=0,
            presence_penalty=0,
            stop=None
        )

        if response and "choices" in response and response["choices"]:
            summary = response["choices"][0]["message"]["content"]
            return summary
        else:
            return None
    except Exception as e:
        print(traceback.print_exc())
        print(f"Error: {e}")
        return None


print(openai_fun("https://acko-cms.ackoassets.com/fancy_number_plate_bfbc501f34.jpg"))