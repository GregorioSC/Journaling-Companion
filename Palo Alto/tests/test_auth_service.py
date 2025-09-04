# tests/test_auth_service.py
def test_register_and_login(user_dao, make_user):
    from services.auth_service import AuthService
    from security.passwords import verify_password

    auth = AuthService(user_dao)

    u = make_user(username="auth", email="auth@ex.com", password="p@ssw0rd")
    saved = auth.register(u)
    assert saved.id is not None
    # password stored as hash
    assert saved.password != "p@ssw0rd"
    assert verify_password("p@ssw0rd", saved.password)

    token = auth.login("auth@ex.com", "p@ssw0rd")
    assert isinstance(token, str) and len(token) > 10

    bad = auth.login("auth@ex.com", "wrong")
    assert bad is None
