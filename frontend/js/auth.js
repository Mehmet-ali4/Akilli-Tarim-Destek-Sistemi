const AUTH_TOKEN_KEY = 'akilli_tarim_token';
const AUTH_USER_KEY = 'akilli_tarim_user';

function getToken() {
    return localStorage.getItem(AUTH_TOKEN_KEY);
}

function getUser() {
    try {
        return JSON.parse(localStorage.getItem(AUTH_USER_KEY));
    } catch {
        return null;
    }
}

function saveSession(token, kullanici) {
    localStorage.setItem(AUTH_TOKEN_KEY, token);
    localStorage.setItem(AUTH_USER_KEY, JSON.stringify(kullanici));
}

function clearSession() {
    localStorage.removeItem(AUTH_TOKEN_KEY);
    localStorage.removeItem(AUTH_USER_KEY);
}

function isLoggedIn() {
    return !!getToken();
}

async function authRequest(path, body) {
    const res = await fetch(`http://localhost:3000/api${path}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body)
    });
    const payload = await res.json();
    if (!res.ok) throw new Error(payload.message || 'İstek başarısız.');
    return payload;
}

async function login(email, sifre) {
    const payload = await authRequest('/auth/login', { email, sifre });
    saveSession(payload.data.token, payload.data.kullanici);
    return payload.data.kullanici;
}

async function register(adSoyad, email, sifre) {
    const payload = await authRequest('/auth/register', { ad_soyad: adSoyad, email, sifre });
    saveSession(payload.data.token, payload.data.kullanici);
    return payload.data.kullanici;
}

function logout() {
    clearSession();
    showAuthOverlay();
}

// ── UI ──────────────────────────────────────────────────────────────────────

function showAuthOverlay() {
    document.getElementById('auth-overlay').classList.remove('hidden');
    document.getElementById('app-content').classList.add('hidden');
    document.getElementById('user-bar').classList.add('hidden');
}

function hideAuthOverlay(kullanici) {
    document.getElementById('auth-overlay').classList.add('hidden');
    document.getElementById('app-content').classList.remove('hidden');
    renderUserBar(kullanici);
}

function renderUserBar(kullanici) {
    const bar = document.getElementById('user-bar');
    bar.classList.remove('hidden');
    document.getElementById('user-name').textContent = kullanici.ad_soyad;
}

function setAuthError(msg) {
    const el = document.getElementById('auth-error');
    el.textContent = msg;
    el.classList.remove('hidden');
}

function clearAuthError() {
    const el = document.getElementById('auth-error');
    el.textContent = '';
    el.classList.add('hidden');
}

function switchToLogin() {
    document.getElementById('register-panel').classList.add('hidden');
    document.getElementById('login-panel').classList.remove('hidden');
    clearAuthError();
}

function switchToRegister() {
    document.getElementById('login-panel').classList.add('hidden');
    document.getElementById('register-panel').classList.remove('hidden');
    clearAuthError();
}

// ── Bootstrap ────────────────────────────────────────────────────────────────

document.addEventListener('DOMContentLoaded', () => {
    const loginForm = document.getElementById('login-form');
    const registerForm = document.getElementById('register-form');
    const logoutBtn = document.getElementById('logout-btn');
    const toRegisterLink = document.getElementById('to-register');
    const toLoginLink = document.getElementById('to-login');

    toRegisterLink.addEventListener('click', (e) => { e.preventDefault(); switchToRegister(); });
    toLoginLink.addEventListener('click', (e) => { e.preventDefault(); switchToLogin(); });
    logoutBtn.addEventListener('click', logout);

    loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        clearAuthError();
        const btn = loginForm.querySelector('button[type=submit]');
        btn.disabled = true;
        try {
            const kullanici = await login(
                loginForm.email.value.trim(),
                loginForm.sifre.value
            );
            hideAuthOverlay(kullanici);
        } catch (err) {
            setAuthError(err.message);
        } finally {
            btn.disabled = false;
        }
    });

    registerForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        clearAuthError();
        const btn = registerForm.querySelector('button[type=submit]');
        btn.disabled = true;
        try {
            const kullanici = await register(
                registerForm.ad_soyad.value.trim(),
                registerForm.email.value.trim(),
                registerForm.sifre.value
            );
            hideAuthOverlay(kullanici);
        } catch (err) {
            setAuthError(err.message);
        } finally {
            btn.disabled = false;
        }
    });

    // Sayfa yüklenince oturum kontrolü
    if (isLoggedIn()) {
        hideAuthOverlay(getUser());
    } else {
        showAuthOverlay();
    }
});
