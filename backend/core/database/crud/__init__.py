import json
from sqlmodel import SQLModel, Session, asc, desc, col, select, func

from typing import Any, Generic, Optional, Type, TypeVar
from fastapi import HTTPException
from fastapi.encoders import jsonable_encoder

ModelType = TypeVar("ModelType", bound=SQLModel)
CreateSchemaType = TypeVar("CreateSchemaType", bound=SQLModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=SQLModel)

FilterParseException = HTTPException(
    status_code=400, detail="Filter parsing failed. Invalid attributes present."
)

OrderParseException = HTTPException(
    status_code=400, detail="Order parsing failed. Invalid attributes present."
)

JSONParseError = HTTPException(status_code=400, detail="Invalid JSON string")


def parse_filter(filters: dict, parent: Any) -> list:
    """
    Convert filter dict into filter list

    :param filters: Dict to be converted
    :param parent: Parent object / model
    :return: Filter list
    """
    new_filters = []

    for k, v in filters.items():

        # Detect comparison
        gt = "__gt" in k
        ge = "__ge" in k
        lt = "__lt" in k
        le = "__le" in k

        # Remove suffixes
        if gt or ge or lt or le:
            k = k[:-4]

        try:
            attr = getattr(parent, k)

            # Construct filter expressions
            if isinstance(v, dict):
                new_filters += parse_filter(v, attr.property.mapper.class_)
            else:
                if gt:
                    new_filters.append(col(attr) > v)
                elif ge:
                    new_filters.append(col(attr) >= v)
                elif lt:
                    new_filters.append(col(attr) < v)
                elif le:
                    new_filters.append(col(attr) <= v)
                else:
                    new_filters.append(col(attr) == v)
        except AttributeError:
            raise FilterParseException

    return new_filters


def parse_order(order: list[str], parent) -> list[str]:
    """
    Convert order list into usable version in SQLAlchemy

    :param order: Order list
    :param parent: Parent object
    :return: New order list
    """
    for i, v in enumerate(order):
        a = "__a" in v
        d = "__d" in v

        if a or d:
            v = v[:-3]

        if not hasattr(parent, v):
            raise OrderParseException

        order[i] = (
            asc(col(getattr(parent, v)))
            if a and not d
            else desc(col(getattr(parent, v)))
            if not a and d
            else col(getattr(parent, v))
        )
    return order


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType]):
        self.model = model

    def get_count(self, db: Session) -> int:
        """
        Get total number of objects in database.
        :param db: Database Session to be used
        """
        # return db.query(self.model).count()
        return db.scalar(select(func.count()).select_from(self.model))

    def get(self, db: Session, uuid: Any) -> Optional[ModelType]:
        # return db.query(self.model).filter(self.model.id == id).first()
        return db.execute(select(self.model).filter(self.model.uuid == uuid)).first()

    def get_multi(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[dict | str] = None,
        group: Optional[list[str] | str] = None,
        order: Optional[list[str] | str] = None
    ) -> list[ModelType]:

        q = select(self.model)

        # Add filter to query
        if filters is not None:
            if isinstance(filters, str):
                try:
                    filters = json.loads(filters)
                except json.decoder.JSONDecodeError:
                    raise JSONParseError

                if not isinstance(filters, dict):
                    raise JSONParseError

            q = q.filter(*parse_filter(filters, self.model))

        # Add grouping to query
        if group is not None:
            if isinstance(group, str):
                try:
                    group = json.loads(group)
                except json.decoder.JSONDecodeError:
                    raise JSONParseError

                if not isinstance(group, list):
                    raise JSONParseError

            q = q.group_by(*group)

        # Add ordering to query
        if order is not None:
            if isinstance(order, str):
                try:
                    order = json.loads(order)
                except json.decoder.JSONDecodeError:
                    raise JSONParseError
                if not isinstance(order, list):
                    raise JSONParseError

            q = q.order_by(*parse_order(order, self.model))

        return db.execute(q.offset(skip).limit(limit)).all()

    def create(self, db: Session, *, obj_in: CreateSchemaType) -> ModelType:
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self.model(**obj_in_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self,
        db: Session,
        *,
        db_obj: ModelType,
        obj_in: UpdateSchemaType | dict[str, Any]
    ) -> ModelType:
        obj_data = jsonable_encoder(db_obj)

        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)

        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def remove(self, db: Session, *, uuid: Any) -> ModelType:
        obj = db.query(self.model).get(uuid)
        db.delete(obj)
        db.commit()
        return obj
