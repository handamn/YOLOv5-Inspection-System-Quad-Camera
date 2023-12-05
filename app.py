import datetime
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
nilai_ymin = 10
nilai_ymax = 450

kuota_benar = 50
kuota_salah = 50
kuota_belum = 100

latest_data = None
data_seq = None
data_car = None
data_camera = None
data_steer = None
data_box_X = None
data_box_Y = None
data_box_Z = None


reference_box_X = None
actual_box_X = None
status_box_X = None

reference_box_Y = None
actual_box_Y = None
status_box_Y = None

reference_box_Z = None
actual_box_Z = None
status_box_Z = None

status_final = None

kondisi_reset = 0

file_plc = 'baca_file_ini_plc.csv'
file_report = 'baca_file_ini_report.csv'

none_stat = "BELUM_TERDETEKSI"



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

def draw_horizontal_lines(image, height1, height2):
    cv2.line(image, (0, height1), (image.shape[1], height1), (0, 0, 255), 2)
    cv2.line(image, (0, height2), (image.shape[1], height2), (0, 0, 255), 2)
    return image

def remove_prefix(string):
    if len(string) > 3:
        return string[3:]
    else:
        return ""

def remove_array(string):
    a = string
    a = str(a)
    a = a.strip("{}")
    a = a.split(":")[1]
    a = a.strip().strip("'")
    return a

def write_new_line_to_csv(data):
    with open(file_plc, 'w', newline='') as output_file:
        writer = csv.writer(output_file)
        writer.writerows(data)

def update_continue_csv(data):
    with open(file_report, 'a', newline='') as output_file:
        writer = csv.writer(output_file)
        writer.writerows(data)

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
    #data = [[sequence, nomor_body, vin_no, car, steer, suffix, Kode_relay, Box_X, Box_Y, Box_Z, "ok"]]
    
    #write_new_line_to_csv(data)
    #update_continue_csv(data)


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

def get_sequence2():
    global data_seq

    return data_seq

def get_box_X2():
    global data_box_X
    a = data_box_X
    a = str(data_box_X)
    a = a.strip("{}")
    a = a.split(":")[1]
    a = a.strip().strip("'")
    return a

def get_box_Y2():
    global data_box_Y
    b = data_box_Y
    b = str(data_box_Y)
    b = b.strip("{}")
    b = b.split(":")[1]
    b = b.strip().strip("'")
    return b

def get_box_Z2():
    global data_box_Z
    c = data_box_Z
    c = str(data_box_Z)
    c = c.strip("{}")
    c = c.split(":")[1]
    c = c.strip().strip("'")
    return c

def get_car2():
    global data_car
    a = data_car
    a = str(data_car)
    a = a.strip("{}")
    a = a.split(":")[1]
    a = a.strip().strip("'")
    return a

def get_steer2():
    global data_steer
    a = data_steer
    a = str(data_steer)
    a = a.strip("{}")
    a = a.split(":")[1]
    a = a.strip().strip("'")
    return a


def custom_model():
    a = get_box_X2()
    b = get_car2()
    c = get_steer2()
    mobil = b + '_' + c

    model2 = torch.hub.load('.', 'custom', path_model + mobil +'/Box1/'+a+'/train1/weights/best.pt', source='local',force_reload=True)
    return model2
    
def custom_model2():
    a = get_box_Y2()
    b = get_car2()
    c = get_steer2()
    mobil = b + '_' + c

    model2 = torch.hub.load('.', 'custom', path_model + mobil +'/Box2/'+ a +'/train1/weights/best.pt', source='local',force_reload=True)
    return model2

def custom_model3():
    a = get_box_Z2()
    b = get_car2()
    c = get_steer2()
    mobil = b + '_' + c
    model2 = torch.hub.load('.', 'custom', path_model + mobil +'/Box3/'+a+'/train1/weights/best.pt', source='local',force_reload=True)
    
    return model2



