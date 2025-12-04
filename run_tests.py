#!/usr/bin/env python
"""
Test runner script for PCO API Wrapper
Provides convenient commands for running different types of tests
"""

import sys
import subprocess
import argparse


def run_command(cmd, description):
    """Run a command and print results"""
    print(f"\n{'='*60}")
    print(f"  {description}")
    print('='*60)
    
    result = subprocess.run(cmd, shell=True)
    return result.returncode


def main():
    parser = argparse.ArgumentParser(description='Run tests for PCO API Wrapper')
    parser.add_argument(
        'test_type',
        nargs='?',
        default='unit',
        choices=['unit', 'integration', 'all', 'coverage', 'quick'],
        help='Type of tests to run (default: unit)'
    )
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Verbose output'
    )
    parser.add_argument(
        '--no-cov',
        action='store_true',
        help='Run without coverage'
    )
    
    args = parser.parse_args()
    
    # Base pytest command
    verbose_flag = '-vv' if args.verbose else '-v'
    
    if args.test_type == 'unit':
        # Run only unit tests
        cmd = f'pytest tests/unit {verbose_flag}'
        if not args.no_cov:
            cmd += ' --cov=src --cov-report=html --cov-report=term-missing'
        return run_command(cmd, 'Running Unit Tests')
    
    elif args.test_type == 'integration':
        # Run only integration tests (requires PCO credentials)
        cmd = f'pytest tests/integration {verbose_flag} -m integration'
        return run_command(cmd, 'Running Integration Tests')
    
    elif args.test_type == 'all':
        # Run all tests
        cmd = f'pytest tests/ {verbose_flag}'
        if not args.no_cov:
            cmd += ' --cov=src --cov-report=html --cov-report=term-missing'
        return run_command(cmd, 'Running All Tests')
    
    elif args.test_type == 'coverage':
        # Run tests with detailed coverage report
        print("\n" + "="*60)
        print("  Running Tests with Coverage Analysis")
        print("="*60)
        
        # Run unit tests with coverage
        result = run_command(
            f'pytest tests/unit {verbose_flag} --cov=src --cov-report=html --cov-report=term-missing --cov-report=json',
            'Unit Tests with Coverage'
        )
        
        if result == 0:
            print("\n" + "="*60)
            print("  Coverage Report Generated")
            print("="*60)
            print("\n📊 HTML Report: htmlcov/index.html")
            print("📊 JSON Report: coverage.json")
            print("\nOpen htmlcov/index.html in your browser to view detailed coverage")
        
        return result
    
    elif args.test_type == 'quick':
        # Quick test run (unit tests only, no coverage)
        cmd = f'pytest tests/unit {verbose_flag} --tb=short'
        return run_command(cmd, 'Quick Test Run (Unit Tests Only)')
    
    return 0


if __name__ == '__main__':
    sys.exit(main())