
import cv2
import zxingcpp

def decode_zxing(frame):
    # ZXing works best with RGB
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    results = []
    decoded = zxingcpp.read_barcodes(rgb)

    for d in decoded:
        # Barcode text
        text = d.text

        # Barcode type (QR_CODE, EAN_13, CODE_128, etc.)
        fmt = str(d.format)

        # Convert to simple label
        if "QR" in fmt:
            label = "QR"
        else:
            label = "BARCODE"

        # 4 corner points
        pos = d.position
        pts = [
            (int(pos.top_left.x), int(pos.top_left.y)),
            (int(pos.top_right.x), int(pos.top_right.y)),
            (int(pos.bottom_right.x), int(pos.bottom_right.y)),
            (int(pos.bottom_left.x), int(pos.bottom_left.y))
        ]

        results.append((label, text, pts))

    return results


def draw_results(frame, results):
    for label, text, pts in results:
        color = (0, 255, 0) if label == "QR" else (255, 0, 0)

        # Draw polygon
        for i in range(len(pts)):
            cv2.line(frame, pts[i], pts[(i + 1) % len(pts)], color, 2)

        # Label text above
        x, y = pts[0]
        cv2.putText(frame, f"{label}: {text}", (x, y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

    return frame


def main():
    # Webcam: cap = cv2.VideoCapture(0)
    # IP camera example: cap = cv2.VideoCapture("http://ip:port/video")
    #cap = cv2.VideoCapture("http://172.16.52.156:4747/video")
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Could not open camera")
        return

    print("ZXingCPP Scanner running... Press Q to quit")

    while True:
        ret, frame = cap.read()
        if not ret:
            continue

        # Decode using ZXingCPP
        results = decode_zxing(frame)

        # Draw detected results
        output = draw_results(frame, results)

        cv2.imshow("ZXingCPP QR + Barcode Scanner", output)

        # Exit
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
