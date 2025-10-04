#!/usr/bin/env python3
"""
Check generated videos
"""

from pathlib import Path
from datetime import datetime

videos_dir = Path('./videos')

print("\n📹 Generated Videos:")
print("="*60)

if not videos_dir.exists():
    print("❌ No videos folder yet. Videos will be saved to:")
    print(f"   {videos_dir.absolute()}")
    print("\nAfter generation completes, videos appear here.")
else:
    videos = list(videos_dir.glob('*.mp4'))
    
    if not videos:
        print("❌ No videos generated yet")
    else:
        print(f"✅ Found {len(videos)} video(s):\n")
        
        for video in sorted(videos, key=lambda x: x.stat().st_mtime, reverse=True):
            size_mb = video.stat().st_size / 1024 / 1024
            mtime = datetime.fromtimestamp(video.stat().st_mtime)
            
            print(f"  📹 {video.name}")
            print(f"     Size: {size_mb:.2f} MB")
            print(f"     Created: {mtime.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"     Path: {video.absolute()}")
            print()

print("="*60)
print(f"\n💡 Full path: {videos_dir.absolute()}")
print()

