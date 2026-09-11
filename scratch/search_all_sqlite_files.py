import os

def find_sqlite():
    print("=== SEARCHING FOR ALL SQLITE/DB FILES ===")
    for root, dirs, files in os.walk('.'):
        if '.venv' in root or '.git' in root:
            continue
        for file in files:
            if file.endswith('.sqlite') or file.endswith('.db'):
                path = os.path.join(root, file)
                size = os.path.getsize(path)
                print(f"File: {path} | Size: {size} bytes")

if __name__ == '__main__':
    find_sqlite()
