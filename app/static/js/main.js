// ====================================================
// ОСНОВНОЙ КОД ГЛАВНОЙ СТРАНИЦЫ
// ====================================================

// Глобальное состояние приложения
const AppState = {
    user: null,
    currentPage: 1,
    totalPages: 1,
    filterTheme: 'all'
};

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', function() {
    console.log('Главная страница загружена. Инициализация...');
    
    // Проверяем авторизацию
    checkAuth();
    
    // Инициализируем функционал страницы
    initPageFunctionality();
    
    // Обновляем статистику
    updateThemeStatsOnce();
});

// Проверка авторизации
function checkAuth() {
    const user = getCurrentUser();
    const guestButtons = document.getElementById('guest-buttons');
    const userMenu = document.getElementById('user-menu');
    
    if (user) {
        if (guestButtons) guestButtons.style.display = 'none';
        if (userMenu) userMenu.style.display = 'block';
        const username = document.getElementById('username');
        if (username) username.textContent = user.name || 'Пользователь';
    } else {
        if (guestButtons) guestButtons.style.display = 'flex';
        if (userMenu) userMenu.style.display = 'none';
    }
}

// Получение текущего пользователя из localStorage
function getCurrentUser() {
    try {
        const userData = localStorage.getItem('user');
        if (userData) {
            return JSON.parse(userData);
        }
    } catch (e) {
        console.error('Ошибка при получении данных пользователя:', e);
    }
    return null;
}

// Инициализация функционала страницы
function initPageFunctionality() {
    // 1. Фильтрация постов
    const filterButtons = document.querySelectorAll('.theme-filters-bar .theme-filter-btn');
    filterButtons.forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            
            filterButtons.forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            
            const theme = this.getAttribute('data-theme');
            AppState.filterTheme = theme;
            filterPosts(theme);
        });
    });
    
    // 2. Форма создания поста
    const showCreatePostBtn = document.getElementById('show-create-post');
    const createPostCard = document.getElementById('create-post-card');
    const cancelPostBtn = document.getElementById('cancel-post');
    
    if (showCreatePostBtn && createPostCard) {
        showCreatePostBtn.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            
            // Проверяем авторизацию
            const currentUser = getCurrentUser();
            if (!currentUser) {
                const guestNotice = document.getElementById('guest-notice');
                if (guestNotice) {
                    guestNotice.style.display = 'block';
                    setTimeout(() => {
                        guestNotice.style.display = 'none';
                    }, 5000);
                }
                return;
            }
            
            createPostCard.style.display = 'block';
            showCreatePostBtn.style.display = 'none';
        });
        
        if (cancelPostBtn) {
            cancelPostBtn.addEventListener('click', function(e) {
                e.preventDefault();
                e.stopPropagation();
                
                createPostCard.style.display = 'none';
                showCreatePostBtn.style.display = 'inline-flex';
                resetPostForm();
            });
        }
    }
    
    // 3. Выбор темы в форме
    const themeButtons = document.querySelectorAll('.theme-selection-buttons .theme-btn');
    const postThemeInput = document.getElementById('post-theme');
    const postThemeNameInput = document.getElementById('post-theme-name');
    
    themeButtons.forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            
            themeButtons.forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            
            if (postThemeInput) postThemeInput.value = this.getAttribute('data-theme-id');
            if (postThemeNameInput) postThemeNameInput.value = this.getAttribute('data-theme-name');
        });
    });
    
    // 4. Отправка формы создания поста
    const createPostForm = document.getElementById('create-post-form');
    if (createPostForm) {
        createPostForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            await submitPostForm();
        });
    }
    
    // 5. Голосование
    initVoteButtons();
    
    // 6. Кнопка выхода
    const logoutBtn = document.getElementById('logout-btn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', handleLogout);
    }
}

// Фильтрация постов по теме
function filterPosts(theme) {
    const posts = document.querySelectorAll('.post');
    posts.forEach(post => {
        const postTheme = post.getAttribute('data-theme');
        if (theme === 'all' || postTheme === theme) {
            post.style.display = 'block';
        } else {
            post.style.display = 'none';
        }
    });
    updateThemeStatsOnce();
}

