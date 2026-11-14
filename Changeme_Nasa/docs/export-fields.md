# CombusLab export fields

| Field | Meaning |
|---|---|
| `experiment_id` | Trial identifier in CombusLab. |
| `source_url`, `source_doi`, `source_version` | NASA PSI source, DOI and repository version when recorded. |
| `from_s`, `to_s` | Inclusive limits of the selected time window, in seconds. |
| `epoch_ms`, `time_s` | Epoch in milliseconds and seconds from the first calibrated record for the trial. |
| `channel`, `value`, `unit` | Selected measurement channel, observed value and documented unit. |
| `saffire_file_id`, `saffire_source_row` | File and row provenance for the calibrated SAFFIRE measurement. |
| `investigation_id`, `source_test_id` | NASA PSI investigation and test identifiers for a condition. |
| `field`, `value`, `unit` | Condition name, value and source unit. |
| `lower_bound`, `upper_bound`, `status`, `qualifier`, `method` | Published bounds and interpretation metadata when available. |
| `source_record_id`, `source_column` | Source record and column for the condition. |

CSV uses UTF-8 and comma delimiters. Unquoted empty fields represent missing values. Series exports include every row in the window, including rows where the selected channel is missing.
