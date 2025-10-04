#!/usr/bin/env python3
"""
Fast Video Generation Client - Optimized for Speed
Generates videos in 2-4 minutes instead of 5-10 minutes
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / 'serverless'))

from runpod_client import generate_video


PRESETS = {
    "ultra_fast": {
        "size": "832*480",
        "steps": 15,
        "description": "2-3 min generation, acceptable quality"
    },
    "fast": {
        "size": "960*544", 
        "steps": 20,
        "description": "3-4 min generation, good quality"
    },
    "balanced": {
        "size": "1280*704",
        "steps": 25,
        "description": "4-6 min generation, high quality"
    },
    "quality": {
        "size": "1280*704",
        "steps": 35,
        "description": "5-10 min generation, best quality"
    }
}


def main():
    if len(sys.argv) < 2:
        print("""
🚀 Fast Video Generation with Speed Presets

Usage:
  python fast_generate.py "your prompt" [preset]

Presets (default: fast):
  ultra_fast - 2-3 min, 832x480, 15 steps (acceptable quality)
  fast       - 3-4 min, 960x544, 20 steps (good quality) ⭐ RECOMMENDED
  balanced   - 4-6 min, 1280x704, 25 steps (high quality)
  quality    - 5-10 min, 1280x704, 35 steps (best quality)

Examples:
  python fast_generate.py "a red sports car driving fast"
  python fast_generate.py "sunset over mountains" ultra_fast
  python fast_generate.py "cat playing with yarn" quality

Speed Comparison:
  • ultra_fast: 2-3 minutes ⚡⚡⚡
  • fast:       3-4 minutes ⚡⚡ (recommended)
  • balanced:   4-6 minutes ⚡
  • quality:    5-10 minutes (default original)
        """)
        sys.exit(1)
    
    prompt = sys.argv[1]
    preset_name = sys.argv[2] if len(sys.argv) > 2 else "fast"
    
    if preset_name not in PRESETS:
        print(f"❌ Unknown preset: {preset_name}")
        print(f"Available: {', '.join(PRESETS.keys())}")
        sys.exit(1)
    
    preset = PRESETS[preset_name]
    
    print(f"\n🎬 Fast Video Generation")
    print(f"=" * 60)
    print(f"📝 Prompt: {prompt}")
    print(f"⚡ Preset: {preset_name}")
    print(f"   {preset['description']}")
    print(f"📐 Size: {preset['size']}")
    print(f"⚙️  Steps: {preset['steps']}")
    print(f"=" * 60)
    print()
    
    success = generate_video(
        prompt=prompt,
        size=preset['size'],
        steps=preset['steps']
    )
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

