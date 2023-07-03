import bot
from flask import Flask

app = Flask(__name__)


@app.route('/', methods=['GET'])
def handle_get_request():
  return "Success"


if __name__ == '__main__':
  bot.run_discord_bot()
  app.run(host='0.0.0.0', port=8000)
