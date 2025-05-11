const API_BASE = 'https://attendance-hbe3.onrender.com';  // رابط خدمتك على Render

// عناصر الـ DOM
const loginSec    = document.getElementById('login-section');
const appSec      = document.getElementById('app-section');
const msgLogin    = document.getElementById('login-msg');
const msgAttend   = document.getElementById('attendance-msg');
const msgExport   = document.getElementById('export-msg');       // (إن أردت رسالة مخصصة للتصدير)
const msgChange   = document.getElementById('change-msg');

// تسجيل الدخول
document.getElementById('btn-login').onclick = async () => {
  msgLogin.textContent = '';
  const nid = document.getElementById('nid').value;
  const pwd = document.getElementById('pwd').value;
  try {
    const res = await fetch(`${API_BASE}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ national_id: nid, password: pwd })
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || 'خطأ في الدخول');
    localStorage.setItem('token', data.access_token);
    loginSec.style.display = 'none';
    appSec.style.display   = 'block';
  } catch (e) {
    msgLogin.textContent = e.message;
  }
};

// تسجيل حضور (Check-In)
document.getElementById('btn-checkin').onclick = async () => {
  msgAttend.textContent = '';
  const token = localStorage.getItem('token');
  try {
    const res = await fetch(`${API_BASE}/attendance/check-in`, {
      method: 'POST',
      headers: { 'Authorization': 'Bearer ' + token }
    });
    const data = await res.json();
    msgAttend.style.color = res.ok ? 'green' : 'red';
    msgAttend.textContent = data.message || data.detail;
  } catch (e) {
    msgAttend.style.color = 'red';
    msgAttend.textContent = e.message;
  }
};

// تسجيل انصراف (Check-Out)
document.getElementById('btn-checkout').onclick = async () => {
  msgAttend.textContent = '';
  const token = localStorage.getItem('token');
  try {
    const res = await fetch(`${API_BASE}/attendance/check-out`, {
      method: 'POST',
      headers: { 'Authorization': 'Bearer ' + token }
    });
    const data = await res.json();
    msgAttend.style.color = res.ok ? 'green' : 'red';
    msgAttend.textContent = data.message || data.detail;
  } catch (e) {
    msgAttend.style.color = 'red';
    msgAttend.textContent = e.message;
  }
};

// تصدير تقرير Excel
document.getElementById('btn-export').onclick = () => {
  const token = localStorage.getItem('token');
  const start = document.getElementById('start').value;
  const end   = document.getElementById('end').value;
  if (!start || !end) return alert('حدد الفترة أولاً');
  const url = `${API_BASE}/export/excel?start_date=${start}&end_date=${end}`;
  fetch(url, {
    headers: { 'Authorization': 'Bearer ' + token }
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

// تغيير كلمة المرور
document.getElementById('btn-change-pwd').onclick = async () => {
  msgChange.textContent = '';
  const token   = localStorage.getItem('token');
  const oldPwd  = document.getElementById('old-pwd').value;
  const newPwd  = document.getElementById('new-pwd').value;
  try {
    const res = await fetch(`${API_BASE}/auth/change-password`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + token
      },
      body: JSON.stringify({ old_password: oldPwd, new_password: newPwd })
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || 'فشل تغيير كلمة المرور');
    msgChange.style.color = 'green';
    msgChange.textContent = data.message;
    // تفريغ الحقول
    document.getElementById('old-pwd').value = '';
    document.getElementById('new-pwd').value = '';
  } catch (e) {
    msgChange.style.color = 'red';
    msgChange.textContent = e.message;
  }
};
