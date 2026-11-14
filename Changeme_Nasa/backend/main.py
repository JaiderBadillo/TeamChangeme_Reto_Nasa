import csv
import io
import logging
import re
from typing import Annotated, Literal

import asyncpg
from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, Response
from pydantic import BeforeValidator

from database import read_snapshot

app = FastAPI(
    title="CombusLab API", docs_url="/api/docs", redoc_url=None,
    openapi_url="/api/openapi.json", swagger_ui_oauth2_redirect_url=None,
)
logger = logging.getLogger(__name__)
STUDIES = ["PSI-98", "PSI-99", "PSI-100", "PSI-26", "PSI-25"]
PAGE_SIZE = 20
MAX_SERIES_ROWS = 5000
ExperimentId = Annotated[str, Query(min_length=1, max_length=160)]
Channel = Literal["o2", "co2"]
OptionalFlow = Annotated[
    Annotated[float, Query(ge=0, allow_inf_nan=False)] | None,
    BeforeValidator(lambda value: None if value is None or not str(value).strip() else value),
    Query(),
]


@app.exception_handler(HTTPException)
async def http_error(_request: Request, exc: HTTPException):
    return JSONResponse({"error": exc.detail}, status_code=exc.status_code, headers=exc.headers)


@app.exception_handler(RequestValidationError)
async def invalid_query(_request: Request, _exc: RequestValidationError):
    return JSONResponse({"error": "Invalid request parameters"}, status_code=400)


@app.exception_handler(ValueError)
@app.exception_handler(OSError)
@app.exception_handler(asyncpg.PostgresError)
async def database_error(_request: Request, exc: Exception):
    logger.error("Scientific data read failed (%s)", type(exc).__name__)
    return JSONResponse({"error": "Scientific data temporarily unavailable"}, status_code=503)


@app.get("/api/health")
async def health():
    return {"status": "ok", "runtime": "python"}


@app.get("/api/catalog")
async def catalog(
    investigation_id: str = "", q: Annotated[str, Query(max_length=120)] = "",
    page: Annotated[int, Query(ge=1, le=100)] = 1,
    flow_min: OptionalFlow = None, flow_max: OptionalFlow = None,
):
    if (investigation_id and investigation_id not in STUDIES) or (
        flow_min is not None and flow_max is not None and flow_min > flow_max
    ):
        raise HTTPException(400, "Invalid catalog filters")
    async with read_snapshot() as db:
        rows = await db.fetch(
            """SELECT experiment_id, investigation_id, study_name, material_original,
                coalesce(saffire_filas, 0) + coalesce(cygnus_filas, 0) > 0 AS has_series,
                coalesce(condiciones_filas, 0) > 0 AS has_conditions
            FROM combuslab.experiment_catalog
            WHERE investigation_id = ANY($1::text[])
                AND ($2 = '' OR investigation_id = $2)
                AND strpos(lower(concat_ws(' ', study_name, experiment_id, source_test_id,
                    material_original, material_normalized)), lower($3)) > 0
                AND ($4::double precision IS NULL OR air_velocity_cm_s >= $4)
                AND ($5::double precision IS NULL OR air_velocity_cm_s <= $5)
            ORDER BY study_name, experiment_id LIMIT $6 OFFSET $7""",
            STUDIES, investigation_id, q.strip(), flow_min, flow_max, PAGE_SIZE + 1, (page - 1) * PAGE_SIZE,
        )
    return {"page": page, "has_next": len(rows) > PAGE_SIZE, "rows": [dict(row) for row in rows[:PAGE_SIZE]]}


@app.get("/api/ranking")
async def ranking():
    async with read_snapshot() as db:
        rows = await db.fetch(
            """SELECT experiment_id, investigation_id, study_name, material_original, source_url,
                air_velocity_cm_s, burn_duration_s, ignition_power_w
            FROM combuslab.experiment_catalog WHERE investigation_id = ANY($1::text[])
            ORDER BY study_name, experiment_id""",
            STUDIES,
        )
    return {"rows": [dict(row) for row in rows]}


async def read_experiment(db, experiment_id):
    experiment = await db.fetchrow(
        """SELECT * FROM combuslab.experiment_catalog
        WHERE experiment_id = $1 AND investigation_id = ANY($2::text[])""",
        experiment_id, STUDIES,
    )
    if experiment is None:
        raise HTTPException(404, "Experiment not found")
    return dict(experiment)


