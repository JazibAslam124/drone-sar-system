# from ultralytics import YOLO
# import cv2
# import cvzone
# import math
#
# cap = cv2.VideoCapture(1)
# cap.set(3,1280)
# cap.set(4, 720)
#
# model = YOLO
# import cv2
# from ultralytics import YOLO
#
# model = YOLO('Yolo-Weights/yolov8l.pt')
# results = model("data/1.jpg")  # Remove show=True
#
# # Plot the results onto the image
# annotated = results[0].plot()
#
# cv2.imshow("Detection", annotated)
# cv2.waitKey(0)
# cv2.destroyAllWindows()

















# from ultralytics import YOLO
# import cv2
# import cvzone
# import math
#
# cap = cv2.VideoCapture("data/test_video.mp4")
# # cap.set(3, 1280)
# # cap.set(4,720)
#
# model = YOLO("Yolo-Weights/yolov8l.pt")
#
# classNames = ["person", "bicycle", "car", "motorbike", "aeroplane", "bus", "train", "truck", "boat",
#     "traffic light", "fire hydrant", "stop sign", "parking meter", "bench", "bird", "cat",
#     "dog", "horse", "sheep", "cow", "elephant", "bear", "zebra", "giraffe", "backpack", "umbrella",
#     "handbag", "tie", "suitcase", "frisbee", "skis", "snowboard", "sports ball", "kite", "baseball bat",
#     "baseball glove", "skateboard", "surfboard", "tennis racket", "bottle", "wine glass", "cup",
#     "fork", "knife", "spoon", "bowl", "banana", "apple", "sandwich", "orange", "broccoli",
#     "carrot", "hot dog", "pizza", "donut", "cake", "chair", "sofa", "pottedplant", "bed",
#     "diningtable", "toilet", "tvmonitor", "laptop", "mouse", "remote", "keyboard", "cell phone",
#     "microwave", "oven", "toaster", "sink", "refrigerator", "book", "clock", "vase", "scissors",
#     "teddy bear", "hair drier", "toothbrush"]
#
# while True:
#     success, img = cap.read()
#     results = model(img,stream=True)
#     for r in results:
#         boxes = r.boxes
#         for box in boxes:
#             x1, y1, x2, y2 = box.xyxy[0]
#             x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
#
#             w, h = x2 - x1, y2 - y1
#             cvzone.cornerRect(img, (x1, y1, w, h))
#
#             conf = math.ceil((box.conf[0] * 100))/100
#             cls = box.cls[0]
#
#             cvzone.putTextRect(img, f'{cls}{conf}', (max(0,x1), max(35,y1)))
#
#
#
#     cv2.imshow("Image", img)
#     cv2.waitKey(1)




































