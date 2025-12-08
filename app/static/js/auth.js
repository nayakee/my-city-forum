// API конфигурация
const API_BASE_URL = window.location.origin;
const API = {
    LOGIN: '/auth/login',
    REGISTER: '/auth/register',
    ME: '/auth/me'
};

// Вспомогательные функции
function disableButton(button, text = 'Загрузка...') {
    if (!button) return;
    button.dataset.originalText = button.innerHTML;
    button.innerHTML = `<i class="fas fa-spinner fa-spin"></i> ${text}`;
    button.disabled = true;
}

function enableButton(button) {
    if (!button || !button.dataset.originalText) return;
    button.innerHTML = button.dataset.originalText;
    button.disabled = false;
}

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', function() {
    console.log('Страница авторизации загружена');
    
    // Проверяем авторизацию
    checkAuth();
    
    // Настраиваем обработчики
    setupAuthForms();
});

// Проверка авторизации
async function checkAuth() {
    try {
        const response = await fetch(API_BASE_URL + API.ME, {
            method: 'GET',
            credentials: 'include'
        });
        
        if (response.ok) {
            window.location.href = '/';
        }
    } catch (error) {
        console.log('Пользователь не авторизован');
    }
}

// Настройка обработчиков форм
function setupAuthForms() {
    // Форма входа
    const loginForm = document.getElementById('login-form');
    if (loginForm) {
        loginForm.addEventListener('submit', handleLogin);
    }
    
    // Форма регистрации
    const registerForm = document.getElementById('register-form');
    if (registerForm) {
        registerForm.addEventListener('submit', handleRegister);
    }
}

// Обработка входа
async function handleLogin(e) {
    e.preventDefault();
    
    const form = e.target;
    const submitBtn = form.querySelector('button[type="submit"]');
    
    const email = document.getElementById('login-email').value.trim();
    const password = document.getElementById('login-password').value;
    
    // Валидация
    if (!email || !password) {
        notify.error('Заполните все поля');
        return;
    }
    
    const loginData = {
        email: email,
        password: password
    };
    
    // Показываем загрузку
    disableButton(submitBtn, 'Вход...');
    
    try {
        const response = await fetch(API_BASE_URL + API.LOGIN, {
            method: 'POST',
            headers: {
                'accept': 'application/json',
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(loginData),
            credentials: 'include'
        });
        
        const responseText = await response.text();
        let data;
        
        try {
            data = responseText ? JSON.parse(responseText) : {};
        } catch (e) {
            console.error('Ошибка парсинга JSON:', e);
            data = { detail: responseText || 'Некорректный ответ сервера' };
        }
        
        if (response.ok) {
            notify.success('Успешный вход!');
            setTimeout(() => window.location.href = '/', 1000);
        } else {
            // Извлекаем сообщение об ошибке
            let errorMessage = 'Ошибка авторизации';
            if (data.detail) errorMessage = data.detail;
            else if (data.message) errorMessage = data.message;
            else if (typeof data === 'string') errorMessage = data;
            
            notify.error(errorMessage);
        }
        
    } catch (error) {
        console.error('Ошибка сети:', error);
        notify.error('Ошибка подключения к серверу');
    } finally {
        enableButton(submitBtn);
    }
}

// Обработка регистрации
async function handleRegister(e) {
    e.preventDefault();
    
    const form = e.target;
    const submitBtn = form.querySelector('button[type="submit"]');
    
    const name = document.getElementById('register-name').value.trim();
    const email = document.getElementById('register-email').value.trim();
    const password = document.getElementById('register-password').value;
    const confirmPassword = document.getElementById('confirm-password').value;
    
    // Валидация
    if (!name || !email || !password || !confirmPassword) {
        notify.error('Заполните все поля');
        return;
    }
    
    if (password !== confirmPassword) {
        notify.error('Пароли не совпадают');
        return;
    }
    
    if (password.length < 8) {
        notify.error('Пароль должен быть не менее 8 символов');
        return;
    }
    
    // Проверка email
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
        notify.error('Введите корректный email адрес');
        return;
    }
    
    const userData = {
        name: name,
        email: email,
        password: password
    };
    
    // Показываем загрузку
    disableButton(submitBtn, 'Регистрация...');
    
    try {
        const response = await fetch(API_BASE_URL + API.REGISTER, {
            method: 'POST',
            headers: {
                'accept': 'application/json',
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(userData)
        });
        
        const responseText = await response.text();
        let data;
        
        try {
            data = responseText ? JSON.parse(responseText) : {};
        } catch (e) {
            console.error('Ошибка парсинга JSON:', e);
            data = { detail: responseText || 'Некорректный ответ сервера' };
        }
        
        if (response.ok) {
            notify.success('Регистрация успешна! Теперь войдите в систему.');
            // Переключаем на форму входа и очищаем
            document.getElementById('login-tab').click();
            form.reset();
        } else {
            // Извлекаем сообщение об ошибке
            let errorMessage = 'Ошибка регистрации';
            if (data.detail) errorMessage = data.detail;
            else if (data.message) errorMessage = data.message;
            else if (data.error) errorMessage = data.error;
            else if (typeof data === 'string') errorMessage = data;
            else if (response.status === 409) errorMessage = 'Пользователь с таким email уже существует';
            
            notify.error(errorMessage);
        }
        
    } catch (error) {
        console.error('Ошибка сети:', error);
        notify.error('Ошибка подключения к серверу');
    } finally {
        enableButton(submitBtn);
    }
}