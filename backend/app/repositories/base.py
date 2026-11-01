from typing import Generic, TypeVar, Type, List, Optional
from sqlalchemy.orm import Session
from ..db.database import Base

T = TypeVar("T", bound=Base)

class BaseRepository(Generic[T]):
    def __init__(self, model: Type[T]):
        self.model = model

    def get_by_id(self, db: Session, id: int) -> Optional[T]:
        return db.query(self.model).filter(self.model.id == id).first()

    def get_all(self, db: Session, skip: int = 0, limit: int = 100) -> List[T]:
        return db.query(self.model).offset(skip).limit(limit).all()

    def create(self, db: Session, obj_in):
        db_obj = self.model(**obj_in)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
