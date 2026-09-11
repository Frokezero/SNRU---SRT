import requests

sess = requests.Session()
# Login as admin
res = sess.post('http://127.0.0.1:8080/api/login', json={'username': 'admin', 'password': 'password'})
print("Login:", res.status_code, res.text)

res = sess.get('http://127.0.0.1:8080/api/admin/dashboard-stats')
print("Dashboard Stats:", res.status_code, res.text)
