import os
import datetime
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import csv
from flask import Flask, render_template, jsonify, Response, request
import io
import cv2
import numpy as np
from PIL import Image, ImageFilter
import torch
from obswebsocket import obsws, requests
from obswebsocket.exceptions import ConnectionFailure
import pandas as pd
from flask import send_from_directory
import random

camera1 = cv2.VideoCapture(0)

app = Flask(__name__)

password = "XD9RjF4blgdS9E3f"

ws = obsws('localhost', 4455, password)
ws.connect()

scenes = ws.call(requests.GetSceneList())
list_scene = scenes.getScenes()

path_model ="/home/engser/YOLO/yolov5_research2/model_custom/"
path_standard_image = "/home/engser/YOLO/yolov5_research2/gambar3"


# Global variable to store the latest data
data_acuan = pd.Series(np.array([1]))
nilai_ymin = 10
nilai_ymax = 450

kuota_benar = 50
kuota_salah = 50
kuota_belum = 100

list_kamera = [0,1,2,3]

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

notif_final = None

kondisi_reset = 0

file_plc = 'file_plc.csv'
file_report = 'file_report.csv'
urutan_kamera = 'urutan_kamera.csv'

none_stat = "BELUM_TERDETEKSI"

path_gambar = '/home/engser/YOLO/yolov5_research2/gambar/'


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
                trimming_code = row[6]
                Kode_relay = row[7]
                Box_X = row[8]
                Box_Y = row[9]
                Box_Z = row[10]
                self.data_handler(sequence, nomor_body, vin_no, car, steer, suffix, trimming_code, Kode_relay, Box_X, Box_Y, Box_Z)
                
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
                print("Trimming Code:", trimming_code)
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
    a = str(string)
    a = a.strip("{}")
    a = a.split(":")[1]
    a = a.strip().strip("'")
    print(a)
    return a

def write_new_line_to_csv(data,dokumen):
    with open(dokumen, 'w', newline='') as output_file:
        writer = csv.writer(output_file)
        writer.writerows(data)

def update_continue_csv(data, dokumen):
    with open(dokumen, 'a', newline='') as output_file:
        writer = csv.writer(output_file)
        writer.writerows(data)

def tambah_data(data, dokumen):
    with open(dokumen, 'r', newline='') as file_csv:
        reader = csv.reader(file_csv)
        rows = list(reader)
    
    rows[-1].append(data)

    with open(dokumen, 'w', newline='') as file_csv:
        writer = csv.writer(file_csv)
        writer.writerows(rows)

def csv_ke_dataframe(nama_file):
    dataframe = pd.read_csv(nama_file)
    return dataframe

def handle_data(sequence, nomor_body, vin_no, car, steer, suffix, trimming_code, Kode_relay, Box_X, Box_Y, Box_Z):
    global latest_data
    latest_data = {
        'sequence': sequence,
        'nomor_body': nomor_body,
        'vin_no': vin_no,
        'car': car,
        'steer': steer,
        'suffix': suffix,
        'trimming_code' : trimming_code,
        'Kode_relay': Kode_relay,
        'Box_X': Box_X,
        'Box_Y': Box_Y,
        'Box_Z': Box_Z
    }


def handle_sequence(sequence, nomor_body, vin_no, car, steer, suffix, trimming_code, Kode_relay, Box_X, Box_Y, Box_Z):
    global data_seq
    data_seq = {
        'sequence2' : sequence
    }

def handle_car(sequence, nomor_body, vin_no, car, steer, suffix, trimming_code, Kode_relay, Box_X, Box_Y, Box_Z):
    global data_car
    data_car = {
        'car2' : car
    }
    return data_car

def handle_steer(sequence, nomor_body, vin_no, car, steer, suffix, trimming_code, Kode_relay, Box_X, Box_Y, Box_Z):
    global data_steer
    data_steer = {
        'steer2' : steer
    }
    return data_steer

def handle_box_X(sequence, nomor_body, vin_no, car, steer, suffix, trimming_code, Kode_relay, Box_X, Box_Y, Box_Z):
    global data_box_X
    data_box_X = {
        'box_X2' : Box_X
    }

def handle_box_Y(sequence, nomor_body, vin_no, car, steer, suffix, trimming_code, Kode_relay, Box_X, Box_Y, Box_Z):
    global data_box_Y
    data_box_Y = {
        'box_Y2' : Box_Y
    }

def handle_box_Z(sequence, nomor_body, vin_no, car, steer, suffix, trimming_code, Kode_relay, Box_X, Box_Y, Box_Z):
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

def crop(img, bbox, final_name):
    # Mendapatkan waktu saat ini
    now = datetime.datetime.now()
    tanggal = now.strftime("%d-%m-%Y")

    # Mendapatkan jam, menit, dan detik
    hour = str(now.hour)
    minute = str(now.minute)
    second = str(now.second)

    # Crop the image using the bounding box coordinates
    cropped_img = Image.fromarray(img).crop((bbox[0], bbox[1], bbox[2], bbox[3]))

    # Calculate the new size while maintaining the aspect ratio
    width, height = cropped_img.size
    max_w = 320
    max_h = 240

    # Menentukan faktor perubahan ukuran
    width_ratio = max_w / width
    height_ratio = max_h / height
    resize_ratio = min(width_ratio, height_ratio)

    # Menghitung ukuran baru
    new_width = int(width * resize_ratio)
    new_height = int(height * resize_ratio)

    
    # Resize the image while maintaining the aspect ratio
    resized_img = cropped_img.resize((new_width, new_height), Image.LANCZOS)

    # Enhance the sharpness of the resized image
    enhanced_img = resized_img.filter(ImageFilter.UnsharpMask(radius=3, percent=180, threshold=3))

    # Save the cropped image as a screenshot
    save_name = path_gambar + tanggal + "_" + hour + ":" + minute + ":" + second + "_" + final_name
    
    #cropped_img.save(path_gambar+ hour + minute + second +"screenshotX.jpg")
    enhanced_img.save(save_name+ ".jpg")
    print("Screenshot saved!")

