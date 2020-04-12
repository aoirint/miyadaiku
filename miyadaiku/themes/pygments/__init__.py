# type: ignore

DEST_PATH = "/static/pygments/"


def load_package(site) -> None:
    css = site.config.get("/", "pygments_css")
    src_path = "externals/" + css

    css_path = DEST_PATH + css
    content = bin_loader.from_package(site, __name__, src_path, css_path)
    site.contents.add(content)
    site.config.add("/", {"pygments_css_path": css_path})

    site.add_template_module("pygments", "miyadaiku.themes.pygments!macros.html")
