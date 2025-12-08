// API конфигурация
const API_BASE_URL = window.location.origin;
const API = {
    LOGIN: '/auth/login',
    LOGOUT: '/auth/logout',
    REGISTER: '/auth/register',
    ME: '/auth/me',
    POSTS: '/posts',
    TOPICS: '/topics',
    STATS: '/stats'
};

// Состояние приложения
let appState = {
    user: null,
    posts: [],
    topics: [],
    stats: {},
    currentPage: 1,
    totalPages: 1,
    sortBy: 'new',
    filterTopic: 'all',
    isCreatingPost: false
};

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', function() {
    console.log('Главная страница форума загружена');
    
    // Загружаем начальные данные
    loadInitialData();
    
    // Настраиваем обработчики
    setupEventListeners();
});

// Загрузка начальных данных
async function loadInitialData() {
    try {
        // Проверяем авторизацию
        await checkAuthStatus();
        
        // Загружаем темы
        await loadTopics();
        
        // Загружаем статистику
        await loadStats();
        
        // Загружаем посты
        await loadPosts();
        
        // Обновляем интерфейс
        updateUI();
        
    } catch (error) {
        console.error('Ошибка загрузки данных:', error);
        showNotification('Ошибка загрузки данных', 'error');
    }
}

// Проверка статуса авторизации
async function checkAuthStatus() {
    try {
        const response = await fetch(API_BASE_URL + API.ME, {
            method: 'GET',
            credentials: 'include'
        });
        
        if (response.ok) {
            appState.user = await response.json();
            console.log('Пользователь авторизован:', appState.user);
        } else {
            appState.user = null;
            console.log('Пользователь не авторизован');
        }
    } catch (error) {
        console.error('Ошибка проверки авторизации:', error);
        appState.user = null;
    }
}

// Загрузка тем
async function loadTopics() {
    try {
        const response = await fetch(API_BASE_URL + API.TOPICS, {
            method: 'GET',
            credentials: 'include'
        });
        
        if (response.ok) {
            appState.topics = await response.json();
        } else {
            // Если API тем нет, используем заглушки
            appState.topics = [
                { id: 1, name: 'Городские новости', count: 0, icon: 'building' },
                { id: 2, name: 'Транспорт и дороги', count: 0, icon: 'car' },
                { id: 3, name: 'Благоустройство', count: 0, icon: 'tree' },
                { id: 4, name: 'ЖКХ и услуги', count: 0, icon: 'home' },
                { id: 5, name: 'Культура и отдых', count: 0, icon: 'theater-masks' },
                { id: 6, name: 'Безопасность', count: 0, icon: 'shield-alt' }
            ];
        }
    } catch (error) {
        console.error('Ошибка загрузки тем:', error);
        appState.topics = [];
    }
}

// Загрузка статистики
async function loadStats() {
    try {
        const response = await fetch(API_BASE_URL + API.STATS, {
            method: 'GET',
            credentials: 'include'
        });
        
        if (response.ok) {
            appState.stats = await response.json();
        } else {
            // Если API статистики нет, используем заглушки
            appState.stats = {
                users: 0,
                posts: 0,
                topics: appState.topics.length,
                comments: 0
            };
        }
    } catch (error) {
        console.error('Ошибка загрузки статистики:', error);
        appState.stats = {
            users: 0,
            posts: 0,
            topics: 0,
            comments: 0
        };
    }
}

// Загрузка постов
async function loadPosts() {
    try {
        // Параметры запроса
        const params = new URLSearchParams({
            page: appState.currentPage,
            sort: appState.sortBy,
            topic: appState.filterTopic === 'all' ? '' : appState.filterTopic
        });
        
        const response = await fetch(API_BASE_URL + API.POSTS + '?' + params, {
            method: 'GET',
            credentials: 'include'
        });
        
        if (response.ok) {
            const data = await response.json();
            appState.posts = data.posts || [];
            appState.totalPages = data.total_pages || 1;
            appState.currentPage = data.current_page || 1;
        } else {
            // Если API постов нет, показываем сообщение
            appState.posts = [];
            appState.totalPages = 1;
        }
    } catch (error) {
        console.error('Ошибка загрузки постов:', error);
        appState.posts = [];
        appState.totalPages = 1;
    }
}

