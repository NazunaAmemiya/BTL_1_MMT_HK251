import json
import os

user_global =[]
peer_global =[]

class DBManager:
    def __init__(self):
        self.users_file = 'db/users.json'
        self.peers_file = 'db/peers.json'

        #base_dir = os.path.dirname(__file__)  # thư mục chứa db_manager.py
        #self.users_file = os.path.join(base_dir, 'users.json')
        #self.peers_file = os.path.join(base_dir, 'users.json')
    
        with open(self.users_file, 'r') as f:
            user_global = json.load(f)
            #self.users = user_global
        
        with open(self.peers_file, 'r') as f:
            peer_global = json.load(f)
            #self.peers = peer_global

    def add_usser(self,username, password):
        new_user = { 'username' : username , 'password' : password }
        #self.users.append(new_user)
        user_global.append(new_user)
        with open(self.users_file, 'w') as f:
            json.dump(user_global,f)


    def add_peer(self, peer_id, peer_ip, peer_port):
        new_peer = {'peer_id': peer_id, 'peer_ip': peer_ip,'peer_port':peer_port}
        #self.peers.append(new_peer)
        peer_global.append(new_peer)
        with open(self.peers_file, 'w') as f:
            json.dump(peer_global,f)
    
    def delete_user(self, username):
        user_global = [user for user in user_global if user['username'] != username]
        with open(self.users_file, 'w') as f:
            json.dump(user_global,f)


    def delete_peer(self, peer_id):
        peer_global = [peer for peer in peer_global if peer['peer_id'] != peer_id]
        with open(self.peers_file, 'w') as f:
            json.dump(peer_global,f)

    def get_user(self, username):
        for user in user_global:
            if user['username'] == username :
                return user
        return None
    
    def get_peer(self, peer_id):
        for peer in peer_global:
            if peer['peer_id'] == peer_id:
                return peer
        return None

    def get_list_user(self):
        return user_global
    
    def get_list_peer(self):
        return peer_global
    
