from __future__ import annotations

from navil.recon.spider import extract_forms, extract_links

HTML = """
<html>
  <body>
    <a href="/a">A</a>
    <a href="https://example.com/b">B</a>
    <form action="/submit" method="post">
      <input name="username" />
      <input name="password" />
    </form>
  </body>
</html>
"""


def test_extract_links_and_forms() -> None:
    links = extract_links("https://example.com", HTML)
    assert "https://example.com/a" in links
    assert "https://example.com/b" in links

    forms = extract_forms("https://example.com", HTML)
    assert forms[0].action == "https://example.com/submit"
    assert forms[0].method == "POST"
    assert forms[0].fields == ["username", "password"]
