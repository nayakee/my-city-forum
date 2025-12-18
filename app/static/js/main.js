// ====================================================
// ОСНОВНОЙ КОД ГЛАВНОЙ СТРАНИЦЫ
// ====================================================

// Глобальное состояние приложения
const AppState = {
    user: null,
    currentPage: 1,
    totalPages: 1,
    filterTheme: 'all',
    userReactions: {} // Храним реакции текущего пользователя {postId: 'like'/'dislike'}
};

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', function() {
    console.log('Главная страница загружена. Инициализация...');
    
    // Устанавливаем правильные шрифты
    initFonts();
    
    // Проверяем авторизацию
    checkAuth();
    
    // Загружаем реакции пользователя если он авторизован
    if (AppState.user) {
        loadUserReactions();
    }
    
    // Инициализируем функционал страницы
    initPageFunctionality();
    
    // Обновляем статистику
    updateThemeStatsOnce();
    
    // Инициализируем закрытие меню по клику вне его
    initMenuCloseHandlers();
    
    // Инициализируем обработчики кликов на посты
    initPostClickHandlers();
});

// Инициализация шрифтов
function initFonts() {
    // Принудительно устанавливаем шрифты
    document.body.style.fontFamily = "'Segoe UI', 'Roboto', 'Helvetica Neue', Arial, sans-serif";
    document.body.style.fontWeight = '400';
    document.body.style.fontSize = '16px';
    document.body.style.lineHeight = '1.5';
    
    // Устанавливаем шрифты для заголовков
    document.querySelectorAll('h1, h2, h3, h4, h5, h6').forEach(el => {
        el.style.fontFamily = "'Segoe UI', 'Roboto', 'Helvetica Neue', Arial, sans-serif";
        el.style.fontWeight = '600';
    });
    
    // Устанавливаем шрифты для кнопок
    document.querySelectorAll('.btn, button').forEach(el => {
        el.style.fontFamily = "'Segoe UI', 'Roboto', 'Helvetica Neue', Arial, sans-serif";
        el.style.fontWeight = '500';
    });
    
    // Устанавливаем шрифты для постов
    document.querySelectorAll('.post').forEach(el => {
        el.style.fontFamily = "'Segoe UI', 'Roboto', 'Helvetica Neue', Arial, sans-serif";
    });
}

// Инициализация обработчиков кликов на посты
function initPostClickHandlers() {
    // Вешаем обработчик на весь контейнер с постами
    const postsFeed = document.getElementById('posts-feed');
    if (postsFeed) {
        postsFeed.addEventListener('click', function(e) {
            // Проверяем, кликнули ли на сам пост (но не на кнопки внутри)
            const postElement = e.target.closest('.post');
            if (postElement) {
                // Проверяем, не кликнули ли на элементы, которые не должны вести на страницу поста
                const isClickableElement = e.target.closest('.vote-btn') || 
                                          e.target.closest('.post-menu-btn') || 
                                          e.target.closest('.post-menu-dropdown') ||
                                          e.target.closest('.post-menu-item') ||
                                          e.target.closest('.btn[onclick*="showComments"]');
                
                if (!isClickableElement) {
                    const postId = postElement.id.replace('post-', '');
                    if (postId) {
                        // Переходим на страницу поста
                        window.location.href = `/web/post/${postId}`;
                    }
                }
            }
        });
    }
}

// Загрузка реакций текущего пользователя для всех постов на странице
async function loadUserReactions() {
    if (!AppState.user) return;
    
    try {
        // Получаем все ID постов на странице
        const postElements = document.querySelectorAll('.post');
        const postIds = Array.from(postElements).map(el => el.id.replace('post-', ''));
        
        if (postIds.length === 0) return;
        
        // Параллельно загружаем реакции для всех постов
        const promises = postIds.map(postId => getUserReactionForPost(postId));
        await Promise.all(promises);
        
    } catch (error) {
        console.error('Ошибка при загрузке реакций пользователя:', error);
    }
}

