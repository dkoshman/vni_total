#!/usr/bin/env python3
"""
Test runner script for the VNI Total project.
This script runs all tests and generates coverage reports.
"""

import subprocess
import sys
import os


def run_tests():
    """Run all tests with coverage reporting."""
    print("Running VNI Total Test Suite")
    print("=" * 50)
    
    # Change to the project directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # Run tests with coverage
    cmd = [
        sys.executable, "-m", "pytest",
        "tests/",
        "-v",
        "--cov=entrypoint",
        "--cov-report=term-missing",
        "--cov-report=html",
        "--tb=short"
    ]
    
    try:
        result = subprocess.run(cmd, check=True)
        print("\n" + "=" * 50)
        print("✅ All tests passed!")
        print("📊 Coverage report generated in htmlcov/")
        return True
    except subprocess.CalledProcessError as e:
        print("\n" + "=" * 50)
        print("❌ Some tests failed!")
        print(f"Exit code: {e.returncode}")
        return False


def run_integration_tests_only():
    """Run only integration tests."""
    print("Running Integration Tests Only")
    print("=" * 50)
    
    cmd = [
        sys.executable, "-m", "pytest",
        "tests/",
        "-v",
        "-m", "integration",
        "--tb=short"
    ]
    
    try:
        result = subprocess.run(cmd, check=True)
        print("\n" + "=" * 50)
        print("✅ Integration tests passed!")
        return True
    except subprocess.CalledProcessError as e:
        print("\n" + "=" * 50)
        print("❌ Integration tests failed!")
        print(f"Exit code: {e.returncode}")
        return False


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--integration-only":
        success = run_integration_tests_only()
    else:
        success = run_tests()
    
    sys.exit(0 if success else 1)