def crop2(img, final_name):
    # Mendapatkan waktu saat ini
    now = datetime.datetime.now()
    tanggal = now.strftime("%d-%m-%Y")

    # Mendapatkan jam, menit, dan detik
    hour = str(now.hour)
    minute = str(now.minute)
    second = str(now.second)

    screen_img = Image.fromarray(img)
    resized_img = screen_img.resize((320,240), Image.LANCZOS)

    # Save the cropped image as a screenshot
    save_name = path_gambar + tanggal + "_" + hour + ":" + minute + ":" + second + "_" + final_name
    
    resized_img.save(save_name+ ".jpg")



def gen(camera):
    global reference_box_X
    global actual_box_X
    global status_box_X

    global latest_data

    sequence1 = latest_data ['sequence']
    body_no1 = latest_data ['nomor_body']
    vin_no1 = latest_data ['vin_no']
    car1 = latest_data ['car']
    steering1 = latest_data ['steer']
    suffix1 = latest_data ['suffix']
    trimming_code1 = latest_data ['trimming_code']
    relay1 = latest_data ['Kode_relay']
    box_X1 = latest_data ['Box_X']

    file_name = sequence1 + '_' + body_no1 + '_' + vin_no1 + '_' + car1 + '_' + steering1 + '_' + suffix1 + '_' + trimming_code1 + '_' + relay1 + '_'

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

                        final_name = file_name + "JB_X_" +box_X1 + "_" +"NG"
                        crop2(img, final_name) 

                        break

                else:
                    bbox = results.pandas().xyxy[0][['xmin', 'ymin', 'xmax', 'ymax']].values[0]
                    bbox = bbox.astype(int)  

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
                                final_name = file_name + "JB_X_" + ef + "_" +"OK"
                                crop(img, bbox, final_name)

                            else :
                                status_box_X = {
                                    'stat_box_X' : "NG"
                                }
                                final_name = file_name + "JB_X_" + box_X1 + "_" +"NG"
                                crop(img, bbox, final_name)
                            

                            break
                            
                    else:
                        if df_array.count("NG") > kuota_salah:
                            actual_box_X = {
                                'act_box_X' : ef
                            }
                            status_box_X = {
                                'stat_box_X' : "NG"
                            }
                            final_name = file_name + "JB_X_" + box_X1 + "_" +"NG"
                            crop(img, bbox, final_name)                            

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
                    final_name = file_name + "JB_X_" + box_X1 + "_" +"NG"
                    crop2(img, final_name)

                    break

        else:
            break

def gen2(camera):
    global reference_box_Y
    global actual_box_Y
    global status_box_Y

    global latest_data

    sequence1 = latest_data ['sequence']
    body_no1 = latest_data ['nomor_body']
    vin_no1 = latest_data ['vin_no']
    car1 = latest_data ['car']
    steering1 = latest_data ['steer']
    suffix1 = latest_data ['suffix']
    trimming_code1 = latest_data ['trimming_code']
    relay1 = latest_data ['Kode_relay']
    box_Y1 = latest_data ['Box_Y']

    file_name = sequence1 + '_' + body_no1 + '_' + vin_no1 + '_' + car1 + '_' + steering1 + '_' + suffix1 + '_' + trimming_code1 + '_' + relay1 + '_'

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

                        final_name = file_name + "JB_Y_" + box_Y1 + "_" +"NG"
                        crop2(img, final_name) 

                        break

                else:
                    bbox = results.pandas().xyxy[0][['xmin', 'ymin', 'xmax', 'ymax']].values[0]
                    bbox = bbox.astype(int)  

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
                                final_name = file_name + "JB_Y_" + ef + "_" +"OK"
                                crop(img, bbox, final_name)                                
                            else:
                                status_box_Y = {
                                    'stat_box_Y' : "NG"
                                }
                                final_name = file_name + "JB_Y_" + box_Y1 + "_" +"NG"
                                crop(img, bbox, final_name)

                            break
                    
                    else:
                        if df_array.count("NG") > kuota_salah:
                            actual_box_Y = {
                                'act_box_Y' : ef
                            }
                            status_box_Y = {
                                'stat_box_Y' : "NG"
                            }
                            final_name = file_name + "JB_Y_" + box_Y1 + "_" +"NG"
                            crop(img, bbox, final_name)

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

                    final_name = file_name + "JB_Y_" + box_Y1 + "_" +"NG"
                    crop2(img, final_name)   

                    break

        else:
            break

