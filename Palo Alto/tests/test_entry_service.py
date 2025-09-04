def test_entry_service_crud(entry_service, user_service, make_user, make_entry):
    # need a user
    u = user_service.register(make_user(username="writer", email="w@ex.com"))

    # create
    e = entry_service.create(make_entry(user_id=u.id, title="My Title", text="Body"))
    assert e.id is not None

    # get
    assert entry_service.get(e.id).title == "My Title"

    # list_for_user
    lst = entry_service.list_for_user(u.id)
    assert len(lst) == 1 and lst[0].id == e.id

    # full update
    e.title, e.text = "New Title", "New Body"
    entry_service.update_full(e)
    assert entry_service.get(e.id).text == "New Body"

    # partial update
    patched = entry_service.update_partial(e.id, title="Patched")
    assert patched.title == "Patched"

    # delete
    entry_service.remove(e.id)
    assert entry_service.get(e.id) is None


def test_entry_service_validations(entry_service, make_entry):
    # missing user_id
    from models.entry import Entry

    bad = Entry(id=None, user_id=None, title="t", text="x", created_at=None)
    try:
        entry_service.create(bad)
        assert False, "should have raised"
    except ValueError:
        pass

    # empty title
    try:
        entry_service.create(make_entry(user_id=1, title="", text="x"))
        assert False
    except ValueError:
        pass
