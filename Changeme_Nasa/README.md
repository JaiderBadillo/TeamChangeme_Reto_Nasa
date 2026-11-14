# CombusLab

The React/Vite dashboard and the read-only API share the Vercel deployment. The Research page queries the NASA catalog, trial details and time series. The local file explorer is available separately under Data.

## Local development

From the repository root, run `npm ci` and `npm run api`. The API listens on port 8787. In a second terminal, run `npm ci` and `npm run dev` inside `dashboard/`. Vite proxies `/api` to the local server.

The API requires `COMBUSLAB_DB_HOST`, `COMBUSLAB_DB_USER`, `COMBUSLAB_DB_PASSWORD`, and `COMBUSLAB_DB_CA`. The CA variable contains the PEM certificate and the user includes the project suffix on the Supabase Session pooler. These values belong in the ignored root `.env` locally and in the server-side environment for deployment.

## Read endpoints

| Request | Response |
|---|---|
| `GET /api/catalog?investigation_id=PSI-25&page=1` | Up to 20 trial records with coverage flags. Optional filters are `q`, `flow_min` and `flow_max` in cm/s. |
| `GET /api/experiment?experiment_id=PSI-25:B10:r11` | BASS-II trial metadata, PSI provenance and six tabular conditions. |
| `GET /api/series?experiment_id=PSI-100:S1:r2&from_s=0&to_s=60` | 1,877 synchronized rows with O₂ and CO₂, units, provenance and time in seconds. |
| `GET /api/export?experiment_id=PSI-100:S1:r2&mode=series&channel=o2&from_s=0&to_s=60&format=csv` | The selected channel at native resolution with units and source references. The format can be `csv` or `json`. |
| `GET /api/export?experiment_id=PSI-25:B10:r11&mode=conditions&format=json` | Experimental conditions with units, qualifiers, bounds and provenance. |

The series endpoint accepts windows of up to 60 seconds, orders by epoch and has a maximum response of 5,000 rows. Its `truncated` property indicates when that limit is reached. PostgreSQL bigint values, including epoch milliseconds, are returned as decimal strings.

## Comparing and exporting

Open Comparations and choose two distinct trial IDs from the catalog. The overlay supports O₂ and CO₂ when both trials have values for the selected channel, the same documented unit, and compatible relative time axes. For a BASS–SAFFIRE pair, the trial cards show the available experimental context and cite NASA PSI.

Downloads are per trial. The series links preserve the selected channel and time window. The conditions links export the test observations listed in the card. For CSV, see [export fields](docs/export-fields.md). Unquoted empty CSV fields and JSON nulls represent missing values.

## Database bootstrap

`scripts/publish_metadata.py` initializes the `combuslab` schema from the project's synchronized DuckDB file. It requires DuckDB, psycopg, the official Supabase CA and an administrator connection to the database containing `public.nasa_synchronized`. The bootstrap is a one-time transaction, checks the four input row counts and provisions a login with SELECT grants for the four metadata tables and the synchronized readings. It prompts for the administrator password and writes the generated application login to the specified, previously absent local env file. Use `--help` for the file and connection arguments.

