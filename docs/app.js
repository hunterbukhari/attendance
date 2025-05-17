const API_BASE = 'https://attendance-hbe3.onrender.com';

// دالة fetch موحدة لتمرير الكوكيز
const defaultFetch = (url, opts = {}) =>
  fetch(url, {
    credentials: 'include',  // <— مهم جداً لتمرير session_id الكوكي
    ...opts
  });

// تسجيل الدخول
document.getElementById('btn-login').onclick = async () => {
  const nid = document.getElementById('nid').value;
  const pwd = document.getElementById('pwd').value;

  try {
    const res = await defaultFetch(`${API_BASE}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ national_id: nid, password: pwd })
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || data.message);

    // نجاح
    document.getElementById('login-section').style.display = 'none';
    document.getElementById('app-section').style.display   = 'block';
  } catch (e) {
    document.getElementById('login-msg').textContent = e.message;
  }
};

// مثال على Check-In (بنفس الطريقة لباقي الطلبات)
document.getElementById('btn-checkin').onclick = async () => {
  const { latitude, longitude } = await getCurrentLocation();
  try {
    const res = await defaultFetch(`${API_BASE}/attendance/check-in`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ latitude, longitude })
    });
    const data = await res.json();
    document.getElementById('attendance-msg').style.color = res.ok ? 'green' : 'red';
    document.getElementById('attendance-msg').textContent = data.message || data.detail;
  } catch (e) {
    document.getElementById('attendance-msg').style.color = 'red';
    document.getElementById('attendance-msg').textContent = e.message;
  }
};
