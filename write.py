import pandas as pd
import random
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import pandas as pd

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
                        status_final = row[10]
                        
                        self.data_handler(sequence, nomor_body, vin_no, car, steer, suffix, Kode_relay, Box_X, Box_Y, Box_Z, status_final)  # Durasi loop


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

def command(sequence, nomor_body, vin_no, car, steer, suffix, Kode_relay, Box_X, Box_Y, Box_Z, status_final):
    status = status_final

    if status_final = "NG":
        break   

#############################

#path
path = "/home/engser/YOLO/yolov5_research2/"

#nama file jembatan
filename_tulis_csv ="baca_file_ini.csv"

#path file jembatan
filename_tulis = path + filename_tulis_csv

#nama file transform
filename_read_transform_csv ="transform_data4.csv"

#path file transform
filename_read_transform = path + filename_read_transform_csv


#read data file transform
df_read = pd.read_csv(filename_read_transform_csv)
df_read_list = df_read.values.tolist()

#read data file jembatan
ef = pd.read_csv(filename_tulis)



for x in range(1000000):
    random_item = random.choice(df_read_list)
    ff = pd.DataFrame([x])
    hf = pd.DataFrame([x*random.randrange(100)])
    ef = pd.DataFrame([random_item])
    gf = pd.concat([ff,hf,ef],axis=1, join='inner')
    gf.to_csv(filename_tulis,index=False, header=False)

    print(gf)

    time.sleep(18)
