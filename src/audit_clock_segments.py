"""Evaluate drift and local interpolation on held-out published clock pairs."""
from pathlib import Path
import json

import duckdb
import numpy as np
import pandas as pd

from src.synchronize_telemetry import MAX_PAIR_ERROR_MS, read_table

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data/synchronized"


def main():
    catalog = pd.read_csv(ROOT / "data/expanded_processed/table_catalog.csv")
    audit = []
    for source in catalog[catalog.sheet.eq("RawData")].itertuples():
        data = read_table(source.local_table)
        pairs = data[["CygnusTimestamp", "SaffireTimestamp"]].apply(pd.to_numeric, errors="coerce")
        pairs = pairs[(pairs > 1.4e12).all(axis=1)].drop_duplicates().sort_values("CygnusTimestamp")
        pairs = pairs[~(pairs.CygnusTimestamp.duplicated(keep=False) |
                        pairs.SaffireTimestamp.duplicated(keep=False))]
        cygnus = pairs.CygnusTimestamp.to_numpy()
        offset = cygnus - pairs.SaffireTimestamp.to_numpy()
        for segment, ids in enumerate(np.array_split(np.arange(len(pairs)), 4), start=1):
            train, held_out = ids[::2], ids[1:-1:2]
            anchor = cygnus[train[0]]
            methods = {
                "affine": np.polyval(np.polyfit(cygnus[train] - anchor, offset[train], 1),
                                    cygnus[held_out] - anchor),
                "local_interpolation": np.interp(cygnus[held_out] - anchor,
                                                 cygnus[train] - anchor, offset[train]),
            }
            for name, predicted in methods.items():
                error = np.abs(predicted - offset[held_out])
                audit.append({
                    "investigation_id": source.investigation_id, "source_file_id": source.file_id,
                    "segment": segment, "method": name, "training_pairs": len(train),
                    "held_out_pairs": len(error), "start_cygnus_epoch_ms": int(cygnus[ids[0]]),
                    "end_cygnus_epoch_ms": int(cygnus[ids[-1]]),
                    "p95_residual_ms": float(np.quantile(error, .95)),
                    "max_residual_ms": float(error.max()),
                    "all_residuals_within_3ms": bool(error.max() <= MAX_PAIR_ERROR_MS),
                })
    frame = pd.DataFrame(audit)
    frame.to_csv(OUT / "auditoria_desfases_por_tramo.csv", index=False)
    with duckdb.connect(str(ROOT / "data/integrated/nasa_integrado.duckdb"), read_only=True) as db:
        master = db.execute("SELECT count(*) FROM dataset_integrado").fetchone()[0]
        timed = db.execute("SELECT count(*),count(*) FILTER (WHERE missing_clock) FROM events").fetchone()
        analysis = db.execute("SELECT count(*) FROM dataset_analisis").fetchone()[0]
    with duckdb.connect(str(OUT / "nasa_sincronizado.duckdb"), read_only=True) as db:
        counts = db.execute("""SELECT
            (SELECT count(*) FROM sensores_saffire),
            (SELECT count(*) FROM telemetria_cygnus),
            (SELECT count(*) FROM condiciones_bass)
        """).fetchone()
        shared = db.execute("""SELECT count(*) FROM telemetria_cygnus c
            JOIN sensores_saffire s ON s.experiment_id=c.experiment_id
              AND s.source_epoch_ms=c.saffire_epoch_ms""").fetchone()[0]
    report = {
        "historical_master_rows": master, "historical_temporal_events": timed[0],
        "historical_events_without_clock": timed[1], "historical_analysis_rows": analysis,
        "calibrated_rows": counts[0], "aligned_cygnus_rows": counts[1],
        "aligned_temporal_rows_across_tables": counts[0] + counts[1],
        "distinct_aligned_experiment_instants": counts[0] + counts[1] - shared,
        "temporal_rows_sharing_exact_experiment_epoch": shared,
        "bass_condition_observations": counts[2], "new_rows_admitted_from_segment_audit": 0,
    }
    assert master - timed[1] == analysis
    (OUT / "conciliacion_registros.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(report)
    print(frame.groupby(["investigation_id", "source_file_id", "method"]).agg(
        passing_segments=("all_residuals_within_3ms", "sum"),
        best_segment_max_ms=("max_residual_ms", "min")).to_string())


if __name__ == "__main__":
    main()
