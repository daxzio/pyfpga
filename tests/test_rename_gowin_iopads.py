import importlib.util
from pathlib import Path

_HELPER = (
    Path(__file__).resolve().parents[1]
    / 'pyfpga'
    / 'helpers'
    / 'rename_gowin_iopads.py'
)


def _load_helper():
    spec = importlib.util.spec_from_file_location(
        'rename_gowin_iopads', _HELPER
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_pad_cst_name():
    mod = _load_helper()
    assert mod.pad_cst_name('clkin', 'input', 0) == 'clkin_IBUF_I'
    assert mod.pad_cst_name('uart_tx', 'output', 0) == 'uart_tx_OBUF_O'
    assert mod.pad_cst_name('led', 'output', 1) == 'led_OBUF_O_1'


def test_rename_iopads():
    mod = _load_helper()
    top = 'gax_noho'
    modules = {
        top: {
            'ports': {
                'clkin': {'direction': 'input', 'bits': [2]},
                'uart_tx': {'direction': 'output', 'bits': [4]},
                'led': {'direction': 'output', 'bits': [6, 7]},
            },
            'cells': {
                f'$iopadmap${top}.clkin': {'type': 'IBUF', 'hide_name': 1},
                f'$iopadmap${top}.uart_tx': {'type': 'OBUF', 'hide_name': 1},
                f'$iopadmap${top}.led': {'type': 'OBUF', 'hide_name': 1},
                f'$iopadmap${top}.led_1': {'type': 'OBUF', 'hide_name': 1},
            },
        }
    }
    mapping = mod.rename_iopads(modules, top)
    cells = modules[top]['cells']
    assert mapping[f'$iopadmap${top}.clkin'] == 'clkin_IBUF_I'
    assert mapping[f'$iopadmap${top}.led_1'] == 'led_OBUF_O_1'
    assert cells['clkin_IBUF_I']['hide_name'] == 0