// Настройка обработчиков событий
function setupEventListeners() {
    // Кнопка выхода
    const logoutBtn = document.getElementById('logout-btn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', handleLogout);
    }
    
    // Создание поста
    const showCreatePostBtn = document.getElementById('show-create-post');
    const cancelPostBtn = document.getElementById('cancel-post');
    const createPostForm = document.getElementById('create-post-form');
    
    if (showCreatePostBtn) {
        showCreatePostBtn.addEventListener('click', showCreatePostForm);
    }
    
    if (cancelPostBtn) {
        cancelPostBtn.addEventListener('click', hideCreatePostForm);
    }
    
    if (createPostForm) {
        createPostForm.addEventListener('submit', handleCreatePost);
    }
    
    // Сортировка и фильтрация
    const sortSelect = document.getElementById('sort-select');
    const topicFilter = document.getElementById('topic-filter');
    
    if (sortSelect) {
        sortSelect.addEventListener('change', handleSortChange);
    }
    
    if (topicFilter) {
        topicFilter.addEventListener('change', handleTopicFilterChange);
    }
    
    // Пагинация
    const prevPageBtn = document.getElementById('prev-page');
    const nextPageBtn = document.getElementById('next-page');
    
    if (prevPageBtn) {
        prevPageBtn.addEventListener('click', goToPreviousPage);
    }
    
    if (nextPageBtn) {
        nextPageBtn.addEventListener('click', goToNextPage);
    }
}

// Обновление интерфейса
function updateUI() {
    // Обновляем информацию о пользователе
    updateUserUI();
    
    // Обновляем форму создания поста
    updateCreatePostUI();
    
    // Обновляем темы в селекторах
    updateTopicsSelectors();
    
    // Обновляем статистику
    updateStatsUI();
    
    // Обновляем список постов
    updatePostsUI();
    
    // Обновляем пагинацию
    updatePaginationUI();
}

// Обновление информации о пользователе
function updateUserUI() {
    const guestButtons = document.getElementById('guest-buttons');
    const userMenu = document.getElementById('user-menu');
    const username = document.getElementById('username');
    const userAvatar = document.getElementById('user-avatar');
    
    if (appState.user) {
        // Пользователь авторизован
        if (guestButtons) guestButtons.style.display = 'none';
        if (userMenu) userMenu.style.display = 'block';
        if (username) username.textContent = appState.user.name || 'Пользователь';
        
        // Обновляем аватар
        if (userAvatar && appState.user.name) {
            userAvatar.src = `https://ui-avatars.com/api/?name=${encodeURIComponent(appState.user.name)}&background=2e7d32&color=fff`;
        }
    } else {
        // Гость
        if (guestButtons) guestButtons.style.display = 'flex';
        if (userMenu) userMenu.style.display = 'none';
    }
}

// Обновление формы создания поста
function updateCreatePostUI() {
    const createPostCard = document.getElementById('create-post-card');
    const guestNotice = document.getElementById('guest-notice');
    const showCreatePostBtn = document.getElementById('show-create-post');
    
    if (appState.user) {
        // Пользователь авторизован
        if (guestNotice) guestNotice.style.display = 'none';
        if (showCreatePostBtn) {
            showCreatePostBtn.textContent = appState.isCreatingPost ? 'Скрыть форму' : 'Создать пост';
            showCreatePostBtn.innerHTML = appState.isCreatingPost ? 
                '<i class="fas fa-times"></i> Скрыть форму' : 
                '<i class="fas fa-pen"></i> Создать пост';
        }
        if (createPostCard) {
            createPostCard.style.display = appState.isCreatingPost ? 'block' : 'none';
        }
    } else {
        // Гость
        if (createPostCard) createPostCard.style.display = 'none';
        if (guestNotice) guestNotice.style.display = 'block';
        if (showCreatePostBtn) {
            showCreatePostBtn.textContent = 'Создать пост';
            showCreatePostBtn.innerHTML = '<i class="fas fa-pen"></i> Создать пост';
        }
    }
}

