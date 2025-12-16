// API конфигурация
const API_BASE_URL = window.location.origin;
const API = {
    LOGIN: '/auth/login',
    LOGOUT: '/auth/logout',
    REGISTER: '/auth/register',
    ME: '/auth/me',
    POSTS: '/api/posts',  // Основной эндпоинт для постов
    POSTS_DETAILED: '/api/posts/detailed',  // Для постов с деталями
    THEMES: '/themes',
    STATS: '/stats'
};

// Состояние приложения
let appState = {
    user: null,
    posts: [],
    themes: [],
    stats: {},
    currentPage: 1,
    totalPages: 1,
    sortBy: 'new',
    filterTheme: 'all',
    isCreatingPost: false
};

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOMContentLoaded сработал');
    
    // Загружаем начальные данные
    loadInitialData();
    
    // Настраиваем обработчики
    setupEventListeners();
});

// Загрузка начальных данных
async function loadInitialData() {
    console.log('loadInitialData начата');
    try {
        // Проверяем авторизацию
        await checkAuthStatus();
        console.log('Проверка авторизации завершена');
        
        // Загружаем темы
        await loadThemes();
        console.log('Темы загружены:', appState.themes);
        
        // Загружаем статистику
        await loadStats();
        console.log('Статистика загружена');
        
        // Загружаем посты
        await loadPosts();
        console.log('Посты загружены');
        
        // Обновляем интерфейс
        updateUI();
        console.log('Интерфейс обновлен');
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
async function loadThemes() {
    try {
        console.log('Загрузка тем начата...');
        const response = await fetch(API_BASE_URL + API.THEMES, {
            method: 'GET',
            credentials: 'include'
        });
        
        console.log('Ответ от API тем:', response.status);
        if (response.ok) {
            appState.themes = await response.json();
            console.log('Темы успешно загружены:', appState.themes);
        } else {
            console.error('Ошибка при загрузке тем:', response.status);
            // Если API тем не работает, используем заглушки с правильными ID из базы данных
            appState.themes = [
                { id: 1, name: 'Новости', posts_count: 0, icon: 'newspaper', created_at: null, updated_at: null },
                { id: 2, name: 'Недвижимость', posts_count: 0, icon: 'building', created_at: null, updated_at: null },
                { id: 3, name: 'Работа', posts_count: 0, icon: 'briefcase', created_at: null, updated_at: null }
            ];
        }
    } catch (error) {
        console.error('Ошибка загрузки тем:', error);
        // В случае ошибки используем темы из базы данных как заглушки
        appState.themes = [
            { id: 1, name: 'Новости', posts_count: 0, icon: 'newspaper', created_at: null, updated_at: null },
            { id: 2, name: 'Недвижимость', posts_count: 0, icon: 'building', created_at: null, updated_at: null },
            { id: 3, name: 'Работа', posts_count: 0, icon: 'briefcase', created_at: null, updated_at: null }
        ];
    }
}

// Вспомогательная функция для получения названия темы по ID
function getThemeNameById(themeId) {
    const theme = appState.themes.find(t => t.id === themeId);
    return theme ? theme.name : 'Без темы';
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
                themes: appState.themes.length,
                comments: 0
            };
        }
    } catch (error) {
        console.error('Ошибка загрузки статистики:', error);
        appState.stats = {
            users: 0,
            posts: 0,
            themes: 0,
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
            limit: 10
        });
        
        // Добавляем параметр сортировки, если не 'new' (по умолчанию)
        if (appState.sortBy !== 'new') {
            params.append('sort', appState.sortBy);
        }
        
        // Добавляем параметр фильтрации по теме, если не 'all'
        if (appState.filterTheme !== 'all') {
            const themeId = parseInt(appState.filterTheme);
            if (!isNaN(themeId)) {
                params.append('theme_id', themeId);
            }
        }
        
        // Сначала пробуем получить посты с дополнительной информацией
        const response = await fetch(API_BASE_URL + API.POSTS_DETAILED + '?' + params, {
            method: 'GET',
            credentials: 'include'
        });
        
        if (response.ok) {
            const data = await response.json();
            appState.posts = data.map(post => ({
                id: post.id,
                title: post.header,
                content: post.body,
                author_name: post.user_name,
                created_at: post.created_at,
                likes: post.likes || 0,
                dislikes: post.dislikes || 0,
                comments_count: post.comments_count || 0,
                theme_id: post.theme_id,
                theme_name: post.theme_name
            }));
            // Устанавливаем totalPages и currentPage, если они есть в ответе
            if (data.total_pages !== undefined) appState.totalPages = data.total_pages;
            if (data.current_page !== undefined) appState.currentPage = data.current_page;
        } else {
            // Если detailed endpoint не сработал, пробуем стандартный endpoint
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
                appState.posts = [];
                appState.totalPages = 1;
            }
        }
    } catch (error) {
        console.error('Ошибка загрузки постов:', error);
        appState.posts = [];
        appState.totalPages = 1;
    }
}