// Получение реакции пользователя для конкретного поста
async function getUserReactionForPost(postId) {
    if (!AppState.user) return null;
    
    try {
        const response = await fetchWithTokenCheck(`/api/v2/posts/${postId}/reaction`);
        
        // Если токен истек, response будет null и пользователь уже вышел
        if (!response) {
            return null;
        }
        
        if (response.ok) {
            const result = await response.json();
            if (result.status === 'OK') {
                // Сохраняем реакцию пользователя
                AppState.userReactions[postId] = result.reaction_type;
                
                // Обновляем отображение кнопок голосования
                updateVoteButtonsForPost(postId, result);
                return result.reaction_type;
            }
        }
    } catch (error) {
        console.error(`Ошибка при получении реакции для поста ${postId}:`, error);
    }
    return null;
}

// Обновление кнопок голосования для поста
function updateVoteButtonsForPost(postId, reactionData) {
    const likeBtn = document.querySelector(`.vote-btn.like[data-post-id="${postId}"]`);
    const dislikeBtn = document.querySelector(`.vote-btn.dislike[data-post-id="${postId}"]`);
    
    if (likeBtn && dislikeBtn) {
        // Сбрасываем все активные классы
        likeBtn.classList.remove('active-like');
        dislikeBtn.classList.remove('active-dislike');
        
        // Обновляем счетчики
        const likeCountSpan = likeBtn.querySelector('.vote-count');
        const dislikeCountSpan = dislikeBtn.querySelector('.vote-count');
        
        if (likeCountSpan && reactionData.likes !== undefined) {
            likeCountSpan.textContent = reactionData.likes;
        }
        
        if (dislikeCountSpan && reactionData.dislikes !== undefined) {
            dislikeCountSpan.textContent = reactionData.dislikes;
        }
        
        // Устанавливаем активный класс для текущей реакции
        if (reactionData.reaction_type === 'like') {
            likeBtn.classList.add('active-like');
        } else if (reactionData.reaction_type === 'dislike') {
            dislikeBtn.classList.add('active-dislike');
        }
    }
}

// Инициализация обработчиков закрытия меню
function initMenuCloseHandlers() {
    // Закрытие меню по клику вне его
    document.addEventListener('click', function(event) {
        if (!event.target.closest('.post-menu-btn') && !event.target.closest('.post-menu-dropdown')) {
            document.querySelectorAll('.post-menu-dropdown.show').forEach(menu => {
                menu.classList.remove('show');
            });
        }
    });
    
    // Закрытие модального окна при клике на фон
    document.getElementById('deleteModal')?.addEventListener('click', function(e) {
        if (e.target === this) {
            closeDeleteModal();
        }
    });
    
    // Закрытие по Escape
    document.addEventListener('keydown', function(event) {
        if (event.key === 'Escape') {
            closeDeleteModal();
            document.querySelectorAll('.post-menu-dropdown.show').forEach(menu => {
                menu.classList.remove('show');
            });
        }
    });
}

// Переключение меню поста
function togglePostMenu(postId) {
    // Закрыть все открытые меню
    document.querySelectorAll('.post-menu-dropdown.show').forEach(menu => {
        if (menu.id !== `menu-${postId}`) {
            menu.classList.remove('show');
        }
    });
    
    // Переключить текущее меню
    const menu = document.getElementById(`menu-${postId}`);
    if (menu) {
        menu.classList.toggle('show');
    }
}

// Копирование ссылки на пост
function copyPostLink(postId) {
    const postUrl = `${window.location.origin}/web/post/${postId}`;
    
    navigator.clipboard.writeText(postUrl)
        .then(() => {
            // Закрываем меню
            const menu = document.getElementById(`menu-${postId}`);
            if (menu) {
                menu.classList.remove('show');
            }
            
            // Используем глобальную систему уведомлений
            if (window.notify) {
                window.notify.success('Ссылка скопирована');
            } else {
                alert('Ссылка скопирована');
            }
        })
        .catch(err => {
            console.error('Ошибка копирования ссылки: ', err);
            
            if (window.notify) {
                window.notify.error('Не удалось скопировать ссылку');
            } else {
                alert('Не удалось скопировать ссылку');
            }
        });
}

// Подтверждение удаления поста
function confirmDeletePost(postId) {
    // Закрываем меню
    const menu = document.getElementById(`menu-${postId}`);
    if (menu) {
        menu.classList.remove('show');
    }
    
    // Показываем модальное окно
    document.getElementById('deleteModal').classList.add('show');
    
    // Сохраняем ID поста для удаления
    document.getElementById('confirmDeleteBtn').setAttribute('data-post-id', postId);
}