# import cv2
# import csv
# import os
# from datetime import datetime
# import torch
#
# # ── Config ───────────────────────────────────────────────────
# VIDEO_PATH  = "data/test_video.mp4"
# OUTPUT_PATH = "data/latest2.mp4"
#
# CONFIDENCE = 0.05   # lower for higher recall
#
# # If using custom CrowdHuman weights:
# # MODEL_WEIGHTS = "best.pt"
# # Otherwise fallback:
# MODEL_WEIGHTS = "yolov5x.pt"
#
# DANGER_ZONE_RATIO = (0.0, 0.0, 0.3, 0.3)
#
#
# # ── Load YOLOv5 ──────────────────────────────────────────────
# print("Loading YOLOv5 model...")
# model = torch.hub.load("ultralytics/yolov5", "custom", path=MODEL_WEIGHTS)
# model.conf = CONFIDENCE
#
#
# # ── Drawing functions ─────────────────────────────────────────
# def draw_danger_zone(frame, w, h):
#     x1 = int(DANGER_ZONE_RATIO[0] * w)
#     y1 = int(DANGER_ZONE_RATIO[1] * h)
#     x2 = int(DANGER_ZONE_RATIO[2] * w)
#     y2 = int(DANGER_ZONE_RATIO[3] * h)
#
#     overlay = frame.copy()
#     cv2.rectangle(overlay, (x1, y1), (x2, y2), (0, 0, 255), -1)
#     cv2.addWeighted(overlay, 0.15, frame, 0.85, 0, frame)
#     cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
#
#     cv2.putText(frame, "DANGER ZONE", (x1 + 5, y1 + 20),
#                 cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
#
#     return (x1, y1, x2, y2)
#
#
# def log_alert(alert):
#     file_exists = os.path.exists("alerts_log.csv")
#     with open("alerts_log.csv", "a", newline="") as f:
#         writer = csv.writer(f)
#         if not file_exists:
#             writer.writerow(["timestamp", "level", "reason", "frame"])
#
#         writer.writerow([
#             datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
#             alert["level"],
#             alert["reason"],
#             alert["frame"]
#         ])
#
#
# # ── Main Pipeline ─────────────────────────────────────────────
# def run():
#     cap = cv2.VideoCapture(VIDEO_PATH)
#     fps = cap.get(cv2.CAP_PROP_FPS) or 25
#
#     width  = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
#     height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
#
#     out = cv2.VideoWriter(
#         OUTPUT_PATH,
#         cv2.VideoWriter_fourcc(*"mp4v"),
#         fps, (width, height)
#     )
#
#     frame_num = 0
#     alerts = []
#
#     print("Processing...")
#
#     while cap.isOpened():
#         ret, frame = cap.read()
#         if not ret:
#             break
#
#         h, w = frame.shape[:2]
#         danger_zone = draw_danger_zone(frame, w, h)
#
#         # ── YOLOv5 inference ──
#         results = model(frame)
#
#         if results.xyxy[0] is None or len(results.xyxy[0]) == 0:
#             detections = []
#         else:
#             detections = results.xyxy[0].cpu().numpy()
#         person_count = 0
#
#         for det in detections:
#             x1, y1, x2, y2, conf, cls = det
#
#             # class 0 = person
#             if int(cls) != 0:
#                 continue
#
#             person_count += 1
#
#             x1, y1, x2, y2 = map(int, [x1, y1, x2, y2])
#
#             # draw box
#             color = (0, 255, 0) if conf > 0.5 else (0, 165, 255)
#
#             cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
#             cv2.putText(frame,
#                         f"{conf:.2f}",
#                         (x1, y1 - 5),
#                         cv2.FONT_HERSHEY_SIMPLEX,
#                         0.4, color, 1)
#
#             # ── Danger zone check ──
#             zx1, zy1, zx2, zy2 = danger_zone
#
#             if (x1 < zx2 and x2 > zx1 and y1 < zy2 and y2 > zy1):
#                 alert = {
#                     "level": "CRITICAL",
#                     "reason": "Person in danger zone",
#                     "frame": frame_num
#                 }
#                 alerts.append(alert)
#                 log_alert(alert)
#
#         # ── HUD ──
#         cv2.putText(frame,
#                     f"Frame:{frame_num} | Persons:{person_count} | Alerts:{len(alerts)}",
#                     (20, 30),
#                     cv2.FONT_HERSHEY_SIMPLEX,
#                     0.6, (255, 255, 255), 2)
#
#         out.write(frame)
#         frame_num += 1
#
#         if frame_num % 100 == 0:
#             print(f"Processed {frame_num} frames...")
#
#     cap.release()
#     out.release()
#
#     print(f"\n✅ Done → {OUTPUT_PATH}")
#     print(f"Frames: {frame_num}")
#     print(f"Alerts: {len(alerts)}")
#
#     return alerts
#
#
# if __name__ == "__main__":
#     run()

























