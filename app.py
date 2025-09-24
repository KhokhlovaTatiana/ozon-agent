import os
import re
import requests
from bs4 import BeautifulSoup
from flask import Flask, request, jsonify

app = Flask(__name__)

def safe_text(el):
    return el.get_text(strip=True) if el else None

def parse_ozon(url: str) -> dict:
    headers = {"User-Agent": "Mozilla/5.0"}
    r = requests.get(url, headers=headers, timeout=15)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")

    title = safe_text(soup.find("h1"))
    price_text = None
    price_node = soup.find("span", {"class": re.compile(r"^tsBody")})
    if price_node:
        price_text = re.sub(r"[^\d]", "", price_node.get_text())
    price = int(price_text) if price_text else None

    return {"title": title, "price": price, "url": url}

@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.get_json(silent=True) or {}
    url = data.get("url")
    if not url:
        return jsonify({"error": "url is required"}), 400
    try:
        product = parse_ozon(url)
        return jsonify({"product": product})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
