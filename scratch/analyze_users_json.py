import json
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

def count_hashes():
    try:
        with open('users.json', 'r', encoding='utf-8') as f:
            users = json.load(f)
            
        print(f"Total users in users.json: {len(users)}")
        
        hash_counts = {}
        for username, data in users.items():
            pwd_hash = data.get('password')
            if pwd_hash not in hash_counts:
                hash_counts[pwd_hash] = []
            hash_counts[pwd_hash].append(username)
            
        print(f"Unique hashes: {len(hash_counts)}")
        print("="*60)
        for h, usernames in hash_counts.items():
            # truncate hash for printing
            short_hash = h[:35] + "..." if h else "None/Empty"
            print(f"Hash: {short_hash} -> Count: {len(usernames)}")
            print(f"Sample users: {usernames[:5]}")
            print("-" * 40)
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    count_counts = count_hashes()