# import cv2
# import torch
# import csv
# import os
# from datetime import datetime
#
# from vision_utils import (
#     enhance_frame,
#     tile_inference,
#     draw_danger_zone,
#     apply_nms
# )
# from decision import DecisionEngine
#
#
# # ── Config ───────────────────────────────────────────────────
# VIDEO_PATH = "data/13207766_2160_3840_60fps.mp4"
# OUTPUT_PATH = "data/02.mp4"
#
# MODEL_WEIGHTS = "Yolo-Weights/yolov5x.pt"
# CONFIDENCE = 0.02
#
#
# # ── Load YOLOv5 ──────────────────────────────────────────────
# print("Loading YOLOv5...")
# model = torch.hub.load(
#     "ultralytics/yolov5",
#     "custom",
#     path=MODEL_WEIGHTS,
#     trust_repo=True
# )
# model.conf = CONFIDENCE
#
#
# # ── Decision Engine ──────────────────────────────────────────
# engine = DecisionEngine()
#
#
# # ── Logging ─────────────────────────────────────────────────
# def log_alert(alert):
#     file_exists = os.path.exists("alerts_log.csv")
#
#     with open("alerts_log.csv", "a", newline="") as f:
#         writer = csv.writer(f)
#
#         if not file_exists:
#             writer.writerow(["timestamp", "level", "reason", "frame"])
#
#         writer.writerow([
#             datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
#             alert["level"],
#             alert["reason"],
#             alert["frame"]
#         ])
#
#
# # ── Main Pipeline ────────────────────────────────────────────
# def run():
#     cap = cv2.VideoCapture(VIDEO_PATH)
#
#     ret, frame = cap.read()
#     if not ret:
#         print("Error reading video")
#         return
#
#     height, width = frame.shape[:2]
#     fps = cap.get(cv2.CAP_PROP_FPS) or 25
#
#     out = cv2.VideoWriter(
#         OUTPUT_PATH,
#         cv2.VideoWriter_fourcc(*"mp4v"),
#         fps, (width, height)
#     )
#
#     frame_num = 0
#     alerts = []
#
#     # 🔥 TEMPORAL MEMORY SETUP
#     last_detections = []
#     memory_frames = 3
#     memory_counter = 0
#
#     print("Processing...")
#
#     while cap.isOpened():
#         ret, frame = cap.read()
#         if not ret:
#             break
#
#         # ── Enhancement ─────────────────────────────
#         enhanced = enhance_frame(frame)
#
#         # ── Detection (tiling + NMS) ────────────────
#         detections = tile_inference(enhanced, model)
#         detections = apply_nms(detections)
#
#         # 🔥 TEMPORAL MEMORY (NEW)
#         if len(detections) == 0 and memory_counter < memory_frames:
#             detections = last_detections
#             memory_counter += 1
#         else:
#             last_detections = detections
#             memory_counter = 0
#
#         # ── Danger Zone ─────────────────────────────
#         danger_zone = draw_danger_zone(frame, width, height)
#
#         person_count = 0
#
#         for det in detections:
#             x1, y1, x2, y2, conf, cls = det
#
#             if int(cls) != 0:
#                 continue
#
#             person_count += 1
#             x1, y1, x2, y2 = map(int, [x1, y1, x2, y2])
#
#             color = (0, 255, 0) if conf > 0.5 else (0, 165, 255)
#
#             # Draw bounding box
#             cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
#             cv2.putText(frame,
#                         f"{conf:.2f}",
#                         (x1, y1 - 5),
#                         cv2.FONT_HERSHEY_SIMPLEX,
#                         0.4, color, 1)
#
#             bbox = (x1, y1, x2, y2)
#
#             # ── Decision Logic ─────────────────────
#             alert = engine.check_danger_zone(bbox, danger_zone)
#             if alert:
#                 alert["frame"] = frame_num
#                 alerts.append(alert)
#                 log_alert(alert)
#
#             alert = engine.check_stationary(bbox, frame_num)
#             if alert:
#                 alert["frame"] = frame_num
#                 alerts.append(alert)
#                 log_alert(alert)
#
#         # ── Cluster Detection ─────────────────────
#         cluster_alert = engine.check_cluster(detections)
#         if cluster_alert:
#             cluster_alert["frame"] = frame_num
#             alerts.append(cluster_alert)
#             log_alert(cluster_alert)
#
#         # ── HUD ───────────────────────────────────
#         cv2.putText(frame,
#                     f"Frame:{frame_num} | Persons:{person_count} | Alerts:{len(alerts)}",
#                     (20, 30),
#                     cv2.FONT_HERSHEY_SIMPLEX,
#                     0.6, (255, 255, 255), 2)
#
#         out.write(frame)
#         frame_num += 1
#
#         if frame_num % 50 == 0:
#             print(f"Processed {frame_num} frames...")
#
#     cap.release()
#     out.release()
#
#     print("\nDone!")
#     print(f"Frames: {frame_num}")
#     print(f"Alerts: {len(alerts)}")
#
#
# if __name__ == "__main__":
#     run()






















