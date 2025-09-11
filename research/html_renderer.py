import os
from typing import Dict, Any
from jinja2 import Environment, FileSystemLoader, select_autoescape
from .diagram_renderer import render_svg_from_dsl


class HTMLSlideRenderer:
    def __init__(self, templates_dir: str = "research/templates"):
        self.templates_dir = templates_dir
        os.makedirs(self.templates_dir, exist_ok=True)
        self.env = Environment(
            loader=FileSystemLoader(self.templates_dir),
            autoescape=select_autoescape()
        )

    def render_html(self, slide: Dict[str, Any]) -> str:
        # Preprocess diagram specs into SVG strings
        visual_elements = slide.get("visual_elements") or []
        svg_diagrams = []
        for v in visual_elements:
            if v.get("type") == "diagram":
                try:
                    svg = render_svg_from_dsl({
                        "nodes": v.get("nodes") or [],
                        "edges": v.get("edges") or []
                    })
                    svg_diagrams.append(svg)
                except Exception:
                    continue
        slide = dict(slide)
        slide["_svg_diagrams"] = svg_diagrams
        template = self.env.get_template("slide.html")
        return template.render(slide=slide)


html_renderer = HTMLSlideRenderer()