// Сброс формы создания поста
function resetPostForm() {
    const form = document.getElementById('create-post-form');
    if (form) form.reset();
    
    const themeButtons = document.querySelectorAll('.theme-selection-buttons .theme-btn');
    const postThemeInput = document.getElementById('post-theme');
    const postThemeNameInput = document.getElementById('post-theme-name');
    
    if (themeButtons.length > 0) {
        themeButtons.forEach(b => b.classList.remove('active'));
        themeButtons[0].classList.add('active');
        if (postThemeInput) postThemeInput.value = themeButtons[0].getAttribute('data-theme-id');
        if (postThemeNameInput) postThemeNameInput.value = themeButtons[0].getAttribute('data-theme-name');
    }
}

// Отправка формы создания поста
async function submitPostForm() {
    const submitBtn = document.getElementById('submit-post-btn');
    const loadingIndicator = document.getElementById('loading-indicator');
    
    if (submitBtn) submitBtn.disabled = true;
    if (loadingIndicator) loadingIndicator.style.display = 'block';
    
    // Имитация отправки
    setTimeout(() => {
        if (submitBtn) submitBtn.disabled = false;
        if (loadingIndicator) loadingIndicator.style.display = 'none';
        
        const successMessage = document.getElementById('post-success-message');
        const createPostCard = document.getElementById('create-post-card');
        const showCreatePostBtn = document.getElementById('show-create-post');
        
        if (successMessage) {
            successMessage.style.display = 'flex';
            setTimeout(() => {
                successMessage.style.display = 'none';
            }, 3000);
        }
        
        if (createPostCard) createPostCard.style.display = 'none';
        if (showCreatePostBtn) showCreatePostBtn.style.display = 'inline-flex';
        
        resetPostForm();
        
        // Используем глобальную систему уведомлений
        if (window.notify) {
            window.notify.success('Пост успешно создан!');
        } else {
            alert('Пост успешно создан!');
        }
    }, 1000);
}

// Инициализация кнопок голосования
function initVoteButtons() {
    document.querySelectorAll('.vote-btn').forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            
            const isLike = this.classList.contains('like');
            const countSpan = this.querySelector('.vote-count');
            
            if (countSpan) {
                let count = parseInt(countSpan.textContent) || 0;
                countSpan.textContent = count + 1;
            }
            
            if (isLike) {
                this.classList.add('active-like');
            } else {
                this.classList.add('active-dislike');
            }
        });
    });
}

// Обновление статистики тем
function updateThemeStatsOnce() {
    const posts = document.querySelectorAll('.post');
    const counts = { news: 0, realestate: 0, job: 0, general: 0 };
    
    posts.forEach(post => {
        if (post.style.display !== 'none') {
            const theme = post.getAttribute('data-theme');
            if (counts.hasOwnProperty(theme)) {
                counts[theme]++;
            }
        }
    });
    
    const newsCount = document.getElementById('news-count');
    const realestateCount = document.getElementById('realestate-count');
    const jobCount = document.getElementById('job-count');
    
    if (newsCount) newsCount.textContent = `${counts.news} постов`;
    if (realestateCount) realestateCount.textContent = `${counts.realestate} постов`;
    if (jobCount) jobCount.textContent = `${counts.job} постов`;
}

// Обработка выхода
function handleLogout(e) {
    e.preventDefault();
    
    // Удаляем пользователя из localStorage
    localStorage.removeItem('user');
    
    // Показываем уведомление
    if (window.notify) {
        window.notify.success('Вы успешно вышли из системы');
    } else {
        alert('Вы успешно вышли из системы');
    }
    
    // Перезагружаем страницу через секунду
    setTimeout(() => {
        window.location.reload();
    }, 1000);
}

// Функция для комментариев
function showComments(postId) {
    console.log('Показать комментарии для поста:', postId);
    if (window.notify) {
        window.notify.info('Функция комментариев временно недоступна');
    } else {
        alert('Функция комментариев временно недоступна');
    }
}

console.log('main.js загружен');