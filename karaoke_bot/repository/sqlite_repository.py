"""
SQLite repository class module.
"""
import sqlite3
from inspect import get_annotations
from typing import Type, Any
from karaoke_bot.repository.abstract_repository import AbstractRepository, T


class SQLiteRepository(AbstractRepository[T]):
    """
    Repository that works with an SQLite database.
    """

    def __init__(self, db_file: str, cls: Type) -> None:
        self.db_file = db_file
        self.table_name = cls.__name__.lower()
        self.fields = get_annotations(cls, eval_str=True)
        self.fields.pop("pk")

        self._create_table()

    def _create_table(self) -> None:
        with sqlite3.connect(self.db_file) as con:
            cur = con.cursor()
            cur.execute(
                f"""CREATE TABLE IF NOT EXISTS {self.table_name}(
                'id' INTEGER UNIQUE, {self.fields_str},
                PRIMARY KEY("id" AUTOINCREMENT)
            );"""
            )
        con.commit()

    def add(self, obj: T) -> int:
        """
        Add an object to the repo and return its id.
        """
        if getattr(obj, "pk", None) != 0:
            raise ValueError(f"trying to add object {obj} with filled 'pk' attribute")
        marks = ", ".join("?" * len(self.fields))
        values = [getattr(obj, f) for f in self.fields]
        with sqlite3.connect(self.db_file) as con:
            cur = con.cursor()
            cur.execute("""PRAGMA foreign_keys = ON""")
            cur.execute(
                f"""INSERT INTO {self.table_name}({self.fields_str}) VALUES ({marks})""",
                values,
            )
            pk = cur.lastrowid
            assert (
                pk is not None
            )  # something must go terribly wrong for this not to be the case
            obj.pk = pk
        con.close()
        return obj.pk

    def _covert_row(self, row_: list[str]) -> T:
        fields = dict(zip(self.fields, row_[1:]))
        fields["pk"] = row_[0]
        res_obj = self.entry_cls(**fields)
        return res_obj

    def get(self, pk: int) -> T | None:
        """
        Get and object with a fixed id.
        """
        with sqlite3.connect(self.db_file) as con:
            cur = con.cursor()
            row = cur.execute(
                f"""SELECT * FROM {self.table_name} WHERE id=={pk}"""
            ).fetchone()
        con.close()
        if not row:
            return None
        return self._covert_row(row)

    def get_all(self, where: dict[str, Any] | None = None) -> list[T] | None:
        """
        Get all entries that satisfy all "where" conditions, return all
        entries if where is None.
        where is a dictionary {"entry_field": value}
        """
        with sqlite3.connect(self.db_file) as con:
            cur = con.cursor()
            query = f"""SELECT * FROM {self.table_name}"""
            mark_replacements = []
            if where:
                fields = " AND ".join([f"{name} LIKE ?" for name in where])
                query += f" WHERE {fields}"
                mark_replacements = list(map(str, where.values()))
            rows = cur.execute(query, mark_replacements).fetchall()
        con.close()
        if rows:
            res = [self._covert_row(row) for row in rows]
            return res
        return None

    def update(self, obj: T) -> None:
        """
        Update an entry with the same pk as the object.
        """
        if obj.pk == 0:
            raise ValueError("trying to update an object with no primary key")
        new_values = [getattr(obj, x) for x in self.fields]
        with sqlite3.connect(self.db_file) as con:
            cur = con.cursor()
            cur.execute(
                f"""UPDATE {self.table_name} SET {self.fields_with_marks}
                WHERE id=={obj.pk}""",
                new_values,
            )
            if cur.rowcount == 0:
                raise ValueError(
                    "trying to update an object with an unknown primary key"
                )

        con.close()

    def delete(self, pk: int) -> None:
        """
        Remove an entry.
        """
        with sqlite3.connect(self.db_file) as con:
            cur = con.cursor()
            cur.execute(f"""DELETE FROM {self.table_name} WHERE id=={pk}""")
        con.close()
