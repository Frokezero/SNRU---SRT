with open('admin.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

print("--- REGISTRATIONS MODAL ---")
for idx in range(1045, min(1120, len(lines))):
    print(f"{idx+1}: {lines[idx]}", end="")

print("\n--- REGISTRATIONS JS ---")
for idx in range(2810, min(2890, len(lines))):
    print(f"{idx+1}: {lines[idx]}", end="")
