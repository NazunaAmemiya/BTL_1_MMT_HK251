const PROXY_BASE_URL = window.location.protocol + "//" + '10.230.155.99:9010';

// Lấy PEER_ID từ sessionStorage (login)
let PEER_ID = sessionStorage.getItem('username') || `User_${Math.floor(Math.random()*1000)}`;
//const MY_P2P_IP = '10.230.155.99';
//const MY_P2P_PORT = 9003;

// UI
const peerListUI = document.getElementById('peer-list');
const chatWindow = document.getElementById('chat-window');
const chatInput = document.getElementById('chat-input');
const sendBtn = document.getElementById('send-btn');
const currentPeerUI = document.getElementById('current-peer');
const reloadPeer = document.getElementById('reloadPeer');
const broadcastBtn = document.getElementById('broadcast-btn');

let currentRecipient = null;
let unread ={}


// --- Gọi API ---
async function apiCall(path, method='GET', body=null){
    const options = {method, headers: {'Content-Type':'application/json'},credentials: 'include'};
    if(body) options.body = JSON.stringify(body);
    try{
        const res = await fetch(`${PROXY_BASE_URL}${path}`, options);
        const data = await res.json();
        return {ok: res.ok, data};
    }catch(e){
        console.error("API error:", e);
        return {ok:false, data:{message:"Lỗi kết nối"}};
    }
}


// --- Lấy danh sách Peer ---
async function refreshPeers(){
    await getPeerList();
}

async function logout(){
    // Lấy username đang đăng nhập (đã lưu trong sessionStorage)
    const username = sessionStorage.getItem('username');
    
    // 1. Gửi yêu cầu xóa Peer khỏi Tracker
    const res = await apiCall('/logout', 'POST', { username: username });
    
    if (res.ok) {
        // 2. Xóa thông tin cục bộ và chuyển về trang login
        sessionStorage.removeItem('username');
        // Thường thì bạn sẽ redirect về trang login/trang chủ
        window.location.href = '/loginUI.html'; 
    } else {
        console.error("Logout thất bại:", res.data.message);
        alert("Đăng xuất thất bại: " + (res.data.message || "Lỗi không xác định"));
    }
}

// --- Gửi tin nhắn ---
async function sendMessage(){
    const msg = chatInput.value.trim();
    if(!msg || !currentRecipient) return;
    
    // Hiển thị ở web
    addMessage(PEER_ID, msg, 'self');
    chatInput.value='';

    // Gửi tới API
    const res = await apiCall('/send_direct_message','POST',{
        sender_id: PEER_ID,
        recipient_ip: currentRecipient.peer_ip,
        recipient_port: currentRecipient.peer_port,
        
        // --- THÊM DÒNG NÀY ---
        recipient_id: currentRecipient.peer_id, // Gửi ID của người nhận
        // --------------------
        
        message: msg
    });

    if(!res.ok) addMessage('System', res.data.message, 'error');
}

// --- Hiển thị tin nhắn ---
function addMessage(sender, msg, type='other'){
    const div = document.createElement('div');
    // Đảm bảo CSS phân biệt 'self' và 'other'
    div.className = type==='self'?'text-right text-indigo-700':'text-left';
    div.textContent = `${sender}: ${msg}`;
    chatWindow.appendChild(div);
    chatWindow.scrollTop = chatWindow.scrollHeight;
}


async function pollNewMessages(){
    if (!PEER_ID || !currentRecipient) return; // Chỉ Polling khi có người được chọn

    // Gửi yêu cầu Polling. API này trả về dict: {"conversations": {"Peer_X": [...], "Peer_Z": [...]}}
    const res = await apiCall('/get_new_messages', 'POST', { 
        user_id: PEER_ID // Gửi ID của mình để Backend biết hỏi Peer Process nào
    }); 

    if(res.ok && res.data.success && res.data.conversations){
        const conversations = res.data.conversations;
        
        const activeRecipientId = currentRecipient.peer_id;
        
        // CHỈ hiển thị nếu Peer đang chat có tin nhắn mới
        if (conversations.hasOwnProperty(activeRecipientId)) {
            
            conversations[activeRecipientId].forEach(msg => {
                 // 3. Hiển thị từng tin nhắn mới
                 addMessage(msg.sender, msg.message, 'other'); 
            });
        }
    }
}






