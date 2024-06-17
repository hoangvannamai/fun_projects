from ultralytics import YOLO
import numpy as np
import cv2
# ------------------------------------------------------------------

model_path_ = '../models/best_model.pt'
classnames_ = ['fire']
label_map = {c: i for i, c in enumerate(classnames_)}
reversed_label_map = {i: c for i, c in enumerate(classnames_)}

# ------------------------------------------------------------------

yolo_model = YOLO(model_path_)

# ------------------------------------------------------------------

fontFace = cv2.FONT_HERSHEY_SIMPLEX
fontScale = 0.5
thickness = 5
BLUE = (255, 0, 0)
RED = (0, 0, 255)

# ------------------------------------------------------------------

sender_email_ = ""
password_ = ""

# ------------------------------------------------------------------