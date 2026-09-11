import os

def search_files():
    print("=== Searching for sqlite3.connect or get_db_connection in python files ===")
    for root, dirs, files in os.walk('.'):
        if '.venv' in root or '__pycache__' in root or '.git' in root:
            continue
        for file in files:
            if file.endswith('.py'):
                path = os.path.join(root, file)
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                    for idx, line in enumerate(lines, 1):
                        if 'sqlite3.connect' in line or 'get_db_connection' in line:
                            print(f"{path} | Line {idx}: {line.strip()}")
                except Exception as e:
                    pass

if __name__ == '__main__':
    search_files()