async function loadChatHistory(targetPeerId) {
    const res = await apiCall('/get_chat_history', 'POST', {
        user_id: PEER_ID, 
        target_peer_id: targetPeerId 
    });

    // Xóa cửa sổ chat cũ (RẤT QUAN TRỌNG)
    chatWindow.innerHTML = '';
    
    if (res.ok && res.data.success && res.data.history) {
        // GIẢ ĐỊNH: history đã là danh sách kết hợp (sent + received) và đã sắp xếp theo thời gian
        const history = res.data.history; 

        if (history.length === 0) {
            chatWindow.innerHTML = `<div class="text-gray-500">Bắt đầu chat với ${targetPeerId}</div>`;
        } else {
            // Hiển thị từng tin nhắn trong lịch sử
            history.forEach(msg => {
                let messageType;
                console.log(`Tải lịch sử với ${targetPeerId}:`, history);
                console.log(`PEER_ID của t là: [${PEER_ID}]`);
                // So sánh người gửi (sender) của tin nhắn với ID của mình (PEER_ID)
                // PEER_ID này được lấy từ sessionStorage ở đầu file messenger.js
                if (msg.sender === PEER_ID) {
                    messageType = 'self'; // Tin nhắn của mình
                } else {
                    messageType = 'other'; // Tin nhắn của người kia
                }
                
                // Gọi addMessage với đúng type
                addMessage(msg.sender, msg.message, messageType);
            });
        }
    } else {
         chatWindow.innerHTML = `<div class="text-red-500">Không thể tải lịch sử chat.</div>`;
    }
}


// --- Chọn Peer để chat ---
function selectPeer(peer){
    currentRecipient = peer;
    currentPeerUI.textContent = `${peer.peer_id} (${peer.peer_ip}:${peer.peer_port})`;
    
    // 1. Xóa đốm đỏ (thủ công, để phản hồi nhanh)
    const listItem = document.querySelector(`[data-peer-id="${peer.peer_id}"] .notification-badge`);
    if (listItem) {
        listItem.classList.add('hidden');
    }
    delete unreadStatus[peer.peer_id];
    
    // 2. Tải toàn bộ lịch sử chat (Để hiển thị lịch sử và đánh dấu READ ở Backend)
    loadChatHistory(peer.peer_id);
    
    // Bỏ gọi pollNewMessages/pollForUpdates: Logic cập nhật tức thời đã nằm trong setInterval bên trên.
}

let unreadStatus = {}; 
window.allPeers = []; // Lưu trữ danh sách peer đang online

// --- Hàm Polling Notification ---
async function pollUnreadStatus() {
    const res = await apiCall('/poll_unread_status', 'POST', { user_id: PEER_ID });

    if (res.ok && res.data.success) {
        const unreadPeersList = res.data.unread_peers || []; 
        let changed = false;
        const newUnreadStatus = {};
        
        unreadPeersList.forEach(peerId => {
            newUnreadStatus[peerId] = true;
            if (!unreadStatus[peerId]) changed = true;
        });
        console.log('NewUnread',newUnreadStatus)
        // 1. Logic CẬP NHẬT UI ĐỐM ĐỎ
        if (changed || Object.keys(unreadStatus).length !== unreadPeersList.length) {
            console.log('RUN')
            unreadStatus = newUnreadStatus;
            
            updatePeerListUI(); 
        }

        // 2. LOGIC CẬP NHẬT TỨC THỜI CHO CHAT WINDOW
        if (currentRecipient) {
            const activeRecipientId = currentRecipient.peer_id;
            
            // Nếu Peer đang xem có tin nhắn NEW
            if (unreadPeersList.includes(activeRecipientId))  {
                 // Gọi tải lịch sử ngay lập tức. Hành động này sẽ:
                 // a) Đánh dấu tin nhắn là READ ở Backend.
                 // b) Tải toàn bộ lịch sử (bao gồm tin nhắn mới) và vẽ lại cửa sổ chat.
                 loadChatHistory(activeRecipientId);
            }
        }
    }
}

