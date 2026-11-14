"""Materialize the validated measurements on one experiment/epoch key."""
from pathlib import Path
import json
from zipfile import ZipFile, ZIP_DEFLATED

import duckdb

OUTPUT = Path(__file__).resolve().parents[1] / "outputs"


def main():
    with duckdb.connect(str(OUTPUT / "NASA_APLICATIVO_v2.0.duckdb")) as db:
        db.execute("ATTACH ? AS previous (READ_ONLY)".replace(
            "?", "'" + str(OUTPUT / "NASA_APLICATIVO_v1.0.duckdb").replace("'", "''") + "'"
        ))
        for table in ("catalogo", "condiciones", "unidades_saffire", "unidades_cygnus"):
            db.execute(f"CREATE OR REPLACE TABLE {table} AS SELECT * FROM previous.{table}")
        mismatch = db.execute("""
            SELECT count(*) FROM previous.saffire s JOIN previous.cygnus c
            ON s.experiment_id=c.experiment_id AND s.source_epoch_ms=c.saffire_epoch_ms
            WHERE s.time_s IS DISTINCT FROM c.time_s
        """).fetchone()[0]
        if mismatch:
            raise ValueError(f"Clock mismatch in {mismatch} shared instants")
        db.execute("""
            CREATE OR REPLACE TABLE mediciones AS
            SELECT coalesce(s.experiment_id,c.experiment_id) AS experiment_id,
                   coalesce(s.source_epoch_ms,c.saffire_epoch_ms) AS epoch_ms,
                   coalesce(s.time_s,c.time_s) AS time_s,
                   s.record_id AS saffire_record_id,
                   s.source_file_id AS saffire_file_id, s.source_row AS saffire_source_row,
                   c.source_file_id AS cygnus_file_id, c.source_row AS cygnus_source_row,
                   s.* EXCLUDE (experiment_id, investigation_id, source_test_id, record_id,
                       source_file_id, source_row, source_doi, time_s, source_epoch_ms, clock_scope),
                   c.* EXCLUDE (experiment_id, investigation_id, source_file_id, source_row,
                       saffire_epoch_ms, time_s)
            FROM previous.saffire s FULL OUTER JOIN previous.cygnus c
            ON s.experiment_id=c.experiment_id AND s.source_epoch_ms=c.saffire_epoch_ms
            ORDER BY experiment_id, epoch_ms
        """)
        db.execute("ALTER TABLE mediciones ADD PRIMARY KEY (experiment_id, epoch_ms)")
        db.execute("""
            CREATE OR REPLACE MACRO serie(ensayo, desde, hasta) AS TABLE
            SELECT * FROM mediciones
            WHERE experiment_id=ensayo AND time_s BETWEEN desde AND hasta ORDER BY epoch_ms
        """)
        counts = db.execute("""
            SELECT count(*), count(saffire_record_id), count(cygnus_file_id),
                   count(*) FILTER (WHERE saffire_record_id IS NOT NULL AND cygnus_file_id IS NOT NULL),
                   count(DISTINCT (experiment_id,time_s))
            FROM mediciones
        """).fetchone()
        if counts != (226124, 225300, 846, 22, 226124):
            raise ValueError(f"Unexpected measurement coverage: {counts}")
        assert db.execute("SELECT count(*) FROM serie(?, ?, ?)",
                          ["PSI-100:S1:r2", 0, 60]).fetchone()[0] > 0
        db.execute("COPY mediciones TO ? (FORMAT PARQUET, COMPRESSION ZSTD)",
                   [str(OUTPUT / "NASA_MEDICIONES_v2.0.parquet")])
        db.execute("CHECKPOINT")
    report = OUTPUT / "NASA_VALIDACION_v2.0.json"
    report.write_text(json.dumps({
        "measurement_rows": counts[0], "saffire_rows_reconciled": counts[1],
        "cygnus_rows_reconciled": counts[2], "exact_matches_merged": counts[3],
        "unique_experiment_relative_times": counts[4],
        "key": ["experiment_id", "epoch_ms"],
        "join_policy": "exact_match_only",
    }, indent=2), encoding="utf-8")
    with ZipFile(OUTPUT / "NASA_DATOS_APLICATIVO_v2.0.zip", "w", ZIP_DEFLATED) as package:
        for name in ("NASA_APLICATIVO_v2.0.duckdb", "NASA_MEDICIONES_v2.0.parquet", report.name):
            package.write(OUTPUT / name, name)
    with ZipFile(OUTPUT / "NASA_DATOS_APLICATIVO_v2.0.zip") as package:
        assert package.testzip() is None
    print(counts)


if __name__ == "__main__":
    main()
