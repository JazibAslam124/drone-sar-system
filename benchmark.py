import cv2
import time
import torch
from ultralytics import YOLO
from vision_utils import load_model, enhance_frame, tile_inference, apply_nms


VIDEO_PATH = "data/test_video.mp4"
TEST_FRAMES = 100  # how many frames to benchmark on


def benchmark_fast():
    model = YOLO("Yolo-Weights/yolov8n.pt")
    model.overrides["imgsz"] = 640

    cap = cv2.VideoCapture(VIDEO_PATH)
    times = []
    detections_per_frame = []
    frame_num = 0

    while cap.isOpened() and frame_num < TEST_FRAMES:
        ret, frame = cap.read()
        if not ret:
            break

        enhanced = enhance_frame(frame)

        start = time.perf_counter()
        results = model(enhanced, verbose=False)[0]
        elapsed = time.perf_counter() - start

        persons = sum(1 for b in results.boxes if int(b.cls) == 0)
        times.append(elapsed)
        detections_per_frame.append(persons)
        frame_num += 1

    cap.release()
    return times, detections_per_frame


def benchmark_deep():
    model = load_model("Yolo-Weights/yolov8x.pt", confidence=0.15)

    cap = cv2.VideoCapture(VIDEO_PATH)
    times = []
    detections_per_frame = []
    frame_num = 0

    while cap.isOpened() and frame_num < TEST_FRAMES:
        ret, frame = cap.read()
        if not ret:
            break

        enhanced = enhance_frame(frame)

        start = time.perf_counter()
        raw = tile_inference(enhanced, model)
        dets = apply_nms(raw)
        elapsed = time.perf_counter() - start

        persons = sum(1 for d in dets if int(d[5]) == 0)
        times.append(elapsed)
        detections_per_frame.append(persons)
        frame_num += 1

    cap.release()
    return times, detections_per_frame


def print_results(name, times, detections):
    avg_time = sum(times) / len(times)
    fps = 1 / avg_time
    avg_persons = sum(detections) / len(detections)
    max_persons = max(detections)

    print(f"\n── {name} ──────────────────────────")
    print(f"  Avg time per frame : {avg_time*1000:.1f} ms")
    print(f"  FPS                : {fps:.1f}")
    print(f"  Avg persons/frame  : {avg_persons:.1f}")
    print(f"  Max persons/frame  : {max_persons}")


if __name__ == "__main__":
    print(f"Benchmarking on {TEST_FRAMES} frames...\n")

    print("Running YOLOv8n (fast model)...")
    fast_times, fast_dets = benchmark_fast()
    print_results("YOLOv8n — Fast Model", fast_times, fast_dets)

    print("\nRunning YOLOv8x + SAHI (deep model)...")
    deep_times, deep_dets = benchmark_deep()
    print_results("YOLOv8x + SAHI — Deep Model", deep_times, deep_dets)

    # Coarse-to-fine estimate
    # Deep runs ~30% of frames, fast runs 100%
    deep_ratio = 0.30
    blended_fps = 1 / (
        (sum(fast_times)/len(fast_times)) +
        (deep_ratio * sum(deep_times)/len(deep_times))
    )
    print(f"\n── Coarse-to-Fine Pipeline (estimated) ────")
    print(f"  Effective FPS      : {blended_fps:.1f}")
    print(f"  (fast every frame + deep on ~30% of frames)")