# #
# # Copyright (C) 2025 pdnguyen of HCMC University of Technology VNU-HCM.
# # All rights reserved.
# # This file is part of the CO3093/CO3094 course.
# #
# # WeApRous release
# #
# # The authors hereby grant to Licensee personal permission to use
# # and modify the Licensed Source Code for the sole purpose of studying
# # while attending the course
# #

# """
# daemon.response
# ~~~~~~~~~~~~~~~~~

# This module provides a :class: `Response <Response>` object to manage and persist 
# response settings (cookies, auth, proxies), and to construct HTTP responses
# based on incoming requests. 

# The current version supports MIME type detection, content loading and header formatting
# """
# import datetime
# import os
# import mimetypes
# import json
# from .dictionary import CaseInsensitiveDict

# BASE_DIR = ""

# class Response():   
#     """The :class:`Response <Response>` object, which contains a
#     server's response to an HTTP request.

#     Instances are generated from a :class:`Request <Request>` object, and
#     should not be instantiated manually; doing so may produce undesirable
#     effects.

#     :class:`Response <Response>` object encapsulates headers, content, 
#     status code, cookies, and metadata related to the request-response cycle.
#     It is used to construct and serve HTTP responses in a custom web server.

#     :attrs status_code (int): HTTP status code (e.g., 200, 404).
#     :attrs headers (dict): dictionary of response headers.
#     :attrs url (str): url of the response.
#     :attrsencoding (str): encoding used for decoding response content.
#     :attrs history (list): list of previous Response objects (for redirects).
#     :attrs reason (str): textual reason for the status code (e.g., "OK", "Not Found").
#     :attrs cookies (CaseInsensitiveDict): response cookies.
#     :attrs elapsed (datetime.timedelta): time taken to complete the request.
#     :attrs request (PreparedRequest): the original request object.

#     Usage::

#       >>> import Response
#       >>> resp = Response()
#       >>> resp.build_response(req)
#       >>> resp
#       <Response>
#     """

#     __attrs__ = [
#         "_content",
#         "_header",
#         "status_code",
#         "method",
#         "headers",
#         "url",
#         "history",
#         "encoding",
#         "reason",
#         "cookies",
#         "elapsed",
#         "request",
#         "body",
#         "reason",
#     ]


#     def __init__(self, request=None):
#         """
#         Initializes a new :class:`Response <Response>` object.

#         : params request : The originating request object.
#         """
#         self.raw = None # Raw socket response
#         self._content = b""
#         self._content_consumed = False
#         self._next = None
#         self.connection = None
#         #: Integer Code of responded HTTP Status, e.g. 404 or 200.
#         self.status_code = None
        
#         self.hook_result = None

#         #: Case-insensitive Dictionary of Response Headers.
#         #: For example, ``headers['content-type']`` will return the
#         #: value of a ``'Content-Type'`` response header.
#         self.headers = {}

#         #: URL location of Response.
#         self.url = None

#         #: Encoding to decode with when accessing response text.
#         self.encoding = None

#         #: A list of :class:`Response <Response>` objects from
#         #: the history of the Request.
#         self.history = []

#         #: Textual reason of responded HTTP Status, e.g. "Not Found" or "OK".
#         self.reason = None

#         #: A of Cookies the response headers.
#         self.cookies = CaseInsensitiveDict()

#         #: The amount of time elapsed between sending the request
#         self.elapsed = datetime.timedelta(0)

#         #: The :class:`PreparedRequest <PreparedRequest>` object to which this
#         #: is a response.
#         self.request = None


#     def get_mime_type(self, path):
#         """
#         Determines the MIME type of a file based on its path.

#         "params path (str): Path to the file.

#         :rtype str: MIME type string (e.g., 'text/html', 'image/png').
#         """

#         try:
#             mime_type, _ = mimetypes.guess_type(path)
#         except Exception:
#             return 'application/octet-stream'
#         return mime_type or 'application/octet-stream'


#     def prepare_content_type(self, mime_type='text/html'):
#         """
#         Prepares the Content-Type header and determines the base directory
#         for serving the file based on its MIME type.

#         :params mime_type (str): MIME type of the requested resource.

#         :rtype str: Base directory path for locating the resource.

#         :raises ValueError: If the MIME type is unsupported.
#         """
        
#         base_dir = ""

