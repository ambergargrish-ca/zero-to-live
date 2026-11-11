#!/usr/bin/env python3
"""Write dist/_routes.json for Cloudflare Pages so static files are served without invoking Pages Functions.

Without it, every image, stylesheet and script request runs your Function and counts against the request quota.
Cloudflare allows at most 100 include plus exclude rules, so folders are excluded with wildcards.

  python3 scripts/make_routes.py                 dist/, default static folders
  python3 scripts/make_routes.py build /static/* /images/*   another output dir and extra excludes

Excluded by default: /assets/*, and every top-level file in the output directory that is not HTML
(favicon.ico, robots.txt, sitemap.xml, llms.txt, manifest files)."""
import json, sys
from pathlib import Path

LIMIT = 100


def main():
    args = sys.argv[1:]
    dist = Path(args[0]) if args and not args[0].startswith("/") else Path("dist")
    extra = [a for a in args if a.startswith("/")]
    if not dist.is_dir():
        print(f"{dist}/ not found. Build first."); return 1
    exclude = ["/assets/*"] + extra
    for f in sorted(dist.iterdir()):
        if f.is_file() and f.suffix != ".html" and not f.name.startswith("_"):
            exclude.append(f"/{f.name}")
    exclude = list(dict.fromkeys(exclude))
    if 1 + len(exclude) > LIMIT:
        print(f"Too many rules ({1 + len(exclude)} > {LIMIT}). Group files into folders and exclude the folder."); return 1
    (dist / "_routes.json").write_text(json.dumps({"version": 1, "include": ["/*"], "exclude": exclude}, indent=2) + "\n")
    print(f"wrote {dist}/_routes.json with {len(exclude)} exclude rules")
    return 0


if __name__ == "__main__":
    sys.exit(main())
