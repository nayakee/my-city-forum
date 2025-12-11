// communities.js - Функциональность страницы сообществ

class CommunitiesPage {
    constructor() {
        this.init();
    }
    
    init() {
        this.setupEventListeners();
        this.loadSavedState();
        this.updateUI();
    }
    
    setupEventListeners() {
        // Фильтрация сообществ
        document.querySelectorAll('.filter-btn').forEach(filter => {
            filter.addEventListener('click', (e) => this.handleFilterClick(e));
        });
        
        // Поиск сообществ
        const searchInput = document.querySelector('.search-input');
        if (searchInput) {
            searchInput.addEventListener('input', (e) => this.handleSearchInput(e));
        }
        
        // Присоединение к сообществу
        document.querySelectorAll('.join-btn').forEach(button => {
            button.addEventListener('click', (e) => this.handleJoinClick(e));
        });
        
        // Создание сообщества
        const createBtn = document.getElementById('create-community-btn');
        if (createBtn) {
            createBtn.addEventListener('click', () => this.handleCreateCommunity());
        }
        
        // Сохранение активного фильтра
        document.querySelectorAll('.filter-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                if (e.target.dataset.filter) {
                    localStorage.setItem('communityFilter', e.target.dataset.filter);
                }
            });
        });
    }
    
    loadSavedState() {
        // Загружаем сохраненный фильтр
        const savedFilter = localStorage.getItem('communityFilter');
        if (savedFilter) {
            const filterBtn = document.querySelector(`[data-filter="${savedFilter}"]`);
            if (filterBtn) {
                filterBtn.click();
            }
        }
    }
    
    updateUI() {
        // Обновляем интерфейс в зависимости от авторизации
        const isGuest = document.getElementById('guest-buttons').style.display !== 'none';
        
        if (isGuest) {
            // Для гостей показываем сообщение о необходимости авторизации
            const joinButtons = document.querySelectorAll('.join-btn');
            joinButtons.forEach(btn => {
                btn.addEventListener('click', (e) => {
                    e.preventDefault();
                    this.showAuthRequired();
                });
            });
        }
    }
    
    handleFilterClick(event) {
        const filterBtn = event.currentTarget;
        const filterType = filterBtn.dataset.filter;
        
        // Обновляем активный фильтр
        document.querySelectorAll('.filter-btn').forEach(f => f.classList.remove('active'));
        filterBtn.classList.add('active');
        
        // Показываем/скрываем сообщества
        const allCards = document.querySelectorAll('.community-card');
        
        if (filterType === 'all') {
            allCards.forEach(card => {
                card.style.display = 'block';
                card.style.animation = 'fadeIn 0.3s ease-out';
            });
        } else if (filterType === 'popular' || filterType === 'new') {
            allCards.forEach(card => {
                if (card.dataset.category === filterType) {
                    card.style.display = 'block';
                    card.style.animation = 'fadeIn 0.3s ease-out';
                } else {
                    card.style.display = 'none';
                }
            });
        } else if (filterType === 'district' || filterType === 'topic') {
            allCards.forEach(card => {
                if (card.dataset.district || card.dataset.topic) {
                    card.style.display = 'block';
                    card.style.animation = 'fadeIn 0.3s ease-out';
                } else {
                    card.style.display = 'none';
                }
            });
        }
        
        // Сохраняем в историю
        this.saveToHistory(`Фильтр: ${filterBtn.textContent.trim()}`);
    }
    
    handleSearchInput(event) {
        const searchTerm = event.target.value.toLowerCase().trim();
        const cards = document.querySelectorAll('.community-card');
        
        if (searchTerm === '') {
            // Если поиск пустой, показываем все карточки
            cards.forEach(card => {
                card.style.display = 'block';
                card.style.animation = 'fadeIn 0.3s ease-out';
            });
            return;
        }
        
        cards.forEach(card => {
            const title = card.querySelector('.community-title').textContent.toLowerCase();
            const description = card.querySelector('.community-description').textContent.toLowerCase();
            const tags = Array.from(card.querySelectorAll('.tag'))
                .map(tag => tag.textContent.toLowerCase());
            
            const matches = title.includes(searchTerm) || 
                           description.includes(searchTerm) || 
                           tags.some(tag => tag.includes(searchTerm));
            
            if (matches) {
                card.style.display = 'block';
                card.style.animation = 'fadeIn 0.3s ease-out';
                
                // Подсвечиваем совпадения
                this.highlightText(card, searchTerm);
            } else {
                card.style.display = 'none';
            }
        });
    }
    
    highlightText(card, searchTerm) {
        // Снимаем предыдущие подсветки
        const highlightedElements = card.querySelectorAll('.highlight');
        highlightedElements.forEach(el => {
            const parent = el.parentNode;
            parent.replaceChild(document.createTextNode(el.textContent), el);
            parent.normalize();
        });
        
        if (!searchTerm) return;
        
        // Подсвечиваем текст в заголовке и описании
        const elementsToHighlight = [
            ...card.querySelectorAll('.community-title, .community-description')
        ];
        
        elementsToHighlight.forEach(element => {
            const text = element.textContent;
            const regex = new RegExp(`(${searchTerm})`, 'gi');
            const newText = text.replace(regex, '<span class="highlight" style="background-color: #fff3cd; padding: 0 2px; border-radius: 2px;">$1</span>');
            
            if (newText !== text) {
                element.innerHTML = newText;
            }
        });
    }
    
    handleJoinClick(event) {
        const button = event.currentTarget;
        const communityCard = button.closest('.community-card');
        const communityTitle = communityCard.querySelector('.community-title h3').textContent;
        
        // Проверяем авторизацию
        const isGuest = document.getElementById('guest-buttons').style.display !== 'none';
        
        if (isGuest) {
            this.showAuthRequired();
            return;
        }
        
        // Переключаем состояние кнопки
        if (button.classList.contains('joined')) {
            button.classList.remove('joined');
            button.innerHTML = '<i class="fas fa-plus"></i> Присоединиться';
            this.showNotification(`Вы покинули сообщество "${communityTitle}"`, 'info');
        } else {
            button.classList.add('joined');
            button.innerHTML = '<i class="fas fa-check"></i> Вы в сообществе';
            this.showNotification(`Вы присоединились к сообществу "${communityTitle}"`, 'success');
        }
        
        // Сохраняем состояние
        this.saveCommunityState(communityCard.id || communityTitle, button.classList.contains('joined'));
        
        // Обновляем статистику (в реальном приложении - запрос к API)
        this.updateCommunityStats(communityCard, button.classList.contains('joined'));
    }
    
    handleCreateCommunity() {
        const isGuest = document.getElementById('guest-buttons').style.display !== 'none';
        
        if (isGuest) {
            this.showAuthRequired();
            setTimeout(() => {
                window.location.href = '/auth';
            }, 1000);
        } else {
            this.showNotification('Функция создания сообщества скоро будет доступна', 'info');
            // В реальном приложении здесь будет переход на форму создания
            // window.location.href = '/communities/create';
        }
    }
    
    updateCommunityStats(card, isJoining) {
        const statsElement = card.querySelector('.community-stats');
        if (!statsElement) return;
        
        const membersElement = statsElement.querySelector('.stat-item:nth-child(1) span');
        if (membersElement) {
            let currentMembers = parseInt(membersElement.textContent) || 0;
            currentMembers = isJoining ? currentMembers + 1 : currentMembers - 1;
            if (currentMembers < 0) currentMembers = 0;
            membersElement.textContent = `${currentMembers.toLocaleString()} ${this.getPluralForm(currentMembers, ['участник', 'участника', 'участников'])}`;
        }
    }
    
    getPluralForm(number, forms) {
        number = Math.abs(number) % 100;
        const remainder = number % 10;
        
        if (number > 10 && number < 20) return forms[2];
        if (remainder > 1 && remainder < 5) return forms[1];
        if (remainder === 1) return forms[0];
        return forms[2];
    }
    
    saveCommunityState(communityId, isJoined) {
        // Сохраняем состояние в localStorage
        const communities = JSON.parse(localStorage.getItem('userCommunities') || '{}');
        communities[communityId] = isJoined;
        localStorage.setItem('userCommunities', JSON.stringify(communities));
    }
    
    loadCommunityStates() {
        // Загружаем сохраненные состояния
        const communities = JSON.parse(localStorage.getItem('userCommunities') || '{}');
        
        document.querySelectorAll('.community-card').forEach(card => {
            const communityId = card.id || card.querySelector('.community-title h3').textContent;
            const isJoined = communities[communityId];
            
            if (isJoined) {
                const joinBtn = card.querySelector('.join-btn');
                if (joinBtn) {
                    joinBtn.classList.add('joined');
                    joinBtn.innerHTML = '<i class="fas fa-check"></i> Вы в сообществе';
                }
            }
        });
    }
    
    showAuthRequired() {
        if (typeof notify !== 'undefined') {
            notify.error('Для этого действия необходимо войти в систему');
        } else {
            alert('Для этого действия необходимо войти в систему');
        }
    }
    
    showNotification(message, type = 'info') {
        if (typeof notify !== 'undefined') {
            notify[type](message);
        } else {
            console.log(`${type}: ${message}`);
        }
    }
    
    saveToHistory(action) {
        // Сохраняем действия в историю (для аналитики)
        const history = JSON.parse(localStorage.getItem('communityHistory') || '[]');
        history.push({
            action,
            timestamp: new Date().toISOString(),
            page: 'communities'
        });
        
        // Ограничиваем историю 50 записями
        if (history.length > 50) {
            history.shift();
        }
        
        localStorage.setItem('communityHistory', JSON.stringify(history));
    }
    
    // Методы для работы с API (заглушки)
    async fetchCommunities() {
        // В реальном приложении здесь будет запрос к API
        return [];
    }
    
    async joinCommunity(communityId) {
        // В реальном приложении здесь будет запрос к API
        return { success: true };
    }
    
    async leaveCommunity(communityId) {
        // В реальном приложении здесь будет запрос к API
        return { success: true };
    }
}

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', () => {
    console.log('Страница сообществ загружена');
    
    const communitiesPage = new CommunitiesPage();
    communitiesPage.loadCommunityStates();
    
    // Добавляем глобальный объект для доступа из консоли
    window.communitiesPage = communitiesPage;
});

