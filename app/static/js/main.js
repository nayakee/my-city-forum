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
        
        // Обновляем аватар пользователя
        const userAvatar = document.getElementById('user-avatar');
        if (userAvatar) {
            if (user.name) {
                // Показываем инициалы пользователя вместо изображения
                userAvatar.style.display = 'none'; // Скрываем img
                // Создаем или обновляем элемент с инициалами, если он не существует
                let initialsElement = userAvatar.nextElementSibling;
                if (!initialsElement || !initialsElement.classList.contains('user-initials')) {
                    // Создаем элемент с инициалами
                    initialsElement = document.createElement('div');
                    initialsElement.className = 'post-avatar user-initials';
                    initialsElement.style.cssText = `
                        width: 40px;
                        height: 40px;
                        border-radius: 50%;
                        background: linear-gradient(135deg, #2e7d32 0%, #4caf50 100%);
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        color: white;
                        font-weight: bold;
                        font-size: 16px;
                        margin-right: 8px;
                    `;
                    userAvatar.parentNode.insertBefore(initialsElement, userAvatar.nextSibling);
                }
                initialsElement.textContent = user.name.substring(0, 2).toUpperCase();
                initialsElement.style.display = 'flex';
            } else {
                // Если нет имени, показываем стандартный аватар
                userAvatar.style.display = 'block';
                userAvatar.src = `https://ui-avatars.com/api/?name=${encodeURIComponent(user.name || 'Пользователь')}&background=2e7d32&color=fff`;
            }
        }
    } else {
        if (guestButtons) guestButtons.style.display = 'flex';
        if (userMenu) userMenu.style.display = 'none';
        
        // Сбрасываем аватар пользователя
        const userAvatar = document.getElementById('user-avatar');
        if (userAvatar) {
            userAvatar.style.display = 'block';
            userAvatar.src = '';
            // Удаляем элемент с инициалами, если он существует
            const initialsElement = userAvatar.nextElementSibling;
            if (initialsElement && initialsElement.classList.contains('user-initials')) {
                initialsElement.remove();
            }
        }
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
    // Инициализация фильтрации
    initFilters();
    
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
        console.log('Форма создания поста найдена, добавляем обработчик');
        createPostForm.addEventListener('submit', async function(e) {
            console.log('Событие submit формы перехвачено');
            e.preventDefault();
            await submitPostForm();
        });
    } else {
        console.error('Форма создания поста не найдена');
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
        
        // Преобразуем theme к формату, используемому в постах
        let normalizedTheme = theme;
        if (theme === 'news') normalizedTheme = 'новости';
        else if (theme === 'realestate') normalizedTheme = 'недвижимость';
        else if (theme === 'job') normalizedTheme = 'работа';
        
        if (theme === 'all' || postTheme === normalizedTheme) {
            post.style.display = 'block';
        } else {
            post.style.display = 'none';
        }
    });
    updateThemeStatsOnce();
}