// Закрытие модального окна
function closeDeleteModal() {
    document.getElementById('deleteModal').classList.remove('show');
    document.getElementById('confirmDeleteBtn').removeAttribute('data-post-id');
}

// Удаление поста (заглушка - только показывает окно подтверждения)
function deletePost() {
    const postId = document.getElementById('confirmDeleteBtn').getAttribute('data-post-id');
    
    // Здесь будет реальная логика удаления через API
    console.log(`Удаление поста с ID: ${postId}`);
    
    // Закрываем модальное окно
    closeDeleteModal();
    
    // Используем глобальную систему уведомлений
    if (window.notify) {
        window.notify.success('Пост удален');
    } else {
        alert('Пост удален');
    }
}

// Проверка авторизации
function checkAuth() {
    const user = getCurrentUser();
    const guestButtons = document.getElementById('guest-buttons');
    const userMenu = document.getElementById('user-menu');
    
    if (user) {
        AppState.user = user;
        if (guestButtons) guestButtons.style.display = 'none';
        if (userMenu) userMenu.style.display = 'block';
        const username = document.getElementById('username');
        if (username) username.textContent = user.name || 'Пользователь';
        
        // Обновляем аватар пользователя
        const userAvatar = document.getElementById('user-avatar');
        if (userAvatar) {
            if (user.name) {
                userAvatar.style.display = 'none';
                let initialsElement = userAvatar.nextElementSibling;
                if (!initialsElement || !initialsElement.classList.contains('user-initials')) {
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
                userAvatar.style.display = 'block';
                userAvatar.src = `https://ui-avatars.com/api/?name=${encodeURIComponent(user.name || 'Пользователь')}&background=2e7d32&color=fff`;
            }
        }
    } else {
        AppState.user = null;
        if (guestButtons) guestButtons.style.display = 'flex';
        if (userMenu) userMenu.style.display = 'none';
        
        const userAvatar = document.getElementById('user-avatar');
        if (userAvatar) {
            userAvatar.style.display = 'block';
            userAvatar.src = '';
            const initialsElement = userAvatar.nextElementSibling;
            if (initialsElement && initialsElement.classList.contains('user-initials')) {
                initialsElement.remove();
            }
        }
    }
}

// Вспомогательная функция для проверки необходимости автоматического выхода
function checkResponseForLogout(response) {
    // Проверяем, содержит ли ответ флаг logout_required
    if (response.headers.get('content-type')?.includes('application/json')) {
        return response.clone().json().then(data => {
            if (data.logout_required) {
                handleAutoLogout();
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
    
    // Инициализация поиска
    initSearch();
    
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
            updateThemeColorLines(); // Обновляем цвета линий при фильтрации
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
    
    // 5. Голосование - НОВАЯ ЛОГИКА
    initVoteButtons();
    
    // 6. Кнопка выхода
    const logoutBtn = document.getElementById('logout-btn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', handleLogout);
    }
    
    // 7. Обработка кнопок модального окна
    document.getElementById('cancelDeleteBtn')?.addEventListener('click', closeDeleteModal);
    document.getElementById('confirmDeleteBtn')?.addEventListener('click', deletePost);
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

// Обновление цветных линий у постов в зависимости от темы
function updateThemeColorLines() {
    const posts = document.querySelectorAll('.post');
    posts.forEach(post => {
        const theme = post.getAttribute('data-theme');
        let color;
        
        switch(theme) {
            case 'новости':
                color = '#2196F3';
                break;
            case 'недвижимость':
                color = '#FF9800';
                break;
            case 'работа':
                color = '#9c27b0';
                break;
            default:
                color = '#2e7d32'; // Зеленый для общей темы
        }
        
        // Применяем цвет к посту
        post.style.borderLeft = `4px solid ${color}`;
    });
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
    
    // Инициализируем цветные линии у постов
    updateThemeColorLines();
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
        const response = await fetchWithTokenCheck('/api/v2/posts', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(postData)
        });

        // Если токен истек, response будет null и пользователь уже вышел
        if (!response) {
            return; // Прерываем выполнение, так как пользователь уже вышел
        }

        
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
        
        // Используем глобальную систему уведомлений
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
        const response = await fetchWithTokenCheck(url);
        if (!response) {
            return; // Прерываем выполнение, так как пользователь уже вышел
        }
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
    
    // Загружаем реакции пользователя для всех постов
    if (AppState.user) {
        loadUserReactions();
    }
    
    // Инициализируем кнопки голосования для новых постов
    initVoteButtons();
    
    // Инициализируем цветные линии
    updateThemeColorLines();
}

// Функция для создания элемента поста
function createPostElement(post) {
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
    postDiv.className = `post ${themeClass} post-clickable`;
    postDiv.setAttribute('data-theme', themeData);
    postDiv.id = `post-${post.id}`;
    
    // Проверяем текущую реакцию пользователя
    const userReaction = AppState.userReactions[post.id];
    const isLiked = userReaction === 'like';
    const isDisliked = userReaction === 'dislike';
    
    let borderColor = '#2e7d32';
    switch(themeData) {
        case 'новости':
            borderColor = '#2196F3';
            break;
        case 'недвижимость':
            borderColor = '#FF9800';
            break;
        case 'работа':
            borderColor = '#9c27b0';
            break;
    }
    
    postDiv.style.borderLeft = `4px solid ${borderColor}`;
    postDiv.style.borderRadius = '8px';
    postDiv.style.cursor = 'pointer';
    
    postDiv.innerHTML = `
        <!-- Кнопка меню поста (три точки) -->
        <button class="post-menu-btn" onclick="togglePostMenu('${post.id}')">
            <i class="fas fa-ellipsis-v"></i>
        </button>
        
        <!-- Выпадающее меню для поста -->
        <div class="post-menu-dropdown" id="menu-${post.id}">
            <button class="post-menu-item" onclick="copyPostLink('${post.id}')">
                <i class="fas fa-link"></i> Копировать ссылку
            </button>
            <button class="post-menu-item delete" onclick="confirmDeletePost('${post.id}')">
                <i class="fas fa-trash"></i> Удалить пост
            </button>
        </div>
        
        <div class="post-header">
            <div class="post-avatar">
                ${post.user_name ? post.user_name.substring(0, 2).toUpperCase() : '??'}
            </div>
            <div class="post-meta">
                <span class="post-theme ${themeClass}">${post.theme_name || 'Общее'}</span>
                ${post.user_name || 'Неизвестный'} • ${formatDate(post.created_at)}
            </div>
        </div>
        <h4 class="post-title">${escapeHtml(post.header)}</h4>
        <div class="post-content">
            ${escapeHtml(post.body)}
        </div>
        <div class="post-actions">
            <div class="vote-buttons">
                <button class="vote-btn like ${isLiked ? 'active-like' : ''}" data-post-id="${post.id}">
                    <i class="fas fa-thumbs-up"></i>
                    <span class="vote-count">${post.likes || 0}</span>
                </button>
                <button class="vote-btn dislike ${isDisliked ? 'active-dislike' : ''}" data-post-id="${post.id}">
                    <i class="fas fa-thumbs-down"></i>
                    <span class="vote-count">${post.dislikes || 0}</span>
                </button>
            </div>
            <button class="vote-btn favorite" data-post-id="${post.id}">
                <i class="fas fa-star"></i>
            </button>
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

// НОВАЯ ЛОГИКА ГОЛОСОВАНИЯ
function initVoteButtons() {
    document.querySelectorAll('.vote-btn').forEach(btn => {
        btn.addEventListener('click', async function(e) {
            e.preventDefault();
            e.stopPropagation();
            
            const postId = this.getAttribute('data-post-id');
            
            // Проверяем, является ли кнопка избранного
            if (this.classList.contains('favorite')) {
                // Обработка кнопки избранного
                if (!AppState.user) {
                    // Если пользователь не авторизован, перенаправляем на страницу входа
                    window.location.href = '/web/auth';
                    return;
                }
                
                try {
                    const response = await fetch('/favorites/toggle', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'Authorization': `Bearer ${localStorage.getItem('token')}`
                        },
                        body: JSON.stringify({ post_id: parseInt(postId) })
                    });
                    
                    if (response.ok) {
                        const result = await response.json();
                        
                        // Обновляем состояние кнопки
                        if (result.is_favorite) {
                            this.classList.add('active-favorite');
                        } else {
                            this.classList.remove('active-favorite');
                        }
                        
                        // Показываем уведомление
                        if (window.notify) {
                            window.notify.success(result.message);
                        }
                    } else {
                        const error = await response.json();
                        if (window.notify) {
                            window.notify.error(error.detail || 'Ошибка при изменении избранного');
                        }
                    }
                } catch (error) {
                    console.error('Ошибка при изменении избранного:', error);
                    if (window.notify) {
                        window.notify.error('Ошибка при изменении избранного');
                    }
                }
            } else {
                // Проверяем авторизацию для кнопок голосования
                if (!AppState.user) {
                    if (window.notify) {
                        window.notify.warning('Для голосования необходимо авторизоваться');
                    } else {
                        alert('Для голосования необходимо авторизоваться');
                    }
                    return;
                }
                
                const isLike = this.classList.contains('like');
                const endpoint = isLike ? `/api/v2/posts/${postId}/like` : `/api/v2/posts/${postId}/dislike`;
                
                try {
                    const response = await fetchWithTokenCheck(endpoint, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        }
                    });
                    
                    // Если токен истек, response будет null и пользователь уже вышел
                    if (!response) {
                        return;
                    }
                    
                    if (response.ok) {
                        const result = await response.json();
                        if (result.status === 'OK') {
                            // Обновляем глобальное состояние реакций
                            AppState.userReactions[postId] = result.user_reaction;
                            
                            // Обновляем счетчики голосов для обоих кнопок
                            const likeBtn = document.querySelector(`.vote-btn.like[data-post-id="${postId}"]`);
                            const dislikeBtn = document.querySelector(`.vote-btn.dislike[data-post-id="${postId}"]`);
                            
                            if (likeBtn && result.likes !== undefined) {
                                const likeCountSpan = likeBtn.querySelector('.vote-count');
                                if (likeCountSpan) {
                                    likeCountSpan.textContent = result.likes;
                                }
                            }
                            
                            if (dislikeBtn && result.dislikes !== undefined) {
                                const dislikeCountSpan = dislikeBtn.querySelector('.vote-count');
                                if (dislikeCountSpan) {
                                    dislikeCountSpan.textContent = result.dislikes;
                                }
                            }
                            
                            // Обновляем состояние кнопок
                            updateVoteButtonsAfterAction(postId, result.action, isLike);
                            
                            // Показываем сообщение о результате
                            if (window.notify) {
                                window.notify.success(result.message);
                            }
                        }
                    } else {
                        const errorData = await response.json().catch(() => ({ detail: 'Ошибка сервера' }));
                        if (window.notify) {
                            window.notify.error(errorData.detail || 'Ошибка при голосовании');
                        }
                    }
                } catch (error) {
                    console.error('Ошибка сети при голосовании:', error);
                    if (window.notify) {
                        window.notify.error('Ошибка сети при голосовании');
                    }
                }
            }
        });
    });
}

// Обновление состояния кнопок после действия
function updateVoteButtonsAfterAction(postId, action, isLike) {
    const likeBtn = document.querySelector(`.vote-btn.like[data-post-id="${postId}"]`);
    const dislikeBtn = document.querySelector(`.vote-btn.dislike[data-post-id="${postId}"]`);
    
    if (!likeBtn || !dislikeBtn) return;
    
    // Сначала сбрасываем все активные состояния
    likeBtn.classList.remove('active-like');
    dislikeBtn.classList.remove('active-dislike');
    
    // Применяем новое состояние в зависимости от действия
    switch (action) {
        case 'added':
            // Добавлена новая реакция
            if (isLike) {
                likeBtn.classList.add('active-like');
            } else {
                dislikeBtn.classList.add('active-dislike');
            }
            break;
            
        case 'removed':
            // Реакция удалена
            // Оба кнопки остаются неактивными
            break;
            
        case 'changed':
            // Реакция изменена (лайк на дизлайк или наоборот)
            if (isLike) {
                likeBtn.classList.add('active-like');
            } else {
                dislikeBtn.classList.add('active-dislike');
            }
            break;
    }
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

// Функция для автоматического выхода при истечении токена
function handleAutoLogout() {
    // Удаляем пользователя из localStorage
    localStorage.removeItem('user');
    
    // Удаляем токен из куки (если есть)
    document.cookie = "access_token=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;";
    
    // Используем глобальную систему уведомлений
    if (window.notify) {
        window.notify.warning('Ваша сессия истекла. Пожалуйста, войдите снова.');
    } else {
        alert('Ваша сессия истекла. Пожалуйста, войдите снова.');
    }
    
    // Перенаправляем на страницу авторизации
    setTimeout(() => {
        window.location.href = '/web/auth';
    }, 1500);
}

// Обработка выхода
function handleLogout(e) {
    e.preventDefault();
    
    // Удаляем пользователя из localStorage
    localStorage.removeItem('user');
    
    // Используем глобальную систему уведомлений
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
    // Переход на страницу поста с комментариями
    window.location.href = `/web/post/${postId}`;
}

// Инициализация поиска
function initSearch() {
    const searchInput = document.getElementById('search-input');
    const searchButton = document.getElementById('search-button');
    if (!searchInput) return;
    
    let searchTimeout;
    
    // Обработчик для поля ввода (поиск по мере ввода)
    searchInput.addEventListener('input', function(e) {
        clearTimeout(searchTimeout);
        
        const searchTerm = e.target.value.trim();
        console.log('Ввод поиска:', searchTerm); // Добавим лог для отладки
        
        // Задержка в 300мс перед выполнением поиска
        searchTimeout = setTimeout(() => {
            if (searchTerm.length === 0) {
                // Если поле пустое, показываем все посты
                console.log('Сброс фильтров');
                resetFilters();
            } else {
                // Выполняем поиск для любого запроса длиной 1 и более символов
                console.log('Выполнение поиска:', searchTerm);
                performSearch(searchTerm);
            }
        }, 300);
    });
    
    // Обработчик для кнопки поиска
    if (searchButton) {
        searchButton.addEventListener('click', function() {
            const searchTerm = searchInput.value.trim();
            console.log('Кнопка поиска нажата, значение:', searchTerm); // Лог для отладки
            
            if (searchTerm.length > 0) {
                performSearch(searchTerm);
            } else {
                // Если поле пустое, сбрасываем фильтры
                resetFilters();
            }
        });
    }
    

// Выполнение поиска
async function performSearch(searchTerm) {
    try {
        const response = await fetchWithTokenCheck(`/api/v2/posts/search?query=${encodeURIComponent(searchTerm)}`);
        
        // Если токен истек, response будет null и пользователь уже вышел
        if (!response) {
            return; // Прерываем выполнение, так как пользователь уже вышел
        }
        
        if (!response.ok) {
            throw new Error(`Ошибка поиска: ${response.status}`);
        }
        
        const posts = await response.json();
        console.log('Результаты поиска:', posts); // Добавим лог для отладки
        
        // Проверим, что posts - это массив
        if (!Array.isArray(posts)) {
            console.error('Ошибка: полученные данные не являются массивом', posts);
            return;
        }
        
        // Обновляем ленту постов результатами поиска
        updatePostsFeed(posts);
        
        // Сбрасываем активный фильтр темы
        AppState.filterTheme = 'all';
        document.querySelectorAll('.theme-filters-bar .theme-filter-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        document.querySelector('.theme-filters-bar .theme-filter-btn[data-theme="all"]').classList.add('active');
        
    } catch (error) {
        console.error('Ошибка при поиске постов:', error);
        
        // Показываем сообщение об ошибке
        if (window.notify) {
            window.notify.error('Ошибка при поиске постов');
        } else {
            alert('Ошибка при поиске постов');
        }
    }
}

// Сброс фильтров и возврат к обычному отображению постов
function resetFilters() {
    // Сбрасываем фильтр темы к "Все"
    AppState.filterTheme = 'all';
    document.querySelectorAll('.theme-filters-bar .theme-filter-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    document.querySelector('.theme-filters-bar .theme-filter-btn[data-theme="all"]').classList.add('active');
    
    // Загружаем все посты
    loadPosts();
}
}

console.log('main.js с исправлениями загружен');