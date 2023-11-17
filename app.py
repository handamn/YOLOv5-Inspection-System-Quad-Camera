from flask import Flask, jsonify, render_template
import random
import time

app = Flask(__name__)

def generate_data():
    while True:
        # Generate random data
        data = {
            'value': random.randint(1, 100),
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
        }
        yield data
        time.sleep(5)

@app.route('/')
def index():
    return render_template('index2.html')

@app.route('/data')
def get_data():
    return jsonify(next(generate_data()))

if __name__ == '__main__':
    app.run()
