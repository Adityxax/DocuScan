"""
scanner.py
──────────
Simplified Pipeline with Color/B&W Modes
"""

import cv2
import numpy as np

# ──────────────────────────────────────────────
# GEOMETRY HELPERS
# ──────────────────────────────────────────────

def order_points(pts):
    rect = np.zeros((4, 2), dtype="float32")
    s    = pts.sum(axis=1)
    diff = np.diff(pts, axis=1)
    rect[0] = pts[np.argmin(s)]
    rect[2] = pts[np.argmax(s)]
    rect[1] = pts[np.argmin(diff)]
    rect[3] = pts[np.argmax(diff)]
    return rect


def four_point_transform(image, pts):
    rect = order_points(pts)
    (tl, tr, br, bl) = rect
    w = max(int(np.linalg.norm(br - bl)), int(np.linalg.norm(tr - tl)))
    h = max(int(np.linalg.norm(tr - br)), int(np.linalg.norm(tl - bl)))
    dst = np.array([[0, 0], [w - 1, 0], [w - 1, h - 1], [0, h - 1]], dtype="float32")
    M   = cv2.getPerspectiveTransform(rect, dst)
    return cv2.warpPerspective(image, M, (w, h))


# ──────────────────────────────────────────────
# DOCUMENT DETECTION
# ──────────────────────────────────────────────

def detect_document_corners(image_path: str):
    image   = cv2.imread(image_path)
    if image is None: return None
    h, w    = image.shape[:2]
    ratio   = 800.0 / max(h, w)
    small   = cv2.resize(image, (int(w * ratio), int(h * ratio)))
    gray    = cv2.cvtColor(small, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edged   = cv2.Canny(blurred, 75, 200)
    contours, _ = cv2.findContours(edged, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    contours     = sorted(contours, key=cv2.contourArea, reverse=True)[:10]

    for c in contours:
        area_small = cv2.contourArea(c)
        if area_small < (small.shape[0] * small.shape[1] * 0.10): continue
        peri   = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.02 * peri, True)
        if len(approx) == 4:
            pts = approx.reshape(4, 2)
            dist_matrix = []
            for i in range(4):
                for j in range(i + 1, 4):
                    dist_matrix.append(np.linalg.norm(pts[i] - pts[j]))
            if min(dist_matrix) < (800.0 * 0.05): continue
            return (pts / ratio).astype("float32")
    return None


# ──────────────────────────────────────────────
# IMAGE ENHANCEMENT
# ──────────────────────────────────────────────

def enhance_for_document(image, mode="bw"):
    """
    Enhancement modes:
      - 'bw': Crisp grayscale with CLAHE
      - 'color': Vibrant color preservation using CLAHE on Lab colorspace
    """
    if mode == "bw":
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(gray)
        # Sharpen
        gaussian_blur = cv2.GaussianBlur(enhanced, (0, 0), 3)
        sharpened = cv2.addWeighted(enhanced, 1.5, gaussian_blur, -0.5, 0)
        return sharpened
    
    else: # 'color'
        # Enhance using Lab space to keep colors while improving contrast
        lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        cl = clahe.apply(l)
        limg = cv2.merge((cl, a, b))
        enhanced = cv2.cvtColor(limg, cv2.COLOR_LAB2BGR)
        # Subtle Sharpening
        gaussian_blur = cv2.GaussianBlur(enhanced, (0, 0), 3)
        sharpened = cv2.addWeighted(enhanced, 1.3, gaussian_blur, -0.3, 0)
        return sharpened


# ──────────────────────────────────────────────
# MAIN SCAN FUNCTION
# ──────────────────────────────────────────────

def scan_document(input_path: str, output_path: str, mode="bw"):
    image = cv2.imread(input_path)
    if image is None: return {"success": False, "error": "Could not read image"}

    warning = None
    corners = detect_document_corners(input_path)

    if corners is not None:
        try:
            warped = four_point_transform(image, corners)
            wh, ww = warped.shape[:2]
            if ww < 100 or wh < 100:
                 warped = image
                 warning = "Full image used — corners not clearly found"
        except:
            warped = image
            warning = "Full image used — warp failed"
    else:
        warped = image
        warning = "Full image used — corners not detected"

    result = enhance_for_document(warped, mode=mode)
    cv2.imwrite(output_path, result)
    return {"success": True, "warning": warning}
