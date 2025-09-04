import pytest
from dao.exceptions import DAOError


def test_user_create_and_get(user_dao, make_user):
    u = user_dao.create(make_user())
    assert u.id is not None
    assert user_dao.find_by_id(u.id).username == "alice"
    assert user_dao.find_by_email("alice@example.com").id == u.id


def test_user_update_full(user_dao, make_user):
    u = user_dao.create(make_user(username="bob", email="bob@ex.com"))
    u.username = "bobby"
    user_dao.update(u)
    assert user_dao.find_by_id(u.id).username == "bobby"


def test_user_update_partial(user_dao, make_user):
    u = user_dao.create(make_user(username="carol", email="carol@ex.com"))
    patched = user_dao.update_partial(u.id, age=30)
    assert patched.age == 30


def test_user_list_recent(user_dao, make_user):
    user_dao.create(make_user(username="u1", email="u1@ex.com"))
    user_dao.create(make_user(username="u2", email="u2@ex.com"))
    assert len(user_dao.list_recent(limit=2)) == 2


def test_user_delete(user_dao, make_user):
    u = user_dao.create(make_user(username="deleteme", email="del@ex.com"))
    user_dao.delete(u.id)
    assert user_dao.find_by_id(u.id) is None


def test_user_unique_email_violation(user_dao, make_user):
    user_dao.create(make_user(email="dup@ex.com"))
    with pytest.raises(DAOError):
        user_dao.create(make_user(username="other", email="dup@ex.com"))
