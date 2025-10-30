# emulator/emulator.py
import json, pathlib, io, contextlib, os
from typing import Any, Dict, Optional
from qick import QickConfig

class QickEmulator:
    """
    Minimal helper:
      - Load a QICK JSON config file and expose a QickConfig for program compilation.
      - Provide tiny JSON mutation helpers and persist (commit) back to disk.
      - Wrap QICK's existing print_* helpers to ALWAYS write files,
        even if that QICK version only prints to stdout.

    You STILL use your normal QICK flow:
        soccfg = emu.soccfg
        prog = YourProgram(soccfg, ...)
        emu.export_all(prog, outdir="tb_mem")
    """

    def __init__(self, qick_config_json: str):
        self.cfg_path = pathlib.Path(qick_config_json)
        self.reload()

    # load + raw dict snapshot
    def reload(self):
        self.soccfg = QickConfig(str(self.cfg_path))  # QICK object for compiling
        self._raw: Dict[str, Any] = json.loads(self.cfg_path.read_text())  # pure JSON dict

    # access underlying dict, across QICK versions
    def cfg_dict(self) -> Dict[str, Any]:
        s = self.soccfg
        if hasattr(s, "_cfg"):  # many versions
            return s._cfg
        if hasattr(s, "as_dict"):
            d = s.as_dict()
            if d is not None:
                return d
        if hasattr(s, "to_dict"):
            d = s.to_dict()
            if d is not None:
                return d
        return self._raw  # fallback snapshot

    # persist JSON to disk and re-load QickConfig
    def _save_raw(self):
        # avoid int/str key compare issues when sort_keys
        def _stringify_int_keys(o):
            if isinstance(o, dict):
                return {str(k): _stringify_int_keys(v) for k, v in o.items()}
            if isinstance(o, list):
                return [_stringify_int_keys(v) for v in o]
            return o

        clean = _stringify_int_keys(self._raw)
        self.cfg_path.write_text(json.dumps(clean, indent=2, sort_keys=True))
        self.reload()

    # simple JSON edits 
    def set_gen_mixer(self, ch: int, f_MHz: float):
        gens = self._raw.setdefault("gens", [])
        while len(gens) <= ch:
            gens.append({})
        gens[ch]["mixer_freq"] = float(f_MHz)

    def set_dac_tile_fs(self, tile: int, fs_Msps: float):
        rf = self._raw.setdefault("rf", {}).setdefault("tiles", {}).setdefault("dac", {})
        key = str(tile)
        rf[key] = {**rf.get(key, {}), "fs": float(fs_Msps)}

    def set_adc_tile_fs(self, tile: int, fs_Msps: float):
        rf = self._raw.setdefault("rf", {}).setdefault("tiles", {}).setdefault("adc", {})
        key = str(tile)
        rf[key] = {**rf.get(key, {}), "fs": float(fs_Msps)}

    def commit(self):
        """Persist JSON to disk and refresh self.soccfg for program compilation."""
        self._save_raw()

    # file writers that ALWAYS produce a file using QICK's print_* helpers
    @staticmethod
    def _capture_to_file(fn, out_path, *args, **kwargs):
        out_path = pathlib.Path(out_path)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            # Some QICK versions accept a filename directly:
            fn(str(out_path), *args, **kwargs)
        except TypeError:
            # Others only print to stdout; capture and write it:
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                fn(*args, **kwargs)
            out_path.write_text(buf.getvalue())

    def export_pmem_hex(self, prog, path="tb_mem/pmem.mem"):
        self._capture_to_file(prog.print_pmem2hex, path)

    def export_dmem_hex(self, prog, path="tb_mem/dmem.mem"):
        if hasattr(prog, "print_dmem2hex"):
            self._capture_to_file(prog.print_dmem2hex, path)

    def export_wmem_hex(self, prog, stem="tb_mem/wmem"):
        if hasattr(prog, "print_wmem2hex"):
            try:
                # many versions support a stem
                prog.print_wmem2hex(stem=str(stem))
            except TypeError:
                # fallback to capture stdout in a single file
                self._capture_to_file(prog.print_wmem2hex, f"{stem}.mem")

    def export_sgmem(self, prog, ch: int, prefix="tb_mem/sgmem_ch"):
        # prefer the file_prefix+gen_file path if available
        try:
            prog.print_sg_mem(sg_idx=ch, gen_file=True, file_prefix=f"{prefix}{ch}")
        except TypeError:
            # fallback: capture to one file
            self._capture_to_file(prog.print_sg_mem, f"{prefix}{ch}.mem",
                                  sg_idx=ch, gen_file=True)

    def export_all(self, prog, outdir="tb_mem", sg_channels=None, skip_empty_dmem=True):
        """
        Write PMEM, DMEM (if present), WMEM, and SGMEM for channels.
        DMEM is often zero; you can skip if you want.
        """
        outdir = pathlib.Path(outdir)
        outdir.mkdir(parents=True, exist_ok=True)

        self.export_pmem_hex(prog, outdir / "pmem.mem")
        if not skip_empty_dmem or hasattr(prog, "print_dmem2hex"):
            self.export_dmem_hex(prog, outdir / "dmem.mem")
        self.export_wmem_hex(prog, stem=str(outdir / "wmem"))

        if sg_channels is None:
            gens = self._raw.get("gens", [])
            sg_channels = range(len(gens))
        for ch in sg_channels:
            self.export_sgmem(prog, ch, prefix=str(outdir / "sgmem_ch"))

        return str(outdir.resolve())
