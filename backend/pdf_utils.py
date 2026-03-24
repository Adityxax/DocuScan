import img2pdf
import os

def images_to_pdf(image_paths, output_pdf_path):
    """
    Convert a list of images to a single PDF.
    Expects absolute paths.
    """
    try:
        with open(output_pdf_path, "wb") as f:
            f.write(img2pdf.convert(image_paths))
        return True
    except Exception as e:
        print(f"PDF creation error: {e}")
        return False