// Инициализация фильтрации при загрузке страницы
function initFilters() {
    // Убедимся, что все посты изначально видны
    const posts = document.querySelectorAll('.post');
    posts.forEach(post => {
        post.style.display = 'block';
    });
    
    // Установим начальный активный фильтр
    const allFilterBtn = document.querySelector('.theme-filters-bar .theme-filter-btn[data-theme="all"]');
    if (allFilterBtn) {
        // Снимаем активный класс со всех кнопок
        document.querySelectorAll('.theme-filters-bar .theme-filter-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        // Устанавливаем активным фильтр "Все"
        allFilterBtn.classList.add('active');
    }
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
    const titleInput = document.getElementById('post-title');
    const contentInput = document.getElementById('post-content');
    const themeInput = document.getElementById('post-theme');
    const themeNameInput = document.getElementById('post-theme-name');
    
    console.log('Попытка создания поста...');
    
    if (submitBtn) submitBtn.disabled = true;
    if (loadingIndicator) loadingIndicator.style.display = 'block';
    
    try {
        // Получаем значения из формы
        const title = titleInput.value.trim();
        const content = contentInput.value.trim();
        const themeId = themeInput.value;
        const themeName = themeNameInput.value;
        
        console.log('Данные формы:', { title, content, themeId, themeName });
        
        // Проверяем, все ли обязательные поля заполнены
        if (!title || !content || !themeId) {
            throw new Error('Пожалуйста, заполните все обязательные поля');
        }
        
        // Подготовляем данные для отправки
        const postData = {
            header: title,
            body: content,
            theme_id: parseInt(themeId),
            is_published: true
        };
        
        console.log('Отправляемые данные:', postData);
        
        // Отправляем запрос на сервер (используем v2 API)
        // Используем credentials: 'include' для отправки куки с токеном аутентификации
        const response = await fetch('/api/v2/posts', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(postData),
            credentials: 'include' // Включаем куки в запрос
        });
        
        console.log('Ответ от сервера:', response);
        
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({ message: 'Неизвестная ошибка' }));
            throw new Error(errorData.message || `Ошибка сервера: ${response.status}`);
        }
        
        const result = await response.json();
        console.log('Результат от сервера:', result);
        
        if (result.status === 'OK') {
            // Показываем сообщение об успехе
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
            
            // Обновляем ленту постов
            await loadPosts();
            
            // Используем глобальную систему уведомлений
            if (window.notify) {
                window.notify.success('Пост успешно создан!');
            } else {
                alert('Пост успешно создан!');
            }
        } else {
            throw new Error(result.message || 'Неизвестная ошибка при создании поста');
        }
    } catch (error) {
        console.error('Ошибка при создании поста:', error);
        
        // Показываем сообщение об ошибке
        if (window.notify) {
            window.notify.error(`Ошибка: ${error.message}`);
        } else {
            alert(`Ошибка: ${error.message}`);
        }
    } finally {
        if (submitBtn) submitBtn.disabled = false;
        if (loadingIndicator) loadingIndicator.style.display = 'none';
    }
}

// Функция для загрузки постов
async function loadPosts(themeId = null) {
    try {
        let url = '/api/v2/posts/detailed?page=1&limit=100';
        if (themeId && themeId !== 'all') {
            url += `&theme_id=${themeId}`;
        }
        
        const response = await fetch(url, {
            credentials: 'include'  // Включаем куки в запрос
        });
        if (!response.ok) {
            throw new Error(`Ошибка загрузки постов: ${response.status}`);
        }
        
        const posts = await response.json();
        
        // Обновляем ленту постов
        updatePostsFeed(posts);
    } catch (error) {
        console.error('Ошибка при загрузке постов:', error);
    }
}

// Функция для обновления ленты постов
function updatePostsFeed(posts) {
    const postsFeed = document.getElementById('posts-feed');
    if (!postsFeed) return;
    
    // Очищаем текущую ленту
    postsFeed.innerHTML = '';
    
    if (posts.length === 0) {
        postsFeed.innerHTML = `
            <div class="no-posts-message">
                <p>Пока нет постов. Будьте первым, кто создаст пост!</p>
            </div>
        `;
        return;
    }
    
    // Добавляем посты в ленту
    posts.forEach(post => {
        const postElement = createPostElement(post);
        postsFeed.appendChild(postElement);
    });
    
    // Обновляем фильтрацию, если есть активный фильтр
    if (AppState.filterTheme && AppState.filterTheme !== 'all') {
        filterPosts(AppState.filterTheme);
    }
    
    // Инициализируем кнопки голосования для новых постов
    initVoteButtons();
}