#         # Processing mime_type based on main_type and sub_type
#         main_type, sub_type = mime_type.split('/', 1)
#         print("[Response] processing MIME main_type={} sub_type={}".format(main_type,sub_type))
#         if main_type == 'text':
#             self.headers['Content-Type']='text/{}'.format(sub_type)
#             if sub_type == 'plain' or sub_type == 'css':
#                 base_dir = BASE_DIR+"static/"
#             elif sub_type == 'html':
#                 base_dir = BASE_DIR+"www/"
#             elif sub_type == 'javascript':
#                 base_dir = BASE_DIR+"static/"
#             else:
#                 #handle_text_other(sub_type)
#                 raise ValueError("Unsupported text subtype: {}".format(sub_type))
#         elif main_type == 'image':
#             base_dir = BASE_DIR+"static/"
#             self.headers['Content-Type']='image/{}'.format(sub_type)
#             if sub_type =="x-icon":
#                 base_dir = BASE_DIR+"static/image/"
#                 self.headers['Content-Type']='image/{}'.format(sub_type)
#         elif main_type == 'application':
#             if sub_type == 'javascript':
#                 base_dir = BASE_DIR+"static/"
#                 self.headers['Content-Type']='application/javascript'
#             # === KẾT THÚC SỬA ĐỔI ===
#             else:
#                 base_dir = BASE_DIR+"apps/"
#                 self.headers['Content-Type']='application/{}'.format(sub_type)
#         #
#         #  TODO: process other mime_type
#         #        application/xml       
#         #        application/zip
#         #        ...
#         #        text/csv
#         #        text/xml
#         #        ...
#         #        video/mp4 
#         #        video/mpeg
#         #        ...
#         #
#         else:
#             raise ValueError("Invalid MEME type: main_type={} sub_type={}".format(main_type,sub_type))

#         return base_dir


#     def build_content(self, path, base_dir):
#         """
#         Loads the objects file from storage space.

#         :params path (str): relative path to the file.
#         :params base_dir (str): base directory where the file is located.

#         :rtype tuple: (int, bytes) representing content length and content data.
#         """

#         filepath = os.path.join(base_dir, path.lstrip('/'))

#         print("[Response] serving the object at location {}".format(filepath))
#             #
#             #  TODO: implement the step of fetch the object file
#             #        store in the return value of content
#             #
#         with open (filepath, 'rb') as f:
#             content = f.read()
#         return len(content), content


#     def build_response_header(self, request):
#         """
#         Constructs the HTTP response headers based on the class:`Request <Request>
#         and internal attributes.

#         :params request (class:`Request <Request>`): incoming request object.

#         :rtypes bytes: encoded HTTP response header.
#         """
#         reqhdr = request.headers
#         rsphdr = self.headers
#         #Build dynamic headers
#         headers = {
#                 "Accept": "{}".format(reqhdr.get("Accept", "application/json")),
#                 "Accept-Language": "{}".format(reqhdr.get("Accept-Language", "en-US,en;q=0.9")),
#                 "Authorization": "{}".format(reqhdr.get("Authorization", "Basic <credentials>")),
#                 "Cache-Control": "no-cache",
#                 "Content-Type": "{}".format(self.headers['Content-Type']),
#                 "Content-Length": "{}".format(len(self._content)),
# #                "Cookie": "{}".format(reqhdr.get("Cookie", "sessionid=xyz789")), #dummy cooki
#         #
#         # TODO prepare the request authentication
#         #
# 	# self.auth = ...
#                 "Date": "{}".format(datetime.datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S GMT")),
#                 "Max-Forward": "10",
#                 "Pragma": "no-cache",
#                 "Proxy-Authorization": "Basic dXNlcjpwYXNz",  # example base64
#                 "Warning": "199 Miscellaneous warning",
#                 "User-Agent": "{}".format(reqhdr.get("User-Agent", "Chrome/123.0.0.0")),
#             }

#         # Header text alignment
#             #
#             #  TODO: implement the header building to create formated
#             #        header from the provied headers
#             #
#         #
#         # TODO prepare the request authentication
#         #
# 	# self.auth = ...
#         fmt_header = ""
#         for key, value in headers.items():
#             fmt_header += f"{key}: {value}\r\n"
    
#         # Thêm dòng trống để kết thúc header
#         fmt_header += "\r\n"
#         return str(fmt_header).encode('utf-8')


#     def build_notfound(self):
#         """
#         Constructs a standard 404 Not Found HTTP response.

#         :rtype bytes: Encoded 404 response.
#         """

