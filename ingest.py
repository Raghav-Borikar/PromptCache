import os
from pypdf import PdfReader
import json
import re

DATA_DIR = "data"

def chunk_text(text):
    """Splits text into paragraphs and filters for meaningful content."""
    # A more robust way to split paragraphs and handle different line endings
    paragraphs = re.split(r'\n\s*\n', text)
    chunks = []
    for para in paragraphs:
        # Clean up whitespace and filter out very short strings
        cleaned_para = para.strip()
        if len(cleaned_para) > 100: # Increased minimum length for better context
            chunks.append(cleaned_para)
    return chunks

def process_all_pdfs():
    """Finds all PDFs in the data directory and processes them."""
    pdf_files = [f for f in os.listdir(DATA_DIR) if f.endswith(".pdf")]
    
    if not pdf_files:
        print(f"No PDF files found in the '{DATA_DIR}' directory.")
        return

    print(f"Found {len(pdf_files)} PDF(s) to process: {', '.join(pdf_files)}")

    for pdf_file in pdf_files:
        pdf_path = os.path.join(DATA_DIR, pdf_file)
        print(f"\nProcessing '{pdf_path}'...")
        
        try:
            reader = PdfReader(pdf_path)
            all_chunks = []
            for page_num, page in enumerate(reader.pages):
                page_text = page.extract_text()
                if page_text:
                    page_chunks = chunk_text(page_text)
                    for chunk in page_chunks:
                        all_chunks.append({
                            "source": f"{pdf_file}, page {page_num + 1}",
                            "text": chunk
                        })
            
            # Define the output JSON filename based on the PDF filename
            output_filename = os.path.splitext(pdf_file)[0] + '.json'
            output_path = os.path.join(DATA_DIR, output_filename)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(all_chunks, f, indent=2, ensure_ascii=False)
                
            print(f"-> Successfully processed {len(all_chunks)} chunks from '{pdf_file}'.")
            print(f"-> Saved to '{output_path}'")

        except Exception as e:
            print(f"!! Failed to process {pdf_file}. Error: {e}")

if __name__ == "__main__":
    process_all_pdfs()