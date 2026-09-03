#!/usr/bin/env python3
"""
Generates an animated "jet over contribution grid" SVG using a GitHub
user's REAL contribution calendar (last 34 weeks, same layout as
GitHub's own heatmap: 34 columns x 7 rows).
"""

import os
import sys
import json
import urllib.request
from pathlib import Path

USERNAME = os.environ.get("GH_USERNAME", "Er-prince-kumar")
TOKEN = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
OUTPUT = os.environ.get("OUTPUT_PATH", "dist/github-jet.svg")

COLS = 34
ROWS = 7
CELL = 11
STEP = 14
GRID_X = 20
GRID_Y = 15
WIDTH = 513
HEIGHT = 170
JET_X_START = 35
JET_X_END = 478
LOOP_DUR = 20
MAX_TARGETS = 12
FLASH_COLOR = "#39d353"
BULLET_COLOR = "#7ee787"
BLAST_COLOR = "#56d364"
PAD_Y = 128

QUERY = """
  query($login: String!) {
    user(login: $login) {
      contributionsCollection {
        contributionCalendar {
          weeks {
            contributionDays {
              date
              contributionCount
              color
            }
          }
        }
      }
    }
  }
"""

LEVEL_COLORS = {
    0: "#161b22",
    1: "#0e4429",
    2: "#006d32",
    3: "#26a641",
    4: "#39d353"
}

def fetch_weeks():
    # 1. Try GraphQL if token exists
    if TOKEN:
        try:
            print("Fetching via GitHub GraphQL API...")
            req = urllib.request.Request(
                "https://api.github.com/graphql",
                data=json.dumps({"query": QUERY, "variables": {"login": USERNAME}}).encode("utf-8"),
                headers={
                    "Authorization": f"bearer {TOKEN}",
                    "Content-Type": "application/json",
                    "User-Agent": "Mozilla/5.0"
                }
            )
            with urllib.request.urlopen(req) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                if not data.get("errors"):
                    return data["data"]["user"]["contributionsCollection"]["contributionCalendar"]["weeks"]
        except Exception as e:
            print(f"GraphQL fetch failed ({e}), falling back to public API...")

    # 2. Public contributions API
    try:
        print(f"Fetching via public contributions API for {USERNAME}...")
        url = f"https://github-contributions-api.jogruber.de/v4/{USERNAME}?y=last"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            contributions = data.get("contributions", [])
            # Group into weeks of 7 days
            # Pad so that length is divisible by 7
            rem = len(contributions) % 7
            if rem != 0:
                contributions = contributions[rem:]
            weeks = []
            for i in range(0, len(contributions), 7):
                chunk = contributions[i:i+7]
                days = []
                for d in chunk:
                    level = d.get("level", 0)
                    days.append({
                        "date": d.get("date"),
                        "contributionCount": d.get("count", 0),
                        "color": LEVEL_COLORS.get(level, "#161b22")
                    })
                weeks.append({"contributionDays": days})
            return weeks
    except Exception as e:
        print(f"Public API error: {e}. Generating default active calendar...")
        
    # 3. Fallback dummy data if offline
    weeks = []
    for w in range(COLS):
        days = []
        for r in range(ROWS):
            days.append({
                "date": f"2026-01-{w+1:02d}",
                "contributionCount": 0 if (w + r) % 3 != 0 else (w % 5),
                "color": "#39d353" if (w == 30 and r == 2) else ("#0e4429" if (w + r) % 3 == 0 else "#161b22")
            })
        weeks.append({"contributionDays": days})
    return weeks

def build_cells(weeks):
    recent = weeks[-COLS:]
    pad_count = COLS - len(recent)
    padded = []
    for _ in range(pad_count):
        padded.append({
            "contributionDays": [
                {"contributionCount": 0, "color": "#161b22", "date": None}
                for _ in range(ROWS)
            ]
        })
    padded.extend(recent)

    cells = []
    for col, week in enumerate(padded):
        for row, day in enumerate(week["contributionDays"]):
            cells.append({
                "col": col,
                "row": row,
                "x": GRID_X + col * STEP,
                "y": GRID_Y + row * STEP,
                "color": day.get("color") or "#161b22",
                "count": day.get("contributionCount", 0),
                "date": day.get("date")
            })
    return cells

