#!/usr/bin/env python3
"""
Main CLI interface for the Presentation Toolkit
"""

import argparse
import sys
from pathlib import Path
import logging

from .config import Config
from .utils.logging import setup_logging
from .generators.router import GenerationRouter
from .conversion.html_to_pdf import PresentationConverter
from .evaluation.evaluator import PresentationEvaluator

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
    
    router = GenerationRouter(
        api_key=Config.ANTHROPIC_API_KEY,
        brave_api_key=Config.BRAVE_API_KEY
    )
    
    result = router.generate(
        input_source=args.input,
        purpose=args.purpose,
        theme=args.theme,
        output_dir=args.output_dir
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
    
    # Determine API key based on provider
    if args.eval_provider == "claude":
        api_key = Config.ANTHROPIC_API_KEY
        if not api_key:
            logger.error("ANTHROPIC_API_KEY is required for Claude evaluation")
            return 1
        assert api_key is not None  # For type checker
    elif args.eval_provider == "gpt":
        api_key = Config.OPENAI_API_KEY
        if not api_key:
            logger.error("OPENAI_API_KEY is required for GPT evaluation")
            return 1
        assert api_key is not None  # For type checker
    else:
        logger.error(f"Unsupported evaluation provider: {args.eval_provider}. Use 'claude' or 'gpt'")
        return 1
    
    logger.info(f"Using {args.eval_provider} provider for evaluation")
    
    evaluator = PresentationEvaluator(
        api_key=api_key,
        model=args.model,
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
    """Handle pipeline command - full workflow"""
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
        output_dir=args.output_dir
    )
    
    if not gen_result:
        logger.error("Generation failed")
        return 1
    
    html_file = gen_result.get('html_file')
    if not html_file:
        logger.error("No HTML file generated")
        return 1
    
    print(f"✅ Step 1 complete: {html_file}")
    
    # Step 2: Convert to PDF
    logger.info("Step 2: Converting to PDF...")
    converter = PresentationConverter(
        html_file=html_file,
        output_dir=args.output_dir,
        method=args.method,
        zoom_factor=args.zoom
    )
    
    pdf_path = converter.convert(output_filename="presentation.pdf")
    print(f"✅ Step 2 complete: {pdf_path}")
    
    # Step 3: Evaluate (if requested)
    if args.evaluate:
        logger.info("Step 3: Evaluating presentation...")
        
        # Setup evaluation folder
        eval_folder = Path(args.output_dir)
        
        # Copy source PDF if provided
        if args.source_pdf:
            import shutil
            source_path = Path(args.source_pdf)
            if source_path.exists():
                shutil.copy2(source_path, eval_folder / "paper.pdf")
                logger.info(f"Copied source PDF: {args.source_pdf}")
        
        # Determine API key based on provider
        if args.eval_provider == "claude":
            api_key = Config.ANTHROPIC_API_KEY
            if not api_key:
                logger.error("ANTHROPIC_API_KEY is required for Claude evaluation")
                return 1
            assert api_key is not None  # For type checker
        elif args.eval_provider == "gpt":
            api_key = Config.OPENAI_API_KEY
            if not api_key:
                logger.error("OPENAI_API_KEY is required for GPT evaluation")
                return 1
            assert api_key is not None  # For type checker
        else:
            logger.error(f"Unsupported evaluation provider: {args.eval_provider}. Use 'claude' or 'gpt'")
            return 1
        
        logger.info(f"Using {args.eval_provider} provider for evaluation")
        
        evaluator = PresentationEvaluator(
            api_key=api_key,
            model=Config.EVALUATION_MODEL,
            provider=args.eval_provider
        )
        eval_result = evaluator.evaluate_presentation(str(eval_folder))
        
        # Print results
        evaluator.print_results(eval_result)
        
        # Save results
        output_path = eval_folder / "evaluation_results.json"
        evaluator.save_results(eval_result, str(output_path))
        
        print(f"✅ Step 3 complete: {output_path}")
    
    print(f"\n🎉 Pipeline completed successfully!")
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