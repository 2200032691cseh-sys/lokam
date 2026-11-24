from django.urls import reverse


def test_lok_007_landing_is_server_rendered(client):
    response = client.get(reverse("landing"))

    assert response.status_code == 200
    html = response.content.decode()
    assert "A world of your own." in html
    assert 'href="#main"' in html and 'id="main"' in html
    assert 'href="/static/css/site.css"' in html
    assert "<script" not in html


def test_lok_007_not_found_uses_shared_layout(client, settings):
    settings.DEBUG = False
    response = client.get("/unavailable/")

    assert response.status_code == 404
    assert b"Page unavailable" in response.content
