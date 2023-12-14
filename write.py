import pandas as pd
import random
import time

#path
path = "/home/engser/YOLO/yolov5_research2/"

#nama file jembatan
filename_tulis_csv ="data_terima.csv"

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

    time.sleep(20)
