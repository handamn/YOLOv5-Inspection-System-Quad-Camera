import time
from program_fungs_membaca_dan_mengirim_data import baca_data_terbaru
from obswebsocket import obsws, requests
from obswebsocket.exceptions import ConnectionFailure

password = "XD9RjF4blgdS9E3f"

ws = obsws('localhost', 4455, password)
ws.connect()

scenes = ws.call(requests.GetSceneList())
list_scene = scenes.getScenes()

"""
def handle_data(sequence,nomor_body,vin_no,car,steer,suffix,Kode_relay, Box_X, Box_Y, Box_Z):
    print("=============================")
    print("Sequence   : " + sequence)
    print("Nomor Body : " + nomor_body)
    print("Vin_no     : " + vin_no)
    print("Car        : " + car)
    print("Steer      : " + steer)
    print("Suffix     : " + suffix)
    print("Kode Relay : " + Kode_relay)
    print("Box X      : " + Box_X)
    print("Box Y      : " + Box_Y)
    print("Box Z      : " + Box_Z)
    print("=============================")
"""


def command(sequence,nomor_body,vin_no,car,steer,suffix,Kode_relay, Box_X, Box_Y, Box_Z):
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

    if car == "Fortuner":
        if steer == "LHD":
            print("Box X      : " + Box_X)
            ws.call(requests.SetCurrentProgramScene(sceneName=list_scene[2]['sceneName']))
            print("Perintah detect2.py/"+ Box_X + "/best.pt")
            print(list_scene[2]['sceneName'])
            time.sleep(3) #seolah-olah proses

            print("Box Y      : " + Box_Y)
            ws.call(requests.SetCurrentProgramScene(sceneName=list_scene[1]['sceneName']))
            print("Perintah detect2.py/"+ Box_Y + "/best.pt")
            print(list_scene[1]['sceneName'])
            time.sleep(3) #seolah-olah proses

            print("Box Z      : " + Box_Z)
            ws.call(requests.SetCurrentProgramScene(sceneName=list_scene[3]['sceneName']))
            print("Perintah detect2.py/"+ Box_Z + "/best.pt")
            print(list_scene[3]['sceneName'])
            time.sleep(3) #seolah-olah proses

            end_time = time.time()
            duration = end_time-start_time
            print("=============================")
            print(f"Durasi loop: {duration} detik")
            
            
        
        else :
            print("Box Y      : " + Box_Y)
            ws.call(requests.SetCurrentProgramScene(sceneName=list_scene[2]['sceneName']))
            print("Perintah detect2.py/"+ Box_Y + "/best.pt")
            print(list_scene[2]['sceneName'])
            time.sleep(3) #seolah-olah proses

            print("Box Z      : " + Box_Z)
            ws.call(requests.SetCurrentProgramScene(sceneName=list_scene[0]['sceneName']))
            print("Perintah detect2.py/"+ Box_Z + "/best.pt")
            print(list_scene[0]['sceneName'])
            time.sleep(3) #seolah-olah proses

            print("Box X      : " + Box_X)
            ws.call(requests.SetCurrentProgramScene(sceneName =list_scene[1]['sceneName']))
            print("Perintah detect2.py/"+ Box_X + "/best.pt")
            print(list_scene[1]['sceneName'])
            time.sleep(3) #seolah-olah proses

            
            end_time = time.time()
            duration = end_time-start_time
            print("=============================")
            print(f"Durasi proses: {duration} detik")
    
    else :
        if steer == "LHD":
            print("Box X      : " + Box_X)
            ws.call(requests.SetCurrentProgramScene(sceneName=list_scene[2]['sceneName']))
            print("Perintah detect2.py/"+ Box_X + "/best.pt")
            print(list_scene[2]['sceneName'])
            time.sleep(3) #seolah-olah proses

            print("Box Y      : " + Box_Y)
            ws.call(requests.SetCurrentProgramScene(sceneName=list_scene[1]['sceneName']))
            print("Perintah detect2.py/"+ Box_Y + "/best.pt")
            print(list_scene[1]['sceneName'])
            time.sleep(3) #seolah-olah proses

            print("Box Z      : " + Box_Z)
            ws.call(requests.SetCurrentProgramScene(sceneName=list_scene[3]['sceneName']))
            print("Perintah detect2.py/"+ Box_Z + "/best.pt")
            print(list_scene[3]['sceneName'])
            time.sleep(3) #seolah-olah proses

            end_time = time.time()
            duration = end_time-start_time
            print("=============================")
            print(f"Durasi loop: {duration} detik")
            
        
        else :
            print("Box Y      : " + Box_Y)
            ws.call(requests.SetCurrentProgramScene(sceneName=list_scene[2]['sceneName']))
            print("Tidak ada objek")
            print(list_scene[2]['sceneName'])
            time.sleep(3) #seolah-olah proses

            print("Box Z      : " + Box_Z)
            ws.call(requests.SetCurrentProgramScene(sceneName=list_scene[0]['sceneName']))
            print("Perintah detect2.py/"+ Box_Z + "/best.pt")
            print(list_scene[0]['sceneName'])
            time.sleep(3) #seolah-olah proses

            print("Box X      : " + Box_X)
            ws.call(requests.SetCurrentProgramScene(sceneName =list_scene[1]['sceneName']))
            print("Perintah detect2.py/"+ Box_X + "/best.pt")
            print(list_scene[1]['sceneName'])
            time.sleep(3) #seolah-olah proses

            
            end_time = time.time()
            duration = end_time-start_time
            print("=============================")
            print(f"Durasi proses: {duration} detik")
    
baca_data_terbaru('baca_file_ini.csv', command)

ws.disconnect()