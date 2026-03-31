import socket
import threading
import argparse
import time
import requests
import json
import sys

# --- Cấu hình ---
P2P_PORT = 9005
PEER_ID = f"Peer_{P2P_PORT}"
PROXY_URL = "http://10.230.155.99:9010"
MY_IP = "10.230.155.99"

# --- Hàng đợi tin nhắn (Để đồng bộ với Web Frontend - Như đã phân tích trước đó) ---
CHAT_HISTORY = []   
CHAT_HISTORY_LOCK = threading.Lock()
# -------------------------------------------------------------------

print('tui được tạo nè')

# --- Hàm HTTP Client (Giữ nguyên) ---
def register_with_tracker(peer_id, ip, port):
    url = f"{PROXY_URL}/submit_info"
    payload = {"peer_id": peer_id, "peer_ip": ip, "peer_port": port}
    try:
        response = requests.post(url, json=payload, headers={"Content-Type": "application/json"})
        if response.status_code == 201:
            print(f"[{peer_id}] Đăng ký P2P (port {port}) với Tracker thành công.")
        else:
            print(f"[{peer_id}] Đăng ký Tracker thất bại. Status: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print(f"[{peer_id}] LỖI: Không kết nối được Proxy/Tracker tại {PROXY_URL}.")

def get_peer_list_from_tracker(peer_id):
    url = f"{PROXY_URL}/get_peers"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            peers = response.json().get("peers", [])
            print(f"[{peer_id}] --- Danh sách Peer (từ Tracker) ---")
            # Lọc bỏ chính mình
            peers_list = [p for p in peers if p.get("peer_id") != peer_id]
            for p in peers_list:
                print(f"  -> {p.get('peer_id')}: {p.get('peer_ip')}:{p.get('peer_port')}")
            print("-------------------------------------")
            return peers_list
        else:
            print(f"[{peer_id}] Lấy danh bạ thất bại. Status: {response.status_code}")
            return []
    except requests.exceptions.ConnectionError:
        print(f"[{peer_id}] LỖI: Không kết nối được Proxy/Tracker tại {PROXY_URL}.")
        return []

# --- Hàm P2P Listener (Sửa để xử lý tin nhắn và lệnh API) ---
def handle_peer_connection(conn, addr):
    print(f"\n[P2P Listener] Nhận kết nối trực tiếp từ Peer: {addr}")
    try:
        data = conn.recv(4096).decode('utf-8')
        if not data:
            return
        
        # 1. Xử lý LỆNH API từ Backend (Relay)
        if data.strip().startswith('{"command":'):
            try:
                command = json.loads(data.strip())
                if command.get("command") == "GET_HISTORY": 
                    target_peer_id = command.get("peer_id") 
                    
                    filtered_history = []
                    for msg in CHAT_HISTORY:
                        is_sent = (msg.get('sender') == PEER_ID and msg.get('recipient') == target_peer_id)
                        is_received = (msg.get('sender') == target_peer_id and msg.get('recipient') == PEER_ID)
                        
                        if is_sent or is_received:
                            filtered_history.append(msg)
                            
                            # --- ĐÁNH DẤU ĐÃ ĐỌC ---
                            # Nếu tin nhắn này là tin NHẬN được (is_received) VÀ có status "NEW"
                            if is_received and msg.get('status') == "NEW":
                                msg['status'] = "READ" # Đánh dấu đã đọc
                    
                    # Sắp xếp lịch sử theo timestamp
                    history = sorted(filtered_history, key=lambda x: x.get('timestamp', 0))
                    
                    response_content = json.dumps({"success": True, "history": history})
                    
                    # *** KHÔNG XÓA DỮ LIỆU VÀ KHÔNG THAY ĐỔI CỜ STATUS ***
                    
                    response = f"HTTP/1.1 200 OK\r\nContent-Type: application/json\r\nContent-Length: {len(response_content)}\r\n\r\n{response_content}"
                    conn.sendall(response.encode('utf-8'))
                    return
                elif command.get("command") == "GET_UNREAD_STATUS":
                    unread_peers = set() # Dùng set để tránh trùng lặp
                    
                    # Duyệt qua lịch sử để tìm các tin nhắn "NEW"
                    for msg in CHAT_HISTORY:
                        # Chỉ kiểm tra tin nhắn NHẬN được (recipient là mình)
                        if msg.get('recipient') == PEER_ID and msg.get('status') == "NEW":
                            unread_peers.add(msg.get('sender')) # Thêm người GỬI vào danh sách
                            
                    response_content = json.dumps({
                        "success": True, 
                        "unread_peers": list(unread_peers) # Trả về danh sách các peer có tin mới
                    })
                elif command.get("command") == "SEND_MESSAGE":
                    target_ip = command.get("recipient_ip")
                    target_port = int(command.get("recipient_port"))
                    message = command.get("message")
                    recipient_id = command.get("recipient_id") # ID của người nhận
                    
                    # 1. Gửi tin nhắn đi (dùng hàm nội bộ)
                    # (Lưu ý: PEER_ID là ID của P2P Daemon này)
                    success = send_p2p_message(target_ip, target_port, message, PEER_ID)
                    
                    if success:
                        # 2. LƯU LẠI TIN ĐÃ GỬI (nếu gửi thành công)
                        with CHAT_HISTORY_LOCK:
                            CHAT_HISTORY.append({
                                "sender": PEER_ID, # Mình là người gửi
                                "recipient": recipient_id, # ID người nhận
                                "message": message,
                                "timestamp": time.time()
                            })
                        response_content = json.dumps({"success": True})
                    else:
                        response_content = json.dumps({"success": False, "message": "Failed to connect to peer"})
                
                elif command.get("command") == "BROADCAST":
                    message = command.get("message")
                    
                    if not message:
                        response_content = json.dumps({"success": False, "message": "Missing message for broadcast"})
                    else:
                        print(f"[P2P Listener] Nhận lệnh BROADCAST: {message}")
                        # Gọi hàm send_all (đã có)
                        # PEER_ID là ID của daemon này (đã có ở global)
                        send_all(message, PEER_ID) 
                        response_content = json.dumps({"success": True, "message": "Broadcast sent"})
                
                if response_content:  
                    response = f"HTTP/1.1 200 OK\r\nContent-Type: application/json\r\nContent-Length: {len(response_content)}\r\n\r\n{response_content}"
                    conn.sendall(response.encode('utf-8'))
                    return
                
                
            except json.JSONDecodeError:
                pass
        
        # 2. Xử lý TIN NHẮN CHAT
        if data.startswith("P2P_MESSAGE (From "):
            # Logic trích xuất tin nhắn chat (đã đơn giản hóa)
            parts = data.split(': ', 1)
            full_sender = parts[0].split(' (From ')[1].replace(')', '')
            message_content = parts[1]

            
            # --- LOGIC LƯU TRỮ MỚI ---
            current_timestamp = time.time()
            message_object = {
                "sender": full_sender, 
                "recipient": PEER_ID, # Mình là người nhận
                "message": message_content.strip(), 
                "status": "NEW", # Giữ lại cờ unread
                "timestamp": current_timestamp
            }
            CHAT_HISTORY.append(message_object)
            # ------------------------------------
            
            print(f"\n[P2P Receiver] <<< TIN NHẮN TRỰC TIẾP TỪ {full_sender}: {message_content.strip()}\nP2P> ", end="")
            
            # Gửi phản hồi ACK (xác nhận)
            response = "HTTP/1.1 200 OK\r\nContent-Length: 3\r\n\r\nACK"
            conn.sendall(response.encode('utf-8'))

    except Exception as e:
        print(f"[P2P Listener] Lỗi khi xử lý kết nối: {e}")
    finally:
        conn.close()

def run_p2p_listener(ip, port):
    # (Logic khởi động Socket Server giữ nguyên)
    listener_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        listener_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        listener_socket.bind((ip, port))
        listener_socket.listen(10)
        print(f"[P2P Listener] Đã khởi động! Lắng nghe P2P tại {ip}:{port}")
        while True:
            conn, addr = listener_socket.accept()
            peer_thread = threading.Thread(target=handle_peer_connection, args=(conn, addr), daemon=True)
            peer_thread.start()
    except socket.error as e:
        print(f"[P2P Listener] Lỗi Socket (Port {port} có thể đã được sử dụng): {e}")
    except KeyboardInterrupt:
        pass
    finally:
        listener_socket.close()

# --- Chức năng P2P Client (Tách biệt logic) ---

# 1. Hàm tạo kết nối Socket TCP (Tách biệt logic kết nối)
def connect_to_peer(target_ip, target_port):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client_socket.connect((target_ip, target_port))
        return client_socket
    except socket.error as e:
        print(f"[P2P Client] Lỗi kết nối đến {target_ip}:{target_port}: {e}")
        return None

# 2. Hàm Gửi Tin nhắn (Chỉ tập trung vào giao thức gửi)
def send_p2p_message(target_ip, target_port, message, sender_id,recipient_id=None):
    client_socket = connect_to_peer(target_ip, target_port)
    if not client_socket:
        return False
        
    try:
        print(f"[P2P Client] Đang gửi TRỰC TIẾP đến {target_ip}:{target_port}...")
        full_message = f"P2P_MESSAGE (From {sender_id}): {message}"
        client_socket.sendall(full_message.encode('utf-8'))
        
        response = client_socket.recv(1024).decode('utf-8')
        print(f"[P2P Client] Nhận phản hồi ACK từ Peer: {response.strip()}")
        
        
        return True

    except socket.error as e:
        print(f"[P2P Client] Lỗi giao tiếp Socket: {e}")
        return False
    finally:
        client_socket.close()


# 3. Hàm Gửi Toàn bộ (Sửa lỗi logic)
def send_all(message, sender_id):
    # Lấy danh bạ (dùng hàm đã có)
    peers = get_peer_list_from_tracker(sender_id) 
    
    if not peers:
        print("[P2P Client] Không tìm thấy Peer nào để broadcast.")
        return

    print(f"[{sender_id}] Broadcasting message to {len(peers)} peers...")
    
    for p in peers:
        
        send_p2p_message(
            p.get('peer_ip'), 
            int(p.get('peer_port')), 
            message, 
            sender_id,
            p.get('peer_id') # Thêm recipient_id
        )
        with CHAT_HISTORY_LOCK:
             CHAT_HISTORY.append({
                "sender": sender_id,      
                "recipient": p.get('peer_id'), # Lưu cho từng người
                "message": message,
                "timestamp": time.time()
            })
             
    print("Broadcast hoàn tất.")


if __name__ == "__main__":
    # (Logic CLI giữ nguyên)
    parser = argparse.ArgumentParser(
        prog='PeerProcess',
        description='Start the P2P chat process (Listener and Client)',
    )
    parser.add_argument('--peer-id', type=str, help='Unique ID for this peer.')
    parser.add_argument('--bind-ip', type=str, default='127.0.0.1', help='IP address to bind the P2P listener.')
    parser.add_argument('--bind-port', type=int, default=P2P_PORT, help=f'Port for the P2P listener. Default is {P2P_PORT}.')
 
    args = parser.parse_args()
    
    MY_IP = args.bind_ip
    MY_PORT = args.bind_port
    PEER_ID = args.peer_id if args.peer_id else f"Peer_{MY_PORT}"
    
    # 1. Khởi động P2P Listener (Chạy ngầm)
    listener_thread = threading.Thread(
        target=run_p2p_listener, 
        args=(MY_IP, MY_PORT),
        daemon=True
    )
    listener_thread.start()
    
    # 2. Đăng ký với Tracker (Pha 1)
    register_with_tracker(PEER_ID, MY_IP, MY_PORT)
    
    print(f"[{PEER_ID}] P2P Process Running. Type 'list' (lấy danh bạ), 'send <ip> <port> <message>', 'send_all <message>', hoặc 'quit'.")

    # 3. CLI (Giao diện chat P2P)
    while True:
        try:
            command = input("P2P> ").strip()
            
            if not command:
                continue

            parts = command.split(' ', 3)
            
            if parts[0].lower() == 'send' :
                if len(parts) != 4:
                    print("Cú pháp: send <ip> <port> <message>")
                    continue
                # Pha 2: Gửi P2P trực tiếp
                _, ip, port_str, message = parts
                try:
                    port = int(port_str)
                    send_p2p_message(ip, port, message, PEER_ID)
                except ValueError:
                    print("Lỗi: Port không hợp lệ.")
            
            elif parts[0].lower() == 'list':
                get_peer_list_from_tracker(PEER_ID)
                
            elif parts[0].lower() == 'send_all':
                if len(command.split(' ', 1)) < 2:
                    print("Cú pháp: send_all <message>")
                    continue
                # Trích xuất toàn bộ tin nhắn sau 'send_all'
                message = command.split(' ', 1)[1]
                send_all(message, PEER_ID)

            elif parts[0].lower() == 'quit':
                break
            else:
                print("Cú pháp: list | send <ip> <port> <message> | send_all <message> | quit")

        except EOFError:
            break
        except KeyboardInterrupt:
            break

    print(f"[{PEER_ID}] P2P Process Tắt.")