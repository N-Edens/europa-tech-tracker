#!/usr/bin/env python3
"""
Test runner for Europa Tech Tracker
Comprehensive testing across all phases and components
"""

import sys
import subprocess
import argparse
from pathlib import Path


def run_command(cmd, description):
    """Run a command and report results"""
    print(f"\n🔄 {description}")
    print(f"Command: {' '.join(cmd)}")
    print("-" * 60)
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        print(f"✅ {description} - PASSED")
        if result.stdout:
            print(result.stdout)
    else:
        print(f"❌ {description} - FAILED")
        if result.stderr:
            print("STDERR:", result.stderr)
        if result.stdout:
            print("STDOUT:", result.stdout)
    
    return result.returncode == 0


def main():
    parser = argparse.ArgumentParser(description='Run Europa Tech Tracker tests')
    parser.add_argument('--suite', choices=['unit', 'integration', 'workflow', 'all'], 
                       default='all', help='Test suite to run')
    parser.add_argument('--coverage', action='store_true', 
                       help='Generate coverage report')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Verbose output')
    parser.add_argument('--fast', action='store_true',
                       help='Skip slow tests')
    
    args = parser.parse_args()
    
    # Change to project root
    project_root = Path(__file__).parent.parent
    print(f"📁 Running tests from: {project_root.absolute()}")
    
    # Base pytest command
    pytest_cmd = ['python', '-m', 'pytest']
    
    if args.verbose:
        pytest_cmd.append('-v')
    
    if args.fast:
        pytest_cmd.extend(['-m', 'not slow'])
    
    if args.coverage:
        pytest_cmd.extend(['--cov=src', '--cov-report=html', '--cov-report=term'])
    
    success_count = 0
    total_count = 0
    
    # Run test suites based on selection
    if args.suite in ['unit', 'all']:
        total_count += 1
        cmd = pytest_cmd + ['-m', 'unit', 'tests/']
        if run_command(cmd, "Unit Tests (Phase 1-3 Components)"):
            success_count += 1
    
    if args.suite in ['integration', 'all']:
        total_count += 1
        cmd = pytest_cmd + ['-m', 'integration', 'tests/']
        if run_command(cmd, "Integration Tests (RSS Processing Pipeline)"):
            success_count += 1
    
    if args.suite in ['workflow', 'all']:
        total_count += 1
        cmd = pytest_cmd + ['-m', 'workflow', 'tests/']
        if run_command(cmd, "Workflow Tests (GitHub Actions Validation)"):
            success_count += 1
    
    if args.suite == 'all':
        # Run additional comprehensive test
        total_count += 1
        cmd = pytest_cmd + ['tests/']
        if run_command(cmd, "All Tests Combined"):
            success_count += 1
    
    # Summary
    print("\n" + "="*60)
    print("🏁 TEST SUMMARY")
    print("="*60)
    
    if success_count == total_count:
        print(f"✅ All test suites passed! ({success_count}/{total_count})")
        print("\n🎉 Europa Tech Tracker is ready for all phases!")
        
        if args.coverage:
            print("\n📊 Coverage report generated in htmlcov/index.html")
        
        return 0
    else:
        print(f"❌ Some tests failed ({success_count}/{total_count} passed)")
        print("\n🔧 Please fix failing tests before proceeding to next phase")
        return 1


if __name__ == "__main__":
    sys.exit(main())