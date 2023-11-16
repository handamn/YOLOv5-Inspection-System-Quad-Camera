import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import csv
from flask import Flask, render_template, jsonify, Response
import io
import cv2
import numpy as np
from PIL import Image
import torch
from obswebsocket import obsws, requests
from obswebsocket.exceptions import ConnectionFailure



app = Flask(__name__)

password = "XD9RjF4blgdS9E3f"

ws = obsws('localhost', 4455, password)
ws.connect()

scenes = ws.call(requests.GetSceneList())
list_scene = scenes.getScenes()


# YOLOv5 Model
model = torch.hub.load('.', 'custom', 'best.pt', source='local',force_reload=True)
#model = torch.hub.load("ultralytics/yolov5", "yolov5s", pretrained=True)
#model = torch.hub.load("ultralytics/yolov5", "custom", path="./best.pt", force_reload=True)
#model = torch.hub.load("/home/engser/YOLO/yolov5/yolov5fish/", "custom", path="best.pt", force_reload=True, source="local")
model.conf = 0.6
model.iou = 0.45


#model = kumpulan_model.FL_X_3_ABD
#model2 = kumpulan_model.FL_X_4_ABCD
#model3 = kumpulan_model.FL_X_6_ABCDEF
#model4 = kumpulan_model.FL_Y_0_BLANK
#model5 = kumpulan_model.FL_Y_2_AB
#model6 = kumpulan_model.FL_Y_3_ABC


# Global variable to store the latest data
latest_data = None
data_seq = None
data_car = None
data_camera = None


class FileChangeHandler(FileSystemEventHandler):
    def __init__(self, filename, data_handler):
        self.filename = filename
        self.data_handler = data_handler

    def on_modified(self, event):
        if not event.is_directory and event.src_path.endswith(self.filename):
            self.read_data_from_csv()

    def read_data_from_csv(self):
        with open(self.filename, 'r') as file:
            reader = csv.reader(file)
            data = list(reader)

            if data:
                row = data[-1]
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
                self.data_handler(sequence, nomor_body, vin_no, car, steer, suffix, Kode_relay, Box_X, Box_Y, Box_Z)
                
                # Cetak nilai sequence di luar fungsi handle_data
                print("Sequence:", sequence)
                
                # Cetak data saat diperbarui di luar fungsi handle_data
                print("Data diperbarui:")
                print("Sequence:", sequence)
                print("Nomor Body:", nomor_body)
                print("VIN No:", vin_no)
                print("Car:", car)
                print("Steer:", steer)
                print("Suffix:", suffix)
                print("Kode Relay:", Kode_relay)
                print("Box X:", Box_X)
                print("Box Y:", Box_Y)
                print("Box Z:", Box_Z)

def gen(camera):

    while True:
        success, frame = camera.read()
        
        if success:
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()

            img = Image.open(io.BytesIO(frame))
            results = model(img, size=640)
            df = results.pandas().xyxy[0]['name']
            print(df)
            #print(results.pandas())

            img = np.squeeze(results.render())  # RGB
            img_BGR = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)  # BGR

            frame = cv2.imencode('.jpg', img_BGR)[1].tobytes()

            yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

        else:
            break


