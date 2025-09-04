def test_insight_upsert_and_get(
    insight_dao, entry_dao, user_dao, make_user, make_entry, make_insight
):
    u = user_dao.create(make_user())
    e = entry_dao.create(make_entry(user_id=u.id))
    ins = insight_dao.upsert_for_entry(make_insight(entry_id=e.id))
    got = insight_dao.find_by_entry(e.id)
    assert got is not None
    assert abs(got.sentiment - ins.sentiment) < 1e-6


def test_insight_update_partial(
    insight_dao, entry_dao, user_dao, make_user, make_entry, make_insight
):
    u = user_dao.create(make_user())
    e = entry_dao.create(make_entry(user_id=u.id))
    insight_dao.upsert_for_entry(make_insight(entry_id=e.id, themes=["old"]))
    patched = insight_dao.update_partial(e.id, themes=["new"])
    assert patched.themes == ["new"]


def test_insight_delete(
    insight_dao, entry_dao, user_dao, make_user, make_entry, make_insight
):
    u = user_dao.create(make_user())
    e = entry_dao.create(make_entry(user_id=u.id))
    ins = insight_dao.upsert_for_entry(make_insight(entry_id=e.id))
    insight_dao.delete(ins.id)
    assert insight_dao.find_by_id(ins.id) is None
