// ====================================================
// СИСТЕМА УВЕДОМЛЕНИЙ
// ====================================================
class NotificationSystem {
    constructor() {
        this.container = null;
        this.notifications = new Set();
        this.defaultDuration = {
            success: 5000,
            error: 6000,
            info: 4000,
            warning: 4500
        };
        this.init();
    }
    
    init() {
        // Создаем контейнер для уведомлений
        this.container = document.createElement('div');
        this.container.id = 'notifications-container';
        this.container.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 9999;
            display: flex;
            flex-direction: column;
            gap: 10px;
            max-width: 400px;
            pointer-events: none;
        `;
        document.body.appendChild(this.container);
        
        // Добавляем стили
        this.addStyles();
    }
    
    addStyles() {
        if (!document.querySelector('#notification-styles')) {
            const style = document.createElement('style');
            style.id = 'notification-styles';
            style.textContent = `
                @keyframes notificationSlideIn {
                    from {
                        transform: translateX(100%);
                        opacity: 0;
                    }
                    to {
                        transform: translateX(0);
                        opacity: 1;
                    }
                }
                
                @keyframes notificationSlideOut {
                    from {
                        transform: translateX(0);
                        opacity: 1;
                    }
                    to {
                        transform: translateX(100%);
                        opacity: 0;
                    }
                }
                
                .notification-item {
                    background: white;
                    color: #333;
                    padding: 15px 20px;
                    border-radius: 8px;
                    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
                    animation: notificationSlideIn 0.3s ease-out;
                    word-break: break-word;
                    max-width: 100%;
                    pointer-events: auto;
                    position: relative;
                    overflow: hidden;
                    border-left: 4px solid transparent;
                    min-width: 300px;
                }
                
                .notification-item:hover {
                    box-shadow: 0 6px 16px rgba(0,0,0,0.2);
                    transform: translateY(-1px);
                    transition: all 0.2s;
                }
                
                .notification-item.success {
                    background: #e8f5e9;
                    color: #1b5e20;
                    border-left-color: #2e7d32;
                }
                
                .notification-item.error {
                    background: #ffebee;
                    color: #c62828;
                    border-left-color: #d32f2f;
                }
                
                .notification-item.info {
                    background: #e3f2fd;
                    color: #1565c0;
                    border-left-color: #1976d2;
                }
                
                .notification-item.warning {
                    background: #fff3e0;
                    color: #ef6c00;
                    border-left-color: #f57c00;
                }
                
                .notification-content {
                    display: flex;
                    align-items: flex-start;
                    gap: 12px;
                }
                
                .notification-icon {
                    font-size: 1.2rem;
                    flex-shrink: 0;
                    margin-top: 2px;
                }
                
                .notification-text {
                    flex-grow: 1;
                    line-height: 1.5;
                }
                
                .notification-close {
                    background: none;
                    border: none;
                    color: inherit;
                    opacity: 0.6;
                    cursor: pointer;
                    padding: 0;
                    margin-left: 10px;
                    font-size: 1.1rem;
                    flex-shrink: 0;
                    margin-top: 2px;
                }
                
                .notification-close:hover {
                    opacity: 1;
                }
                
                .notification-timer {
                    position: absolute;
                    bottom: 0;
                    left: 0;
                    height: 3px;
                    background: currentColor;
                    opacity: 0.3;
                    transition: width linear;
                }
            `;
            document.head.appendChild(style);
        }
    }
    
    show(message, type = 'info', duration = null) {
        // Преобразуем объект в строку
        const messageText = this.extractMessage(message);
        
        // Создаем элемент уведомления
        const notification = document.createElement('div');
        notification.className = `notification-item ${type}`;
        
        // Используем дефолтное время или переданное
        const showDuration = duration || this.defaultDuration[type] || 4000;
        
        notification.innerHTML = `
            <div class="notification-content">
                <div class="notification-icon">
                    <i class="${this.getIcon(type)}"></i>
                </div>
                <div class="notification-text">${this.escapeHtml(messageText)}</div>
                <button class="notification-close" title="Закрыть">
                    <i class="fas fa-times"></i>
                </button>
            </div>
            <div class="notification-timer" style="width: 100%"></div>
        `;
        
        this.container.appendChild(notification);
        this.notifications.add(notification);
        
        // Устанавливаем таймер для прогресс-бара
        const timer = notification.querySelector('.notification-timer');
        if (timer) {
            timer.style.transition = `width ${showDuration}ms linear`;
            setTimeout(() => {
                timer.style.width = '0%';
            }, 50);
        }
        
        // Обработчик закрытия
        const closeBtn = notification.querySelector('.notification-close');
        if (closeBtn) {
            closeBtn.addEventListener('click', () => this.remove(notification));
        }
        
        // Автоматическое удаление
        const autoRemove = setTimeout(() => {
            this.remove(notification);
        }, showDuration);
        
        // Останавливаем автоудаление при наведении
        notification.addEventListener('mouseenter', () => {
            clearTimeout(autoRemove);
            if (timer) {
                timer.style.transition = 'none';
                const currentWidth = parseFloat(timer.style.width) || 100;
                timer.style.width = `${currentWidth}%`;
            }
        });
        
        // Возобновляем автоудаление при уходе мыши
        notification.addEventListener('mouseleave', () => {
            const remainingTime = (parseFloat(timer.style.width) || 100) * showDuration / 100;
            if (timer) {
                timer.style.transition = `width ${remainingTime}ms linear`;
                setTimeout(() => {
                    timer.style.width = '0%';
                }, 50);
            }
            
            setTimeout(() => {
                if (this.notifications.has(notification)) {
                    this.remove(notification);
                }
            }, remainingTime);
        });
        
        return notification;
    }
    
    success(message, duration = null) {
        return this.show(message, 'success', duration);
    }
    
    error(message, duration = null) {
        return this.show(message, 'error', duration);
    }
    
    info(message, duration = null) {
        return this.show(message, 'info', duration);
    }
    
    warning(message, duration = null) {
        return this.show(message, 'warning', duration);
    }
    
    remove(notification) {
        if (!notification || !this.notifications.has(notification)) return;
        
        // Анимация исчезновения
        notification.style.animation = 'notificationSlideOut 0.3s ease-out forwards';
        
        setTimeout(() => {
            if (notification.parentNode === this.container) {
                this.container.removeChild(notification);
            }
            this.notifications.delete(notification);
        }, 300);
    }
    
    clearAll() {
        this.notifications.forEach(notification => {
            this.remove(notification);
        });
    }
    
    extractMessage(input) {
        if (typeof input === 'string') return input;
        if (input instanceof Error) return input.message;
        
        if (typeof input === 'object') {
            // Для отладки
            console.log('Получен объект:', input);
            
            // Ищем сообщение в различных полях
            const fields = ['detail', 'message', 'error', 'reason', 'description', 'status'];
            for (const field of fields) {
                if (input[field] && typeof input[field] === 'string') {
                    return input[field];
                }
            }
            
            // Если не нашли, пробуем JSON
            try {
                const jsonStr = JSON.stringify(input, null, 2);
                if (jsonStr.length < 200) {
                    return jsonStr;
                } else {
                    return 'Произошла ошибка (получен объект)';
                }
            } catch (e) {
                return 'Произошла ошибка';
            }
        }
        
        return String(input);
    }
    
    getIcon(type) {
        const icons = {
            success: 'fas fa-check-circle',
            error: 'fas fa-exclamation-circle',
            info: 'fas fa-info-circle',
            warning: 'fas fa-exclamation-triangle'
        };
        return icons[type] || 'fas fa-info-circle';
    }
    
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Создаем глобальный экземпляр
window.notify = new NotificationSystem();

// Глобальные функции для удобства
window.showSuccess = (message, duration) => notify.success(message, duration);
window.showError = (message, duration) => notify.error(message, duration);
window.showInfo = (message, duration) => notify.info(message, duration);

console.log('notifications.js загружен');