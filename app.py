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
import pandas as pd

camera1 = cv2.VideoCapture(0)

app = Flask(__name__)

password = "XD9RjF4blgdS9E3f"

ws = obsws('localhost', 4455, password)
ws.connect()

scenes = ws.call(requests.GetSceneList())
list_scene = scenes.getScenes()

path_model ="/home/engser/YOLO/yolov5_research2/model_custom/"



# Global variable to store the latest data
data_acuan = pd.Series(np.array([1]))

latest_data = None
data_seq = None
data_car = None
data_camera = None
data_steer = None
data_box_X = None
data_box_Y = None
data_box_Z = None



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

def handle_steer(sequence, nomor_body, vin_no, car, steer, suffix, Kode_relay, Box_X, Box_Y, Box_Z):
    global data_steer
    data_steer = {
        'steer2' : steer
    }
    return data_steer

def handle_box_X(sequence, nomor_body, vin_no, car, steer, suffix, Kode_relay, Box_X, Box_Y, Box_Z):
    global data_box_X
    data_box_X = {
        'box_X2' : Box_X
    }

#model3 = handle_box_X(sequence, nomor_body, vin_no, car, steer, suffix, Kode_relay, Box_X, Box_Y, Box_Z)


def handle_box_Y(sequence, nomor_body, vin_no, car, steer, suffix, Kode_relay, Box_X, Box_Y, Box_Z):
    global data_box_Y
    data_box_Y = {
        'box_Y2' : Box_Y
    }
    

def handle_box_Z(sequence, nomor_body, vin_no, car, steer, suffix, Kode_relay, Box_X, Box_Y, Box_Z):
    global data_box_Z
    data_box_Z = {
        'box_Z2' : Box_Z
    }
    time.sleep(3)
    data_box_Z = {
        'box_Z2' : Box_Y
    }
    time.sleep(3)
    data_box_Z = {
        'box_Z2' : Box_X
    }
    time.sleep(3)



def custom_model():
    a = get_box_X2()
    model2 = torch.hub.load('.', 'custom', path_model + 'Fortuner_LHD/Box1/'+a+'/train1/weights/best.pt', source='local',force_reload=True)
    return model2
    



def draw_horizontal_lines(image, height1, height2):
    cv2.line(image, (0, height1), (image.shape[1], height1), (0, 0, 255), 2)
    cv2.line(image, (0, height2), (image.shape[1], height2), (0, 0, 255), 2)
    return image

