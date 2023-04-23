from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from typing import Type, Any
from karaoke_bot.repository.abstract_repository import AbstractRepository, T


class SQLAlchemyRepository(AbstractRepository[T]):
    """
    Repository that works with a SQLAlchemy ORM.
    """

    def __init__(self, engine: str, cls: Type) -> None:
        self.engine = create_engine(engine)
        self.Session = sessionmaker(bind=self.engine)
        self.cls = cls

    def add(self, obj: T) -> int:
        """Add object to the repository and return the id of the object."""
        session = self.Session()
        session.add(obj)
        session.commit()
        session.refresh(obj)
        return obj.id

    def get(self, id: int) -> T | None:
        """Get object from the repository by id."""
        session = self.Session()
        obj = session.query(self.cls).get(id)
        return obj

    def get_all(self, where: dict[str, Any] | None = None) -> list[T]:
        """Get all objects from the repository."""
        session = self.Session()
        if where is not None:
            query = session.query(self.cls).filter_by(**where)
        else:
            query = session.query(self.cls)
        return query.all()

    def update(self, obj: T) -> None:
        """Update object in the repository."""
        session = self.Session()
        session.merge(obj)
        session.commit()

    def delete(self, id: int) -> None:
        """Delete object from the repository by id."""
        session = self.Session()
        obj = session.query(self.cls).get(id)
        session.delete(obj)
        session.commit()

    def __del__(self) -> None:
        """Clean up resources."""
        self.engine.dispose()
