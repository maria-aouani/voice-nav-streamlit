# object_detector.py
import cv2
import time
import threading
import pyttsx3
from ultralytics import YOLO

class ObjectDetector:
    def __init__(self,
                 model_path="yolov8n.pt",
                 detect_interval=30,   # seconds between *runs* of full detection (you can lower to e.g. 5)
                 cooldown=4):          # seconds between spoken alerts
        self.model = YOLO(model_path)
        self.detect_interval = detect_interval
        self.cooldown = cooldown

        self.running = False
        self.last_alert = 0

        self.last_frame = None
        self._last_detect_time = 0
        self._lock = threading.Lock()

        # Danger zone ratios (center rectangle)
        self.zone = (0.25, 0.25, 0.75, 0.85)  # x1,y1,x2,y2 as fractions of width/height

    def _speak_once(self, text):
        # create engine per call to avoid pyttsx3 event-loop issues
        engine = pyttsx3.init()
        engine.say(text)
        engine.runAndWait()
        try:
            engine.stop()
        except Exception:
            pass

    def start(self):
        if not self.running:
            self.running = True
            threading.Thread(target=self._loop, daemon=True).start()

    def stop(self):
        self.running = False

    def _loop(self):
        cap = cv2.VideoCapture(0)
        # read continuously, but run heavy detection only every detect_interval seconds
        while self.running:
            ret, frame = cap.read()
            if not ret:
                time.sleep(0.1)
                continue

            h, w, _ = frame.shape
            x1 = int(w * self.zone[0])
            y1 = int(h * self.zone[1])
            x2 = int(w * self.zone[2])
            y2 = int(h * self.zone[3])

            # always draw danger zone and save last_frame for UI
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)

            now = time.time()
            do_detect = (now - self._last_detect_time) >= self.detect_interval

            if do_detect:
                self._last_detect_time = now

                # run model inference (this may be slow depending on model/hardware)
                results = self.model(frame, verbose=False)

                object_front = False
                person_detected = False

                for r in results:
                    for box in r.boxes:
                        bx1, by1, bx2, by2 = map(int, box.xyxy[0])
                        cls = int(box.cls[0])
                        label = self.model.names[cls]

                        # draw bounding box + label
                        cv2.rectangle(frame, (bx1, by1), (bx2, by2), (0, 255, 0), 2)
                        cv2.putText(frame, label, (bx1, by1 - 6),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

                        # check inside danger zone
                        if bx1 > x1 and bx2 < x2 and by1 > y1 and by2 < y2:
                            object_front = True
                            if label.lower() == "person":
                                person_detected = True

                # speak alert if needed (use cooldown)
                if object_front and (time.time() - self.last_alert) > self.cooldown:
                    # non-blocking speak in its own thread so detection loop isn't blocked
                    threading.Thread(target=self._speak_once,
                                     args=("Be careful, there is an object in front of you",),
                                     daemon=True).start()
                    if person_detected:
                        threading.Thread(target=self._speak_once,
                                         args=("Warning: a person is in front of you",),
                                         daemon=True).start()
                    self.last_alert = time.time()

            # save latest annotated frame for UI (under lock)
            with self._lock:
                self.last_frame = frame.copy()

            # small sleep to keep loop responsive (frame rate)
            time.sleep(0.03)

        cap.release()