#         return (
#                 "HTTP/1.1 404 Not Found\r\n"
#                 "Accept-Ranges: bytes\r\n"
#                 "Content-Type: text/html\r\n"
#                 "Content-Length: 13\r\n"
#                 "Cache-Control: max-age=86000\r\n"
#                 "Connection: close\r\n"
#                 "\r\n"
#                 "404 Not Found"
#             ).encode('utf-8')


#     def _build_api_response(self, response_data):
#         """
#         Xây dựng phản hồi HTTP bytes từ dict của WeApRous (hook_result).
#         (Đây là logic được chuyển từ httpadapter.py sang)
#         """
#         try:
#             status = response_data.get('status', 200)
#             reason = response_data.get('reason', 'OK')
            
#             # Kiểm tra xem content trả về là bytes (từ file) hay string (từ API JSON)
#             if 'content_bytes' in response_data:
#                 content_bytes = response_data.get('content_bytes')
#             else:
#                 content_str = response_data.get('content', '')
#                 content_bytes = content_str.encode('utf-8')

#             headers_dict = response_data.get('headers', {})
            
#             status_line = f"HTTP/1.1 {status} {reason}\r\n"
#             header_lines = f"Content-Length: {len(content_bytes)}\r\n"
            
#             # Thêm các header tùy chỉnh (Vd: Set-Cookie, Content-Type)
#             for key, val in headers_dict.items():
#                 header_lines += f"{key}: {val}\r\n"
            
#             # Nối tất cả lại
#             response = (
#                 status_line.encode('utf-8') +
#                 header_lines.encode('utf-8') +
#                 b"\r\n" +  # Dòng trống
#                 content_bytes # Body
#             )
#             print('Xây resp thành công',response)
#             return response
        
#         except Exception as e:
#             # Nếu "bảng hướng dẫn" (dict) bị lỗi
#             print(f"[Response] Lỗi khi xây dựng API response: {e}")
#             # Trả về lỗi 500 JSON
#             error_content = json.dumps({"success": False, "message": "Internal Server Error"}).encode('utf-8')
#             return (
#                 b"HTTP/1.1 500 Internal Server Error\r\n" +
#                 b"Content-Type: application/json\r\n" +
#                 f"Content-Length: {len(error_content)}\r\n\r\n".encode('utf-8') +
#                 error_content
#             )




#     def build_response(self, request):
#         """
#         Builds a full HTTP response including headers and content based on the request.

#         :params request (class:`Request <Request>`): incoming request object.

#         :rtype bytes: complete HTTP response using prepared headers and content.
#         """

#         if self.hook_result:
#             # 1. Đây là API (WeApRous) hoặc File Tĩnh do WeApRous phục vụ
#             print(f"[Response] Xây dựng phản hồi API cho: {request.path}")
#             return self._build_api_response(self.hook_result)
#         else:
#             # 2. Đây là File Tĩnh (Fallback - Logic cũ của server 9000)
#             print(f"[Response] Xây dựng phản hồi file tĩnh cho: {request.path}")
#             path = request.path

#             mime_type = self.get_mime_type(path)
#             print("[Response] {} path {} mime_type {}".format(request.method, request.path, mime_type))

#             base_dir = ""

#             try:
#                 # 1. Xác định base_dir và Content-Type
#                 base_dir = self.prepare_content_type(mime_type)
#             except ValueError as e:
#                 print(f"[Response] Lỗi MIME type: {e}. Trả về 404.")
#                 return self.build_notfound()
            
#             # 2. Tải nội dung
#             c_len, self._content = self.build_content(path, base_dir)
            
#             # 3. Kiểm tra File Not Found (logic trong build_content đã set self.status_code = 404)
#             if self.status_code == 404:
#                 return self.build_notfound()

#             # 4. Xây dựng Header
#             self._header = self.build_response_header(request)
            
#             # 5. Xây dựng Status Line (Mặc định là 200 OK)
#             status_line = b"HTTP/1.1 200 OK\r\n" 
            
#             # NOTE: Giữ nguyên logic status_line mặc định là 200 OK vì các lỗi 404/401/500
#             #       đã được xử lý bởi handler (App hook) hoặc build_notfound.
#             #       Tuy nhiên, nếu bạn muốn dùng status_code, bạn phải điều chỉnh
#             #       dòng trên thành: f"HTTP/1.1 {self.status_code or 200} {self.reason or 'OK'}\r\n".encode('utf-8')
            
#             return status_line + self._header + self._content
 
        
        
        
    
