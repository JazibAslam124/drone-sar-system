import streamlit as st
import tempfile
import os
from ultralytics import YOLO
from vision_utils import load_model, enhance_frame, tile_inference, draw_danger_zone, apply_nms
from decision import DecisionEngine
from datetime import datetime
import cv2
import pandas as pd

# ── Page config ───────────────────────────────────────────────
st.set_page_config(
    page_title="Drone SAR System",
    page_icon="🚁",
    layout="wide"
)

st.markdown("""
<style>
    .block-container { padding-top: 2rem; }
    .section-label {
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        color: #888;
        margin-bottom: 4px;
    }
</style>
""", unsafe_allow_html=True)


# ── Re-encode to H.264 for browser playback ───────────────────
def reencode_for_browser(input_path, output_path):
    os.system(f'ffmpeg -y -i "{input_path}" -vcodec libx264 -crf 23 -preset fast "{output_path}"')


# ── Model loader (cached so it only loads once) ───────────────
@st.cache_resource
def get_models():
    fast = YOLO("Yolo-Weights/yolov8n.pt")
    fast.overrides["imgsz"] = 640
    deep = load_model("Yolo-Weights/yolov8x.pt", confidence=0.15)
    return fast, deep


# ── Process uploaded video ────────────────────────────────────
def process_video(input_path, output_path, progress_bar, status_text):
    fast_model, deep_model = get_models()
    engine = DecisionEngine()

    cap = cv2.VideoCapture(input_path)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS) or 25
    ret, frame = cap.read()
    if not ret:
        return []

    h, w = frame.shape[:2]
    out = cv2.VideoWriter(output_path, cv2.VideoWriter_fourcc(*"mp4v"), fps, (w, h))

    alerts = []
    last_detections = []
    memory_counter = 0
    frame_num = 0
    DEEP_INTERVAL = 30
    MEMORY_FRAMES = 5

    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        enhanced = enhance_frame(frame)

        # Fast pass
        fast_results = fast_model(enhanced, verbose=False)[0]
        fast_dets = []
        for box in fast_results.boxes:
            x1, y1, x2, y2 = box.xyxy[0].tolist()
            conf = float(box.conf)
            cls = int(box.cls)
            if conf >= 0.25:
                fast_dets.append([x1, y1, x2, y2, conf, cls])

        fast_hit = any(int(d[5]) == 0 for d in fast_dets)
        run_deep = fast_hit or (frame_num % DEEP_INTERVAL == 0)

        if run_deep:
            raw = tile_inference(enhanced, deep_model)
            detections = apply_nms(raw)
            scan = "DEEP"
        else:
            detections = fast_dets
            scan = "fast"

        if len(detections) == 0:
            if memory_counter < MEMORY_FRAMES:
                detections = [[*d[:4], d[4] * 0.7, d[5]] for d in last_detections]
                memory_counter += 1
        else:
            last_detections = detections
            memory_counter = 0

        danger_zone = draw_danger_zone(frame, w, h)
        person_count = 0

        for det in detections:
            x1, y1, x2, y2, conf, cls = det
            if int(cls) != 0:
                continue
            person_count += 1
            x1, y1, x2, y2 = map(int, [x1, y1, x2, y2])
            color = (0, 255, 0) if conf > 0.5 else (0, 165, 255)
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            cv2.putText(frame, f"{conf:.2f}", (x1, y1 - 5),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.4, color, 1)
            bbox = (x1, y1, x2, y2)

            alert = engine.check_danger_zone(bbox, danger_zone)
            if alert:
                alert["frame"] = frame_num
                alert["timestamp"] = datetime.now().strftime("%H:%M:%S")
                alerts.append(alert)

            alert = engine.check_stationary(bbox, frame_num)
            if alert:
                alert["frame"] = frame_num
                alert["timestamp"] = datetime.now().strftime("%H:%M:%S")
                alerts.append(alert)

        cluster_alert = engine.check_cluster(detections)
        if cluster_alert:
            cluster_alert["frame"] = frame_num
            cluster_alert["timestamp"] = datetime.now().strftime("%H:%M:%S")
            alerts.append(cluster_alert)

        cv2.putText(frame,
                    f"Frame:{frame_num} | Scan:{scan} | Persons:{person_count} | Alerts:{len(alerts)}",
                    (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

        out.write(frame)
        frame_num += 1

        if total_frames > 0:
            progress_bar.progress(min(frame_num / total_frames, 1.0))
            status_text.text(f"Frame {frame_num}/{total_frames} — {person_count} persons detected")

    cap.release()
    out.release()
    return alerts


# ════════════════════════════════════════════════════════════════
# UI
# ════════════════════════════════════════════════════════════════

st.title("🚁 Drone SAR Detection System")
st.caption("Search & Rescue — coarse-to-fine dual-model pipeline · YOLOv8n + YOLOv8x + SAHI")
st.divider()

col_demo, col_sep, col_user = st.columns([1, 0.05, 1])

# ── LEFT: Demo result ─────────────────────────────────────────
with col_demo:
    st.markdown("### 🎬 Demo Result")
    st.caption("Pre-processed SAR footage using the full pipeline")

    DEMO_PATH  = "data/LATEST_test_video_output.mp4"
    DEMO_H264  = "data/LATEST_test_video_output_h264.mp4"

    if os.path.exists(DEMO_PATH):
        # Re-encode once to H.264 so browser can play it
        if not os.path.exists(DEMO_H264):
            with st.spinner("Preparing demo video for playback..."):
                reencode_for_browser(DEMO_PATH, DEMO_H264)

        if os.path.exists(DEMO_H264):
            with open(DEMO_H264, "rb") as f:
                demo_bytes = f.read()
            st.video(demo_bytes)
            st.download_button(
                "⬇ Download Demo Video",
                demo_bytes,
                file_name="sar_demo_output.mp4",
                mime="video/mp4",
                use_container_width=True
            )
        else:
            st.error("ffmpeg re-encode failed. Make sure ffmpeg is installed and on PATH.")
    else:
        st.info("No demo video found at `data/LATEST_test_video_output.mp4`.\nRun `python main.py` first to generate it.")

# ── SEPARATOR ─────────────────────────────────────────────────
with col_sep:
    st.markdown(
        "<div style='border-left:1px solid #333; height:600px; margin:auto;'></div>",
        unsafe_allow_html=True
    )

# ── RIGHT: User upload ────────────────────────────────────────
with col_user:
    st.markdown("### 📤 Process Your Own Video")
    st.caption("Upload any drone footage MP4 to run detection")

    uploaded = st.file_uploader("Choose an MP4 file", type=["mp4"], label_visibility="collapsed")

    if uploaded:
        st.success(f"Uploaded: `{uploaded.name}` ({uploaded.size / 1e6:.1f} MB)")

        if st.button("▶ Run Detection", type="primary", use_container_width=True):

            # Save upload to temp file
            tmp_in = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
            tmp_in.write(uploaded.read())
            tmp_in.close()

            tmp_out = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
            tmp_out.close()

            st.markdown("**Processing...**")
            progress = st.progress(0)
            status   = st.empty()

            alerts = process_video(tmp_in.name, tmp_out.name, progress, status)
            status.text("✅ Done! Re-encoding for playback...")

            # Re-encode result to H.264 for browser
            tmp_h264 = tempfile.NamedTemporaryFile(delete=False, suffix="_h264.mp4")
            tmp_h264.close()
            reencode_for_browser(tmp_out.name, tmp_h264.name)

            status.text("✅ Complete!")

            # Show result video
            st.markdown("**Result:**")
            if os.path.exists(tmp_h264.name):
                with open(tmp_h264.name, "rb") as f:
                    result_bytes = f.read()
                st.video(result_bytes)
            else:
                st.error("Re-encode failed — make sure ffmpeg is installed.")

            # Alert summary
            if alerts:
                critical = sum(1 for a in alerts if a.get("level") == "CRITICAL")
                warning  = sum(1 for a in alerts if a.get("level") == "WARNING")

                m1, m2, m3 = st.columns(3)
                m1.metric("Total Alerts", len(alerts))
                m2.metric("🔴 Critical",  critical)
                m3.metric("🟠 Warning",   warning)

                df = pd.DataFrame(alerts)[["timestamp", "level", "reason", "frame"]]
                df.columns = ["Time", "Level", "Reason", "Frame"]
                st.dataframe(df, use_container_width=True, height=180)

                st.download_button(
                    "⬇ Download Alert Log (CSV)",
                    df.to_csv(index=False),
                    file_name="alerts_log.csv",
                    mime="text/csv",
                    use_container_width=True
                )
            else:
                st.info("No alerts generated for this video.")

            if os.path.exists(tmp_h264.name):
                st.download_button(
                    "⬇ Download Processed Video",
                    result_bytes,
                    file_name="sar_output.mp4",
                    mime="video/mp4",
                    use_container_width=True
                )

            # Cleanup raw temp files (keep h264 until session ends)
            os.unlink(tmp_in.name)
            os.unlink(tmp_out.name)

    else:
        st.markdown("""
        <div style='
            border: 2px dashed #333;
            border-radius: 12px;
            padding: 48px 24px;
            text-align: center;
            color: #666;
            margin-top: 16px;
        '>
            <div style='font-size: 2rem;'>📁</div>
            <div style='margin-top: 8px;'>Drop your MP4 here or click above to browse</div>
            <div style='font-size: 0.8rem; margin-top: 4px;'>Drone footage works best</div>
        </div>
        """, unsafe_allow_html=True)