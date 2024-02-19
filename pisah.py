import os
import shutil
from datetime import datetime

def move_images(source_folder, destination_folder):
    # Membuat folder pemisahan jika belum ada
    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)

    # Loop through semua file di folder sumber
    for filename in os.listdir(source_folder):
        source_path = os.path.join(source_folder, filename)

        # Mengecek apakah file adalah file gambar (JPEG, PNG, dll.)
        if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            # Mendapatkan tanggal dari nama file
            date_str = extract_date_from_filename(filename)

            # Membuat folder tanggal jika belum ada
            date_folder = os.path.join(destination_folder, date_str)
            if not os.path.exists(date_folder):
                os.makedirs(date_folder)

            # Menentukan path tujuan untuk pemindahan file
            destination_path = os.path.join(date_folder, filename)

            # Memindahkan file ke folder tujuan
            shutil.move(source_path, destination_path)
            print(f"File {filename} dipindahkan ke {date_folder}")

def extract_date_from_filename(filename):
    # Menemukan tanggal dalam nama file menggunakan ekstraksi substring
    # Sesuaikan dengan format tanggal yang mungkin muncul di nama file Anda
    # Contoh: "2022-12-13" dari "2022-12-13_filename.jpg"
    date_str = filename.split('_')[0]
    return date_str

if __name__ == "__main__":
    # Ganti path sesuai dengan struktur folder Anda
    source_folder = "/home/engser/YOLO/yolov5_research2/gambar/"
    destination_folder = "/home/engser/YOLO/yolov5_research2/gambar_4/"

    move_images(source_folder, destination_folder)