def gen3(camera):
    global reference_box_Z
    global actual_box_Z
    global status_box_Z

    global latest_data

    sequence1 = latest_data ['sequence']
    body_no1 = latest_data ['nomor_body']
    vin_no1 = latest_data ['vin_no']
    car1 = latest_data ['car']
    steering1 = latest_data ['steer']
    suffix1 = latest_data ['suffix']
    trimming_code1 = latest_data ['trimming_code']
    relay1 = latest_data ['Kode_relay']
    box_Z1 = latest_data ['Box_Z']

    file_name = sequence1 + '_' + body_no1 + '_' + vin_no1 + '_' + car1 + '_' + steering1 + '_' + suffix1 + '_' + trimming_code1 + '_' + relay1 + '_'

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

                        final_name = file_name +  "JB_Z_" + box_Z1 + "_" +"NG"
                        crop2(img, final_name)   

                        break

                else:
                    bbox = results.pandas().xyxy[0][['xmin', 'ymin', 'xmax', 'ymax']].values[0]
                    bbox = bbox.astype(int)  

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
                                final_name = file_name + "JB_Z_" + ef + "_" +"OK"
                                crop(img, bbox, final_name)
                            else :
                                status_box_Z = {
                                    'stat_box_Z' : "NG"
                                }
                                final_name = file_name + "JB_Z_" + box_Z1 + "_" +"NG"
                                crop(img, bbox, final_name)

                            break
                    else:
                        if df_array.count("NG") > kuota_salah:
                            actual_box_Z = {
                                'act_box_Z' : ef
                            }
                            status_box_Z = {
                                'stat_box_Z' : "NG"
                            }
                            final_name = file_name + "JB_Z_" + box_Z1 + "_" +"NG"
                            crop(img, bbox, final_name)

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

                    final_name = file_name + "JB_Z_" +box_Z1 + "_" +"NG"
                    crop2(img, final_name)
                    
                    break

        else:
            break

