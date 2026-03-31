# app.py (Phiên bản đã sửa đổi và hoàn thiện)

import json
import socket
import argparse
import os
import subprocess

from db.db_manager import DBManager
db = DBManager()

# NOTE: Giả định file start_p2p.py đã được đổi tên thành start_peer.py (theo convention)
# và logic Socket Client đã được định nghĩa trong hàm send_p2p_message tại đó.

from daemon.weaprous import WeApRous
#PORT = 9001  # Port mặc định cho WebApp

# --- Hàm hỗ trợ ---

def get_cookie_value(headers_dict, cookie_name):
    # ... (Logic get_cookie_value giữ nguyên) ...
    cookie_string = headers_dict.get("cookie", "")
    if not cookie_string:
        return None
    cookies = cookie_string.split(';')
    for cookie in cookies:
        cookie_pair = cookie.strip()
        if "=" in cookie_pair:
            key, value = cookie_pair.split('=', 1)
            if key.strip() == cookie_name:
                return value.strip() 
    return None

def read_file_content(relative_path):
    # ... (Logic read_file_content giữ nguyên) ...
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.abspath(os.path.join(base_dir, '..'))
        filepath = os.path.join(parent_dir, relative_path)
        if not os.path.exists(filepath):
             raise FileNotFoundError(f"File not found: {filepath}")
        with open(filepath, 'rb') as f:
            return f.read()
    except Exception as e:
        print(f"[App] Lỗi khi đọc file: {e}")
        return None

def send_p2p_command_to_peer(target_ip, target_port, command_json_string):
    """Gửi một lệnh JSON (ví dụ: GET_MESSAGES, GET_HISTORY) qua Socket đến Peer Process."""
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((target_ip, target_port))
        
        client_socket.sendall(command_json_string.encode('utf-8'))
        
        response_bytes = client_socket.recv(4096)
        
        # Phân tích phản hồi HTTP để trích xuất body JSON
        header_body_split = response_bytes.decode('utf-8').split('\r\n\r\n', 1)
        if len(header_body_split) == 2:
            json_body = header_body_split[1]
            return json.loads(json_body)
        
        return {"success": False, "message": "Invalid response from peer"}

    except Exception as e:
        print(f"[Tracker] Error sending command to peer {target_ip}:{target_port}: {e}")
        return {"success": False, "message": f"Connection error: {e}"}
    finally:
        if 'client_socket' in locals():
            client_socket.close()


