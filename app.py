import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import csv

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

def write_to_csv(data):
    with open('coba.csv', 'w', newline='') as output_file:
        writer = csv.writer(output_file)
        writer.writerows(data)

def update_csv(data):
    with open('coba2.csv', 'a', newline='') as output_file:
        writer = csv.writer(output_file)
        writer.writerows(data)

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

def command(sequence, nomor_body, vin_no, car, steer, suffix, Kode_relay, Box_X, Box_Y, Box_Z):
    start_time = time.time()
    print("=============================")
    print("Sequence   : " + sequence)
    print("Nomor Body : " + nomor_body)
    print("Vin_no     : " + vin_no)
    print("Car        : " + car)
    print("Steer      : " + steer)
    print("Suffix     : " + suffix)
    print("Kode Relay : " + Kode_relay)
    print("-----------------------------")
    
    # Menulis data yang sudah ditambahkan ke file coba.csv
    data = [[sequence, nomor_body, vin_no, car, steer, suffix, Kode_relay, Box_X, Box_Y, Box_Z, "ok"]]
    
    time.sleep(3)
    write_to_csv(data)
    update_csv(data)

baca_data_terbaru('baca_file_ini.csv', command)

### COMMENT INI
"""
    sekarang = datetime.datetime.now()
    tanggal = sekarang.strftime("%d-%m-%Y")
    jam = sekarang.strftime("%H:%M:%S")
   
    if signal = 0:
        data = [[tanggal, jam, sequence, nomor_body, vin_no, car, steer, suffix, Kode_relay, Box_X, Box_Y, Box_Z, "OK"]]
        write_to_csv(data)
        update_csv(data)
    
    else:
        data = [[tanggal, jam, sequence, nomor_body, vin_no, car, steer, suffix, Kode_relay, Box_X, Box_Y, Box_Z, "NG"]]
        write_to_csv(data)
        update_csv(data) 
        """