// Обновление селекторов тем
function updateTopicsSelectors() {
    const postTopicSelect = document.getElementById('post-topic');
    const topicFilterSelect = document.getElementById('topic-filter');
    const topicsList = document.getElementById('topics-list');
    
    // Заполняем селектор тем для создания поста
    if (postTopicSelect) {
        postTopicSelect.innerHTML = '<option value="">-- Выберите тему --</option>';
        appState.topics.forEach(topic => {
            const option = document.createElement('option');
            option.value = topic.id;
            option.textContent = topic.name;
            postTopicSelect.appendChild(option);
        });
    }
    
    // Заполняем селектор фильтра тем
    if (topicFilterSelect) {
        topicFilterSelect.innerHTML = '<option value="all">Все темы</option>';
        appState.topics.forEach(topic => {
            const option = document.createElement('option');
            option.value = topic.id;
            option.textContent = topic.name;
            if (appState.filterTopic === String(topic.id)) {
                option.selected = true;
            }
            topicFilterSelect.appendChild(option);
        });
    }
    
    // Заполняем список тем в боковой панели
    if (topicsList) {
        topicsList.innerHTML = '';
        
        appState.topics.forEach(topic => {
            const topicItem = document.createElement('div');
            topicItem.className = 'topic-item';
            if (appState.filterTopic === String(topic.id)) {
                topicItem.classList.add('active');
            }
            
            topicItem.innerHTML = `
                <div class="topic-icon">
                    <i class="fas fa-${topic.icon || 'tag'}"></i>
                </div>
                <div class="topic-info">
                    <h4>${topic.name}</h4>
                    <div class="topic-count">${topic.count || 0} постов</div>
                </div>
            `;
            
            topicItem.addEventListener('click', () => {
                appState.filterTopic = String(topic.id);
                appState.currentPage = 1;
                loadPosts().then(() => updateUI());
            });
            
            topicsList.appendChild(topicItem);
        });
    }
}

// Обновление статистики
function updateStatsUI() {
    const statsGrid = document.getElementById('forum-stats');
    
    if (statsGrid) {
        statsGrid.innerHTML = '';
        
        const stats = [
            { label: 'Пользователей', value: appState.stats.users || 0, icon: 'users' },
            { label: 'Постов', value: appState.stats.posts || 0, icon: 'file-alt' },
            { label: 'Тем', value: appState.stats.topics || appState.topics.length, icon: 'tags' },
            { label: 'Комментариев', value: appState.stats.comments || 0, icon: 'comments' }
        ];
        
        stats.forEach(stat => {
            const statItem = document.createElement('div');
            statItem.className = 'stat-item';
            
            statItem.innerHTML = `
                <div class="stat-value">${stat.value}</div>
                <div class="stat-label">${stat.label}</div>
            `;
            
            statsGrid.appendChild(statItem);
        });
    }
}

// Обновление списка постов
function updatePostsUI() {
    const postsFeed = document.getElementById('posts-feed');
    
    if (!postsFeed) return;
    
    if (appState.posts.length === 0) {
        postsFeed.innerHTML = `
            <div class="empty-posts">
                <i class="fas fa-inbox"></i>
                <h3>Пока нет постов</h3>
                <p>Будьте первым, кто создаст пост!</p>
            </div>
        `;
        return;
    }
    
    postsFeed.innerHTML = '';
    
    appState.posts.forEach(post => {
        const postElement = document.createElement('article');
        postElement.className = 'post';
        
        // Форматируем дату
        const postDate = new Date(post.created_at || Date.now());
        const timeAgo = getTimeAgo(postDate);
        
        // Находим тему поста
        const topic = appState.topics.find(t => t.id === post.topic_id) || 
                     appState.topics.find(t => t.name === post.topic_name) || 
                     { name: 'Без темы', icon: 'tag' };
        
        postElement.innerHTML = `
            <div class="post-header">
                <img src="https://ui-avatars.com/api/?name=${encodeURIComponent(post.author_name || 'Аноним')}&background=4caf50&color=fff" 
                     alt="Аватар" class="post-avatar">
                <div class="post-author">
                    <h3>${post.author_name || 'Анонимный пользователь'}</h3>
                    <span class="post-time">
                        ${timeAgo} • 
                        <span class="post-category">
                            <i class="fas fa-${topic.icon || 'tag'}"></i> ${topic.name}
                        </span>
                    </span>
                </div>
            </div>
            <h2 class="post-title">${post.title || 'Без названия'}</h2>
            <div class="post-content">${post.content || 'Нет содержания'}</div>
            
            ${post.tags ? `
            <div class="post-tags">
                ${post.tags.split(',').map(tag => 
                    `<span class="tag">#${tag.trim()}</span>`
                ).join('')}
            </div>
            ` : ''}
            
            <div class="post-footer">
                <button class="post-action like-btn" data-post-id="${post.id}">
                    <i class="far fa-thumbs-up"></i> 
                    <span>${post.likes || 0}</span>
                </button>
                <button class="post-action comment-btn">
                    <i class="far fa-comment"></i> 
                    <span class="post-stats">${post.comments || 0} комментариев</span>
                </button>
                <button class="post-action share-btn">
                    <i class="far fa-share-square"></i>
                </button>
            </div>
        `;
        
        // Добавляем обработчик лайка
        const likeBtn = postElement.querySelector('.like-btn');
        if (likeBtn) {
            likeBtn.addEventListener('click', () => handleLike(post.id));
        }
        
        postsFeed.appendChild(postElement);
    });
}

