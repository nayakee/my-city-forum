from typing import TypeVar, Generic
from pydantic import BaseModel
from sqlalchemy import delete, insert, select, update
from sqlalchemy.exc import IntegrityError


from app.database.database import Base
from app.exceptions.base import ObjectAlreadyExistsError


T = TypeVar('T', bound=BaseModel)

class BaseRepository(Generic[T]):
    model: Base = None
    schema: T = None

    def __init__(self, session):
        self.session = session

    async def get_filtered(
        self,
        limit: int | None = None,
        offset: int | None = None,
        *filter,
        **filter_by,
    ) -> list[T]:
        filter_by = {k: v for k, v in filter_by.items() if v is not None}
        filter_ = [v for v in filter if v is not None]

        query = select(self.model)
        
        if filter_:
            query = query.filter(*filter_)
        
        if filter_by:
            # Применяем фильтрацию по именованным параметрам
            for key, value in filter_by.items():
                if hasattr(self.model, key) and value is not None:
                    query = query.filter(getattr(self.model, key) == value)
        
        if limit is not None and offset is not None:
            query = query.limit(limit).offset(offset)
        
        result = await self.session.execute(query)
        result = [
            self.schema.model_validate(model, from_attributes=True)
            for model in result.scalars().all()
        ]

        return result

    async def get_all(self) -> list[T]:
        """Возращает все записи в БД из связаной таблицы"""
        return await self.get_filtered()

    async def get_one_or_none(self, **filter_by) -> None | T:
        query = select(self.model)
        
        # Применяем фильтрацию по именованным параметрам
        for key, value in filter_by.items():
            if hasattr(self.model, key) and value is not None:
                query = query.filter(getattr(self.model, key) == value)

        result = await self.session.execute(query)

        model = result.scalars().one_or_none()
        if model is None:
            return None
        result = self.schema.model_validate(model, from_attributes=True)
        return result

    async def get(self, id_: int) -> T | None:
        """Получение объекта по ID"""
        query = select(self.model).where(self.model.id == id_)
        result = await self.session.execute(query)
        model = result.scalars().one_or_none()
        if model is None:
            return None
        return self.schema.model_validate(model, from_attributes=True)

    async def add(self, data: T):
        try:
            # Check if data is a Pydantic model or a dictionary
            if hasattr(data, 'model_dump'):
                # It's a Pydantic model
                values = data.model_dump()
            else:
                # It's a dictionary
                values = data
            
            add_stmt = (
                insert(self.model).values(**values).returning(self.model)
            )
            # print(add_stmt.compile(compile_kwargs={"literal_binds": True}))

            result = await self.session.execute(add_stmt)

            model = result.scalars().one_or_none()
            if model is None:
                return None
            return self.schema.model_validate(model, from_attributes=True)

        except IntegrityError as exc:
            raise ObjectAlreadyExistsError from exc

    async def add_bulk(self, data: list[T]) -> None | T:
        """
        Метод для множественного добавления данных в таблицу
        """
        # Check if items in data are Pydantic models or dictionaries
        if data and hasattr(data[0], 'model_dump'):
            # Items are Pydantic models
            values = [item.model_dump() for item in data]
        else:
            # Items are dictionaries
            values = data
        
        add_stmt = insert(self.model).values(values)
        # print(add_stmt.compile(compile_kwargs={"literal_binds": True}))
        await self.session.execute(add_stmt)

    async def delete(self, *filters, **filter_by) -> None:
        delete_stmt = delete(self.model)
        if filters:
            delete_stmt = delete_stmt.where(*filters)
        if filter_by:
            # Применяем фильтрацию по именованным параметрам
            for key, value in filter_by.items():
                if hasattr(self.model, key) and value is not None:
                    delete_stmt = delete_stmt.where(getattr(self.model, key) == value)

        await self.session.execute(delete_stmt)
        await self.session.commit()

    async def edit(
        self, data: T, exclude_unset: bool = False, **filter_by
    ) -> None:
        edit_stmt = update(self.model)
        
        # Применяем фильтрацию по именованным параметрам
        for key, value in filter_by.items():
            if hasattr(self.model, key) and value is not None:
                edit_stmt = edit_stmt.where(getattr(self.model, key) == value)
        
        # Check if data is a Pydantic model or a dictionary
        if hasattr(data, 'model_dump'):
            # It's a Pydantic model
            values = data.model_dump(exclude_unset=exclude_unset)
        else:
            # It's a dictionary
            values = data
            
        edit_stmt = edit_stmt.values(**values)
        await self.session.execute(edit_stmt)
