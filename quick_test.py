#!/usr/bin/env python3
"""
Quick Test - Fastest possible video generation for testing
~1-2 minutes generation time
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / 'serverless'))

from runpod_client import generate_video


def main():
    prompt = sys.argv[1] if len(sys.argv) > 1 else "a red car driving on a road"
    
    print("""
🧪 QUICK TEST MODE - Optimized for Speed
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Settings:
  • Size: 512x288 (very small, for testing only)
  • Steps: 10 (minimal quality, fast generation)
  • Expected time: 1-2 minutes ⚡⚡⚡

Note: This is for TESTING ONLY. Quality will be low.
      For production, use fast_generate.py with "fast" preset.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    """)
    
    print(f"📝 Prompt: {prompt}\n")
    
    success = generate_video(
        prompt=prompt,
        size="512*288",  # Very small for quick test
        steps=10         # Minimal steps
    )
    
    if success:
        print("""
✅ Test completed successfully!

Next steps:
  • For better quality: python fast_generate.py "prompt" fast
  • For production: python fast_generate.py "prompt" balanced
        """)
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