// Обновление пагинации
function updatePaginationUI() {
    const pagination = document.getElementById('pagination');
    const pageInfo = document.getElementById('page-info');
    const prevPageBtn = document.getElementById('prev-page');
    const nextPageBtn = document.getElementById('next-page');
    
    if (appState.totalPages <= 1) {
        if (pagination) pagination.style.display = 'none';
        return;
    }
    
    if (pagination) pagination.style.display = 'flex';
    if (pageInfo) pageInfo.textContent = `Страница ${appState.currentPage} из ${appState.totalPages}`;
    
    if (prevPageBtn) {
        prevPageBtn.disabled = appState.currentPage <= 1;
        prevPageBtn.style.opacity = appState.currentPage <= 1 ? '0.5' : '1';
    }
    
    if (nextPageBtn) {
        nextPageBtn.disabled = appState.currentPage >= appState.totalPages;
        nextPageBtn.style.opacity = appState.currentPage >= appState.totalPages ? '0.5' : '1';
    }
}

// Показать форму создания поста
function showCreatePostForm() {
    if (!appState.user) {
        showNotification('Для создания поста необходимо войти в систему', 'info');
        return;
    }
    
    appState.isCreatingPost = !appState.isCreatingPost;
    updateCreatePostUI();
}

// Скрыть форму создания поста
function hideCreatePostForm() {
    appState.isCreatingPost = false;
    updateCreatePostUI();
    
    // Очищаем форму
    const form = document.getElementById('create-post-form');
    if (form) form.reset();
}