# #new04
# import cv2
# import torch
# import csv
# import os
# from datetime import datetime
#
# from vision_utils import (
#     enhance_frame,
#     tile_inference,
#     draw_danger_zone,
#     apply_nms
# )
# from decision import DecisionEngine
#
#
# # ── Config ───────────────────────────────────────────────────
# VIDEO_PATH = "data/13207766_2160_3840_60fps.mp4"
# OUTPUT_PATH = "data/new04.mp4"
#
# MODEL_WEIGHTS = "Yolo-Weights/yolov5x.pt"
# CONFIDENCE = 0.15           # raised from 0.02 — cuts noise
# MEMORY_WEIGHT_FRAMES = 5    # how many frames to persist lost detections
#
#
# # ── Load YOLOv5 ──────────────────────────────────────────────
# print("Loading YOLOv5...")
# model = torch.hub.load(
#     "ultralytics/yolov5",
#     "custom",
#     path=MODEL_WEIGHTS,
#     trust_repo=True
# )
# model.conf = CONFIDENCE
#
#
# # ── Decision Engine ──────────────────────────────────────────
# engine = DecisionEngine()
#
#
# # ── Logging ──────────────────────────────────────────────────
# def log_alert(alert):
#     file_exists = os.path.exists("alerts_log.csv")
#
#     with open("alerts_log.csv", "a", newline="") as f:
#         writer = csv.writer(f)
#
#         if not file_exists:
#             writer.writerow(["timestamp", "level", "reason", "frame"])
#
#         writer.writerow([
#             datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
#             alert["level"],
#             alert["reason"],
#             alert["frame"]
#         ])
#
#
# # ── Main Pipeline ─────────────────────────────────────────────
# def run():
#     cap = cv2.VideoCapture(VIDEO_PATH)
#
#     ret, frame = cap.read()
#     if not ret:
#         print("Error reading video")
#         return
#
#     height, width = frame.shape[:2]
#     fps = cap.get(cv2.CAP_PROP_FPS) or 25
#
#     out = cv2.VideoWriter(
#         OUTPUT_PATH,
#         cv2.VideoWriter_fourcc(*"mp4v"),
#         fps, (width, height)
#     )
#
#     frame_num = 0
#     alerts = []
#
#     # ── Temporal Memory ───────────────────────────────────────
#     last_detections = []
#     memory_counter = 0
#
#     print("Processing...")
#
#     while cap.isOpened():
#         ret, frame = cap.read()
#         if not ret:
#             break
#
#         # ── Enhancement ──────────────────────────────────────
#         enhanced = enhance_frame(frame)
#
#         # ── Detection (tiling + NMS) ─────────────────────────
#         raw_detections = tile_inference(enhanced, model)
#         detections = apply_nms(raw_detections)
#
#         # ── Temporal Memory ───────────────────────────────────
#         # If no detections, carry forward previous ones with
#         # decaying confidence — avoids ghost alerts while
#         # bridging momentary occlusion gaps in crowds
#         if len(detections) == 0:
#             if memory_counter < MEMORY_WEIGHT_FRAMES:
#                 detections = [
#                     [*d[:4], d[4] * 0.7, d[5]]  # decay conf each frame
#                     for d in last_detections
#                 ]
#                 memory_counter += 1
#             # else: stale data is worse than nothing — let it be empty
#         else:
#             last_detections = detections
#             memory_counter = 0
#
#         # ── Danger Zone ───────────────────────────────────────
#         danger_zone = draw_danger_zone(frame, width, height)
#
#         person_count = 0
#
#         for det in detections:
#             x1, y1, x2, y2, conf, cls = det
#
#             if int(cls) != 0:
#                 continue
#
#             person_count += 1
#             x1, y1, x2, y2 = map(int, [x1, y1, x2, y2])
#
#             # Green = confident detection, orange = low-confidence / memory carry
#             color = (0, 255, 0) if conf > 0.5 else (0, 165, 255)
#
#             cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
#             cv2.putText(
#                 frame,
#                 f"{conf:.2f}",
#                 (x1, y1 - 5),
#                 cv2.FONT_HERSHEY_SIMPLEX,
#                 0.4, color, 1
#             )
#
#             bbox = (x1, y1, x2, y2)
#
#             # ── Decision Checks ───────────────────────────────
#             alert = engine.check_danger_zone(bbox, danger_zone)
#             if alert:
#                 alert["frame"] = frame_num
#                 alerts.append(alert)
#                 log_alert(alert)
#
#             alert = engine.check_stationary(bbox, frame_num)
#             if alert:
#                 alert["frame"] = frame_num
#                 alerts.append(alert)
#                 log_alert(alert)
#
#         # ── Cluster Detection ─────────────────────────────────
#         cluster_alert = engine.check_cluster(detections)
#         if cluster_alert:
#             cluster_alert["frame"] = frame_num
#             alerts.append(cluster_alert)
#             log_alert(cluster_alert)
#
#         # ── HUD ───────────────────────────────────────────────
#         cv2.putText(
#             frame,
#             f"Frame:{frame_num} | Persons:{person_count} | Alerts:{len(alerts)}",
#             (20, 30),
#             cv2.FONT_HERSHEY_SIMPLEX,
#             0.6, (255, 255, 255), 2
#         )
#
#         out.write(frame)
#         frame_num += 1
#
#         if frame_num % 50 == 0:
#             print(f"Processed {frame_num} frames | "
#                   f"Persons this frame: {person_count} | "
#                   f"Total alerts: {len(alerts)}")
#
#     cap.release()
#     out.release()
#
#     print("\n── Done ─────────────────────────────")
#     print(f"  Frames processed : {frame_num}")
#     print(f"  Total alerts     : {len(alerts)}")
#     print(f"  Output saved to  : {OUTPUT_PATH}")
#     print(f"  Alert log        : alerts_log.csv")
#
#
# if __name__ == "__main__":
#     run()










