from sqlalchemy.orm import scoped_session, DeclarativeBase, Mapper
from sqlalchemy.exc import IntegrityError
from sqlalchemy import inspect
from sqlalchemy.sql.schema import Table
import os
from datetime import datetime
from typing import cast
import json

class SessionHelper:
    @staticmethod
    def session_add(model: DeclarativeBase, session: scoped_session) -> bool:
        if __name__ == 'test_config':
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            table_name = cast(Table, inspect(model).mapper.local_table).name
            primary_key_0 = str(getattr(model, inspect(model).mapper.primary_key[0].name))
            filename = f"{timestamp}{os.sep}{model.__tablename__}{os.sep}{primary_key_0}"
            file_text = json.dumps({
                column.key: getattr(model, column.key) for column in model.__table__.columns
            })
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            with open(filename, "w") as f:
                f.write(file_text)
            return True
        try:
            session.add(model)
        except IntegrityError as e:
            print(f"IntegrityError: {e}")
            session.rollback()
            return False
        return True
    @staticmethod
    def session_merge(model: DeclarativeBase, session: scoped_session) -> None:
        session.merge(model)