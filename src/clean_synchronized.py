"""Publish synchronized within-run channels and an audit of cross-clock candidates."""
from pathlib import Path
import json
import re

import duckdb
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data/synchronized"
UNIT_MAP = {
    "%": "%", "rpm": "rpm", "cm/sec": "cm/s", "psia": "psia",
    "mw/cm2": "mW/cm²", "mw/cm^2": "mW/cm²", "degrees c": "°C",
    "amps": "A", "volts": "V",
}
CHANNELS = re.compile(
    r"^(o2|co2|humidity|average_fan_speed|ambient_pressure|test_section_inlet_temp|"
    r"anemometer_[12]|radiometer_[1-4]|radiometer_temp_[1-4]|"
    r"(plume|sample)_temp_\d+_tc\d+|igniter_current)$"
)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    with duckdb.connect(str(ROOT / "data/integrated/nasa_integrado.duckdb"), read_only=True) as db:
        data = db.execute("""
            SELECT s.*, e.experiment_id FROM calibrated_timeseries s
            LEFT JOIN experiments e USING(investigation_id, source_test_id)
            ORDER BY s.investigation_id,s.source_test_id,s.source_row
        """).fetchdf()
        conditions = db.execute("""
            SELECT e.investigation_id,e.source_test_id,o.experiment_id,o.field,
                   o.value,o.lower_bound,o.upper_bound,o.status,o.qualifier,o.unit,
                   o.method,o.source_record_id,o.source_column,o.source_url
            FROM experiment_observations o JOIN experiments e USING(experiment_id)
            WHERE o.usable_for_analysis AND e.investigation_id IN ('PSI-25','PSI-26')
        """).fetchdf()
    assert len(data) == 225300 and data.record_id.is_unique and data.experiment_id.notna().all()
    definitions = pd.read_csv(ROOT / "data/expanded_processed/sensor_dictionary.csv").fillna("")
    channels = sorted(c for c in data if CHANNELS.fullmatch(c))
    clean = []
    clocks = []
    metrics = []
    for (investigation, test), run in data.groupby(["investigation_id", "source_test_id"]):
        elapsed = run.elapsed_time_s.to_numpy()
        epoch = run.epoch_time.to_numpy(dtype=np.int64)
        assert run.source_file_id.nunique() == 1 and np.isfinite(elapsed).all()
        assert elapsed[0] == 0 and (np.diff(elapsed) > 0).all() and (np.diff(epoch) > 0).all()
        residual = abs(epoch - epoch[0] - elapsed * 1000)
        assert residual.max() <= 0.5
        run_defs = definitions[definitions.file_name.eq(run.source_file_name.iloc[0])]
        output = run[["record_id", "experiment_id", "investigation_id", "source_test_id",
                      "source_file_id", "source_row", "source_doi"]].copy()
        output["time_s"] = (epoch - epoch[0]) / 1000
        output["source_epoch_ms"] = epoch
        output["clock_scope"] = "within_experiment"
        clocks.append({"investigation_id": investigation, "test": test, "rows": len(run),
                       "max_elapsed_epoch_difference_ms": float(residual.max()),
                       "median_interval_ms": float(np.median(np.diff(epoch)))})
        for channel in channels:
            published = run_defs[run_defs.normalized_column.eq(channel)].source_unit
            units = {UNIT_MAP.get(u.strip().lower()) for u in published}
            assert len(units) == 1 and None not in units, (test, channel, units)
            values = run[channel].astype(float)
            mask = np.isfinite(values)
            if channel in {"o2", "co2", "humidity"}:
                mask &= values.between(0, 100)
            elif channel in {"ambient_pressure", "average_fan_speed"}:
                mask &= values.gt(0) if channel == "ambient_pressure" else values.ge(0)
            elif "_temp" in channel:
                mask &= values.ge(-273.15)
            output[channel] = values.where(mask)
            metrics.append({"investigation_id": investigation, "test": test, "channel": channel,
                            "unit": next(iter(units)), "source_missing": int(values.isna().sum()),
                            "masked": int((~mask & values.notna()).sum()),
                            "negative_retained": int((values.lt(0) & mask).sum())})
        clean.append(output)
    result = pd.concat(clean, ignore_index=True)
    assert result.groupby(["experiment_id", "time_s"]).size().max() == 1
    result.to_parquet(OUT / "sensores_sincronizados.parquet", compression="zstd", index=False)
    pd.DataFrame(clocks).to_csv(OUT / "verificacion_relojes.csv", index=False)
    pd.DataFrame(metrics).to_csv(OUT / "calidad_canales.csv", index=False)
    conditions.to_parquet(OUT / "condiciones_bass.parquet", compression="zstd", index=False)

    catalog = pd.read_csv(ROOT / "data/expanded_processed/table_catalog.csv")
    clock_audit = []
    for src in catalog[catalog.sheet.eq("RawData")].itertuples():
        table = pd.read_parquet(ROOT / src.local_table).iloc[1:]
        cygnus = pd.to_numeric(table.iloc[:, 1], errors="coerce")
        saffire = pd.to_numeric(table.iloc[:, 2], errors="coerce")
        mission = data[data.investigation_id.eq(src.investigation_id)]
        candidates = cygnus.gt(0) & saffire.between(mission.epoch_time.min(), mission.epoch_time.max())
        delta = (cygnus - saffire)[candidates]
        clock_audit.append({
            "investigation_id": src.investigation_id, "source_file_id": src.file_id,
            "paired_rows_in_calibrated_epoch_envelope": len(delta),
            "offset_min_ms": float(delta.min()), "offset_median_ms": float(delta.median()),
            "offset_max_ms": float(delta.max()),
            "raw_saffire_epochs_matching_calibrated": int(saffire.isin(mission.epoch_time).sum()),
            "admitted_rows": 0,
        })
    pd.DataFrame(clock_audit).to_csv(OUT / "auditoria_telemetria.csv", index=False)
    checks = {
        "rows": len(result), "experiments": len(clocks), "channels": len(channels),
        "max_clock_difference_ms": max(x["max_elapsed_epoch_difference_ms"] for x in clocks),
        "masked_cells": sum(x["masked"] for x in metrics),
        "bass_condition_observations": len(conditions), "telemetry_rows_added": 0,
        "by_investigation": result.groupby("investigation_id").size().to_dict(),
    }
    (OUT / "validacion.json").write_text(json.dumps(checks, indent=2), encoding="utf-8")
    print(json.dumps(checks, indent=2))


if __name__ == "__main__":
    main()
