
# PDF Detection and Annotations using `pdfplumber`

This documentation explains how to use `pdfplumber` to detect and extract key elements from a PDF file, annotate the PDF with relevant data, and save the extracted information (including word dimensions, font size, tables, images, and more) in a structured JSON file.

## Overview

This script leverages `pdfplumber` and `PyMuPDF (fitz)` to perform the following tasks:

1. **Text Extraction**: Extract text, font size, and word dimensions from each page.
2. **Table Detection**: Extract table structures from the PDF.
3. **Image Detection**: Extract images and annotate their positions in the PDF.
4. **Page Metadata**: Retrieve page-level metadata such as page dimensions and annotations.
5. **Annotations**: Annotate the PDF with bounding boxes around detected elements.
6. **Word Font and Dimensions**: Store the font size and word dimensions for each word in an ordered dictionary and output it in JSON format.

The output consists of two parts:
- An annotated PDF file with bounding boxes around tables, images, and words.
- A JSON file that records details of the text, font sizes, and other detected elements.

## Prerequisites

Before using the script, install the required Python libraries:

```bash
pip install pdfplumber fitz PyMuPDF
```

## Workflow

### 1. Setup

The script begins by setting up the output directories and opening the input PDF file using both `pdfplumber` and `fitz`:

```python
import os
import pdfplumber
import fitz  # PyMuPDF
import json
```

### 2. PDF and JSON Processing

- **PDF Data Extraction**: The script processes each page in the PDF document, extracting the following elements:
    - **Text**: The full text content of each page.
    - **Word-level Information**: Word positions, font sizes, and dimensions.
    - **Table Structures**: Extracts and counts table data on each page.
    - **Images**: Extracts the images and their bounding boxes.
    - **Annotations**: Processes annotations like highlighting or comments present in the PDF.

### 3. Annotating PDF with PyMuPDF

The script also provides visual annotations for images, tables, and words by drawing bounding boxes on the PDF pages. The bounding boxes are highlighted with red rectangles for easier identification of detected elements.

### 4. JSON Structure

The extracted information is stored in a JSON file. Key elements in the JSON structure include:

- **Word-level data**:
    - Word text
    - Font size
    - Word dimensions (bounding box coordinates)
- **Table data**:
    - Number of tables per page
    - Table structure
- **Image data**:
    - Number of images per page
    - Image dimensions
- **Annotations and Metadata**:
    - Annotations and page metadata like dimensions.

### Code Overview

Below is the main part of the code:

```python
import os
import pdfplumber
import fitz  # PyMuPDF
import json
from collections import OrderedDict

def detect_layout(pdf_path, output_pdf_path, output_json_path):
    # Ensure the output directory exists
    os.makedirs(os.path.dirname(output_json_path), exist_ok=True)
    
    # Dictionary to store results
    results = {
        "pdf_path": pdf_path,
        "pages": []
    }

    # Open the PDF file with pdfplumber and fitz (PyMuPDF)
    with pdfplumber.open(pdf_path) as pdf:
        pdf_document = fitz.open(pdf_path)
        
        for i, page in enumerate(pdf.pages):
            print(f"Processing page {i + 1}")
            
            # Extract elements from the page
            text = page.extract_text()
            tables = page.extract_tables()
            images = page.images
            words = page.extract_words()

            # Create an ordered dictionary for words with their font size and dimensions
            words_with_attributes = OrderedDict()

            # Extract the first line of the page as the title
            first_line = text.split("\n")[0] if text else ""

            # Store word details (font size, dimensions) in the ordered dictionary
            for word in words:
                font_size = word['size']
                x0, top, x1, bottom = word['x0'], word['top'], word['x1'], word['bottom']
                words_with_attributes[word['text']] = {
                    "font_size": font_size,
                    "dimensions": {
                        "x0": x0,
                        "top": top,
                        "x1": x1,
                        "bottom": bottom
                    }
                }

            # Store results for the page
            page_data = {
                "page_number": i + 1,
                "title": first_line.strip(),
                "text": text,
                "tables_count": len(tables),
                "images_count": len(images),
                "words_with_font_and_dimensions": words_with_attributes
            }
            results["pages"].append(page_data)
            
            # Draw rectangles directly on the PDF page using PyMuPDF
            pdf_page = pdf_document[i]
            rect_color = (1, 0, 0)  # Red color for rectangles
            
            # Draw rectangles around images
            for image in images:
                rect = fitz.Rect(image["x0"], image["top"], image["x1"], image["bottom"])
                pdf_page.draw_rect(rect, color=rect_color, width=2)
                
            # Draw rectangles around tables
            for table in tables:
                rect = fitz.Rect(table.bbox)
                pdf_page.draw_rect(rect, color=rect_color, width=2)

            # Draw rectangles around words
            for word in words:
                rect = fitz.Rect(word["x0"], word["top"], word["x1"], word["bottom"])
                pdf_page.draw_rect(rect, color=rect_color, width=2)
        
        # Save the modified PDF
        pdf_document.save(output_pdf_path)
        print(f"Annotated PDF saved as {output_pdf_path}")

    # Write results to a JSON file
    with open(output_json_path, 'w') as json_file:
        json.dump(results, json_file, indent=4)
    print(f"Results saved to {output_json_path}")

if __name__ == "__main__":
    # Path to your input PDF file
    pdf_path = "path/to/your/file.pdf"
    # Path to the output annotated PDF file
    output_pdf_path = "output/annotated_file.pdf"
    # Path to the output JSON file
    output_json_path = "output/layout_results.json"
    detect_layout(pdf_path, output_pdf_path, output_json_path)
```

## JSON Output Format

The resulting JSON file will contain structured data like this:

```json
{
    "pdf_path": "path/to/your/file.pdf",
    "pages": [
        {
            "page_number": 1,
            "title": "Document Title",
            "text": "Full text of the page...",
            "tables_count": 3,
            "images_count": 2,
            "words_with_font_and_dimensions": {
                "Hello": {
                    "font_size": 12,
                    "dimensions": {
                        "x0": 72.0,
                        "top": 700.0,
                        "x1": 100.0,
                        "bottom": 712.0
                    }
                },
                "World": {
                    "font_size": 12,
                    "dimensions": {
                        "x0": 110.0,
                        "top": 700.0,
                        "x1": 145.0,
                        "bottom": 712.0
                    }
                }
            }
        },
        ...
    ]
}
```

### Key Elements:
- **`page_number`**: Page index in the PDF.
- **`title`**: The first line of the page, assumed to be the title.
- **`text`**: Full text extracted from the page.
- **`tables_count`**: Number of tables detected on the page.
- **`images_count`**: Number of images detected on the page.
- **`words_with_font_and_dimensions`**: Ordered dictionary of words with their font sizes and bounding box coordinates.

## Conclusion

This script provides a complete workflow for detecting and extracting key elements from a PDF, including word font sizes, dimensions, tables, images, and annotations, and saving the results in a structured JSON file. The output JSON can be easily processed for further analysis, while the annotated PDF provides a visual representation of the extracted elements.

## Learn More
GitHub Repository:https://github.com/jsvine/pdfplumber.git
