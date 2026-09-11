import json
from werkzeug.security import check_password_hash

def test_hypotheses():
    with open('users.json', 'r', encoding='utf-8') as f:
        users = json.load(f)
        
    print("Testing admin...")
    admin_hash = users['admin']['password']
    for p in ['admin', '1234', 'password', 'admin123', 'admin@scitech']:
        if check_password_hash(admin_hash, p):
            print(f"  Admin password is: '{p}'")
            break
            
    print("Testing major_sci...")
    major_hash = users['major_sci']['password']
    for p in ['password', '1234', 'major_sci', 'admin']:
        if check_password_hash(major_hash, p):
            print(f"  major_sci password is: '{p}'")
            break
            
    print("Testing dt...")
    dt_hash = users['dt']['password']
    for p in ['password', '1234', 'dt']:
        if check_password_hash(dt_hash, p):
            print(f"  dt password is: '{p}'")
            break

    print("Testing student 69102101101...")
    std_hash = users['69102101101']['password']
    # Hypotheses:
    # 1. The full student ID: '69102101101'
    # 2. Last 3 digits: '101'
    # 3. '1234'
    # 4. 'password'
    # 5. Last 4 digits: '1101'
    # 6. '101101'
    # 7. Last 8 digits: '02101101'
    # 8. 'student_101'
    # 9. '69102101101'
    hypotheses = [
        '69102101101', '101', '1234', 'password', '1101', '101101',
        '02101101', 'student', 'student_101', 'student_69102101101',
        '69102101101'
    ]
    for p in hypotheses:
        if check_password_hash(std_hash, p):
            print(f"  Student 69102101101 password is: '{p}'")
            break
            
    print("Testing student 69102102102...")
    std_hash_2 = users['69102102102']['password']
    for p in ['69102102102', '102', '1234', 'password', '2102', '02102']:
        if check_password_hash(std_hash_2, p):
            print(f"  Student 69102102102 password is: '{p}'")
            break
            
    print("Testing student 67102122111...")
    std_hash_3 = users['67102122111']['password']
    for p in ['67102122111', '111', '1234', 'password', '2111', '22111']:
        if check_password_hash(std_hash_3, p):
            print(f"  Student 67102122111 password is: '{p}'")
            break

if __name__ == "__main__":
    test_hypotheses()
