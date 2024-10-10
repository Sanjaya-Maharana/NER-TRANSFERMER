import requests

url = 'https://aiml.azurewebsites.net/translate'

local = "http://127.0.0.1:8000/translate"

def api_post(text):
    response = requests.post(url, json={"text": text})
    if response.status_code == 200:
        return response.json()
    else:
        return response.text

print(api_post('''

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Multilingual Test Page</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #f0f0f0;
            margin: 0;
            padding: 0;
            line-height: 1.6;
        }

        h1 {
            text-align: center;
            color: #333;
            background-color: #4CAF50;
            padding: 20px;
            margin-bottom: 20px;
            color: white;
        }

        h2 {
            color: #4CAF50;
            margin-left: 20px;
        }

        p {
            margin-left: 40px;
            font-size: 18px;
            color: #555;
        }

        .language-section {
            background-color: white;
            margin: 20px;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
        }

        footer {
            text-align: center;
            padding: 20px;
            background-color: #333;
            color: white;
            position: fixed;
            width: 100%;
            bottom: 0;
        }
    </style>
</head>
<body>

    <h1>Test HTML with Multiple Languages</h1>

    <div class="language-section">
        <h2>Hindi (हिन्दी)</h2>
        <p>नमस्ते, यह एक परीक्षण पृष्ठ है।</p>
    </div>

    <div class="language-section">
        <h2>Telugu (తెలుగు)</h2>
        <p>హలో, ఇది ఒక పరీక్షా పేజీ.</p>
    </div>

    <div class="language-section">
        <h2>Chinese (中文)</h2>
        <p>你好，这是一个测试页面。</p>
    </div>

    <div class="language-section">
        <h2>Spanish (Español)</h2>
        <p>Hola, esta es una página de prueba.</p>
    </div>

    <footer>
        © 2024 Multilingual Test Page
    </footer>

</body>
</html>


'''))