#!/usr/bin/env python3
"""PBJRAG Command Line Interface.

This module provides a command-line interface for running PBJRAG (Differential Symbolic
Calculus for Code Analysis). It supports analyzing code files and projects, generating
reports in multiple formats, and customizing output for different user personas.

The CLI provides two main commands:
    - analyze: Analyze code files or entire projects
    - report: Generate reports from previously analyzed results

Example:
    Basic file analysis::

        $ pbjrag analyze myfile.py

    Project analysis with custom output directory::

        $ pbjrag analyze ./myproject --output results --purpose stability

    Generate report from previous analysis::

        $ pbjrag report --input results --format json

Available Personas:
    - general: Default balanced output with standard terminology
    - devops: Production-focused output with deployment metrics
    - scholar: Academic terminology with theoretical foundations

Attributes:
    None: This module contains only functions and command definitions.
"""

import argparse
import json
from pathlib import Path
import sys


def main():
    """Main CLI entry point for PBJRAG.

    Parses command-line arguments and executes the appropriate analysis or
    reporting command. Supports two main subcommands: 'analyze' and 'report'.

    The function sets up argument parsing with comprehensive help text,
    processes the command, and handles errors gracefully with user-friendly
    messages.

    Returns:
        int: Exit code (0 for success, 1 for error)

    Raises:
        ImportError: If pbjrag package is not properly installed
        Exception: For other runtime errors during analysis or reporting

    Examples:
        Analyze a single file::

            $ pbjrag analyze file.py
            🔍 Analyzing file.py...
            ✓ Analyzed 1 file
            📊 Field Coherence: 0.845
            📁 Results saved to: pbjrag_output/

        Analyze with DevOps persona::

            $ pbjrag analyze ./project --persona devops
            🔍 Analyzing ./project...
            ✓ Analyzed 42 files
            📊 Field Coherence: 0.892

            🎯 Production Readiness:
              Production-ready: 78.5%
              Needs review: 15.2%
              Technical debt: 6.3%

        Generate JSON report::

            $ pbjrag report --format json
            📊 Generating report...
            {
              "field_coherence": 0.892,
              "blessing_distribution": {...}
            }
    """
    parser = argparse.ArgumentParser(
        description="PBJRAG - Differential Symbolic Calculus for Code Analysis",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  pbjrag analyze file.py           # Analyze a single file
  pbjrag analyze ./project         # Analyze entire project
  pbjrag report                    # Generate analysis report

Translation modes:
  --persona devops                 # DevOps-friendly output
  --persona scholar                # Academic terminology
  --persona general                # Default balanced mode
        """,
    )

    parser.add_argument("--version", action="version", version="%(prog)s 3.0.0")

    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Analyze command
    analyze_parser = subparsers.add_parser(
        "analyze",
        help="Analyze code files or projects for field coherence and structural patterns",
    )
    analyze_parser.add_argument(
        "path",
        help="Path to file or directory to analyze (supports Python, JavaScript, etc.)",
    )
    analyze_parser.add_argument(
        "--output",
        "-o",
        default="pbjrag_output",
        help="Output directory for analysis results and reports (default: pbjrag_output)",
    )
    analyze_parser.add_argument(
        "--purpose",
        "-p",
        choices=["stability", "emergence", "coherence", "innovation"],
        default="coherence",
        help=(
            "Analysis purpose: "
            "stability (find reliable patterns), "
            "emergence (discover new patterns), "
            "coherence (overall structure), "
            "innovation (highlight novel approaches). "
            "Default: coherence"
        ),
    )
    analyze_parser.add_argument(
        "--no-vector",
        action="store_true",
        help="Disable vector store integration (faster, no external dependencies required)",
    )
    analyze_parser.add_argument(
        "--persona",
        choices=["devops", "scholar", "general"],
        default="general",
        help=(
            "Output terminology style: "
            "devops (production metrics), "
            "scholar (academic terms), "
            "general (balanced). "
            "Default: general"
        ),
    )

    # Report command
    report_parser = subparsers.add_parser(
        "report",
        help="Generate analysis report from previously saved results",
    )
    report_parser.add_argument(
        "--input",
        "-i",
        default="pbjrag_output",
        help="Input directory containing previous analysis results (default: pbjrag_output)",
    )
    report_parser.add_argument(
        "--format",
        "-f",
        choices=["json", "markdown", "html"],
        default="markdown",
        help=(
            "Report output format: "
            "json (machine-readable), "
            "markdown (human-readable), "
            "html (formatted). "
            "Default: markdown"
        ),
    )

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    try:
        # Import here to avoid import errors if package not installed
        from pbjrag.dsc import DSCAnalyzer

        if args.command == "analyze":
            print(f"🔍 Analyzing {args.path}...")

            config = {
                "purpose": args.purpose,
                "output_dir": args.output,
                "enable_vector_store": not args.no_vector,
            }

            analyzer = DSCAnalyzer(config)

            path = Path(args.path)
            if path.is_file():
                results = analyzer.analyze_file(str(path))
                print("✓ Analyzed 1 file")
            elif path.is_dir():
                results = analyzer.analyze_project(str(path))
                if results.get("success"):
                    dsc = results.get("dsc_analysis", {})
                    print(f"✓ Analyzed {dsc.get('files_analyzed', 0)} files")
            else:
                print(f"❌ Path not found: {path}")
                return 1

            # Generate report
            report = analyzer.generate_report()
            print(f"📊 Field Coherence: {report['field_coherence']:.3f}")
            print(f"📁 Results saved to: {args.output}/")

            # Show blessing distribution
            if args.persona == "devops":
                print("\n🎯 Production Readiness:")
                dist = report.get("blessing_distribution", {})
                print(f"  Production-ready: {dist.get('Φ+', 0):.1%}")
                print(f"  Needs review: {dist.get('Φ~', 0):.1%}")
                print(f"  Technical debt: {dist.get('Φ-', 0):.1%}")
            else:
                print("\n✨ Blessing Distribution:")
                dist = report.get("blessing_distribution", {})
                for tier, pct in dist.items():
                    print(f"  {tier}: {pct:.1%}")

        elif args.command == "report":
            print("📊 Generating report...")

            config = {
                "output_dir": args.input,
                "enable_vector_store": False,
            }

            analyzer = DSCAnalyzer(config)

            # Load previous analysis state
            loaded = analyzer.field_container.load_field_state(args.input)
            if not loaded:
                print(f"❌ No analysis data found in {args.input}")
                return 1

            report = analyzer.generate_report()

            if args.format == "json":
                json_path = Path(args.input) / "dsc_analysis_report.json"
                print(json.dumps(report, indent=2))
                print(f"📁 Report saved to: {json_path}")
            elif args.format == "markdown":
                md_path = Path(args.input) / "dsc_analysis_report.md"
                if md_path.exists():
                    print(md_path.read_text())
                else:
                    print("❌ Markdown report not found")
            elif args.format == "html":
                md_path = Path(args.input) / "dsc_analysis_report.md"
                html_path = Path(args.input) / "dsc_analysis_report.html"
                if md_path.exists():
                    try:
                        import markdown  # type: ignore

                        html_content = markdown.markdown(md_path.read_text())
                    except Exception:
                        html_content = f"<pre>{md_path.read_text()}</pre>"
                else:
                    html_content = "<p>No report available</p>"
                html_path.write_text(html_content, encoding="utf-8")
                print(f"📁 HTML report saved to: {html_path}")
            else:
                print("❌ Unknown format")

            return 0

    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure PBJRAG is installed: pip install -e .")
        return 1
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
