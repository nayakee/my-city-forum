# Импорты моделей убраны, чтобы избежать циклических зависимостей
# Модели импортируются непосредственно в функциях, где они нужны

from .favorites import FavoritePostModel

__all__ = ["FavoritePostModel"]