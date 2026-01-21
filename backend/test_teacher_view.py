import urllib.request
import urllib.parse
import json
import sys

# 配置
BASE_URL = 'http://127.0.0.1:5000/api'
TEACHER_USERNAME = 'jqls'
TEACHER_PASSWORD = 'password123'  # 假设这是默认密码

def post(url, data):
    data_bytes = json.dumps(data).encode('utf-8')
    req = urllib.request.Request(url, data=data_bytes, headers={'Content-Type': 'application/json'})
    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        print(f"HTTP Error: {e.code} - {e.read().decode('utf-8')}")
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None

def get(url, token):
    req = urllib.request.Request(url, headers={'Authorization': f'Bearer {token}'})
    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode('utf-8')), response.getcode()
    except urllib.error.HTTPError as e:
        print(f"HTTP Error: {e.code} - {e.read().decode('utf-8')}")
        return None, e.code
    except Exception as e:
        print(f"Error: {e}")
        return None, 500

def check_teacher_dashboard():
    print("\n--- Checking Teacher Dashboard ---")
    login_resp = post(f"{BASE_URL}/auth/login", {'username': TEACHER_USERNAME, 'password': TEACHER_PASSWORD})
    if not login_resp or login_resp['code'] != 200:
        print("Login failed")
        return

    token = login_resp['data']['access_token']
    print("Login successful.")

    # 1. 获取问题列表
    list_resp, code = get(f"{BASE_URL}/questions/teacher-dashboard", token)
    if code != 200:
        print("Failed to get dashboard list")
        return

    data_list = list_resp['data']
    print(f"Found {len(data_list)} student groups.")
    
    question_id = None
    if data_list:
        first_group = data_list[0]
        print(f"First group student: {first_group['student_name']}")
        if first_group['questions']:
            first_q = first_group['questions'][0]
            print(f"First Question: ID={first_q['id']}, Title={first_q['title']}, Status={first_q['status']}")
            question_id = first_q['id']
    
    # 2. 获取问题详情
    if question_id:
        print(f"\n--- Checking Question Details (ID: {question_id}) ---")
        detail_resp, code = get(f"{BASE_URL}/questions/{question_id}", token)
        if code == 200:
            detail_data = detail_resp['data']
            print(f"Title: {detail_data['title']}")
            print(f"Status: {detail_data['status']}")
            print(f"Messages count: {len(detail_data.get('messages', []))}")
        else:
            print("Failed to get question details")

if __name__ == "__main__":
    check_teacher_dashboard()