// Функция для создания элемента поста
function createPostElement(post) {
    // Нормализуем названия тем для использования в CSS классах и атрибутах
    let themeClass = 'general';
    let themeData = 'general';
    if (post.theme_name) {
        const normalizedTheme = post.theme_name.toLowerCase();
        switch(normalizedTheme) {
            case 'новости':
                themeClass = 'news';
                themeData = 'новости';
                break;
            case 'недвижимость':
                themeClass = 'realestate';
                themeData = 'недвижимость';
                break;
            case 'работа':
                themeClass = 'job';
                themeData = 'работа';
                break;
            default:
                themeClass = normalizedTheme;
                themeData = normalizedTheme;
        }
    }
    
    const postDiv = document.createElement('div');
    postDiv.className = `post ${themeClass}`;
    postDiv.setAttribute('data-theme', themeData);
    postDiv.id = `post-${post.id}`;
    
    postDiv.innerHTML = `
        <div class="post-header">
            <div class="post-avatar">
                ${post.user_name ? post.user_name.substring(0, 2).toUpperCase() : '??'}
            </div>
            <div class="post-meta">
                <span class="post-theme ${themeClass}">${post.theme_name || 'Общее'}</span>
                ${post.user_name || 'Неизвестный'} • ${formatDate(post.created_at)}
            </div>
        <h4 class="post-title">${escapeHtml(post.header)}</h4>
        <div class="post-content">
            ${escapeHtml(post.body)}
        </div>
        <div class="post-actions">
            <div class="vote-buttons">
                <button class="vote-btn like ${post.likes > 0 ? 'active-like' : ''}" data-post-id="${post.id}">
                    <i class="fas fa-thumbs-up"></i>
                    <span class="vote-count">${post.likes || 0}</span>
                </button>
                <button class="vote-btn dislike ${post.dislikes > 0 ? 'active-dislike' : ''}" data-post-id="${post.id}">
                    <i class="fas fa-thumbs-down"></i>
                    <span class="vote-count">${post.dislikes || 0}</span>
                </button>
            </div>
            <button class="btn" onclick="showComments('${post.id}')">
                <i class="far fa-comment"></i> <span id="comment-count-${post.id}">${post.comments_count || 0}</span> комментариев
            </button>
        </div>
    `;
    
    return postDiv;
}

// Вспомогательная функция для экранирования HTML
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Вспомогательная функция для форматирования даты
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('ru-RU', { day: '2-digit', month: 'short', hour: '2-digit', minute: '2-digit' });
}

// Инициализация кнопок голосования
function initVoteButtons() {
    document.querySelectorAll('.vote-btn').forEach(btn => {
        btn.addEventListener('click', async function(e) {
            e.preventDefault();
            e.stopPropagation();
            
            const postId = this.getAttribute('data-post-id');
            const isLike = this.classList.contains('like');
            const endpoint = isLike ? `/api/v2/posts/${postId}/like` : `/api/v2/posts/${postId}/dislike`;
            
            try {
                const response = await fetch(endpoint, {
                    method: 'POST',
                    credentials: 'include'  // Включаем куки в запрос
                });
                
                if (response.ok) {
                    const result = await response.json();
                    if (result.status === 'OK') {
                        // Обновляем счетчик голосов
                        const countSpan = this.querySelector('.vote-count');
                        if (countSpan) {
                            let count = parseInt(countSpan.textContent) || 0;
                            countSpan.textContent = count + 1;
                        }
                        
                        // Обновляем класс кнопки
                        if (isLike) {
                            this.classList.add('active-like');
                        } else {
                            this.classList.add('active-dislike');
                        }
                    }
                } else {
                    console.error('Ошибка при голосовании:', response.status);
                }
            } catch (error) {
                console.error('Ошибка сети при голосовании:', error);
            }
        });
    });
}

// Обновление статистики тем
function updateThemeStatsOnce() {
    const posts = document.querySelectorAll('.post');
    const counts = { 'новости': 0, 'недвижимость': 0, 'работа': 0, 'general': 0 };
    
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
    
    if (newsCount) newsCount.textContent = `${counts['новости']} постов`;
    if (realestateCount) realestateCount.textContent = `${counts['недвижимость']} постов`;
    if (jobCount) jobCount.textContent = `${counts['работа']} постов`;
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