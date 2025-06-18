#!/usr/bin/env python3
"""
Test runner script for FlutterSwarm.
Provides easy commands to run different types of tests.
"""

import argparse
import subprocess
import sys
import os
from pathlib import Path


def run_command(cmd, description):
    """Run a command and print the result."""
    print(f"\n{'='*60}")
    print(f"🧪 {description}")
    print(f"{'='*60}")
    print(f"Running: {' '.join(cmd)}")
    print()
    
    result = subprocess.run(cmd, cwd=Path(__file__).parent)
    if result.returncode != 0:
        print(f"❌ {description} failed!")
        return False
    else:
        print(f"✅ {description} passed!")
        return True


def main():
    parser = argparse.ArgumentParser(description="FlutterSwarm Test Runner")
    parser.add_argument(
        "test_type",
        choices=["all", "unit", "integration", "e2e", "performance", "quick", "coverage"],
        help="Type of tests to run"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Run with verbose output"
    )
    parser.add_argument(
        "--fail-fast", "-x",
        action="store_true",
        help="Stop on first failure"
    )
    parser.add_argument(
        "--pattern", "-k",
        help="Run tests matching this pattern"
    )

    args = parser.parse_args()

    # Base pytest command
    base_cmd = ["python", "-m", "pytest"]
    
    if args.verbose:
        base_cmd.append("-v")
    
    if args.fail_fast:
        base_cmd.append("-x")
    
    if args.pattern:
        base_cmd.extend(["-k", args.pattern])

    success = True

    if args.test_type == "unit":
        cmd = base_cmd + ["tests/unit", "-m", "unit or not (integration or e2e or performance)"]
        success = run_command(cmd, "Unit Tests")
    
    elif args.test_type == "integration":
        cmd = base_cmd + ["tests/integration", "-m", "integration or not (unit or e2e or performance)"]
        success = run_command(cmd, "Integration Tests")
    
    elif args.test_type == "e2e":
        cmd = base_cmd + ["tests/e2e", "-m", "e2e or not (unit or integration or performance)"]
        success = run_command(cmd, "End-to-End Tests")
    
    elif args.test_type == "performance":
        cmd = base_cmd + ["tests/performance", "-m", "performance or not (unit or integration or e2e)"]
        success = run_command(cmd, "Performance Tests")
    
    elif args.test_type == "quick":
        # Run only fast tests
        cmd = base_cmd + ["tests/unit", "tests/integration", "-m", "not (slow or performance or requires_flutter or requires_network)"]
        success = run_command(cmd, "Quick Tests (Fast Unit & Integration)")
    
    elif args.test_type == "coverage":
        cmd = base_cmd + [
            "tests/",
            "--cov=.",
            "--cov-report=html:htmlcov",
            "--cov-report=term-missing",
            "--cov-report=xml",
            "--cov-fail-under=80"
        ]
        success = run_command(cmd, "All Tests with Coverage Report")
    
    elif args.test_type == "all":
        # Run all test types in order
        test_suites = [
            (["tests/unit", "-m", "unit or not (integration or e2e or performance)"], "Unit Tests"),
            (["tests/integration", "-m", "integration or not (unit or e2e or performance)"], "Integration Tests"),
            (["tests/e2e", "-m", "e2e or not (unit or integration or performance)"], "End-to-End Tests"),
            (["tests/performance", "-m", "performance or not (unit or integration or e2e)"], "Performance Tests")
        ]
        
        for test_args, description in test_suites:
            cmd = base_cmd + test_args
            if not run_command(cmd, description):
                success = False
                if args.fail_fast:
                    break

    if success:
        print(f"\n🎉 All tests completed successfully!")
        sys.exit(0)
    else:
        print(f"\n💥 Some tests failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