// Настройка обработчиков событий
function setupEventListeners() {
    console.log('setupEventListeners начата');
    
    // Кнопка выхода
    const logoutBtn = document.getElementById('logout-btn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', handleLogout);
        console.log('Обработчик logoutBtn добавлен');
    } else {
        console.log('Элемент logoutBtn не найден');
    }
    
    // Создание поста
    const showCreatePostBtn = document.getElementById('show-create-post');
    const cancelPostBtn = document.getElementById('cancel-post');
    const createPostForm = document.getElementById('create-post-form');
    
    if (showCreatePostBtn) {
        showCreatePostBtn.addEventListener('click', showCreatePostForm);
        console.log('Обработчик showCreatePostBtn добавлен');
    } else {
        console.log('Элемент showCreatePostBtn не найден');
    }
    
    if (cancelPostBtn) {
        cancelPostBtn.addEventListener('click', hideCreatePostForm);
        console.log('Обработчик cancelPostBtn добавлен');
    } else {
        console.log('Элемент cancelPostBtn не найден');
    }
    
    if (createPostForm) {
        createPostForm.addEventListener('submit', handleCreatePost);
        console.log('Обработчик createPostForm добавлен');
    } else {
        console.log('Элемент createPostForm не найден');
    }
    
    // Сортировка и фильтрация
    const sortSelect = document.getElementById('sort-select');
    
    if (sortSelect) {
        sortSelect.addEventListener('change', handleSortChange);
        console.log('Обработчик sortSelect добавлен');
    } else {
        console.log('Элемент sortSelect не найден');
    }
    
    // Пагинация
    const prevPageBtn = document.getElementById('prev-page');
    const nextPageBtn = document.getElementById('next-page');
    
    if (prevPageBtn) {
        prevPageBtn.addEventListener('click', goToPreviousPage);
        console.log('Обработчик prevPageBtn добавлен');
    } else {
        console.log('Элемент prevPageBtn не найден');
    }
    
    if (nextPageBtn) {
        nextPageBtn.addEventListener('click', goToNextPage);
        console.log('Обработчик nextPageBtn добавлен');
    } else {
        console.log('Элемент nextPageBtn не найден');
    }
    
    // Обработчики для кнопок тем
    setupThemeButtonListeners();
}

// Настройка обработчиков для кнопок тем
function setupThemeButtonListeners() {
    const themeBtns = document.querySelectorAll('.theme-btn');
    themeBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const themeId = this.getAttribute('data-theme-id');
            const themeName = this.getAttribute('data-theme-name');
            document.getElementById('post-theme').value = themeId;
            document.getElementById('post-theme-name').value = themeName;
            
            // Убираем активный класс у всех кнопок
            themeBtns.forEach(b => b.classList.remove('active'));
            // Добавляем активный класс к выбранной кнопке
            this.classList.add('active');
        });
    });
}

