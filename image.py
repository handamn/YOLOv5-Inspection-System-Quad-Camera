import os
import time
import csv
from flask import Flask, render_template, request, jsonify
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from flask import send_from_directory


app = Flask(__name__)
image_folder = '/home/engser/YOLO/yolov5_research2/gambar3'  # Ganti dengan path folder gambar Anda
app.config['UPLOAD_FOLDER'] = image_folder
app.config['LATEST_IMAGE_X'] = ''
app.config['LATEST_IMAGE_Y'] = ''
app.config['LATEST_IMAGE_Z'] = ''
app.config['DISPLAY_IMAGES'] = {'x': True, 'y': True, 'z': True}
app.config['CSV_FILE_PATH'] = 'baca_file_ini.csv'
app.config['CSV_FILE_LAST_MODIFIED'] = 0
app.config['SELECTED_IMAGES'] = {'x': 'a1.jpg', 'y': 'b1.jpg', 'z': 'c1.jpg'}


class ImageHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory:
            return
        filename, extension = os.path.splitext(event.src_path)
        if extension.lower() in ['.jpg', '.jpeg', '.png', '.gif']:
            if 'X' in os.path.basename(event.src_path):
                app.config['LATEST_IMAGE_X'] = os.path.basename(event.src_path)
                app.config['DISPLAY_IMAGES']['x'] = True
            if 'Y' in os.path.basename(event.src_path):
                app.config['LATEST_IMAGE_Y'] = os.path.basename(event.src_path)
                app.config['DISPLAY_IMAGES']['y'] = True
            if 'Z' in os.path.basename(event.src_path):
                app.config['LATEST_IMAGE_Z'] = os.path.basename(event.src_path)
                app.config['DISPLAY_IMAGES']['z'] = True

    def on_modified(self, event):
        if event.is_directory or event.src_path != app.config['CSV_FILE_PATH']:
            return

        file_modified_time = os.path.getmtime(app.config['CSV_FILE_PATH'])
        if file_modified_time > app.config['CSV_FILE_LAST_MODIFIED']:
            app.config['CSV_FILE_LAST_MODIFIED'] = file_modified_time
            reset_images()


def get_latest_images():
    latest_image_x = app.config.get('LATEST_IMAGE_X', '')
    latest_image_y = app.config.get('LATEST_IMAGE_Y', '')
    latest_image_z = app.config.get('LATEST_IMAGE_Z', '')
    return latest_image_x, latest_image_y, latest_image_z


def reset_images():
    app.config['DISPLAY_IMAGES'] = {'x': False, 'y': False, 'z': False}


def check_csv_changes():
    csv_file_path = app.config['CSV_FILE_PATH']
    last_modified = app.config['CSV_FILE_LAST_MODIFIED']
    file_modified_time = os.path.getmtime(csv_file_path)

    if file_modified_time > last_modified:
        app.config['CSV_FILE_LAST_MODIFIED'] = file_modified_time
        reset_images()


@app.route('/')
def index():
    return render_template('index4.html')


@app.route('/latest_images')
def latest_images():
    check_csv_changes()
    latest_image_x, latest_image_y, latest_image_z = get_latest_images()
    display_images = app.config.get('DISPLAY_IMAGES', {'x': False, 'y': False, 'z': False})
    return jsonify({'image_x': latest_image_x, 'image_y': latest_image_y, 'image_z': latest_image_z, 'display_images': display_images})


@app.route('/select_image', methods=['POST'])
def select_image():
    selected_image = request.form.get('selected_image', '')
    if selected_image and selected_image in ['x', 'y', 'z']:
        app.config['SELECTED_IMAGES'][selected_image] = selected_image
        return jsonify({'success': True})
    return jsonify({'success': False})


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


if __name__ == '__main__':
    event_handler = ImageHandler()
    observer = Observer()
    observer.schedule(event_handler, path=image_folder, recursive=False)
    observer.start()
    app.run(debug=True, port=9000)
