import logging
import time
import json
from pathlib import Path
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import (
    AcceleratorDevice,
    AcceleratorOptions,
    PdfPipelineOptions,
)
from docling.document_converter import DocumentConverter, PdfFormatOption
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

# Setup logging
logging.basicConfig(level=logging.INFO)
_log = logging.getLogger(__name__)

def extract_text_from_pdf(input_doc_path):
    pipeline_options = PdfPipelineOptions()
    pipeline_options.do_ocr = True
    pipeline_options.do_table_structure = True
    pipeline_options.table_structure_options.do_cell_matching = True
    pipeline_options.ocr_options.lang = ["es"]
    pipeline_options.accelerator_options = AcceleratorOptions(
        num_threads=4, device=AcceleratorDevice.AUTO
    )

    doc_converter = DocumentConverter(
        format_options={
            InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
        }
    )

    conv_result = doc_converter.convert(input_doc_path)
    return conv_result.document.export_to_markdown()

def main():
    # Path to your input document (PDF)
    input_doc_path = Path(r"pdfs\amex.pdf")

    # Start the conversion process with Docling
    start_time = time.time()
    conv_result = extract_text_from_pdf(input_doc_path)
    end_time = time.time() - start_time
    _log.info(f"Document converted in {end_time:.2f} seconds.")

    # Export the converted document to Markdown format
    output_dir = Path("_final_folder")
    output_dir.mkdir(parents=True, exist_ok=True)
    doc_filename = Path(input_doc_path).stem

    # Export the document as Markdown
    markdown_output_path = output_dir / f"{doc_filename}.md"
    with open(markdown_output_path, "w", encoding="utf-8") as fp:
        fp.write(conv_result)

    # Load the converted markdown content
    with open(markdown_output_path, "r", encoding="utf-8") as f:
        markdown_content = f.read()

if __name__ == "__main__":
    main()