def gen(camera):
    global reference_box_X
    global actual_box_X
    global status_box_X

    reference_box_X = None
    actual_box_X = None
    status_box_X = None

    temp_reference_box_X = remove_prefix(get_box_X2())

    reference_box_X = {
        'ref_box_X' : temp_reference_box_X
    }

    
    model = custom_model()
    df_array = [] # Array untuk menyimpan hasil df
    af_array = []

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

                if ymin < nilai_ymin or ymax > nilai_ymax:
                    img = np.array(img)  # RGB
                    img_BGR = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)  # BGR

                    # Gambar garis horizontal
                    img_BGR = draw_horizontal_lines(img_BGR, nilai_ymin, nilai_ymax)

                    frame = cv2.imencode('.jpg', img_BGR)[1].tobytes()

                    print("gen1")
                    print(none_stat)
                    
                    yield(b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
                    
                    af_array.append(none_stat)
                
                    if af_array.count(none_stat) > kuota_belum:
                        actual_box_X = {
                            'act_box_X' : none_stat
                        }
                        status_box_X = {
                            'stat_box_X' : none_stat
                        }
                        break

                else:
                    df = results.pandas().xyxy[0]['name']
                    ef = df.to_string()
                    ef = ef.split()[1]
                    print("============")
                    print(ef)

                    df_array.append(ef)

                    nilai_unik = list(set(df_array))
                    print("gen1")
                    print(len(df_array))  # Menyimpan hasil df dalam array
                    print("==============")
                    img = np.squeeze(results.render())  # RGB
                    img_BGR = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)  # BGR

                    # Gambar garis horizontal
                    img_BGR = draw_horizontal_lines(img_BGR, nilai_ymin, nilai_ymax)

                    frame = cv2.imencode('.jpg', img_BGR)[1].tobytes()

                    yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

                    # Perhitungan jika ada nilai yang sama sebanyak 500

                    if ef != "NG":
                        if df_array.count(ef) > kuota_benar:
                            actual_box_X = {
                                'act_box_X' : ef
                            }
                            if temp_reference_box_X == ef:
                                status_box_X = {
                                    'stat_box_X' : "OK"
                                }
                            else :
                                status_box_X = {
                                    'stat_box_X' : "NG"
                                }

                            break
                            
                    else:
                        if df_array.count("NG") > kuota_salah:
                            actual_box_X = {
                                'act_box_X' : ef
                            }
                            status_box_X = {
                                'stat_box_X' : "NG"
                            }
                            

                            print("================================")
                            print("================================")
                            print("================================")
                            print("================================")
                            break
                    
                            
                    

            else:
                ymin = 0
                ymax = 0

                img = np.array(img)  # RGB
                img_BGR = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)  # BGR

                # Gambar garis horizontal
                img_BGR = draw_horizontal_lines(img_BGR, nilai_ymin, nilai_ymax)

                frame = cv2.imencode('.jpg', img_BGR)[1].tobytes()

                print(none_stat)

                yield(b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

                af_array.append(none_stat)
                print(len(af_array))
                
                if af_array.count(none_stat) > kuota_belum:
                    actual_box_X = {
                        'act_box_X' : none_stat
                    }
                    status_box_X = {
                        'stat_box_X' : none_stat
                    }
                    break

        else:
            break

def gen2(camera):
    global reference_box_Y
    global actual_box_Y
    global status_box_Y

    reference_box_Y = None
    actual_box_Y = None
    status_box_Y = None

    temp_reference_box_Y = remove_prefix(get_box_Y2())

    reference_box_Y = {
        'ref_box_Y' : temp_reference_box_Y
    }

    model = custom_model2()
    df_array = [] # Array untuk menyimpan hasil df
    af_array = []

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

                if ymin < nilai_ymin or ymax > nilai_ymax:
                    img = np.array(img)  # RGB
                    img_BGR = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)  # BGR

                    # Gambar garis horizontal
                    img_BGR = draw_horizontal_lines(img_BGR, nilai_ymin, nilai_ymax)

                    frame = cv2.imencode('.jpg', img_BGR)[1].tobytes()

                    print("gen2")
                    print(none_stat)
                    

                    yield(b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

                    af_array.append(none_stat)

                    if af_array.count(none_stat) > kuota_belum:
                        actual_box_Y = {
                            'act_box_Y' : none_stat
                        }
                        status_box_Y = {
                            'stat_box_Y' : none_stat
                        }
                        break


                else:
                    df = results.pandas().xyxy[0]['name']
                    ef = df.to_string()
                    ef = ef.split()[1]
                    print(ef)

                    df_array.append(ef)

                    nilai_unik = list(set(df_array))
                    print("gen2")
                    print(len(df_array))  # Menyimpan hasil df dalam array
                    print("==============")
                    img = np.squeeze(results.render())  # RGB
                    img_BGR = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)  # BGR

                    # Gambar garis horizontal
                    img_BGR = draw_horizontal_lines(img_BGR, nilai_ymin, nilai_ymax)

                    frame = cv2.imencode('.jpg', img_BGR)[1].tobytes()

                    yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

                    # Perhitungan jika ada nilai yang sama sebanyak 500

                    if ef != "NG":
                        if df_array.count(ef) > kuota_benar:
                            actual_box_Y = {
                                'act_box_Y' : ef
                            }
                            if temp_reference_box_Y == ef:
                                status_box_Y = {
                                    'stat_box_Y' : "OK"
                                }
                            else:
                                status_box_Y = {
                                    'stat_box_Y' : "NG"
                                }

                            break
                    
                    else:
                        if df_array.count("NG") > kuota_salah:
                            actual_box_Y = {
                                'act_box_Y' : ef
                            }
                            status_box_Y = {
                                'stat_box_Y' : "NG"
                            }

                            print("================================")
                            print("================================")
                            print("================================")
                            print("================================")
                            break

            else:
                ymin = 0
                ymax = 0

                img = np.array(img)  # RGB
                img_BGR = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)  # BGR

                # Gambar garis horizontal
                img_BGR = draw_horizontal_lines(img_BGR, nilai_ymin, nilai_ymax)

                frame = cv2.imencode('.jpg', img_BGR)[1].tobytes()

                print(none_stat)

                yield(b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
                af_array.append(none_stat)
                print(len(af_array))
                
                if af_array.count(none_stat) > kuota_belum:
                    actual_box_Y = {
                        'act_box_Y' : none_stat
                    }
                    status_box_Y = {
                        'stat_box_Y' : none_stat
                    }
                    break

        else:
            break

def gen3(camera):
    global reference_box_Z
    global actual_box_Z
    global status_box_Z

    reference_box_Z = None
    actual_box_Z = None
    status_box_Z = None

    temp_reference_box_Z = remove_prefix(get_box_Z2())

    reference_box_Z = {
        'ref_box_Z' : temp_reference_box_Z
    }

    model = custom_model3()
    df_array = [] # Array untuk menyimpan hasil df
    af_array = []

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

                if ymin < nilai_ymin or ymax > nilai_ymax:
                    img = np.array(img)  # RGB
                    img_BGR = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)  # BGR

                    # Gambar garis horizontal
                    img_BGR = draw_horizontal_lines(img_BGR, nilai_ymin, nilai_ymax)

                    frame = cv2.imencode('.jpg', img_BGR)[1].tobytes()

                    print("gen3")
                    print(none_stat)
                    

                    yield(b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

                    af_array.append(none_stat)
                
                    if af_array.count(none_stat) > kuota_belum:
                        actual_box_Z = {
                            'act_box_Z' : none_stat
                        }
                        status_box_Z = {
                            'stat_box_Z' : none_stat
                        }
                        break

                else:
                    df = results.pandas().xyxy[0]['name']
                    ef = df.to_string()
                    ef = ef.split()[1]
                    print(ef)

                    df_array.append(ef)

                    nilai_unik = list(set(df_array))
                    print("gen3")
                    print(len(df_array))  # Menyimpan hasil df dalam array
                    print("==============")
                    img = np.squeeze(results.render())  # RGB
                    img_BGR = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)  # BGR

                    # Gambar garis horizontal
                    img_BGR = draw_horizontal_lines(img_BGR, nilai_ymin, nilai_ymax)

                    frame = cv2.imencode('.jpg', img_BGR)[1].tobytes()

                    yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

                    # Perhitungan jika ada nilai yang sama sebanyak 500

                    if ef != "NG":
                        if df_array.count(ef) > kuota_benar:
                            actual_box_Z = {
                                'act_box_Z' : ef
                            }
                            if temp_reference_box_Z == ef:
                                status_box_Z = {
                                    'stat_box_Z' : "OK"
                                }
                            else :
                                status_box_Z = {
                                    'stat_box_Z' : "NG"
                                }

                            break
                    else:
                        if df_array.count("NG") > kuota_salah:
                            actual_box_Z = {
                                'act_box_Z' : ef
                            }
                            status_box_Z = {
                                'stat_box_Z' : "NG"
                            }

                            print("================================")
                            print("================================")
                            print("================================")
                            print("================================")
                            break

            else:
                ymin = 0
                ymax = 0

                img = np.array(img)  # RGB
                img_BGR = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)  # BGR

                # Gambar garis horizontal
                img_BGR = draw_horizontal_lines(img_BGR, nilai_ymin, nilai_ymax)

                frame = cv2.imencode('.jpg', img_BGR)[1].tobytes()

                print(none_stat)

                yield(b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

                af_array.append(none_stat)
                print(len(af_array))
                
                if af_array.count(none_stat) > kuota_belum:
                    actual_box_Z = {
                        'act_box_Z' : none_stat
                    }
                    status_box_Z = {
                        'stat_box_Z' : none_stat
                    }
                    break

        else:
            break

def gen_tunggu(camera):

    
    global reference_box_X
    global actual_box_X
    global status_box_X
    global reference_box_Y
    global actual_box_Y
    global status_box_Y
    global reference_box_Z
    global actual_box_Z
    global status_box_Z
    global status_final
    global kondisi_reset

    global latest_data

    sequence1 = latest_data ['sequence']
    body_no1 = latest_data ['nomor_body']
    vin_no1 = latest_data ['vin_no']
    car1 = latest_data ['car']
    steering1 = latest_data ['steer']
    suffix1 = latest_data ['suffix']
    relay1 = latest_data ['Kode_relay']

    #kondisi_reset = 100

    sekarang = datetime.datetime.now()
    tanggal = sekarang.strftime("%d-%m-%Y")
    jam = sekarang.strftime("%H:%M:%S")

    """
    if (remove_array(status_box_X)=="OK") and (remove_array(status_box_Y)=="OK") and (remove_array(status_box_Z)=="OK"):
        status_final ={
            'stat_final' : "OK"
        }
        kondisi_reset = 0
        #data = [[]]
    else :
        status_final = {
            'stat_final' : "NG"
        }
        kondisi_reset = 2
    """

    a = get_box_Z2()
    b = get_car2()
    c = get_steer2()
    mobil = b + '_' + c
    stir = data_steer

    if mobil == "Innova_RHD":
        if (remove_array(status_box_X)=="OK") and (remove_array(status_box_Z)=="OK"):
            status_final = {
                'stat_final' : "OK"
            }
            kondisi_reset = 0
        else :
            status_final = {
                'stat_final' : "NG"
            }
            kondisi_reset = 2
    
    else :
        if (remove_array(status_box_X)=="OK") and (remove_array(status_box_Y)=="OK") and (remove_array(status_box_Z)=="OK"):
            status_final = {
                'stat_final' : "OK"
            }
            kondisi_reset = 0
        else :
            status_final = {
                'stat_final' : "NG"
            }
            kondisi_reset = 2
        


    
    a = get_box_Z2()
    b = get_car2()
    c = get_steer2()
    mobil = b + '_' + c

    model = custom_model3()
    df_array = [] # Array untuk menyimpan hasil df

    while True:
        success, frame = camera.read()

        if success:
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()

            img = Image.open(io.BytesIO(frame))
            results = model(img, size=640)

            
            ymin = 0
            ymax = 0

            img = np.array(img)  # RGB
            img_BGR = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)  # BGR

            frame = cv2.imencode('.jpg', img_BGR)[1].tobytes()

            print("TUNGGU DATA MASUK")

            yield(b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        
        else:
            break
    



def generate_frames():
    cameraa = camera1

    global reference_box_X
    global actual_box_X
    global status_box_X
    global reference_box_Y
    global actual_box_Y
    global status_box_Y
    global reference_box_Z
    global actual_box_Z
    global status_box_Z
    global status_final
    global kondisi_reset
    
    
    
    
    while True:
        ###untuk membuktikan bahwa terjadi NG #time.sleep(5)
        reference_box_X = None
        actual_box_X = None
        status_box_X = None
        reference_box_Y = None
        actual_box_Y = None
        status_box_Y = None
        reference_box_Z = None
        actual_box_Z = None
        status_box_Z = None
        status_final = None

        reference_box_X = {
            'ref_box_X' : remove_prefix(get_box_X2())
        }

        reference_box_Y = {
            'ref_box_Y' : remove_prefix(get_box_Y2())
        }        

        reference_box_Z = {
            'ref_box_Z' : remove_prefix(get_box_Z2())
        }     



        a = get_box_Z2()
        b = get_car2()
        c = get_steer2()
        mobil = b + '_' + c
        stir = data_steer
        previous_data_seq = data_seq
        continue_loop = True

        #CYCLE1
        ws.call(requests.SetCurrentProgramScene(sceneName=list_scene[0]['sceneName']))
        for frame in gen(cameraa):
            yield frame

            if status_box_X == none_stat:
                kondisi_reset = 2
                continue_loop = False

                #time.sleep(5)

                break
            
        if not continue_loop:
            continue

        #CYCLE2
        if mobil == "Innova_RHD":
            if status_box_Y == none_stat:
                kondisi_reset = 2
                #time.sleep(5)
                continue_loop = False

                break

            if not continue_loop:
                continue

        else :
            ws.call(requests.SetCurrentProgramScene(sceneName=list_scene[1]['sceneName']))
            for frame in gen2(cameraa):
                yield frame

                if status_box_Y == none_stat:
                    kondisi_reset = 2
                    #time.sleep(5)
                    continue_loop = False

                    break
                
            if not continue_loop:
                continue

        #CYCLE3
        ws.call(requests.SetCurrentProgramScene(sceneName=list_scene[2]['sceneName']))
        for frame in gen3(cameraa):
            yield frame

            if status_box_Z == none_stat:
                kondisi_reset = 2
                #time.sleep(5)

                break

        #CYCLE_WAIT
        if data_seq == previous_data_seq:
            while data_seq == previous_data_seq:
                # Tunggu hingga data_seq diperbarui
                ws.call(requests.SetCurrentProgramScene(sceneName=list_scene[5]['sceneName']))

                
                for frame in gen_tunggu(cameraa):
                    yield frame

                    if data_seq != previous_data_seq:
                        break
                pass
                   




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

########################################
########################################

@app.route('/get_value')
def get_value():
    global kondisi_reset
    return str(kondisi_reset)


@app.route('/reset')
def reset():
    global kondisi_reset
    kondisi_reset = 0
    return ''

########################################
########################################

@app.route('/get_reference_box_X')
def get_reference_box_X():
    global reference_box_X
    return jsonify(reference_box_X)

@app.route('/get_actual_box_X')
def get_actual_box_X():
    global actual_box_X
    return jsonify(actual_box_X)

@app.route('/get_status_box_X')
def get_status_box_X():
    global status_box_X
    return jsonify(status_box_X)

########################################

@app.route('/get_reference_box_Y')
def get_reference_box_Y():
    global reference_box_Y
    return jsonify(reference_box_Y)

@app.route('/get_actual_box_Y')
def get_actual_box_Y():
    global actual_box_Y
    return jsonify(actual_box_Y)

@app.route('/get_status_box_Y')
def get_status_box_Y():
    global status_box_Y
    return jsonify(status_box_Y)

########################################

@app.route('/get_reference_box_Z')
def get_reference_box_Z():
    global reference_box_Z
    return jsonify(reference_box_Z)

@app.route('/get_actual_box_Z')
def get_actual_box_Z():
    global actual_box_Z
    return jsonify(actual_box_Z)

@app.route('/get_status_box_Z')
def get_status_box_Z():
    global status_box_Z
    return jsonify(status_box_Z)

########################################

@app.route('/get_status_final')
def get_status_final():
    global status_final
    return jsonify(status_final)



@app.route('/video')
def video():
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