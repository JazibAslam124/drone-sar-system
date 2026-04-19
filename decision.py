import math
from collections import defaultdict


class DecisionEngine:
    def __init__(self):
        self.history = defaultdict(list)

    def check_danger_zone(self, bbox, danger_zone):
        x1, y1, x2, y2 = bbox
        zx1, zy1, zx2, zy2 = danger_zone

        if (x1 < zx2 and x2 > zx1 and y1 < zy2 and y2 > zy1):
            return {"level": "CRITICAL", "reason": "Person in danger zone"}
        return None

    # def check_stationary(self, bbox, frame_num):
    #     x1, y1, x2, y2 = bbox
    #     cx = (x1 + x2) / 2
    #     cy = (y1 + y2) / 2
    #
    #     key = int(cx // 50), int(cy // 50)
    #     self.history[key].append((frame_num, cx, cy))
    #     self.history[key] = self.history[key][-10:]
    #
    #     if len(self.history[key]) < 5:
    #         return None
    #
    #     first = self.history[key][0]
    #     last = self.history[key][-1]
    #
    #     dist = math.hypot(last[1] - first[1], last[2] - first[2])
    #
    #     if dist < 10:
    #         return {"level": "WARNING", "reason": "Person appears stationary"}
    #
    #     return None

    def check_stationary(self, bbox, frame_num, track_id=None):
        x1, y1, x2, y2 = bbox
        cx = (x1 + x2) / 2
        cy = (y1 + y2) / 2

        # Key by track ID if available, else by position cell
        # The old approach merged different people in the same cell
        key = track_id if track_id is not None else (int(cx // 50), int(cy // 50))

        self.history[key].append((frame_num, cx, cy))
        self.history[key] = self.history[key][-10:]

        if len(self.history[key]) < 5:
            return None

        first = self.history[key][0]
        last = self.history[key][-1]

        # Guard: require enough elapsed frames to avoid false positives
        if (last[0] - first[0]) < 4:
            return None

        dist = math.hypot(last[1] - first[1], last[2] - first[2])

        if dist < 10:
            return {"level": "WARNING", "reason": "Person appears stationary"}

        return None

    def check_cluster(self, detections):
        centers = []

        for det in detections:
            x1, y1, x2, y2, conf, cls = det
            if int(cls) != 0:
                continue

            cx = (x1 + x2) / 2
            cy = (y1 + y2) / 2
            centers.append((cx, cy))

        if len(centers) < 3:
            return None

        close_count = 0

        for i in range(len(centers)):
            for j in range(i + 1, len(centers)):
                dist = math.hypot(
                    centers[i][0] - centers[j][0],
                    centers[i][1] - centers[j][1]
                )

                if dist < 100:
                    close_count += 1

        if close_count >= 3:
            return {"level": "WARNING", "reason": "People clustered together"}

        return None