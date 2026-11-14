"""Publish and verify the final data-only snapshot for the application."""
from hashlib import file_digest
import json
from pathlib import Path
import shutil
from zipfile import ZIP_DEFLATED, ZipFile

import duckdb

from src.prepare_app_data import main as build_app_data

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "outputs"
SOURCE = ROOT / "data/synchronized"


def verify(db):
    counts = db.execute("""
        SELECT (SELECT count(*) FROM catalogo), count(*),
               count(DISTINCT (experiment_id, epoch_ms))
        FROM (
            SELECT experiment_id, source_epoch_ms AS epoch_ms FROM saffire
            UNION ALL SELECT experiment_id, saffire_epoch_ms FROM cygnus
        )
    """).fetchone()
    if counts != (263, 226146, 226124):
        raise ValueError(f"Unexpected release counts: {counts}")
    invalid = db.execute("""
        SELECT count(*) FROM cygnus c LEFT JOIN cobertura_temporal w
        ON c.experiment_id = w.experiment_id AND w.serie = 'saffire'
        WHERE w.experiment_id IS NULL OR c.time_s IS NULL
           OR c.time_s NOT BETWEEN w.inicio_s AND w.fin_s
           OR c.anchor_span_ms IS NULL OR c.anchor_span_ms NOT BETWEEN 0 AND 2000
           OR c.validation_max_residual_ms IS NULL
           OR c.validation_max_residual_ms NOT BETWEEN 0 AND 3
    """).fetchone()[0]
    if invalid:
        raise ValueError(f"Invalid Cygnus rows: {invalid}")
    bass = db.execute("SELECT count(*) FROM condiciones").fetchone()[0]
    if bass != 735:
        raise ValueError(f"Unexpected BASS coverage: {bass}")
    return dict(catalogo=counts[0], filas_temporales=counts[1],
                instantes_distintos_por_ensayo=counts[2], condiciones_bass=bass)


def main():
    build_app_data()
    db_path = OUTPUT / "NASA_APLICATIVO_v1.0.duckdb"
    shutil.copyfile(OUTPUT / "nasa_app.duckdb", db_path)
    metadata = json.loads((SOURCE / "sincronizacion.json").read_text(encoding="utf-8"))
    with duckdb.connect(str(db_path)) as db:
        db.execute("""
            CREATE OR REPLACE VIEW cobertura_temporal AS
            SELECT experiment_id, 'saffire' AS serie, count(*) AS filas,
                   min(time_s) AS inicio_s, max(time_s) AS fin_s
            FROM saffire GROUP BY experiment_id
            UNION ALL
            SELECT experiment_id, 'cygnus', count(*), min(time_s), max(time_s)
            FROM cygnus GROUP BY experiment_id
        """)
        db.execute("CREATE TABLE unidades_cygnus (canal VARCHAR PRIMARY KEY, unidad VARCHAR)")
        columns = {r[0] for r in db.execute("DESCRIBE cygnus").fetchall()}
        db.executemany("INSERT INTO unidades_cygnus VALUES (?, ?)",
                       [(k, v) for k, v in metadata["units"].items() if k in columns])
        db.execute("CHECKPOINT")
    with duckdb.connect(str(db_path), read_only=True) as db:
        counts = verify(db)
        db.execute("COPY (SELECT * FROM cobertura_temporal ORDER BY experiment_id, serie) TO ? (HEADER)",
                   [str(OUTPUT / "cobertura_temporal_v1.0.csv")])
    with db_path.open("rb") as stream:
        checksum = file_digest(stream, "sha256").hexdigest()
    manifest = OUTPUT / "validacion_aplicativo_v1.0.json"
    manifest.write_text(json.dumps({
        "version": "1.0", "source_version": "0.5", **counts,
        "sha256_duckdb": checksum,
    }, indent=2), encoding="utf-8")
    archive = OUTPUT / "NASA_DATOS_APLICATIVO_v1.0.zip"
    with ZipFile(archive, "w", ZIP_DEFLATED) as package:
        for path in (db_path, manifest, OUTPUT / "cobertura_temporal_v1.0.csv",
                     SOURCE / "sincronizacion.json", SOURCE / "auditoria_desfases_por_tramo.csv"):
            package.write(path, path.name)
    with ZipFile(archive) as package:
        if package.testzip():
            raise ValueError("ZIP verification failed")
    print(counts, archive.stat().st_size)


if __name__ == "__main__":
    main()
