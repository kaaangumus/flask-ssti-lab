import pytest

from app import app


@pytest.fixture()
def client():
    app.config.update(TESTING=True, SECRET_KEY="test-secret")
    with app.test_client() as test_client:
        yield test_client


def login(client):
    return client.post(
        "/login",
        data={"username": "iskender", "password": "kontrtim34"},
        follow_redirects=True,
    )


def test_protected_page_redirects_to_login(client):
    response = client.get("/personnel")
    assert response.status_code == 302
    assert response.headers["Location"].endswith("/login")


def test_valid_credentials_open_dashboard(client):
    response = login(client)
    assert response.status_code == 200
    assert b"KONTROL" in response.data


def test_intentional_ssti_sink_evaluates_expression(client):
    login(client)
    response = client.post("/personnel", data={"search_term": "{{ 7 * 7 }}"})
    assert b"49" in response.data


def test_search_term_is_not_rendered_as_unescaped_html(client):
    login(client)
    response = client.post("/personnel", data={"search_term": "<script>alert(1)</script>"})
    assert b"<script>alert(1)</script>" not in response.data
    assert b"&lt;script&gt;alert(1)&lt;/script&gt;" in response.data


def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json == {"status": "ok"}
