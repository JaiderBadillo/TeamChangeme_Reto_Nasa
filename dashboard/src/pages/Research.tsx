import { useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import { Search, Upload } from 'lucide-react'
import { DynamicLineChart, EmptyChartState } from '../components/Charts'
import { FlameTitle } from '../components/FlameTitle'
import { useDataStore } from '../context/DataStoreContext'

export function Research() {
  const { datasets, activeDataset, setActiveDatasetId } = useDataStore()
  const [search, setSearch] = useState('')
  const [xAxis, setXAxis] = useState('')
  const [yAxis, setYAxis] = useState('')

  const labelCol = useMemo(() => {
    if (!activeDataset) return ''
    if (xAxis && activeDataset.columns.includes(xAxis)) return xAxis
    return activeDataset.columns[0] ?? ''
  }, [activeDataset, xAxis])

  const valueCol = useMemo(() => {
    if (!activeDataset) return ''
    if (yAxis && activeDataset.numericColumns.includes(yAxis)) return yAxis
    return activeDataset.numericColumns[0] ?? ''
  }, [activeDataset, yAxis])

  const filteredRows = useMemo(() => {
    if (!activeDataset) return []
    const q = search.trim().toLowerCase()
    if (!q) return activeDataset.rows
    return activeDataset.rows.filter((row) =>
      Object.values(row).some((v) => String(v ?? '').toLowerCase().includes(q)),
    )
  }, [activeDataset, search])

  return (
    <div className="space-y-6">
      <FlameTitle>Research</FlameTitle>

      <section className="svg-black-panel p-6 md:p-10 space-y-8">
        <p className="svg-lead-text max-w-3xl mx-auto text-center">
          Explore and filter structured records from your connected datasets — ready for external JSON/CSV files or backend API streams.
        </p>

        {/* Search & Dataset Selection */}
        <div className="svg-subpanel p-5 space-y-4">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <h2 className="svg-section-heading text-lg">Explore Records</h2>
            <span className="text-xs text-[#E2B84D]">
              Showing <strong className="text-[#B7E4F9]">{filteredRows.length}</strong> of{' '}
              {activeDataset?.rows.length ?? 0} rows
            </span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-4 gap-3">
            <label className="space-y-1 text-xs text-[#E2B84D] md:col-span-2">
              <span>Filter rows by keyword</span>
              <div className="relative">
                <Search className="w-4 h-4 text-[#FEB352] absolute left-3 top-1/2 -translate-y-1/2" />
                <input
                  type="text"
                  value={search}
                  onChange={(e) => setSearch(e.target.value)}
                  placeholder="Search across all loaded columns..."
                  className="svg-input w-full pl-9 pr-3 py-2 text-sm"
                />
              </div>
            </label>

            <label className="space-y-1 text-xs text-[#E2B84D]">
              <span>Dataset Source</span>
              <select
                disabled={datasets.length === 0}
                value={activeDataset?.id ?? ''}
                onChange={(e) => setActiveDatasetId(e.target.value || null)}
                className="svg-input w-full px-3 py-2 text-sm disabled:opacity-50"
              >
                {datasets.length === 0 ? (
                  <option value="">No source loaded</option>
                ) : (
                  datasets.map((d) => (
                    <option key={d.id} value={d.id}>
                      {d.name}
                    </option>
                  ))
                )}
              </select>
            </label>

            <label className="space-y-1 text-xs text-[#E2B84D]">
              <span>Y-Axis Metric</span>
              <select
                disabled={!activeDataset || activeDataset.numericColumns.length === 0}
                value={valueCol}
                onChange={(e) => setYAxis(e.target.value)}
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
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div>
              <h2 className="svg-section-heading text-xl md:text-2xl">Series Explorer</h2>
              <p className="text-xs text-[#9B8F83] mt-0.5">
                Plots numeric trends over any selected label field from uploaded JSON or CSV datasets.
              </p>
            </div>

            {activeDataset && (
              <label className="flex items-center gap-2 text-xs text-[#E2B84D]">
                <span>X-Axis:</span>
                <select
                  value={labelCol}
                  onChange={(e) => setXAxis(e.target.value)}
                  className="svg-input px-3 py-1.5 text-xs"
                >
                  {activeDataset.columns.map((c) => (
                    <option key={c} value={c}>
                      {c}
                    </option>
                  ))}
                </select>
              </label>
            )}
          </div>

          {filteredRows.length > 0 && labelCol && valueCol ? (
            <DynamicLineChart rows={filteredRows} labelColumn={labelCol} valueColumn={valueCol} />
          ) : (
            <EmptyChartState />
          )}
        </div>

        {/* Dynamic Table */}
        <div className="space-y-3">
          <h2 className="svg-section-heading text-xl">Dataset Entries</h2>

          {!activeDataset ? (
            <div className="svg-subpanel p-8 text-center space-y-3">
              <p className="text-sm text-[#9B8F83]">
                No preloaded records. Upload a `.json` or `.csv` file to populate this view dynamically.
              </p>
              <Link
                to="/data"
                className="svg-chip-active px-4 py-1.5 text-xs rounded-full inline-flex items-center gap-1.5"
              >
                <Upload className="w-3.5 h-3.5" /> Go to Data Uploader
              </Link>
            </div>
          ) : (
            <div className="svg-subpanel p-4 overflow-x-auto">
              <table className="w-full text-left text-xs border-collapse">
                <thead>
                  <tr className="border-b border-[#FEB352]/25 text-[#E2B84D]">
                    {activeDataset.columns.slice(0, 8).map((col) => (
                      <th key={col} className="py-2 pr-4 font-[var(--font-mono)]">
                        {col}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody className="divide-y divide-[#FEB352]/10 text-[#EDE3D6]">
                  {filteredRows.slice(0, 30).map((row, idx) => (
                    <tr key={idx}>
                      {activeDataset.columns.slice(0, 8).map((col) => (
                        <td key={col} className="py-2 pr-4 font-[var(--font-mono)]">
                          {row[col] === null ? '—' : String(row[col])}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </section>
    </div>
  )
}
