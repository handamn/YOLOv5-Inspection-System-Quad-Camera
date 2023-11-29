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
    
    # Mengganti nama gambar terbaru dengan gambar yang sudah ditentukan
    if latest_image_x in ['0_BLANK(822).jpg', '3_ABC(48).jpg']:
        latest_image_x = '0_BLANK(822).jpg'
    if latest_image_y in ['3_ABC(48).jpg', '4_ABCD(1).jpg']:
        latest_image_y = '3_ABC(48).jpg'
    if latest_image_z in ['4_ABCD(1).jpg', '0_BLANK(822).jpg']:
        latest_image_z = '4_ABCD(1).jpg'
    
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
    return render_template('index3.html')

@app.route('/latest_images')
def latest_images():
    check_csv_changes()
    latest_image_x, latest_image_y, latest_image_z = get_latest_images()
    display_images = app.config.get('DISPLAY_IMAGES', {'x': False, 'y': False, 'z': False})
    return jsonify({'image_x': latest_image_x, 'image_y': latest_image_y, 'image_z': latest_image_z, 'display_images': display_images})

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    event_handler = ImageHandler()
    observer = Observer()
    observer.schedule(event_handler, path=image_folder, recursive=False)
    observer.start()
    app.run(debug=True, port=9000)