// Обновление интерфейса
function updateUI() {
    // Обновляем информацию о пользователе
    updateUserUI();
    
    // Обновляем темы в селекторах
    updateThemeSelectors();
    
    // Обновляем форму создания поста
    updateCreatePostUI();
    
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
            showCreatePostBtn.textContent = appState.isCreatingPost ? 'Скрыть форму' : 'Новый пост';
            showCreatePostBtn.innerHTML = appState.isCreatingPost ?
                '<i class="fas fa-times"></i> Скрыть форму' :
                '<i class="fas fa-plus"></i> Новый пост';
        }
        if (createPostCard) {
            createPostCard.style.display = appState.isCreatingPost ? 'block' : 'none';
        }
    } else {
        // Гость
        if (createPostCard) createPostCard.style.display = 'none';
        if (guestNotice) guestNotice.style.display = 'block';
        if (showCreatePostBtn) {
            showCreatePostBtn.textContent = 'Новый пост';
            showCreatePostBtn.innerHTML = '<i class="fas fa-plus"></i> Новый пост';
        }
    }
    
    // Обновляем селектор тем в форме создания поста
    updateThemeSelectors();
}

// Обновление селекторов тем
function updateThemeSelectors() {
    const postThemeSelect = document.getElementById('post-theme');
    const themesList = document.getElementById('themes-list');
    const themeFiltersContainer = document.getElementById('theme-filters');
    
    console.log('updateThemeSelectors вызвана, тем в состоянии:', appState.themes.length);
    
    // Заполняем селектор тем для создания поста
    if (postThemeSelect) {
        // Убираем старые обработчики и добавляем новые
        const themeBtns = document.querySelectorAll('.theme-btn');
        themeBtns.forEach(btn => {
            // Удаляем старые обработчики
            const newBtn = btn.cloneNode(true);
            btn.parentNode.replaceChild(newBtn, btn);
        });
        
        // Находим новые кнопки и добавляем обработчики
        const newThemeBtns = document.querySelectorAll('.theme-btn');
        newThemeBtns.forEach(btn => {
            btn.addEventListener('click', function() {
                const themeId = this.getAttribute('data-theme-id');
                const themeName = this.getAttribute('data-theme-name');
                document.getElementById('post-theme').value = themeId;
                document.getElementById('post-theme-name').value = themeName;
                
                // Убираем активный класс у всех кнопок
                newThemeBtns.forEach(b => b.classList.remove('active'));
                // Добавляем активный класс к выбранной кнопке
                this.classList.add('active');
            });
        });
    }
    
    // Заполняем список тем в боковой панели
    if (themesList) {
        themesList.innerHTML = '';
        
        appState.themes.forEach(theme => {
            const themeItem = document.createElement('div');
            themeItem.className = 'theme-item';
            if (appState.filterTheme === String(theme.id)) {
                themeItem.classList.add('active');
            }
            
            themeItem.innerHTML = `
                <div class="theme-icon">
                    <i class="fas fa-${theme.icon || 'tag'}"></i>
                </div>
                <div class="theme-info">
                    <h4>${theme.name}</h4>
                    <div class="theme-count">${theme.posts_count || theme.count || 0} постов</div>
                </div>
            `;
            
            themeItem.addEventListener('click', () => {
                appState.filterTheme = String(theme.id);
                appState.currentPage = 1;
                loadPosts().then(() => updateUI());
            });
            
            themesList.appendChild(themeItem);
        });
    }
    
    // Генерируем кнопки фильтрации тем над лентой постов
    if (themeFiltersContainer) {
        // Очищаем контейнер и добавляем кнопку "Все" снова
        themeFiltersContainer.innerHTML = '';
        
        // Кнопка "Все" остается статичной
        const allButton = document.createElement('button');
        allButton.className = appState.filterTheme === 'all' ? 'theme-filter active' : 'theme-filter';
        allButton.setAttribute('data-theme', 'all');
        allButton.id = 'theme-filter-all';
        allButton.innerHTML = '<i class="fas fa-layer-group"></i> Все';
        allButton.addEventListener('click', handleThemeFilterChange);
        themeFiltersContainer.appendChild(allButton);
        
        // Добавляем кнопки для каждой темы
        appState.themes.forEach(theme => {
            const themeButton = document.createElement('button');
            themeButton.className = `theme-filter ${theme.name.toLowerCase()}`;
            if (appState.filterTheme === String(theme.id)) {
                themeButton.classList.add('active');
            }
            themeButton.setAttribute('data-theme', theme.id);
            themeButton.id = `theme-filter-${theme.id}`;
            
            // Определяем иконку для темы
            let iconClass = 'tag'; // иконка по умолчанию
            if (theme.name.toLowerCase().includes('новост')) {
                iconClass = 'newspaper';
            } else if (theme.name.toLowerCase().includes('недвижим')) {
                iconClass = 'building';
            } else if (theme.name.toLowerCase().includes('работ')) {
                iconClass = 'briefcase';
            } else if (theme.name.toLowerCase().includes('транспорт')) {
                iconClass = 'bus';
            } else if (theme.name.toLowerCase().includes('эколог')) {
                iconClass = 'leaf';
            } else if (theme.name.toLowerCase().includes('культ')) {
                iconClass = 'theater-masks';
            }
            
            themeButton.innerHTML = `<i class="fas fa-${iconClass}"></i> ${theme.name}`;
            themeButton.addEventListener('click', handleThemeFilterChange);
            themeFiltersContainer.appendChild(themeButton);
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
            { label: 'Тем', value: appState.stats.themes || appState.themes.length, icon: 'tags' },
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
            <div class="no-posts-message">
                <p>Пока нет постов. Будьте первым, кто создаст пост!</p>
            </div>
        `;
        return;
    }
    
    postsFeed.innerHTML = '';
    
    appState.posts.forEach(post => {
        // Создаем пост в формате, соответствующем серверному шаблону
        const postElement = document.createElement('div');
        postElement.className = `post ${post.theme_name ? post.theme_name.toLowerCase() : 'general'}`;
        postElement.setAttribute('data-theme', post.theme_name ? post.theme_name.toLowerCase() : 'general');
        
        // Форматируем дату
        const postDate = new Date(post.created_at || Date.now());
        const formattedDate = postDate.toLocaleDateString('ru-RU', {
            day: 'numeric',
            month: 'short',
            hour: '2-digit',
            minute: '2-digit'
        }).replace('.', ' ');
        
        // Получаем первые 2 буквы имени пользователя для аватара
        const userInitials = (post.author_name || '??').substring(0, 2).toUpperCase();
        
        postElement.innerHTML = `
            <div class="post-header">
                <div class="post-avatar">
                    ${userInitials}
                </div>
                <div class="post-meta">
                    <span class="post-theme ${post.theme_name ? post.theme_name.toLowerCase() : 'general'}">${post.theme_name || 'Общее'}</span>
                    ${post.author_name || 'Анонимный пользователь'} • ${formattedDate}
                </div>
            </div>
            <h4 class="post-title">${post.title || post.header || 'Без названия'}</h4>
            <div class="post-content">${post.content || post.body || 'Нет содержания'}</div>
            <div class="post-actions">
                <div class="vote-buttons">
                    <button class="vote-btn like" data-post-id="${post.id}">
                        <i class="fas fa-thumbs-up"></i>
                        <span class="vote-count">${post.likes || 0}</span>
                    </button>
                    <button class="vote-btn dislike" data-post-id="${post.id}">
                        <i class="fas fa-thumbs-down"></i>
                        <span class="vote-count">${post.dislikes || 0}</span>
                    </button>
                </div>
                <button class="btn" onclick="showComments('${post.id}')">
                    <i class="far fa-comment"></i> <span id="comment-count-${post.id}">${post.comments_count || post.comments || 0}</span> комментариев
                </button>
            </div>
        `;
        
        // Добавляем обработчики событий для кнопок лайков и дизлайков
        const likeBtn = postElement.querySelector('.vote-btn.like');
        const dislikeBtn = postElement.querySelector('.vote-btn.dislike');
        
        if (likeBtn) {
            likeBtn.addEventListener('click', (e) => {
                e.preventDefault();
                handleLike(post.id);
            });
        }
        
        if (dislikeBtn) {
            dislikeBtn.addEventListener('click', (e) => {
                e.preventDefault();
                handleDislike(post.id);
            });
        }
        
        postsFeed.appendChild(postElement);
    });
}

// Функция для добавления нового поста в ленту без перезагрузки страницы
function addPostToFeed(post) {
    const postsFeed = document.getElementById('posts-feed');
    if (!postsFeed) return;
    
    // Удаляем сообщение "Пока нет постов", если это первый пост
    const noPostsMessage = postsFeed.querySelector('.no-posts-message');
    if (noPostsMessage) {
        noPostsMessage.remove();
    }
    
    // Создаем пост в формате, соответствующем серверному шаблону
    const postElement = document.createElement('div');
    postElement.className = `post ${post.theme_name ? post.theme_name.toLowerCase() : 'general'}`;
    postElement.setAttribute('data-theme', post.theme_name ? post.theme_name.toLowerCase() : 'general');
    
    // Форматируем дату
    const postDate = new Date(post.created_at || Date.now());
    const formattedDate = postDate.toLocaleDateString('ru-RU', {
        day: 'numeric',
        month: 'short',
        hour: '2-digit',
        minute: '2-digit'
    }).replace('.', ' ');
    
    // Получаем первые 2 буквы имени пользователя для аватара
    const userInitials = (post.author_name || '??').substring(0, 2).toUpperCase();
    
    postElement.innerHTML = `
        <div class="post-header">
            <div class="post-avatar">
                ${userInitials}
            </div>
            <div class="post-meta">
                <span class="post-theme ${post.theme_name ? post.theme_name.toLowerCase() : 'general'}">${post.theme_name || 'Общее'}</span>
                ${post.author_name || 'Анонимный пользователь'} • ${formattedDate}
            </div>
        </div>
        <h4 class="post-title">${post.title || post.header || 'Без названия'}</h4>
        <div class="post-content">${post.content || post.body || 'Нет содержания'}</div>
        <div class="post-actions">
            <div class="vote-buttons">
                <button class="vote-btn like" data-post-id="${post.id}">
                    <i class="fas fa-thumbs-up"></i>
                    <span class="vote-count">${post.likes || 0}</span>
                </button>
                <button class="vote-btn dislike" data-post-id="${post.id}">
                    <i class="fas fa-thumbs-down"></i>
                    <span class="vote-count">${post.dislikes || 0}</span>
                </button>
            </div>
            <button class="btn" onclick="showComments('${post.id}')">
                <i class="far fa-comment"></i> <span id="comment-count-${post.id}">${post.comments_count || post.comments || 0}</span> комментариев
            </button>
        </div>
    `;
    
    // Добавляем обработчики событий для кнопок лайков и дизлайков
    const likeBtn = postElement.querySelector('.vote-btn.like');
    const dislikeBtn = postElement.querySelector('.vote-btn.dislike');
    
    if (likeBtn) {
        likeBtn.addEventListener('click', (e) => {
            e.preventDefault();
            handleLike(post.id);
        });
    }
    
    if (dislikeBtn) {
        dislikeBtn.addEventListener('click', (e) => {
            e.preventDefault();
            handleDislike(post.id);
        });
    }
    
    // Добавляем пост в начало ленты
    if (postsFeed.firstChild) {
        postsFeed.insertBefore(postElement, postsFeed.firstChild);
    } else {
        postsFeed.appendChild(postElement);
    }
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
        // Показываем уведомление для гостей
        const guestNotice = document.getElementById('guest-notice');
        if (guestNotice) {
            guestNotice.style.display = 'block';
            setTimeout(() => {
                guestNotice.style.display = 'none';
            }, 3000);
        }
        return;
    }
    
    // Проверяем, загружены ли темы
    if (appState.themes.length === 0) {
        showNotification('Загрузка тем...', 'info');
        // Загружаем темы, если они не загружены
        loadThemes().then(() => {
            // После загрузки тем обновляем UI и показываем форму
            updateUI();
            appState.isCreatingPost = true;
            updateCreatePostUI();
        }).catch(error => {
            console.error('Ошибка загрузки тем:', error);
            showNotification('Ошибка загрузки тем. Попробуйте перезагрузить страницу.', 'error');
        });
    } else {
        appState.isCreatingPost = !appState.isCreatingPost;
        updateCreatePostUI();
    }
}

// Скрыть форму создания поста
function hideCreatePostForm() {
    appState.isCreatingPost = false;
    updateCreatePostUI();
    
    // Очищаем форму
    const form = document.getElementById('create-post-form');
    if (form) form.reset();
    
    // Сбрасываем активный класс у кнопок тем
    const themeBtns = document.querySelectorAll('.theme-btn');
    themeBtns.forEach(btn => btn.classList.remove('active'));
    
    // Сбрасываем первую тему как активную
    if (themeBtns.length > 0) {
        themeBtns[0].classList.add('active');
        const postTheme = document.getElementById('post-theme');
        const postThemeName = document.getElementById('post-theme-name');
        if (postTheme) postTheme.value = themeBtns[0].getAttribute('data-theme-id');
        if (postThemeName) postThemeName.value = themeBtns[0].getAttribute('data-theme-name');
    }
}

// Обработка создания поста
async function handleCreatePost(e) {
    console.log('handleCreatePost вызвана');
    e.preventDefault();
    
    if (!appState.user) {
        console.log('Пользователь не авторизован');
        showNotification('Для создания поста необходимо войти в систему', 'error');
        return;
    }
    
    const title = document.getElementById('post-title').value.trim();
    const content = document.getElementById('post-content').value.trim();
    const themeIdValue = document.getElementById('post-theme').value;
    console.log('Полученные данные:', { title, content, themeId: themeIdValue });
    
    // Валидация
    if (!title || !content || !themeIdValue) {
        console.log('Ошибка валидации:', { title: !!title, content: !!content, themeId: !!themeIdValue });
        showNotification('Заполните обязательные поля', 'error');
        return;
    }
    
    // Преобразуем themeIdValue в число и проверяем его корректность
    const themeId = parseInt(themeIdValue, 10);
    console.log('themeId после parseInt:', themeId);
    if (isNaN(themeId) || themeId <= 0) {
        showNotification('Выберите корректную тему', 'error');
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
        header: title,
        body: content,
        theme_id: themeId,
        community_id: null,  // Явно указываем null для опционального поля
        is_published: true
    };
    console.log('Данные для отправки:', postData);
    
    try {
        // ИСПРАВЛЕНО: отправляем на /api/posts (без /web)
        const response = await fetch(API_BASE_URL + API.POSTS, {
            method: 'POST',
            headers: {
                'accept': 'application/json',
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(postData),
            credentials: 'include'
        });
        console.log('Ответ от сервера:', response.status);
        
        const contentType = response.headers.get('content-type');
        let data;
        
        if (contentType && contentType.includes('application/json')) {
            data = await response.json();
        } else {
            const text = await response.text();
            console.log('Ответ не JSON:', text);
            data = { detail: text || 'Неизвестная ошибка' };
        }
        
        console.log('Данные ответа:', data);
        
        if (response.ok) {
            showNotification('Пост успешно создан!', 'success');
            hideCreatePostForm();
            
            // Создаем объект нового поста для добавления в ленту
            const newPost = {
                id: data.post_id || Date.now(), // используем ID из ответа или временный
                title: title,
                content: content,
                author_name: appState.user?.name || 'Вы',
                created_at: new Date().toISOString(),
                likes: 0,
                dislikes: 0,
                comments_count: 0,
                theme_id: themeId,
                theme_name: getThemeNameById(themeId) // используем вспомогательную функцию для получения названия темы
            };
            
            // Добавляем пост в ленту без перезагрузки страницы
            addPostToFeed(newPost);
            
            // Перезагружаем посты для обновления состояния
            appState.currentPage = 1;
            await loadPosts();
            
        } else {
            // Проверяем, является ли data объектом и содержит ли он detail
            let errorMessage = 'Ошибка создания поста';
            if (data && typeof data === 'object') {
                if (data.detail) {
                    errorMessage = data.detail;
                } else if (data.message) {
                    errorMessage = data.message;
                } else if (Array.isArray(data)) {
                    // Если data - массив ошибок, объединяем их
                    errorMessage = data.map(err => err.msg || err.detail || 'Ошибка').join('; ');
                }
            } else if (typeof data === 'string') {
                errorMessage = data;
            }
            showNotification(errorMessage, 'error');
        }
    } catch (error) {
        console.error('Ошибка создания поста:', error);
        showNotification('Не удалось создать пост. Проверьте подключение к интернету.', 'error');
    }
}

// Обработка изменения сортировки
function handleSortChange(e) {
    appState.sortBy = e.target.value;
    appState.currentPage = 1;
    loadPosts().then(() => updateUI());
}

// Обновление состояния кнопок фильтра тем
function updateThemeFilterButtons() {
    // Находим все кнопки фильтра тем
    const themeFilterButtons = document.querySelectorAll('.theme-filter');
    themeFilterButtons.forEach(button => {
        const themeValue = button.getAttribute('data-theme');
        if (themeValue === appState.filterTheme || (appState.filterTheme === 'all' && themeValue === 'all')) {
            button.classList.add('active');
        } else {
            button.classList.remove('active');
        }
    });
}

// Обработка изменения фильтра тем
function handleThemeFilterChange(e) {
    // Находим, какая кнопка была нажата
    const clickedButton = e.currentTarget;
    const themeValue = clickedButton.getAttribute('data-theme');
    appState.filterTheme = themeValue;
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
        const response = await fetch(`${API_BASE_URL}/api/posts/${postId}/like`, {
            method: 'POST',
            credentials: 'include'
        });
        
        if (response.ok) {
            showNotification('Лайк добавлен!', 'success');
            
            // Обновляем интерфейс
            const likeBtn = document.querySelector(`.vote-btn.like[data-post-id="${postId}"]`);
            if (likeBtn) {
                const span = likeBtn.querySelector('span');
                let count = parseInt(span.textContent) || 0;
                count++;
                span.textContent = count;
                likeBtn.classList.add('active-like');
                likeBtn.innerHTML = `<i class="fas fa-thumbs-up"></i> <span class="vote-count">${count}</span>`;
            }
        } else {
            showNotification('Ошибка добавления лайка', 'error');
        }
        
    } catch (error) {
        console.error('Ошибка добавления лайка:', error);
        showNotification('Ошибка добавления лайка', 'error');
    }
}

// Обработка дизлайка
async function handleDislike(postId) {
    if (!appState.user) {
        showNotification('Для оценки поста необходимо войти в систему', 'info');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}/api/posts/${postId}/dislike`, {
            method: 'POST',
            credentials: 'include'
        });
        
        if (response.ok) {
            showNotification('Дизлайк добавлен!', 'success');
            
            // Обновляем интерфейс
            const dislikeBtn = document.querySelector(`.vote-btn.dislike[data-post-id="${postId}"]`);
            if (dislikeBtn) {
                const span = dislikeBtn.querySelector('span');
                let count = parseInt(span.textContent) || 0;
                count++;
                span.textContent = count;
                dislikeBtn.classList.add('active-dislike');
                dislikeBtn.innerHTML = `<i class="fas fa-thumbs-down"></i> <span class="vote-count">${count}</span>`;
            }
        } else {
            showNotification('Ошибка добавления дизлайка', 'error');
        }
        
    } catch (error) {
        console.error('Ошибка добавления дизлайка:', error);
        showNotification('Ошибка добавления дизлайка', 'error');
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
    
    const minutes = Math.floor(diff / 6000);
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

// Показ уведомлений (обновленная версия)
function showNotification(message, type = 'success') {
    // Создаем контейнер для уведомлений, если его нет
    let notificationsContainer = document.getElementById('notifications-container');
    if (!notificationsContainer) {
        notificationsContainer = document.createElement('div');
        notificationsContainer.id = 'notifications-container';
        document.body.appendChild(notificationsContainer);
    }
    
    // Удаляем старые уведомления
    const oldNotifications = notificationsContainer.querySelectorAll('.notification-item');
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
    notification.className = `notification-item ${type}`;
    
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
    
    notification.innerHTML = `
        <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : 'info-circle'}"></i>
        <span>${message}</span>
    `;
    
    notificationsContainer.appendChild(notification);
    
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

// Функция для отображения комментариев к посту
async function showComments(postId) {
    try {
        // Преобразуем postId в число, если он пришел как строка
        const numericId = parseInt(postId, 10);
        if (isNaN(numericId)) {
            console.error('Некорректный ID поста:', postId);
            showNotification('Некорректный ID поста', 'error');
            return;
        }
        // Здесь можно реализовать логику для загрузки и отображения комментариев
        // Пока что просто перенаправляем на страницу поста
        window.location.href = `/web/post/${numericId}`;
    } catch (error) {
        console.error('Ошибка при загрузке комментариев:', error);
        showNotification('Не удалось загрузить комментарии', 'error');
    }
}