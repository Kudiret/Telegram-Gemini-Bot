import asyncio
import logging
from telethon import TelegramClient, events
import requests
import os

logging.basicConfig(level=logging.DEBUG)

api_id = os.getenv('API_ID')
api_hash = os.getenv('API_HASH')
phone_number = os.getenv('PHONE_NUMBER')

GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

client = TelegramClient('session_name', api_id, api_hash)

def get_gemini_response(message: str) -> str:
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"
    headers = {'Content-Type': 'application/json'}
    data = {
        "contents": [{
            "parts": [{"text": message}]
        }]
    }

    response = requests.post(url, json=data, headers=headers)

    if response.status_code == 200:
        try:
            gemini_response = response.json()
            answer = gemini_response['candidates'][0]['content']['parts'][0]['text']
            return answer
        except KeyError:
            return "Ошибка обработки ответа от Gemini."
    else:
        return "Ошибка при получении ответа от Gemini."

@client.on(events.NewMessage(incoming=True))
async def handler(event):
    if event.is_private:
        sender = await event.get_sender()
        message = event.message.text

        gemini_response = get_gemini_response(message)

        await event.reply(gemini_response)

async def main():
    try:
        await client.start(phone_number)
        print("Авторизация прошла успешно!")
        await client.run_until_disconnected()

    except Exception as e:
        print(f"Произошла ошибка: {e}")

if __name__ == '__main__':
    asyncio.run(main())
