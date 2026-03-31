// --- Cấu hình API Base ---
const PROXY_BASE_URL = window.location.protocol + "//" + window.location.host;

// --- Thông tin Peer (Client) ---
let PEER_ID = sessionStorage.getItem('username');

// Fallback (Nếu sessionStorage bị trống hoặc lỗi, ví dụ: user vào thẳng chatUI.html)
if (!PEER_ID) {
    alert("Lỗi: Không tìm thấy username. Dùng ID ngẫu nhiên.");
    PEER_ID = `User_Random_${Math.floor(Math.random() * 1000)}`;
}
const MY_P2P_IP = '127.0.0.1';
const MY_P2P_PORT = 9003; // Cổng P2P mặc định cho Peer này

// --- Khai báo biến UI (Lấy từ chatUI.html) ---
const registerBtn = document.getElementById('register-peer-btn');
const refreshBtn = document.getElementById('refresh-peers-btn');
const activePeersList = document.getElementById('active-peers');
const apiLog = document.getElementById('api-log');
const msgWindow = document.getElementById('message-window');
const msgInput = document.getElementById('message-input');
const sendBtn = document.getElementById('send-msg-btn');
let selectedPeerUI;

// BIẾN MỚI: Lưu trữ thông tin người nhận
let currentRecipient = null; // { id: '...', ip: '...', port: ... }


// Cập nhật UI thông tin của chính mình
document.getElementById('my-peer-id').textContent = PEER_ID;
document.getElementById('access-host-port').textContent = `${window.location.hostname}:${window.location.port}`;
document.getElementById('my-ip').textContent = MY_P2P_IP;
document.getElementById('my-port').textContent = MY_P2P_PORT;



// --- (Hàm log() và apiCall() giữ nguyên) ---
function log(message, type = 'info') {
    const logItem = document.createElement('div');
    logItem.textContent = `[${new Date().toLocaleTimeString()}] [${type.toUpperCase()}] ${message}`;
    if (type === 'error') {
        logItem.className = 'text-red-400';
    } else if (type === 'success') {
        logItem.className = 'text-yellow-300';
    } else if (type === 'info') {
        logItem.className = 'text-green-400';
    }
    apiLog.prepend(logItem); 
    if (apiLog.children.length > 50) { 
        apiLog.removeChild(apiLog.lastChild);
    }
}

async function apiCall(path, method = 'GET', body = null) {
    const url = `${PROXY_BASE_URL}${path}`;
    log(`CALL: ${method} ${path}`, 'info');

    const options = {
        method: method,
        headers: {
            'Content-Type': 'application/json',
        }
    };

    if (body) {
        options.body = JSON.stringify(body);
    }

    try {
        const response = await fetch(url, options);
        
        if (response.status === 401) {
            log('LỖI: Unauthorized. Cookie không hợp lệ. Đang chuyển về trang Login.', 'error');
            alert('Phiên đăng nhập không hợp lệ. Vui lòng đăng nhập lại.');
            window.location.href = `${PROXY_BASE_URL}/loginUI.html`;
            return { success: false, data: { message: "Unauthorized" } };
        }
        
        const data = await response.json();
        log(`RESPONSE: ${response.status} ${response.statusText}`, response.ok ? 'success' : 'error');
        
        return { success: response.ok, data: data, status: response.status };

    } catch (error) {
        log(`LỖI KẾT NỐI: ${error.message}. (Server 9001 có thể đang lỗi)`, 'error');
        return { success: false, data: { message: "Lỗi kết nối hoặc server không phản hồi." } };
    }
}

// --- 1. Logic Đăng ký Peer (submit_info) (Giữ nguyên) ---
async function registerPeer() {
    registerBtn.disabled = true;
    registerBtn.textContent = 'Đang đăng ký...';

    const info = {
        peer_id: PEER_ID,
        peer_ip: MY_P2P_IP,
        peer_port: MY_P2P_PORT
    };
    
    const result = await apiCall('/submit_info', 'POST', info);
    
    if (result.success) {
        log(`Đăng ký Peer thành công: ${PEER_ID} tại ${MY_P2P_IP}:${MY_P2P_PORT}`, 'success');
        refreshPeers(); 
    } else {
        log(`Đăng ký Peer thất bại: ${result.data.message}`, 'error');
    }
    
    registerBtn.disabled = false;
    registerBtn.textContent = '1. Đăng ký Peer (Gọi /submit_info)';
}

