# Example usage
import json
from flask import Flask, request, redirect, url_for,send_from_directory,render_template
from flask_cors import CORS

from db.db_manager import DBManager

db = DBManager()

PORT = 8000  # Default port





def checkCookie(cookies):
    if(cookies['Authentication'] == 'true'):
        return True
    return False



def create_sampleapp():

    #app = Flask(__name__)

    app = Flask(__name__, template_folder="../www",static_folder="../static")  # Flask sẽ tìm html ở www
    CORS(app, origins=["http://127.0.0.1:8000"])

    @app.route("/", methods=["GET"])
    def home():
        return render_template('loginUI.html')

    @app.route("/mainUI", methods=["GET"])
    def mainUI():
        return render_template('mainUI.html')

    @app.route("/user", methods=["GET"])
    def get_user():
        return {"id": 1, "name": "Alice", "email": "alice@example.com"} 

    @app.route("/echo", methods=["POST"])
    #def echo(body):
    def echo():
        body = request.data.decode('utf-8')
        try:
            data = json.loads(body)
            return {"received": data}
        except json.JSONDecodeError:
            return {"error": "Invalid JSON"}
        
    
    @app.route('/login', methods=['POST'])
    def login():
        data = request.get_json()#them
        
        #data  = json.loads(body)
        username = data.get("username")
        password = data.get("password")
        user = db.get_user(username)
        if user and user['password'] == password:
            return {"success": True, "message": "Login successful"}
        else:
            return {'success':False , 'message': "Login failed"}
    
    
    @app.route('/register', methods=['POST'])
    def register():
        print("Register endpoint called")
        data = request.get_json()# them
        #data = json.loads(body)
        username = data.get("username")
        password = data.get('password')
        existing_user = db.get_user(username)
        if existing_user:
            return {'success':False , 'message': "Username already exists"}
        db.add_usser(username,password)
        return {'success':True , 'message': "Registration successful"}
    
    
    
    @app.route("/submit_info",method =["POST"])
    # lấy thông tin -> lưu vào db
    def submit_info():
        print(f"[App] Nhận được yêu cầu /submit-info")
        try:
            data = request.get_json()# them
            #data = json.loads(body)
            peer_id = data.get('peer_id')
            peer_ip = data.get('peer_ip')
            peer_port = data.get('peer_port')
            print(f"Received peer info: ID={peer_id}, IP={peer_ip}, Port={peer_port}")
            
            if not peer_id or not peer_ip or not peer_port:
                return {'success':False , 'message': "Missing required fields"}
            
            # save to db
            db.add_peer(peer_id, peer_ip, peer_port)

        except Exception as e:
            print(f"Lỗi : {e}")
            return {'success':False , 'message': "Invalid data format"}
        
        
        return {'success':True , 'message': "Info submitted successfully"}
    
    
    
    
    
    
    
    return app