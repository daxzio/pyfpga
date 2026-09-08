#!/usr/bin/env python3
#
# Copyright (C) 2026 PyFPGA Project
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

"""Rename Yosys iopadmap cells to nextpnr-safe pad names.

iopadmap names pads ``$iopadmap$TOP.port`` (and ``$iopadmap$TOP.port_N``).
nextpnr-himbaechel CST IO_LOC is an exact cell-name match, but a pad cell
must not share the top-level port name (``Cell 'clkin' ... same name as a
top-level IO is not allowed``). Map to the usual autoname style:

* 1-bit input  -> ``port_IBUF_I``
* 1-bit output -> ``port_OBUF_O``
* extra bits   -> ``port_OBUF_O_N`` / ``port_IBUF_I_N``
"""

from __future__ import annotations

import json
import re
import sys


def pad_cst_name(port: str, direction: str, bit: int) -> str:
    """Return the nextpnr CST cell name for one iopadmap bit."""
    kind = "IBUF_I" if direction == "input" else "OBUF_O"
    if bit == 0:
        return f"{port}_{kind}"
    return f"{port}_{kind}_{bit}"


def rename_iopads(modules: dict, top: str) -> dict[str, str]:
    """Rename ``$iopadmap$TOP.port`` cells in-place; return old-to-new map."""
    if top not in modules:
        raise SystemExit(f"module {top!r} not in JSON")
    mod = modules[top]
    ports = mod.get("ports", {})
    prefix = f"$iopadmap${top}."
    suffix_re = re.compile(r"^(.*)_(\d+)$")
    mapping: dict[str, str] = {}
    cells = mod["cells"]
    for old in list(cells):
        if not old.startswith(prefix):
            continue
        rest = old[len(prefix):]
        if rest in ports:
            port, bit = rest, 0
        else:
            matched = suffix_re.match(rest)
            if matched is None or matched.group(1) not in ports:
                raise SystemExit(f"cannot map iopad cell {old!r} to a top port")
            port, bit = matched.group(1), int(matched.group(2))
        new = pad_cst_name(port, ports[port]["direction"], bit)
        if new in cells and new != old:
            raise SystemExit(f"rename {old!r} -> {new!r} collides")
        mapping[old] = new
    for old, new in mapping.items():
        cell = cells.pop(old)
        cell["hide_name"] = 0
        cells[new] = cell
    return mapping


def main() -> None:
    """CLI: rewrite a Yosys JSON in place and print the mapping."""
    if len(sys.argv) != 3:
        raise SystemExit(f"usage: {sys.argv[0]} <yosys.json> <top>")
    path, top = sys.argv[1], sys.argv[2]
    with open(path, encoding="utf-8") as handle:
        data = json.load(handle)
    mapping = rename_iopads(data["modules"], top)
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(data, handle)
        handle.write("\n")
    for old, new in sorted(mapping.items(), key=lambda kv: kv[1]):
        print(f"iopad {old} -> {new}")


if __name__ == "__main__":
    main()
