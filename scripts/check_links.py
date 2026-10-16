"""Check that every internal link, image, script, stylesheet and #anchor in the built site resolves.

    python3 scripts/check_links.py public

External links are not checked (they change outside our control). Exits with
status 1 and a list of problems if anything is broken.
"""
import posixpath
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

SITE_HOSTS = {"shamzehe.github.io", "localhost", "127.0.0.1"}
SKIP_SCHEMES = {"mailto", "tel", "data", "javascript"}


class PageScan(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.urls = []
        self.ids = set()

    def handle_starttag(self, tag, attrs):
        a = {k: v for k, v in attrs if v is not None}
        if a.get("id"):
            self.ids.add(a["id"])
        for key in ("href", "src"):
            if a.get(key):
                self.urls.append(a[key])
        for candidate in a.get("srcset", "").split(","):
            url = candidate.strip().split(" ")[0]
            if url:
                self.urls.append(url)


def resolve(root, page_dir, path):
    if not path.startswith("/"):
        path = posixpath.normpath(posixpath.join(page_dir, path)) + ("/" if path.endswith("/") else "")
    target = root / unquote(path).lstrip("/")
    if path.endswith("/") or target.is_dir():
        target = target / "index.html"
    return target


def main(root_arg):
    root = Path(root_arg).resolve()
    scans = {}
    for html in sorted(root.rglob("*.html")):
        scan = PageScan()
        scan.feed(html.read_text(encoding="utf-8"))
        scans[html] = scan

    problems = []
    for html, scan in scans.items():
        page_dir = "/" + html.parent.relative_to(root).as_posix()
        for url in scan.urls:
            parts = urlsplit(url)
            if parts.scheme in SKIP_SCHEMES:
                continue
            if parts.scheme in ("http", "https") and parts.hostname not in SITE_HOSTS:
                continue
            target = html if not parts.path else resolve(root, page_dir, parts.path)
            where = html.relative_to(root).as_posix()
            if not target.exists():
                problems.append(f"{where}: broken link {url}")
                continue
            if parts.fragment and target.suffix == ".html":
                ids = scans[target].ids if target in scans else set()
                if unquote(parts.fragment) not in ids:
                    problems.append(f"{where}: missing anchor #{parts.fragment} in {url or 'this page'}")

    if problems:
        print(f"{len(problems)} broken link(s):")
        print("\n".join(f"  - {p}" for p in sorted(set(problems))))
        return 1
    print(f"All internal links OK across {len(scans)} pages.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "public"))
