def test_insight_service_crud(
    insight_service, entry_service, user_service, make_user, make_entry, make_insight
):
    u = user_service.register(make_user(username="ai", email="ai@ex.com"))
    e = entry_service.create(
        make_entry(user_id=u.id, title="AI Day", text="Optimistic")
    )

    # upsert + get
    ins = insight_service.upsert_for_entry(
        make_insight(entry_id=e.id, sentiment=0.7, themes=["work"], embedding=[0.1])
    )
    got = insight_service.get_for_entry(e.id)
    assert got is not None and abs(got.sentiment - 0.7) < 1e-6

    # update_partial
    patched = insight_service.update_partial(e.id, sentiment=0.2, themes=["life"])
    assert abs(patched.sentiment - 0.2) < 1e-6 and patched.themes == ["life"]

    # list_recent (smoke)
    lst = insight_service.list_recent(limit=3)
    assert isinstance(lst, list) and len(lst) >= 1

    # delete by id
    insight_service.delete(got.id)
    assert insight_service.get_by_id(got.id) is None


def test_insight_service_validations(insight_service, make_insight):
    # invalid sentiment
    bad = make_insight(entry_id=1, sentiment=2.0)
    try:
        insight_service.upsert_for_entry(bad)
        assert False, "expected ValueError"
    except ValueError:
        pass