// Добавляем стили для анимаций
const style = document.createElement('style');
style.textContent = `
    @keyframes fadeIn {
        from {
            opacity: 0;
            transform: translateY(10px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .community-card {
        animation: fadeIn 0.3s ease-out;
    }
    
    .highlight {
        background-color: #fff3cd !important;
        padding: 0 2px !important;
        border-radius: 2px !important;
        transition: background-color 0.3s ease;
    }
`;
document.head.appendChild(style);

// communities.js - Работа с сообществами на фронтенде

const API_BASE_URL = window.location.origin;
const COMMUNITIES_API = {
    GET_COMMUNITIES: '/communities/',
    GET_COMMUNITY: '/communities/{id}',
    JOIN_COMMUNITY: '/communities/{id}/join',
    LEAVE_COMMUNITY: '/communities/{id}/leave',
    USER_COMMUNITIES: '/communities/user/joined',
    STATS_OVERALL: '/communities/stats/overall',
    STATS_POPULAR: '/communities/stats/popular',
    CREATE_COMMUNITY: '/communities/create'
};

class CommunitiesManager {
    constructor() {
        this.userId = null;
        this.userCommunities = new Set();
    }
    
    async init() {
        // Проверяем авторизацию
        await this.checkAuth();
        
        // Загружаем сообщества пользователя
        if (this.userId) {
            await this.loadUserCommunities();
        }
        
        // Настраиваем обработчики
        this.setupHandlers();
        
        // Загружаем начальные сообщества
        await this.loadInitialCommunities();
    }
    
