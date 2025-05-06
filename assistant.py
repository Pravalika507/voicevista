import webbrowser
import requests
import json
import threading

# Global flag to control stopping the command
stop_flag = threading.Event()

def set_stop_flag():
    stop_flag.set()

def reset_stop_flag():
    stop_flag.clear()

# Predefined commands with their actions in multiple languages
PREDEFINED_COMMANDS = {
    "youtube": ("https://www.youtube.com", "Opening YouTube"),
    "gmail": ("https://mail.google.com", "Opening Gmail"),
    "telegram": ("https://web.telegram.org", "Opening Telegram"),
    "google": ("https://www.google.com", "Opening Google"),
    "chrome": ("https://www.google.com", "Opening Google Chrome"),
    "whatsapp": ("https://web.whatsapp.com", "Opening WhatsApp"),
    "photos": ("https://photos.google.com", "Opening Google Photos"),
    "यूट्यूब": ("https://www.youtube.com", "YouTube खोल रहा हूँ"),
    "जीमेल": ("https://mail.google.com", "Gmail खोल रहा हूँ"),
    "टेलीग्राम": ("https://web.telegram.org", "Telegram खोल रहा हूँ"),
    "गूगल": ("https://www.google.com", "Google खोल रहा हूँ"),
    "యూట్యూబ్": ("https://www.youtube.com", "YouTube తెరుస్తున్నాను"),
    "జీమెయిల్": ("https://mail.google.com", "Gmail తెరుస్తున్నాను"),
    "టెలిగ్రామ్": ("https://web.telegram.org", "Telegram తెరుస్తున్నాను"),
    "గూగుల్": ("https://www.google.com", "Google తెరుస్తున్నాను"),
    "யூடியூப்": ("https://www.youtube.com", "YouTube திறக்கிறது"),
    "ஜிமெயில்": ("https://mail.google.com", "Gmail திறக்கிறது"),
    "டெலிகிராம்": ("https://web.telegram.org", "Telegram திறக்கிறது"),
    "கூகுள்": ("https://www.google.com", "Google திறக்கிறது")
}

LANGUAGE_KEYWORDS = {
    "english": ["open", "what", "how", "when", "where", "why"],
    "hindi": ["खोलो", "क्या", "कैसे", "कब", "कहाँ", "क्यों"],
    "telugu": ["తెరువు", "ఏమి", "ఎలా", "ఎప్పుడు", "ఎక్కడ", "ఎందుకు"],
    "tamil": ["திற", "என்ன", "எப்படி", "எப்போது", "எங்கே", "ஏன்"]
}

OPENROUTER_API_KEY = "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"
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"

def detect_language(command):
    command_lower = command.lower()
    for lang, keywords in LANGUAGE_KEYWORDS.items():
        for keyword in keywords:
            if keyword.lower() in command_lower:
                return lang
    return "english"

def query_ai(prompt, language="english"):
    if stop_flag.is_set():
        return "Voice command stopped."

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://your-site.com",
        "X-Title": "Voice Assistant"
    }

    language_instructions = {
        "english": "Respond in English.",
        "hindi": "हिंदी में उत्तर दें।",
        "telugu": "తెలుగులో జవాబు ఇవ్వండి.",
        "tamil": "தமிழில் பதிலளிக்கவும்."
    }

    system_message = {
        "role": "system",
        "content": f"You are a helpful voice assistant. {language_instructions.get(language, 'Respond in English.')}"
    }

    payload = {
        "model": "openai/gpt-3.5-turbo",
        "messages": [system_message, {"role": "user", "content": prompt}]
    }

    try:
        response = requests.post(OPENROUTER_API_URL, headers=headers, json=payload, timeout=30)
        if stop_flag.is_set():
            return "Voice command stopped."
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        if stop_flag.is_set():
            return "Voice command stopped."
        error_messages = {
            "english": f"Error: {str(e)}",
            "hindi": f"त्रुटि: {str(e)}",
            "telugu": f"లోపం: {str(e)}",
            "tamil": f"பிழை: {str(e)}"
        }
        return error_messages.get(language, f"Error: {str(e)}")

def process_voice_command(command):
    reset_stop_flag()  # Reset the stop flag at the beginning

    if not command.strip():
        return "Please give a command."
    
    if stop_flag.is_set():
        return "Voice command stopped."

    language = detect_language(command)
    command_lower = command.lower()

    for cmd, (url, response) in PREDEFINED_COMMANDS.items():
        if cmd.lower() in command_lower:
            if stop_flag.is_set():
                return "Voice command stopped."
            webbrowser.open_new_tab(url)
            return response

    question_keywords = [
        "what", "how", "when", "where", "why", "who", 
        "क्या", "कैसे", "कब", "कहाँ", "क्यों", "कौन",
        "ఏమి", "ఎలా", "ఎప్పుడు", "ఎక్కడ", "ఎందుకు", "ఎవరు",
        "என்ன", "எப்படி", "எப்போது", "எங்கே", "ஏன்", "யார்"
    ]

    if any(keyword in command_lower for keyword in question_keywords):
        return query_ai(command, language)

    action_phrases = {
        "english": ["open ", "launch ", "start ", "go to ", "show me ", "take me to "],
        "hindi": ["खोलो ", "शुरू करो ", "दिखाओ ", "ले चलो "],
        "telugu": ["తెరువు ", "ప్రారంభించు ", "చూపించు ", "తీసుకెళ్ళు "],
        "tamil": ["திற ", "தொடங்க ", "காட்டு ", "அழைத்துச் "]
    }

    action_triggered = any(command_lower.startswith(phrase.lower()) for phrases in action_phrases.values() for phrase in phrases)

    if action_triggered:
        target = command.split(maxsplit=1)[1] if len(command.split()) > 1 else ""
        if any(ext in target.lower() for ext in [".com", ".org", ".net", ".io", ".in"]):
            if not target.lower().startswith(("http://", "https://")):
                target = f"https://{target}"
            if stop_flag.is_set():
                return "Voice command stopped."
            try:
                webbrowser.open_new_tab(target)
                responses = {
                    "english": f"Opening {target}",
                    "hindi": f"{target} खोल रहा हूँ",
                    "telugu": f"{target} తెరుస్తున్నాను",
                    "tamil": f"{target} திறக்கிறது"
                }
                return responses.get(language, f"Opening {target}")
            except:
                error_responses = {
                    "english": f"Could not open {target}",
                    "hindi": f"{target} खोल नहीं सका",
                    "telugu": f"{target} తెరవలేకపోయాను",
                    "tamil": f"{target} திறக்க முடியவில்லை"
                }
                return error_responses.get(language, f"Could not open {target}")
        else:
            return query_ai({
                "english": f"I want to {command}. What should I do?",
                "hindi": f"मैं {command} चाहता हूँ। मुझे क्या करना चाहिए?",
                "telugu": f"నేను {command} కోరుకుంటున్నాను. నేను ఏమి చేయాలి?",
                "tamil": f"நான் {command} விரும்புகிறேன். நான் என்ன செய்ய வேண்டும்?"
            }.get(language, f"I want to {command}. What should I do?"), language)

    return query_ai(command, language)
