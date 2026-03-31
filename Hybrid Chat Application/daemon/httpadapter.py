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
# daemon.httpadapter
# ~~~~~~~~~~~~~~~~~

# This module provides a http adapter object to manage and persist 
# http settings (headers, bodies). The adapter supports both
# raw URL paths and RESTful route definitions, and integrates with
# Request and Response objects to handle client-server communication.
# """
# import json
# from .request import Request
# from .response import Response
# from .dictionary import CaseInsensitiveDict

# class HttpAdapter:
#     """
#     A mutable :class:`HTTP adapter <HTTP adapter>` for managing client connections
#     and routing requests.

#     The `HttpAdapter` class encapsulates the logic for receiving HTTP requests,
#     dispatching them to appropriate route handlers, and constructing responses.
#     It supports RESTful routing via hooks and integrates with :class:`Request <Request>` 
#     and :class:`Response <Response>` objects for full request lifecycle management.

#     Attributes:
#         ip (str): IP address of the client.
#         port (int): Port number of the client.
#         conn (socket): Active socket connection.
#         connaddr (tuple): Address of the connected client.
#         routes (dict): Mapping of route paths to handler functions.
#         request (Request): Request object for parsing incoming data.
#         response (Response): Response object for building and sending replies.
#     """

#     __attrs__ = [
#         "ip",
#         "port",
#         "conn",
#         "connaddr",
#         "routes",
#         "request",
#         "response",
#     ]

#     def __init__(self, ip, port, conn, connaddr, routes):
#         """
#         Initialize a new HttpAdapter instance.

#         :param ip (str): IP address of the client.
#         :param port (int): Port number of the client.
#         :param conn (socket): Active socket connection.
#         :param connaddr (tuple): Address of the connected client.
#         :param routes (dict): Mapping of route paths to handler functions.
#         """

#         #: IP address.
#         self.ip = ip
#         #: Port.
#         self.port = port
#         #: Connection
#         self.conn = conn
#         #: Conndection address
#         self.connaddr = connaddr
#         #: Routes
#         self.routes = routes
#         #: Request
#         self.request = Request()
#         #: Response
#         self.response = Response()

#     def handle_client(self, conn, addr, routes):
#         """
#         Handle an incoming client connection.
#         """
        
#         self.conn = conn        
#         self.connaddr = addr
#         req = self.request
#         resp = self.response

#         try:
#             msg = conn.recv(4096).decode()
#             if not msg:
#                 conn.close()
#                 return
#         except ConnectionResetError:
#             conn.close()
#             return
            
#         req.prepare(msg, routes)
        
#         # 1. GỌI HOOK (NẾU CÓ)
#         # hook_result sẽ là dict (nếu là API) hoặc None (nếu là file tĩnh)
#         hook_result = None
#         if req.hook:
#             try:
#                 # Gọi hàm API (ví dụ: login(), get_peers(), serve_static_css())
#                 resp.hook_result = req.hook(headers=req.headers, body=req.body)
#             except Exception as e:
#                 # Nếu chính hàm API (app.py) bị lỗi (ví dụ: lỗi logic, DB...)
#                 print(f"[HttpAdapter] LỖI THỰC THI HOOK: {e}")
#                 hook_result = {
                    
#                     'status': 500,
#                     'reason': 'Internal Server Error',
#                     'content': json.dumps({"success": False, "message": "Lỗi server khi thực thi route."})
#                 }

#         # 2. CHUYỂN TIẾP CHO RESPONSE.PY XỬ LÝ
#         # Luôn gọi build_response, dù là API hay file tĩnh
#         response_bytes = resp.build_response(req) 

#         conn.sendall(response_bytes)
#         conn.close()

#     #@property
#     def extract_cookies(self, req, resp):
#         """
#         Build cookies from the :class:`Request <Request>` headers.

#         :param req:(Request) The :class:`Request <Request>` object.
#         :param resp: (Response) The res:class:`Response <Response>` object.
#         :rtype: cookies - A dictionary of cookie key-value pairs.
#         """
#         cookies = {}
#         headers = req.headers or {}
#         for header in headers:
#             if header.startswith("Cookie:"):
#                 cookie_str = header.split(":", 1)[1].strip()
#                 for pair in cookie_str.split(";"):
#                     key, value = pair.strip().split("=")
#                     cookies[key] = value
#         return cookies


    
#     def build_response(self, req, resp):
#         """Builds a :class:`Response <Response>` object 