def create_sampleapp():

    app = WeApRous()
    
    # --- ROUTES CƠ BẢN ---
    @app.route("/", methods=["GET"])
    def home(headers, body):
        return { 'status': 302, 'reason': 'Found', 'headers': {'Location': '/loginUI.html'} }
    
    @app.route('/login', methods=['POST'])
    def login(headers, body):
        try:
            data  = json.loads(body)
            username = data.get("username")
            password = data.get("password")
            user = db.get_user(username)
            
            if user and user['password'] == password:
                print('tao peer')
                
                # SỬA LOGIC CẤP CỔNG: Dùng hash để tránh lỗi khi người dùng không login theo thứ tự
                BASE_PORT = 9003
                # Tính toán cổng ngẫu nhiên dựa trên username (Tối đa 1000 cổng)
                port = BASE_PORT + len(db.get_list_peer())
                
                # Giả định start_p2p.py nằm ở thư mục cha
                peer_script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'start_p2p.py')
                
                # Khởi động Peer Process
                subprocess.Popen([
                    "python",
                    peer_script_path,
                    "--peer-id", username,
                    "--bind-port", str(port)
                ])
                print('đã mở')
                return {
                    "status": 200, "reason": "OK",
                    "content": json.dumps({"success": True, "message": "Login successful"}),
                    "headers": { "Content-Type": "application/json", "Set-Cookie": "auth=true; Path=/", }
                }
            else:
                return {'status': 401, 'reason': 'Unauthorized', 'content': json.dumps({'success':False , 'message': "Login failed"}), 'headers': {'Content-Type': 'application/json'}}
        except json.JSONDecodeError:
             return {'status': 400, 'reason': 'Bad Request', 'content': json.dumps({'success':False , 'message': "Invalid JSON"})}
    
    
    
    @app.route('/register', methods=['POST'])
    def register(headers,body):
        # ... (Logic register giữ nguyên)
        try:
            data = json.loads(body)
            username = data.get("username")
            password = data.get('password')
            
            existing_user = db.get_user(username)
            if existing_user:
                return {'status': 409, 'reason': 'Conflict', 'content': json.dumps({'success':False , 'message': "Username already exists"}), 'headers': {'Content-Type': 'application/json'}}
            db.add_usser(username,password)
            return {'status': 201, 'reason': 'Created', 'content': json.dumps({'success':True , 'message': "Registration successful"}), 'headers': {'Content-Type': 'application/json'}}
        except json.JSONDecodeError:
             return {'status': 400, 'reason': 'Bad Request', 'content': json.dumps({'success':False , 'message': "Invalid JSON"})}

    
    @app.route('/submit_info', methods=['POST'])
    def submit_info(headers, body):
        # ... (Logic submit_info giữ nguyên, bỏ kiểm tra cookie)
        
        try:
            print('vo')
            data = json.loads(body)
            peer_id = data.get("peer_id")
            peer_ip = data.get("peer_ip")
            peer_port = data.get("peer_port")
            print('submit peer ',peer_id,peer_ip,peer_port)
            if not all([peer_id, peer_ip, peer_port]):
                return { 'status': 400, 'reason': 'Bad Request', 'content': json.dumps({"success": False, "message": "Missing peer_info"}), 'headers': {'Content-Type': 'application/json'} }
            
            p = db.get_peer(peer_id)
            if p:
                # Nếu đã tồn tại, cập nhật cổng
                # Giả định db_manager có hàm update_peer
                # Nếu không, lỗi 409 sẽ xảy ra
                pass 
            db.add_peer(peer_id, peer_ip, peer_port)
            return { 'status': 201, 'reason': 'Created', 'content': json.dumps({"success": True, "message": f"Peer {peer_id} registered"}), 'headers': {'Content-Type': 'application/json'} }
        except json.JSONDecodeError:
            return { 'status': 400, 'reason': 'Bad Request', 'content': json.dumps({"success": False, "message": "Invalid JSON format"}), 'headers': {'Content-Type': 'application/json'} }
        except Exception as e:
            print(f"[submit_info] Lỗi không xác định: {e}")
            return {
                'status': 500,
                'reason': 'Internal Server Error',
                'content': json.dumps({
                    "success": False,
                    "message": f"Lỗi server: {str(e)}"
                }),
                'headers': {'Content-Type': 'application/json'}
            }
            
    
    @app.route('/get_peers', methods=['GET'])
    def get_peers(headers, body):
        
        try:
            peers = db.get_list_peer()
            print(peers)
            return { 'status': 200, 'reason': 'OK', 'content': json.dumps({"success": True, "peers": peers}), 'headers': {'Content-Type': 'application/json'} }
        except Exception as e:
            return { 'status': 500, 'reason': 'Internal Server Error', 'content': json.dumps({"success": False, "message": "Internal server error"}), 'headers': {'Content-Type': 'application/json'} }
            
    
    
    # --- API MỚI: LOGOUT ---
    @app.route('/logout', methods=['POST'])
    def logout(headers, body):
        try:
            data = json.loads(body)
            username = data.get('username')

            if username:
                db.delete_peer(username) # Xóa Peer khỏi danh sách Online
            
            set_cookie_header = "auth=; Path=/; Max-Age=0" 
            
            return { 
                'status': 200, 
                'reason': 'OK', 
                'content': json.dumps({"success": True}), 
                'headers': {
                    'Content-Type': 'application/json',
                    'Set-Cookie': set_cookie_header
                } 
            }
        except Exception as e:
            return { 'status': 500, 'reason': 'Internal Server Error', 'content': json.dumps({"success": False, "message": f"Internal server error: {e}"}), 'headers': {'Content-Type': 'application/json'} }


    # --- API MỚI: P2P RELAY (Gửi tin nhắn) ---
    @app.route('/send_direct_message', methods=['POST'])
    def send_direct_message(headers, body):
        try:
            data = json.loads(body)
            sender_id = data.get("sender_id")
            recipient_ip = data.get("recipient_ip")
            recipient_port = data.get("recipient_port")
            message = data.get("message")

            recipient_id = data.get("recipient_id") # Lấy ID người nhận
            
            if not all([sender_id, recipient_ip, recipient_port, message, recipient_id]):
                return { 'status': 400, 'reason': 'Bad Request', 'content': json.dumps({"success": False, "message": "Missing parameters"}), 'headers': {'Content-Type': 'application/json'} }
            
            # 1. Lấy thông tin P2P Daemon CỦA MÌNH (NGƯỜI GỬI)
            my_peer_info = db.get_peer(sender_id)
            if not my_peer_info:
                 return { 'status': 404, 'reason': 'Not Found', 'content': json.dumps({"success": False, "message": "Sender Peer not found"}), 'headers': {'Content-Type': 'application/json'} }

            # 2. Tạo lệnh SEND_MESSAGE mới
            command = json.dumps({
                "command": "SEND_MESSAGE",
                "recipient_id": recipient_id,
                "recipient_ip": recipient_ip,
                "recipient_port": recipient_port,
                "message": message
            })
            
            # 3. Gửi lệnh đến P2P Daemon CỦA MÌNH
            # (send_p2p_command_to_peer sẽ kết nối đến 127.0.0.1:port của mình)
            peer_response = send_p2p_command_to_peer(
                my_peer_info['peer_ip'], 
                my_peer_info['peer_port'], 
                command
            )
            
            # peer_response là kết quả {"success": true}
            if peer_response.get("success"):
                 return { 'status': 200, 'reason': 'OK', 'content': json.dumps({"success": True}), 'headers': {'Content-Type': 'application/json'} }
            else:
                 # Trả về lỗi nếu P2P Daemon gửi không thành công
                 error_msg = peer_response.get("message", "Failed to send message via P2P daemon")
                 return { 'status': 500, 'reason': 'Internal Server Error', 'content': json.dumps({"success": False, "message": error_msg}), 'headers': {'Content-Type': 'application/json'} }
        except json.JSONDecodeError:
            return { 'status': 400, 'reason': 'Bad Request', 'content': json.dumps({"success": False, "message": "Invalid JSON format"}), 'headers': {'Content-Type': 'application/json'} }
        except Exception as e:
            print(f"[send_direct_message] Lỗi không xác định: {e}")
            return { 'status': 500, 'reason': 'Internal Server Error', 'content': json.dumps({"success": False, "message": f"Server Error: {str(e)}"}), 'headers': {'Content-Type': 'application/json'} }
            
    # --- API MỚI: POLLING TRẠNG THÁI CHƯA ĐỌC (NOTIFICATION) ---
    @app.route('/poll_unread_status', methods=['POST'])
    def poll_unread_status(headers, body):
        try:
            request_data = json.loads(body)
            polling_peer_id = request_data.get('user_id') 
            print
            auth_status = get_cookie_value(headers, "auth")
            if auth_status != "true":
                 return { 'status': 401, 'reason': 'Unauthorized', 'content': json.dumps({"success": False, "message": "Unauthorized"}), 'headers': {'Content-Type': 'application/json'} }
            
            peer_info = db.get_peer(polling_peer_id)
            if not peer_info:
                 return { 'status': 404, 'reason': 'Not Found', 'content': json.dumps({"success": False, "message": "Peer not found"}), 'headers': {'Content-Type': 'application/json'} }

            # Gửi lệnh GET_UNREAD_STATUS đến Peer Process Y (qua Socket)
            command = json.dumps({"command": "GET_UNREAD_STATUS"})
            peer_response = send_p2p_command_to_peer(peer_info['peer_ip'], peer_info['peer_port'], command)

            return { 
                'status': 200, 
                'reason': 'OK', 
                'content': json.dumps(peer_response),
                'headers': {'Content-Type': 'application/json'} 
            }

        except Exception as e:
            return { 'status': 500, 'reason': 'Internal Server Error', 'content': json.dumps({"success": False, "message": f"Internal server error: {e}"}), 'headers': {'Content-Type': 'application/json'} }
            
    # --- API MỚI: TẢI LỊCH SỬ CHAT ---
    @app.route('/get_chat_history', methods=['POST'])
    def get_chat_history(headers, body):
        try:
            request_data = json.loads(body)
            polling_peer_id = request_data.get('user_id') 
            target_peer_id = request_data.get('target_peer_id')

            auth_status = get_cookie_value(headers, "auth")
            if auth_status != "true":
                 return { 'status': 401, 'reason': 'Unauthorized', 'content': json.dumps({"success": False, "message": "Unauthorized"}), 'headers': {'Content-Type': 'application/json'} }
            
            peer_info = db.get_peer(polling_peer_id)
            if not peer_info:
                 return { 'status': 404, 'reason': 'Not Found', 'content': json.dumps({"success": False, "message": "Peer not found"}), 'headers': {'Content-Type': 'application/json'} }

            # Gửi lệnh GET_HISTORY đến Peer Process Y (qua Socket)
            command = json.dumps({
                "command": "GET_HISTORY", 
                "peer_id": target_peer_id 
            })
            peer_response = send_p2p_command_to_peer(peer_info['peer_ip'], peer_info['peer_port'], command)

            return { 
                'status': 200, 
                'reason': 'OK', 
                'content': json.dumps(peer_response),
                'headers': {'Content-Type': 'application/json'} 
            }

        except Exception as e:
            return { 'status': 500, 'reason': 'Internal Server Error', 'content': json.dumps({"success": False, "message": f"Internal server error: {e}"}), 'headers': {'Content-Type': 'application/json'} }
        
        
        
        
        
    @app.route('/broadcast_message', methods=['POST'])
    def broadcast_message(headers, body):
        try:
            data = json.loads(body)
            sender_id = data.get("sender_id")
            message = data.get("message")

            if not all([sender_id, message]):
                return { 'status': 400, 'reason': 'Bad Request', 'content': json.dumps({"success": False, "message": "Missing sender_id or message"}), 'headers': {'Content-Type': 'application/json'} }

            # 1. Lấy thông tin P2P Daemon CỦA MÌNH (NGƯỜI GỬI)
            my_peer_info = db.get_peer(sender_id)
            if not my_peer_info:
                 return { 'status': 404, 'reason': 'Not Found', 'content': json.dumps({"success": False, "message": "Sender Peer not found"}), 'headers': {'Content-Type': 'application/json'} }

            # 2. Tạo lệnh BROADCAST mới
            command = json.dumps({
                "command": "BROADCAST", # Dùng lệnh mới
                "message": message
            })
            
            # 3. Gửi lệnh đến P2P Daemon CỦA MÌNH
            peer_response = send_p2p_command_to_peer(
                my_peer_info['peer_ip'], 
                my_peer_info['peer_port'], 
                command
            )
            
            # 4. Trả về kết quả từ P2P Daemon
            return { 
                'status': 200, 
                'reason': 'OK', 
                'content': json.dumps(peer_response),
                'headers': {'Content-Type': 'application/json'} 
            }

        except Exception as e:
            print(f"[broadcast_message] Lỗi không xác định: {e}")
            return { 'status': 500, 'reason': 'Internal Server Error', 'content': json.dumps({"success": False, "message": f"Server Error: {str(e)}"}), 'headers': {'Content-Type': 'application/json'} }
        
        
    return app