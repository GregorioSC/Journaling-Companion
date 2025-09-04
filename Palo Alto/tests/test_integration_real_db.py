# # tests/test_integration_real_db.py
# import sys
# from pathlib import Path

# root = Path(__file__).resolve().parents[1]
# if str(root) not in sys.path:
#     sys.path.insert(0, str(root))

# import pytest
# from datetime import datetime

# from connection import get_connection
# from dao.user_dao import UserDAO
# from dao.entry_dao import EntryDAO
# from dao.insight_dao import InsightDAO
# from models.user import User
# from models.entry import Entry
# from models.insights import Insight


# # ---------- Real DB connection (transaction rollback per test) ----------
# @pytest.fixture()
# def real_conn():
#     """
#     Uses the real DB file from connection.get_connection().
#     Starts a connection and commits changes at the end
#     so test data will remain in your database.
#     """
#     conn = get_connection()
#     conn.execute("PRAGMA foreign_keys = ON;")
#     try:
#         yield conn
#         # ✅ persist inserts/updates/deletes
#         conn.commit()
#     finally:
#         conn.close()


# @pytest.fixture()
# def user_dao_real(real_conn):
#     # DAOs will use the injected connection (they won't commit/close)
#     return UserDAO(real_conn)


# @pytest.fixture()
# def entry_dao_real(real_conn):
#     return EntryDAO(real_conn)


# @pytest.fixture()
# def insight_dao_real(real_conn):
#     return InsightDAO(real_conn)


# # ---------- Helpers to make model objects ----------
# def make_user(
#     username="int_user",
#     email="int_user@example.com",
#     password="pw",
#     age=22,
#     gender="M",
#     id=None,
# ):
#     return User(
#         id=id, username=username, email=email, password=password, age=age, gender=gender
#     )


# def make_entry(
#     user_id: int, title="Integration Day", text="Real DB test", created_at=None, id=None
# ):
#     return Entry(id=id, text=text, user_id=user_id, created_at=created_at, title=title)


# def make_insight(
#     entry_id: int, sentiment=0.42, themes=None, embedding=None, created_at=None, id=None
# ):
#     if themes is None:
#         themes = ["testing", "integration"]
#     if embedding is None:
#         embedding = [0.01, 0.02, 0.03]
#     if created_at is None:
#         created_at = datetime.utcnow()
#     return Insight(
#         id=id,
#         entry_id=entry_id,
#         sentiment=sentiment,
#         themes=themes,
#         embedding=embedding,
#         created_at=created_at,
#     )


# # =========================
# #         USER DAO
# # =========================
# def test_user_dao_crud_real_db(user_dao_real):
#     # create
#     u = make_user(
#         username="int_alice", email="int_alice@example.com", age=30, gender="F"
#     )
#     saved = user_dao_real.create(u)
#     assert saved.id is not None

#     # find_by_id
#     got = user_dao_real.find_by_id(saved.id)
#     assert got is not None and got.username == "int_alice"

#     # find_by_email
#     by_email = user_dao_real.find_by_email("int_alice@example.com")
#     assert by_email is not None and by_email.id == saved.id

#     # update (full)
#     saved.username = "int_alicia"
#     saved.age = 31
#     user_dao_real.update(saved)
#     again = user_dao_real.find_by_id(saved.id)
#     assert again.username == "int_alicia" and again.age == 31

#     # update_partial
#     patched = user_dao_real.update_partial(
#         saved.id, email="int_alicia_new@example.com", gender="F"
#     )
#     assert patched is not None and patched.email == "int_alicia_new@example.com"

#     # list_recent (smoke)
#     recent = user_dao_real.list_recent(limit=5)
#     assert isinstance(recent, list)

#     # delete
#     user_dao_real.delete(saved.id)
#     assert user_dao_real.find_by_id(saved.id) is None


# # =========================
# #        ENTRY DAO
# # =========================
# def test_entry_dao_crud_real_db(user_dao_real, entry_dao_real):
#     # need a user to own the entry
#     owner = user_dao_real.create(
#         make_user(username="int_writer", email="int_writer@example.com")
#     )

#     # create
#     e = entry_dao_real.create(
#         make_entry(user_id=owner.id, title="First Real Entry", text="Hello real DB")
#     )
#     assert e.id is not None

#     # find_by_id
#     got = entry_dao_real.find_by_id(e.id)
#     assert got is not None and got.title == "First Real Entry"

#     # list_by_user
#     lst = entry_dao_real.list_by_user(owner.id, limit=10)
#     assert len(lst) >= 1 and any(x.id == e.id for x in lst)

#     # update (full)
#     e.title, e.text = "Edited Title", "Edited body"
#     entry_dao_real.update(e)
#     again = entry_dao_real.find_by_id(e.id)
#     assert again.title == "Edited Title" and again.text == "Edited body"

#     # update_partial
#     patched = entry_dao_real.update_partial(e.id, title="Patched Title")
#     assert patched is not None and patched.title == "Patched Title"

#     # delete
#     entry_dao_real.delete(e.id)
#     assert entry_dao_real.find_by_id(e.id) is None


# # =========================
# #       INSIGHT DAO
# # =========================
# def test_insight_dao_crud_real_db(user_dao_real, entry_dao_real, insight_dao_real):
#     # bootstrap user + entry
#     owner = user_dao_real.create(
#         make_user(username="int_ai", email="int_ai@example.com")
#     )
#     e = entry_dao_real.create(
#         make_entry(user_id=owner.id, title="AI Day", text="Feeling optimistic")
#     )

#     # upsert_for_entry (create)
#     ins = make_insight(
#         entry_id=e.id, sentiment=0.7, themes=["work"], embedding=[0.1, 0.2]
#     )
#     insight_dao_real.upsert_for_entry(ins)

#     # find_by_entry
#     got = insight_dao_real.find_by_entry(e.id)
#     assert got is not None and abs(got.sentiment - 0.7) < 1e-6

#     # find_by_id
#     same = insight_dao_real.find_by_id(got.id)
#     assert same is not None and same.id == got.id

#     # upsert_for_entry (update)
#     ins2 = make_insight(
#         entry_id=e.id, sentiment=0.9, themes=["career"], embedding=[0.9, 0.8]
#     )
#     insight_dao_real.upsert_for_entry(ins2)
#     got2 = insight_dao_real.find_by_entry(e.id)
#     assert (
#         got2 is not None
#         and abs(got2.sentiment - 0.9) < 1e-6
#         and got2.themes == ["career"]
#     )

#     # update_partial
#     patched = insight_dao_real.update_partial(
#         e.id, sentiment=0.3, themes=["career", "family"]
#     )
#     assert (
#         patched is not None
#         and abs(patched.sentiment - 0.3) < 1e-6
#         and patched.themes == ["career", "family"]
#     )

#     # list_recent (smoke)
#     recent = insight_dao_real.list_recent(limit=3)
#     assert isinstance(recent, list) and len(recent) >= 1

#     # delete_by_entry
#     insight_dao_real.delete_by_entry(e.id)
#     assert insight_dao_real.find_by_entry(e.id) is None

#     # recreate and delete by id
#     insight_dao_real.upsert_for_entry(make_insight(entry_id=e.id, sentiment=0.4))
#     got3 = insight_dao_real.find_by_entry(e.id)
#     insight_dao_real.delete(got3.id)
#     assert insight_dao_real.find_by_entry(e.id) is None