#
# Copyright (C) 2025 pdnguyen of HCMC University of Technology VNU-HCM.
# All rights reserved.
# This file is part of the CO3093/CO3094 course.
#
# WeApRous release
#
# The authors hereby grant to Licensee personal permission to use
# and modify the Licensed Source Code for the sole purpose of studying
# while attending the course
#

"""
daemon.response
~~~~~~~~~~~~~~~~~

This module provides a :class: `Response <Response>` object to manage and persist 
response settings (cookies, auth, proxies), and to construct HTTP responses
based on incoming requests. 

The current version supports MIME type detection, content loading and header formatting
"""
import datetime
import os
import mimetypes
from .dictionary import CaseInsensitiveDict

# Set BASE_DIR to the project root (parent directory of daemon/)
BASE_DIR = ""

class Response():   
    """The :class:`Response <Response>` object, which contains a
    server's response to an HTTP request.

    Instances are generated from a :class:`Request <Request>` object, and
    should not be instantiated manually; doing so may produce undesirable
    effects.

    :class:`Response <Response>` object encapsulates headers, content, 
    status code, cookies, and metadata related to the request-response cycle.
    It is used to construct and serve HTTP responses in a custom web server.

    :attrs status_code (int): HTTP status code (e.g., 200, 404).
    :attrs headers (dict): dictionary of response headers.
    :attrs url (str): url of the response.
    :attrsencoding (str): encoding used for decoding response content.
    :attrs history (list): list of previous Response objects (for redirects).
    :attrs reason (str): textual reason for the status code (e.g., "OK", "Not Found").
    :attrs cookies (CaseInsensitiveDict): response cookies.
    :attrs elapsed (datetime.timedelta): time taken to complete the request.
    :attrs request (PreparedRequest): the original request object.

    Usage::

      >>> import Response
      >>> resp = Response()
      >>> resp.build_response(req)
      >>> resp
      <Response>
    """

    __attrs__ = [
        "_content",
        "_header",
        "status_code",
        "method",
        "headers",
        "url",
        "history",
        "encoding",
        "reason",
        "cookies",
        "elapsed",
        "request",
        "body",
        "reason",
    ]


    def __init__(self, request=None):
        """
        Initializes a new :class:`Response <Response>` object.

        : params request : The originating request object.
        """

        # self._content = False
        self._content = b""
        self._content_consumed = False
        self._next = None

        #: Integer Code of responded HTTP Status, e.g. 404 or 200.
        self.status_code = None

        #: Case-insensitive Dictionary of Response Headers.
        #: For example, ``headers['content-type']`` will return the
        #: value of a ``'Content-Type'`` response header.
        self.headers = {}

        #: URL location of Response.
        self.url = None

        #: Encoding to decode with when accessing response text.
        self.encoding = None

        #: A list of :class:`Response <Response>` objects from
        #: the history of the Request.
        self.history = []

        #: Textual reason of responded HTTP Status, e.g. "Not Found" or "OK".
        self.reason = None

        #: A of Cookies the response headers.
        self.cookies = CaseInsensitiveDict()

        #: The amount of time elapsed between sending the request
        self.elapsed = datetime.timedelta(0)

        #: The :class:`PreparedRequest <PreparedRequest>` object to which this
        #: is a response.
        self.request = None


    def get_mime_type(self, path):
        """
        Determines the MIME type of a file based on its path.

        "params path (str): Path to the file.

        :rtype str: MIME type string (e.g., 'text/html', 'image/png').
        """

        try:
            mime_type, _ = mimetypes.guess_type(path)
        except Exception:
            return 'application/octet-stream'
        return mime_type or 'application/octet-stream'


    def prepare_content_type(self, mime_type='text/html'):
        base_dir = ""
        main_type, sub_type = mime_type.split('/', 1)
        

        if main_type == 'text':
            self.headers['Content-Type']='text/{}'.format(sub_type)
            if sub_type == 'html':
                base_dir = BASE_DIR+"www/"
            elif sub_type in ['plain', 'css', 'javascript']:
                base_dir = BASE_DIR+"static/"
            else:
                raise ValueError("Unsupported text subtype: {}".format(sub_type))
            
        elif main_type == 'image':
            base_dir = BASE_DIR+"static/"
            self.headers['Content-Type']='image/{}'.format(sub_type)

        elif main_type == 'application':
            if sub_type == 'javascript':
                base_dir = BASE_DIR+"static/"
                self.headers['Content-Type']='application/{}'.format(sub_type)
            else:
                base_dir = BASE_DIR+"apps/"
                self.headers['Content-Type']='application/{}'.format(sub_type)

        else:
            raise ValueError("Invalid MEME type: main_type={} sub_type={}".format(main_type,sub_type))

        return base_dir

    def build_content(self, path, base_dir):
        """
        Loads the objects file from storage space.

        :params path (str): relative path to the file.
        :params base_dir (str): base directory where the file is located.

        :rtype tuple: (int, bytes) representing content length and content data.
        """

        filepath = os.path.join(base_dir, path.lstrip('/'))

        print("[Response] serving the object at location {}".format(filepath))
            #
            #  TODO: implement the step of fetch the object file
            #        store in the return value of content
            #
        with open(filepath, 'rb') as f:
            content = f.read()
        return len(content), content


    def build_response_header(self, request):
        """
        Constructs the HTTP response headers based on the class:`Request <Request>
        and internal attributes.

        :params request (class:`Request <Request>`): incoming request object.

        :rtypes bytes: encoded HTTP response header.
        """
        reqhdr = request.headers
        rsphdr = self.headers

        if self.status_code is None:
            self.status_code = 200
            self.reason = "OK"

    #     #Build dynamic headers
    #     headers = {
    #             "Accept": "{}".format(reqhdr.get("Accept", "application/json")),
    #             "Accept-Language": "{}".format(reqhdr.get("Accept-Language", "en-US,en;q=0.9")),
    #             "Authorization": "{}".format(reqhdr.get("Authorization", "Basic <credentials>")),
    #             "Cache-Control": "no-cache",
    #             "Content-Type": "{}".format(self.headers['Content-Type']),
    #             "Content-Length": "{}".format(len(self._content)),
    #             "Cookie": "{}".format(reqhdr.get("Cookie", "sessionid=xyz789")), #dummy cooki
    #     #
    #     # TODO prepare the request authentication
    #     #
	# # self.auth = ...
    #             "Date": "{}".format(datetime.datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S GMT")),
    #             "Max-Forward": "10",
    #             "Pragma": "no-cache",
    #             "Proxy-Authorization": "Basic dXNlcjpwYXNz",  # example base64
    #             "Warning": "199 Miscellaneous warning",
    #             "User-Agent": "{}".format(reqhdr.get("User-Agent", "Chrome/123.0.0.0")),
    #         }

    #     # Header text alignment
    #         #
    #         #  TODO: implement the header building to create formated
    #         #        header from the provied headers
    #         #

        fmt_header = "HTTP/1.1 {} {}\r\n".format(self.status_code, self.reason)

        rsphdr['Date'] = "{}".format(datetime.datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S GMT"))
        rsphdr['Content-Length'] = "{}".format(len(self._content))

        for key, value in rsphdr.items():
            fmt_header += "{}: {}\r\n".format(key, value)
        fmt_header += "\r\n"  
        #
        # TODO prepare the request authentication
        #
	# self.auth = ...
        return str(fmt_header).encode('utf-8')


    def build_notfound(self):
        """
        Constructs a standard 404 Not Found HTTP response.

        :rtype bytes: Encoded 404 response.
        """

        return (
                "HTTP/1.1 404 Not Found\r\n"
                "Accept-Ranges: bytes\r\n"
                "Content-Type: text/html\r\n"
                "Content-Length: 13\r\n"
                "Cache-Control: max-age=86000\r\n"
                "Connection: close\r\n"
                "\r\n"
                "404 Not Found"
            ).encode('utf-8')
    

    def _build_api_response(self, response_data):
        """
        Xây dựng phản hồi HTTP bytes từ dict của WeApRous (hook_result).
        (Đây là logic được chuyển từ httpadapter.py sang)
        """
        try:
            status = response_data.get('status', 200)
            reason = response_data.get('reason', 'OK')
            
            # Kiểm tra xem content trả về là bytes (từ file) hay string (từ API JSON)
            if 'content_bytes' in response_data:
                content_bytes = response_data.get('content_bytes')
            else:
                content_str = response_data.get('content', '')
                content_bytes = content_str.encode('utf-8')

            headers_dict = response_data.get('headers', {})
            
            status_line = f"HTTP/1.1 {status} {reason}\r\n"
            header_lines = f"Content-Length: {len(content_bytes)}\r\n"
            
            # Thêm các header tùy chỉnh (Vd: Set-Cookie, Content-Type)
            for key, val in headers_dict.items():
                header_lines += f"{key}: {val}\r\n"
            
            # Nối tất cả lại
            response = (
                status_line.encode('utf-8') +
                header_lines.encode('utf-8') +
                b"\r\n" +  # Dòng trống
                content_bytes # Body
            )
            print('Xây resp thành công',response)
            return response
        
        except Exception as e:
            import json
            # Nếu "bảng hướng dẫn" (dict) bị lỗi
            print(f"[Response] Lỗi khi xây dựng API response: {e}")
            # Trả về lỗi 500 JSON
            error_content = json.dumps({"success": False, "message": "Internal Server Error"}).encode('utf-8')
            return (
                b"HTTP/1.1 500 Internal Server Error\r\n" +
                b"Content-Type: application/json\r\n" +
                f"Content-Length: {len(error_content)}\r\n\r\n".encode('utf-8') +
                error_content
            )


    def build_response(self, request):
        """
        Builds a full HTTP response including headers and content based on the request.

        :params request (class:`Request <Request>`): incoming request object.

        :rtype bytes: complete HTTP response using prepared headers and content.
        """

        # if hasattr(self, 'hook_result') and self.hook_result:
        #     import json
        #     self._content = json.dumps(self.hook_result).encode('utf-8')
        #     self.status_code = 200
        #     self.reason = "OK"
        #     self.headers['Content-Type'] = 'application/json'
        #     self._header = self.build_response_header(request)
        #     return self._header + self._content

        if hasattr(self, 'hook_result') and self.hook_result:
            print("[Response] Building API response from hook_result")
            return self._build_api_response(self.hook_result)

        path = request.path

        if request.method == 'POST' and path == '/login':
            parsed_body = {}
            if request.body:
                body_pairs = request.body.split('&')
                for pair in body_pairs:
                    if '=' in pair:
                        key, value = pair.split('=', 1)
                        if key in parsed_body:
                            parsed_body[key].append(value)
                        else:
                            parsed_body[key] = [value]

            username = parsed_body.get('username', [''])[0].strip()
            password = parsed_body.get('password', [''])[0].strip()

            if username == 'admin' and password == 'password':
                print("[Response] Login successful for user: {}".format(username))
                self.status_code = 302
                self.reason = "Found"
                self.headers['Set-Cookie'] = 'auth=true; Path=/'
                self.headers['Location'] = '/index.html'
                self._content = b''
                self._header = self.build_response_header(request)
                return self._header + self._content
            else:
                print("[Response] Login failed for user: {}".format(username))
                self.status_code = 401
                self.reason = "Unauthorized"
                path = '/loginUI.html'

                try: 
                    mime_type = self.get_mime_type(path)
                    base_dir = self.prepare_content_type(mime_type = 'text/html')
                    c_len, self._content = self.build_content(path, base_dir)
                    self._header = self.build_response_header(request)
                    return self._header + self._content
                except Exception as e:
                    print("[Response] Error loading login.html content: {}".format(e))
                    return self.build_notfound()
                
        if request.method == 'GET' and path == '/index.html':
            if request.cookies.get('auth') != 'true':
                print("[Response] Unauthorized access to index.html, redirecting to login.html")
                self.status_code = 302
                self.reason = "Found"
                self.headers['Location'] = '/loginUI.html'
                self._content = b''
                self._header = self.build_response_header(request)
                return self._header + self._content

        path = request.path
        mime_type = self.get_mime_type(path)
        base_dir = ""

        # 1. PHÂN LOẠI FILE VÀ XÁC ĐỊNH base_dir
        try:
            base_dir = self.prepare_content_type(mime_type)
        except ValueError:
            return self.build_notfound()

        # 2. KHẮC PHỤC LỖI LẶP ĐƯỜNG DẪN (Phần fix 404)
        if path.startswith('/static/') and base_dir.endswith('static/'):
            # Loại bỏ tiền tố /static/ khỏi path (Ví dụ: /static/js/fe.js -> js/fe.js)
            path = path.replace('/static/', '', 1) 

        # 3. TẢI NỘI DUNG VÀ PHẢN HỒI (CHUNG)
        try:
            c_len, self._content = self.build_content(path, base_dir)
        except FileNotFoundError:
            return self.build_notfound()
        except Exception:
            # Bắt tất cả lỗi khác, bao gồm cả lỗi đọc file (nếu có vấn đề về encoding/lock)
            return self.build_notfound()
                
        self._header = self.build_response_header(request)

        return self._header + self._content


    
    