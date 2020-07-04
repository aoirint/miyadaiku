from typing import List, Tuple
import os
import shutil
import glob
import pathlib


def copyfiles(files: List[Tuple[pathlib.Path, List[str], pathlib.Path]]) -> None:
    for srcdir, specs, destdir in files:
        if not destdir.is_dir():
            destdir.mkdir(parents=True, exist_ok=True)
        for spec in specs:
            srcfiles = glob.glob(os.path.join(srcdir, spec))
            for fname in srcfiles:
                print(f"copy {fname} -> {destdir}")
                shutil.copy(fname, destdir)
