import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

log_file = 'auto_open.log'
try:
    with open(log_file, 'rb') as f:
        # Seek to the end of the file minus some bytes (e.g. 5000 bytes)
        f.seek(0, 2)
        size = f.tell()
        seek_pos = max(0, size - 15000)
        f.seek(seek_pos)
        tail_bytes = f.read()
        tail_str = tail_bytes.decode('utf-8', errors='ignore')
        
        # Split into lines and take the last 80 lines
        lines = tail_str.splitlines()
        print(f"--- Last 80 lines of {log_file} ---")
        for line in lines[-80:]:
            print(line)
except Exception as e:
    print(f"Error reading log file: {e}")
