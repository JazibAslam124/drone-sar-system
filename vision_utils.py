# import cv2
# import numpy as np
#
#
# def enhance_frame(frame):
#     lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
#     l, a, b = cv2.split(lab)
#
#     clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
#     l = clahe.apply(l)
#
#     enhanced = cv2.merge((l, a, b))
#     return cv2.cvtColor(enhanced, cv2.COLOR_LAB2BGR)
#
#
# def tile_inference(frame, model):
#     h, w = frame.shape[:2]
#     detections = []
#
#     tile_h = h // 2
#     tile_w = w // 2
#
#     for y in range(0, h, tile_h):
#         for x in range(0, w, tile_w):
#             tile = frame[y:y+tile_h, x:x+tile_w]
#
#             results = model(tile)
#             preds = results.xyxy[0]
#
#             if preds is None or len(preds) == 0:
#                 continue
#
#             for det in preds:
#                 x1, y1, x2, y2, conf, cls = det.tolist()
#
#                 detections.append([
#                     x1 + x,
#                     y1 + y,
#                     x2 + x,
#                     y2 + y,
#                     conf,
#                     cls
#                 ])
#
#     return detections
#
#
# # 🔥 CROSS-TILE NMS
# def apply_nms(detections, iou_threshold=0.5):
#     if len(detections) == 0:
#         return []
#
#     boxes = np.array([det[:4] for det in detections])
#     scores = np.array([det[4] for det in detections])
#     classes = np.array([det[5] for det in detections])
#
#     indices = cv2.dnn.NMSBoxes(
#         boxes.tolist(),
#         scores.tolist(),
#         score_threshold=0.01,
#         nms_threshold=iou_threshold
#     )
#
#     if len(indices) == 0:
#         return []
#
#     filtered = []
#     for i in indices.flatten():
#         filtered.append(detections[i])
#
#     return filtered
#
#
# def draw_danger_zone(frame, w, h):
#     x1 = int(0.0 * w)
#     y1 = int(0.0 * h)
#     x2 = int(0.3 * w)
#     y2 = int(0.3 * h)
#
#     overlay = frame.copy()
#     cv2.rectangle(overlay, (x1, y1), (x2, y2), (0, 0, 255), -1)
#     cv2.addWeighted(overlay, 0.15, frame, 0.85, 0, frame)
#     cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
#
#     cv2.putText(frame, "DANGER ZONE",
#                 (x1 + 5, y1 + 20),
#                 cv2.FONT_HERSHEY_SIMPLEX,
#                 0.6, (0, 0, 255), 2)
#
#     return (x1, y1, x2, y2)





# #new04
# import cv2
# import numpy as np
#
#
# # ── Shadow Enhancement ───────────────────────────────────────
# def enhance_frame(frame):
#     lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
#     l, a, b = cv2.split(lab)
#
#     clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
#     l = clahe.apply(l)
#
#     enhanced = cv2.merge((l, a, b))
#     return cv2.cvtColor(enhanced, cv2.COLOR_LAB2BGR)
#
#
# # ── 3x3 Tiling (UPDATED) ─────────────────────────────────────
# # def tile_inference(frame, model):
# #     h, w = frame.shape[:2]
# #     detections = []
# #
# #     grid_size = 3  # 🔥 upgraded from 2 → 3
# #     tile_h = h // grid_size
# #     tile_w = w // grid_size
# #
# #     for y in range(0, h, tile_h):
# #         for x in range(0, w, tile_w):
# #             tile = frame[y:y+tile_h, x:x+tile_w]
# #
# #             results = model(tile)
# #             preds = results.xyxy[0]
# #
# #             if preds is None or len(preds) == 0:
# #                 continue
# #
# #             for det in preds:
# #                 x1, y1, x2, y2, conf, cls = det.tolist()
# #
# #                 detections.append([
# #                     x1 + x,
# #                     y1 + y,
# #                     x2 + x,
# #                     y2 + y,
# #                     conf,
# #                     cls
# #                 ])
# #
# #     return detections
# #
# #
# # # ── Improved NMS ─────────────────────────────────────────────
# # def apply_nms(detections, iou_threshold=0.4):  # 🔥 lowered from 0.5
# #     if len(detections) == 0:
# #         return []
# #
# #     boxes = np.array([det[:4] for det in detections])
# #     scores = np.array([det[4] for det in detections])
# #
# #     indices = cv2.dnn.NMSBoxes(
# #         boxes.tolist(),
# #         scores.tolist(),
# #         score_threshold=0.01,
# #         nms_threshold=iou_threshold
# #     )
# #
# #     if len(indices) == 0:
# #         return []
# #
# #     return [detections[i] for i in indices.flatten()]
# #
#
# def tile_inference(frame, model, overlap=0.2):
#     h, w = frame.shape[:2]
#     detections = []
#
#     grid_size = 3
#     tile_h = h // grid_size
#     tile_w = w // grid_size
#
#     stride_h = int(tile_h * (1 - overlap))  # step with overlap
#     stride_w = int(tile_w * (1 - overlap))
#
#     for y in range(0, h - tile_h + 1, stride_h):
#         for x in range(0, w - tile_w + 1, stride_w):
#             tile = frame[y:y+tile_h, x:x+tile_w]
#             results = model(tile)
#             preds = results.xyxy[0]
#
#             if preds is None or len(preds) == 0:
#                 continue
#
#             for det in preds:
#                 x1, y1, x2, y2, conf, cls = det.tolist()
#                 detections.append([
#                     x1 + x, y1 + y,
#                     x2 + x, y2 + y,
#                     conf, cls
#                 ])
#
#     return detections
#
#
# def apply_nms(detections, iou_threshold=0.45):
#     if len(detections) == 0:
#         return []
#
#     boxes = np.array([det[:4] for det in detections])
#     scores = np.array([det[4] for det in detections])
#
#     # Use area-aware NMS — important for drone/top-down views
#     # where people appear small and close together
#     x1, y1, x2, y2 = boxes[:,0], boxes[:,1], boxes[:,2], boxes[:,3]
#     areas = (x2 - x1) * (y2 - y1)
#
#     # Soft-NMS style: penalise score by overlap rather than hard-remove
#     indices = cv2.dnn.NMSBoxes(
#         boxes.tolist(),
#         scores.tolist(),
#         score_threshold=0.15,   # raise floor to cut noise
#         nms_threshold=iou_threshold
#     )
#
#     if len(indices) == 0:
#         return []
#
#     return [detections[i] for i in indices.flatten()]
#
#
#
# # ── Danger Zone ──────────────────────────────────────────────
# def draw_danger_zone(frame, w, h):
#     x1 = int(0.0 * w)
#     y1 = int(0.0 * h)
#     x2 = int(0.3 * w)
#     y2 = int(0.3 * h)
#
#     overlay = frame.copy()
#     cv2.rectangle(overlay, (x1, y1), (x2, y2), (0, 0, 255), -1)
#     cv2.addWeighted(overlay, 0.15, frame, 0.85, 0, frame)
#     cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
#
#     cv2.putText(frame, "DANGER ZONE",
#                 (x1 + 5, y1 + 20),
#                 cv2.FONT_HERSHEY_SIMPLEX,
#                 0.6, (0, 0, 255), 2)
#
#     return (x1, y1, x2, y2)




