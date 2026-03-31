// --- Cấu hình API Base ---
// Luôn sử dụng Host và Port mà trang hiện tại đang chạy (Proxy Port 8888)
const PROXY_BASE_URL = window.location.protocol + "//" + "10.230.155.99:8888";

// --- Khai báo biến UI ---
var Gosignin_btn = document.getElementById("GoSignin_btn");
var signin_btn = document.getElementById("signin_btn");
var login_btn = document.getElementById("login_btn");
var back_btn = document.getElementById("back_btn");
// Các biến inputCode và checkCode_btn không được dùng trong code này

function checkValidation(name, pass) {
  // Đã sửa: Chỉ kiểm tra name và pass (email sẽ kiểm tra riêng nếu cần)
  if (!name || !pass) {
    alert("Vui lòng điền đầy đủ tên đăng nhập và mật khẩu.");
    return false;
  }
  return true;
}

function goSignin() {
  document.getElementById("box_login").style.display = "none";
  document.getElementById("box_signin").style.display = "flex";
}
function goLogin() {
  document.getElementById("box_signin").style.display = "none";
  document.getElementById("box_login").style.display = "flex";
}

// --- 1. Hàm Login (Đã sửa sang fetch) ---
async function login() {
  const usernameInput = document.getElementById("name");
  const passwordInput = document.getElementById("pass");
  
  const username = usernameInput.value;
  const password = passwordInput.value;
  
  // Sửa: Hàm checkValidation chỉ cần 2 tham số
  if (!checkValidation(username, password)) {
    usernameInput.value = "";
    passwordInput.value = "";
    return;
  }
  
  // URL GỌI PROXY: Phải gọi /login (đúng theo app.py)
  const url = `${PROXY_BASE_URL}/login`; 
  
  try {
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      credentials: 'include',
      // Gửi body dưới dạng JSON (đúng theo app.py)
      body: JSON.stringify({
        username: username,
        password: password 
      })
    });
    
    const data = await response.json(); 
    
    if (response.ok) {
        // Đăng nhập thành công (Backend 9001 trả về Set-Cookie: auth=true)
        alert("Đăng nhập thành công!");
        sessionStorage.setItem('username', username);
        // *** SỬA LỖI CHUYỂN HƯỚNG TẠI ĐÂY ***
        // Phải chuyển hướng đến /chatUI.html (file mà App 9001 đang phục vụ)
        window.location.href = `${PROXY_BASE_URL}/messenger.html`;
        //window.location.href = `${PROXY_BASE_URL}/chatUI.html`; 
        
    } else {

        alert("Đăng nhập thất bại: " + (data.message || "Sai tên đăng nhập hoặc mật khẩu."));
        usernameInput.value = "";
        passwordInput.value = "";
    }
  } catch (error) {
      console.error("Lỗi mạng/API:", error);
      alert("Lỗi kết nối đến server. (Có thể do CORS hoặc server 9001 chưa chạy)");
  }
}

// --- 2. Hàm Sign-in  ---
async function signin() {
  const usernameInput = document.getElementById("nameSign");
  const passwordInput = document.getElementById("passSign");

  
  const username = usernameInput.value;
  const password = passwordInput.value;

  if (!checkValidation(username, password)) {
    usernameInput.value = "";
    passwordInput.value = "";

    return;
  }
  
  // URL GỌI PROXY: Phải gọi /register (đúng theo app.py)
  const url = `${PROXY_BASE_URL}/register`;
  
  try {
    const response = await fetch(url, {
      method: 'POST',
      headers:{
        'Content-Type':'application/json',
      },
      body: JSON.stringify({
        username: username,
        password: password
        // email: email // Gửi email nếu app.py yêu cầu
      })
    });
    
    const data = await response.json();
    
    if (response.ok) {
      alert("Đăng ký thành công!");
      goLogin(); // Quay lại màn hình đăng nhập
    } else {
       // Lỗi (VíV dụ: 409 Conflict - User đã tồn tại)
      alert("Đăng ký thất bại: " + (data.message || "Tài khoản đã tồn tại."));
    }
  } catch (error) {
      console.error("Lỗi mạng/API:", error);
      alert("Lỗi kết nối đến server.");
  }
}

// --- Xử lý Sự kiện ---
back_btn.addEventListener("click", goLogin);
login_btn.addEventListener("click", login);
Gosignin_btn.addEventListener("click", goSignin);
signin_btn.addEventListener("click", signin);