import cv2
import csv
import os
from datetime import datetime

from vision_utils import (
    load_model,
    enhance_frame,
    tile_inference,
    draw_danger_zone,
    apply_nms
)
from decision import DecisionEngine


# ── Config ────────────────────────────────────────────────────
VIDEO_PATH = "data/test_video.mp4"
OUTPUT_PATH = "data/LATEST_test_video_output.mp4"

# YOLOv8x gives the best accuracy; swap to yolov8l.pt if too slow
# Download: https://github.com/ultralytics/assets/releases
MODEL_WEIGHTS = "Yolo-Weights/yolov8x.pt"
CONFIDENCE = 0.15
MEMORY_WEIGHT_FRAMES = 5


# ── Load Model (YOLOv8 via SAHI) ─────────────────────────────
print("Loading YOLOv8 + SAHI...")
model = load_model(MODEL_WEIGHTS, confidence=CONFIDENCE)
print("Model loaded.")


# ── Decision Engine ───────────────────────────────────────────
engine = DecisionEngine()


# ── Logging ───────────────────────────────────────────────────
def log_alert(alert):
    file_exists = os.path.exists("alerts_log.csv")

    with open("alerts_log.csv", "a", newline="") as f:
        writer = csv.writer(f)

        if not file_exists:
            writer.writerow(["timestamp", "level", "reason", "frame"])

        writer.writerow([
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            alert["level"],
            alert["reason"],
            alert["frame"]
        ])