def gen_tunggu(camera):

    global data_camera

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

    global notif_final

    sequence1 = latest_data ['sequence']
    body_no1 = latest_data ['nomor_body']
    vin_no1 = latest_data ['vin_no']
    car1 = latest_data ['car']
    steering1 = latest_data ['steer']
    suffix1 = latest_data ['suffix']
    trimming_code1 = latest_data ['trimming_code']
    relay1 = latest_data ['Kode_relay']

    sekarang = datetime.datetime.now()
    tanggal = sekarang.strftime("%d-%m-%Y")
    jam = sekarang.strftime("%H:%M:%S")

    pesan_kosong = "No Camera"

    print("HI")
    print(status_box_X)
    print(status_box_Y)
    print(status_box_Z)
    #print(remove_array(status_box_X))
    ##print(remove_array(status_box_Y))
    #print(remove_array(status_box_Z))


    a = get_box_Z2()
    b = get_car2()
    c = get_steer2()
    mobil = b + '_' + c
    stir = data_steer

    data_camera = {
        'camera' : list_scene[5]['sceneName']
    }

    if mobil == "Innova_RHD":
        if (remove_array(status_box_X)=="OK") and (remove_array(status_box_Z)=="OK"):
            status_final = {
                'stat_final' : "OK"
            }
            kondisi_reset = 0
            data = [[tanggal, jam, sequence1, body_no1, vin_no1, car1, steering1, suffix1, trimming_code1, relay1,remove_array(actual_box_X), remove_array(status_box_X), pesan_kosong, pesan_kosong, remove_array(actual_box_Z), remove_array(status_box_Z), remove_array(status_final)]]
            write_new_line_to_csv(data, file_plc)
            update_continue_csv(data, file_report)
            notif_final = "OK"

        else :
            status_final = {
                'stat_final' : "NG"
            }
            kondisi_reset = 2
            data = [[tanggal, jam, sequence1, body_no1, vin_no1, car1, steering1, suffix1, trimming_code1, relay1, remove_array(actual_box_X), remove_array(status_box_X), pesan_kosong, pesan_kosong, remove_array(actual_box_Z), remove_array(status_box_Z), remove_array(status_final)]]
            write_new_line_to_csv(data, file_plc)
            update_continue_csv(data, file_report)
            notif_final = "NG"


    else :
        if (remove_array(status_box_X)=="OK") and (remove_array(status_box_Y)=="OK") and (remove_array(status_box_Z)=="OK"):
            status_final = {
                'stat_final' : "OK"
            }
            kondisi_reset = 0
            data = [[tanggal, jam, sequence1, body_no1, vin_no1, car1, steering1, suffix1, trimming_code1, relay1, remove_array(actual_box_X), remove_array(status_box_X), remove_array(actual_box_Y), remove_array(status_box_Y), remove_array(actual_box_Z), remove_array(status_box_Z), remove_array(status_final)]]
            write_new_line_to_csv(data, file_plc)
            update_continue_csv(data, file_report)
            notif_final = "OK"

        else :
            status_final = {
                'stat_final' : "NG"
            }
            kondisi_reset = 2
            data = [[tanggal, jam, sequence1, body_no1, vin_no1, car1, steering1, suffix1, trimming_code1, relay1, remove_array(actual_box_X), remove_array(status_box_X), remove_array(actual_box_Y), remove_array(status_box_Y), remove_array(actual_box_Z), remove_array(status_box_Z), remove_array(status_final)]]
            write_new_line_to_csv(data, file_plc)
            update_continue_csv(data, file_report)
            notif_final = "NG"

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

    global data_camera

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
    global notif_final
    
    df = csv_ke_dataframe(urutan_kamera)
    print(df)
    
    
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

        car_type = get_car2()
        steer_type = get_steer2()

        if car_type =="Fortuner":
            if steer_type == "LHD":

                #CYCLE1
                if int(df.loc[(df["Car"] == "Fortuner") & (df["Steering"] == "LHD"), "Cycle_1"].values[0]) in list_kamera:
                    if str(df.loc[(df["Car"] == "Fortuner") & (df["Steering"] == "LHD"), "Mode_1"].values[0]) != None:
                        cycle_1 = int(df.loc[(df["Car"] == "Fortuner") & (df["Steering"] == "LHD"), "Cycle_1"].values[0])
                        mode_1  = str(df.loc[(df["Car"] == "Fortuner") & (df["Steering"] == "LHD"), "Mode_1"].values[0])

                        ws.call(requests.SetCurrentProgramScene(sceneName=list_scene[cycle_1]['sceneName']))
                        notif_final = "RUN"
                        
                        data_camera = {
                            'camera' : list_scene[cycle_1]['sceneName']
                        }

                        if mode_1 == 'gen':
                            for frame in gen(cameraa):
                                yield frame
                                if status_box_X == none_stat:
                                    kondisi_reset = 2
                                    continue_loop = False
                                    break

                            if not continue_loop:
                                continue

                        elif mode_1 == 'gen2':
                            for frame in gen2(cameraa):
                                yield frame
                                if status_box_Y == none_stat:
                                    kondisi_reset = 2
                                    continue_loop = False
                                    break
                            
                            if not continue_loop:
                                continue
                        
                        elif mode_1 == 'gen3':
                            for frame in gen3(cameraa):
                                yield frame
                                if status_box_Z == none_stat:
                                    kondisi_reset = 2
                                    continue_loop = False
                                    break
                                
                            if not continue_loop:
                                continue
                        
                #CYCLE2
                if int(df.loc[(df["Car"] == "Fortuner") & (df["Steering"] == "LHD"), "Cycle_2"].values[0]) in list_kamera:
                    if str(df.loc[(df["Car"] == "Fortuner") & (df["Steering"] == "LHD"), "Mode_2"].values[0]) != None:
                        cycle_2 = int(df.loc[(df["Car"] == "Fortuner") & (df["Steering"] == "LHD"), "Cycle_2"].values[0])
                        mode_2  = str(df.loc[(df["Car"] == "Fortuner") & (df["Steering"] == "LHD"), "Mode_2"].values[0])

                        ws.call(requests.SetCurrentProgramScene(sceneName=list_scene[cycle_2]['sceneName']))
                        notif_final = "RUN"

                        data_camera = {
                            'camera' : list_scene[cycle_2]['sceneName']
                        }
                        
                        if mode_2 == 'gen':
                            for frame in gen(cameraa):
                                yield frame
                                if status_box_X == none_stat:
                                    kondisi_reset = 2
                                    continue_loop = False
                                    break

                            if not continue_loop:
                                continue

                        elif mode_2 == 'gen2':
                            for frame in gen2(cameraa):
                                yield frame
                                if status_box_Y == none_stat:
                                    kondisi_reset = 2
                                    continue_loop = False
                                    break
                            
                            if not continue_loop:
                                continue
                        
                        elif mode_2 == 'gen3':
                            for frame in gen3(cameraa):
                                yield frame
                                if status_box_Z == none_stat:
                                    kondisi_reset = 2
                                    continue_loop = False
                                    break
                                
                            if not continue_loop:
                                continue                

                #CYCLE3      
                if int(df.loc[(df["Car"] == "Fortuner") & (df["Steering"] == "LHD"), "Cycle_3"].values[0]) in list_kamera:
                    if str(df.loc[(df["Car"] == "Fortuner") & (df["Steering"] == "LHD"), "Mode_3"].values[0]) != None:
                        cycle_3 = int(df.loc[(df["Car"] == "Fortuner") & (df["Steering"] == "LHD"), "Cycle_3"].values[0])
                        mode_3  = str(df.loc[(df["Car"] == "Fortuner") & (df["Steering"] == "LHD"), "Mode_3"].values[0])

                        ws.call(requests.SetCurrentProgramScene(sceneName=list_scene[cycle_3]['sceneName']))
                        notif_final = "RUN"

                        data_camera = {
                            'camera' : list_scene[cycle_3]['sceneName']
                        }
                        
                        if mode_3 == 'gen':
                            for frame in gen(cameraa):
                                yield frame
                                if status_box_X == none_stat:
                                    kondisi_reset = 2
                                    continue_loop = False
                                    break

                            if not continue_loop:
                                continue

                        elif mode_3 == 'gen2':
                            for frame in gen2(cameraa):
                                yield frame
                                if status_box_Y == none_stat:
                                    kondisi_reset = 2
                                    continue_loop = False
                                    break
                            
                            if not continue_loop:
                                continue
                        
                        elif mode_3 == 'gen3':
                            for frame in gen3(cameraa):
                                yield frame
                                if status_box_Z == none_stat:
                                    kondisi_reset = 2
                                    continue_loop = False
                                    break
                                
                            if not continue_loop:
                                continue
            

            if steer_type == "RHD":

                #CYCLE1
                if int(df.loc[(df["Car"] == "Fortuner") & (df["Steering"] == "RHD"), "Cycle_1"].values[0]) in list_kamera:
                    if str(df.loc[(df["Car"] == "Fortuner") & (df["Steering"] == "RHD"), "Mode_1"].values[0]) != None:
                        cycle_1 = int(df.loc[(df["Car"] == "Fortuner") & (df["Steering"] == "RHD"), "Cycle_1"].values[0])
                        mode_1  = str(df.loc[(df["Car"] == "Fortuner") & (df["Steering"] == "RHD"), "Mode_1"].values[0])

                        ws.call(requests.SetCurrentProgramScene(sceneName=list_scene[cycle_1]['sceneName']))
                        notif_final = "RUN"

                        data_camera = {
                            'camera' : list_scene[cycle_1]['sceneName']
                        }
                        
                        if mode_1 == 'gen':
                            for frame in gen(cameraa):
                                yield frame
                                if status_box_X == none_stat:
                                    kondisi_reset = 2
                                    continue_loop = False
                                    break

                            if not continue_loop:
                                continue

                        elif mode_1 == 'gen2':
                            for frame in gen2(cameraa):
                                yield frame
                                if status_box_Y == none_stat:
                                    kondisi_reset = 2
                                    continue_loop = False
                                    break
                            
                            if not continue_loop:
                                continue
                        
                        elif mode_1 == 'gen3':
                            for frame in gen3(cameraa):
                                yield frame
                                if status_box_Z == none_stat:
                                    kondisi_reset = 2
                                    continue_loop = False
                                    break
                                
                            if not continue_loop:
                                continue
                        
                #CYCLE2
                if int(df.loc[(df["Car"] == "Fortuner") & (df["Steering"] == "RHD"), "Cycle_2"].values[0])in list_kamera:
                    if str(df.loc[(df["Car"] == "Fortuner") & (df["Steering"] == "RHD"), "Mode_2"].values[0]) != None:
                        cycle_2 = int(df.loc[(df["Car"] == "Fortuner") & (df["Steering"] == "RHD"), "Cycle_2"].values[0])
                        mode_2  = str(df.loc[(df["Car"] == "Fortuner") & (df["Steering"] == "RHD"), "Mode_2"].values[0])

                        ws.call(requests.SetCurrentProgramScene(sceneName=list_scene[cycle_2]['sceneName']))
                        notif_final = "RUN"

                        data_camera = {
                            'camera' : list_scene[cycle_2]['sceneName']
                        }
                        
                        if mode_2 == 'gen':
                            for frame in gen(cameraa):
                                yield frame
                                if status_box_X == none_stat:
                                    kondisi_reset = 2
                                    continue_loop = False
                                    break

                            if not continue_loop:
                                continue

                        elif mode_2 == 'gen2':
                            for frame in gen2(cameraa):
                                yield frame
                                if status_box_Y == none_stat:
                                    kondisi_reset = 2
                                    continue_loop = False
                                    break
                            
                            if not continue_loop:
                                continue
                        
                        elif mode_2 == 'gen3':
                            for frame in gen3(cameraa):
                                yield frame
                                if status_box_Z == none_stat:
                                    kondisi_reset = 2
                                    continue_loop = False
                                    break
                                
                            if not continue_loop:
                                continue                

                #CYCLE3      
                if int(df.loc[(df["Car"] == "Fortuner") & (df["Steering"] == "RHD"), "Cycle_3"].values[0]) in list_kamera :
                    if str(df.loc[(df["Car"] == "Fortuner") & (df["Steering"] == "RHD"), "Mode_3"].values[0])!= None:
                        cycle_3 = int(df.loc[(df["Car"] == "Fortuner") & (df["Steering"] == "RHD"), "Cycle_3"].values[0])
                        mode_3  = str(df.loc[(df["Car"] == "Fortuner") & (df["Steering"] == "RHD"), "Mode_3"].values[0])

                        ws.call(requests.SetCurrentProgramScene(sceneName=list_scene[cycle_3]['sceneName']))
                        notif_final = "RUN"

                        data_camera = {
                            'camera' : list_scene[cycle_3]['sceneName']
                        }

                        if mode_3 == 'gen':
                            for frame in gen(cameraa):
                                yield frame
                                if status_box_X == none_stat:
                                    kondisi_reset = 2
                                    continue_loop = False
                                    break

                            if not continue_loop:
                                continue

                        elif mode_3 == 'gen2':
                            for frame in gen2(cameraa):
                                yield frame
                                if status_box_Y == none_stat:
                                    kondisi_reset = 2
                                    continue_loop = False
                                    break
                            
                            if not continue_loop:
                                continue
                        
                        elif mode_3 == 'gen3':
                            for frame in gen3(cameraa):
                                yield frame
                                if status_box_Z == none_stat:
                                    kondisi_reset = 2
                                    continue_loop = False
                                    break
                                
                            if not continue_loop:
                                continue
            
        if car_type =="Innova":
            if steer_type == "LHD":

                #CYCLE1
                if int(df.loc[(df["Car"] == "Innova") & (df["Steering"] == "LHD"), "Cycle_1"].values[0]) in list_kamera:
                    if str(df.loc[(df["Car"] == "Innova") & (df["Steering"] == "LHD"), "Mode_1"].values[0]) != None:
                        cycle_1 = int(df.loc[(df["Car"] == "Innova") & (df["Steering"] == "LHD"), "Cycle_1"].values[0])
                        mode_1  = str(df.loc[(df["Car"] == "Innova") & (df["Steering"] == "LHD"), "Mode_1"].values[0])

                        ws.call(requests.SetCurrentProgramScene(sceneName=list_scene[cycle_1]['sceneName']))
                        notif_final = "RUN"

                        data_camera = {
                            'camera' : list_scene[cycle_1]['sceneName']
                        }
                        
                        if mode_1 == 'gen':
                            for frame in gen(cameraa):
                                yield frame
                                if status_box_X == none_stat:
                                    kondisi_reset = 2
                                    continue_loop = False
                                    break

                            if not continue_loop:
                                continue

                        elif mode_1 == 'gen2':
                            for frame in gen2(cameraa):
                                yield frame
                                if status_box_Y == none_stat:
                                    kondisi_reset = 2
                                    continue_loop = False
                                    break
                            
                            if not continue_loop:
                                continue
                        
                        elif mode_1 == 'gen3':
                            for frame in gen3(cameraa):
                                yield frame
                                if status_box_Z == none_stat:
                                    kondisi_reset = 2
                                    continue_loop = False
                                    break
                                
                            if not continue_loop:
                                continue
                        
                #CYCLE2
                if int(df.loc[(df["Car"] == "Innova") & (df["Steering"] == "LHD"), "Cycle_2"].values[0])in list_kamera:
                    if str(df.loc[(df["Car"] == "Innova") & (df["Steering"] == "LHD"), "Mode_2"].values[0])!= None:
                        cycle_2 = int(df.loc[(df["Car"] == "Innova") & (df["Steering"] == "LHD"), "Cycle_2"].values[0])
                        mode_2  = str(df.loc[(df["Car"] == "Innova") & (df["Steering"] == "LHD"), "Mode_2"].values[0])

                        ws.call(requests.SetCurrentProgramScene(sceneName=list_scene[cycle_2]['sceneName']))
                        notif_final = "RUN"

                        data_camera = {
                            'camera' : list_scene[cycle_2]['sceneName']
                        }
                        
                        if mode_2 == 'gen':
                            for frame in gen(cameraa):
                                yield frame
                                if status_box_X == none_stat:
                                    kondisi_reset = 2
                                    continue_loop = False
                                    break

                            if not continue_loop:
                                continue

                        elif mode_2 == 'gen2':
                            for frame in gen2(cameraa):
                                yield frame
                                if status_box_Y == none_stat:
                                    kondisi_reset = 2
                                    continue_loop = False
                                    break
                            
                            if not continue_loop:
                                continue
                        
                        elif mode_2 == 'gen3':
                            for frame in gen3(cameraa):
                                yield frame
                                if status_box_Z == none_stat:
                                    kondisi_reset = 2
                                    continue_loop = False
                                    break
                                
                            if not continue_loop:
                                continue                

                #CYCLE3      
                if int(df.loc[(df["Car"] == "Innova") & (df["Steering"] == "LHD"), "Cycle_3"].values[0])in list_kamera:
                    if str(df.loc[(df["Car"] == "Innova") & (df["Steering"] == "LHD"), "Mode_3"].values[0]) != None:
                        cycle_3 = int(df.loc[(df["Car"] == "Innova") & (df["Steering"] == "LHD"), "Cycle_3"].values[0])
                        mode_3  = str(df.loc[(df["Car"] == "Innova") & (df["Steering"] == "LHD"), "Mode_3"].values[0])

                        ws.call(requests.SetCurrentProgramScene(sceneName=list_scene[cycle_3]['sceneName']))
                        notif_final = "RUN"

                        data_camera = {
                            'camera' : list_scene[cycle_3]['sceneName']
                        }
                        
                        if mode_3 == 'gen':
                            for frame in gen(cameraa):
                                yield frame
                                if status_box_X == none_stat:
                                    kondisi_reset = 2
                                    continue_loop = False
                                    break

                            if not continue_loop:
                                continue

                        elif mode_3 == 'gen2':
                            for frame in gen2(cameraa):
                                yield frame
                                if status_box_Y == none_stat:
                                    kondisi_reset = 2
                                    continue_loop = False
                                    break
                            
                            if not continue_loop:
                                continue
                        
                        elif mode_3 == 'gen3':
                            for frame in gen3(cameraa):
                                yield frame
                                if status_box_Z == none_stat:
                                    kondisi_reset = 2
                                    continue_loop = False
                                    break
                                
                            if not continue_loop:
                                continue
            

            if steer_type == "RHD":

                #CYCLE1
                if int(df.loc[(df["Car"] == "Innova") & (df["Steering"] == "RHD"), "Cycle_1"].values[0]) in list_kamera:
                    if str(df.loc[(df["Car"] == "Innova") & (df["Steering"] == "RHD"), "Mode_1"].values[0]) != None:
                        cycle_1 = int(df.loc[(df["Car"] == "Innova") & (df["Steering"] == "RHD"), "Cycle_1"].values[0])
                        mode_1  = str(df.loc[(df["Car"] == "Innova") & (df["Steering"] == "RHD"), "Mode_1"].values[0])

                        ws.call(requests.SetCurrentProgramScene(sceneName=list_scene[cycle_1]['sceneName']))
                        notif_final = "RUN"

                        data_camera = {
                            'camera' : list_scene[cycle_1]['sceneName']
                        }
                        
                        if mode_1 == 'gen':
                            for frame in gen(cameraa):
                                yield frame
                                if status_box_X == none_stat:
                                    kondisi_reset = 2
                                    continue_loop = False
                                    break

                            if not continue_loop:
                                continue

                        elif mode_1 == 'gen2':
                            for frame in gen2(cameraa):
                                yield frame
                                if status_box_Y == none_stat:
                                    kondisi_reset = 2
                                    continue_loop = False
                                    break
                            
                            if not continue_loop:
                                continue
                        
                        elif mode_1 == 'gen3':
                            for frame in gen3(cameraa):
                                yield frame
                                if status_box_Z == none_stat:
                                    kondisi_reset = 2
                                    continue_loop = False
                                    break
                                
                            if not continue_loop:
                                continue
                        
                #CYCLE2
                if int(df.loc[(df["Car"] == "Innova") & (df["Steering"] == "RHD"), "Cycle_2"].values[0]) in list_kamera:
                    if str(df.loc[(df["Car"] == "Innova") & (df["Steering"] == "RHD"), "Mode_2"].values[0]) != None:
                        cycle_2 = int(df.loc[(df["Car"] == "Innova") & (df["Steering"] == "RHD"), "Cycle_2"].values[0])
                        mode_2  = str(df.loc[(df["Car"] == "Innova") & (df["Steering"] == "RHD"), "Mode_2"].values[0])

                        ws.call(requests.SetCurrentProgramScene(sceneName=list_scene[cycle_2]['sceneName']))
                        notif_final = "RUN"

                        data_camera = {
                            'camera' : list_scene[cycle_2]['sceneName']
                        }
                        
                        if mode_2 == 'gen':
                            for frame in gen(cameraa):
                                yield frame
                                if status_box_X == none_stat:
                                    kondisi_reset = 2
                                    continue_loop = False
                                    break

                            if not continue_loop:
                                continue

                        elif mode_2 == 'gen2':
                            for frame in gen2(cameraa):
                                yield frame
                                if status_box_Y == none_stat:
                                    kondisi_reset = 2
                                    continue_loop = False
                                    break
                            
                            if not continue_loop:
                                continue
                        
                        elif mode_2 == 'gen3':
                            for frame in gen3(cameraa):
                                yield frame
                                if status_box_Z == none_stat:
                                    kondisi_reset = 2
                                    continue_loop = False
                                    break
                                
                            if not continue_loop:
                                continue                

                #CYCLE3      
                if int(df.loc[(df["Car"] == "Innova") & (df["Steering"] == "RHD"), "Cycle_3"].values[0])in list_kamera:
                    if str(df.loc[(df["Car"] == "Innova") & (df["Steering"] == "RHD"), "Mode_3"].values[0])!= None:
                        cycle_3 = int(df.loc[(df["Car"] == "Innova") & (df["Steering"] == "RHD"), "Cycle_3"].values[0])
                        mode_3  = str(df.loc[(df["Car"] == "Innova") & (df["Steering"] == "RHD"), "Mode_3"].values[0])

                        ws.call(requests.SetCurrentProgramScene(sceneName=list_scene[cycle_3]['sceneName']))
                        notif_final = "RUN"

                        data_camera = {
                            'camera' : list_scene[cycle_3]['sceneName']
                        }
                        
                        if mode_3 == 'gen':
                            for frame in gen(cameraa):
                                yield frame
                                if status_box_X == none_stat:
                                    kondisi_reset = 2
                                    continue_loop = False
                                    break

                            if not continue_loop:
                                continue

                        elif mode_3 == 'gen2':
                            for frame in gen2(cameraa):
                                yield frame
                                if status_box_Y == none_stat:
                                    kondisi_reset = 2
                                    continue_loop = False
                                    break
                            
                            if not continue_loop:
                                continue
                        
                        elif mode_3 == 'gen3':
                            for frame in gen3(cameraa):
                                yield frame
                                if status_box_Z == none_stat:
                                    kondisi_reset = 2
                                    continue_loop = False
                                    break
                                
                            if not continue_loop:
                                continue
                         

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

