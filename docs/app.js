// API_BASE: رابط خدمتك على Render أو أي سيرفر تستضيف عليه الباك-اند
const API_BASE = 'https://attendance-hbe3.onrender.com';

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

// مراجع لعناصر الـ DOM
const loginSec  = document.getElementById('login-section');
const appSec    = document.getElementById('app-section');
const msgLogin  = document.getElementById('login-msg');
const msgCheck  = document.getElementById('attendance-msg');
const msgChange = document.getElementById('change-msg');
const msgExport = document.getElementById('export-msg');

// خيارات fetch عامة لإرسال الكوكيز
const fetchOpts = {
  credentials: 'include',           // لتمرير كوكيز الجلسة
  headers: { 'Content-Type': 'application/json' }
};

// --- تسجيل الدخول ---
document.getElementById('btn-login').onclick = async () => {
  msgLogin.textContent = '';
  const nid = document.getElementById('nid').value;
  const pwd = document.getElementById('pwd').value;

  try {
    const res = await fetch(`${API_BASE}/auth/login`, {
      ...fetchOpts,
      method: 'POST',
      body: JSON.stringify({ national_id: nid, password: pwd })
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || 'خطأ في الدخول');

    // حالياً لا نحتاج لحفظ أي توكن في localStorage
    loginSec.style.display = 'none';
    appSec.style.display   = 'block';
  } catch (e) {
    msgLogin.textContent = e.message;
  }
};

// --- تسجيل حضور (Check-In) مع GPS ---
document.getElementById('btn-checkin').onclick = async () => {
  msgCheck.textContent = '';
  try {
    const loc = await getCurrentLocation();
    const res = await fetch(`${API_BASE}/attendance/check-in`, {
      ...fetchOpts,
      method: 'POST',
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

// --- تسجيل انصراف (Check-Out) مع GPS ---
document.getElementById('btn-checkout').onclick = async () => {
  msgCheck.textContent = '';
  try {
    const loc = await getCurrentLocation();
    const res = await fetch(`${API_BASE}/attendance/check-out`, {
      ...fetchOpts,
      method: 'POST',
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

// --- تغيير كلمة المرور ---
document.getElementById('btn-change-pwd').onclick = async () => {
  msgChange.textContent = '';
  const oldPwd = document.getElementById('old-pwd').value;
  const newPwd = document.getElementById('new-pwd').value;

  try {
    const res = await fetch(`${API_BASE}/auth/change-password`, {
      ...fetchOpts,
      method: 'POST',
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

// --- تصدير تقرير Excel ---
document.getElementById('btn-export').onclick = async () => {
  msgExport.textContent = '';
  const start = document.getElementById('start').value;
  const end   = document.getElementById('end').value;
  if (!start || !end) {
    msgExport.style.color = 'red';
    return msgExport.textContent = 'حدد الفترة أولاً';
  }

  try {
    const res = await fetch(
      `${API_BASE}/export/excel?start_date=${start}&end_date=${end}`,
      { ...fetchOpts, method: 'GET' }
    );
    if (!res.ok) throw new Error('فشل التصدير');

    const blob = await res.blob();
    const a    = document.createElement('a');
    a.href     = URL.createObjectURL(blob);
    a.download = `attendance_${start}_to_${end}.xlsx`;
    a.click();

    msgExport.style.color = 'green';
    msgExport.textContent = 'تم تنزيل التقرير بنجاح';
  } catch (e) {
    msgExport.style.color = 'red';
    msgExport.textContent = e.message;
  }
};