@app.get("/api/experiment")
async def experiment(experiment_id: ExperimentId):
    async with read_snapshot() as db:
        trial = await read_experiment(db, experiment_id)
        conditions = await db.fetch(
            """SELECT * FROM combuslab.experiment_conditions WHERE experiment_id = $1
            ORDER BY field, source_column""",
            experiment_id,
        )
    return {"experiment": trial, "conditions": [dict(row) for row in conditions]}


@app.get("/api/series")
async def series(
    experiment_id: ExperimentId,
    from_s: Annotated[float, Query(ge=0, allow_inf_nan=False)] = 0,
    to_s: Annotated[float, Query(ge=0, allow_inf_nan=False)] = 60,
):
    if not 0 <= to_s - from_s <= 60:
        raise HTTPException(400, "Use a nonnegative time window of at most 60 seconds")
    async with read_snapshot() as db:
        trial = await read_experiment(db, experiment_id)
        units = await db.fetch(
            """SELECT channel, unit FROM combuslab.saffire_channel_units
            WHERE investigation_id = $1 AND test = $2 AND channel IN ('o2', 'co2') ORDER BY channel""",
            trial["investigation_id"], trial["source_test_id"],
        )
        rows = await db.fetch(
            """SELECT epoch_ms::text AS epoch_ms, time_s, o2, co2, saffire_file_id, saffire_source_row
            FROM public.nasa_synchronized WHERE experiment_id = $1 AND time_s BETWEEN $2 AND $3
            ORDER BY public.nasa_synchronized.epoch_ms LIMIT $4""",
            experiment_id, from_s, to_s, MAX_SERIES_ROWS + 1,
        )
    return {
        "experiment_id": experiment_id, "from_s": from_s, "to_s": to_s,
        "units": [dict(row) for row in units], "time_unit": "s", "time_reference": "first_calibrated_record",
        "source": {"url": trial["source_url"], "doi": trial["source_doi"], "version": trial["repository_version"]},
        "truncated": len(rows) > MAX_SERIES_ROWS, "rows": [dict(row) for row in rows[:MAX_SERIES_ROWS]],
    }


@app.get("/api/export")
async def export(
    experiment_id: ExperimentId, mode: Literal["conditions", "series"], format: Literal["csv", "json"],
    channel: Channel | None = None,
    from_s: Annotated[float, Query(ge=0, allow_inf_nan=False)] = 0,
    to_s: Annotated[float, Query(ge=0, allow_inf_nan=False)] = 60,
):
    filename = re.sub(r"[^a-zA-Z0-9_-]", "-", experiment_id)
    if mode == "series":
        if channel is None:
            raise HTTPException(400, "Select a series channel")
        data = await series(experiment_id, from_s, to_s)
        if data["truncated"]:
            raise HTTPException(422, "Select a smaller time window for a complete export")
        data["channel"] = channel
        data["units"] = [unit for unit in data["units"] if unit["channel"] == channel]
        for row in data["rows"]:
            row.pop("co2" if channel == "o2" else "o2")
        filename += f"-{channel}"
    else:
        data = await experiment(experiment_id)
        filename += "-conditions"
    headers = {"Content-Disposition": f'attachment; filename="{filename}.{format}"'}
    if format == "json":
        return JSONResponse(jsonable_encoder(data), headers=headers)
    return Response(csv_export(data, experiment_id, mode, channel), media_type="text/csv", headers=headers)


def csv_export(data, experiment_id, mode, channel):
    if mode == "series":
        source = data["source"]
        columns = ("from_s", "to_s", "epoch_ms", "time_s", "channel", "value", "unit", "saffire_file_id", "saffire_source_row")
        rows = (
            {**row, "from_s": data["from_s"], "to_s": data["to_s"], "channel": channel,
             "value": row[channel], "unit": data["units"][0]["unit"] if data["units"] else None}
            for row in data["rows"]
        )
    else:
        trial = data["experiment"]
        source = {"url": trial["source_url"], "doi": trial["source_doi"], "version": trial["repository_version"]}
        columns = ("investigation_id", "source_test_id", "field", "value", "lower_bound", "upper_bound",
                   "status", "qualifier", "unit", "method", "source_record_id", "source_column")
        rows = data["conditions"]
    metadata = ("experiment_id", "source_url", "source_doi", "source_version")
    output = io.StringIO(newline="")
    csv.writer(output).writerow((*metadata, *columns))
    writer = csv.writer(output, quoting=csv.QUOTE_NOTNULL)
    for row in rows:
        writer.writerow((experiment_id, row.get("source_url") or source["url"], source["doi"],
                         source["version"], *(row.get(column) for column in columns)))
    return output.getvalue()
