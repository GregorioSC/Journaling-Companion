def test_entry_create_and_get(entry_dao, user_dao, make_user, make_entry):
    u = user_dao.create(make_user())
    e = entry_dao.create(make_entry(user_id=u.id, title="My Title", text="Body"))
    assert entry_dao.find_by_id(e.id).title == "My Title"


def test_entry_list_by_user(entry_dao, user_dao, make_user, make_entry):
    u = user_dao.create(make_user(username="writer", email="writer@ex.com"))
    entry_dao.create(make_entry(user_id=u.id, title="E1"))
    entry_dao.create(make_entry(user_id=u.id, title="E2"))
    assert len(entry_dao.list_by_user(u.id)) == 2


def test_entry_update_full(entry_dao, user_dao, make_user, make_entry):
    u = user_dao.create(make_user())
    e = entry_dao.create(make_entry(user_id=u.id, title="Old", text="old"))
    e.title = "New"
    entry_dao.update(e)
    assert entry_dao.find_by_id(e.id).title == "New"


def test_entry_update_partial(entry_dao, user_dao, make_user, make_entry):
    u = user_dao.create(make_user())
    e = entry_dao.create(make_entry(user_id=u.id, title="Partial", text="hi"))
    patched = entry_dao.update_partial(e.id, text="changed")
    assert patched.text == "changed"


def test_entry_delete(entry_dao, user_dao, make_user, make_entry):
    u = user_dao.create(make_user())
    e = entry_dao.create(make_entry(user_id=u.id))
    entry_dao.delete(e.id)
    assert entry_dao.find_by_id(e.id) is None
