import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import csv
from flask import Flask, render_template, jsonify

app = Flask(__name__)

class FileChangeHandler(FileSystemEventHandler):
    def __init__(self, filename, data_handler):
        self.filename = filename
        self.data_handler = data_handler
        self.data_terakhir = None

    def on_modified(self, event):
        if not event.is_directory and event.src_path.endswith(self.filename):
            start_time = time.time()  # Waktu awal
            with open(self.filename, 'r') as file:
                reader = csv.reader(file)
                data = list(reader)

                if data != self.data_terakhir:
                    self.data_terakhir = data
                    for row in data:
                        sequence = row[0]
                        nomor_body = row[1]
                        vin_no = row[2]
                        car = row[3]
                        steer = row[4]
                        suffix = row[5]
                        Kode_relay = row[6]
                        Box_X = row[7]
                        Box_Y = row[8]
                        Box_Z = row[9]

                        self.data_handler(sequence, nomor_body, vin_no, car, steer, suffix, Kode_relay, Box_X, Box_Y, Box_Z)  # Durasi loop

def baca_data_terbaru(nama_file, data_handler):
    event_handler = FileChangeHandler(nama_file, data_handler)
    observer = Observer()
    observer.schedule(event_handler, path='.', recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

def handle_data(sequence, nomor_body, vin_no, car, steer, suffix, Kode_relay, Box_X, Box_Y, Box_Z):
    data = {
        'sequence': sequence,
        'nomor_body': nomor_body,
        'vin_no': vin_no,
        'car': car,
        'steer': steer,
        'suffix': suffix,
        'Kode_relay': Kode_relay,
        'Box_X': Box_X,
        'Box_Y': Box_Y,
        'Box_Z': Box_Z
    }
    return data

@app.route('/')
def show_data():
    return render_template('index.html')

@app.route('/get_data')
def get_data():
    with open('baca_file_ini.csv', 'r') as file:
        reader = csv.reader(file)
        data = list(reader)
        if data:
            row = data[-1]  # Ambil baris terakhir
            sequence = row[0]
            nomor_body = row[1]
            vin_no = row[2]
            car = row[3]
            steer = row[4]
            suffix = row[5]
            Kode_relay = row[6]
            Box_X = row[7]
            Box_Y = row[8]
            Box_Z = row[9]
            data = handle_data(sequence, nomor_body, vin_no, car, steer, suffix, Kode_relay, Box_X, Box_Y, Box_Z)
            return jsonify(data)
    return jsonify(None)

if __name__ == "__main__":
    app.run()