########################################
image_folder = '/home/engser/YOLO/yolov5_research2/gambar'  # Ganti dengan path folder gambar Anda
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
            if 'JB_X_' in os.path.basename(event.src_path):
                app.config['LATEST_IMAGE_X'] = os.path.basename(event.src_path)
                app.config['DISPLAY_IMAGES']['x'] = True
            if 'JB_Y_' in os.path.basename(event.src_path):
                app.config['LATEST_IMAGE_Y'] = os.path.basename(event.src_path)
                app.config['DISPLAY_IMAGES']['y'] = True
            if 'JB_Z_' in os.path.basename(event.src_path):
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

######################################## 

########################################
image_folder2 = '/home/engser/YOLO/yolov5_research2/gambar'  # Ganti dengan path folder gambar Anda
app.config['UPLOAD_FOLDER2'] = "/home/engser/YOLO/yolov5_research2/gambar3"
app.config['LATEST_IMAGE_X2'] = ''
app.config['LATEST_IMAGE_Y2'] = ''
app.config['LATEST_IMAGE_Z2'] = ''
app.config['DISPLAY_IMAGES2'] = {'x2': True, 'y2': True, 'z2': True}
app.config['CSV_FILE_PATH2'] = 'baca_file_ini.csv'
app.config['CSV_FILE_LAST_MODIFIED2'] = 0

