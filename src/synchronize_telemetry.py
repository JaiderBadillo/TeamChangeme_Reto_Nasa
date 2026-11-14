"""Align Cygnus readings using observed clock pairs and calibrated test windows."""
import json
from pathlib import Path

import duckdb
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data/synchronized"
# Threshold for agreement with the workbook's paired timestamps, not sensor latency.
MAX_PAIR_ERROR_MS = 3
MIN_VALIDATION_PAIRS = 30
CHANNEL_UNITS = {
    "PCM Air Temp (degC)": "°C",
    "PCM Press (psi)": "psi",
    "PCM Press EPS1 (psi)": "psi",
    "PCM Press EPS2 (Psi)": "psi",
    "PCM Press EPS3 (PSI)": "psi",
    "FIZ1 Smoke Detector Obscuration (V)": "V",
    "FIZ 2 Smoke Detector Obscuration (V)": "V",
    "FIZ 1 Smoke Detector Scatterometer (V)": "V",
    "FIZ 2 Smoke Detector Scatterometer (V)": "V",
    "body rate x axis (rad/s)": "rad/s",
    "body rate y axis (rad/s)": "rad/s",
    "body rate z axis (rad/s)": "rad/s",
    "acceleration x axis (m/s^2)": "m/s²",
    "acceleration y axis (m/s^2)": "m/s²",
    "acceleration z axis (m/s^2)": "m/s²",
}


def read_table(path):
    raw = pd.read_parquet(ROOT / path)
    data = raw.iloc[1:].copy()
    data.columns = [" ".join(label.split()) or f"unnamed_{i}" for i, label in enumerate(raw.iloc[0])]
    return data