def handle_data(sequence, nomor_body, vin_no, car, steer, suffix, Kode_relay, Box_X, Box_Y, Box_Z):
    global latest_data
    latest_data = {
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

def handle_sequence(sequence, nomor_body, vin_no, car, steer, suffix, Kode_relay, Box_X, Box_Y, Box_Z):
    global data_seq
    data_seq = {
        'sequence2' : sequence
    }

def handle_car(sequence, nomor_body, vin_no, car, steer, suffix, Kode_relay, Box_X, Box_Y, Box_Z):
    global data_car
    data_car = {
        'car2' : car
    }
    return data_car

def command(sequence, nomor_body, vin_no, car, steer, suffix, Kode_relay, Box_X, Box_Y, Box_Z):
    global data_camera
    if car == "Fortuner":
        if steer == "LHD":
            ws.call(requests.SetCurrentProgramScene(sceneName=list_scene[2]['sceneName']))
            data_camera = {
                'camera' : list_scene[2]['sceneName']
            }
            time.sleep(3) #seolah-olah proses

            ws.call(requests.SetCurrentProgramScene(sceneName=list_scene[1]['sceneName']))
            data_camera = {
                'camera' : list_scene[1]['sceneName']
            }
            time.sleep(3) #seolah-olah proses

            ws.call(requests.SetCurrentProgramScene(sceneName=list_scene[3]['sceneName']))
            data_camera = {
                'camera' : list_scene[3]['sceneName']
            }
            time.sleep(3)
        
        else:
            ws.call(requests.SetCurrentProgramScene(sceneName=list_scene[2]['sceneName']))
            data_camera = {
                'camera' : list_scene[2]['sceneName']
            }
            time.sleep(3)

            ws.call(requests.SetCurrentProgramScene(sceneName=list_scene[0]['sceneName']))
            data_camera = {
                'camera' : list_scene[0]['sceneName']
            }
            time.sleep(3)

            ws.call(requests.SetCurrentProgramScene(sceneName =list_scene[1]['sceneName']))
            data_camera = {
                'camera' : list_scene[1]['sceneName']
            }
            time.sleep(3)
    
    else :
        if steer == "LHD":
            ws.call(requests.SetCurrentProgramScene(sceneName=list_scene[2]['sceneName']))
            data_camera = {
                'camera' : list_scene[2]['sceneName']
            }
            time.sleep(3) #seolah-olah proses

            ws.call(requests.SetCurrentProgramScene(sceneName=list_scene[1]['sceneName']))
            data_camera = {
                'camera' : list_scene[1]['sceneName']
            }
            time.sleep(3) #seolah-olah proses

            ws.call(requests.SetCurrentProgramScene(sceneName=list_scene[3]['sceneName']))
            data_camera = {
                'camera' : list_scene[3]['sceneName']
            }
            time.sleep(3)
        
        else:
            ws.call(requests.SetCurrentProgramScene(sceneName=list_scene[2]['sceneName']))
            data_camera = {
                'camera' : list_scene[2]['sceneName']
            }
            time.sleep(3)

            ws.call(requests.SetCurrentProgramScene(sceneName=list_scene[0]['sceneName']))
            data_camera = {
                'camera' : list_scene[0]['sceneName']
            }
            time.sleep(3)

            ws.call(requests.SetCurrentProgramScene(sceneName =list_scene[1]['sceneName']))
            data_camera = {
                'camera' : list_scene[1]['sceneName']
            }
            time.sleep(3)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_data')
def get_data():
    global latest_data
    return jsonify(latest_data)

@app.route('/get_sequence')
def get_sequence():
    global data_seq
    return jsonify(data_seq)

@app.route('/get_car')
def get_car():
    global data_car
    return jsonify(data_car)

@app.route('/get_camera')
def get_camera():
    global data_camera
    return jsonify(data_camera)


@app.route('/video')
def video():
    camera1 = cv2.VideoCapture(0)
    return Response(gen(camera1), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == "__main__":
    event_handler = FileChangeHandler('baca_file_ini.csv', handle_data)
    event_handler2 = FileChangeHandler('baca_file_ini.csv', handle_sequence)
    event_handler3 = FileChangeHandler('baca_file_ini.csv', handle_car)
    event_handler4 = FileChangeHandler('baca_file_ini.csv', command)
    observer = Observer()
    observer.schedule(event_handler, path='.', recursive=False)
    observer.schedule(event_handler2, path='.', recursive=False)
    observer.schedule(event_handler3, path='.', recursive=False)
    observer.schedule(event_handler4, path='.', recursive=False)
    observer.start()

    try:
        app.run()
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