#         :param req: The :class:`Request <Request>` used to generate the response.
#         :param resp: The  response object.
#         :rtype: Response
#         """
#         response = Response()

#         # Set encoding.
#         #response.encoding = self.get_encoding_from_headers(response.headers)
#         response = resp
#         response.reason = response.raw.reason

#         if isinstance(req.url, bytes):
#             response.url = req.url.decode("utf-8")
#         else:
#             response.url = req.url

#         # Add new cookies from the server.
#         response.cookies = self.extract_cookies(req, resp)

#         # Give the Response some context.
#         response.request = req
#         response.connection = self

#         return response

#     # def get_connection(self, url, proxies=None):
#         # """Returns a url connection for the given URL. 

#         # :param url: The URL to connect to.
#         # :param proxies: (optional) A Requests-style dictionary of proxies used on this request.
#         # :rtype: int
#         # """

#         # proxy = select_proxy(url, proxies)

#         # if proxy:
#             # proxy = prepend_scheme_if_needed(proxy, "http")
#             # proxy_url = parse_url(proxy)
#             # if not proxy_url.host:
#                 # raise InvalidProxyURL(
#                     # "Please check proxy URL. It is malformed "
#                     # "and could be missing the host."
#                 # )
#             # proxy_manager = self.proxy_manager_for(proxy)
#             # conn = proxy_manager.connection_from_url(url)
#         # else:
#             # # Only scheme should be lower case
#             # parsed = urlparse(url)
#             # url = parsed.geturl()
#             # conn = self.poolmanager.connection_from_url(url)

#         # return conn


#     def add_headers(self, request):
#         """
#         Add headers to the request.

#         This method is intended to be overridden by subclasses to inject
#         custom headers. It does nothing by default.

        
#         :param request: :class:`Request <Request>` to add headers to.
#         """
#         pass

#     def build_proxy_headers(self, proxy):
#         """Returns a dictionary of the headers to add to any request sent
#         through a proxy. 

#         :class:`HttpAdapter <HttpAdapter>`.

#         :param proxy: The url of the proxy being used for this request.
#         :rtype: dict
#         """
#         headers = {}
#         #
#         # TODO: build your authentication here
#         #       username, password =...
#         # we provide dummy auth here
#         #
#         username, password = ("user1", "password")

#         if username:
#             headers["Proxy-Authorization"] = (username, password)

#         return headers
"""
daemon.httpadapter
~~~~~~~~~~~~~~~~~

This module provides a http adapter object to manage and persist 
http settings (headers, bodies). The adapter supports both
raw URL paths and RESTful route definitions, and integrates with
Request and Response objects to handle client-server communication.
"""
import json
from .request import Request
from .response import Response
from .dictionary import CaseInsensitiveDict

