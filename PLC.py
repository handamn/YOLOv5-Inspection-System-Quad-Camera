import time
from watchdog.observers.polling import PollingObserver
from watchdog.events import FileSystemEventHandler
import csv
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
                        if row[5] != "Zenix":
                            tanggal = row[0]
                            jam = row[1]
                            sequence = row[2]
                            nomor_body = row[3]
                            vin_no = row[4]
                            car = row[5]
                            steer = row[6]
                            suffix = row[7]
                            trimming_code = row[8]
                            Kode_relay = row[9]
                            Box_X = row[10]
                            stat_Box_X = row[10]
                            Box_Y = row[11]
                            stat_Box_Y = row[12]
                            Box_Z = row[13]
                            stat_Box_Z = row[14]
                            stat_FINAL = row[15]

                            self.data_handler(tanggal, jam, sequence, nomor_body, vin_no, car, steer, suffix, trimming_code, Kode_relay, Box_X, stat_Box_X,Box_Y, stat_Box_Y, Box_Z, stat_Box_Z, stat_FINAL)  # Durasi loop

                        else:
                            tanggal = row[0]
                            jam = row[1]
                            sequence = row[2]
                            nomor_body = row[3]
                            vin_no = row[4]
                            car = row[5]
                            steer = row[6]
                            suffix = row[7]
                            trimming_code = row[8]
                            Kode_relay = "None"
                            Box_X = "None"
                            stat_Box_X = "None"
                            Box_Y = "None"
                            stat_Box_Y = "None"
                            Box_Z = "None"
                            stat_Box_Z = "None"
                            stat_FINAL = "OK"

                            self.data_handler(tanggal, jam, sequence, nomor_body, vin_no, car, steer, suffix, trimming_code, Kode_relay, Box_X, stat_Box_X,Box_Y, stat_Box_Y, Box_Z, stat_Box_Z, stat_FINAL)  # Durasi loop

def baca_data_terbaru(nama_file, data_handler):
    event_handler = FileChangeHandler(nama_file, data_handler)
    observer = PollingObserver()  # Menggunakan PollingObserver
    path = '.'  # Ganti dengan path folder yang ingin Anda monitor
    observer.schedule(event_handler, path=path, recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(1)  # Interval polling
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

def command(tanggal, jam, sequence,nomor_body,vin_no,car,steer,suffix,trimming_code,Kode_relay, Box_X, stat_Box_X, Box_Y, stat_Box_Y, Box_Z, stat_Box_Z, stat_FINAL):
    start_time = time.time()
    print("=============================")
    print("=============================")
    print("Tanggal    : " + tanggal)
    print("Jam        : " + jam)
    print("Sequence   : " + sequence)
    print("Nomor Body : " + nomor_body)
    print("Vin_no     : " + vin_no)
    print("Car        : " + car)
    print("Steer      : " + steer)
    print("Suffix     : " + suffix)
    print("Trimming   : " + trimming_code)
    print("Kode Relay : " + Kode_relay)
    print("Box X      : " + Box_X)
    print("Stat_Box_X : " + stat_Box_X)
    print("Box Y      : " + Box_Y)
    print("Stat_Box_Y : " + stat_Box_Y)
    print("Box Z      : " + Box_Z)
    print("Stat_Box_Z : " + stat_Box_Z)
    print("Stat_FINAL : " + stat_FINAL)
    print("-----------------------------")

    pd_tanggal = pd.DataFrame([tanggal])
    pd_jam = pd.DataFrame([jam])
    pd_sequence = pd.DataFrame([sequence])
    pd_nomorbody = pd.DataFrame([nomor_body])
    pd_vinno = pd.DataFrame([vin_no])
    pd_car = pd.DataFrame([car])
    pd_steer = pd.DataFrame([steer])
    pd_suffix = pd.DataFrame([suffix])
    pd_trimmingcode = pd.DataFrame([trimming_code])
    pd_koderelay = pd.DataFrame([Kode_relay])
    pd_boxX = pd.DataFrame([Box_X])
    pd_stat_boxX = pd.DataFrame([stat_Box_X])
    pd_boxY = pd.DataFrame([Box_Y])
    pd_stat_boxY = pd.DataFrame([stat_Box_Y])
    pd_boxZ = pd.DataFrame([Box_Z])
    pd_stat_boxZ = pd.DataFrame([stat_Box_Z])
    pd_stat_FINAL = pd.DataFrame([stat_FINAL])

    #nama file jembatan
    filename_tulis_csv ="result.csv"

    #path file jembatan
    path = "/run/user/1000/gvfs/smb-share:server=192.168.250.2,share=share/"
    filename_tulis = path + filename_tulis_csv

    ef = pd.read_csv(filename_tulis)

    
    ini = pd.concat([pd_tanggal,pd_jam,pd_sequence,pd_nomorbody,pd_vinno,pd_car,pd_steer,pd_suffix,pd_trimmingcode,pd_koderelay,pd_boxX,pd_stat_boxX,pd_boxY,pd_stat_boxY,pd_boxZ,pd_stat_boxZ,pd_stat_FINAL], axis=1, join='inner')
    ini.to_csv(filename_tulis, index=False, header=False)                                                                                             
    

baca_data_terbaru('file_plc.csv', command)


