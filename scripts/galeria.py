#!/usr/bin/env python3
"""Galería de estilos de Quantum Linux.

  python scripts/galeria.py index           rearma index.json (con los «me gusta» = 👍 del issue de cada estilo)
  python scripts/galeria.py aprobar N       pasa el estilo del issue N (formulario «Subir un estilo») a estilos/

Lo corre la GitHub Action (.github/workflows/galeria.yml). Usa GITHUB_TOKEN y GITHUB_REPOSITORY si están.
"""
import datetime, io, json, os, re, sys, unicodedata, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO = os.environ.get("GITHUB_REPOSITORY", "QuantumLinux-arch/quantum-estilos")
TOKEN = os.environ.get("GITHUB_TOKEN", "")
SHELLS = {"caelestial", "serpantium", "nimbus", "aurora"}
# lo que un estilo puede cambiar (lo mismo que comparte Personalizar) y lo que nunca se publica
SECTIONS = {"appearance", "layout", "dock", "clock", "windows", "lock"}
PRIVATE = {"appearance": {"wallpaper", "customWallpapers", "desktopWidgets"}, "lock": {"city", "idleMinutes", "screenOffMinutes"}}


def api(path, method="GET", data=None):
    req = urllib.request.Request("https://api.github.com" + path, method=method,
                                 data=json.dumps(data).encode() if data is not None else None)
    req.add_header("Accept", "application/vnd.github+json")
    if TOKEN:
        req.add_header("Authorization", "Bearer " + TOKEN)
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read() or b"null")


def likes(issue):
    if not issue:
        return 0
    n, page = 0, 1
    try:
        while True:
            got = api(f"/repos/{REPO}/issues/{issue}/reactions?content=%2B1&per_page=100&page={page}")
            n += len(got)
            if len(got) < 100:
                return n
            page += 1
    except Exception as e:                       # sin red o sin permiso: se deja en 0 y se sigue
        print("aviso: no se pudieron contar los me gusta de", issue, e, file=sys.stderr)
        return 0


def index():
    out = []
    base = os.path.join(ROOT, "estilos")
    for slug in sorted(os.listdir(base)):
        d = os.path.join(base, slug)
        try:
            e = json.load(open(os.path.join(d, "estilo.json"), encoding="utf-8"))
            m = json.load(open(os.path.join(d, "meta.json"), encoding="utf-8")) if os.path.exists(os.path.join(d, "meta.json")) else {}
        except (OSError, ValueError) as err:
            print("aviso: estilo inválido", slug, err, file=sys.stderr)
            continue
        out.append({"id": slug, "name": e.get("name", slug), "description": e.get("description", ""), "author": e.get("author", ""),
                    "shell": e.get("shell", ""), "accent": (e.get("settings", {}).get("appearance", {}) or {}).get("accent", ""),
                    "likes": likes(m.get("issue")), "issue": m.get("issue"), "added": m.get("added", ""),
                    "estilo": f"estilos/{slug}/estilo.json", "captura": f"estilos/{slug}/captura.jpg"})
    out.sort(key=lambda s: (-s["likes"], s["added"]), reverse=False)
    data = {"version": 1, "updated": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%MZ"), "estilos": out}
    with open(os.path.join(ROOT, "index.json"), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print("index.json:", len(out), "estilos")


def slugify(name):
    s = unicodedata.normalize("NFD", name.lower())
    s = re.sub(r"[̀-ͯ]", "", s)
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")[:40] or "estilo"


def section(body, title):
    """El valor de una sección del formulario («### Título» y lo que sigue hasta la próxima)."""
    m = re.search(r"^###\s+" + re.escape(title) + r"\s*$(.*?)(?=^###\s|\Z)", body, re.S | re.M)
    v = m.group(1).strip() if m else ""
    return "" if v == "_No response_" else v


def clean(settings):
    out = {}
    for sec, vals in (settings or {}).items():
        if sec not in SECTIONS or not isinstance(vals, dict):
            continue
        out[sec] = {k: v for k, v in vals.items() if k not in PRIVATE.get(sec, set())}
    return out


def approve(number):
    issue = api(f"/repos/{REPO}/issues/{number}")
    body = issue.get("body") or ""
    name = section(body, "Nombre del estilo")[:40].strip()
    author = section(body, "Tu nombre o apodo")[:40].strip() or issue["user"]["login"]
    desc = re.sub(r"\s+", " ", section(body, "Descripción"))[:160].strip()
    code = section(body, "Estilo")
    code = re.sub(r"^```[a-z]*\s*|\s*```$", "", code.strip())
    try:
        st = json.loads(code)
    except ValueError:
        sys.exit("El estilo no es un JSON válido")
    if not isinstance(st, dict) or not isinstance(st.get("settings"), dict):
        sys.exit("Al estilo le faltan los ajustes")
    name = name or str(st.get("name", ""))[:40] or "Estilo"
    shot = section(body, "Captura")
    m = re.search(r"!\[[^\]]*\]\((https://[^)\s]+)\)", shot) or re.search(r'<img[^>]+src="(https://[^"]+)"', shot)
    if not m:
        sys.exit("No encontré la captura (arrástrala al campo «Captura»)")
    url = m.group(1)
    if not re.match(r"https://(github\.com/user-attachments/|user-images\.githubusercontent\.com/|private-user-images\.githubusercontent\.com/)", url):
        sys.exit("La captura tiene que estar subida a GitHub (arrástrala al formulario)")
    req = urllib.request.Request(url)
    if TOKEN:
        req.add_header("Authorization", "Bearer " + TOKEN)
    raw = urllib.request.urlopen(req, timeout=60).read(15 * 1024 * 1024)
    from PIL import Image                        # pip install pillow (en la Action)
    img = Image.open(io.BytesIO(raw)).convert("RGB")
    img.thumbnail((1280, 720))

    slug = slugify(name)
    base = os.path.join(ROOT, "estilos")
    s, n = slug, 2
    while os.path.exists(os.path.join(base, s)):
        s, n = f"{slug}-{n}", n + 1
    d = os.path.join(base, s)
    os.makedirs(d)
    shell = st.get("shell") if st.get("shell") in SHELLS else ""
    with open(os.path.join(d, "estilo.json"), "w", encoding="utf-8") as f:
        json.dump({"name": name, "description": desc or str(st.get("description", ""))[:160], "author": author,
                   "shell": shell, "settings": clean(st["settings"])}, f, ensure_ascii=False, indent=2)
        f.write("\n")
    with open(os.path.join(d, "meta.json"), "w", encoding="utf-8") as f:
        json.dump({"issue": number, "added": datetime.date.today().isoformat(), "github": issue["user"]["login"]}, f, indent=2)
        f.write("\n")
    img.save(os.path.join(d, "captura.jpg"), quality=88)
    print(s)


if __name__ == "__main__":
    if sys.argv[1:] == ["index"]:
        index()
    elif len(sys.argv) == 3 and sys.argv[1] == "aprobar" and sys.argv[2].isdigit():
        approve(int(sys.argv[2]))
    else:
        sys.exit(__doc__)
