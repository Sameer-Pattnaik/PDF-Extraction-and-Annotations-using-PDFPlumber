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
            lines = page.lines
            chars = page.chars  # Character-level data including font size
            
            # Extract the first line of the page as the title
            first_line = text.split("\n")[0] if text else ""

            # Extract words and font sizes using character data (chars)
            words_with_font_sizes = OrderedDict()
            current_word = ""
            current_font_size = None

            for char in chars:
                font_size = char['size']
                text = char['text']

                # Check if we are in the same word (based on space and font size)
                if current_font_size is None or current_font_size == font_size:
                    current_word += text
                    current_font_size = font_size
                else:
                    # Add word to the ordered dictionary
                    if current_font_size not in words_with_font_sizes:
                        words_with_font_sizes[current_font_size] = []
                    words_with_font_sizes[current_font_size].append(current_word.strip())

                    # Start a new word
                    current_word = text
                    current_font_size = font_size

            # Add the last word if it's not empty
            if current_word:
                if current_font_size not in words_with_font_sizes:
                    words_with_font_sizes[current_font_size] = []
                words_with_font_sizes[current_font_size].append(current_word.strip())

            # Store results for the page
            page_data = {
                "page_number": i + 1,
                "title": first_line.strip(),
                "text": text,
                "tables_count": len(tables),
                "images_count": len(images),
                "tables": tables,
                "lines_count": len(lines),
                "lines": lines,
                "words_with_font_sizes": {
                    f"Size: {size}": words
                    for size, words in words_with_font_sizes.items()
                }
            }
            results["pages"].append(page_data)
            
            # Annotate the PDF: Draw rectangles around elements
            pdf_page = pdf_document[i]
            rect_color = (1, 0, 0)  # Red color for rectangles
            
            # Draw rectangles around images
            for image in images:
                rect = fitz.Rect(image["x0"], image["top"], image["x1"], image["bottom"])
                pdf_page.draw_rect(rect, color=rect_color, width=2)
                
            # Draw rectangles around tables
            for table in page.find_tables():
                rect = fitz.Rect(table.bbox)
                pdf_page.draw_rect(rect, color=rect_color, width=2)

            # Draw rectangles around words using char data
            for char in chars:
                rect = fitz.Rect(char["x0"], char["top"], char["x1"], char["bottom"])
                pdf_page.draw_rect(rect, color=rect_color, width=2)

        # Save the modified PDF with rectangles
        pdf_document.save(output_pdf_path)
        print(f"Annotated PDF saved as {output_pdf_path}")

    # Write results to a JSON file
    with open(output_json_path, 'w') as json_file:
        json.dump(results, json_file, indent=4)
    print(f"Results saved to {output_json_path}")

if __name__ == "__main__":
    # Path to your input PDF file
    pdf_path = "Fraud_Report_2022.pdf"
    # Path to the output annotated PDF file
    output_pdf_path = "output/annotated_file.pdf"
    # Path to the output JSON file
    output_json_path = "output/layout_results1.json"
    detect_layout(pdf_path, output_pdf_path, output_json_path)
