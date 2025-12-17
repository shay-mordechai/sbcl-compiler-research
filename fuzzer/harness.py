#!/usr/bin/env python3
"""
SBCL-LISP Fuzzing Test Harness

This module provides a test harness for systematically testing SBCL-LISP
with various inputs and collecting detailed crash information.

Author: [Your Name]
Date: [Current Date]
"""

import os
import sys
import subprocess
import json
import time
import signal
from pathlib import Path
from typing import Dict, List, Any, Optional

class SBCLTestHarness:
    """
    Test harness for running SBCL tests and collecting detailed results.
    """
    
    def __init__(self, sbcl_path: str = "sbcl", results_dir: str = "results"):
        """
        Initialize the test harness.
        
        Args:
            sbcl_path: Path to SBCL executable
            results_dir: Directory to store test results
        """
        self.sbcl_path = sbcl_path
        self.results_dir = Path(results_dir)
        self.results_dir.mkdir(exist_ok=True)
        
        # Create subdirectories for different types of results
        (self.results_dir / "crashes").mkdir(exist_ok=True)
        (self.results_dir / "timeouts").mkdir(exist_ok=True)
        (self.results_dir / "successful").mkdir(exist_ok=True)
        (self.results_dir / "logs").mkdir(exist_ok=True)
        
        self.test_results = []
        
    def run_single_test(self, test_file: Path, timeout: int = 30) -> Dict[str, Any]:
        """
        Run a single test case with detailed monitoring.
        
        Args:
            test_file: Path to the test file
            timeout: Timeout in seconds
            
        Returns:
            Detailed test result dictionary
        """
        result = {
            'test_file': str(test_file),
            'timestamp': time.time(),
            'timeout': timeout,
            'crashed': False,
            'timed_out': False,
            'return_code': None,
            'stdout': '',
            'stderr': '',
            'execution_time': 0,
            'memory_usage': 0,
            'signal': None,
            'core_dump': False
        }
        
        start_time = time.time()
        
        try:
            # Prepare the command
            cmd = [self.sbcl_path, '--noinform', '--load', str(test_file), '--quit']
            
            # Run the process
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                preexec_fn=os.setsid if os.name != 'nt' else None
            )
            
            try:
                stdout, stderr = process.communicate(timeout=timeout)
                result['stdout'] = stdout
                result['stderr'] = stderr
                result['return_code'] = process.returncode
                
            except subprocess.TimeoutExpired:
                # Kill the process group
                if os.name != 'nt':
                    os.killpg(os.getpgid(process.pid), signal.SIGTERM)
                else:
                    process.terminate()
                
                stdout, stderr = process.communicate()
                result['stdout'] = stdout
                result['stderr'] = stderr
                result['timed_out'] = True
                result['return_code'] = -1
                
        except Exception as e:
            result['crashed'] = True
            result['stderr'] = str(e)
            result['return_code'] = -1
        
        result['execution_time'] = time.time() - start_time
        
        # Analyze the result
        if result['return_code'] != 0 and not result['timed_out']:
            result['crashed'] = True
            
        # Check for specific crash indicators
        if result['stderr']:
            crash_indicators = [
                'segmentation fault',
                'bus error',
                'illegal instruction',
                'abort',
                'assertion failed',
                'memory corruption',
                'stack overflow'
            ]
            
            stderr_lower = result['stderr'].lower()
            for indicator in crash_indicators:
                if indicator in stderr_lower:
                    result['crashed'] = True
                    break
        
        return result
    
    def save_test_result(self, result: Dict[str, Any]):
        """
        Save test result to appropriate directory and log file.
        
        Args:
            result: Test result dictionary
        """
        timestamp = time.strftime("%Y%m%d_%H%M%S", time.localtime(result['timestamp']))
        test_name = Path(result['test_file']).stem
        
        # Determine result category
        if result['crashed']:
            category = "crashes"
        elif result['timed_out']:
            category = "timeouts"
        else:
            category = "successful"
        
        # Save detailed result as JSON
        result_file = self.results_dir / category / f"{test_name}_{timestamp}.json"
        with open(result_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2)
        
        # Save test file copy if it's a crash or timeout
        if result['crashed'] or result['timed_out']:
            test_copy = self.results_dir / category / f"{test_name}_{timestamp}.lisp"
            if Path(result['test_file']).exists():
                import shutil
                shutil.copy2(result['test_file'], test_copy)
        
        # Append to main log
        log_file = self.results_dir / "logs" / f"test_log_{time.strftime('%Y%m%d')}.txt"
        with open(log_file, 'a', encoding='utf-8') as f:
            status = "CRASH" if result['crashed'] else "TIMEOUT" if result['timed_out'] else "PASS"
            f.write(f"[{timestamp}] {status} - {result['test_file']} "
                   f"(RC: {result['return_code']}, Time: {result['execution_time']:.2f}s)\n")
            
            if result['stderr']:
                f.write(f"  STDERR: {result['stderr'][:200]}...\n")
            f.write("\n")
    
    def run_test_suite(self, test_files: List[Path], timeout: int = 30) -> Dict[str, Any]:
        """
        Run a suite of test files.
        
        Args:
            test_files: List of test file paths
            timeout: Timeout per test in seconds
            
        Returns:
            Summary statistics
        """
        stats = {
            'total_tests': len(test_files),
            'passed': 0,
            'crashed': 0,
            'timed_out': 0,
            'start_time': time.time(),
            'end_time': None
        }
        
        print(f"Running test suite with {len(test_files)} test cases...")
        print(f"Timeout per test: {timeout}s")
        print("-" * 50)
        
        for i, test_file in enumerate(test_files):
            print(f"Running test {i+1}/{len(test_files)}: {test_file.name}")
            
            result = self.run_single_test(test_file, timeout)
            self.save_test_result(result)
            self.test_results.append(result)
            
            # Update statistics
            if result['crashed']:
                stats['crashed'] += 1
                print(f"  CRASHED (RC: {result['return_code']})")
            elif result['timed_out']:
                stats['timed_out'] += 1
                print(f"  TIMED OUT")
            else:
                stats['passed'] += 1
                print(f"  PASSED")
            
            # Progress update
            if (i + 1) % 10 == 0:
                print(f"Progress: {i + 1}/{len(test_files)} - "
                      f"Crashed: {stats['crashed']}, Timeouts: {stats['timed_out']}")
        
        stats['end_time'] = time.time()
        
        # Save summary
        summary_file = self.results_dir / "test_summary.json"
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(stats, f, indent=2)
        
        return stats
    
    def generate_report(self) -> str:
        """
        Generate a summary report of all test results.
        
        Returns:
            Report as string
        """
        if not self.test_results:
            return "No test results available."
        
        total = len(self.test_results)
        crashed = sum(1 for r in self.test_results if r['crashed'])
        timed_out = sum(1 for r in self.test_results if r['timed_out'])
        passed = total - crashed - timed_out
        
        avg_execution_time = sum(r['execution_time'] for r in self.test_results) / total
        
        report = f"""
SBCL-LISP Test Harness Report
=============================

Total Tests: {total}
Passed: {passed} ({passed/total*100:.1f}%)
Crashed: {crashed} ({crashed/total*100:.1f}%)
Timed Out: {timed_out} ({timed_out/total*100:.1f}%)

Average Execution Time: {avg_execution_time:.2f}s

Results stored in: {self.results_dir}
"""
        
        return report

def main():
    """Main entry point for the test harness."""
    import argparse
    import glob
    
    parser = argparse.ArgumentParser(description="SBCL-LISP Test Harness")
    parser.add_argument("--sbcl-path", default="sbcl", help="Path to SBCL executable")
    parser.add_argument("--results-dir", default="results", help="Results directory")
    parser.add_argument("--test-dir", required=True, help="Directory containing test files")
    parser.add_argument("--timeout", type=int, default=30, help="Timeout per test in seconds")
    parser.add_argument("--pattern", default="*.lisp", help="File pattern to match")
    
    args = parser.parse_args()
    
    # Find test files
    test_pattern = str(Path(args.test_dir) / args.pattern)
    test_files = [Path(f) for f in glob.glob(test_pattern)]
    
    if not test_files:
        print(f"No test files found matching pattern: {test_pattern}")
        sys.exit(1)
    
    # Initialize harness
    harness = SBCLTestHarness(args.sbcl_path, args.results_dir)
    
    # Run tests
    stats = harness.run_test_suite(test_files, args.timeout)
    
    # Generate report
    report = harness.generate_report()
    print(report)

if __name__ == "__main__":
    main()
