import sqlite3

conn = sqlite3.connect('database.sqlite')
cursor = conn.cursor()

# Get total number of events
cursor.execute("SELECT COUNT(*) FROM events")
total_events = cursor.fetchone()[0]

# Get events not matching SNRU
cursor.execute("SELECT COUNT(*) FROM events WHERE latitude != 17.18994 OR longitude != 104.09153")
non_matching = cursor.fetchone()[0]

print(f"Total events: {total_events}")
print(f"Events not matching SNRU: {non_matching}")

# Print sample events
cursor.execute("SELECT id, title, latitude, longitude FROM events LIMIT 5")
for row in cursor.fetchall():
    print(row)

conn.close()
