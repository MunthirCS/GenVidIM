#!/usr/bin/env python3
"""
Test if all required dependencies can be imported successfully
This simulates what will happen in the serverless container
"""

import sys
import subprocess

print("\n" + "="*60)
print("TESTING SERVERLESS DEPENDENCIES")
print("="*60 + "\n")

# List of critical dependencies that will be in the Dockerfile
dependencies = [
    ("numpy", "import numpy; print(f'NumPy: {numpy.__version__}'); assert numpy.__version__ < '2', 'NumPy must be <2'"),
    ("torch", "import torch; print(f'PyTorch: {torch.__version__}')"),
    ("einops", "import einops; print('einops: OK')"),
    ("transformers", "import transformers; print(f'Transformers: {transformers.__version__}')"),
    ("diffusers", "import diffusers; print(f'Diffusers: {diffusers.__version__}')"),
    ("peft", "import peft; print(f'PEFT: {peft.__version__}')"),
    ("decord", "import decord; print(f'Decord: {decord.__version__}')"),
    ("sentencepiece", "import sentencepiece; print('SentencePiece: OK')"),
    ("librosa", "import librosa; print(f'Librosa: {librosa.__version__}')"),
    ("cv2", "import cv2; print(f'OpenCV: {cv2.__version__}')"),
    ("PIL", "from PIL import Image; print('Pillow: OK')"),
    ("safetensors", "import safetensors; print('SafeTensors: OK')"),
    ("accelerate", "import accelerate; print(f'Accelerate: {accelerate.__version__}')"),
    ("imageio", "import imageio; print('ImageIO: OK')"),
    ("av", "import av; print(f'PyAV: {av.__version__}')"),
]

optional_dependencies = [
    ("onnxruntime", "import onnxruntime; print(f'ONNXRuntime: {onnxruntime.__version__}')"),
    ("pandas", "import pandas; print(f'Pandas: {pandas.__version__}')"),
]

results = {
    "passed": [],
    "failed": [],
    "optional_missing": []
}

# Test critical dependencies
print("Testing CRITICAL dependencies:")
print("-" * 60)

for name, test_code in dependencies:
    try:
        exec(test_code)
        results["passed"].append(name)
        print(f"  ✓ {name}")
    except ImportError as e:
        results["failed"].append((name, str(e)))
        print(f"  ✗ {name} - NOT INSTALLED: {e}")
    except AssertionError as e:
        results["failed"].append((name, str(e)))
        print(f"  ✗ {name} - VERSION ERROR: {e}")
    except Exception as e:
        results["failed"].append((name, str(e)))
        print(f"  ✗ {name} - ERROR: {e}")

# Test optional dependencies
print("\n\nTesting OPTIONAL dependencies:")
print("-" * 60)

for name, test_code in optional_dependencies:
    try:
        exec(test_code)
        results["passed"].append(name)
        print(f"  ✓ {name}")
    except ImportError:
        results["optional_missing"].append(name)
        print(f"  ⊘ {name} - Not installed (optional)")
    except Exception as e:
        results["optional_missing"].append(name)
        print(f"  ⊘ {name} - ERROR: {e}")

# Summary
print("\n" + "="*60)
print("SUMMARY")
print("="*60)
print(f"✓ Passed: {len(results['passed'])}")
print(f"✗ Failed: {len(results['failed'])}")
print(f"⊘ Optional Missing: {len(results['optional_missing'])}")

if results["failed"]:
    print("\n⚠ CRITICAL FAILURES:")
    for name, error in results["failed"]:
        print(f"  • {name}: {error}")
    print("\n❌ Some dependencies are MISSING or have VERSION CONFLICTS")
    print("   These MUST be installed in the serverless container!")
    sys.exit(1)
else:
    print("\n✅ All critical dependencies are available!")
    if results["optional_missing"]:
        print(f"   ({len(results['optional_missing'])} optional packages missing but not required)")
    sys.exit(0)

