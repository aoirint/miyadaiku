from typing import List, Any, Dict, Tuple
import os
from jinja2 import (
    TemplateNotFound,
    Environment,
    PrefixLoader,
    FileSystemLoader,
    ChoiceLoader,
    PackageLoader,
    select_autoescape,
    make_logging_undefined,
    StrictUndefined,
)

from jinja2 import DebugUndefined  # NOQA


import logging
import miyadaiku.site
from pathlib import Path

logger = logging.getLogger(__name__)


class PackagesLoader(PrefixLoader):
    delimiter = "!"

    def __init__(self) -> None:
        self._loaders: Dict[str, Any] = {}

    def get_loader(self, template: str) -> Tuple[Any, str]:
        package, *rest = template.split(self.delimiter, 1)
        if not rest:
            raise TemplateNotFound(template)

        if package not in self._loaders:
            self._loaders[package] = PackageLoader(package)

        return self._loaders[package], rest[0]

    def list_templates(self) -> None:
        raise TypeError("this loader cannot iterate over all templates")


EXTENSIONS = ["jinja2.ext.do"]


def create_env(
    site: "miyadaiku.site.Site", themes: List[str], paths: List[Path]
) -> Environment:
    loaders: List[Any] = [PackagesLoader()]
    for path in paths:
        loaders.append(FileSystemLoader(os.fspath(path)))

    loaders.extend([PackageLoader(theme) for theme in themes])
    loaders.append(PackageLoader("miyadaiku.themes.base"))

    env = Environment(
        #        undefined=make_logging_undefined(logger, DebugUndefined),
        undefined=make_logging_undefined(logger, StrictUndefined),
        loader=ChoiceLoader(loaders),
        autoescape=select_autoescape(["html", "xml"]),
        extensions=EXTENSIONS,
    )

    env.globals["str"] = str
    env.globals["list"] = list
    env.globals["tuple"] = tuple

    env.globals["site"] = site

    env.globals["repr"] = repr
    env.globals["type"] = type
    env.globals["dir"] = dir
    env.globals["isinstance"] = isinstance

    return env