class HttpAdapter:
    """
    A mutable :class:`HTTP adapter <HTTP adapter>` for managing client connections
    and routing requests.

    The `HttpAdapter` class encapsulates the logic for receiving HTTP requests,
    dispatching them to appropriate route handlers, and constructing responses.
    It supports RESTful routing via hooks and integrates with :class:`Request <Request>` 
    and :class:`Response <Response>` objects for full request lifecycle management.

    Attributes:
        ip (str): IP address of the client.
        port (int): Port number of the client.
        conn (socket): Active socket connection.
        connaddr (tuple): Address of the connected client.
        routes (dict): Mapping of route paths to handler functions.
        request (Request): Request object for parsing incoming data.
        response (Response): Response object for building and sending replies.
    """

    __attrs__ = [
        "ip",
        "port",
        "conn",
        "connaddr",
        "routes",
        "request",
        "response",
    ]

    def __init__(self, ip, port, conn, connaddr, routes):
        """
        Initialize a new HttpAdapter instance.

        :param ip (str): IP address of the client.
        :param port (int): Port number of the client.
        :param conn (socket): Active socket connection.
        :param connaddr (tuple): Address of the connected client.
        :param routes (dict): Mapping of route paths to handler functions.
        """

        #: IP address.
        self.ip = ip
        #: Port.
        self.port = port
        #: Connection
        self.conn = conn
        #: Conndection address
        self.connaddr = connaddr
        #: Routes
        self.routes = routes
        #: Request
        self.request = Request()
        #: Response
        self.response = Response()

    def handle_client(self, conn, addr, routes):
        """
        Handle an incoming client connection.
        """
        
        self.conn = conn        
        self.connaddr = addr
        req = self.request
        resp = self.response

        try:
            msg = conn.recv(4096).decode()
            if not msg:
                conn.close()
                return
        except ConnectionResetError:
            conn.close()
            return
            
        req.prepare(msg, routes)
        
        # 1. GỌI HOOK (NẾU CÓ)
        # hook_result sẽ là dict (nếu là API) hoặc None (nếu là file tĩnh)
        hook_result = None
        if req.hook:
            try:
                # Gọi hàm API (ví dụ: login(), get_peers(), serve_static_css())
                resp.hook_result = req.hook(headers=req.headers, body=req.body)
            except Exception as e:
                # Nếu chính hàm API (app.py) bị lỗi (ví dụ: lỗi logic, DB...)
                print(f"[HttpAdapter] LỖI THỰC THI HOOK: {e}")
                hook_result = {
                    
                    'status': 500,
                    'reason': 'Internal Server Error',
                    'content': json.dumps({"success": False, "message": "Lỗi server khi thực thi route."})
                }

        # 2. CHUYỂN TIẾP CHO RESPONSE.PY XỬ LÝ
        # Luôn gọi build_response, dù là API hay file tĩnh
        response_bytes = resp.build_response(req) 

        conn.sendall(response_bytes)
        conn.close()

    #@property
    def extract_cookies(self, req, resp):
        """
        Build cookies from the :class:`Request <Request>` headers.

        :param req:(Request) The :class:`Request <Request>` object.
        :param resp: (Response) The res:class:`Response <Response>` object.
        :rtype: cookies - A dictionary of cookie key-value pairs.
        """
        cookies = {}
        headers = req.headers or {}
        for header in headers:
            if header.startswith("Cookie:"):
                cookie_str = header.split(":", 1)[1].strip()
                for pair in cookie_str.split(";"):
                    key, value = pair.strip().split("=")
                    cookies[key] = value
        return cookies


    
    def build_response(self, req, resp):
        """Builds a :class:`Response <Response>` object 

        :param req: The :class:`Request <Request>` used to generate the response.
        :param resp: The  response object.
        :rtype: Response
        """
        response = Response()

        # Set encoding.
        #response.encoding = self.get_encoding_from_headers(response.headers)
        response = resp
        response.reason = response.raw.reason

        if isinstance(req.url, bytes):
            response.url = req.url.decode("utf-8")
        else:
            response.url = req.url

        # Add new cookies from the server.
        response.cookies = self.extract_cookies(req, resp)

        # Give the Response some context.
        response.request = req
        response.connection = self

        return response

    # def get_connection(self, url, proxies=None):
        # """Returns a url connection for the given URL. 

        # :param url: The URL to connect to.
        # :param proxies: (optional) A Requests-style dictionary of proxies used on this request.
        # :rtype: int
        # """

        # proxy = select_proxy(url, proxies)

        # if proxy:
            # proxy = prepend_scheme_if_needed(proxy, "http")
            # proxy_url = parse_url(proxy)
            # if not proxy_url.host:
                # raise InvalidProxyURL(
                    # "Please check proxy URL. It is malformed "
                    # "and could be missing the host."
                # )
            # proxy_manager = self.proxy_manager_for(proxy)
            # conn = proxy_manager.connection_from_url(url)
        # else:
            # # Only scheme should be lower case
            # parsed = urlparse(url)
            # url = parsed.geturl()
            # conn = self.poolmanager.connection_from_url(url)

        # return conn


    def add_headers(self, request):
        """
        Add headers to the request.

        This method is intended to be overridden by subclasses to inject
        custom headers. It does nothing by default.

        
        :param request: :class:`Request <Request>` to add headers to.
        """
        pass

    def build_proxy_headers(self, proxy):
        """Returns a dictionary of the headers to add to any request sent
        through a proxy. 

        :class:`HttpAdapter <HttpAdapter>`.

        :param proxy: The url of the proxy being used for this request.
        :rtype: dict
        """
        headers = {}
        #
        # TODO: build your authentication here
        #       username, password =...
        # we provide dummy auth here
        #
        username, password = ("user1", "password")

        if username:
            headers["Proxy-Authorization"] = (username, password)

        return headers
    