    async checkAuth() {
        try {
            const response = await fetch('/auth/me', {
                credentials: 'include'
            });
            if (response.ok) {
                const user = await response.json();
                this.userId = user.id;
                
                // Обновляем UI
                const userMenu = document.getElementById('user-menu');
                const guestButtons = document.getElementById('guest-buttons');
                const username = document.getElementById('username');
                
                if (userMenu && guestButtons && username) {
                    userMenu.style.display = 'flex';
                    guestButtons.style.display = 'none';
                    username.textContent = user.name || 'Пользователь';
                }
            }
        } catch (error) {
            console.log('Пользователь не авторизован');
        }
    }
    
    async loadUserCommunities() {
        try {
            const response = await fetch(COMMUNITIES_API.USER_COMMUNITIES, {
                credentials: 'include'
            });
            
            if (response.ok) {
                const communities = await response.json();
                this.userCommunities = new Set(communities.map(c => c.id));
                this.updateCommunityCards();
            }
        } catch (error) {
            console.error('Ошибка загрузки сообществ пользователя:', error);
        }
    }
    
    async loadInitialCommunities() {
        try {
            const response = await fetch(COMMUNITIES_API.GET_COMMUNITIES, {
                credentials: 'include'
            });
            
            if (response.ok) {
                const communities = await response.json();
                this.renderCommunities(communities);
            }
        } catch (error) {
            console.error('Ошибка загрузки сообществ:', error);
        }
    }
    
