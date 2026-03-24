# DocuScan Pro

DocuScan Pro is a lean, professional-grade "Photo-to-Document" utility. It transforms multiple high-resolution photos into perfectly enhanced, multi-page PDF documents with a single click.

## ✨ Key Features

- **Multi-Page Scanning**: Upload several photos at once and merge them into a single, consolidated PDF.
- **Intelligent Enhancement**: High-contrast B&W and vibrant Color modes for professional document output.
- **Minimalist UX**: Streamlined "one-click" experience with instant previews and direct downloads.
- **Session History**: Easily re-download or preview your recent scans from a convenient session list.
- **Privacy First**: Optimized for local processing with zero unnecessary external AI dependencies.

## 🛠️ Technology Stack

- **Backend**: Python, Flask, OpenCV (Image Processing), img2pdf.
- **Frontend**: Vanilla HTML5, CSS3 (Modern, responsive UI), JavaScript.
- **Performance**: Deeply optimized OpenCV pipeline for low-latency document enhancement.

## 🚀 Quick Start

### 1. Project Setup
Ensure you have Python 3.8+ installed.

```bash
# Clone the repository
git clone https://github.com/Adityxax/DocuScan.git
cd DocuScan

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Run the Application
```bash
cd backend
python app.py
```
Open `http://localhost:5000` in your browser to start scanning.

## 📄 License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.