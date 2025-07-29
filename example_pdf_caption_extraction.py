#!/usr/bin/env python3
"""
Example: Extract plots and captions from a PDF file
"""

import os
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

def main():
    """Example usage of PDF plot caption extraction"""
    
    # Check API key
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("❌ Please set your OpenAI API key:")
        print("export OPENAI_API_KEY='your-api-key-here'")
        return 1
    
    # Example PDF file (replace with your own)
    pdf_file = "test_data/paper.pdf"
    
    if not Path(pdf_file).exists():
        print(f"❌ PDF file not found: {pdf_file}")
        print("Please place a PDF file in test_data/ or update the pdf_file variable")
        return 1
    
    try:
        from opencanvas.utils.plot_caption_extractor import PDFPlotCaptionExtractor
        
        print(f"🔍 Extracting plots and captions from: {pdf_file}")
        
        # Initialize extractor with GPT
        extractor = PDFPlotCaptionExtractor(api_key=api_key, provider="gpt")
        
        # Extract plots and generate captions
        plots = extractor.extract_captions_from_pdf(pdf_file)
        
        if not plots:
            print("No plots found in the PDF")
            return 0
        
        print(f"\n📊 Found {len(plots)} plots")
        
        # Display results
        for i, plot in enumerate(plots, 1):
            print(f"\n--- Plot {i} (Page {plot.page_number}) ---")
            print(f"Caption: {plot.caption}")
            print(f"Type: {plot.plot_type}")
            print(f"Confidence: {plot.confidence:.2f}")
            
            if plot.key_insights:
                print("Key Insights:")
                for insight in plot.key_insights:
                    print(f"  • {insight}")
        
        # Generate report
        report = extractor.generate_pdf_report(plots, pdf_file)
        
        # Save report
        report_file = "caption_extraction_report.md"
        with open(report_file, 'w') as f:
            f.write(report)
        print(f"\n📄 Report saved to: {report_file}")
        
        # Save extracted plots
        plots_dir = "extracted_plots"
        saved_files = extractor.save_plots_to_directory(plots, plots_dir)
        print(f"📁 Saved {len(saved_files)} plots to: {plots_dir}")
        
        print("\n✅ Extraction completed successfully!")
        return 0
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit(main()) 
