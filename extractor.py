import httpx
from bs4 import BeautifulSoup

async def extract_text_from_url(url: str) -> str | None:
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            r = await client.get(url, follow_redirects=True)
            if r.status_code != 200:
                return None
            html = r.text
    except Exception:
        return None

    soup = BeautifulSoup(html, "html.parser")
    paragraphs = soup.find_all('p')
    text = "\n\n".join(p.get_text().strip() for p in paragraphs if p.get_text().strip())
    return text[:40000] if text else None