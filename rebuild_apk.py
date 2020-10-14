#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   rebuild_apk.py
@Time    :   2020/10/14 10:39:02
@Author  :   Lateautumn4lin 
@Version :   1.0
@Contact :   Lateautumn4lin
@License :   (C)Copyright 2020
@Desc    :   None
'''

from pathlib import Path
import shutil
import zipfile
import argparse

"""
将脱壳后的dex重打包成新的apk文件，使用范例如下：

python rebuild_apk.py -A 新华字典v0.9.0.apk  -D cn.dictcn.android.digitize.swg_xhzd_21003/ -O 新华字典v0.9.0_new.apk

"""


class RebuildApk:
    def __init__(self, args):
        self.args = args
        self.dex_temp = Path(__file__).absolute().parent / "dex_temp"
        if not self.dex_temp.exists():
            self.dex_temp.mkdir()

    def normalization_class(self) -> None:
        dex_index = 0
        try:
            for idx, _file in enumerate(Path(self.args.dex_path).iterdir()):
                if _file.suffix == ".dex":
                    if not dex_index:
                        normalization_path = self.dex_temp/"classes.dex"
                    else:
                        normalization_path = self.dex_temp / \
                            f"classes{dex_index}.dex"
                    if not normalization_path.exists():
                        if self.args.debug:
                            print(
                                f"[*] {idx} {_file.name} replace {normalization_path.name}")
                        shutil.copy(_file, normalization_path)
                    dex_index += 1
        except Exception as e:
            print(e)
        else:
            print("[*] normalization_class success")

    def normalization_source(self) -> None:
        if zipfile.is_zipfile(self.args.apk_path):
            apk_zip_dir = zipfile.ZipFile(self.args.apk_path, 'r')
            for _file in apk_zip_dir.namelist():
                if _file.startswith('META-INF'):
                    if self.args.debug:
                        print(f"[*] insert META-INF {_file}")
                    apk_zip_dir.extract(_file, self.dex_temp)
            print("[*] normalization_source success")
        else:
            print(f"[*] {self.args.apk_path} format error")

    def rebuild(self) -> None:
        with zipfile.ZipFile(
                self.args.output, 'w', zipfile.ZIP_DEFLATED) as rebuild_apk_zip_dir:
            for idx, _file in enumerate(self.dex_temp.iterdir()):
                if self.args.debug:
                    print(f"[*] insert no.{idx} file {_file}")
                if _file.is_dir():
                    for _sub_file in _file.iterdir():
                        rebuild_apk_zip_dir.write(
                            _sub_file,
                            f"{_file.name}\{_sub_file.name}"
                        )
                rebuild_apk_zip_dir.write(_file, _file.name)
        print("[*] apk rebuild success")

    def start(self):
        self.normalization_class()
        self.normalization_source()
        self.rebuild()


def parse_args():
    parser = argparse.ArgumentParser(
        description="Rebuild apk from dex dir about after shelling for analysis"
    )
    parser.add_argument(
        "--debug",
        type=str,
        default=True,
        help="turn on debug"
    )
    parser.add_argument(
        "-A",
        "--apk_path",
        required=True,
        type=str,
        help="Specify apk path"
    )
    parser.add_argument(
        "-D",
        "--dex_path",
        required=True,
        type=str,
        help="Specify dex dir path"
    )
    parser.add_argument(
        "-O",
        "--output",
        type=str,
        default="rebuild.apk",
        help="Specify rebuild apk path"
    )
    args = parser.parse_args()
    return args


if __name__ == '__main__':
    args = parse_args()
    rebuilder = RebuildApk(args)
    rebuilder.start()