def pick_targets(cells):
    active = [c for c in cells if c["count"] > 0]
    if not active:
        # Fallback to some decorative targets if user has zero public commits
        active = [cells[len(cells)//2], cells[len(cells)//3], cells[len(cells)*2//3]]
    active.sort(key=lambda c: c["count"], reverse=True)
    top = active[:MAX_TARGETS]
    top.sort(key=lambda c: (c["col"], c["row"]))
    return top

def key_time_for_col(col, direction):
    span = 0.46
    t = 0.02 + (col / (COLS - 1)) * span
    return t if direction == "forward" else (1.0 - t)

def fmt(n):
    return f"{n:.4f}".rstrip("0").rstrip(".")

def build_grid(cells, targets):
    target_keys = {f"{t['col']}-{t['row']}" for t in targets}
    svg = []
    for c in cells:
        k = f"{c['col']}-{c['row']}"
        if k not in target_keys:
            svg.append(f'<rect x="{c["x"]:.2f}" y="{c["y"]:.2f}" width="{CELL}" height="{CELL}" rx="2" ry="2" fill="{c["color"]}"/>')
            continue
        t_fwd = key_time_for_col(c["col"], "forward")
        t_back = key_time_for_col(c["col"], "backward")
        t1 = min(t_fwd, t_back)
        t2 = max(t_fwd, t_back)
        dur = 0.006
        elem = (
            f'<rect x="{c["x"]:.2f}" y="{c["y"]:.2f}" width="{CELL}" height="{CELL}" rx="2" ry="2" fill="{c["color"]}">'
            f'<animate attributeName="fill" dur="{LOOP_DUR}s" repeatCount="indefinite" '
            f'keyTimes="0;{fmt(t1)};{fmt(t1 + dur)};{fmt(t2)};{fmt(t2 + dur)};1" '
            f'values="{c["color"]};{c["color"]};{FLASH_COLOR};{c["color"]};{FLASH_COLOR};{c["color"]}"/>'
            f'</rect>'
        )
        svg.append(elem)
    return "\n".join(svg)

def build_bullets_and_blasts(targets):
    bullets = []
    blasts = []
    dur = 0.006

    for direction in ["forward", "backward"]:
        ordered = targets if direction == "forward" else list(reversed(targets))
        for c in ordered:
            t = key_time_for_col(c["col"], direction)
            rise = t - dur * 3
            arrive = t
            fade_end = t + dur
            cx = fmt(c["x"] + CELL / 2.0)
            target_y = fmt(c["y"] + CELL / 2.0)

            bullet = (
                f'<circle cx="{cx}" cy="{PAD_Y}" r="2.4" fill="{BULLET_COLOR}">'
                f'<animate attributeName="cy" dur="{LOOP_DUR}s" repeatCount="indefinite" '
                f'keyTimes="0;{fmt(rise)};{fmt(arrive)};1" values="{PAD_Y};{PAD_Y};{target_y};{target_y}"/>'
                f'<animate attributeName="opacity" dur="{LOOP_DUR}s" repeatCount="indefinite" '
                f'keyTimes="0;{fmt(rise)};{fmt(arrive)};{fmt(fade_end)};1" values="0;1;1;0;0"/>'
                f'</circle>'
            )
            bullets.append(bullet)

            blast = (
                f'<circle cx="{cx}" cy="{target_y}" r="0" fill="none" stroke="{BLAST_COLOR}" stroke-width="1.6" opacity="0">'
                f'<animate attributeName="r" dur="{LOOP_DUR}s" repeatCount="indefinite" '
                f'keyTimes="0;{fmt(arrive)};{fmt(arrive + dur * 3)};1" values="0;1;9;9"/>'
                f'<animate attributeName="opacity" dur="{LOOP_DUR}s" repeatCount="indefinite" '
                f'keyTimes="0;{fmt(arrive)};{fmt(arrive + dur * 3)};1" values="0;1;1;0"/>'
                f'</circle>'
            )
            blasts.append(blast)

    return "\n".join(bullets), "\n".join(blasts)

def build_stars():
    pts = [
        (8, 20, 1.2), (8, 60, 1.6), (8, 100, 2.0),
        (505, 25, 1.2), (505, 70, 1.6), (505, 110, 2.0),
        (30, 164, 1.2), (483, 164, 1.6),
    ]
    return "\n".join(
        f'<circle cx="{x}" cy="{y}" r="1.1" fill="#8b949e">'
        f'<animate attributeName="opacity" values="0.2;1;0.2" dur="{dur}s" repeatCount="indefinite"/>'
        f'</circle>'
        for x, y, dur in pts
    )

def build_jet():
    return f"""<g id="jet">
  <g transform="translate(0,0)">
    <polygon points="0,-16 8,6 4,3 -4,3 -8,6" fill="#58a6ff" stroke="#1f6feb" stroke-width="1"/>
    <polygon points="-8,6 -14,12 -4,7" fill="#388bfd"/>
    <polygon points="8,6 14,12 4,7" fill="#388bfd"/>
    <circle cx="0" cy="-6" r="2.2" fill="#c9e6ff"/>
    <polygon points="-3,7 3,7 0,15" fill="#f0883e">
      <animate attributeName="opacity" values="0.5;1;0.6;1" dur="0.18s" repeatCount="indefinite"/>
    </polygon>
  </g>
  <animateTransform attributeName="transform" attributeType="XML" type="translate"
    dur="{LOOP_DUR}s" repeatCount="indefinite"
    keyTimes="0;0.5;1"
    values="{JET_X_START}.00,140.00;{JET_X_END}.00,140.00;{JET_X_START}.00,140.00"/>
</g>"""

def build_svg(weeks):
    cells = build_cells(weeks)
    targets = pick_targets(cells)
    bullets, blasts = build_bullets_and_blasts(targets)
    stars = build_stars()
    grid = build_grid(cells, targets)
    jet = build_jet()

    return f"""<svg viewBox="0 0 {WIDTH} {HEIGHT}" xmlns="http://www.w3.org/2000/svg">
<rect x="0" y="0" width="{WIDTH}" height="{HEIGHT}" fill="#0d1117"/>
{stars}
<g id="grid">
{grid}
</g>
<g id="bullets">
{bullets}
</g>
<g id="blasts">
{blasts}
</g>
{jet}
</svg>
"""

def main():
    print(f"Fetching contributions for {USERNAME}...")
    weeks = fetch_weeks()
    svg = build_svg(weeks)
    out_path = Path(OUTPUT)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(svg, encoding="utf-8")
    print(f"Wrote {out_path.resolve()}")

if __name__ == "__main__":
    main()
