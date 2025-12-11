import time

class GPSSimulator:
    def __init__(self, route_steps, interval=5):
        """
        route_steps: список координат [(lat, lon), ...] маршрута
        interval: время между обновлениями в секундах
        """
        self.route_steps = route_steps
        self.interval = interval
        self.index = 0
        self.current = self.route_steps[0]

    def start(self):
        for coord in self.route_steps:
            self.current = coord
            yield self.current
            time.sleep(self.interval)
