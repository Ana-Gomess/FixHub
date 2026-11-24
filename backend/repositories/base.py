from contextlib import contextmanager
import sqlite3
from typing import Iterator

from infrastructure.database import Database


@contextmanager
def usar_conexao(
    banco: Database, conexao: sqlite3.Connection | None = None
) -> Iterator[sqlite3.Connection]:

    if conexao is not None:
        yield conexao
    else:
        with banco.transacao() as nova_conexao:
            yield nova_conexao
