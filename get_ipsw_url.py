import urllib.request

# Search for leaked Snoopy aerial
queries = [
    "https://www.google.com/search?q=AD001_A008_C005_SNOOPY_SPACE+download",
    "https://archive.org/search?query=apple+aerial+snoopy+space",
]

# Try YouTube via yt-dlp (check if video exists)
import subprocess
result = subprocess.run(
    ["yt-dlp", "--get-url", "ytsearch1:Apple TV Snoopy Space aerial screensaver 4K download"],
    capture_output=True, text=True, timeout=30
)
print("yt-dlp:", result.stdout[:500] or result.stderr[:200])