// Обработка создания поста
async function handleCreatePost(e) {
    e.preventDefault();
    
    if (!appState.user) {
        showNotification('Для создания поста необходимо войти в систему', 'error');
        return;
    }
    
    const title = document.getElementById('post-title').value.trim();
    const content = document.getElementById('post-content').value.trim();
    const topicId = document.getElementById('post-topic').value;
    const tags = document.getElementById('post-tags').value.trim();
    
    // Валидация
    if (!title || !content || !topicId) {
        showNotification('Заполните обязательные поля', 'error');
        return;
    }
    
    if (title.length > 200) {
        showNotification('Заголовок должен быть не более 200 символов', 'error');
        return;
    }
    
    if (content.length > 5000) {
        showNotification('Содержание должно быть не более 5000 символов', 'error');
        return;
    }
    
    const postData = {
        title: title,
        content: content,
        topic_id: parseInt(topicId),
        tags: tags
    };
    
    try {
        const response = await fetch(API_BASE_URL + API.POSTS, {
            method: 'POST',
            headers: {
                'accept': 'application/json',
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(postData),
            credentials: 'include'
        });
        
        const data = await response.json();
        
        if (response.status === 200 || response.status === 201) {
            showNotification('Пост успешно создан!', 'success');
            hideCreatePostForm();
            
            // Перезагружаем посты
            appState.currentPage = 1;
            await loadPosts();
            updateUI();
            
        } else {
            showNotification(data.detail || 'Ошибка создания поста', 'error');
        }
    } catch (error) {
        console.error('Ошибка создания поста:', error);
        showNotification('Не удалось создать пост', 'error');
    }
}

// Обработка изменения сортировки
function handleSortChange(e) {
    appState.sortBy = e.target.value;
    appState.currentPage = 1;
    loadPosts().then(() => updateUI());
}

// Обработка изменения фильтра тем
function handleTopicFilterChange(e) {
    appState.filterTopic = e.target.value;
    appState.currentPage = 1;
    loadPosts().then(() => updateUI());
}

// Переход на предыдущую страницу
function goToPreviousPage() {
    if (appState.currentPage > 1) {
        appState.currentPage--;
        loadPosts().then(() => updateUI());
    }
}

// Переход на следующую страницу
function goToNextPage() {
    if (appState.currentPage < appState.totalPages) {
        appState.currentPage++;
        loadPosts().then(() => updateUI());
    }
}

// Обработка лайка
async function handleLike(postId) {
    if (!appState.user) {
        showNotification('Для оценки поста необходимо войти в систему', 'info');
        return;
    }
    
    try {
        // В реальном приложении здесь будет запрос к API
        showNotification('Лайк добавлен!', 'success');
        
        // Обновляем интерфейс
        const likeBtn = document.querySelector(`.like-btn[data-post-id="${postId}"]`);
        if (likeBtn) {
            const span = likeBtn.querySelector('span');
            let count = parseInt(span.textContent) || 0;
            count++;
            span.textContent = count;
            likeBtn.classList.add('liked');
            likeBtn.innerHTML = `<i class="fas fa-thumbs-up"></i> <span>${count}</span>`;
        }
        
    } catch (error) {
        console.error('Ошибка добавления лайка:', error);
        showNotification('Ошибка добавления лайка', 'error');
    }
}

// Выход из системы
async function handleLogout(e) {
    e.preventDefault();
    
    try {
        const response = await fetch(API_BASE_URL + API.LOGOUT, {
            method: 'POST',
            credentials: 'include'
        });
        
        if (response.ok) {
            showNotification('Вы успешно вышли из системы', 'success');
            
            // Сбрасываем состояние
            appState.user = null;
            appState.isCreatingPost = false;
            
            // Перезагружаем страницу через секунду
            setTimeout(() => {
                window.location.reload();
            }, 1000);
            
        } else {
            showNotification('Ошибка при выходе', 'error');
        }
    } catch (error) {
        console.error('Ошибка при выходе:', error);
        showNotification('Ошибка соединения', 'error');
    }
}

// Вспомогательная функция: время назад
function getTimeAgo(date) {
    const now = new Date();
    const diff = now - date;
    
    const minutes = Math.floor(diff / 60000);
    const hours = Math.floor(diff / 3600000);
    const days = Math.floor(diff / 86400000);
    
    if (minutes < 1) return 'только что';
    if (minutes < 60) return `${minutes} мин. назад`;
    if (hours < 24) return `${hours} ч. назад`;
    if (days === 1) return 'вчера';
    if (days < 7) return `${days} дн. назад`;
    
    // Форматируем дату
    return date.toLocaleDateString('ru-RU', {
        day: 'numeric',
        month: 'long',
        year: 'numeric'
    });
}

// Показ уведомлений
function showNotification(message, type = 'success') {
    const notification = document.getElementById('notification');
    if (notification) {
        notification.textContent = message;
        notification.className = `notification ${type}`;
        notification.classList.add('show');
        
        setTimeout(() => {
            notification.classList.remove('show');
        }, 3000);
    } else {
        // Создаем временное уведомление
        const tempNotif = document.createElement('div');
        tempNotif.textContent = message;
        tempNotif.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 15px 25px;
            border-radius: 5px;
            color: white;
            background: ${type === 'success' ? '#388e3c' : type === 'error' ? '#d32f2f' : '#2196f3'};
            z-index: 2000;
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        `;
        document.body.appendChild(tempNotif);
        
        setTimeout(() => {
            document.body.removeChild(tempNotif);
        }, 3000);
    }
}
// Показ уведомлений (обновленная версия)
function showNotification(message, type = 'success') {
    // Удаляем старые уведомления
    const oldNotifications = document.querySelectorAll('.notification');
    oldNotifications.forEach(notif => {
        notif.classList.add('slide-out');
        setTimeout(() => {
            if (notif.parentNode) {
                notif.parentNode.removeChild(notif);
            }
        }, 300);
    });
    
    // Создаем новое уведомление
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    
    // Если message это объект, преобразуем в строку
    if (typeof message === 'object') {
        console.log('Получен объект вместо строки:', message);
        
        // Пробуем извлечь полезную информацию
        if (message.detail) {
            message = message.detail;
        } else if (message.message) {
            message = message.message;
        } else if (message.error) {
            message = message.error;
        } else {
            // Преобразуем объект в строку JSON для отладки
            message = JSON.stringify(message);
        }
    }
    
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    // Удаляем через 5 секунд
    setTimeout(() => {
        notification.classList.add('slide-out');
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 300);
    }, 5000);
}