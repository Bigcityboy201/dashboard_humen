"""
Script để reset password cho user trong database
Sử dụng endpoint Java API để reset password (password sẽ được encode BCrypt tự động)
"""

import requests
import json

# Cấu hình
JAVA_API_URL = "http://localhost:8080"
USERNAME = "truong201"  # Username cần reset password
NEW_PASSWORD = "Quangtruong1"  # Password mới (sẽ được encode BCrypt)

def get_user_id(username, token):
    """Lấy user ID từ username"""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Tìm user trong danh sách
    response = requests.get(
        f"{JAVA_API_URL}/users?page=0&size=100",
        headers=headers
    )
    
    if response.status_code == 200:
        data = response.json()
        users = data.get("data", {}).get("content", [])
        for user in users:
            if user.get("userName") == username:
                return user.get("id")
    
    return None

def reset_password(user_id, new_password, token):
    """Reset password cho user"""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "password": new_password
    }
    
    response = requests.put(
        f"{JAVA_API_URL}/users/{user_id}/reset-password",
        headers=headers,
        json=payload
    )
    
    return response

if __name__ == "__main__":
    print("=" * 60)
    print("SCRIPT RESET PASSWORD")
    print("=" * 60)
    print(f"Username: {USERNAME}")
    print(f"New Password: {NEW_PASSWORD}")
    print()
    
    # Bước 1: Đăng nhập với admin account để lấy token
    print("Bước 1: Đăng nhập với admin account...")
    admin_username = input("Nhập admin username (hoặc Enter để dùng 'quangtruongngo2012004'): ").strip()
    if not admin_username:
        admin_username = "quangtruongngo2012004"
    
    admin_password = input("Nhập admin password (hoặc Enter để dùng 'quangtruong1'): ").strip()
    if not admin_password:
        admin_password = "quangtruong1"
    
    login_response = requests.post(
        f"{JAVA_API_URL}/auth/signIn",
        json={
            "userName": admin_username,
            "password": admin_password
        }
    )
    
    if login_response.status_code != 200:
        print(f"❌ Lỗi đăng nhập: {login_response.text}")
        exit(1)
    
    token = login_response.json().get("data", {}).get("token")
    if not token:
        print("❌ Không lấy được token")
        exit(1)
    
    print("✅ Đăng nhập thành công!")
    print()
    
    # Bước 2: Tìm user ID
    print(f"Bước 2: Tìm user ID cho username '{USERNAME}'...")
    user_id = get_user_id(USERNAME, token)
    
    if not user_id:
        print(f"❌ Không tìm thấy user với username: {USERNAME}")
        exit(1)
    
    print(f"✅ Tìm thấy user ID: {user_id}")
    print()
    
    # Bước 3: Reset password
    print(f"Bước 3: Reset password cho user ID {user_id}...")
    reset_response = reset_password(user_id, NEW_PASSWORD, token)
    
    if reset_response.status_code == 200:
        print("✅ Reset password thành công!")
        print(f"   Username: {USERNAME}")
        print(f"   Password mới: {NEW_PASSWORD}")
        print("   (Password đã được encode BCrypt trong database)")
    else:
        print(f"❌ Lỗi reset password: {reset_response.text}")
        exit(1)
    
    print()
    print("=" * 60)
    print("HOÀN TẤT!")
    print("=" * 60)

