from flask import Flask, render_template
import os
import json
from datetime import datetime

app = Flask(__name__)

# Path ke folder success
SUCCESS_DIR = 'static/success'  # Sesuaikan dengan path yang benar di dalam container


@app.route('/')
def index():
    results = []

    try:
        files = os.listdir(SUCCESS_DIR)
        files.sort(reverse=True)
        for file in files:
            if file.endswith('.json'):
                with open(os.path.join(SUCCESS_DIR, file), 'r') as f:
                    data = json.load(f)
                    # Ekstrak informasi
                    uuid = file.split('_')[-1].split('.')[0]
                    datetime_str = file.split('_')[0] + ' ' + file.split('_')[1]
                    input_image = data['result']['input']
                    output = data['result']

                    results.append({
                        'id': uuid,
                        'datetime': datetime_str,
                        'service': data['service'].upper(),
                        'input': input_image,
                        'output': output
                    })
    except FileNotFoundError:
        pass

    return render_template('index.html', results=results)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
