def find_def(name):
    with open('app.py', 'r', encoding='utf-8') as f:
        lines = f.readlines()
    for idx, line in enumerate(lines, 1):
        if f"def {name}(" in line:
            start = idx
            print(f"--- {name} ---")
            for i in range(start, start + 10):
                print(f"{i}: {lines[i-1].rstrip()}")

find_def('load_users')
find_def('load_participations')
find_def('load_registrations')
find_def('load_carousel')
find_def('load_events')