    setupHandlers() {
        // Обработка кнопок присоединения
        document.addEventListener('click', async (e) => {
            if (e.target.closest('.join-btn')) {
                await this.handleJoinLeave(e);
            }
        });
        
        // Обработка поиска
        const searchInput = document.querySelector('.search-input');
        if (searchInput) {
            searchInput.addEventListener('input', (e) => this.handleSearch(e));
        }
        
        // Обработка фильтров
        document.querySelectorAll('.filter-btn').forEach(btn => {
            btn.addEventListener('click', (e) => this.handleFilter(e));
        });
        
        // Обработка создания сообщества
        const createBtn = document.getElementById('create-community-btn');
        if (createBtn) {
            createBtn.addEventListener('click', () => this.handleCreateCommunity());
        }
    }
    
    async handleJoinLeave(event) {
        const button = event.target.closest('.join-btn');
        if (!button) return;
        
        const communityId = parseInt(button.dataset.communityId);
        const isJoining = !button.classList.contains('joined');
        
        // Проверяем авторизацию
        if (!this.userId) {
            this.showNotification('Для этого действия необходимо войти в систему', 'error');
            return;
        }
        
        try {
            const endpoint = isJoining ? 
                COMMUNITIES_API.JOIN_COMMUNITY.replace('{id}', communityId) :
                COMMUNITIES_API.LEAVE_COMMUNITY.replace('{id}', communityId);
            
            const response = await fetch(endpoint, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                credentials: 'include'
            });
            
            if (response.ok) {
                const result = await response.json();
                
                // Обновляем UI
                button.classList.toggle('joined');
                const icon = button.querySelector('i');
                icon.className = isJoining ? 'fas fa-check' : 'fas fa-plus';
                button.innerHTML = `
                    <i class="fas ${isJoining ? 'fa-check' : 'fa-plus'}"></i>
                    ${isJoining ? 'Вы в сообществе' : 'Присоединиться'}
                `;
                
                // Обновляем локальное хранилище
                if (isJoining) {
                    this.userCommunities.add(communityId);
                } else {
                    this.userCommunities.delete(communityId);
                }
                
                // Обновляем статистику
                this.updateCommunityStats(communityId, isJoining);
                
                this.showNotification(result.message, isJoining ? 'success' : 'info');
                
            } else {
                const error = await response.json();
                throw new Error(error.detail || 'Ошибка операции');
            }
        } catch (error) {
            console.error('Ошибка операции с сообществом:', error);
            this.showNotification(error.message || 'Произошла ошибка', 'error');
        }
    }
    
    updateCommunityCards() {
        // Обновляем все карточки сообществ на странице
        document.querySelectorAll('.community-card').forEach(card => {
            const communityId = parseInt(card.dataset.id);
            const joinBtn = card.querySelector('.join-btn');
            
            if (joinBtn && this.userCommunities.has(communityId)) {
                joinBtn.classList.add('joined');
                joinBtn.innerHTML = '<i class="fas fa-check"></i> Вы в сообществе';
            } else if (joinBtn) {
                joinBtn.classList.remove('joined');
                joinBtn.innerHTML = '<i class="fas fa-plus"></i> Присоединиться';
            }
        });
    }
    
    updateCommunityStats(communityId, isJoining) {
        const card = document.querySelector(`[data-id="${communityId}"]`);
        if (!card) return;
        
        const statsElement = card.querySelector('.community-stats');
        const membersElement = statsElement?.querySelector('.stat-item:nth-child(1) span');
        
        if (membersElement) {
            let currentMembers = parseInt(membersElement.textContent) || 0;
            currentMembers = isJoining ? currentMembers + 1 : currentMembers - 1;
            if (currentMembers < 0) currentMembers = 0;
            membersElement.textContent = `${currentMembers.toLocaleString()} участников`;
        }
    }
    
    async handleSearch(event) {
        const searchTerm = event.target.value.trim();
        
        try {
            const params = new URLSearchParams();
            if (searchTerm) params.append('search', searchTerm);
            
            // Получаем активный фильтр
            const activeFilter = document.querySelector('.filter-btn.active');
            if (activeFilter && activeFilter.dataset.filter !== 'all') {
                params.append('filter', activeFilter.dataset.filter);
            }
            
            const response = await fetch(`${COMMUNITIES_API.GET_COMMUNITIES}?${params}`, {
                credentials: 'include'
            });
            
            if (response.ok) {
                const communities = await response.json();
                this.renderCommunities(communities);
            }
        } catch (error) {
            console.error('Ошибка поиска сообществ:', error);
        }
    }
    
    async handleFilter(event) {
        const button = event.currentTarget;
        const filterType = button.dataset.filter;
        
        // Обновляем активный фильтр
        document.querySelectorAll('.filter-btn').forEach(f => f.classList.remove('active'));
        button.classList.add('active');
        
        try {
            const params = new URLSearchParams();
            if (filterType !== 'all') {
                params.append('filter', filterType);
            }
            
            // Получаем значение поиска
            const searchInput = document.querySelector('.search-input');
            if (searchInput?.value) {
                params.append('search', searchInput.value);
            }
            
            const response = await fetch(`${COMMUNITIES_API.GET_COMMUNITIES}?${params}`, {
                credentials: 'include'
            });
            
            if (response.ok) {
                const communities = await response.json();
                this.renderCommunities(communities);
            }
        } catch (error) {
            console.error('Ошибка фильтрации сообществ:', error);
        }
    }
    
    renderCommunities(communities) {
        const container = document.querySelector('.communities-grid');
        if (!container) return;
        
        container.innerHTML = '';
        
        communities.forEach(community => {
            const card = this.createCommunityCard(community);
            container.appendChild(card);
        });
    }
    
    createCommunityCard(community) {
        const card = document.createElement('div');
        card.className = 'community-card';
        card.dataset.id = community.id;
        
        // Определяем иконку сообщества
        let icon = 'fa-users';
        if (community.name.includes('транспорт') || community.name.includes('Транспорт')) {
            icon = 'fa-bus';
        } else if (community.name.includes('парк') || community.name.includes('Парк')) {
            icon = 'fa-tree';
        } else if (community.name.includes('дети') || community.name.includes('Дети')) {
            icon = 'fa-child';
        }
        
        // Определяем теги
        const tags = this.detectTags(community);
        const tagsHtml = tags.map(tag => `<span class="tag">${tag}</span>`).join('');
        
        card.innerHTML = `
            <div class="community-banner"></div>
            <div class="community-avatar">
                <i class="fas ${icon}"></i>
            </div>
            <div class="community-content">
                <div class="community-title">
                    <h3><a href="#">${community.name}</a></h3>
                </div>
                <p class="community-description">
                    ${community.description}
                </p>
                <div class="community-tags">
                    ${tagsHtml}
                </div>
                <div class="community-stats">
                    <div class="stat-item">
                        <i class="fas fa-users"></i>
                        <span>${community.members_count.toLocaleString()} участников</span>
                    </div>
                    <div class="stat-item">
                        <i class="fas fa-comments"></i>
                        <span>${community.posts_count} обсуждений</span>
                    </div>
                </div>
                <div class="community-action">
                    <button class="join-btn ${community.is_joined ? 'joined' : ''}" 
                            data-community-id="${community.id}">
                        <i class="fas ${community.is_joined ? 'fa-check' : 'fa-plus'}"></i>
                        ${community.is_joined ? 'Вы в сообществе' : 'Присоединиться'}
                    </button>
                </div>
            </div>
        `;
        
        return card;
    }
    
    detectTags(community) {
        // Логика определения тегов
        const tags = [];
        
        if (community.name.includes('район') || community.name.includes('Район')) {
            tags.push('Район');
        }
        if (community.description.includes('транспорт') || community.name.includes('транспорт')) {
            tags.push('Транспорт');
        }
        if (community.description.includes('экология') || community.name.includes('парк')) {
            tags.push('Экология');
        }
        if (community.description.includes('дети') || community.name.includes('дети')) {
            tags.push('Дети');
        }
        if (community.description.includes('культура') || community.name.includes('культура')) {
            tags.push('Культура');
        }
        if (community.description.includes('недвижимость') || community.name.includes('недвижимость')) {
            tags.push('Недвижимость');
        }
        
        return tags.length > 0 ? tags : ['Сообщество'];
    }
    
    async handleCreateCommunity() {
        if (!this.userId) {
            this.showNotification('Для создания сообщества необходимо войти в систему', 'error');
            return;
        }
        
        this.showNotification('Функция создания сообщества в разработке', 'info');
        
        // В будущем здесь будет форма создания сообщества
        // const name = prompt('Введите название сообщества:');
        // const description = prompt('Введите описание сообщества:');
        // 
        // if (name && description) {
        //     await this.createCommunity(name, description);
        // }
    }
    
    async createCommunity(name, description) {
        try {
            const response = await fetch(COMMUNITIES_API.CREATE_COMMUNITY, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                credentials: 'include',
                body: JSON.stringify({
                    name: name,
                    description: description
                })
            });
            
            if (response.ok) {
                const result = await response.json();
                this.showNotification(result.message, 'success');
                // Перезагружаем сообщества
                await this.loadInitialCommunities();
            } else {
                const error = await response.json();
                throw new Error(error.detail || 'Ошибка создания сообщества');
            }
        } catch (error) {
            console.error('Ошибка создания сообщества:', error);
            this.showNotification(error.message || 'Ошибка создания сообщества', 'error');
        }
    }
    
    showNotification(message, type = 'info') {
        if (typeof notify !== 'undefined') {
            notify[type](message);
        } else {
            alert(message);
        }
    }
}

// Проверяем, находимся ли мы на странице сообществ
function isCommunitiesPage() {
    return window.location.pathname.includes('communities');
}

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', () => {
    if (isCommunitiesPage()) {
        const communitiesManager = new CommunitiesManager();
        communitiesManager.init();
        
        // Глобальный доступ для отладки
        window.communitiesManager = communitiesManager;
    }
});