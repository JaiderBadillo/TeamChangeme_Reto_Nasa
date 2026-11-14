# CombusLab system plan

## Purpose

CombusLab is a project for **Flame in Freefall**, a challenge in the **2026 NASA Space Apps Challenge** hackathon. The web application helps users find and compare research on combustion in microgravity and interpret its relevance to fire prevention, detection, and suppression during space missions.

The audience includes safety engineers, researchers, students, and educators. The main workflow starts with a safety question, takes users through the relevant study and trial records, and ends with a comparison, a cited explanation, or a download of the selected data.

## Scope and data coverage

| Integrated investigation | NASA PSI | MVP use |
|---|---|---|
| SAFFIRE-I and SAFFIRE-II | [PSI-98](https://psi.nasa.gov/physci/repo/data/investigations/PSI-98) and [PSI-99](https://psi.nasa.gov/physci/repo/data/investigations/PSI-99) | Study and trial records with calibrated time series where available by trial and channel. |
| SAFFIRE-III | [PSI-100](https://psi.nasa.gov/physci/repo/data/investigations/PSI-100) | Study and trial records, calibrated time series, and aligned Cygnus telemetry for two trials. |
| BASS and BASS-II | [PSI-26](https://psi.nasa.gov/physci/repo/data/investigations/PSI-26) and [PSI-25](https://psi.nasa.gov/physci/repo/data/investigations/PSI-25) | Study and trial records with tabular test conditions. The master dataset preserves calibration and provenance records. |

The catalog, comparison tools, ranking, and exports cover these five investigations. SoFIE, SAME/SAME-R, and FLEX/FLEX-2 are candidates for evaluation after the hackathon. External references on detection, droplets, partial gravity, and technology transfer can provide cited editorial context.

| Resource | Status and function |
|---|---|
| `public.nasa_synchronized` | Loaded into Supabase with 226,124 rows across 13 trials. It supplies time-series charts and exports. Its primary key is `(experiment_id, epoch_ms)`. |
| `public.nasa_master` | Loaded into Supabase with 420,421 rows. It preserves events, conditions, calibration records, and provenance. Relationships to time series require verified keys and cardinality. |
| Local DuckDB metadata | `experiment_catalog` contains 263 records, `experiment_conditions` contains 735 observations, and `saffire_channel_units` and `cygnus_channel_units` contain 377 and 11 rows, respectively. A reproducible import into Supabase is planned for phase 1. |

Time series use `time_s` relative to the first calibrated reading in each trial and `epoch_ms` for chronological order and timestamp identity. Charts show nulls as gaps, and exports preserve the native sampling frequencies. Cygnus clock alignment describes the time reference. Physical sensor delays require independent evidence.

## Proposed architecture

CombusLab is planned as a **modular monolith with Next.js App Router and TypeScript**, deployed as a single application backed by Supabase PostgreSQL. A single deployment reduces integration work during the hackathon and lets pages and endpoints share rules and queries.

| Layer | Responsibility |
|---|---|
| Presentation | Server-rendered catalog and detail pages. Client components handle filters, trial selection, and charts. |
| Application | Modules for the catalog, time series, comparisons, scenarios, exports, and summaries. Pages call shared modules directly. The browser uses Route Handlers for interactive requests. |
| Data and integrations | Typed, parameterized SQL queries, migrations, read-only Supabase access, and an AI provider adapter. Python and DuckDB handle data preparation and validation outside the web runtime. |

PostgreSQL handles filtering, pagination, and selection by trial, time window, and channel. The existing key supports queries by trial and absolute time. Representative queries are checked with `EXPLAIN` to assess whether an additional `(experiment_id, time_s)` index is warranted. Large exports stream in batches with stable ordering. Charts disclose any aggregation, and downloads preserve the selected data's resolution.

The server validates filters and channels, uses a read-only role with grants and RLS policies suited to the application, and keeps credentials on the server. The scientific data remains available during an AI provider outage. [Next.js Backend for Frontend](https://nextjs.org/docs/app/guides/backend-for-frontend) · [Row Level Security in Supabase](https://supabase.com/docs/guides/database/postgres/row-level-security)

## Functional requirements

| ID | Planned capability |
|---|---|
| RF-01 | Search and combined filters for material, fuel, objective, sensor, outcome, hardware, gravity, oxygen, pressure, and airflow where coverage is verified. The interface displays units and missing values and distinguishes total pressure from O₂ partial pressure. |
| RF-02 | Investigation and trial pages with objectives, samples, geometry, hardware, controlled and measured variables, sensors, outcomes, and limitations. Pages link to PSI and include DOI, version, and source locator where available. |
| RF-03 | AI-assisted summaries in three sections. Physical objective, key findings, and implications for space missions. The interface labels measurements, published conclusions, and inferences. The server retrieves evidence by identifier, validates citations against the supplied context, and limits request duration and frequency. |
| RF-04 | Comparison of two or more trials. Charts overlay time series when their variables, units, and time references are compatible. Side-by-side tables explain differences in method, instrumentation, environment, and conditions. |
| RF-05 | Reproducible ranking for a scenario defined by gravity, oxygen, pressure, airflow, material, and safety question. Results explain matches, differences, and missing data. The score measures evidence relevance. |
| RF-06 | Exploration of combustion and solid material flammability using SAFFIRE and BASS/BASS-II. The challenge's other research themes are candidates for expansion and editorial references. |
| RF-07 | CSV or JSON downloads of selected data with identifiers, filters, units, and provenance. CSV exports can include a companion data dictionary. Measured values, derived values, and published limits retain their qualifiers. |

## Quality and acceptance

| ID | Quality criterion |
|---|---|
| RNF-01 | Scientific figures and conclusions have verifiable references and source locators where available. Summaries disclose gaps in the evidence. |
| RNF-02 | The interface distinguishes direct measurements, experimental analogs, models, and planned studies. The lunar scenario of 32% O₂ and 10.2 psi is a configurable example query. |
| RNF-03 | The interface works on desktop and mobile, supports keyboard navigation, and communicates status through text as well as color. Controls, axes, tables, and exports show units. |
| RNF-04 | Filters and charts update without a full page reload. Queries bound response size, and the interface handles loading, errors, and empty results. The demo records latency and response volume for a representative query. |

| User story | Acceptance check |
|---|---|
| US-01 | A known filter combination returns verifiable matches. A query for O₂ above 30% and pressure near 10.2 psi shows valid matches or explains why the result is empty. |
| US-02 | A BASS-II page shows test conditions and provenance. A SAFFIRE-III page opens the selected trial's time window. |
| US-03 | A summary displays all three sections, cites its sources, and identifies a numerical question that the available evidence leaves unresolved. |
| US-04 | Two compatible time series can be compared. A BASS–SAFFIRE comparison identifies differences in measured quantities, hardware, or methods that affect interpretation. |
| US-05 | Lunar and Martian scenarios show gaps in gravity and atmospheric coverage and explain the ranking criteria. |
| US-06 | The terrestrial technology transfer section links to sources on smoke detectors, protective clothing, and breathing-air cylinders. |

Final verification covers ordering and uniqueness within a real time window, export fidelity, application-role permissions, network errors, and AI provider errors. Deliverables include a runnable application, startup instructions, an environment variable template without secrets, migrations, a requirements traceability matrix, and a demo script for the judges.

## Project references

- [Dataset documentation](../datasets/README.en.md)
- [PostgreSQL column name mapping](../datasets/supabase_column_map.csv)
- [Scientific background and NASA sources in Spanish](../CONTEXTO_NASA.md)
- [Versión en español](PLAN_DEL_SISTEMA.es.md)

## Development phases

| Phase | Priority | Work | Exit criterion |
|---|---|---|---|
| 1. Foundation and data contract | MVP | Set up Next.js and read access, load metadata, and validate keys, units, and permissions. | The server returns a BASS-II record and the 0–60 s window for `PSI-100:S1:r2`. |
| 2. Catalog, detail pages, and time series | MVP | Build search, filters, traceable detail pages, and charts with channel coverage. | A BASS-II page and a SAFFIRE-III chart display sources and units. |
| 3. Comparison and export | MVP | Build compatible comparisons, methodological notices, and CSV or JSON downloads. | A BASS–SAFFIRE comparison explains the differences, and the download matches the selection. |
| 4. Scenarios and AI | MVP | Add deterministic ranking and summaries with verifiable citations. | The lunar scenario shows coverage gaps, and the catalog remains available during an AI outage. |
| 5. Testing and demo | MVP | Validate the deployed flow, review performance and accessibility, add terrestrial technology transfer content, and prepare the demo script. | The team completes the demo with real data and records requirements coverage. |
| 6. Additional investigations | Later | Evaluate SoFIE, SAME/SAME-R, and FLEX/FLEX-2. | Each addition has documented provenance, units, a schema, and reproducible validation. |
