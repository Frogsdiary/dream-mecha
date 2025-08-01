import subprocess
import sys
import os

# Run the executable and capture output
try:
    result = subprocess.run(
        ["./dist/Blockmaker.exe"],
        capture_output=True,
        text=True,
        timeout=10  # 10 second timeout
    )
    print("STDOUT:")
    print(result.stdout)
    print("\nSTDERR:")
    print(result.stderr)
    print(f"\nReturn code: {result.returncode}")
except subprocess.TimeoutExpired:
    print("Executable timed out after 10 seconds")
except Exception as e:
    print(f"Error running executable: {e}") 