wkwk = "0_BLANK.jpg"

class ImageHandler2(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory:
            return
        filename2, extension = os.path.splitext(event.src_path)
        if extension.lower() in ['.jpg', '.jpeg', '.png', '.gif']:
            if 'JB_X_' in os.path.basename(event.src_path):
                a = get_box_X2()
                b = get_car2()
                c = get_steer2()
                mobil = b + '_' + c

                app.config['UPLOAD_FOLDER2'] = path_standard_image + "/" + mobil + "/Box1"
                app.config['LATEST_IMAGE_X2'] = a + ".jpg"
                app.config['DISPLAY_IMAGES2']['x2'] = True

            if 'JB_Y_' in os.path.basename(event.src_path):
                a = get_box_Y2()
                b = get_car2()
                c = get_steer2()
                mobil = b + '_' + c

                app.config['UPLOAD_FOLDER2'] = path_standard_image + "/" + mobil + "/Box2"
                app.config['LATEST_IMAGE_Y2'] = a + ".jpg"
                app.config['DISPLAY_IMAGES2']['y2'] = True
                print(path_standard_image + "/" + mobil + "/Box2")

            if 'JB_Z_' in os.path.basename(event.src_path):
                a = get_box_Z2()
                b = get_car2()
                c = get_steer2()
                mobil = b + '_' + c

                app.config['UPLOAD_FOLDER2'] = path_standard_image + "/" + mobil + "/Box3"
                app.config['LATEST_IMAGE_Z2'] = a + ".jpg"
                app.config['DISPLAY_IMAGES2']['z2'] = True

    def on_modified(self, event):
        if event.is_directory or event.src_path != app.config['CSV_FILE_PATH2']:
            return

        file_modified_time = os.path.getmtime(app.config['CSV_FILE_PATH2'])
        if file_modified_time > app.config['CSV_FILE_LAST_MODIFIED2']:
            app.config['CSV_FILE_LAST_MODIFIED2'] = file_modified_time
            reset_images2()


def get_latest_images2():
    latest_image_x2 = app.config.get('LATEST_IMAGE_X2', '')
    latest_image_y2 = app.config.get('LATEST_IMAGE_Y2', '')
    latest_image_z2 = app.config.get('LATEST_IMAGE_Z2', '')
    return latest_image_x2, latest_image_y2, latest_image_z2


def reset_images2():
    app.config['DISPLAY_IMAGES2'] = {'x2': False, 'y2': False, 'z2': False}


def check_csv_changes2():
    csv_file_path = app.config['CSV_FILE_PATH2']
    last_modified = app.config['CSV_FILE_LAST_MODIFIED2']
    file_modified_time = os.path.getmtime(csv_file_path)

    if file_modified_time > last_modified:
        app.config['CSV_FILE_LAST_MODIFIED2'] = file_modified_time
        reset_images2()

########################################

########################################




@app.route('/')
def index():
    return render_template('index_copy8.html')

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
    approve = "APPROVE"
    tambah_data(approve, file_plc)
    tambah_data(approve, file_report)
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

#######################################

@app.route('/latest_images_standard')
def latest_images_standard():
    check_csv_changes()
    latest_image_x, latest_image_y, latest_image_z = get_latest_images()
    display_images = app.config.get('DISPLAY_IMAGES', {'x': False, 'y': False, 'z': False})
    return jsonify({'image_x': latest_image_x, 'image_y': latest_image_y, 'image_z': latest_image_z, 'display_images': display_images})


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

#####################################

#######################################

@app.route('/latest_images')
def latest_images():
    check_csv_changes2()
    latest_image_x2, latest_image_y2, latest_image_z2 = get_latest_images2()
    display_images = app.config.get('DISPLAY_IMAGES2', {'x2': False, 'y2': False, 'z2': False})
    return jsonify({'image_x2': latest_image_x2, 'image_y2': latest_image_y2, 'image_z2': latest_image_z2, 'display_images': display_images})


@app.route('/uploads2/<filename2>')
def uploaded_file2(filename2):
    return send_from_directory(app.config['UPLOAD_FOLDER2'], filename2)

#####################################
#####################################
#def get_random_string():
    #strings = ["OK", "NG", "RUN"]
    #return random.choice(strings)

@app.route('/random_string')
def random_string():
    #random_str = get_random_string()
    global notif_final
    print(notif_final)
    return jsonify(random_string=notif_final)
#####################################


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
    event_handler9 = ImageHandler()
    event_handler10 = ImageHandler2()

    observer = Observer()
    observer.schedule(event_handler, path='.', recursive=False)
    observer.schedule(event_handler2, path='.', recursive=False)
    observer.schedule(event_handler3, path='.', recursive=False)
    #observer.schedule(event_handler4, path='.', recursive=False)
    observer.schedule(event_handler5, path='.', recursive=False)
    observer.schedule(event_handler6, path='.', recursive=False)
    observer.schedule(event_handler7, path='.', recursive=False)
    observer.schedule(event_handler8, path='.', recursive=False)
    observer.schedule(event_handler9, path=image_folder, recursive=False)
    observer.schedule(event_handler10, path=image_folder2, recursive=False)

    observer.start()

    try:
        app.run()
    except KeyboardInterrupt:
        observer.stop()
    observer.join()