"""
app.py — Simplified Backend
"""

import os
import uuid
from flask import Flask, request, jsonify, send_from_directory, send_file
from scanner import scan_document
from pdf_utils import images_to_pdf

app = Flask(__name__, static_folder=os.path.abspath(os.path.join(os.path.dirname(__file__), "../frontend")))

BASE_DIR    = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR  = os.path.join(BASE_DIR, "..", "uploads")
OUTPUT_DIR  = os.path.join(BASE_DIR, "..", "outputs")

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

ALLOWED_EXT = {"png", "jpg", "jpeg", "webp"}

def allowed(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXT

@app.route("/")
def index():
    return send_from_directory(app.static_folder, "index.html")

@app.route("/scan", methods=["POST"])
def scan():
    if "images" not in request.files:
        return jsonify({"error": "No images uploaded"}), 400

    files = request.files.getlist("images")
    mode  = request.form.get("mode", "bw")
    
    if not files or not files[0].filename:
        return jsonify({"error": "No files selected"}), 400

    uid = uuid.uuid4().hex
    processed_paths = []
    warnings = []

    for i, file in enumerate(files):
        if not allowed(file.filename):
            continue
        
        ext = file.filename.rsplit(".", 1)[1].lower()
        input_path  = os.path.join(UPLOAD_DIR, f"{uid}_{i}.{ext}")
        output_path = os.path.join(OUTPUT_DIR, f"result_{uid}_{i}.png")
        
        file.save(input_path)
        result = scan_document(input_path, output_path, mode=mode)
        
        # Clean up upload
        try: os.remove(input_path)
        except: pass
        
        if result["success"]:
            processed_paths.append(output_path)
            if result.get("warning"):
                warnings.append(f"Page {i+1}: {result['warning']}")
        else:
            return jsonify({"error": f"Failed on page {i+1}: {result.get('error','Unknown')}"}), 500

    if not processed_paths:
        return jsonify({"error": "No valid images processed"}), 400

    # Generate multi-page PDF
    pdf_path = os.path.join(OUTPUT_DIR, f"document_{uid}.pdf")
    images_to_pdf(processed_paths, pdf_path)

    # For display, show the first page
    first_page_url = f"/result/result_{uid}_0.png"

    return jsonify({
        "id": uid,
        "warning": " | ".join(warnings) if warnings else None,
        "formats": {
            "png": first_page_url,
            "pdf": f"/result/document_{uid}.pdf"
        },
        "page_count": len(processed_paths)
    })

@app.route("/result/<filename>")
def result(filename):
    return send_from_directory(OUTPUT_DIR, filename)

@app.route("/download/<filename>")
def download(filename):
    path = os.path.join(OUTPUT_DIR, filename)
    if not os.path.exists(path):
        return "File not found", 404
    return send_file(path, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
