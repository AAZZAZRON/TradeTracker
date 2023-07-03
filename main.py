import bot
from flask import Flask
import threading

app = Flask(__name__)


@app.route('/', methods=['GET'])
def handle_get_request():
  return "Success"


def run():
  app.run(host='0.0.0.0', port=8000)


if __name__ == '__main__':
  x = threading.Thread(target=run)
  bot.run_discord_bot(x)
