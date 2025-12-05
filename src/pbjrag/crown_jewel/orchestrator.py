# D:\SanctuarIDE\crown_jewel_core\orchestrator.py
"""
Orchestrator Module - Main pipeline runner for the Crown Jewel Planner.

This module consolidates all orchestration logic into a single, purpose-driven
pipeline that manages the flow of analysis, blessing, and integration.
"""

import datetime
import json
import logging
import sys
from pathlib import Path
from typing import Any, Dict, Optional

from .error_handler import handle_error
from .field_container import create_field
from .metrics import CoreMetrics
from .pattern_analyzer import (analyze_codebase, detect_patterns,
                               suggest_combinations)
from .phase_manager import PhaseManager

logger = logging.getLogger(__name__)


class Orchestrator:
    """
    Main orchestrator for the Crown Jewel Planner pipeline.
    Manages the flow of analysis, blessing, and integration.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the orchestrator with optional configuration.

        Parameters:
        - config: Optional configuration dictionary
        """
        self.config = config or {}

        # Extract configuration
        self.purpose = self.config.get("purpose", "stability")
        self.project_root = self.config.get("project_root", ".")
        self.scan_depth = self.config.get("scan_depth", 2)
        self.output_dir = self.config.get("output_dir", "spiral_reports")
        self.top_n = self.config.get("top_n", 10)
        self.max_group_size = self.config.get("max_group_size", 3)
        self.verbose = self.config.get("verbose", False)

        # Create output directory as a Path object.
        self.output_dir = Path(self.output_dir)
        self.output_dir.mkdir(exist_ok=True, parents=True)

        # Initialize components
        self.metrics = CoreMetrics(self.config)
        self.field = create_field(self.config)
        self.phase_manager = PhaseManager(self.config)

        # Set up logging
        self._setup_logging()

    def _setup_logging(self) -> None:
        """Set up logging for the orchestrator."""
        log_level = logging.DEBUG if self.verbose else logging.INFO

        # Create a file handler
        log_file = (
            Path(self.output_dir)
            / f"orchestrator_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        )
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(log_level)

        # Create a console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(log_level)

        # Create a formatter
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        # Add handlers to the logger
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        logger.setLevel(log_level)

    def run(self) -> Dict[str, Any]:
        """
        Run the full orchestration pipeline.

        Returns:
        - Pipeline results
        """
        logger.info(f"Starting orchestration with purpose: {self.purpose}")

        try:
            # Phase 1: Witness - Analyze codebase
            self._run_witness_phase()

            # Phase 2: Recognition - Identify patterns
            self._run_recognition_phase()

            # Phase 3: Compost - Break down rigid structures
            self._run_compost_phase()

            # Phase 4: Emergence - Allow new patterns to form
            self._run_emergence_phase()

            # Phase 5: Blessing - Amplify coherent patterns
            self._run_blessing_phase()

            # Phase 6: Expression - Manifest the solution
            solution = self._run_expression_phase()

            # Save field state
            state_files = self.field.save_field_state(self.output_dir)

            # Create final report
            report = self._create_final_report(solution, state_files)

            logger.info("Orchestration completed successfully")

            return {
                "success": True,
                "message": "Orchestration completed successfully",
                "solution": solution,
                "report": report,
                "state_files": state_files,
            }

        except Exception as e:
            logger.exception(f"Error in orchestration: {str(e)}")

            # Use error handler to metabolize the error
            error_result = handle_error(e, self.field)

            return {
                "success": False,
                "message": f"Error in orchestration: {str(e)}",
                "exception": str(e),
                "error_handled": error_result,
            }

    def _run_witness_phase(self) -> None:
        """Run the witness phase - analyze codebase."""
        logger.info("Running witness phase - analyzing codebase")

        # Transition to witness phase
        self.phase_manager.transition_to_phase("witness")

        # Analyze codebase
        try:
            fragments = analyze_codebase(
                self.project_root, max_depth=self.scan_depth, output_dir=self.output_dir
            )

            # Add fragments to field
            for fragment in fragments:
                self.field.add_fragment(fragment)

            # Save fragments to file
            fragments_file = Path(self.output_dir) / "fragments.json"
            with open(fragments_file, "w", encoding="utf-8") as f:
                json.dump(fragments, f, indent=2)

            # Update phase data
            self.phase_manager.update_phase_data(
                {
                    "fragment_count": len(fragments),
                    "timestamp": datetime.datetime.now().isoformat(),
                }
            )

            logger.info(f"Witness phase complete - {len(fragments)} fragments analyzed")

        except Exception as e:
            logger.error(f"Error in witness phase: {str(e)}")
            error_result = handle_error(e, self.field)
            logger.info(f"Error handled: {error_result.get('message')}")
            raise

    def _run_recognition_phase(self) -> None:
        """Run the recognition phase - identify patterns."""
        logger.info("Running recognition phase - identifying patterns")

        # Transition to recognition phase
        self.phase_manager.transition_to_phase("recognition")

        try:
            # Get fragments from field
            fragments = self.field.get_fragments()

            # Detect patterns
            patterns = detect_patterns(fragments, self.config)

            # Add patterns to field
            for pattern in patterns:
                self.field.add_pattern(pattern)

            # Save patterns to file
            patterns_file = Path(self.output_dir) / "patterns.json"
            with open(patterns_file, "w", encoding="utf-8") as f:
                json.dump(patterns, f, indent=2)

            # Update phase data
            self.phase_manager.update_phase_data(
                {
                    "pattern_count": len(patterns),
                    "timestamp": datetime.datetime.now().isoformat(),
                }
            )

            logger.info(
                f"Recognition phase complete - {len(patterns)} patterns identified"
            )

        except Exception as e:
            logger.error(f"Error in recognition phase: {str(e)}")
            error_result = handle_error(e, self.field)
            logger.info(f"Error handled: {error_result.get('message')}")
            raise

    def _run_compost_phase(self) -> None:
        """Run the compost phase - break down rigid structures."""
        logger.info("Running compost phase - breaking down rigid structures")

        # Transition to compost phase
        self.phase_manager.transition_to_phase("compost")

        try:
            # Dissolve rigid structures
            self.field.dissolve_rigid_structures()

            # Decay old compost
            decayed = self.field.decay_compost()

            # Update phase data
            self.phase_manager.update_phase_data(
                {
                    "decayed_count": decayed,
                    "timestamp": datetime.datetime.now().isoformat(),
                }
            )

            logger.info(f"Compost phase complete - {decayed} items decayed")

        except Exception as e:
            logger.error(f"Error in compost phase: {str(e)}")
            error_result = handle_error(e, self.field)
            logger.info(f"Error handled: {error_result.get('message')}")
            raise

    def _run_emergence_phase(self) -> None:
        """Run the emergence phase - allow new patterns to form."""
        logger.info("Running emergence phase - allowing new patterns to form")

        # Transition to emergence phase
        self.phase_manager.transition_to_phase("emergence")

        try:
            # Get fragments
            fragments = self.field.get_fragments()

            # Create field context
            field_context = {
                "purpose": self.purpose,
                "phase": "emergence",
                "epc_min": 0.4,
                "max_group_size": self.max_group_size,
            }

            # Suggest combinations
            combinations = suggest_combinations(
                fragments,
                top_n=self.top_n,
                max_group_size=self.max_group_size,
                field_context=field_context,
            )

            # Hold promising combinations in capacitor
            for combo in combinations:
                blessing = combo.get("group_blessing", {})
                if blessing.get("Φ") != "Φ+" and blessing.get("epc", 0.0) > 0.4:
                    self.field.hold_in_capacitor(
                        combo, reason=f"Promising {self.purpose} combination"
                    )

            # Save combinations to file
            combos_file = Path(self.output_dir) / f"combinations_{self.purpose}.json"
            with open(combos_file, "w", encoding="utf-8") as f:
                json.dump(combinations, f, indent=2)

            # Allow emergence from field
            emerged = self.field.allow_emergence()

            # Update phase data
            self.phase_manager.update_phase_data(
                {
                    "combination_count": len(combinations),
                    "emerged_count": len(emerged),
                    "timestamp": datetime.datetime.now().isoformat(),
                }
            )

            logger.info(
                f"Emergence phase complete - {len(combinations)} combinations suggested, {len(emerged)} patterns emerged"
            )

        except Exception as e:
            logger.error(f"Error in emergence phase: {str(e)}")
            error_result = handle_error(e, self.field)
            logger.info(f"Error handled: {error_result.get('message')}")
            raise

    def _run_blessing_phase(self) -> None:
        """Run the blessing phase - amplify coherent patterns."""
        logger.info("Running blessing phase - amplifying coherent patterns")

        # Transition to blessing phase
        self.phase_manager.transition_to_phase("blessing")

        try:
            # Amplify coherent patterns
            amplified = self.field.amplify_coherent_patterns()

            # Calculate field coherence
            coherence = self.field.calculate_field_coherence()

            # Update phase data
            self.phase_manager.update_phase_data(
                {
                    "amplified_count": len(amplified),
                    "field_coherence": coherence,
                    "timestamp": datetime.datetime.now().isoformat(),
                }
            )

            logger.info(
                f"Blessing phase complete - {len(amplified)} patterns amplified, field coherence: {coherence:.4f}"
            )

        except Exception as e:
            logger.error(f"Error in blessing phase: {str(e)}")
            error_result = handle_error(e, self.field)
            logger.info(f"Error handled: {error_result.get('message')}")
            raise

    def _run_expression_phase(self) -> Dict[str, Any]:
        """
        Run the expression phase - manifest the solution.

        Returns:
        - Manifested solution
        """
        logger.info("Running expression phase - manifesting solution")

        # Transition to expression phase
        self.phase_manager.transition_to_phase("expression")

        try:
            # Manifest solution
            solution = self.field.manifest_solution()

            # Save solution to file
            solution_file = Path(self.output_dir) / "solution.json"
            with open(solution_file, "w", encoding="utf-8") as f:
                json.dump(solution, f, indent=2)

            # Update phase data
            self.phase_manager.update_phase_data(
                {
                    "solution_success": solution.get("success", False),
                    "timestamp": datetime.datetime.now().isoformat(),
                }
            )

            logger.info(
                f"Expression phase complete - solution manifested with success: {solution.get('success', False)}"
            )

            return solution

        except Exception as e:
            logger.error(f"Error in expression phase: {str(e)}")
            error_result = handle_error(e, self.field)
            logger.info(f"Error handled: {error_result.get('message')}")
            raise

    def _create_final_report(
        self, solution: Dict[str, Any], state_files: Dict[str, str]
    ) -> Dict[str, Any]:
        """
        Create the final report.

        Parameters:
        - solution: Manifested solution
        - state_files: Dictionary of state file paths

        Returns:
        - Final report
        """
        # Get field state
        fragments = self.field.get_fragments()
        patterns = self.field.get_patterns()
        blessed_groups = self.field.get_blessed_groups()
        compost = self.field.get_compost()
        capacitor = self.field.get_capacitor()

        # Create report
        report = {
            "timestamp": datetime.datetime.now().isoformat(),
            "purpose": self.purpose,
            "project_root": str(self.project_root),
            "scan_depth": self.scan_depth,
            "output_dir": str(self.output_dir),
            "top_n": self.top_n,
            "max_group_size": self.max_group_size,
            "field_coherence": self.field.field_coherence,
            "phase_history": self.phase_manager.get_phase_history(),
            "current_phase": self.phase_manager.current_phase,
            "fragment_count": len(fragments),
            "pattern_count": len(patterns),
            "blessed_group_count": len(blessed_groups),
            "compost_count": len(compost),
            "capacitor_count": len(capacitor),
            "solution": solution,
            "state_files": state_files,
        }

        # Save report to file
        report_file = Path(self.output_dir) / "final_report.json"
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)

        # Create markdown report
        self._create_markdown_report(report, report_file.with_suffix(".md"))

        return report

    def _create_markdown_report(
        self, report: Dict[str, Any], output_file: Path
    ) -> None:
        """
        Create a markdown report.

        Parameters:
        - report: Report data
        - output_file: Output file path
        """
        with open(output_file, "w", encoding="utf-8") as f:
            f.write("# Crown Jewel Planner Report\n\n")
            f.write(f"**Purpose:** {report['purpose']}\n")
            f.write(f"**Timestamp:** {report['timestamp']}\n")
            f.write(f"**Project Root:** {report['project_root']}\n")
            f.write(f"**Field Coherence:** {report['field_coherence']:.4f}\n\n")

            f.write("## Phase History\n\n")
            for phase in report["phase_history"]:
                f.write(f"- {phase['phase']}: {phase['timestamp']}\n")
            f.write(f"\n**Current Phase:** {report['current_phase']}\n\n")

            f.write("## Field State\n\n")
            f.write(f"- Fragments: {report['fragment_count']}\n")
            f.write(f"- Patterns: {report['pattern_count']}\n")
            f.write(f"- Blessed Groups: {report['blessed_group_count']}\n")
            f.write(f"- Compost Items: {report['compost_count']}\n")
            f.write(f"- Capacitor Items: {report['capacitor_count']}\n\n")

            f.write("## Solution\n\n")
            if report["solution"].get("success", False):
                f.write("**Success:** Yes\n")
                f.write(f"**Message:** {report['solution'].get('message', '')}\n")

                group = report["solution"].get("group", {})
                blessing = group.get("group_blessing", {})

                f.write("\n### Solution Group\n\n")
                f.write(f"- EPC: {blessing.get('epc', 0.0):.4f}\n")
                f.write(f"- Blessing: {blessing.get('Φ', 'Unknown')}\n")

                files = group.get("files", [])
                if files:
                    f.write("\n**Files:**\n\n")
                    for file in files:
                        f.write(f"- {file}\n")
            else:
                f.write("**Success:** No\n")
                f.write(f"**Message:** {report['solution'].get('message', '')}\n")

            f.write("\n## State Files\n\n")
            for file_type, file_path in report["state_files"].items():
                f.write(f"- {file_type}: {file_path}\n")


