const API_BASE = 'https://attendance-hbe3.onrender.com';  // عدّل هذا إلى رابط خدمتك

// دالة للحصول على الموقع الجغرافي
function getCurrentLocation() {
  return new Promise((resolve, reject) => {
    if (!navigator.geolocation) {
      return reject(new Error('المتصفح لا يدعم تحديد الموقع'));
    }
    navigator.geolocation.getCurrentPosition(
      pos => resolve({
        latitude:  pos.coords.latitude,
        longitude: pos.coords.longitude
      }),
      err => reject(new Error('تعذّر الحصول على الموقع: ' + err.message))
    );
  });
}

// عناصر الـ DOM
const loginSec   = document.getElementById('login-section');
const appSec     = document.getElementById('app-section');
const msgLogin   = document.getElementById('login-msg');
const msgCheck   = document.getElementById('attendance-msg');
const msgChange  = document.getElementById('change-msg');
const msgExport  = document.getElementById('export-msg');   // عنصر الرسالة للتصدير

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

// تسجيل حضور (Check-In) مع GPS
document.getElementById('btn-checkin').onclick = async () => {
  msgCheck.textContent = '';
  try {
    const loc = await getCurrentLocation();
    const token = localStorage.getItem('token');
    const res = await fetch(`${API_BASE}/attendance/check-in`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + token
      },
      body: JSON.stringify(loc)
    });
    const data = await res.json();
    msgCheck.style.color = res.ok ? 'green' : 'red';
    msgCheck.textContent = data.message || data.detail;
  } catch (e) {
    msgCheck.style.color = 'red';
    msgCheck.textContent = e.message;
  }
};

// تسجيل انصراف (Check-Out) مع GPS
document.getElementById('btn-checkout').onclick = async () => {
  msgCheck.textContent = '';
  try {
    const loc = await getCurrentLocation();
    const token = localStorage.getItem('token');
    const res = await fetch(`${API_BASE}/attendance/check-out`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + token
      },
      body: JSON.stringify(loc)
    });
    const data = await res.json();
    msgCheck.style.color = res.ok ? 'green' : 'red';
    msgCheck.textContent = data.message || data.detail;
  } catch (e) {
    msgCheck.style.color = 'red';
    msgCheck.textContent = e.message;
  }
};

// تصدير تقرير Excel
document.getElementById('btn-export').onclick = () => {
  msgExport.textContent = '';
  const token = localStorage.getItem('token');
  const start = document.getElementById('start').value;
  const end   = document.getElementById('end').value;
  if (!start || !end) {
    msgExport.style.color = 'red';
    return msgExport.textContent = 'حدد الفترة أولاً';
  }
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
    msgExport.style.color = 'green';
    msgExport.textContent = 'تم تنزيل التقرير بنجاح';
  })
  .catch(e => {
    msgExport.style.color = 'red';
    msgExport.textContent = e.message;
  });
};

// تغيير كلمة المرور
document.getElementById('btn-change-pwd').onclick = async () => {
  msgChange.textContent = '';
  const token  = localStorage.getItem('token');
  const oldPwd = document.getElementById('old-pwd').value;
  const newPwd = document.getElementById('new-pwd').value;
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
    document.getElementById('old-pwd').value = '';
    document.getElementById('new-pwd').value = '';
  } catch (e) {
    msgChange.style.color = 'red';
    msgChange.textContent = e.message;
  }
};
