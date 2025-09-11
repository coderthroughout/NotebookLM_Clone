from typing import Dict, Any, List


def render_svg_from_dsl(spec: Dict[str, Any], width: int = 800, height: int = 480) -> str:
    nodes: List[Dict[str, Any]] = spec.get("nodes", []) or []
    edges: List[Dict[str, Any]] = spec.get("edges", []) or []
    # Simple layout: place nodes in a grid
    cols = max(1, int(len(nodes) ** 0.5))
    gap_x = width // (cols + 1)
    gap_y = 160
    x, y, c = gap_x, 80, 0

    positioned = []
    for n in nodes:
        label = str(n.get("label", n.get("id", "")))
        node = {
            "id": n.get("id", label),
            "x": x,
            "y": y,
            "label": label,
            "type": n.get("type", "box")
        }
        positioned.append(node)
        c += 1
        if c % cols == 0:
            x = gap_x
            y += gap_y
        else:
            x += gap_x

    node_map = {n["id"]: n for n in positioned}
    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}">']
    svg.append('<rect x="0" y="0" width="100%" height="100%" fill="rgba(2,6,23,0.2)" />')

    # Edges
    for e in edges:
        src = node_map.get(e.get("from"))
        dst = node_map.get(e.get("to"))
        if not src or not dst:
            continue
        svg.append(
            f'<line x1="{src["x"]}" y1="{src["y"]}" x2="{dst["x"]}" y2="{dst["y"]}" '
            'stroke="#60a5fa" stroke-opacity="0.7" stroke-width="3" />'
        )
        if e.get("label"):
            mx = (src["x"] + dst["x"]) // 2
            my = (src["y"] + dst["y"]) // 2
            svg.append(
                f'<text x="{mx}" y="{my - 8}" fill="#93c5fd" font-size="18" text-anchor="middle">{e["label"]}</text>'
            )

    # Nodes
    for n in positioned:
        if n["type"] == "circle":
            svg.append(f'<circle cx="{n["x"]}" cy="{n["y"]}" r="32" fill="#0b1220" stroke="#60a5fa" />')
        else:
            svg.append(
                f'<rect x="{n["x"]-60}" y="{n["y"]-28}" width="120" height="56" rx="8" fill="#0b1220" stroke="#60a5fa" />'
            )
        svg.append(
            f'<text x="{n["x"]}" y="{n["y"]+5}" fill="#e5e7eb" font-size="18" text-anchor="middle">{n["label"]}</text>'
        )

    svg.append("</svg>")
    return "".join(svg)


