import pandas as pd
import time
import random

#path
path = "/home/engser/YOLO/yolov5_research2/"

#nama file jembatan
filename_tulis_csv = "baca_file_ini.csv"

#path file jembatan
filename_tulis = path + filename_tulis_csv

#nama file transform
filename_read_transform_csv = "transform_data5.csv"

#path file transform
filename_read_transform = path + filename_read_transform_csv

# Read data file transform
df_read = pd.read_csv(filename_read_transform_csv)

# Write data to file jembatan without header
for x in range(len(df_read)):
    random_item = df_read.iloc[x].values
    ff = pd.DataFrame([x])
    hf = pd.DataFrame([x * random.randrange(100)])
    ef = pd.DataFrame([random_item])
    gf = pd.concat([ff, hf, ef], axis=1, join='inner')
    gf.to_csv(filename_tulis, index=False, header=False)

    print(gf)

    time.sleep(30)
