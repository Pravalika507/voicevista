import requests

OPENROUTER_API_KEY = "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"

def get_chatbot_response(message):
    url = "https://openrouter.ai/api/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "openai/gpt-3.5-turbo",
        "messages": [
            {"role": "user", "content": message}
        ]
    }

    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 200:
        reply = response.json()['choices'][0]['message']['content']
        return reply
    else:
        return "Chatbot is unavailable. Please try later."