def gen(camera):
    model = custom_model()
    df_array = [] # Array untuk menyimpan hasil df

    while True:
        success, frame = camera.read()

        if success:
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()

            img = Image.open(io.BytesIO(frame))
            results = model(img, size=640)

            if results.pandas().xyxy[0]['ymin'].shape == data_acuan.shape:
                ymin = results.pandas().xyxy[0]['ymin'][0]
                ymax = results.pandas().xyxy[0]['ymax'][0]

                if ymin < 100 or ymax > 400:
                    img = np.array(img)  # RGB
                    img_BGR = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)  # BGR

                    # Gambar garis horizontal
                    img_BGR = draw_horizontal_lines(img_BGR, 100, 400)

                    frame = cv2.imencode('.jpg', img_BGR)[1].tobytes()

                    print("BELUM TERDETEKSI")

                    yield(b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

                else:
                    df = results.pandas().xyxy[0]['name']
                    ef = df.to_string()
                    print(ef)

                    df_array.append(ef)

                    nilai_unik = list(set(df_array))
                    print(len(df_array))  # Menyimpan hasil df dalam array
                    print("==============")
                    img = np.squeeze(results.render())  # RGB
                    img_BGR = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)  # BGR

                    # Gambar garis horizontal
                    img_BGR = draw_horizontal_lines(img_BGR, 100, 400)

                    frame = cv2.imencode('.jpg', img_BGR)[1].tobytes()

                    yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

                    # Perhitungan jika ada nilai yang sama sebanyak 500

                    if ef != "NG":
                        if df_array.count(ef) > 100:
                            break

            else:
                ymin = 0
                ymax = 0

                img = np.array(img)  # RGB
                img_BGR = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)  # BGR

                # Gambar garis horizontal
                img_BGR = draw_horizontal_lines(img_BGR, 100, 400)

                frame = cv2.imencode('.jpg', img_BGR)[1].tobytes()

                print("BELUM TERDETEKSI")

                yield(b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

        else:
            break




"""
def command(sequence, nomor_body, vin_no, car, steer, suffix, Kode_relay, Box_X, Box_Y, Box_Z):
    global data_camera
    if car == "Fortuner":
        if steer == "LHD":
            #ws.call(requests.SetCurrentProgramScene(sceneName=list_scene[0]['sceneName']))
            data_camera = {
                'camera' : list_scene[0]['sceneName']
            }
            
            time.sleep(9) #seolah-olah proses

            #ws.call(requests.SetCurrentProgramScene(sceneName=list_scene[1]['sceneName']))
            data_camera = {
                'camera' : list_scene[1]['sceneName']
            }
            time.sleep(9) #seolah-olah proses

            #ws.call(requests.SetCurrentProgramScene(sceneName=list_scene[2]['sceneName']))
            data_camera = {
                'camera' : list_scene[2]['sceneName']
            }
            time.sleep(9)
        
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
"""



def generate_frames():
    cameraa = camera1
    global data_car
    global data_steer
    global data_box_X
    global data_box_Y
    global data_box_Z
    global data_seq

    while True:

        start_time1 = time.time()
        previous_data_seq = data_seq

        ws.call(requests.SetCurrentProgramScene(sceneName=list_scene[0]['sceneName']))
        for frame in gen(cameraa):
            yield frame

            a = get_box_X2()
            print(a)

            current_time = time.time()
            elapsed_time = current_time - start_time1

            if data_seq != previous_data_seq:
                break

    
def get_box_X2():
    global data_box_X
    a = data_box_X
    a = str(data_box_X)
    a = a.strip("{}")
    a = a.split(":")[1]
    a = a.strip().strip("'")
    return a
    

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

@app.route('/get_steer')
def get_steer():
    global data_steer
    return jsonify(data_steer)
    
@app.route('/get_box_X')
def get_box_X():
    global data_box_X
    return jsonify(data_box_X)

@app.route('/get_box_Y')
def get_box_Y():
    global data_box_Y
    return jsonify(data_box_Y)

@app.route('/get_box_Z')
def get_box_Z():
    global data_box_Z
    return jsonify(data_box_Z)

@app.route('/get_camera')
def get_camera():
    global data_camera
    return jsonify(data_camera)





@app.route('/video')
def video():
    """
    def generate_frames():
        cameraa = camera1
        for frame in gen(cameraa):
            yield frame
"""
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == "__main__":
    event_handler = FileChangeHandler('baca_file_ini.csv', handle_data)
    event_handler2 = FileChangeHandler('baca_file_ini.csv', handle_sequence)
    event_handler3 = FileChangeHandler('baca_file_ini.csv', handle_car)
    #event_handler4 = FileChangeHandler('baca_file_ini.csv', command)
    event_handler5 = FileChangeHandler('baca_file_ini.csv', handle_steer)
    event_handler6 = FileChangeHandler('baca_file_ini.csv', handle_box_X)
    event_handler7 = FileChangeHandler('baca_file_ini.csv', handle_box_Y)
    event_handler8 = FileChangeHandler('baca_file_ini.csv', handle_box_Z)


    observer = Observer()
    observer.schedule(event_handler, path='.', recursive=False)
    observer.schedule(event_handler2, path='.', recursive=False)
    observer.schedule(event_handler3, path='.', recursive=False)
    #observer.schedule(event_handler4, path='.', recursive=False)
    observer.schedule(event_handler5, path='.', recursive=False)
    observer.schedule(event_handler6, path='.', recursive=False)
    observer.schedule(event_handler7, path='.', recursive=False)
    observer.schedule(event_handler8, path='.', recursive=False)

    observer.start()

    try:
        app.run()
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
