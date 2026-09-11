import os
import sys

# Ensure UTF-8 output
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

def search_files(directory, query):
    results = []
    for root, dirs, files in os.walk(directory):
        # Skip .git, .venv, etc.
        if any(ignored in root for ignored in ['.git', '.venv', '__pycache__', '.pytest_cache']):
            continue
            
        for file in files:
            file_path = os.path.join(root, file)
            try:
                # Try reading as UTF-8
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    for i, line in enumerate(f, 1):
                        if query in line:
                            results.append((file_path, i, line.strip()))
            except Exception as e:
                pass
    return results

def main():
    queries = ["คอมพิวเตอร์", "สุขภาพ", "เคมี", "ฟิสิกส์", "วิทยาศาสตร์สิ่งแวดล้อม", "วิทยาศาสตร์สุขภาพ", "วิทยาการคอมพิวเตอร์"]
    for q in queries:
        print(f"\n=== Searching for '{q}' ===")
        res = search_files('.', q)
        if res:
            # Group by file to be concise
            by_file = {}
            for path, line_no, content in res:
                if path not in by_file:
                    by_file[path] = []
                by_file[path].append((line_no, content))
                
            for path, matches in by_file.items():
                print(f"File: {path} ({len(matches)} matches)")
                # Print first 3 matches
                for line_no, content in matches[:3]:
                    print(f"  Line {line_no}: {content[:100]}")
                if len(matches) > 3:
                    print(f"  ... and {len(matches) - 3} more matches")
        else:
            print("No matches found.")

if __name__ == "__main__":
    main()
