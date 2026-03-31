tạo db_manager.py
tạo 2 file json
chỉnh sửa login.html
thêm home.html - styleHome.css
tạo fe.js -> trung tâm điều khiển frontend

tạo flaskapp.py là để xài framework flask (bị cấm trong btl) để làm app sau đó khi xong hết rồi thì chỉnh lại thôi




Hiểu:
1 Request.py
- prepare_headers(self, request): # chuyển header sang dict
- extract_request_line(self, request): # lấy method, path, version từ request ví dụ GET /index.html HTTP/1.1 -> method=GET, path=/index.html, version=HTTP/1.1
- prepare(self, request, routes=None): chuẩn bị mọi thứ của 1 request
-  def prepare_body(self, data, files, json=None): xử lý body
-  def prepare_content_length(self, body): tính chiều dài body
- prepare_auth(self, auth, url="") xử lý xác thực 
- prepare_cookies(self, cookies) xử lý cookie-> đang ở dạng string cần chuyển sang dict

2 Respone.py
- get_mime_type(self, path): xác định loại mime
- def prepare_content_type(self, mime_type='text/html'): xử lý loại content

3 httpadapter.py
- def handle_client(self, conn, addr, routes): đang xây dựng trả về kiểu statuscode: ... msg ,... còn bên app đang trả là sucess: true/flase , msg -> cần sửa lại
- hook = là mình cho hook = cái hàm sau đó nó trả về dữ liệu nếu 

4 proxy
- def forward_request(host, port, request): Đây là hàm "gửi thư". Nó nhận host và port của máy chủ đích
- def resolve_routing_policy(hostname, routes): 


5 app 
- response type :
{
    'status': code,
    'reason' : str,
    'header' : dict,
    'content' : json.dumps(data)
}

* Python dict ➔ (Bạn dùng json.dumps) ➔ JSON String ➔ (Browser gửi đi) ➔ JSON String ➔ (Bạn dùng response.json()) ➔ JavaScript Object

