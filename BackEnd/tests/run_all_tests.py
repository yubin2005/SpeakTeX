"""
Run All SpeakTeX Backend Tests
Executes all test scripts and provides summary
"""

import subprocess
import sys
from pathlib import Path

# Test scripts in execution order
TEST_SCRIPTS = [
    ("AWS Credentials", "test_aws_credentials.py"),
    ("S3 Operations", "test_s3_operations.py"),
    ("Gemini API", "test_gemini_api.py"),
    ("Transcribe Job", "test_transcribe_job.py"),
    ("Lambda Trigger", "test_lambda_trigger.py"),
]


def run_test(test_name, script_path):
    """
    Run a single test script
    
    Args:
        test_name: Display name of the test
        script_path: Path to test script
        
    Returns:
        True if test passed, False otherwise
    """
    print("\n" + "="*70)
    print(f"Running: {test_name}")
    print("="*70)
    
    try:
        result = subprocess.run(
            [sys.executable, script_path],
            capture_output=False,
            text=True
        )
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"\n❌ Error running test: {str(e)}")
        return False


def main():
    """Main test runner"""
    print("\n" + "="*70)
    print("SpeakTeX Backend - Running All Tests")
    print("="*70)
    
    # Get tests directory
    tests_dir = Path(__file__).parent
    
    # Track results
    results = {}
    
    # Run each test
    for test_name, script_name in TEST_SCRIPTS:
        script_path = tests_dir / script_name
        
        if not script_path.exists():
            print(f"\n❌ Test script not found: {script_name}")
            results[test_name] = False
            continue
        
        success = run_test(test_name, script_path)
        results[test_name] = success
    
    # Print summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70 + "\n")
    
    all_passed = True
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status:10} - {test_name}")
        if not passed:
            all_passed = False
    
    print("\n" + "="*70)
    if all_passed:
        print("✅ ALL TESTS PASSED!")
        print("Your AWS and API configuration is working correctly.")
    else:
        print("❌ SOME TESTS FAILED")
        print("Check individual test output above for details.")
    print("="*70 + "\n")
    
    return all_passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

