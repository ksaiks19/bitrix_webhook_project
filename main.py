from flask import Flask, request
import requests
import logging
import os

app = Flask(__name__)
BOT_TOKEN = '8172776735:AAHgW36R-PSfC5sK-xEOfBuwCSCj_HfvkPs'
TELEGRAM_API_URL = f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage'

logging.basicConfig(level=logging.INFO)

@app.route('/', methods=['POST'])
def webhook():
    data = request.json
    logging.info(f"Received data: {data}")

    try:
        # Получаем ID задачи
        task_id = data["data"]["FIELDS"]["TASK_ID"]
        comment_text = data["data"]["FIELDS"]["COMMENT_TEXT"]

        # Получаем подробности задачи через Bitrix REST API
        task_details = get_task_details(task_id)
        if not task_details:
            return "No task found", 404

        # Извлекаем Telegram ID из описания
        description = task_details.get("DESCRIPTION", "")
        telegram_id = extract_telegram_id(description)
        if telegram_id:
            send_telegram_message(telegram_id, f"💬 Новый комментарий к вашей заявке:\n\n{comment_text}")
            return "Message sent", 200
        else:
            return "Telegram ID not found", 400

    except Exception as e:
        logging.error(f"Error: {e}")
        return "Error processing webhook", 500

def get_task_details(task_id):
    BITRIX_TASK_URL = f'https://bitrix24.btrade.kz/rest/16/6wwa4hxk9e79vyvf/task.item.getdata.json'
    response = requests.get(BITRIX_TASK_URL, params={"taskId": task_id})
    data = response.json()
    return data.get("result", {}).get("task", {}) if "result" in data else None

def extract_telegram_id(text):
    import re
    match = re.search(r'ID Telegram: (\d+)', text)
    return match.group(1) if match else None

def send_telegram_message(chat_id, text):
    response = requests.post(TELEGRAM_API_URL, json={
        "chat_id": chat_id,
        "text": text
    })
    logging.info(f"Telegram response: {response.text}")

if __name__ == '__main__':
    app.run(debug=True)
