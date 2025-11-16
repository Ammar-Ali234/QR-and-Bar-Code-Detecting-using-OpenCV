import streamlit as st
import cv2
import numpy as np
import zxingcpp
from PIL import Image
import time
import io

# --------------------------
# Streamlit Page Config
# --------------------------
st.set_page_config(
    page_title="QR / Barcode Scanner",
    layout="wide",
    page_icon="📷"
)

# --------------------------
# Custom Dark UI Styling
# --------------------------
st.markdown("""
    <style>
        body {
            background-color: #0E1117;
        }
        .stApp {
            background-color: #0E1117;
        }
        .title {
            color: white;
            text-align: center;
            font-size: 42px;
            font-weight: 700;
            padding-bottom: 20px;
        }
        .subheader {
            color: #D0D3D4;
        }
        .scanner-box {
            border: 3px solid #1F618D;
            border-radius: 10px;
            padding: 12px;
            background: #1B2631;
        }
    </style>
""", unsafe_allow_html=True)

# --------------------------
# ZXing Decode Function
# --------------------------
def decode_zxing(frame):
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = []
    decoded = zxingcpp.read_barcodes(rgb)

    for d in decoded:
        text = d.text
        fmt = str(d.format)

        label = "QR" if "QR" in fmt else "BARCODE"
        pos = d.position

        pts = [
            (int(pos.top_left.x), int(pos.top_left.y)),
            (int(pos.top_right.x), int(pos.top_right.y)),
            (int(pos.bottom_right.x), int(pos.bottom_right.y)),
            (int(pos.bottom_left.x), int(pos.bottom_left.y))
        ]
        results.append((label, text, pts))

    return results


# --------------------------
# Draw Detection + Laser Line
# --------------------------
def draw_results(frame, results, animate_line=False, frame_num=0):
    h, w = frame.shape[:2]

    if animate_line:
        laser_y = (frame_num * 5) % h
        cv2.line(frame, (0, laser_y), (w, laser_y), (0, 0, 255), 2)

    for label, text, pts in results:
        color = (0, 255, 0) if label == "QR" else (255, 0, 0)

        for i in range(4):
            cv2.line(frame, pts[i], pts[(i + 1) % 4], color, 2)

        x, y = pts[0]
        cv2.putText(frame, f"{label}: {text}", (x, y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

    return frame


# --------------------------
# Resize Frame to 640x640
# --------------------------
def resize_640(img):
    return cv2.resize(img, (640, 640))


# --------------------------
# Detection History Tracker
# --------------------------
if "history" not in st.session_state:
    st.session_state.history = []


# --------------------------
# Main Title
# --------------------------
st.markdown('<div class="title">📷 QR / Barcode Scanner Pro</div>', unsafe_allow_html=True)

mode = st.sidebar.radio("Choose Mode", ["Upload Image", "Use Webcam Scanner"])


# ============================================================
# 1️⃣ IMAGE UPLOAD MODE
# ============================================================
if mode == "Upload Image":
    st.markdown("### 📤 Upload an Image", unsafe_allow_html=True)

    uploaded = st.file_uploader("Upload JPG/PNG", type=["jpg", "jpeg", "png"])

    if uploaded:
        image = Image.open(uploaded).convert("RGB")
        frame = np.array(image)

        results = decode_zxing(frame)
        processed = draw_results(frame.copy(), results, animate_line=False)
        processed = resize_640(processed)

        # Show results
        st.image(processed, caption="Processed Image (640×640)", use_column_width=False)

        # Add to History
        for label, text, _ in results:
            st.session_state.history.append(f"{label}: {text}")

        # Download Button
        _, center, _ = st.columns([2, 2, 2])
        with center:
            img_bytes = cv2.imencode(".png", processed)[1].tobytes()
            st.download_button(
                label="📥 Download Result",
                data=img_bytes,
                file_name="annotated_result.png",
                mime="image/png"
            )


# ============================================================
# 2️⃣ LIVE WEBCAM MODE
# ============================================================
elif mode == "Use Webcam Scanner":
    st.markdown("### 🎥 Live Webcam Scanner", unsafe_allow_html=True)

    run = st.checkbox("▶ Start Webcam")
    laser = st.checkbox("🔦 Enable Scanning Line Animation")

    frame_placeholder = st.empty()
    frame_num = 0

    if run:
        cap = cv2.VideoCapture(0)

        while run:
            ret, frame = cap.read()
            if not ret:
                st.error("Webcam not detected.")
                break

            frame = resize_640(frame)
            results = decode_zxing(frame)
            frame = draw_results(frame, results, animate_line=laser, frame_num=frame_num)
            frame_num += 1

            frame_placeholder.image(frame, channels="BGR")

            # Log history
            for label, text, _ in results:
                st.session_state.history.append(f"{label}: {text}")

            run = st.checkbox("▶ Webcam Running", value=True)

        cap.release()


# ============================================================
# 📁 Detection History Panel
# ============================================================
st.markdown("### 🗂 Detection History")
if len(st.session_state.history) == 0:
    st.info("No detections yet.")
else:
    for h in reversed(st.session_state.history[-10:]):
        st.success(h)