def run_orchestration(config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Run the orchestration pipeline with the specified configuration.

    Parameters:
    - config: Optional configuration dictionary

    Returns:
    - Pipeline results
    """
    orchestrator = Orchestrator(config)
    return orchestrator.run()


def main():
    """Main entry point for command-line usage."""
    import argparse

    parser = argparse.ArgumentParser(description="Crown Jewel Planner Orchestrator")
    parser.add_argument(
        "--purpose",
        default="stability",
        choices=["stability", "emergence", "coherence", "innovation"],
        help="Purpose for the orchestration",
    )
    parser.add_argument(
        "--project-root", default=".", help="Root directory of the project to analyze"
    )
    parser.add_argument(
        "--scan-depth", type=int, default=2, help="Maximum directory depth to scan"
    )
    parser.add_argument(
        "--output-dir", default="spiral_reports", help="Directory for output reports"
    )
    parser.add_argument(
        "--top-n", type=int, default=10, help="Number of top combinations to suggest"
    )
    parser.add_argument(
        "--max-group-size",
        type=int,
        default=3,
        help="Maximum size of combination groups",
    )
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")

    args = parser.parse_args()

    config = {
        "purpose": args.purpose,
        "project_root": args.project_root,
        "scan_depth": args.scan_depth,
        "output_dir": args.output_dir,
        "top_n": args.top_n,
        "max_group_size": args.max_group_size,
        "verbose": args.verbose,
    }

    result = run_orchestration(config)

    if result.get("success", False):
        print("\n✅ Orchestration completed successfully!")
        print(f"Output directory: {args.output_dir}")
        print(f"Final report: {args.output_dir}/final_report.md")
    else:
        print(f"\n❌ Orchestration failed: {result.get('message', 'Unknown error')}")


if __name__ == "__main__":
    main()
