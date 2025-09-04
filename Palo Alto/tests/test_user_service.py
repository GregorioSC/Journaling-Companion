import pytest


def test_user_service_register_get_update_delete(user_service, make_user):
    # register
    u = user_service.register(make_user(username="sam", email="sam@ex.com", age=20))
    assert u.id is not None

    # get by id/email
    assert user_service.get_by_id(u.id).email == "sam@ex.com"
    assert user_service.get_by_email("sam@ex.com").id == u.id

    # full update
    u.username = "sammy"
    u.age = 21
    user_service.update_full(u)
    assert user_service.get_by_id(u.id).username == "sammy"

    # partial update
    patched = user_service.update_partial(u.id, age=22)
    assert patched.age == 22

    # list recent (smoke)
    rec = user_service.list_recent(limit=5)
    assert isinstance(rec, list) and len(rec) >= 1

    # delete
    user_service.remove(u.id)
    assert user_service.get_by_id(u.id) is None


def test_user_service_validations(user_service, make_user):
    # empty username
    with pytest.raises(ValueError):
        user_service.register(make_user(username="", email="a@b.com"))
    # bad age
    with pytest.raises(ValueError):
        user_service.register(make_user(username="ok", email="ok@b.com", age=999))
