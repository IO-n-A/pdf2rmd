"""
PDF to R Markdown Converter
Converts PDF documents to R Markdown format using OCR.
"""
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from textwrap import dedent


class PDFConverter:
    """Main converter class coordinating all steps"""
    
    def __init__(self, pdf_path: Path):
        self.pdf_path = pdf_path
        self.pdf_name = pdf_path.stem
        
        # Directory structure
        self.assets_in = Path("assets/in")
        self.assets_out = Path("assets/out")
        self.png_dir = self.assets_out / "png"
        self.nougat_out = self.assets_out / "nougat"
        
        # Output files
        self.copied_pdf = self.assets_in / pdf_path.name
        self.rmd_output = self.assets_out / f"{self.pdf_name}.Rmd"
        
        # Create directories
        self.assets_in.mkdir(parents=True, exist_ok=True)
        self.assets_out.mkdir(parents=True, exist_ok=True)
        self.png_dir.mkdir(parents=True, exist_ok=True)
        self.nougat_out.mkdir(parents=True, exist_ok=True)
    
    def convert(self) -> int:
        """Execute full conversion pipeline"""
        print("=" * 70)
        print("PDF to R Markdown Converter")
        print("=" * 70)
        
        # Step 1: Copy PDF
        if not self._copy_pdf():
            return 1
        
        # Step 2: Convert to PNG
        if not self._pdf_to_png():
            return 1
        
        # Step 3: Run Nougat OCR
        if not self._run_nougat():
            return 1
        
        # Step 4: Generate R Markdown
        if not self._generate_base_rmd():
            return 1
        
        print("\n" + "=" * 70)
        print(f"✓ Conversion complete!")
        print(f"  Output: {self.rmd_output}")
        print(f"  PNG pages: {self.png_dir}/")
        print("\nNext steps:")
        print(f"  1. Review {self.rmd_output}")
        print(f"  2. Render: Rscript -e 'rmarkdown::render(\"{self.rmd_output}\")'")
        print("=" * 70)
        
        return 0
    
    def _copy_pdf(self) -> bool:
        """Copy PDF to assets/in"""
        print(f"\n[1/4] Copying PDF to {self.assets_in}/...")
        try:
            if self.copied_pdf.exists():
                print(f"  ℹ PDF already exists at {self.copied_pdf}")
            else:
                shutil.copy2(self.pdf_path, self.copied_pdf)
                print(f"  ✓ Copied {self.pdf_path.name}")
            return True
        except Exception as e:
            print(f"  ✗ Error copying PDF: {e}")
            return False
    
    def _pdf_to_png(self) -> bool:
        """Convert PDF pages to PNG images using pdftoppm"""
        print(f"\n[2/4] Converting PDF to PNG sequence in {self.png_dir}/...")
        
        try:
            # Use pdftoppm to convert PDF to PNG images
            # Output format: 1.png, 2.png, 3.png, etc.
            cmd = [
                'pdftoppm',
                '-png',
                '-r', '150',  # 150 DPI resolution
                str(self.copied_pdf),
                str(self.png_dir / 'page')
            ]
            
            print(f"  Running: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                print(f"  ✗ pdftoppm failed: {result.stderr}")
                return False
            
            # pdftoppm creates files like page-1.png, page-2.png
            # Rename them to 1.png, 2.png, etc.
            page_files = sorted(self.png_dir.glob("page-*.png"))
            for page_file in page_files:
                # Extract page number from page-1.png -> 1
                match = re.search(r'page-(\d+)\.png', page_file.name)
                if match:
                    page_num = int(match.group(1))
                    new_name = self.png_dir / f"{page_num}.png"
                    page_file.rename(new_name)
            
            # Count final PNGs
            png_files = sorted(self.png_dir.glob("*.png"))
            print(f"  ✓ Created {len(png_files)} PNG images")
            return True
            
        except FileNotFoundError:
            print(f"  ✗ pdftoppm not found. Please install poppler-utils:")
            print(f"    sudo apt-get install poppler-utils")
            return False
        except Exception as e:
            print(f"  ✗ Error converting PDF to PNG: {e}")
            return False
    
    def _run_nougat(self) -> bool:
        """Run Nougat OCR on the PDF"""
        print(f"\n[3/4] Running Nougat OCR...")
        
        try:
            # Check if nougat command exists
            nougat_check = subprocess.run(['which', 'nougat'], capture_output=True)
            if nougat_check.returncode != 0:
                print(f"  ✗ Nougat not found. Please install:")
                print(f"    pip install nougat-ocr")
                return False
            
            cmd = [
                'nougat',
                str(self.copied_pdf),
                '-o', str(self.nougat_out),
                '--no-skipping'
            ]
            
            print(f"  Running: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                print(f"  ⚠ Nougat encountered issues: {result.stderr}")
                print(f"  Continuing with available output...")
            
            # Check for output files
            mmd_files = list(self.nougat_out.glob("*.mmd"))
            if mmd_files:
                print(f"  ✓ Nougat completed: {mmd_files[0].name}")
                return True
            else:
                print(f"  ⚠ No Nougat output found, will create placeholder")
                return True  # Continue anyway
                
        except Exception as e:
            print(f"  ⚠ Error running Nougat: {e}")
            print(f"  Continuing without OCR...")
            return True  # Continue anyway
    
    def _generate_base_rmd(self) -> bool:
        """Generate R Markdown file with Nougat transcript"""
        print(f"\n[4/4] Generating R Markdown file...")
        
        try:
            with open(self.rmd_output, 'w', encoding='utf-8') as w:
                # YAML header
                w.write(dedent(f'''
                ---
                title: "{self.pdf_name}"
                author: "Generated by pdf2rmd"
                date: "`r Sys.Date()`"
                output:
                  pdf_document:
                    latex_engine: lualatex
                  html_document:
                    df_print: paged
                header-includes:
                  - \\usepackage{{fontspec}}
                  - \\setmainfont{{DejaVu Serif}}
                  - \\setsansfont{{DejaVu Sans}}
                  - \\setmonofont{{DejaVu Sans Mono}}
                ---
                
                ```{{r setup, include=FALSE}}
                knitr::opts_chunk$set(echo = TRUE, message = FALSE, warning = FALSE, fig.align = "center")
                library(knitr)
                library(magrittr)
                ```
                
                ''').lstrip())
                
                # Add Nougat transcript if available
                mmd_files = list(self.nougat_out.glob("*.mmd"))
                if mmd_files:
                    transcript = mmd_files[0].read_text(encoding='utf-8')
                    w.write("\n<!-- Nougat OCR Transcript -->\n\n")
                    w.write(transcript.rstrip() + '\n')
                else:
                    # Create placeholder content
                    png_files = sorted(self.png_dir.glob("*.png"))
                    w.write("\n<!-- Content Placeholder -->\n\n")
                    w.write("## Document Pages\n\n")
                    w.write(f"_OCR transcript not available. Document has {len(png_files)} pages._\n\n")
            
            print(f"  ✓ Created {self.rmd_output}")
            return True
            
        except Exception as e:
            print(f"  ✗ Error generating Rmd: {e}")
            return False

def get_pdf_input() -> Optional[Path]:
    """Get PDF file path from user"""
    print("\nPDF to R Markdown Converter")
    print("-" * 40)
    
    if len(sys.argv) > 1:
        pdf_path = Path(sys.argv[1])
    else:
        pdf_input = input("Enter path to PDF file: ").strip()
        pdf_path = Path(pdf_input)
    
    # Resolve path
    if not pdf_path.is_absolute():
        pdf_path = Path.cwd() / pdf_path
    
    # Validate
    if not pdf_path.exists():
        print(f"Error: File not found: {pdf_path}")
        return None
    
    if not pdf_path.suffix.lower() == '.pdf':
        print(f"Error: File is not a PDF: {pdf_path}")
        return None
    
    print(f"Input PDF: {pdf_path}")
    print(f"Size: {pdf_path.stat().st_size / 1024 / 1024:.1f} MB")
    
    return pdf_path


def main() -> int:
    """Main entry point"""
    # Get PDF input
    pdf_path = get_pdf_input()
    if not pdf_path:
        return 1
    
    # Create converter and run
    converter = PDFConverter(pdf_path)
    return converter.convert()


if __name__ == '__main__':
    sys.exit(main())