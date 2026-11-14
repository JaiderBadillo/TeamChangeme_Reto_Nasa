"""Build the application's read-only DuckDB snapshot from synchronized v0.5."""
import os
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

import duckdb

ROOT = Path(__file__).resolve().parents[1]


def main():
    source = ROOT / "data/synchronized"
    output = ROOT / "outputs"
    output.mkdir(exist_ok=True)
    target = output / "nasa_app.duckdb"
    temporary = output / "nasa_app.build.duckdb"
    with duckdb.connect(str(temporary)) as db:
        for table, path in {
            "ensayos": ROOT / "data/processed/experiments.parquet",
            "saffire": source / "sensores_sincronizados.parquet",
            "cygnus": source / "telemetria_cygnus_sincronizada.parquet",
            "condiciones": source / "condiciones_bass.parquet",
        }.items():
            db.execute(f"CREATE OR REPLACE TABLE {table} AS SELECT * FROM read_parquet(?)", [str(path)])
        db.execute("""
            CREATE OR REPLACE VIEW catalogo AS
            WITH cobertura AS (
                SELECT experiment_id, count(*) AS saffire_filas, 0 AS cygnus_filas, 0 AS condiciones_filas
                FROM saffire GROUP BY experiment_id
                UNION ALL
                SELECT experiment_id, 0, count(*), 0 FROM cygnus GROUP BY experiment_id
                UNION ALL
                SELECT experiment_id, 0, 0, count(*) FROM condiciones GROUP BY experiment_id
            ), resumen AS (
                SELECT experiment_id, sum(saffire_filas)::BIGINT AS saffire_filas,
                    sum(cygnus_filas)::BIGINT AS cygnus_filas,
                    sum(condiciones_filas)::BIGINT AS condiciones_filas
                FROM cobertura GROUP BY experiment_id
            )
            SELECT e.*, coalesce(r.saffire_filas, 0) AS saffire_filas,
                coalesce(r.cygnus_filas, 0) AS cygnus_filas,
                coalesce(r.condiciones_filas, 0) AS condiciones_filas
            FROM ensayos e LEFT JOIN resumen r USING (experiment_id)
        """)
        db.execute("""
            CREATE OR REPLACE MACRO serie_saffire(ensayo, desde, hasta) AS TABLE
                SELECT * FROM saffire
                WHERE experiment_id = ensayo AND time_s BETWEEN desde AND hasta
                ORDER BY time_s
        """)
        db.execute("""
            CREATE OR REPLACE MACRO serie_cygnus(ensayo, desde, hasta) AS TABLE
                SELECT * FROM cygnus
                WHERE experiment_id = ensayo AND time_s BETWEEN desde AND hasta
                ORDER BY time_s
        """)
        db.execute("""
            CREATE OR REPLACE MACRO ficha_condiciones(ensayo) AS TABLE
                SELECT * FROM condiciones WHERE experiment_id = ensayo
                ORDER BY field, source_record_id
        """)
        db.execute("CREATE OR REPLACE TABLE unidades_saffire AS SELECT * FROM read_csv_auto(?)",
                   [str(source / "calidad_canales.csv")])
        db.execute("CREATE OR REPLACE TABLE auditoria_relojes AS SELECT * FROM read_csv_auto(?)",
                   [str(source / "validacion_relojes_cruzados.csv")])
        counts = db.execute("""
            SELECT count(*), count(DISTINCT experiment_id),
                sum(saffire_filas), sum(cygnus_filas), sum(condiciones_filas)
            FROM catalogo
        """).fetchone()
        assert counts == (263, 263, 225300, 846, 735), counts
        for macro in ("serie_saffire", "serie_cygnus"):
            result = db.execute(
                f"SELECT count(*) FROM {macro}(?, ?, ?)", ["PSI-100:S1:r2", 0, 60]
            ).fetchone()[0]
            assert result > 0, macro
        db.execute("CHECKPOINT")
    os.replace(temporary, target)
    with ZipFile(output / "NASA_DATOS_APLICATIVO_v0.5.zip", "w", ZIP_DEFLATED) as package:
        package.write(target, target.name)
        package.write(ROOT / "DATOS_APLICATIVO.md", "DATOS_APLICATIVO.md")
        package.write(source / "sincronizacion.json", "sincronizacion.json")
    print(counts)


if __name__ == "__main__":
    main()
