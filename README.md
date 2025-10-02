# PDF to R Markdown Converter

A tool that converts PDF documents (especially scanned academic papers) to R Markdown format using OCR.

## Features

- 🔄 **Automatic PDF Conversion**: Converts PDF pages to high-quality PNG images
- 📝 **OCR with Nougat**: Extracts text from scanned PDFs using state-of-the-art Nougat OCR
- 📄 **R Markdown Output**: Generates ready-to-render .Rmd files with proper formatting

## Requirements

### System Dependencies

- **Python 3.9+**
- **poppler-utils** (for `pdftoppm` command)
  - Ubuntu/Debian: `sudo apt-get install poppler-utils`
  - macOS: `brew install poppler`
  - Windows: [Download from GitHub](https://github.com/oschwartz10612/poppler-windows/releases/)

### Python Dependencies

See `requirements.txt` for full list. Main dependencies:
- `nougat-ocr` - OCR engine for academic documents
- `torch` - Deep learning framework
- `transformers` - Hugging Face transformers for Nougat
- `pypdf` / `pypdfium2` - PDF processing

## Installation

```bash
# Clone or download this tool
cd pdf2rmd

# Install Python dependencies
pip install -r requirements.txt

# Verify poppler-utils is installed
pdftoppm -v
```

## Usage

### Command Line

```bash
python main.py path/to/document.pdf
```

### Interactive Mode

```bash
python main.py
# Then enter the PDF path when prompted
```

### Example

```bash
python main.py ../in/Ch2AppliedLinearStatisticalModels.pdf
```

## Output Structure

```
pdf2rmd/
├── assets/
│   ├── in/                    # Copied input PDFs
│   │   └── document.pdf
│   └── out/
│       ├── document.Rmd       # Final R Markdown output ✨
│       ├── png/               # Page images (1.png, 2.png, ...)
│       │   ├── 1.png
│       │   ├── 2.png
│       │   └── ...
│       └── nougat/            # Nougat OCR output (.mmd files)
│           └── document.mmd
```

## Pipeline Steps

The converter executes a 4-step pipeline:

1. **Copy PDF** → `assets/in/`
2. **Convert to PNG** → `assets/out/png/` (numbered: 1.png, 2.png, ...)
3. **Run Nougat OCR** → `assets/out/nougat/` (.mmd file)
4. **Generate .Rmd** → `assets/out/document.Rmd` (with OCR transcript)

## Rendering the Output

Once the `.Rmd` file is generated, render it to PDF or HTML:

### Using RStudio
1. Open the `.Rmd` file in RStudio
2. Click "Knit" button

### Using Command Line
```bash
# Render to PDF
Rscript -e 'rmarkdown::render("assets/out/document.Rmd")'

# Render to HTML
Rscript -e 'rmarkdown::render("assets/out/document.Rmd", output_format="html_document")'
```

## Features

- **Scanned PDFs**: Optimized for scanned documents (page images)

## Limitations

- **English Text**: Nougat works best with English academic papers
- **Processing Time**: Large PDFs may take several minutes
- **GPU Recommended**: Nougat runs faster with CUDA-enabled GPU

## Troubleshooting

### "pdftoppm not found"
Install poppler-utils (see Requirements section)

### "Nougat not found"
```bash
pip install nougat-ocr
```

### Nougat runs slowly
- Use a GPU-enabled machine
- Reduce PDF size/pages
- Consider using `--pages 1-10` option in Nougat command (edit main.py)

### Out of memory errors
- Reduce PNG resolution (edit `_pdf_to_png` method)
- Process fewer pages at once
- Use a machine with more RAM

## Contributing

Contributions are welcome! Areas for improvement:

- Support for more document formats
- Support for non-English languages
- Parallel processing for large PDFs
- GUI interface
- Handling tables, plots etc.

## License

MIT License - see LICENSE file

## Credits

- **Nougat OCR**: Facebook Research's Neural Optical Understanding for Academic Documents
- **Poppler**: PDF rendering library
- **PyTorch**: Deep learning framework

## Citation

If you use this tool in research, please cite the Nougat paper:

```bibtex
@article{blecher2023nougat,
  title={Nougat: Neural Optical Understanding for Academic Documents},
  author={Blecher, Lukas and Cucurull, Guillem and Scialom, Thomas and Stojnic, Robert},
  journal={arXiv preprint arXiv:2308.13418},
  year={2023}
}
```

## Support

For issues and questions:
- Check the Troubleshooting section above
- Review [Nougat documentation](https://github.com/facebookresearch/nougat)
- Open an issue in the project repository