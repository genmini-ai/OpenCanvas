#!/usr/bin/env python3
"""
Main CLI interface for the Presentation Toolkit
"""

import argparse
import sys
from pathlib import Path
import logging

from opencanvas.config import Config
from opencanvas.utils.logging import setup_logging
from opencanvas.generators.router import GenerationRouter
from opencanvas.conversion.html_to_pdf import PresentationConverter
from opencanvas.evaluation.evaluator import PresentationEvaluator

def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Presentation Toolkit - Generate, convert, and evaluate presentations",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate from topic
  opencanvas generate "AI in healthcare" --purpose "academic presentation" --theme "clean minimalist"
  
  # Generate from PDF
  opencanvas generate "path/to/paper.pdf" --purpose "conference presentation"
  
  # Convert HTML to PDF
  opencanvas convert output/slides.html --output presentation.pdf --zoom 1.5
  
  # Evaluate presentation
  opencanvas evaluate evaluation_folder/

  # Evaluate presentation with GPT
  opencanvas evaluate ./test_data --model gpt-4.1-mini --eval_provider gpt
  
  # Full pipeline
  opencanvas pipeline "quantum computing" --purpose "pitch deck" --evaluate
  
  # Start API server
  opencanvas api --host 0.0.0.0 --port 8000 --reload
        """
    )
    
    # Global options
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose logging')
    parser.add_argument('--log-file', help='Log to file')
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Generate command
    gen_parser = subparsers.add_parser('generate', help='Generate presentation from topic or PDF')
    gen_parser.add_argument('input', help='Topic text or PDF file path/URL')
    gen_parser.add_argument('--purpose', default=Config.DEFAULT_PURPOSE, help='Purpose of presentation')
    gen_parser.add_argument('--theme', default=Config.DEFAULT_THEME, help='Visual theme')
    gen_parser.add_argument('--output-dir', default=str(Config.OUTPUT_DIR), help='Output directory')
    gen_parser.add_argument('--extract-images', action='store_true', help='Extract and include images from PDF (PDF input only)')
    
    # Convert command  
    conv_parser = subparsers.add_parser('convert', help='Convert HTML presentation to PDF')
    conv_parser.add_argument('html_file', help='HTML presentation file')
    conv_parser.add_argument('--output', default='presentation.pdf', help='Output PDF filename')
    conv_parser.add_argument('--method', choices=['selenium', 'playwright'], 
                           default=Config.DEFAULT_CONVERSION_METHOD, help='Browser automation method')
    conv_parser.add_argument('--zoom', type=float, default=Config.DEFAULT_ZOOM, 
                           help='Zoom factor for PDF (1.0=100%%, 1.2=120%%, 1.5=150%%)')
    conv_parser.add_argument('--output-dir', default='output', help='Output directory')
    conv_parser.add_argument('--no-cleanup', action='store_true', help='Keep temporary image files')
    
    # Evaluate command
    eval_parser = subparsers.add_parser('evaluate', help='Evaluate presentation quality')
    eval_parser.add_argument('eval_folder', help='Folder containing presentation.pdf and optionally paper.pdf')
    eval_parser.add_argument('--output', help='Output JSON file path (optional)')
    eval_parser.add_argument('--model', default=Config.EVALUATION_MODEL, help='model for evaluation')
    eval_parser.add_argument('--eval_provider', default=Config.EVALUATION_PROVIDER, help='model provider for evaluation')
    
    # Pipeline command (generate + convert + optionally evaluate)
    pipe_parser = subparsers.add_parser('pipeline', help='Complete pipeline: generate -> convert -> evaluate')
    pipe_parser.add_argument('input', help='Topic text or PDF file path/URL')
    pipe_parser.add_argument('--purpose', default=Config.DEFAULT_PURPOSE, help='Purpose of presentation')
    pipe_parser.add_argument('--theme', default=Config.DEFAULT_THEME, help='Visual theme')
    pipe_parser.add_argument('--source-pdf', help='Source PDF for evaluation (if input is topic)')
    pipe_parser.add_argument('--evaluate', action='store_true', help='Run evaluation after generation')
    pipe_parser.add_argument('--eval_provider', default=Config.EVALUATION_PROVIDER, help='Model provider for evaluation (claude or gpt)')
    pipe_parser.add_argument('--output-dir', default=str(Config.OUTPUT_DIR), help='Output directory')
    pipe_parser.add_argument('--zoom', type=float, default=Config.DEFAULT_ZOOM, help='PDF zoom factor')
    pipe_parser.add_argument('--method', choices=['selenium', 'playwright'], 
                           default=Config.DEFAULT_CONVERSION_METHOD, help='Conversion method')
    pipe_parser.add_argument('--extract-images', action='store_true', help='Extract and include images from PDF (PDF input only)')
    
    # API command
    api_parser = subparsers.add_parser('api', help='Start the REST API server')
    api_parser.add_argument('--host', default='127.0.0.1', help='Host to bind to (default: 127.0.0.1)')
    api_parser.add_argument('--port', type=int, default=8000, help='Port to bind to (default: 8000)')
    api_parser.add_argument('--reload', action='store_true', help='Enable auto-reload for development')
    api_parser.add_argument('--log-level', default='info', choices=['debug', 'info', 'warning', 'error'],
                           help='Log level (default: info)')
    api_parser.add_argument('--workers', type=int, default=1, help='Number of worker processes (default: 1)')
    
    args = parser.parse_args()
    
    # Setup logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    setup_logging(level=log_level, log_file=args.log_file)
    logger = logging.getLogger(__name__)
    
    if not args.command:
        parser.print_help()
        return 1
    
    try:
        # Validate configuration
        Config.validate()
        
        if args.command == 'generate':
            return handle_generate(args, logger)
        elif args.command == 'convert':
            return handle_convert(args, logger)
        elif args.command == 'evaluate':
            return handle_evaluate(args, logger)
        elif args.command == 'pipeline':
            return handle_pipeline(args, logger)
        elif args.command == 'api':
            return handle_api(args, logger)
        else:
            parser.print_help()
            return 1
            
    except Exception as e:
        logger.error(f"Command failed: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1

def handle_generate(args, logger):
    """Handle generate command"""
    logger.info(f"🚀 Starting generation from: {args.input}")
    
    # Check if we have the required API key for generation
    if not Config.ANTHROPIC_API_KEY:
        logger.error("ANTHROPIC_API_KEY is required for generation")
        logger.error("Please set ANTHROPIC_API_KEY environment variable or add it to your .env file")
        return 1
    
    router = GenerationRouter(
        api_key=Config.ANTHROPIC_API_KEY,
        brave_api_key=Config.BRAVE_API_KEY
    )
    
    result = router.generate(
        input_source=args.input,
        purpose=args.purpose,
        theme=args.theme,
        output_dir=args.output_dir,
        extract_images=args.extract_images
    )
    
    if result:
        print(f"✅ Generated successfully!")
        print(f"📁 HTML file: {result.get('html_file', 'N/A')}")
        if 'research_performed' in result:
            print(f"🔍 Research performed: {result['research_performed']}")
        return 0
    else:
        print("❌ Generation failed")
        return 1

def handle_convert(args, logger):
    """Handle convert command"""
    logger.info(f"🔄 Converting HTML to PDF: {args.html_file}")
    
    # Validate input file
    html_path = Path(args.html_file)
    if not html_path.exists():
        logger.error(f"HTML file not found: {args.html_file}")
        return 1
    
    # Validate zoom factor
    if args.zoom <= 0 or args.zoom > 3.0:
        logger.error("Zoom factor must be between 0.1 and 3.0")
        return 1
    
    converter = PresentationConverter(
        html_file=args.html_file,
        output_dir=args.output_dir,
        method=args.method,
        zoom_factor=args.zoom
    )
    
    pdf_path = converter.convert(
        output_filename=args.output,
        cleanup=not args.no_cleanup
    )
    
    print(f"✅ PDF created successfully: {pdf_path}")
    print(f"📏 Zoom level: {args.zoom*100:.0f}%")
    return 0

def handle_evaluate(args, logger):
    """Handle evaluate command"""
    logger.info(f"📊 Evaluating presentation: {args.eval_folder}")
    
    # Determine API key and model based on provider
    if args.eval_provider == "claude":
        api_key = Config.ANTHROPIC_API_KEY
        if not api_key:
            logger.error("ANTHROPIC_API_KEY is required for Claude evaluation")
            return 1
        
        # Use Claude model if provider is Claude, regardless of what's specified in args.model
        if args.model.startswith('gpt-') or args.model.startswith('o1-'):
            # If user specified a GPT model but wants Claude provider, use default Claude model
            model = Config.EVALUATION_MODEL  # Default Claude model
            logger.warning(f"Using Claude provider but GPT model specified. Using default Claude model: {model}")
        else:
            model = args.model
            
    elif args.eval_provider == "gpt":
        api_key = Config.OPENAI_API_KEY
        if not api_key:
            logger.error("OPENAI_API_KEY is required for GPT evaluation")
            return 1
        
        # Use GPT model if provider is GPT
        if args.model.startswith('claude-'):
            # If user specified a Claude model but wants GPT provider, use a default GPT model
            model = "gpt-4o-mini"  # Default GPT model
            logger.warning(f"Using GPT provider but Claude model specified. Using default GPT model: {model}")
        else:
            model = args.model
            
    else:
        logger.error(f"Unsupported evaluation provider: {args.eval_provider}. Use 'claude' or 'gpt'")
        return 1
    
    logger.info(f"Using {args.eval_provider} provider with model {model} for evaluation")
    
    # Check if we have an organized structure or flat structure
    eval_path = Path(args.eval_folder)
    slides_folder = eval_path / "slides"
    sources_folder = eval_path / "sources"
    
    if slides_folder.exists():
        # Organized structure - use enhanced evaluator
        logger.info("Detected organized structure, using enhanced evaluator")
        evaluator = PresentationEvaluator(
            api_key=api_key,
            model=model,
            provider=args.eval_provider
        )
        
        # Find the files in organized structure
        presentation_pdf = slides_folder / "presentation.pdf"
        source_content_file = sources_folder / "source_content.txt"
        source_pdf_file = sources_folder / "source.pdf"
        
        # Check for legacy file names too
        if not source_content_file.exists():
            # Look for legacy source content file
            for file in sources_folder.glob("*source*blog*.txt"):
                source_content_file = file
                break
        
        if not presentation_pdf.exists():
            logger.error(f"presentation.pdf not found in {slides_folder}")
            return 1
        
        result = evaluator.evaluate_presentation_with_sources(
            presentation_pdf_path=str(presentation_pdf),
            source_content_path=str(source_content_file) if source_content_file.exists() else None,
            source_pdf_path=str(source_pdf_file) if source_pdf_file.exists() else None
        )
    else:
        # Flat structure - use original evaluator
        logger.info("Detected flat structure, using original evaluator")
        evaluator = PresentationEvaluator(
            api_key=api_key,
            model=model,
            provider=args.eval_provider
        )
        
        result = evaluator.evaluate_presentation(args.eval_folder)
    
    # Print results
    evaluator.print_results(result)
    
    # Save results
    if args.output:
        output_path = args.output
    else:
        folder_name = Path(args.eval_folder).name
        output_path = f"{folder_name}_evaluation_results.json"
    
    evaluator.save_results(result, output_path)
    print(f"\n💾 Results saved to: {output_path}")
    
    return 0

def handle_pipeline(args, logger):
    """Handle pipeline command - full workflow with organized outputs"""
    from opencanvas.utils.file_utils import organize_pipeline_outputs, get_file_summary
    
    logger.info(f"🔧 Starting full pipeline for: {args.input}")
    
    # Step 1: Generate
    logger.info("Step 1: Generating presentation...")
    router = GenerationRouter(
        api_key=Config.ANTHROPIC_API_KEY,
        brave_api_key=Config.BRAVE_API_KEY
    )
    
    gen_result = router.generate(
        input_source=args.input,
        purpose=args.purpose,
        theme=args.theme,
        output_dir=args.output_dir,
        extract_images=args.extract_images
    )
    
    if not gen_result:
        logger.error("Generation failed")
        return 1
    
    html_file = gen_result.get('html_file')
    organized_files = gen_result.get('organized_files', {})
    topic_slug = gen_result.get('topic_slug', 'presentation')
    
    if not html_file:
        logger.error("No HTML file generated")
        return 1
    
    print(f"✅ Step 1 complete: {html_file}")
    
    # Step 2: Convert to PDF
    logger.info("Step 2: Converting to PDF...")
    
    # Use the slides folder if we have organized files
    if 'html' in organized_files:
        html_source = str(organized_files['html'])
        pdf_output_dir = organized_files['html'].parent  # Use slides folder
    else:
        html_source = html_file
        pdf_output_dir = args.output_dir
    
    converter = PresentationConverter(
        html_file=html_source,
        output_dir=str(pdf_output_dir),
        method=args.method,
        zoom_factor=args.zoom
    )
    
    pdf_filename = "presentation.pdf"
    pdf_path = converter.convert(output_filename=pdf_filename)
    print(f"✅ Step 2 complete: {pdf_path}")
    
    # Update organized files with PDF path
    if organized_files:
        organized_files['pdf'] = Path(pdf_path)
    
    # Step 3: Evaluate (if requested)
    if args.evaluate:
        logger.info("Step 3: Evaluating presentation...")
        
        # Determine evaluation folder
        if organized_files and 'base_folder' in organized_files:
            eval_base_folder = organized_files['base_folder']
        else:
            eval_base_folder = Path(args.output_dir)
        
        # Prepare source content for evaluation
        source_content_path = None
        source_pdf_path = None
        
        # For topic-based generation, use the blog content as source
        if 'source_content' in organized_files:
            source_content_path = organized_files['source_content']
            logger.info(f"Using topic source content for evaluation: {source_content_path}")
        
        # For PDF-based generation or explicit source PDF
        if 'source_pdf' in organized_files:
            source_pdf_path = organized_files['source_pdf']
            logger.info(f"Using source PDF for evaluation: {source_pdf_path}")
        elif args.source_pdf:
            # Copy external source PDF
            import shutil
            source_path = Path(args.source_pdf)
            if source_path.exists():
                sources_folder = eval_base_folder / "sources"
                sources_folder.mkdir(exist_ok=True)
                source_pdf_path = sources_folder / "source.pdf"
                shutil.copy2(source_path, source_pdf_path)
                logger.info(f"Copied external source PDF: {source_pdf_path}")
        
        # Use the improved evaluation configuration
        try:
            eval_config = Config.get_evaluation_config()
            api_key = eval_config['api_key']
            model = eval_config['model']
            provider = eval_config['provider']
            
            if not api_key:
                logger.error(f"{provider.upper()}_API_KEY is required for {provider} evaluation")
                return 1
                
        except ValueError as e:
            logger.error(str(e))
            return 1
        
        logger.info(f"Using {provider} provider with model {model} for evaluation")
        
        # Create modified evaluator that can handle source content
        evaluator = PresentationEvaluator(
            api_key=api_key,
            model=model,
            provider=provider
        )
        
        # Use the correct PDF path (organized files take precedence)
        final_pdf_path = str(organized_files.get('pdf', pdf_path))
        
        eval_result = evaluator.evaluate_presentation_with_sources(
            presentation_pdf_path=final_pdf_path,
            source_content_path=str(source_content_path) if source_content_path else None,
            source_pdf_path=str(source_pdf_path) if source_pdf_path else None
        )
        
        # Print results
        evaluator.print_results(eval_result)
        
        # Save results in organized structure
        if organized_files and 'evaluation' in organized_files:
            eval_output_path = organized_files['evaluation'] / "evaluation_results.json"
        else:
            eval_output_path = eval_base_folder / "evaluation_results.json"
        
        evaluator.save_results(eval_result, str(eval_output_path))
        
        # Update organized files
        if organized_files:
            organized_files['evaluation_json'] = eval_output_path
        
        print(f"✅ Step 3 complete: {eval_output_path}")
    
    # Final summary
    print(f"\n🎉 Pipeline completed successfully!")
    
    if organized_files:
        print(f"\n📁 Organized output structure:")
        print(get_file_summary(organized_files))
    else:
        print(f"📁 Output directory: {args.output_dir}")
    
    return 0

def handle_api(args, logger):
    """Handle API command - start the REST API server"""
    logger.info(f"🚀 Starting OpenCanvas API Server")
    logger.info(f"📍 Host: {args.host}")
    logger.info(f"🔌 Port: {args.port}")
    logger.info(f"🔄 Reload: {args.reload}")
    logger.info(f"📝 Log Level: {args.log_level}")
    logger.info(f"👥 Workers: {args.workers}")
    
    print(f"🚀 Starting OpenCanvas API Server")
    print(f"📍 Host: {args.host}")
    print(f"🔌 Port: {args.port}")
    print(f"🔄 Reload: {args.reload}")
    print(f"📝 Log Level: {args.log_level}")
    print(f"👥 Workers: {args.workers}")
    print(f"📚 API Docs: http://{args.host}:{args.port}/docs")
    print(f"🔍 ReDoc: http://{args.host}:{args.port}/redoc")
    print(f"❤️  Health: http://{args.host}:{args.port}/api/v1/health")
    print("-" * 50)
    
    try:
        import uvicorn
        uvicorn.run(
            "src.api.app:app",
            host=args.host,
            port=args.port,
            reload=args.reload,
            log_level=args.log_level,
            workers=args.workers if args.workers > 1 else None,
            access_log=True
        )
    except ImportError:
        logger.error("FastAPI dependencies not installed. Please install with: pip install fastapi uvicorn")
        print("❌ FastAPI dependencies not installed. Please install with: pip install fastapi uvicorn")
        return 1
    except Exception as e:
        logger.error(f"Failed to start API server: {e}")
        print(f"❌ Failed to start API server: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())