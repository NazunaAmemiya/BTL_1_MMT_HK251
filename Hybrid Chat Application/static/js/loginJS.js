var Gosignin_btn = document.getElementById("GoSignin_btn");
var signin_btn = document.getElementById("signin_btn");
var login_btn = document.getElementById("login_btn");
var back_btn = document.getElementById("back_btn");
var inputCode = document.getElementById("inputCode");
var checkCode_btn = document.getElementById("checkCode_btn");

function checkValidation(name, pass, email) {
  if (!name || !pass || !email) {
    alert("Please fill in all fields.");
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
function showCheckCode() {
  document.getElementById("box_signin").style.display = "none";
  document.getElementById("box_checkCode").style.display = "flex";
}
function hideCheckCode() {
  document.getElementById("box_checkCode").style.display = "none";
}

async function login() {
  const username = document.getElementById("name");
  const password = document.getElementById("pass");
  if (!checkValidation(username.value, password.value, "ok")) {
    username.value = "";
    password.value = "";
    return;
  }
  $.ajax({
    url: "/login",
    method: "POST",
    data: {
      username: username.value,
      password: password.value,
    },
    
    xhrFields: {
      withCredentials: true,
    },

    success: function (data, textStatus, jqXHR) {
        alert("Server Task 1 trả về 200 OK? (Lỗi logic)");
    },
    error: function (jqXHR, textStatus, errorThrown) {
        
        if (jqXHR.status == 302) {
            alert("Login Task 1 Thành Công! (Server trả 302). Đang chuyển hướng...");  
            window.location.href = "/index.html"; 
        
        } else {
            const errorMessage = jqXHR.responseJSON ? jqXHR.responseJSON.message : "Login failed. Please try again.";
            alert(errorMessage);
            username.value = "";
            password.value = "";
        }
    },
  });
}

back_btn.addEventListener("click", goLogin);
login_btn.addEventListener("click", login);
Gosignin_btn.addEventListener("click", goSignin);
signin_btn.addEventListener("click", signin);
