import { useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import { ArrowUpDown, SlidersHorizontal, Upload } from 'lucide-react'
import { DynamicBarChart, EmptyChartState } from '../components/Charts'
import { FlameTitle } from '../components/FlameTitle'
import { RequestStatus, useReading } from '../components/ScientificReading'
import { inspectColumns, useDataStore, type DataRow } from '../context/DataStoreContext'

const nasaDatasetId = 'nasa-psi-catalog'

export function Ranking() {
  const { datasets: manualDatasets, activeDataset: manualDataset, setActiveDatasetId } = useDataStore()
  const nasa = useReading<{ rows: DataRow[] }>('/api/ranking')
  const [useNasa, setUseNasa] = useState(!manualDataset)
  const [sortOrder, setSortOrder] = useState<'desc' | 'asc'>('desc')
  const [selectedMetric, setSelectedMetric] = useState<string>('')
  const [selectedLabel, setSelectedLabel] = useState<string>('')
  const nasaRows = nasa.data?.rows
  const nasaDataset = useMemo(() => nasaRows && ({
    id: nasaDatasetId, name: 'NASA PSI', rows: nasaRows, ...inspectColumns(nasaRows),
  }), [nasaRows])
  const datasets = nasaDataset ? [nasaDataset, ...manualDatasets] : manualDatasets
  const activeDataset = (useNasa ? nasaDataset ?? manualDataset : manualDataset ?? nasaDataset)
  const sourceCount = (nasaRows ? new Set(nasaRows.map((row) => row.investigation_id)).size : 0) + manualDatasets.length
  const awaitingNasa = !nasa.data && !nasa.error
  const noActiveValue = awaitingNasa || nasa.error ? '—' : 0

  const labelCol = useMemo(() => {
    if (!activeDataset) return ''
    if (selectedLabel && activeDataset.columns.includes(selectedLabel)) return selectedLabel
    return activeDataset.columns.find((c) => !activeDataset.numericColumns.includes(c)) ?? activeDataset.columns[0] ?? ''
  }, [activeDataset, selectedLabel])

  const metricCol = useMemo(() => {
    if (!activeDataset) return ''
    if (selectedMetric && activeDataset.numericColumns.includes(selectedMetric)) return selectedMetric
    return activeDataset.numericColumns[0] ?? ''
  }, [activeDataset, selectedMetric])

  const rankedRows = useMemo(() => {
    if (!activeDataset || !metricCol) return []
    return [...activeDataset.rows]
      .filter((r) => typeof r[metricCol] === 'number' && Number.isFinite(r[metricCol]))
      .sort((a, b) => {
        const va = a[metricCol] as number
        const vb = b[metricCol] as number
        return sortOrder === 'desc' ? vb - va : va - vb
      })
  }, [activeDataset, metricCol, sortOrder])

  return (
    <div className="space-y-6">
      <FlameTitle>Ranking</FlameTitle>

      <section className="svg-black-panel p-6 md:p-10 space-y-8">
        <p className="svg-lead-text max-w-3xl mx-auto text-center">
          Rank NASA PSI trials by a measured condition or analyze an uploaded JSON / CSV dataset.
        </p>

        {!nasa.data && <RequestStatus error={nasa.error} retry={nasa.retry} />}

        {/* Live KPI Strip */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-3.5">
          <div className="svg-subpanel p-4">
            <p className="text-xs uppercase tracking-wider text-[#E2B84D]">Connected Sources</p>
            <p className="mt-1 font-[var(--font-display)] text-3xl font-bold text-[#B7E4F9]">{sourceCount || noActiveValue}</p>
            <p className="mt-1 text-xs text-[#9B8F83]">NASA investigations and manual sources</p>
          </div>
          <div className="svg-subpanel p-4">
            <p className="text-xs uppercase tracking-wider text-[#E2B84D]">Active Records</p>
            <p className="mt-1 font-[var(--font-display)] text-3xl font-bold text-[#FEB352]">
              {activeDataset?.rows.length ?? noActiveValue}
            </p>
            <p className="mt-1 text-xs text-[#9B8F83]">Rows ready for ranking</p>
          </div>
          <div className="svg-subpanel p-4">
            <p className="text-xs uppercase tracking-wider text-[#E2B84D]">Numeric Metrics</p>
            <p className="mt-1 font-[var(--font-display)] text-3xl font-bold text-[#F8CA54]">
              {activeDataset?.numericColumns.length ?? noActiveValue}
            </p>
            <p className="mt-1 text-xs text-[#9B8F83]">Detected quantitative fields</p>
          </div>
          <div className="svg-subpanel p-4 flex flex-col justify-between">
            <div>
              <p className="text-xs uppercase tracking-wider text-[#E2B84D]">Workspace State</p>
              <p className="mt-1 font-[var(--font-display)] text-xl font-bold text-[#F5EDE4]">
                {activeDataset?.name ?? (awaitingNasa ? 'Loading NASA PSI' : nasa.error ? 'NASA PSI unavailable' : 'Awaiting Data')}
              </p>
            </div>
            <Link to="/data" className="mt-2 inline-flex items-center gap-1.5 text-xs font-semibold text-[#FEB352] hover:text-[#B7E4F9]">
              <Upload className="w-3.5 h-3.5" /> Upload JSON / CSV
            </Link>
          </div>
        </div>

        {/* Dynamic Ranking Controls */}
        <div className="svg-subpanel p-5 space-y-4">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div className="flex items-center gap-2">
              <SlidersHorizontal className="w-4 h-4 text-[#FEB352]" />
              <h2 className="svg-section-heading text-lg">Ranking Parameters</h2>
            </div>

            <button
              type="button"
              onClick={() => setSortOrder((o) => (o === 'desc' ? 'asc' : 'desc'))}
              className="svg-chip px-3.5 py-1 text-xs inline-flex items-center gap-1.5 cursor-pointer"
            >
              <ArrowUpDown className="w-3.5 h-3.5" />
              {sortOrder === 'desc' ? 'Highest First' : 'Lowest First'}
            </button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
            <label className="space-y-1 text-xs text-[#E2B84D]">
              <span>Active Dataset</span>
              <select
                disabled={datasets.length === 0}
                value={activeDataset?.id ?? ''}
                onChange={(e) => {
                  const id = e.target.value
                  setUseNasa(id === nasaDatasetId)
                  if (id !== nasaDatasetId) setActiveDatasetId(id)
                }}
                className="svg-input w-full px-3 py-2 text-sm disabled:opacity-50"
              >
                {datasets.length === 0 ? (
                  <option value="">No datasets available</option>
                ) : (
                  datasets.map((d) => (
                    <option key={d.id} value={d.id}>
                      {d.name} ({d.rows.length} rows)
                    </option>
                  ))
                )}
              </select>
            </label>

            <label className="space-y-1 text-xs text-[#E2B84D]">
              <span>Label Field</span>
              <select
                disabled={!activeDataset}
                value={labelCol}
                onChange={(e) => setSelectedLabel(e.target.value)}
                className="svg-input w-full px-3 py-2 text-sm disabled:opacity-50"
              >
                {!activeDataset ? (
                  <option value="">—</option>
                ) : (
                  activeDataset.columns.map((c) => (
                    <option key={c} value={c}>
                      {c}
                    </option>
                  ))
                )}
              </select>
            </label>

            <label className="space-y-1 text-xs text-[#E2B84D]">
              <span>Score / Numeric Metric</span>
              <select
                disabled={!activeDataset || activeDataset.numericColumns.length === 0}
                value={metricCol}
                onChange={(e) => setSelectedMetric(e.target.value)}
                className="svg-input w-full px-3 py-2 text-sm disabled:opacity-50"
              >
                {!activeDataset || activeDataset.numericColumns.length === 0 ? (
                  <option value="">—</option>
                ) : (
                  activeDataset.numericColumns.map((c) => (
                    <option key={c} value={c}>
                      {c}
                    </option>
                  ))
                )}
              </select>
            </label>
          </div>
        </div>

        {/* Dynamic Chart Section */}
        <div className="svg-subpanel p-5 md:p-6 space-y-4">
          <div>
            <h2 className="svg-section-heading text-xl md:text-2xl">Ranked Visualization</h2>
            <p className="text-xs text-[#9B8F83] mt-0.5">
              The chart shows up to 15 trials with a value for the selected metric.
            </p>
          </div>

          {rankedRows.length > 0 && labelCol && metricCol ? (
            <DynamicBarChart rows={rankedRows.slice(0, 15)} labelColumn={labelCol} valueColumn={metricCol} horizontal />
          ) : (
            <EmptyChartState title="No ranking to display" subtitle="Select a source and a metric with numeric values." />
          )}
        </div>

        {/* Dynamic Ranked List */}
        <div className="space-y-3">
          <h2 className="svg-section-heading text-xl">Ranked Records</h2>

          {rankedRows.length === 0 ? (
            <div className="svg-subpanel p-6 text-center text-xs text-[#9B8F83]">
              No records with a value for the selected metric.
            </div>
          ) : (
            <div className="space-y-2.5">
              {rankedRows.slice(0, 20).map((row, idx) => (
                <div key={idx} className="svg-subpanel p-4 flex flex-wrap items-center justify-between gap-3">
                  <div className="flex items-center gap-3">
                    <span className="font-[var(--font-mono)] text-xs font-bold px-2.5 py-1 rounded-md bg-[#FEB352] text-black">
                      #{idx + 1}
                    </span>
                    <span className="font-[var(--font-display)] text-lg font-semibold text-[#F5EDE4]">
                      {String(row[labelCol] ?? `Row ${idx + 1}`)}
                    </span>
                  </div>
                  <div className="font-[var(--font-mono)] text-sm font-bold text-[#B7E4F9]">
                    {metricCol}: {String(row[metricCol])}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </section>
    </div>
  )
}
