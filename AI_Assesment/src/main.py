"""Deliberation Engine - Entry Point."""

import argparse
import sys
from pathlib import Path
from dotenv import load_dotenv  # Add this import

# Load environment variables from .env file
load_dotenv() 
# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.orchestrator import DeliberationOrchestrator
from src.utils import load_config, DeliberationLogger


def main():
    """Main entry point for the Deliberation Engine."""
    
    parser = argparse.ArgumentParser(
        description="Deliberation Engine - Multi-agent system for refining feature requests",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m src.main
  python -m src.main --request "We need better reporting"
  python -m src.main --config custom_config.yaml
  python -m src.main --request "Add user notifications" --max-rounds 4
        """,
    )
    
    parser.add_argument(
        "--request", "-r",
        type=str,
        help="Feature request to deliberate (overrides config)",
    )
    parser.add_argument(
        "--config", "-c",
        type=str,
        default="config/settings.yaml",
        help="Path to configuration file",
    )
    parser.add_argument(
        "--min-rounds",
        type=int,
        help="Minimum deliberation rounds (default: 2)",
    )
    parser.add_argument(
        "--max-rounds",
        type=int,
        help="Maximum deliberation rounds (default: 6)",
    )
    parser.add_argument(
        "--no-summarizer",
        action="store_true",
        help="Disable the summarizer agent",
    )
    parser.add_argument(
        "--output-format",
        choices=["markdown", "json"],
        default="markdown",
        help="Output format for decision document",
    )
    parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="Reduce output verbosity",
    )
    
    args = parser.parse_args()
    
    # Load configuration
    try:
        config = load_config(args.config)
    except FileNotFoundError:
        print(f"Error: Configuration file not found: {args.config}")
        sys.exit(1)
    
    # Apply CLI overrides
    feature_request = args.request or config.get("feature_request", "")
    if not feature_request:
        print("Error: No feature request provided. Use --request or set in config.")
        sys.exit(1)
    
    min_rounds = args.min_rounds or config.get("deliberation", {}).get("min_rounds", 2)
    max_rounds = args.max_rounds or config.get("deliberation", {}).get("max_rounds", 6)
    use_summarizer = not args.no_summarizer and config.get("deliberation", {}).get("use_summarizer", True)
    
    # Initialize logger
    output_config = config.get("output", {})
    logger = DeliberationLogger(
        save_trace=output_config.get("save_trace", True),
        trace_dir=output_config.get("trace_dir", "output"),
        verbose=not args.quiet,
    )
    
    # Initialize orchestrator
    orchestrator = DeliberationOrchestrator(
        llm_config=config.get("llm", {}),
        system_context=config.get("system_context", ""),
        min_rounds=min_rounds,
        max_rounds=max_rounds,
        use_summarizer=use_summarizer,
        logger=logger,
    )
    
    # Run deliberation
    try:
        document = orchestrator.run(feature_request)
        
        # Output in requested format
        if args.output_format == "json":
            print(document.to_json())
        
        # Save decision document
        output_dir = Path(output_config.get("trace_dir", "output"))
        output_dir.mkdir(parents=True, exist_ok=True)
        
        doc_path = output_dir / "decision_document.md"
        doc_path.write_text(document.to_markdown(), encoding="utf-8")
        
        print(f"\nDecision document saved to: {doc_path}")
        
    except KeyboardInterrupt:
        print("\nDeliberation interrupted by user.")
        sys.exit(130)
    except Exception as e:
        print(f"\nError during deliberation: {e}")
        raise


if __name__ == "__main__":
    main()