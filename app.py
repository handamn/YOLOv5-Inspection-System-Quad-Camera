import io
import cv2
import numpy as np
from PIL import Image
import torch

path_model ="/home/engser/YOLO/yolov5_research2/model_custom/"

def custom_model3():
    model2 = torch.hub.load('.', 'custom', path_model + 'Fortuner_LHD/Box3/FL_Z_3_BCD/train1/weights/best.pt', source='local',force_reload=True)
    return model2


def gen(camera):
   model = custom_model()
   while True:
        success, frame = camera.read()
        
        if success:
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()

            img = Image.open(io.BytesIO(frame))
            results = model(img, size=640)
            df = results.pandas().xyxy[0]['name']
            print(df)

            img = np.squeeze(results.render())  # RGB
            img_BGR = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)  # BGR

            frame = cv2.imencode('.jpg', img_BGR)[1].tobytes()

            yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

        else:
            break
