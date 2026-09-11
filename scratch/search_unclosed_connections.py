with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Let's find all occurrences of get_db_connection() and trace the block
lines = content.splitlines()
print("=== TRACING DB CONNECTIONS IN app.py ===")
for idx, line in enumerate(lines, 1):
    if 'get_db_connection()' in line:
        # Search the next 15 lines for 'close()'
        found_close = False
        conn_var = line.split('=')[0].strip()
        for offset in range(1, 25):
            if idx + offset - 1 < len(lines):
                future_line = lines[idx + offset - 1]
                if f'{conn_var}.close()' in future_line:
                    found_close = True
                    break
        if not found_close:
            print(f"WARNING: Line {idx} has unclosed connection: '{line.strip()}' (searched next 25 lines)")
        else:
            print(f"Line {idx} connection is closed correctly.")