// --- 2. Logic Lấy Danh sách Peer (get_peers) ---
async function refreshPeers() {
    refreshBtn.disabled = true;
    refreshBtn.textContent = 'Đang làm mới...';

    const result = await apiCall('/get_peers', 'GET');
    console.log("đã lấy res",result)
    activePeersList.innerHTML = '';
    
    if (result.success) {
        const peers = result.data.peers.filter(p => p.peer_id !== PEER_ID); 
        console.log(peers)
        if (peers.length === 0) {
            activePeersList.innerHTML = '<li class="text-gray-500 p-2">Chưa có Peer nào khác.</li>';
        } else {
            peers.forEach(peer => {
                const li = document.createElement('li');
                console.log(peer)
                li.className = 'p-2 bg-white rounded-md shadow-sm border border-gray-200 cursor-pointer hover:bg-indigo-100 transition duration-150';
                li.innerHTML = `<strong>${peer.peer_id || 'Unknown'}</strong> (${peer.peer_ip}:${peer.peer_port})`;
                
                // SỬA: Thêm sự kiện OnClick để CHỌN PEER
                li.onclick = () => selectPeer(peer.peer_id, peer.ip, peer.port);
                
                activePeersList.appendChild(li);
            });
            log(`Tìm thấy ${peers.length} Peer khác.`, 'success');
        }
    } else {
        activePeersList.innerHTML = `<li class="text-red-500 p-2">${result.data.message}</li>`;
    }
    
    refreshBtn.disabled = false;
    refreshBtn.textContent = '2. Lấy Danh sách Peer (Gọi /get_peers)';
}

// --- HÀM MỚI: Chọn 1 Peer để nhắn tin ---
function selectPeer(peer_id, ip, port) {
    log(`Đã chọn Peer: ${peer_id} tại ${ip}:${port}`, 'info');
    
    // 1. Lưu trữ thông tin người nhận
    currentRecipient = {
        id: peer_id,
        ip: ip,
        port: port
    };
    
    // 2. Cập nhật UI
    selectedPeerUI.textContent = `${peer_id} (${ip}:${port})`;
    msgInput.disabled = false;
    sendBtn.disabled = false;
    
    // 3. (Tùy chọn) Xóa cửa sổ chat cũ, tải lịch sử chat mới
    msgWindow.innerHTML = `<div class="text-center text-gray-500"><p>Bắt đầu chat với ${peer_id}.</p></div>`;
}


// --- 3. LOGIC GỬI TIN NHẮN (SỬA: Gửi Direct Message) ---
async function sendMessage() {
    const message = msgInput.value.trim();
    if (!message) return;
    
    // SỬA: Kiểm tra xem đã chọn người nhận chưa
    if (!currentRecipient) {
        alert("Vui lòng chọn một Peer từ danh sách bên trái trước khi gửi!");
        return;
    }

    sendBtn.disabled = true;
    sendBtn.textContent = 'Đang gửi...';

    // Hiển thị tin nhắn của chính mình
    addMessageToWindow(PEER_ID, message, 'self');
    msgInput.value = '';

    // SỬA: Gửi tin nhắn đến API /send_direct_message
    const result = await apiCall('/send_direct_message', 'POST', {
        sender_id: PEER_ID,
        message: message,
        recipient_ip: currentRecipient.ip,
        recipient_port: currentRecipient.port
    });

    if (result.success) {
        log(`Đã gửi (Relay) tin nhắn đến ${currentRecipient.id} thành công.`, 'success');
    } else {
        log(`Gửi tin nhắn thất bại: ${result.data.message}`, 'error');
    }
    
    sendBtn.disabled = false;
    sendBtn.textContent = 'Gửi (Direct)';
}

// Hàm hiển thị tin nhắn (Giữ nguyên)
function addMessageToWindow(sender, message, type = 'other') {
    const msgDiv = document.createElement('div');
    
    let alignment = 'justify-start';
    let bgColor = 'bg-gray-200';
    let textColor = 'text-gray-800';

    if (type === 'self') {
        alignment = 'justify-end';
        bgColor = 'bg-indigo-600';
        textColor = 'text-white';
    }

    msgDiv.className = `flex ${alignment}`;
    
    const contentDiv = document.createElement('div');
    contentDiv.className = `max-w-xs md:max-w-md lg:max-w-lg p-3 rounded-xl shadow-md ${bgColor} ${textColor}`;
    
    const senderSpan = document.createElement('span');
    senderSpan.className = `font-bold ${type === 'self' ? 'text-indigo-200' : 'text-indigo-600'} block mb-0.5`;
    senderSpan.textContent = sender;

    const messageP = document.createElement('p');
    messageP.textContent = message;

    contentDiv.appendChild(senderSpan);
    contentDiv.appendChild(messageP);

    msgDiv.appendChild(msgDiv);
    
    msgWindow.scrollTop = msgWindow.scrollHeight;
}


// --- Xử lý Sự kiện ---
document.addEventListener('DOMContentLoaded', () => {
    registerBtn.addEventListener('click', registerPeer);
    refreshBtn.addEventListener('click', refreshPeers);
    selectedPeerUI = document.getElementById('selected-peer'); // <-- MỚI

    log('Trang Chat đã tải. Tự động đăng ký Peer...', 'info');
    registerPeer(); 
});