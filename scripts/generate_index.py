"""
reports/ 폴더의 HTML 파일을 스캔해서 index.html을 생성합니다.

각 HTML 파일에서 다음 정보를 추출:
- <title> 태그: 문서 제목
- <meta name="description">: 요약 (없으면 생략)
- 파일명 앞의 YYYY-MM-DD: 날짜
- 파일의 마지막 수정 시간 (날짜 없을 때 대체용)
"""

import os
import re
from pathlib import Path
from datetime import datetime
from html import escape

REPORTS_DIR = Path("reports")
OUTPUT_FILE = Path("index.html")

# 파일명 패턴: 2026-04-18-제목.html
DATE_PATTERN = re.compile(r"^(\d{4}-\d{2}-\d{2})[-_](.+)\.html$")


def extract_title(html: str, fallback: str) -> str:
    match = re.search(r"<title>(.*?)</title>", html, re.IGNORECASE | re.DOTALL)
    if match:
        title = match.group(1).strip()
        if title:
            return title
    return fallback


def extract_description(html: str) -> str:
    match = re.search(
        r'<meta\s+name=["\']description["\']\s+content=["\'](.*?)["\']',
        html,
        re.IGNORECASE,
    )
    if match:
        return match.group(1).strip()
    return ""


def collect_reports():
    reports = []
    if not REPORTS_DIR.exists():
        return reports

    for path in REPORTS_DIR.glob("*.html"):
        filename = path.name
        match = DATE_PATTERN.match(filename)

        if match:
            date_str = match.group(1)
            slug = match.group(2).replace("-", " ").replace("_", " ")
        else:
            # 날짜 없는 파일은 수정시간 사용
            mtime = datetime.fromtimestamp(path.stat().st_mtime)
            date_str = mtime.strftime("%Y-%m-%d")
            slug = path.stem.replace("-", " ").replace("_", " ")

        html = path.read_text(encoding="utf-8", errors="ignore")
        title = extract_title(html, slug)
        description = extract_description(html)

        reports.append({
            "filename": filename,
            "date": date_str,
            "title": title,
            "description": description,
        })

    # 최신순 정렬
    reports.sort(key=lambda r: r["date"], reverse=True)
    return reports


def render_html(reports):
    items_html = []
    for r in reports:
        desc_html = (
            f'<p class="desc">{escape(r["description"])}</p>'
            if r["description"] else ""
        )
        items_html.append(f"""      <li class="item">
        <a href="reports/{escape(r['filename'])}">
          <time datetime="{escape(r['date'])}">{escape(r['date'])}</time>
          <h2>{escape(r['title'])}</h2>
          {desc_html}
        </a>
      </li>""")

    items_joined = "\n".join(items_html) if items_html else \
        '      <li class="empty">아직 등록된 문서가 없습니다.</li>'

    updated = datetime.now().strftime("%Y-%m-%d")

    return f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Reports</title>
<style>
  :root {{
    --bg: #fafaf7;
    --fg: #1a1a1a;
    --muted: #6b6b6b;
    --line: #e5e3dc;
    --accent: #1a1a1a;
  }}
  * {{ box-sizing: border-box; }}
  body {{
    margin: 0;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Pretendard",
                 "Apple SD Gothic Neo", "Noto Sans KR", sans-serif;
    background: var(--bg);
    color: var(--fg);
    line-height: 1.6;
    -webkit-font-smoothing: antialiased;
  }}
  .wrap {{
    max-width: 720px;
    margin: 0 auto;
    padding: 64px 24px 96px;
  }}
  header {{
    border-bottom: 1px solid var(--line);
    padding-bottom: 24px;
    margin-bottom: 32px;
  }}
  header h1 {{
    margin: 0 0 8px;
    font-size: 28px;
    font-weight: 600;
    letter-spacing: -0.02em;
  }}
  header p {{
    margin: 0;
    color: var(--muted);
    font-size: 14px;
  }}
  ul {{
    list-style: none;
    padding: 0;
    margin: 0;
  }}
  .item {{
    border-bottom: 1px solid var(--line);
  }}
  .item a {{
    display: block;
    padding: 24px 0;
    color: inherit;
    text-decoration: none;
    transition: opacity 0.15s ease;
  }}
  .item a:hover {{
    opacity: 0.6;
  }}
  .item time {{
    display: block;
    font-size: 13px;
    color: var(--muted);
    margin-bottom: 6px;
    font-variant-numeric: tabular-nums;
  }}
  .item h2 {{
    margin: 0 0 6px;
    font-size: 18px;
    font-weight: 500;
    letter-spacing: -0.01em;
  }}
  .item .desc {{
    margin: 0;
    color: var(--muted);
    font-size: 14px;
  }}
  .empty {{
    padding: 48px 0;
    text-align: center;
    color: var(--muted);
  }}
  footer {{
    margin-top: 48px;
    font-size: 12px;
    color: var(--muted);
  }}
  @media (max-width: 480px) {{
    .wrap {{ padding: 40px 20px 64px; }}
    header h1 {{ font-size: 24px; }}
    .item h2 {{ font-size: 16px; }}
  }}
</style>
</head>
<body>
  <div class="wrap">
    <header>
      <h1>Reports</h1>
      <p>총 {len(reports)}개의 문서</p>
    </header>
    <ul>
{items_joined}
    </ul>
    <footer>Last updated: {updated}</footer>
  </div>
</body>
</html>
"""


def main():
    reports = collect_reports()
    html = render_html(reports)
    OUTPUT_FILE.write_text(html, encoding="utf-8")
    print(f"Generated index.html with {len(reports)} report(s)")


if __name__ == "__main__":
    main()
