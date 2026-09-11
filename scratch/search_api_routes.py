import re
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

def find_routes():
    with open('app.py', 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()
        
    print("API Routes in app.py:")
    for i, line in enumerate(lines, 1):
        if '@app.route(' in line:
            print(f"Line {i}: {line.strip()}")

if __name__ == "__main__":
    find_routes()
