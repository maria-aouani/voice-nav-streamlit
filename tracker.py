# tracker.py
import time
import threading
import geopy.distance
from voice import speak_eng
import re

class NavigatorTracker:
    def __init__(self, steps,
                 min_move_meters=3,
                 stop_threshold_seconds=20,
                 off_route_threshold=40,
                 next_step_threshold=20):
        self.steps = steps
        self.running = False
        self.current_step = 0
        self.last_position = None
        self.last_move_time = time.time()
        self._last_instruction_pos = None

        self.min_move_meters = min_move_meters
        self.stop_threshold_seconds = stop_threshold_seconds
        self.off_route_threshold = off_route_threshold
        self.next_step_threshold = next_step_threshold

    def update_position(self, lat, lon):
        """Call this from main.py whenever GPS updates."""
        self.last_position = (lat, lon)

    def start(self):
        if not self.running:
            self.running = True
            threading.Thread(target=self.loop, daemon=True).start()

    def stop(self):
        self.running = False

    def loop(self):
        if len(self.steps) == 0:
            return

        # Speak first instruction immediately
        first = self.steps[0]
        inst = first.get("html_instructions", "")
        inst_text = re.sub(r"<[^>]+>", "", inst)
        speak_eng(inst_text)
        self._last_instruction_pos = self.last_position
        self.last_move_time = time.time()

        while self.running and self.current_step < len(self.steps):
            self._stopped = False
            if self.last_position is None:
                time.sleep(0.5)
                continue

            # Check if user moved
            if self._last_instruction_pos:
                moved_since_inst = geopy.distance.distance(
                    self.last_position, self._last_instruction_pos
                ).meters
            else:
                moved_since_inst = float("inf")

            # Stopped for too long
            if time.time() - self.last_move_time > self.stop_threshold_seconds:
                #speak_eng("It seems you are standing still for a long time. Do you want to stop the navigation?")
                self._stopped = True
                self.last_move_time = time.time()

            step = self.steps[self.current_step]
            start_pos = (step["start_location"]["lat"], step["start_location"]["lng"])
            end_pos = (step["end_location"]["lat"], step["end_location"]["lng"])

            # Check off-route
            off_dist = geopy.distance.distance(self.last_position, start_pos).meters
            if off_dist > self.off_route_threshold:
                speak_eng("Warning. You seem to be going the wrong way.")

                # Repeat instruction if off-route
                inst_html = step.get("html_instructions", "")
                inst_text = re.sub(r"<[^>]+>", "", inst_html)
                speak_eng(inst_text)
                time.sleep(2)  # prevent spam

            # Check if reached current step
            step_dist = geopy.distance.distance(self.last_position, end_pos).meters
            if step_dist < self.next_step_threshold:
                self.current_step += 1
                self._last_instruction_pos = self.last_position
                self.last_move_time = time.time()
                if self.current_step < len(self.steps):
                    next_step = self.steps[self.current_step]
                    inst_html = next_step.get("html_instructions", "")
                    inst_text = re.sub(r"<[^>]+>", "", inst_html)
                    speak_eng(inst_text)
                continue

            # Speak instruction if moved enough since last instruction
            if moved_since_inst >= self.min_move_meters:
                inst_html = step.get("html_instructions", "")
                inst_text = re.sub(r"<[^>]+>", "", inst_html)
                speak_eng(inst_text)
                self._last_instruction_pos = self.last_position
                self.last_move_time = time.time()

            time.sleep(0.5)
