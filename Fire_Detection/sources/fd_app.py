from config_ import *
from send_alerts import send_alerts
from write_video import write_video
import sys
import qdarkstyle
import time
import datetime
import cv2
import re
from PyQt5.QtCore import Qt, QSize, QUrl, QTimer
from PyQt5.QtGui import QIcon, QPixmap, QImage, QFont
from PyQt5.QtWidgets import (
    QMainWindow,
    QWidget,
    QPushButton,
    QHBoxLayout,
    QVBoxLayout,
    QSlider,
    QAction,
    QToolBar,
    QStyle,
    QFileDialog,
    QApplication,
    QStatusBar,
    QLabel,
    QLineEdit,
)
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget


class FireDetection(QMainWindow):
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Unfree Fire 🔥")
        self.setMinimumSize(1080, 720)
        self.setWindowIcon(QIcon("../images/fire.png"))
        self.init_ui()
        self.destination_email_address = ""
        self.start_time = None
        self.end_time = None
        
    def init_ui(self):    
        # ----------------------------------------------------------------
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setFont(QFont("Lora", 28))
        self.image_label.setWindowIcon(QIcon("../images/video_mode.png"))
        self.capture = None
        self.real_time_mode = None
        self.send_mail_check_list = []
        self.temp_frames = []
        self.send_mail = None
        self.attempts = 1
        self.interval_02 = 60000
        self.interval_03 = 1800000

        # ----------------------------------------------------------------

        self.email_input = QLineEdit(self)
        self.email_input.setPlaceholderText("Enter your Email")
        
        self.submit_button = QPushButton("Submit")
        self.submit_button.clicked.connect(self.get_email_address)
        
        email_layout = QHBoxLayout()
        email_layout.addWidget(self.email_input)
        email_layout.addWidget(self.submit_button)

        # ----------------------------------------------------------------
        
        self.browse_button = QPushButton("Choose another video")
        self.browse_button.clicked.connect(self.open_video)
        
        # ----------------------------------------------------------------
        
        self.play_pause_button = QPushButton(self)
        self.play_pause_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay))
        self.play_pause_button.clicked.connect(self.play_pause_video)
        
        # ----------------------------------------------------------------

        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setMinimum(0)
        self.slider.setMaximum(0)
        self.slider.sliderMoved.connect(self.set_position)
        
        # ----------------------------------------------------------------
        
        H_Box = QHBoxLayout()
        H_Box.addWidget(self.browse_button)
        H_Box.addWidget(self.play_pause_button)
        H_Box.addWidget(self.slider)

        # ----------------------------------------------------------------
        
        V_Box = QVBoxLayout()
        V_Box.addLayout(email_layout)
        self.email_input.setHidden(True)
        self.submit_button.setHidden(True)
        V_Box.addWidget(self.image_label)
        V_Box.addLayout(H_Box)
        
        central_widget = QWidget()
        central_widget.setLayout(V_Box)
        self.setCentralWidget(central_widget)
        
        # ----------------------------------------------------------------
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.playing = False
        
        self.timer_02 = QTimer()
        self.timer_02.setInterval(self.interval_02)
        self.timer_02.timeout.connect(self.w_send_email)
        self.timer_02.start()
        
        self.timer_03 = QTimer()
        self.timer_03.setInterval(self.interval_03)
        self.timer_03.timeout.connect(self.set_attempts)
        self.timer_03.start()
        
        # ----------------------------------------------------------------
        
        self.toolbar = QToolBar("Main ToolBar", self)
        self.toolbar.setIconSize(QSize(16, 16))
        self.addToolBar(Qt.TopToolBarArea, self.toolbar)
        self.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        
        # ----------------------------------------------------------------
        
        button_add_email = QAction(QIcon("../images/add_email.png"), "Add Email", self)
        button_add_email.setStatusTip("Add your Email")
        button_add_email.setCheckable(True)
        button_add_email.triggered.connect(self.add_email)
        self.toolbar.addAction(button_add_email)
        self.toolbar.addSeparator()
        
        # ----------------------------------------------------------------
        
        button_real_time_mode = QAction(QIcon("../images/real_time.png"), "Real Time Mode", self)
        button_real_time_mode.setStatusTip("Open real-time mode")
        button_real_time_mode.setCheckable(True)
        button_real_time_mode.triggered.connect(self.change_to_real_time_mode)
        self.toolbar.addAction(button_real_time_mode)
        self.toolbar.addSeparator()
        
        # ----------------------------------------------------------------
        
        self.setStatusBar(QStatusBar(self))
        
        # ----------------------------------------------------------------
    
    def set_attempts(self):
        if self.attempts == 5:
            self.attempts = 1
        
    def w_send_email(self):
        if self.send_mail == True and self.attempts <= 5:
            send_alerts(
                subject=f"Warning! time: {datetime.datetime.now()}",
                text="Fire detected",
                sender_email=sender_email_,
                password=password_,
                receiver_email=self.destination_email_address,
                video_filename="../videos/output_fire.mp4" 
            )
            self.attempts += 1
        else:
            print("Warning has not been sent")
        
    def change_to_real_time_mode(self, s):
        print(f"real-time mode: {s}")
        self.real_time_mode = s
        if self.capture is not None:
            self.capture.release()
    
        if s == True:
            camera = 0
            self.capture = cv2.VideoCapture(camera)
            self.browse_button.setHidden(s)
            self.slider.setHidden(s)
            self.timer.timeout.disconnect()
            self.timer.timeout.connect(self.update_frame_real_time)
            self.image_label.setText("Real-Time mode is ready")
            self.send_mail_check_list = []
            self.temp_frames = []
        else:
            self.capture.release()
            self.browse_button.setHidden(s)
            self.slider.setHidden(s)
            self.timer.timeout.disconnect()
            self.timer.timeout.connect(self.update_frame)
            self.image_label.setText("Video mode is ready")
            self.send_mail_check_list = []
            self.temp_frames = []

    def open_video(self):
        if self.capture is not None:
            self.capture.release()

        filename, _ = QFileDialog.getOpenFileName(self, "Open Video")
        if filename:
            self.capture = cv2.VideoCapture(filename)
            frame_count = int(self.capture.get(cv2.CAP_PROP_FRAME_COUNT))
            self.slider.setMaximum(frame_count)
            self.play_pause_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay))
            self.playing = False
            self.image_label.setText("Path defined")

    def is_valid_email(self, email):
        # Biểu thức chính quy để kiểm tra định dạng email
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None        

    def add_email(self, s):
        self.email_input.setHidden(not s)
        self.submit_button.setHidden(not s)
        self.email_input.setText("")
        self.destination_email_address = ""
        
    def get_email_address(self):
        email_address = self.email_input.text()
        if self.is_valid_email(email_address):
            self.destination_email_address = email_address
            self.email_input.setText(f"Alerts will be sent to: {email_address}")
            self.submit_button.setHidden(True)
        else:
            self.email_input.setText(f"Email address is not valid")
        
    def play_pause_video(self):
        if not self.playing:
            self.timer.start(30)
            self.play_pause_button.setIcon(
                self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPause)
            )
            self.image_label.setText(f"loading .........")
        else:
            self.timer.stop()
            self.play_pause_button.setIcon(
                self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay)
            )
        self.playing = not self.playing
    
    def set_position(self, position):
        self.capture.set(cv2.CAP_PROP_POS_FRAMES, position)
    
    def update_frame(self):
        if self.capture is not None:
            pos = self.capture.get(cv2.CAP_PROP_POS_FRAMES)
        success, frame = self.capture.read()
        if success:
            # resized_frame = cv2.resize(frame, dsize=(640, 480))
            results = yolo_model.predict(source=frame, conf=0.5, device="cuda:0")                 
            annotated_frame = results[0].plot()
            frame_rgb = cv2.cvtColor(annotated_frame, code=cv2.COLOR_BGR2RGB)
            
            # ----------------------------------------------------------------------------
            self.send_mail_check_list.append(results)
            self.temp_frames.append(frame_rgb)
            if len(self.send_mail_check_list) == 160:
                self.send_mail = self.check_email_sending(self.send_mail_check_list)
                write_video(self.temp_frames, 32, output_file="../videos/output_fire.mp4")
                self.send_mail_check_list = []
                self.temp_frames = []
            # ---------------------------------------------------------------------------- 

            h, w, c = frame_rgb.shape
            bytes_per_line = c * w
            q_image = QImage(frame_rgb.data, w, h, bytes_per_line, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(q_image)
            self.image_label.setPixmap(pixmap.scaled(self.image_label.size(), Qt.KeepAspectRatio))
            self.slider.setValue(int(pos))
        else:
            self.timer.stop()
            
    def update_frame_real_time(self):
        success, frame = self.capture.read()
        if success:
            # resized_frame = cv2.resize(frame, dsize=(640, 480))
            results = yolo_model.predict(source=frame, conf=0.5, device="cuda:0") 
            annotated_frame = results[0].plot()
            frame_rgb = cv2.cvtColor(annotated_frame, code=cv2.COLOR_BGR2RGB)
            
            # ----------------------------------------------------------------------------
            self.send_mail_check_list.append(results)
            self.temp_frames.append(frame_rgb)
            if len(self.send_mail_check_list) == 160:
                self.send_mail = self.check_email_sending(self.send_mail_check_list)
                write_video(self.temp_frames, 32, output_file="../videos/output_fire.mp4")
                self.send_mail_check_list = []
                self.temp_frames = []
            # ----------------------------------------------------------------------------
            
            h, w, c = frame_rgb.shape
            bytes_per_line = c * w
            q_image = QImage(frame_rgb.data, w, h, bytes_per_line, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(q_image)
            self.image_label.setPixmap(pixmap.scaled(self.image_label.size(), Qt.KeepAspectRatio))
        else:
            self.timer.stop()
    
    def check_email_sending(self, check_list):
        check = []
        for results in check_list:
            if results[0].boxes.cpu():
                check.append(1)
            else:
                check.append(0)
        _sum_ = np.sum(check)
        return _sum_ > 128
            
            
if __name__ == "__main__":
    app = QApplication(sys.argv)
    fire_detection = FireDetection()
    fire_detection.show()
    sys.exit(app.exec_()) 