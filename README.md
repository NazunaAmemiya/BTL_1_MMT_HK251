# HTTP Server & Hybrid Chat Application
## Computer Network Assignment - HCMC University of Technology (HCMUT)

Dự án này tập trung vào việc triển khai các thành phần chính trong hệ thống mạng máy tính, bao gồm mô hình **Client-Server**, **Peer-to-Peer (P2P)** và lập trình **Socket TCP/IP** bằng ngôn ngữ Python.

---

## 📋 Mục tiêu dự án
*   **HTTP Server:** Xây dựng server hỗ trợ quản lý Session dựa trên Cookie.
*   **Hybrid Chat:** Kết hợp mô hình tập trung (Server-based) để đăng ký Peer và mô hình phân tán (P2P) để truyền tin nhắn trực tiếp.
*   **Protocol Design:** Thiết kế giao thức tùy chỉnh trên nền tảng TCP/IP.
*   **Architecture:** Triển khai cấu trúc Proxy Server điều hướng request đến các Backend và WebApp (WeApRous).

---

## 📂 Cấu trúc mã nguồn
```text
Hybrid Chat Application/
├── daemon/                 
│   ├── response.py         # Xử lý phản hồi HTTP
│   ├── request.py          # Xử lý yêu cầu HTTP
│   ├── backend.py          # Logic cho Backend process
│   ├── httpadapter.py      # Adapter điều phối request/response
│   ├── weaprous.py         # Framework hỗ trợ RESTful routing
│   └── dictionary.py       # CaseInsesitiveDict cho Headers
├── config/                 # Cấu hình Proxy
│   └── proxy.conf         
├── www/                    # Chứa các tệp HTML tĩnh (index.html)
├── static/                 # CSS, JS và Hình ảnh
├── db/                     # Chứa dữ liệu
├── apps/                   # Chứa API
├── start_proxy.py          
├── start_backend.py       
├── start_sampleapp.py
├── start_app.py
└── start_p2p.py
```
## Khởi chạy
```text
python start_backend.py --server-ip 127.0.0.1 --server-port 9000
python start_proxy.py --server-ip 0.0.0.0 --server-port 8080
python start_sampleapp.py --server-ip 127.0.0.1 --server-port 8000
