// API конфигурация
const API_BASE_URL = window.location.origin;
const API = {
    LOGIN: '/auth/login',
    REGISTER: '/auth/register',
    ME: '/auth/me'
};

// Вспомогательные функции

// Вспомогательная функция для проверки необходимости автоматического выхода
function checkResponseForLogout(response) {
    // Проверяем, содержит ли ответ флаг logout_required
    if (response.headers.get('content-type')?.includes('application/json')) {
        return response.clone().json().then(data => {
            if (data.logout_required) {
                // Перенаправляем на страницу авторизации при истечении токена
                window.location.href = '/web/auth';
                return true;
            }
            return false;
        }).catch(error => {
            console.error('Ошибка при проверке ответа на logout_required:', error);
            return false;
        });
    } else {
        return Promise.resolve(false);
    }
}

// Вспомогательная функция для выполнения fetch запроса с проверкой на истечение токена
async function fetchWithTokenCheck(url, options = {}) {
    const response = await fetch(url, {
        credentials: 'include',
        ...options
    });
    
    // Проверяем, не требуется ли автоматический выход
    const shouldLogout = await checkResponseForLogout(response);
    if (shouldLogout) {
        return null; // Прерываем выполнение, так как пользователь уже вышел
    }
    
    return response;
}

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
    
    // Настраиваем обработчики
    setupAuthForms();
});
// Проверка авторизации
async function checkAuth() {
    try {
        const response = await fetchWithTokenCheck(API_BASE_URL + API.ME, {
            method: 'GET'
        });

        // Если токен истек, response будет null и пользователь уже перенаправлен
        if (!response) {
            return; // Прерываем выполнение, так как пользователь уже вышел
        }
        
        if (response.ok) {
            // Если пользователь уже авторизован, НЕ перенаправляем с страницы авторизации
            // Пусть пользователь сам решает, хочет ли он остаться или перейти на главную
            const userData = await response.json();
            // Сохраняем данные пользователя в localStorage для других страниц
            localStorage.setItem('user', JSON.stringify(userData));
            console.log('Пользователь уже авторизован, но остается на странице авторизации');
        } else {
            // Если пользователь не авторизован (ожидаемый сценарий для страницы авторизации)
            // просто продолжаем работу без перенаправления
            // Удаляем старые данные пользователя из localStorage
            localStorage.removeItem('user');
            console.log('Пользователь не авторизован - это ожидаемое поведение на странице авторизации');
        }
    } catch (error) {
        // Обработка сетевых ошибок
        console.log('Ошибка сети при проверке авторизации:', error);
        // Удаляем старые данные пользователя из localStorage при ошибке
        localStorage.removeItem('user');
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
    if (!email || email.trim() === '') {
        notify.error('Введите email');
        return;
    }
    
    if (!password) {
        notify.error('Введите пароль');
        return;
    }
    
    const loginData = {
        email: email,
        password: password
    };
    
    // Показываем загрузку
    disableButton(submitBtn, 'Вход...');
    try {
        const response = await fetchWithTokenCheck(API_BASE_URL + API.LOGIN, {
            method: 'POST',
            headers: {
                'accept': 'application/json',
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(loginData)
        });

        // Если токен истек, response будет null и пользователь уже вышел
        if (!response) {
            return; // Прерываем выполнение, так как пользователь уже вышел
        }
        
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
            // После успешного входа обновляем информацию о пользователе в localStorage
            // Вызываем checkAuth для получения и сохранения данных пользователя
            setTimeout(async () => {
                await checkAuth();  // Обновляем данные пользователя в localStorage
                window.location.href = '/';  // Перенаправляем на главную
            }, 1000);
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
    if (!name || name.trim() === '') {
        notify.error('Введите имя');
        return;
    }
    
    if (!email || email.trim() === '') {
        notify.error('Введите email');
        return;
    }
    
    if (!password) {
        notify.error('Введите пароль');
        return;
    }
    
    if (!confirmPassword) {
        notify.error('Подтвердите пароль');
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
        const response = await fetchWithTokenCheck(API_BASE_URL + API.REGISTER, {
            method: 'POST',
            headers: {
                'accept': 'application/json',
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(userData)
        });

        // Если токен истек, response будет null и пользователь уже вышел
        if (!response) {
            return; // Прерываем выполнение, так как пользователь уже вышел
        }
        
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
            // Удаляем старые данные пользователя из localStorage после регистрации
            localStorage.removeItem('user');
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