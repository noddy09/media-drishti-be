import requests
import json

BASE_URL = "http://127.0.0.1:8000/api/"
ADMIN_USER = "admin"
ADMIN_PASS = "admin"

# Helper to print responses
def print_resp(label, resp):
    print(f"{label} -> {resp.status_code}")
    try:
        print(resp.json())
    except Exception:
        print(resp.text)

# Authenticate and get JWT token
def get_token(username, password):
    resp = requests.post(BASE_URL + "auth/token/", data={"username": username, "password": password})
    resp.raise_for_status()
    return resp.json()["access"]

def test_endpoint(token, method, endpoint, data=None, files=None, json_data=None):
    headers = {"Authorization": f"Bearer {token}"}
    url = BASE_URL + endpoint
    if json_data:
        headers["Content-Type"] = "application/json"
        resp = requests.request(method, url, headers=headers, json=json_data)
    else:
        resp = requests.request(method, url, headers=headers, data=data, files=files)
    print_resp(f"{method} {endpoint}", resp)
    return resp

def main():
    # 1. Admin login
    admin_token = get_token(ADMIN_USER, ADMIN_PASS)

    # 2. Create a new user (employee) as admin
    new_user = {
        "username": "employee1",
        "password": "password123",
        "email": "employee1@example.com",
        "is_active": True,
        "is_staff": False
    }
    resp = test_endpoint(admin_token, "POST", "users/users/", json_data=new_user)
    if resp.status_code in (200, 201):
        print("User created.")
    else:
        print("User creation failed.")
        print("Response:", resp.text)
        return  # Stop if user creation fails

    # 3. Grant permissions if needed (assume role field is enough, else adjust here)

    # 4. Login as employee
    emp_token = get_token("employee1", "password123")

    # 5. Test POST/PUT endpoints as employee
    # Example: create a manual entry
    manual_entry = {
        "title": "Test News",
        "content": "This is a test news entry.",
        "source": "Test Source"
    }
    test_endpoint(emp_token, "POST", "manual-entries/manual-entries/", data=manual_entry)

    # Example: update the manual entry (assuming id=1 for demo)
    update_entry = {
        "title": "Updated News Title"
    }
    test_endpoint(emp_token, "PUT", "manual-entries/manual-entries/1/", data=update_entry)

    # Example: create a clip (dummy data, adjust as needed)
    clip_data = {
        "file": "dummy.pdf",
        "file_type": "pdf",
        "page": 1,
        "x": 10,
        "y": 10,
        "width": 100,
        "height": 100
    }
    test_endpoint(emp_token, "POST", "clipping/clips/", data=clip_data)

    # Example: tag a clip (dummy data, adjust as needed)
    tag_data = {
        "clip": 1,
        "tag": "Politics"
    }
    test_endpoint(emp_token, "POST", "tagging/clip-tags/", data=tag_data)

if __name__ == "__main__":
    main()
