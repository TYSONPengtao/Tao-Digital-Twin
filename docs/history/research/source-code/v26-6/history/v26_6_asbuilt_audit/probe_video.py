from pathlib import Path
import sys,subprocess
W=Path('work').resolve();sys.path.insert(0,str(W/'libs'))
import imageio_ffmpeg
r=subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(),'-hide_banner','-i','E:/jz/VID_20260507_152114_00_001.insv'],capture_output=True)
s=r.stderr.decode('utf8','replace');print('\n'.join(s.splitlines()[:80]))
