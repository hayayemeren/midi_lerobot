#!/usr/bin/env python3
"""
Live Camera Focus & Preview Server for LeRobot.
Streams camera feeds over HTTP (MJPEG) so you can view the live image in your web browser
from any phone, laptop, or desktop on the network to adjust the lens focus.
Also displays a real-time Focus Sharpness score (Laplacian Variance).
"""

import os
import sys
import time
import argparse
from pathlib import Path
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
import cv2
import numpy as np

# Load config
SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))
from config_helper import get_resolved_config

cameras_dict = {}
active_caps = {}
lock = threading.Lock()

def calculate_sharpness(frame):
    """Calculates the Focus Measure (Variance of Laplacian). Higher = Sharper."""
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    return cv2.Laplacian(gray, cv2.CV_64F).var()

def camera_worker(cam_id, dev_path, width, height, fps):
    global active_caps
    idx_or_path = int(dev_path) if (isinstance(dev_path, str) and dev_path.isdigit()) else dev_path
    cap = cv2.VideoCapture(idx_or_path, cv2.CAP_V4L2)
    if not cap.isOpened():
        cap = cv2.VideoCapture(idx_or_path)
        
    if not cap.isOpened():
        print(f"[ERROR] Could not open camera '{cam_id}' at {dev_path}")
        return

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
    cap.set(cv2.CAP_PROP_FPS, fps)
    
    with lock:
        active_caps[cam_id] = {"cap": cap, "latest_frame": None, "sharpness": 0.0, "fps": 0.0}

    last_time = time.time()
    frame_count = 0
    measured_fps = fps

    while True:
        ret, frame = cap.read()
        if not ret or frame is None:
            time.sleep(0.01)
            continue
            
        frame_count += 1
        now = time.time()
        if now - last_time >= 1.0:
            measured_fps = frame_count / (now - last_time)
            frame_count = 0
            last_time = now

        sharpness = calculate_sharpness(frame)
        
        # Overlay visual focus assistance
        h, w, _ = frame.shape
        overlay = frame.copy()
        
        # Semi-transparent HUD header
        cv2.rectangle(overlay, (0, 0), (w, 55), (20, 20, 20), -1)
        frame = cv2.addWeighted(overlay, 0.7, frame, 0.3, 0)
        
        # Color based on sharpness
        sharp_color = (0, 255, 0) if sharpness > 100 else ((0, 220, 255) if sharpness > 40 else (0, 0, 255))
        
        cv2.putText(
            frame,
            f"{cam_id.upper()} ({w}x{h} @ {measured_fps:.1f}fps)",
            (10, 22),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (255, 255, 255),
            2
        )
        cv2.putText(
            frame,
            f"Focus Sharpness Score: {sharpness:6.1f} (Higher is sharper!)",
            (10, 45),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            sharp_color,
            2
        )

        with lock:
            active_caps[cam_id]["latest_frame"] = frame
            active_caps[cam_id]["sharpness"] = sharpness
            active_caps[cam_id]["fps"] = measured_fps

        time.sleep(0.01)

class StreamHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/" or self.path.startswith("/?"):
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            
            cam_cards = ""
            for cid in active_caps.keys():
                cam_cards += f"""
                <div class="card">
                    <h2>📷 {cid.upper()} CAMERA</h2>
                    <img src="/stream/{cid}" alt="{cid} stream">
                    <p class="hint">Twist lens barrel slowly until the Focus Sharpness score reaches its maximum!</p>
                </div>
                """
                
            if not cam_cards:
                cam_cards = "<p class='error'>No cameras are currently open. Check connections and bringup/config.json!</p>"
                
            html = f"""<!DOCTYPE html>
            <html>
            <head>
                <title>LeRobot Camera Focus & Live View</title>
                <meta name="viewport" content="width=device-width, initial-scale=1">
                <style>
                    body {{
                        background: #121212;
                        color: #f0f0f0;
                        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
                        margin: 0;
                        padding: 20px;
                        display: flex;
                        flex-direction: column;
                        align-items: center;
                    }}
                    h1 {{ color: #4CAF50; margin-bottom: 5px; text-align: center; }}
                    p.subtitle {{ color: #bbb; margin-top: 0; margin-bottom: 25px; text-align: center; }}
                    .grid {{
                        display: flex;
                        flex-wrap: wrap;
                        gap: 20px;
                        justify-content: center;
                        max-width: 1400px;
                        width: 100%;
                    }}
                    .card {{
                        background: #1e1e1e;
                        border-radius: 12px;
                        padding: 15px;
                        box-shadow: 0 4px 15px rgba(0,0,0,0.5);
                        display: flex;
                        flex-direction: column;
                        align-items: center;
                    }}
                    .card h2 {{ margin: 0 0 10px 0; font-size: 1.1rem; color: #81C784; }}
                    img {{
                        width: 100%;
                        max-width: 640px;
                        height: auto;
                        border-radius: 8px;
                        background: #000;
                    }}
                    .hint {{
                        color: #ffb74d;
                        font-size: 0.9rem;
                        margin-top: 10px;
                        text-align: center;
                    }}
                    .instructions {{
                        margin-top: 30px;
                        background: #252525;
                        padding: 20px;
                        border-radius: 10px;
                        max-width: 700px;
                        line-height: 1.5;
                        font-size: 0.95rem;
                    }}
                    .instructions h3 {{ margin-top: 0; color: #64B5F6; }}
                    .error {{ color: #e57373; font-weight: bold; }}
                </style>
            </head>
            <body>
                <h1>🎯 LeRobot Camera Focus & Live View</h1>
                <p class="subtitle">Live streaming from SO-100 Robot Cameras</p>
                <div class="grid">
                    {cam_cards}
                </div>
                <div class="instructions">
                    <h3>🔧 How to Adjust Focus:</h3>
                    <ol>
                        <li>Look at the live video stream above and the <b>Focus Sharpness Score</b>.</li>
                        <li><b>Physical Lens Focus:</b> Locate the lens on your camera module. Most SO-100 cameras have a threaded manual focus ring.</li>
                        <li>Slowly rotate the lens barrel clockwise or counter-clockwise by hand.</li>
                        <li>Watch the live feed: as the image gets clearer, the <b>Focus Score will increase</b>.</li>
                        <li>Stop when the image is crisp and the score hits its peak at your robot table's distance!</li>
                    </ol>
                </div>
            </body>
            </html>"""
            self.wfile.write(html.encode("utf-8"))

        elif self.path.startswith("/stream/"):
            cam_id = self.path.split("/stream/")[1].split("?")[0]
            if cam_id not in active_caps:
                self.send_error(404, "Camera not found")
                return

            self.send_response(200)
            self.send_header("Age", "0")
            self.send_header("Cache-Control", "no-cache, private")
            self.send_header("Pragma", "no-cache")
            self.send_header("Content-Type", "multipart/x-mixed-replace; boundary=FRAME")
            self.end_headers()

            try:
                while True:
                    with lock:
                        frame = active_caps[cam_id]["latest_frame"]
                    if frame is not None:
                        ret, jpeg = cv2.imencode(".jpg", frame, [int(cv2.IMWRITE_JPEG_QUALITY), 80])
                        if ret:
                            self.wfile.write(b"--FRAME\r\n")
                            self.send_header("Content-Type", "image/jpeg")
                            self.send_header("Content-Length", str(len(jpeg)))
                            self.end_headers()
                            self.wfile.write(jpeg.tobytes())
                            self.wfile.write(b"\r\n")
                    time.sleep(0.033)
            except (BrokenPipeError, ConnectionResetError):
                pass
        else:
            self.send_error(404, "Not Found")

def main():
    parser = argparse.ArgumentParser(description="Live Camera Focus & Preview Server")
    parser.add_argument("--port", type=int, default=8080, help="Web server port (default: 8080)")
    parser.add_argument("--gui", action="store_true", help="Open local desktop OpenCV window if screen attached")
    args = parser.parse_args()

    cfg = get_resolved_config()
    cameras = cfg.get("cameras", {})

    print("==========================================================")
    print("      LeRobot Live Camera Focus & Inspection Server       ")
    print("==========================================================")
    
    threads = []
    for cname, cinfo in cameras.items():
        if not cinfo.get("enabled", True):
            print(f"[{cname.upper()}] Disabled in config.json, skipping.")
            continue
        cpath = cinfo.get("resolved_path", cinfo.get("index_or_path"))
        if not cpath or (isinstance(cpath, str) and not os.path.exists(cpath) and not cpath.isdigit()):
            print(f"[{cname.upper()}] Warning: Device '{cpath}' not found on filesystem.")
            continue
            
        print(f"Starting capture thread for [{cname.upper()}] at {cpath}...")
        t = threading.Thread(
            target=camera_worker,
            args=(cname, cpath, cinfo.get("width", 640), cinfo.get("height", 480), cinfo.get("fps", 30)),
            daemon=True
        )
        t.start()
        threads.append(t)

    time.sleep(1.0)
    if not active_caps:
        print("\n[WARN] No cameras could be opened. Checking for any available /dev/video* devices...")
        import glob
        all_videos = sorted(glob.glob("/dev/video*"))
        if all_videos:
            print(f"Detected /dev/video devices: {all_videos}")
            fallback_dev = all_videos[0]
            print(f"Attempting to launch fallback preview on {fallback_dev}...")
            t = threading.Thread(
                target=camera_worker,
                args=("camera", fallback_dev, 640, 480, 30),
                daemon=True
            )
            t.start()
            threads.append(t)
            time.sleep(1.0)

    server_address = ("0.0.0.0", args.port)
    httpd = HTTPServer(server_address, StreamHandler)
    
    print("\n" + "=" * 65)
    print(f" 🚀 Web Stream Server running on port {args.port}!")
    print(f" 👉 Open in your browser (computer or phone):")
    print(f"    http://localhost:{args.port}")
    print(f"    http://144.122.245.137:{args.port}")
    print("=" * 65)
    print(" Press Ctrl+C in terminal to stop.")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping server...")
    finally:
        httpd.server_close()
        for cdict in active_caps.values():
            cdict["cap"].release()
        print("Server stopped cleanly.")

if __name__ == "__main__":
    main()
