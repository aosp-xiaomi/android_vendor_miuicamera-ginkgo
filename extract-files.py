#!/usr/bin/env -S PYTHONPATH=../../tools/extract-utils python3
#
# SPDX-License-Identifier: Apache-2.0
#
# Pulls MiuiCamera from a ginkgo V12.5.12.0.RCOEUXM dump (system/ and vendor/ folders).
# If your dump has system/system (system-as-root), point this at a folder where
# "system" is the INNER system dir, e.g.:
#   mkdir ~/dump_flat && ln -s /path/dump/out/system/system ~/dump_flat/system
#   ./extract-files.py ~/dump_flat
#

import struct
import zipfile

from extract_utils.fixups_blob import (
    blob_fixup,
    blob_fixups_user_type,
)
from extract_utils.fixups_lib import (
    lib_fixups,
    lib_fixups_user_type,
)
from extract_utils.main import (
    ExtractUtils,
    ExtractUtilsModule,
)

namespace_imports = [
    'vendor/miuicamera-ginkgo',
]


def _strings(d):
    _, hs, _, cnt, _, flags, sstart, _ = struct.unpack_from('<HHIIIIII', d, 8)
    utf8 = bool(flags & 0x100)
    offs = struct.unpack_from('<%dI' % cnt, d, 8 + hs)
    out = []
    for o in offs:
        p = 8 + sstart + o
        if utf8:
            n = d[p]
            p += 1 if not n & 0x80 else 2
            ln = d[p]
            p += 1
            if ln & 0x80:
                ln = ((ln & 0x7F) << 8) | d[p]
                p += 1
            out.append(d[p:p + ln].decode('utf8', 'replace'))
        else:
            ln = struct.unpack_from('<H', d, p)[0]
            p += 2
            out.append(d[p:p + 2 * ln].decode('utf-16le', 'replace'))
    return out


def _patch_target_sdk(manifest: bytes, target: int = 30) -> bytes:
    """MIUI wrote targetSdkVersion as a resource reference (@7F0A001A); the
    Android 17 parser reads it as a preview codename and rejects the app
    ("Requires development platform ... release platform"). Make it an int."""
    d = bytearray(manifest)
    s = _strings(d)
    pos = 8
    while pos < len(d):
        t, _, sz = struct.unpack_from('<HHI', d, pos)
        if t == 0x102:
            _, name, astart, asize, acount = struct.unpack_from('<IIHHH', d, pos + 16)
            if s[name] == 'uses-sdk':
                for i in range(acount):
                    a = pos + 16 + astart + i * asize
                    ans, aname, _, _, _, _, _ = struct.unpack_from('<IIIHBBI', d, a)
                    if s[aname] == 'targetSdkVersion':
                        struct.pack_into('<IIIHBBI', d, a, ans, aname,
                                         0xFFFFFFFF, 8, 0, 0x10, target)
                        return bytes(d)
        pos += sz
    raise RuntimeError('uses-sdk/targetSdkVersion not found in manifest')


def fix_target_sdk(ctx, file, file_path, *args, tmp_dir=None, **kwargs):
    tmp = file_path + '.tmp'
    with zipfile.ZipFile(file_path) as zin, zipfile.ZipFile(tmp, 'w') as zout:
        for info in zin.infolist():
            data = zin.read(info.filename)
            if info.filename == 'AndroidManifest.xml':
                data = _patch_target_sdk(data)
            ni = zipfile.ZipInfo(info.filename, info.date_time)
            ni.compress_type = info.compress_type
            ni.external_attr = info.external_attr
            zout.writestr(ni, data)
    import os
    os.replace(tmp, file_path)


lib_fixups: lib_fixups_user_type = {
    **lib_fixups,
}

blob_fixups: blob_fixups_user_type = {
    'system/priv-app/MiuiCamera/MiuiCamera.apk': blob_fixup()
        .call(fix_target_sdk, need_tmp_dir=False),
}  # fmt: skip

module = ExtractUtilsModule(
    'xiaomi',
    'miuicamera-ginkgo',
    device_rel_path='vendor/miuicamera-ginkgo',
    blob_fixups=blob_fixups,
    lib_fixups=lib_fixups,
    namespace_imports=namespace_imports,
)

if __name__ == '__main__':
    utils = ExtractUtils.device(module)
    utils.run()
