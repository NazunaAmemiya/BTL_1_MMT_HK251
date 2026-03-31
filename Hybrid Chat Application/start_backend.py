#
# Copyright (C) 2025 pdnguyen of HCMC University of Technology VNU-HCM.
# All rights reserved.
# This file is part of the CO3093/CO3094 course,
# and is released under the "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.
#
# WeApRous release
#
# The authors hereby grant to Licensee personal permission to use
# and modify the Licensed Source Code for the sole purpose of studying
# while attending the course
#


"""
start_backend
~~~~~~~~~~~~~~~~~

This module provides a simple entry point for deploying backend server process
using the socket framework. It parses command-line arguments to configure the
server's IP address and port, and then launches the backend server.
"""

import socket
import argparse
import json
import os
# (Bạn cần đảm bảo đã import thư viện 'os' ở đầu file)



from daemon import create_backend
from db.db_manager import DBManager
# Default port number used if none is specified via command-line arguments.
PORT = 9000 
db = DBManager()




def read_file_content(relative_path):
    """
    Đọc nội dung file từ đường dẫn tương đối (ví dụ: 'www/mainUI.html').
    
    :param relative_path (str): Đường dẫn tương đối đến file.
    :rtype str: Nội dung file dưới dạng chuỗi, hoặc None nếu có lỗi.
    """
    try:
        # 1. Xác định thư mục gốc (Base Directory)
        # Lấy đường dẫn tuyệt đối đến thư mục chứa start_backend.py
        base_dir = os.path.dirname(os.path.abspath(__file__))
        
        # 2. Xây dựng đường dẫn tuyệt đối (Join Path)
        # Nối thư mục gốc với đường dẫn tương đối (ví dụ: 'D:/CO3094/www/mainUI.html')
        filepath = os.path.join(base_dir, relative_path)
        
        # 3. Mở và đọc nội dung file (r - read, encoding='utf-8')
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
            
    except FileNotFoundError:
        # Báo lỗi nếu không tìm thấy file
        print(f"[Backend] LỖI: Không tìm thấy file tại {filepath}")
        return None
    except Exception as e:
        # Báo lỗi khác (quyền truy cập, v.v.)
        print(f"[Backend] LỖI khi đọc file: {e}")
        return None






def register_handler(headers, body):
    # ... logic của bạn ...
    print("Register endpoint called")
    data = json.loads(body)
    username = data.get("username")
    password = data.get('password')
    
    existing_user = db.get_user(username)
    if existing_user:
        return {
            "status": 401,
            "reason": "Not Authorized",
            "headers": {"Content-Type": "application/json" },
            "content": json.dumps({"msg": "Username already exists"})
        }
    db.add_usser(username,password)
    return {
        "status": 200,
        "reason": "OK",
        "headers": {"Content-Type": "application/json" },
        "content": json.dumps({"msg": "Registration successful"})
    }

def login_handler(headers, body):
    # ... logic của bạn ...
    print(body)
    data  = body
    
    username = data.get("username")
    password = data.get("password")
    user = db.get_user(username)
    print("voo")
    print(username)
    print(password)
    print()
    if user and user['password'] == password:
        # === ĐĂNG NHẬP THÀNH CÔNG: SỬA Ở ĐÂY ===
        return {
            "status": 200,
            "reason": "OK",
            "headers": {"Content-Type": "application/json",'Set-Cookie': 'auth=true; Path=/'  },
            "content": json.dumps({"msg": "Login success"})
        }       
    return {'status':401 , 'content': "Login failed"}

def get_cookie_value(headers, cookie_name):
    cookies = headers.get("Cookie", "")
    cookie_pairs = cookies.split('; ')
    for pair in cookie_pairs:
        if '=' in pair:
            key, value = pair.split('=', 1)
            if key.strip() == cookie_name:
                return value.strip()
    return None
"""
def mainUI_handler(headers, body):
    print("MainUI endpoint called")
    content = read_file_content('www/mainUI.html')
    if content:
        return {
            "status": 200,
            "reason": "OK",
            "headers": {"Content-Type": "text/html" },
            "content": content
        }
    else:
        return {
            "status": 404,
            "reason": "Not Found",
            "headers": {"Content-Type": "text/plain" },
            "content": "404 Not Found"
        }
"""

if __name__ == "__main__":
    """
    Entry point for launching the backend server.

    This block parses command-line arguments to determine the server's IP address
    and port. It then calls `create_backend(ip, port)` to start the RESTful
    application server.

    :arg --server-ip (str): IP address to bind the server (default: 127.0.0.1).
    :arg --server-port (int): Port number to bind the server (default: 9000).
    """

    parser = argparse.ArgumentParser(
        prog='Backend',
        description='Start the backend process',
        epilog='Backend daemon for http_deamon application'
    )
    parser.add_argument('--server-ip',
        type=str,
        default='0.0.0.0',
        help='IP address to bind the server. Default is 0.0.0.0'
    )
    parser.add_argument(
        '--server-port',
        type=int,
        default=PORT,
        help='Port number to bind the server. Default is {}.'.format(PORT)
    )
 
    args = parser.parse_args()
    ip = args.server_ip
    port = args.server_port
    
    routes = {

    }

    create_backend(ip, port,routes)
