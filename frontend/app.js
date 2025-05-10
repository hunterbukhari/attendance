const API_BASE = 'https://<your-service>.onrender.com';  // عدّل هذا إلى رابط خدمتك

// عناصر الـ DOM
const loginSec = document.getElementById('login-section');
const appSec   = document.getElementById('app-section');
const msgLogin = document.getElementById('login-msg');
const msgCheck = document.getElementById('checkin-msg');

document.getElementById('btn-login').onclick = async () => {
  msgLogin.textContent = '';
  const nid = document.getElementById('nid').value;
  const pwd = document.getElementById('pwd').value;
  try {
    const res = await fetch(`${API_BASE}/auth/login`, {
      method:'POST',
      headers:{ 'Content-Type':'application/json' },
      body: JSON.stringify({ national_id: nid, password: pwd })
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || 'خطأ في الدخول');
    localStorage.setItem('token', data.access_token);
    loginSec.style.display = 'none';
    appSec.style.display = 'block';
  } catch(e) {
    msgLogin.textContent = e.message;
  }
};

document.getElementById('btn-checkin').onclick = async () => {
  msgCheck.textContent = '';
  const token = localStorage.getItem('token');
  try {
    const res = await fetch(`${API_BASE}/attendance/check-in`, {
      method:'POST',
      headers:{ 'Authorization': 'Bearer '+token }
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || 'خطأ');
    msgCheck.style.color = 'green';
    msgCheck.textContent = data.message;
  } catch(e) {
    msgCheck.style.color = 'red';
    msgCheck.textContent = e.message;
  }
};

document.getElementById('btn-export').onclick = () => {
  const token = localStorage.getItem('token');
  const start = document.getElementById('start').value;
  const end   = document.getElementById('end').value;
  if (!start||!end) return alert('حدد الفترة أولاً');
  const url = `${API_BASE}/export/excel?start_date=${start}&end_date=${end}`;
  // ينشئ رابط تحميل مع Authorization
  fetch(url, {
    headers: { 'Authorization': 'Bearer '+token }
  })
  .then(res => {
    if (!res.ok) throw new Error('فشل التصدير');
    return res.blob();
  })
  .then(blob => {
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = `attendance_${start}_to_${end}.xlsx`;
    a.click();
  })
  .catch(e => alert(e.message));
};
