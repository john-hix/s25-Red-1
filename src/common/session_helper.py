from sqlalchemy.orm import scoped_session, DeclarativeBase, Mapper
from sqlalchemy.exc import IntegrityError
from sqlalchemy import inspect
from sqlalchemy.sql.schema import Table
import os
from typing import cast
import json
from uuid import UUID
import shutil
from src_dir import get_src_dir

class UUIDEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, UUID):
            return obj.hex
        return json.JSONEncoder.default(self, obj)

class SessionHelper:
    @staticmethod
    def session_add(model: DeclarativeBase, session: scoped_session, is_test: bool) -> bool:
        if is_test:
            test_output = get_src_dir() / "tests" / "test_configuration" / "regression" / "test_output"
            table_name = str(model.__tablename__)
            primary_key_0 = str(getattr(model, inspect(model).mapper.primary_key[0].name))
            filename = f"{str(test_output)}{os.sep}{table_name}{os.sep}{primary_key_0}.json"
            file_text = json.dumps({
                column.key: getattr(model, column.key) for column in model.__table__.columns
            }, cls=UUIDEncoder)
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
    def session_merge(model: DeclarativeBase, session: scoped_session, is_test: bool) -> None:
        if is_test:
            if os.path.exists("test_output"):
                shutil.rmtree("test_output")
            table_name = str(model.__tablename__)
            primary_key_0 = str(getattr(model, inspect(model).mapper.primary_key[0].name))
            filename = f"test_output/{os.sep}{table_name}{os.sep}{primary_key_0}.json"
            file_text = json.dumps({
                column.key: getattr(model, column.key) for column in model.__table__.columns
            }, cls=UUIDEncoder)
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            with open(filename, "w") as f:
                f.write(file_text)
            return

        session.merge(model)

