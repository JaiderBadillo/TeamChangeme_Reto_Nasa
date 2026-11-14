"""Export the support and application datasets with English column identifiers."""
import re
from pathlib import Path

import duckdb

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / "datasets"
CYGNUS = {
    "PCM Air Temp (degC)": "cygnus_pcm_air_temperature_c",
    **{f"FIZ{'' if i == 1 and kind == 'Obscuration' else ' '}{i} Smoke Detector {kind} (V)":
       f"cygnus_fiz_{i}_smoke_detector_{kind.lower()}_v"
       for i in (1, 2) for kind in ("Obscuration", "Scatterometer")},
    **{f"body rate {axis} axis (rad/s)": f"cygnus_body_rate_{axis}_rad_s" for axis in "xyz"},
    **{f"acceleration {axis} axis (m/s^2)": f"cygnus_acceleration_{axis}_m_s2" for axis in "xyz"},
}
RENAMES = {**CYGNUS, "canal": "channel", "unidad": "unit",
           "telemetry__smoke_wire_voltageoltage__unit_unspecified":
           "telemetry__smoke_wire_voltage_legacy_label__unit_unspecified"}


def quote(name):
    return '"' + name.replace('"', '""') + '"'


def project(db, source):
    names = set()
    expressions = []
    for old, *_ in db.execute(f"DESCRIBE {source}").fetchall():
        new = RENAMES.get(old, re.sub(r"[^a-z0-9_]+", "_", old.lower()).strip("_"))
        if new in names or not re.fullmatch(r"[a-z][a-z0-9_]*", new):
            raise ValueError(f"Invalid or duplicate column: {old} → {new}")
        names.add(new)
        expr = quote(old)
        if source.endswith(".unidades_cygnus") and old == "canal":
            cases = " ".join(f"WHEN '{label}' THEN '{value}'" for label, value in CYGNUS.items())
            expr = f"CASE {expr} {cases} ELSE {expr} END"
        expressions.append(f"{expr} AS {quote(new)}")
    return f"SELECT {', '.join(expressions)} FROM {source}"


def verify(db, original, exported, count):
    assert db.execute(f"SELECT count(*) FROM {exported}").fetchone()[0] == count
    assert db.execute(f"SELECT count(*) FROM ({original} EXCEPT ALL SELECT * FROM {exported})").fetchone()[0] == 0


def main():
    DEST.mkdir(exist_ok=True)
    master = DEST / "nasa_master.parquet"
    with duckdb.connect() as db:
        db.execute("CREATE VIEW original AS SELECT * FROM read_parquet(" +
                   "'" + (ROOT / "data/integrated/dataset_integrado.parquet").as_posix().replace("'", "''") + "')")
        query = project(db, "original")
        db.execute(f"COPY ({query}) TO ? (FORMAT PARQUET, COMPRESSION ZSTD)", [str(master)])
        verify(db, query, "read_parquet('" + master.as_posix().replace("'", "''") + "')", 420421)

    destination = DEST / "nasa_synchronized.duckdb"
    source = (ROOT / "outputs/NASA_APLICATIVO_v2.0.duckdb").as_posix().replace("'", "''")
    with duckdb.connect(str(destination)) as db:
        db.execute(f"ATTACH '{source}' AS original (READ_ONLY)")
        for old, new in {
            "catalogo": "experiment_catalog", "condiciones": "experiment_conditions",
            "unidades_cygnus": "cygnus_channel_units", "unidades_saffire": "saffire_channel_units",
            "mediciones": "measurements",
        }.items():
            query = project(db, f"original.{old}")
            db.execute(f"CREATE OR REPLACE TABLE {new} AS {query}")
            count = db.execute(f"SELECT count(*) FROM original.{old}").fetchone()[0]
            verify(db, query, new, count)
        db.execute("ALTER TABLE measurements ADD PRIMARY KEY (experiment_id, epoch_ms)")
        db.execute("""CREATE OR REPLACE MACRO measurement_series(test_id, start_s, end_s) AS TABLE
            SELECT * FROM measurements WHERE experiment_id=test_id AND time_s BETWEEN start_s AND end_s
            ORDER BY epoch_ms""")
        columns = {r[0] for r in db.execute("DESCRIBE measurements").fetchall()}
        assert all(channel in columns for (channel,) in db.execute("SELECT channel FROM cygnus_channel_units").fetchall())
        assert db.execute("SELECT count(*), count(DISTINCT (experiment_id,time_s)) FROM measurements").fetchone() == (226124, 226124)
        assert db.execute("SELECT count(*) FROM measurement_series(?, ?, ?)",
                          ["PSI-100:S1:r2", 0, 60]).fetchone()[0] > 0
        db.execute("CHECKPOINT")
    print("Verified 420421 master rows and 226124 synchronized measurement rows")


if __name__ == "__main__":
    main()