# ── Main Pipeline ─────────────────────────────────────────────
def run():
    cap = cv2.VideoCapture(VIDEO_PATH)

    ret, frame = cap.read()
    if not ret:
        print("Error: could not read video file.")
        return

    height, width = frame.shape[:2]
    fps = cap.get(cv2.CAP_PROP_FPS) or 25

    out = cv2.VideoWriter(
        OUTPUT_PATH,
        cv2.VideoWriter_fourcc(*"mp4v"),
        fps, (width, height)
    )

    frame_num = 0
    alerts = []

    # ── Temporal Memory ───────────────────────────────────────
    last_detections = []
    memory_counter = 0

    print("Processing...\n")

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # ── Enhancement ───────────────────────────────────────
        enhanced = enhance_frame(frame)

        # ── SAHI Sliced Inference ─────────────────────────────
        # tile_inference now calls SAHI internally — handles
        # overlapping slices and cross-tile NMS automatically
        raw_detections = tile_inference(enhanced, model)
        detections = apply_nms(raw_detections)  # lightweight cleanup pass

        # ── Temporal Memory ───────────────────────────────────
        if len(detections) == 0:
            if memory_counter < MEMORY_WEIGHT_FRAMES:
                detections = [
                    [*d[:4], d[4] * 0.7, d[5]]  # decay confidence each frame
                    for d in last_detections
                ]
                memory_counter += 1
        else:
            last_detections = detections
            memory_counter = 0

        # ── Danger Zone ───────────────────────────────────────
        danger_zone = draw_danger_zone(frame, width, height)

        person_count = 0

        for det in detections:
            x1, y1, x2, y2, conf, cls = det

            if int(cls) != 0:
                continue

            person_count += 1
            x1, y1, x2, y2 = map(int, [x1, y1, x2, y2])

            # Green = confident, orange = low-conf or memory carry-over
            color = (0, 255, 0) if conf > 0.5 else (0, 165, 255)

            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            cv2.putText(
                frame,
                f"{conf:.2f}",
                (x1, y1 - 5),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.4, color, 1
            )

            bbox = (x1, y1, x2, y2)

            # ── Decision Checks ───────────────────────────────
            alert = engine.check_danger_zone(bbox, danger_zone)
            if alert:
                alert["frame"] = frame_num
                alerts.append(alert)
                log_alert(alert)

            alert = engine.check_stationary(bbox, frame_num)
            if alert:
                alert["frame"] = frame_num
                alerts.append(alert)
                log_alert(alert)

        # ── Cluster Detection ─────────────────────────────────
        cluster_alert = engine.check_cluster(detections)
        if cluster_alert:
            cluster_alert["frame"] = frame_num
            alerts.append(cluster_alert)
            log_alert(cluster_alert)

        # ── HUD ───────────────────────────────────────────────
        cv2.putText(
            frame,
            f"Frame:{frame_num} | Persons:{person_count} | Alerts:{len(alerts)}",
            (20, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6, (255, 255, 255), 2
        )

        out.write(frame)
        frame_num += 1

        if frame_num % 50 == 0:
            print(f"  Frame {frame_num:>5} | Persons: {person_count:>3} | "
                  f"Total alerts: {len(alerts)}")

    cap.release()
    out.release()

    print("\n── Done ──────────────────────────────")
    print(f"  Frames processed : {frame_num}")
    print(f"  Total alerts     : {len(alerts)}")
    print(f"  Output saved to  : {OUTPUT_PATH}")
    print(f"  Alert log        : alerts_log.csv")


if __name__ == "__main__":
    run()