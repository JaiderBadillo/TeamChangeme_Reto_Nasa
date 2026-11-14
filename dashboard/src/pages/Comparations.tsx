import { useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import { GitCompare, Upload } from 'lucide-react'
import { DynamicCompareChart, EmptyChartState } from '../components/Charts'
import { FlameTitle } from '../components/FlameTitle'
import { useDataStore } from '../context/DataStoreContext'

export function Comparations() {
  const { datasets, activeDataset, setActiveDatasetId } = useDataStore()
  const [labelField, setLabelField] = useState('')
  const [colA, setColA] = useState('')
  const [colB, setColB] = useState('')
  const [chartType, setChartType] = useState<'bar' | 'line'>('bar')

  const effectiveLabel = useMemo(() => {
    if (!activeDataset) return ''
    if (labelField && activeDataset.columns.includes(labelField)) return labelField
    return activeDataset.columns[0] ?? ''
  }, [activeDataset, labelField])

  const effectiveA = useMemo(() => {
    if (!activeDataset) return ''
    if (colA && activeDataset.numericColumns.includes(colA)) return colA
    return activeDataset.numericColumns[0] ?? ''
  }, [activeDataset, colA])

  const effectiveB = useMemo(() => {
    if (!activeDataset) return ''
    if (colB && activeDataset.numericColumns.includes(colB)) return colB
    return activeDataset.numericColumns[1] ?? activeDataset.numericColumns[0] ?? ''
  }, [activeDataset, colB])

  const comparisonRows = useMemo(() => {
    if (!activeDataset || !effectiveA || !effectiveB) return []
    return activeDataset.rows.slice(0, 20).map((r, i) => {
      const a = typeof r[effectiveA] === 'number' ? (r[effectiveA] as number) : null
      const b = typeof r[effectiveB] === 'number' ? (r[effectiveB] as number) : null
      const delta = a !== null && b !== null ? Number((a - b).toFixed(4)) : null
      return {
        label: String(r[effectiveLabel] ?? `#${i + 1}`),
        a,
        b,
        delta,
      }
    })
  }, [activeDataset, effectiveLabel, effectiveA, effectiveB])

  return (
    <div className="space-y-6">
      <FlameTitle>Comparations</FlameTitle>

      <section className="svg-black-panel p-6 md:p-10 space-y-8">
        <p className="svg-lead-text max-w-3xl mx-auto text-center">
          Compare two numerical metrics side-by-side from any uploaded JSON or CSV dataset and inspect per-row deltas cleanly without preloaded assumptions.
        </p>

        {/* Controls */}
        <div className="svg-subpanel p-5 space-y-4">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div className="flex items-center gap-2">
              <GitCompare className="w-4 h-4 text-[#FEB352]" />
              <h2 className="svg-section-heading text-lg">Comparison Setup</h2>
            </div>

            <div className="flex items-center gap-2">
              <button
                type="button"
                onClick={() => setChartType('bar')}
                className={`px-3 py-1 text-xs rounded-full cursor-pointer ${
                  chartType === 'bar' ? 'svg-chip-active' : 'svg-chip'
                }`}
              >
                Grouped Bars
              </button>
              <button
                type="button"
                onClick={() => setChartType('line')}
                className={`px-3 py-1 text-xs rounded-full cursor-pointer ${
                  chartType === 'line' ? 'svg-chip-active' : 'svg-chip'
                }`}
              >
                Trend Curves
              </button>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-4 gap-3">
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
              <span>Shared Axis Label</span>
              <select
                disabled={!activeDataset}
                value={effectiveLabel}
                onChange={(e) => setLabelField(e.target.value)}
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

            <label className="space-y-1 text-xs text-[#FEB352]">
              <span>Series A (#FEB352)</span>
              <select
                disabled={!activeDataset || activeDataset.numericColumns.length === 0}
                value={effectiveA}
                onChange={(e) => setColA(e.target.value)}
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

            <label className="space-y-1 text-xs text-[#B7E4F9]">
              <span>Series B (#B7E4F9)</span>
              <select
                disabled={!activeDataset || activeDataset.numericColumns.length === 0}
                value={effectiveB}
                onChange={(e) => setColB(e.target.value)}
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

        {/* Chart Panel */}
        <div className="svg-subpanel p-5 md:p-6 space-y-4">
          <h2 className="svg-section-heading text-xl md:text-2xl">Side-by-Side Comparison Chart</h2>

          {activeDataset && effectiveLabel && effectiveA && effectiveB ? (
            <DynamicCompareChart
              rows={activeDataset.rows}
              labelColumn={effectiveLabel}
              colA={effectiveA}
              colB={effectiveB}
              chartType={chartType}
            />
          ) : (
            <EmptyChartState />
          )}
        </div>

        {/* Delta Table */}
        <div className="svg-subpanel p-5 space-y-3 overflow-x-auto">
          <h2 className="svg-section-heading text-lg">Computed Delta Table</h2>

          {comparisonRows.length === 0 ? (
            <div className="py-6 text-center space-y-3">
              <p className="text-xs text-[#9B8F83]">Upload a dataset with numeric columns to compare rows side-by-side.</p>
              <Link
                to="/data"
                className="svg-chip px-4 py-1.5 text-xs inline-flex items-center gap-1.5"
              >
                <Upload className="w-3.5 h-3.5" /> Open Data Uploader
              </Link>
            </div>
          ) : (
            <table className="w-full text-left text-xs border-collapse">
              <thead>
                <tr className="border-b border-[#FEB352]/25 text-[#E2B84D]">
                  <th className="py-2 pr-3">{effectiveLabel}</th>
                  <th className="py-2 pr-3 text-[#FEB352]">{effectiveA}</th>
                  <th className="py-2 pr-3 text-[#B7E4F9]">{effectiveB}</th>
                  <th className="py-2">Delta (A &minus; B)</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#FEB352]/10 font-[var(--font-mono)]">
                {comparisonRows.map((row, idx) => (
                  <tr key={idx}>
                    <td className="py-2 pr-3 text-[#F5EDE4]">{row.label}</td>
                    <td className="py-2 pr-3 text-[#FEB352]">{row.a ?? '—'}</td>
                    <td className="py-2 pr-3 text-[#B7E4F9]">{row.b ?? '—'}</td>
                    <td className="py-2 text-[#EDE3D6]">
                      {row.delta !== null ? `${row.delta > 0 ? '+' : ''}${row.delta}` : '—'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </section>
    </div>
  )
}