def main():
    cal = pd.read_parquet(OUT / "sensores_sincronizados.parquet")
    catalog = pd.read_csv(ROOT / "data/expanded_processed/table_catalog.csv")
    manifest = json.loads((ROOT / "data/expanded_raw/manifest.json").read_text(encoding="utf-8"))
    sources = {row["file_id"]: row for row in manifest}
    audits, results = [], []
    for source in catalog[catalog.sheet.eq("RawData")].itertuples():
        reference = cal[cal.investigation_id.eq(source.investigation_id)]
        data = read_table(source.local_table)
        pairs = data[["CygnusTimestamp", "SaffireTimestamp"]].apply(pd.to_numeric, errors="coerce")
        pairs = pairs[pairs.CygnusTimestamp.gt(0) & pairs.SaffireTimestamp.between(
            reference.source_epoch_ms.min(), reference.source_epoch_ms.max()
        )].drop_duplicates().sort_values("CygnusTimestamp")
        ambiguous = pairs.duplicated("CygnusTimestamp", keep=False) | pairs.duplicated("SaffireTimestamp", keep=False)
        pairs = pairs[~ambiguous]
        offset = pairs.CygnusTimestamp - pairs.SaffireTimestamp
        training = offset.iloc[::2]
        validation = offset.iloc[1::2]
        estimate = round(training.median()) if len(training) else None
        error = (validation - estimate).abs() if estimate is not None else validation
        exact = int(pairs.SaffireTimestamp.isin(reference.source_epoch_ms).sum())
        # Require a stable offset on the reserved pairs and shared epochs with the calibrated sheets.
        # A source with clock discontinuities requires a separately validated segment.
        accepted = len(error) >= MIN_VALIDATION_PAIRS and error.max() <= MAX_PAIR_ERROR_MS and exact >= 10
        audit = dict(investigation_id=source.investigation_id, file_id=source.file_id,
                     offset_ms=estimate, training_pairs=len(training), held_out_pairs=len(error),
                     held_out_p95_error_ms=float(error.quantile(.95)) if len(error) else None,
                     held_out_max_error_ms=float(error.max()) if len(error) else None,
                     exact_calibrated_epoch_matches=exact, accepted=bool(accepted), admitted_events=0)
        audits.append(audit)
        if not accepted:
            continue
        paired = pairs[(offset - estimate).abs() <= MAX_PAIR_ERROR_MS]
        sheet = catalog[(catalog.file_id == source.file_id) & catalog.sheet.eq("CygnusData")].iloc[0]
        telemetry = read_table(sheet.local_table)
        telemetry["source_row"] = telemetry.index + 1
        telemetry["CygnusTimestamp"] = pd.to_numeric(telemetry.CygnusTimestamp, errors="coerce")
        telemetry = telemetry[~telemetry.CygnusTimestamp.duplicated(keep=False)]
        # Require exact support or two nearby anchors on the same clock segment.
        anchored = paired.CygnusTimestamp.to_numpy()
        t = telemetry.CygnusTimestamp.to_numpy()
        pos = np.searchsorted(anchored, t)
        left = anchored[np.maximum(pos - 1, 0)]
        right = anchored[np.minimum(pos, len(anchored) - 1)]
        exact_support = t == right
        supported = exact_support | ((pos > 0) & (pos < len(anchored)) & (right - left <= 2000))
        telemetry = telemetry.loc[supported].copy()
        telemetry["SaffireTimestamp"] = telemetry.CygnusTimestamp - estimate
        telemetry["anchor_span_ms"] = np.where(exact_support, 0, right-left)[supported]
        for experiment, run in reference.groupby("experiment_id"):
            start, end = run.source_epoch_ms.min(), run.source_epoch_ms.max()
            window = telemetry[telemetry.SaffireTimestamp.between(start, end)].copy()
            output = pd.DataFrame({"investigation_id": source.investigation_id, "experiment_id": experiment,
                                   "source_file_id": source.file_id, "source_row": window.source_row,
                                   "cygnus_epoch_ms": window.CygnusTimestamp.astype("int64"),
                                   "saffire_epoch_ms": window.SaffireTimestamp.astype("int64")})
            output["time_s"] = (output.saffire_epoch_ms - start) / 1000
            output["anchor_span_ms"] = window.anchor_span_ms
            output["validation_max_residual_ms"] = float(error.max())
            for label in CHANNEL_UNITS:
                if label in window:
                    values = pd.to_numeric(window[label], errors="coerce")
                    # Cygnus worksheets use zero among sparse channel updates.
                    output[label] = values.where(np.isfinite(values) & values.ne(0))
            physical_channels = list(output.columns.intersection(CHANNEL_UNITS))
            output = output.dropna(subset=physical_channels, how="all")
            audit["admitted_events"] += len(output)
            results.append(output)
    aligned = pd.concat(results, ignore_index=True)
    print(audits, aligned.shape, aligned.duplicated(["experiment_id","saffire_epoch_ms"]).sum())
    assert len(aligned) and not aligned.duplicated(["experiment_id", "saffire_epoch_ms"]).any()
    assert aligned.validation_max_residual_ms.max() <= MAX_PAIR_ERROR_MS
    aligned.to_parquet(OUT / "telemetria_cygnus_sincronizada.parquet", compression="zstd", index=False)
    pd.DataFrame(audits).to_csv(OUT / "validacion_relojes_cruzados.csv", index=False)
    (OUT / "sincronizacion.json").write_text(json.dumps({
        "cygnus_events": len(aligned), "by_investigation": aligned.groupby("investigation_id").size().to_dict(),
        "source_sheet": "CygnusData", "clock_anchor_sheet": "RawData", "units": CHANNEL_UNITS, "clock_pair_tolerance_ms": MAX_PAIR_ERROR_MS,
        "sources": {key: {k: sources[key][k] for k in ("file_name", "sha256", "doi")}
                    for key in aligned.source_file_id.unique()},
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    with duckdb.connect(str(OUT / "nasa_sincronizado.duckdb")) as db:
        for table, filename in {
            "sensores_saffire": "sensores_sincronizados.parquet",
            "telemetria_cygnus": "telemetria_cygnus_sincronizada.parquet",
            "condiciones_bass": "condiciones_bass.parquet",
        }.items():
            db.execute(f"CREATE OR REPLACE TABLE {table} AS SELECT * FROM read_parquet(?)", [str(OUT / filename)])
    print(len(aligned), pd.DataFrame(audits).to_string(index=False))


if __name__ == "__main__":
    main()