// Chạy Polling định kỳ ( 3 giây)
setInterval(pollUnreadStatus, 3000);



function renderPeerListItem(peer) {
    const li = document.createElement('li');
    li.className = "peer-item p-2 hover:bg-indigo-100 rounded cursor-pointer flex justify-between items-center";
    li.setAttribute('data-peer-id', peer.peer_id);
    li.onclick = () => selectPeer(peer);

    // Tên Peer
    const nameSpan = document.createElement('span');
    nameSpan.textContent = peer.peer_id;
    
    // Đốm đỏ (Notification Badge)
    const badgeSpan = document.createElement('span');
    
    // KHỞI TẠO: Thêm lớp 'hidden' vào định nghĩa ban đầu
    badgeSpan.className = "notification-badge w-3 h-3 bg-red-500 rounded-full ml-2 hidden"; 

    // --- LOGIC HIỂN THỊ ĐỐM ĐỎ ---
    // Kiểm tra trạng thái unreadStatus[peer.peer_id]
    if (unreadStatus[peer.peer_id]) { 
        // Nếu có tin mới (unreadStatus là true), xóa lớp 'hidden'
        badgeSpan.classList.remove('hidden'); 
    }
    // -------------------------

    li.appendChild(nameSpan);
    li.appendChild(badgeSpan);
    return li;
}


function updatePeerListUI() {
    
    peerListUI.innerHTML = '';
    if (!window.allPeers || window.allPeers.length === 0) {
        peerListUI.innerHTML = `<li class="text-gray-500">Không có peer nào online.</li>`;
        return;
    }
    
    window.allPeers.forEach(peer => {
        const listItem = renderPeerListItem(peer);
        peerListUI.appendChild(listItem);
    });
}


async function getPeerList() {
    const result = await apiCall('/get_peers');
    if (result.ok && result.data.success) {
        window.allPeers = result.data.peers.filter(p => p.peer_id !== PEER_ID); 
        console.log("WINDoWW",window.allPeers)
        // Sau khi lấy danh sách Peer, cập nhật UI (lần đầu)
        updatePeerListUI();
    } else {
        peerListUI.innerHTML = `<li class="text-red-500">${result.data.message}</li>`;
    }
}


async function sendBroadcast() {
    // 1. Hiển thị hộp thoại Pop-up
    const msg = prompt("Nhập tin nhắn muốn gửi cho TẤT CẢ MỌI NGƯỜI:", "");

    // 2. Kiểm tra (Nếu người dùng bấm "Cancel" hoặc không nhập gì)
    if (!msg || msg.trim().length === 0) {
        console.log("Broadcast đã hủy.");
        return;
    }

    // 3. Gọi API
    console.log(`Đang gửi broadcast: ${msg}`);
    const res = await apiCall('/broadcast_message', 'POST', {
        sender_id: PEER_ID, // PEER_ID của mình
        message: msg.trim()
    });

    if (res.ok && res.data.success) {
        alert("Đã gửi tin nhắn broadcast thành công!");
    } else {
        alert("Gửi broadcast thất bại: ",(res.data.message || "Lỗi server"));
    }
}


// --- Event ---
sendBtn.addEventListener('click', sendMessage);
chatInput.addEventListener('keypress', e=>{
    if(e.key==='Enter') sendMessage();
});
reloadPeer.addEventListener('click', refreshPeers);

document.addEventListener('DOMContentLoaded', () => {
    const logoutBtn = document.getElementById('logout-btn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', logout);
    }
    getPeerList();
});
broadcastBtn.addEventListener('click', sendBroadcast);