import cv2
import numpy as np
from sahi import AutoDetectionModel
from sahi.predict import get_sliced_prediction


# ── Shadow / Contrast Enhancement ────────────────────────────
def enhance_frame(frame):
    lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)

    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    l = clahe.apply(l)

    enhanced = cv2.merge((l, a, b))
    return cv2.cvtColor(enhanced, cv2.COLOR_LAB2BGR)


# ── SAHI Sliced Inference (replaces manual tile_inference) ────
def tile_inference(frame, model):
    """
    Uses SAHI's get_sliced_prediction instead of manual tiling.
    - slice_height/width: size of each slice in pixels
    - overlap_height/width_ratio: 20% overlap so no person is cut at edges
    - Merging + cross-tile NMS is handled automatically by SAHI
    """
    # SAHI expects a PIL image or file path — convert BGR → RGB
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    result = get_sliced_prediction(
        frame_rgb,
        model,
        slice_height=640,
        slice_width=640,
        overlap_height_ratio=0.2,
        overlap_width_ratio=0.2,
        postprocess_type="NMM",       # Non-Maximum Merging — better than NMS for crowds
        postprocess_match_threshold=0.5,
        verbose=0
    )

    detections = []
    for obj in result.object_prediction_list:
        bbox = obj.bbox
        x1, y1, x2, y2 = bbox.minx, bbox.miny, bbox.maxx, bbox.maxy
        conf = obj.score.value
        cls = obj.category.id      # 0 = person in COCO

        detections.append([x1, y1, x2, y2, conf, cls])

    return detections


# ── NMS (kept as a safety net after SAHI merging) ────────────
def apply_nms(detections, iou_threshold=0.45):
    """
    SAHI already handles cross-tile NMS internally.
    This is a lightweight cleanup pass for any remaining overlaps.
    """
    if len(detections) == 0:
        return []

    boxes = np.array([det[:4] for det in detections])
    scores = np.array([det[4] for det in detections])

    indices = cv2.dnn.NMSBoxes(
        boxes.tolist(),
        scores.tolist(),
        score_threshold=0.15,
        nms_threshold=iou_threshold
    )

    if len(indices) == 0:
        return []

    return [detections[i] for i in indices.flatten()]


# ── Danger Zone ───────────────────────────────────────────────
def draw_danger_zone(frame, w, h):
    x1 = int(0.0 * w)
    y1 = int(0.0 * h)
    x2 = int(0.3 * w)
    y2 = int(0.3 * h)

    overlay = frame.copy()
    cv2.rectangle(overlay, (x1, y1), (x2, y2), (0, 0, 255), -1)
    cv2.addWeighted(overlay, 0.15, frame, 0.85, 0, frame)
    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)

    cv2.putText(frame, "DANGER ZONE",
                (x1 + 5, y1 + 20),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6, (0, 0, 255), 2)

    return (x1, y1, x2, y2)


# ── Model Loader (call once in main.py) ──────────────────────
def load_model(weights_path, confidence=0.15):
    import torch
    device = "cuda:0" if torch.cuda.is_available() else "cpu"
    print(f"Using device: {device}")

    detection_model = AutoDetectionModel.from_pretrained(
        model_type="ultralytics",
        model_path=weights_path,
        confidence_threshold=confidence,
        device=device,
    )
    detection_model.model.overrides["imgsz"] = 640  # drop to 640 to test first
    return detection_model