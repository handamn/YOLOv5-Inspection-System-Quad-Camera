import os
import csv
from flask import Flask, render_template, jsonify
from flask_cors import CORS
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

app = Flask(__name__)
CORS(app)

# Mendapatkan daftar nama file gambar dari folder "gambar3" dan mengurutkannya secara alfabetis
image_folder = "static/gambar3"
image_files = sorted([f for f in os.listdir(image_folder) if os.path.isfile(os.path.join(image_folder, f))])

# Menghitung jumlah gambar
num_images = len(image_files)

# Menginisialisasi variabel index gambar
current_image_index = 0

# Fungsi untuk membaca data dari file CSV
def read_csv_data():
    csv_file = "baca_file_ini.csv"

    with open(csv_file, "r") as file:
        csv_reader = csv.reader(file)
        for row in csv_reader:
            data = row[0]  # Anggap data berada di kolom pertama (index 0)
            return data

# Fungsi untuk mengubah gambar
def change_image():
    global current_image_index
    current_image_index = (current_image_index + 1) % num_images

# Watchdog event handler
class FileChangeHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.src_path == "./baca_file_ini.csv":
            data = read_csv_data()
            if data is not None:
                change_image()

# Membuat objek Observer dan menghubungkannya dengan event handler
observer = Observer()
event_handler = FileChangeHandler()
observer.schedule(event_handler, path="./", recursive=False)
observer.start()

@app.route("/")
def index():
    # Mendapatkan nama file gambar saat ini
    current_image = image_files[current_image_index]

    # Mengirimkan nama file gambar ke template HTML
    return render_template("index5.html", image_path="gambar3/" + current_image)

@app.route("/update_image", methods=["GET"])
def update_image():
    # Mendapatkan nama file gambar saat ini
    current_image = image_files[current_image_index]

    # Mengirimkan nama file gambar dalam bentuk JSON
    return jsonify({"image_path": "gambar3/" + current_image})


if __name__ == "__main__":
    app.run(debug=True, port=9000)
    observer.stop()
    observer.join()


