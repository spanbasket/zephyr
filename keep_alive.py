from flask import Flask
from threading import Thread

app = Flask('')

@app.route('/')
def home():
    return "Zephyr is online and running!"

def run():
    app.run(host='0.0.0.0', port=7860)

def keep_alive():
    t = Thread(target=run)
    t.start()