import sys
sys.path.insert(0, '/home/umair/Desktop/FlutterSwarm')

print("Testing agent fix...")

try:
    from agents.testing_agent import TestingAgent
    agent = TestingAgent()
    print("SUCCESS: TestingAgent created")
except Exception as e:
    print(f"ERROR: {e}")

try:
    from tests.run_tests import main
    result = main()
    print(f"Tests result: {result}")
except Exception as e:
    print(f"Test execution error: {e}")