import logging
import pathlib
import shutil
from typing import Any, Dict, List, Optional, Sequence, Tuple

import pytest
import yaml

import miyadaiku.site
from miyadaiku import ContentSrc, builder, context, extend, to_contentpath

logging.getLogger().setLevel(logging.DEBUG)

# import miyadaiku

# miyadaiku.core.SHOW_TRACEBACK = True
# miyadaiku.core.DEBUG = True


def to_contentsrc(path: pathlib.Path) -> ContentSrc:
    return ContentSrc(
        package="", srcpath=str(path), metadata={}, contentpath=((), path.name), mtime=0
    )


def build_sitedir(path: pathlib.Path) -> pathlib.Path:
    site = path / "site"
    if site.is_dir():
        shutil.rmtree(site)
    site.mkdir()
    (site / "contents").mkdir()
    (site / "files").mkdir()
    (site / "templates").mkdir()
    (site / "modules").mkdir()
    extend.load_hook(site)
    return site


@pytest.fixture
def sitedir(tmpdir: Any) -> pathlib.Path:
    d = pathlib.Path(str(tmpdir))
    return build_sitedir(d)


class SiteRoot:
    path: pathlib.Path
    contents: pathlib.Path
    files: pathlib.Path
    templates: pathlib.Path
    modules: pathlib.Path
    outputs: pathlib.Path

    def __init__(self, path: str) -> None:
        self.path = pathlib.Path(str(path)) / "site"
        self.clear()

        self.contents = self.path / "contents"
        self.files = self.path / "files"
        self.templates = self.path / "templates"
        self.modules = self.path / "modules"
        self.outputs = self.path / "outputs"

    def clear(self) -> None:
        build_sitedir(self.path.parent)

    def load(
        self,
        config: Dict[Any, Any],
        props: Dict[Any, Any],
        debug: bool = True,
    ) -> miyadaiku.site.Site:
        cfg = yaml.dump(config)
        (self.path / "config.yml").write_text(cfg)

        site = miyadaiku.site.Site(debug=debug)
        site.load(self.path, props)
        return site

    def ensure_parent(self, path: pathlib.Path) -> None:
        parent = path.parent
        if not parent.is_dir():
            parent.mkdir(parents=True, exist_ok=True)

    def write_text(self, path: pathlib.Path, text: str) -> pathlib.Path:
        self.ensure_parent(path)
        path.write_text(text)
        return path

    def write_bytes(self, path: pathlib.Path, bin: bytes) -> pathlib.Path:
        self.ensure_parent(path)
        path.write_bytes(bin)
        return path


@pytest.fixture
def siteroot(tmpdir: Any) -> SiteRoot:
    ret = SiteRoot(tmpdir)
    return ret


def create_contexts(
    siteroot: SiteRoot,
    srcs: Sequence[Tuple[str, str]],
    config: Optional[Dict[Any, Any]] = None,
) -> List[context.OutputContext]:
    siteroot.clear()
    for path, src in srcs:
        siteroot.write_text(siteroot.contents / path, src)

    if config is None:
        config = {}
    site = siteroot.load(config, {})
    ret = []
    jinjaenv = site.build_jinjaenv()
    for path, src in srcs:
        contentpath = to_contentpath(path)
        if site.files.has_content(contentpath):
            content = site.files.get_content(contentpath)
            builders = builder.create_builders(site, content)
            for b in builders:
                ctx = b.build_context(site, jinjaenv)
                ret.append(ctx)

    return ret
