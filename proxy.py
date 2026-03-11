from flask import Flask, request, Response
import requests
from urllib.parse import urljoin
from bs4 import BeautifulSoup

app = Flask(__name__)

@app.route("/")
def home():
    return """
    <h2>Enhanced Web Proxy</h2>
    <form method="get" action="/proxy">
        <input type="text" name="url" placeholder="https://example.com" size="50">
        <button type="submit">Go</button>
    </form>
    """

@app.route("/proxy")
def proxy():
    url = request.args.get("url")
    if not url:
        return "No URL provided"
    if not url.startswith("http"):
        url = "https://" + url
    try:
        headers = {
            "User-Agent": request.headers.get("User-Agent"),
            "Accept": request.headers.get("Accept"),
            "Accept-Language": request.headers.get("Accept-Language"),
            "Referer": request.headers.get("Referer", ""),
        }
        resp = requests.get(url, headers=headers, allow_redirects=True, timeout=10)
        content_type = resp.headers.get("Content-Type", "")
        if "text/html" in content_type:
            soup = BeautifulSoup(resp.content, "html.parser")
            tag_attrs = {
                "a": "href", "img": "src", "script": "src",
                "link": "href", "form": "action", "iframe": "src",
                "source": "src", "video": "src"
            }
            for tag, attr in tag_attrs.items():
                for t in soup.find_all(tag):
                    if t.has_attr(attr):
                        link = t[attr]
                        if link.startswith(("javascript:", "mailto:", "#", "data:")):
                            continue
                        t[attr] = "/proxy?url=" + urljoin(url, link)
            return Response(str(soup), content_type="text/html")
        else:
            return Response(resp.content, content_type=content_type)
    except Exception as e:
        return f"Error fetching site: {e}"

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
