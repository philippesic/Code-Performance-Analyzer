#!/usr/bin/env python3
"""
Standalone Test Runner
Executes generated performance test files and provides additional analysis.
"""

import sys
import os
import subprocess
import json
from typing import Dict, List, Optional
import argparse


class TestRunner:
    """Runner for executing performance tests."""
    
    def __init__(self, test_file: str):
        self.test_file = test_file
        self.results = None
    
    def check_dependencies(self) -> Dict[str, bool]:
        """
        Check if required dependencies are installed.
        
        Returns:
            Dictionary of dependency: is_installed
        """
        dependencies = {
            'matplotlib': False,
            'numpy': False
        }
        
        for dep in dependencies.keys():
            try:
                __import__(dep)
                dependencies[dep] = True
            except ImportError:
                dependencies[dep] = False
        
        return dependencies
    
    def install_dependencies(self) -> bool:
        """
        Install missing dependencies.
        
        Returns:
            True if successful, False otherwise
        """
        deps = self.check_dependencies()
        missing = [dep for dep, installed in deps.items() if not installed]
        
        if not missing:
            print("✅ All dependencies are installed!")
            return True
        
        print(f"📦 Installing missing dependencies: {', '.join(missing)}")
        
        try:
            subprocess.check_call([
                sys.executable, '-m', 'pip', 'install', '--quiet', *missing
            ])
            print("✅ Dependencies installed successfully!")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install dependencies: {e}")
            return False
    
    def run_test(self, auto_install: bool = True) -> bool:
        """
        Execute the performance test file.
        
        Args:
            auto_install: Automatically install missing dependencies
        
        Returns:
            True if test executed successfully
        """
        if not os.path.exists(self.test_file):
            print(f"❌ Test file not found: {self.test_file}")
            return False
        
        # Check dependencies
        if auto_install:
            deps = self.check_dependencies()
            if not all(deps.values()):
                self.install_dependencies()
        
        print(f"\n🚀 Running performance test: {self.test_file}\n")
        print("=" * 70)
        
        try:
            # Run the test file
            result = subprocess.run(
                [sys.executable, self.test_file],
                capture_output=False,
                text=True,
                check=True
            )
            
            print("=" * 70)
            print("\n✅ Test completed successfully!")
            return True
            
        except subprocess.CalledProcessError as e:
            print("=" * 70)
            print(f"\n❌ Test execution failed with exit code {e.returncode}")
            if e.stderr:
                print(f"Error: {e.stderr}")
            return False
        except Exception as e:
            print(f"\n❌ Unexpected error: {e}")
            return False
    
    def quick_test(self, sizes: Optional[List[int]] = None) -> None:
        """
        Run a quick test with smaller input sizes.
        
        Args:
            sizes: Optional list of test sizes (default: [10, 50, 100])
        """
        if sizes is None:
            sizes = [10, 50, 100]
        
        print(f"\n⚡ Running quick test with sizes: {sizes}")
        print("Note: Edit the test file to customize test parameters.\n")
        
        self.run_test()


class BatchTestRunner:
    """Runner for executing multiple performance tests."""
    
    def __init__(self, test_directory: str = "."):
        self.test_directory = test_directory
    
    def find_test_files(self) -> List[str]:
        """
        Find all performance test files in directory.
        
        Returns:
            List of test file paths
        """
        test_files = []
        for root, dirs, files in os.walk(self.test_directory):
            for file in files:
                if file.endswith('_performance_test.py'):
                    test_files.append(os.path.join(root, file))
        
        return test_files
    
    def run_all_tests(self) -> Dict[str, bool]:
        """
        Run all found performance tests.
        
        Returns:
            Dictionary mapping test file to success status
        """
        test_files = self.find_test_files()
        
        if not test_files:
            print(f"⚠️  No performance test files found in {self.test_directory}")
            return {}
        
        print(f"📋 Found {len(test_files)} performance test(s)\n")
        
        results = {}
        for i, test_file in enumerate(test_files, 1):
            print(f"\n{'='*70}")
            print(f"Test {i}/{len(test_files)}: {os.path.basename(test_file)}")
            print('='*70)
            
            runner = TestRunner(test_file)
            success = runner.run_test()
            results[test_file] = success
        
        # Summary
        print("\n" + "="*70)
        print("SUMMARY")
        print("="*70)
        
        passed = sum(1 for success in results.values() if success)
        total = len(results)
        
        for test_file, success in results.items():
            status = "✅ PASS" if success else "❌ FAIL"
            print(f"{status} - {os.path.basename(test_file)}")
        
        print(f"\nTotal: {passed}/{total} tests passed")
        
        return results


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Run performance tests for analyzed functions"
    )
    
    parser.add_argument(
        'test_file',
        nargs='?',
        help='Performance test file to run (optional for batch mode)'
    )
    
    parser.add_argument(
        '--batch',
        action='store_true',
        help='Run all performance tests in current directory'
    )
    
    parser.add_argument(
        '--directory',
        '-d',
        default='.',
        help='Directory to search for tests (batch mode only)'
    )
    
    parser.add_argument(
        '--no-install',
        action='store_true',
        help='Skip automatic dependency installation'
    )
    
    parser.add_argument(
        '--quick',
        action='store_true',
        help='Run quick test with smaller input sizes'
    )
    
    args = parser.parse_args()
    
    if args.batch:
        # Batch mode
        runner = BatchTestRunner(args.directory)
        runner.run_all_tests()
    elif args.test_file:
        # Single test mode
        runner = TestRunner(args.test_file)
        
        if args.quick:
            runner.quick_test()
        else:
            runner.run_test(auto_install=not args.no_install)
    else:
        # No arguments - try to find and run tests in current directory
        batch_runner = BatchTestRunner('.')
        test_files = batch_runner.find_test_files()
        
        if not test_files:
            print("⚠️  No test file specified and no performance tests found.")
            print("\nUsage:")
            print("  python test_runner.py <test_file>        # Run specific test")
            print("  python test_runner.py --batch            # Run all tests")
            parser.print_help()
            sys.exit(1)
        else:
            print(f"Found {len(test_files)} test file(s). Running all...\n")
            batch_runner.run_all_tests()


if __name__ == "__main__":
    main()

