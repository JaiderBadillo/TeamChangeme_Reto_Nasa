import { useMemo, useRef, useState } from 'react'
import { Code2, FileJson, FileSpreadsheet, Globe, Trash2, Upload } from 'lucide-react'
import { DynamicBarChart, DynamicScatterChart, EmptyChartState } from '../components/Charts'
import { FlameTitle } from '../components/FlameTitle'
import { useDataStore } from '../context/DataStoreContext'

export function Data() {
  const {
    datasets,
    activeDataset,
    setActiveDatasetId,
    uploadFiles,
    connectApiEndpoint,
    removeDataset,
    clearAll,
  } = useDataStore()

  const fileInputRef = useRef<HTMLInputElement | null>(null)
  const [endpointUrl, setEndpointUrl] = useState('')
  const [statusMsg, setStatusMsg] = useState<string | null>(null)
  const [previewId, setPreviewId] = useState<string | null>(null)
  const [scatterX, setScatterX] = useState('')
  const [scatterY, setScatterY] = useState('')
  const [dragging, setDragging] = useState(false)

  const totalRows = useMemo(() => datasets.reduce((acc, d) => acc + d.rows.length, 0), [datasets])
  const totalNumeric = activeDataset?.numericColumns.length ?? 0

  const effectiveX = useMemo(() => {
    if (!activeDataset) return ''
    if (scatterX && activeDataset.numericColumns.includes(scatterX)) return scatterX
    return activeDataset.numericColumns[0] ?? ''
  }, [activeDataset, scatterX])

  const effectiveY = useMemo(() => {
    if (!activeDataset) return ''
    if (scatterY && activeDataset.numericColumns.includes(scatterY)) return scatterY
    return activeDataset.numericColumns[1] ?? activeDataset.numericColumns[0] ?? ''
  }, [activeDataset, scatterY])

  const effectiveLabel = activeDataset?.columns.find((c) => !activeDataset.numericColumns.includes(c)) ?? activeDataset?.columns[0] ?? ''

  const handleFiles = async (files: FileList | null) => {
    if (!files || files.length === 0) return
    const { added, errors } = await uploadFiles(files)
    if (errors.length > 0) {
      setStatusMsg(errors.join(' · '))
    } else {
      setStatusMsg(`Loaded ${added} file${added === 1 ? '' : 's'} into session memory.`)
    }
  }

  const handleEndpointSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!endpointUrl.trim()) return
    const res = await connectApiEndpoint(endpointUrl.trim())
    setStatusMsg(res.message)
    if (res.ok) setEndpointUrl('')
  }

  return (
    <div className="space-y-6">
      <FlameTitle>Data for predictive models</FlameTitle>

      <section className="svg-black-panel p-6 md:p-10 space-y-8">
        <p className="svg-lead-text max-w-3xl mx-auto text-center">
          Connect live JSON APIs or drop local <code className="font-[var(--font-mono)] text-[#FEB352]">.json</code> /{' '}
          <code className="font-[var(--font-mono)] text-[#B7E4F9]">.csv</code> files — inspect schemas, map numeric variables, and feed Chart.js across every tab.
        </p>

        {/* Live Session Counters (Start at 0) */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-3.5">
          <div className="svg-subpanel p-4">
            <p className="text-xs uppercase tracking-wider text-[#E2B84D]">Loaded Files / Sources</p>
            <p className="mt-1 font-[var(--font-display)] text-3xl font-bold text-[#FEB352]">{datasets.length}</p>
            <p className="mt-1 text-xs text-[#9B8F83]">Zero preloaded datasets</p>
          </div>
          <div className="svg-subpanel p-4">
            <p className="text-xs uppercase tracking-wider text-[#E2B84D]">Parsed Records</p>
            <p className="mt-1 font-[var(--font-display)] text-3xl font-bold text-[#B7E4F9]">{totalRows}</p>
            <p className="mt-1 text-xs text-[#9B8F83]">Rows in active session</p>
          </div>
          <div className="svg-subpanel p-4">
            <p className="text-xs uppercase tracking-wider text-[#E2B84D]">Numeric Features</p>
            <p className="mt-1 font-[var(--font-display)] text-3xl font-bold text-[#F8CA54]">{totalNumeric}</p>
            <p className="mt-1 text-xs text-[#9B8F83]">Variables in active source</p>
          </div>
          <div className="svg-subpanel p-4">
            <p className="text-xs uppercase tracking-wider text-[#E2B84D]">Storage Scope</p>
            <p className="mt-1 font-[var(--font-display)] text-2xl font-bold text-[#F5EDE4]">Client Memory</p>
            <p className="mt-1 text-xs text-[#9B8F83]">Private local session only</p>
          </div>
        </div>

        {/* Upload Dropzone & API Connector */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
          <div
            onDragOver={(e) => {
              e.preventDefault()
              setDragging(true)
            }}
            onDragLeave={() => setDragging(false)}
            onDrop={(e) => {
              e.preventDefault()
              setDragging(false)
              handleFiles(e.dataTransfer.files)
            }}
            className={`svg-subpanel p-6 flex flex-col items-center justify-center text-center gap-3 border-dashed transition ${
              dragging ? '!border-[#FEB352]' : ''
            }`}
          >
            <Upload className="w-7 h-7 text-[#FEB352]" />
            <div className="space-y-1">
              <h2 className="svg-section-heading text-lg">Upload JSON or CSV Dataset</h2>
              <p className="text-xs text-[#9B8F83]">
                Drag and drop local files here, or browse from your computer.
              </p>
            </div>
            <input
              ref={fileInputRef}
              type="file"
              accept=".json,.csv"
              multiple
              className="hidden"
              onChange={(e) => handleFiles(e.target.files)}
            />
            <button
              type="button"
              onClick={() => fileInputRef.current?.click()}
              className="svg-chip-active px-5 py-2 text-xs rounded-full cursor-pointer"
            >
              Select .json / .csv files
            </button>
          </div>

          <form onSubmit={handleEndpointSubmit} className="svg-subpanel p-6 flex flex-col justify-between gap-4">
            <div className="space-y-1.5">
              <div className="flex items-center gap-2">
                <Globe className="w-5 h-5 text-[#B7E4F9]" />
                <h2 className="svg-section-heading text-lg">Connect JSON API Endpoint</h2>
              </div>
              <p className="text-xs text-[#9B8F83]">
                Fetch live JSON arrays or objects directly from your backend service (CORS-enabled).
              </p>
            </div>

            <div className="flex flex-col sm:flex-row gap-2">
              <input
                type="url"
                value={endpointUrl}
                onChange={(e) => setEndpointUrl(e.target.value)}
                placeholder="https://api.example.com/v1/experiments.json"
                className="svg-input flex-1 px-3 py-2 text-xs font-[var(--font-mono)]"
              />
              <button
                type="submit"
                className="svg-chip-blue-active px-4 py-2 text-xs rounded-full cursor-pointer shrink-0"
              >
                Fetch JSON
              </button>
            </div>

            {statusMsg && <p className="text-xs text-[#F2C552]">{statusMsg}</p>}
          </form>
        </div>

        {/* Side-by-Side Dynamic Chart.js Canvases */}
        <div className="grid grid-cols-1 xl:grid-cols-2 gap-5">
          <div className="svg-subpanel p-5 space-y-3">
            <div className="flex flex-wrap items-center justify-between gap-2">
              <h2 className="svg-section-heading text-xl">Feature Distribution</h2>
              {activeDataset && effectiveX && (
                <span className="font-[var(--font-mono)] text-xs text-[#E2B84D]">{effectiveX}</span>
              )}
            </div>
            {activeDataset && effectiveLabel && effectiveX ? (
              <DynamicBarChart rows={activeDataset.rows} labelColumn={effectiveLabel} valueColumn={effectiveX} />
            ) : (
              <EmptyChartState />
            )}
          </div>

          <div className="svg-subpanel p-5 space-y-3">
            <div className="flex flex-wrap items-center justify-between gap-2">
              <h2 className="svg-section-heading text-xl">Predictive Feature Space</h2>
              {activeDataset && activeDataset.numericColumns.length > 0 && (
                <div className="flex items-center gap-2 text-xs">
                  <select
                    aria-label="Scatter X axis"
                    value={effectiveX}
                    onChange={(e) => setScatterX(e.target.value)}
                    className="svg-input px-2 py-1 text-xs"
                  >
                    {activeDataset.numericColumns.map((c) => (
                      <option key={c} value={c}>
                        X: {c}
                      </option>
                    ))}
                  </select>
                  <select
                    aria-label="Scatter Y axis"
                    value={effectiveY}
                    onChange={(e) => setScatterY(e.target.value)}
                    className="svg-input px-2 py-1 text-xs"
                  >
                    {activeDataset.numericColumns.map((c) => (
                      <option key={c} value={c}>
                        Y: {c}
                      </option>
                    ))}
                  </select>
                </div>
              )}
            </div>
            {activeDataset && effectiveX && effectiveY ? (
              <DynamicScatterChart rows={activeDataset.rows} xColumn={effectiveX} yColumn={effectiveY} />
            ) : (
              <EmptyChartState />
            )}
          </div>
        </div>

        {/* Active Uploaded Datasets Inventory */}
        <div className="space-y-4">
          <div className="flex flex-wrap items-center justify-between gap-2">
            <h2 className="svg-section-heading text-xl">Connected Session Sources ({datasets.length})</h2>
            {datasets.length > 0 && (
              <button
                type="button"
                onClick={clearAll}
                className="text-xs text-[#F27756] hover:underline cursor-pointer"
              >
                Clear all session data
              </button>
            )}
          </div>

          {datasets.length === 0 ? (
            <div className="svg-subpanel p-6 text-center text-xs text-[#9B8F83]">
              No datasets connected yet. Upload `.json` or `.csv` files above to inspect columns and populate charts.
            </div>
          ) : (
            <div className="space-y-3">
              {datasets.map((ds) => {
                const isActive = activeDataset?.id === ds.id
                const isPreview = previewId === ds.id
                return (
                  <article key={ds.id} className="svg-subpanel p-5 space-y-3">
                    <div className="flex flex-wrap items-start justify-between gap-3">
                      <div className="space-y-1">
                        <div className="flex flex-wrap items-center gap-2">
                          {ds.format === 'csv' ? (
                            <FileSpreadsheet className="w-4 h-4 text-[#B7E4F9]" />
                          ) : (
                            <FileJson className="w-4 h-4 text-[#FEB352]" />
                          )}
                          <h3 className="font-[var(--font-mono)] text-sm font-bold text-[#F5EDE4]">{ds.name}</h3>
                          <span className="text-[11px] px-2 py-0.5 rounded-full border border-[#FEB352]/40 text-[#E2B84D]">
                            {ds.rows.length} rows · {ds.columns.length} cols
                          </span>
                          {isActive && (
                            <span className="text-[11px] px-2 py-0.5 rounded-full bg-[#B7E4F9] text-black font-semibold">
                              Active
                            </span>
                          )}
                        </div>
                        <p className="text-xs text-[#9B8F83]">
                          Loaded at {ds.uploadedAt} · {(ds.sizeBytes / 1024).toFixed(1)} KB
                        </p>
                      </div>

                      <div className="flex flex-wrap items-center gap-2">
                        {!isActive && (
                          <button
                            type="button"
                            onClick={() => setActiveDatasetId(ds.id)}
                            className="svg-chip px-3 py-1 text-xs cursor-pointer"
                          >
                            Set Active
                          </button>
                        )}
                        <button
                          type="button"
                          onClick={() => setPreviewId(isPreview ? null : ds.id)}
                          className="svg-chip px-3 py-1 text-xs inline-flex items-center gap-1 cursor-pointer"
                        >
                          <Code2 className="w-3.5 h-3.5" /> {isPreview ? 'Hide Raw' : 'Raw Preview'}
                        </button>
                        <button
                          type="button"
                          onClick={() => removeDataset(ds.id)}
                          aria-label={`Remove ${ds.name}`}
                          className="p-1.5 rounded-lg border border-[#F27756]/35 text-[#F27756] hover:bg-[#F27756]/10 cursor-pointer"
                        >
                          <Trash2 className="w-3.5 h-3.5" />
                        </button>
                      </div>
                    </div>

                    <div className="flex flex-wrap gap-1.5">
                      {ds.columns.map((col) => (
                        <span
                          key={col}
                          className="font-[var(--font-mono)] text-[11px] px-2 py-0.5 rounded border border-[#FEB352]/25 text-[#F8CA54]"
                        >
                          {col}
                        </span>
                      ))}
                    </div>

                    {isPreview && (
                      <pre className="max-h-56 overflow-auto rounded-xl border border-[#B7E4F9]/25 p-3 text-[11px] font-[var(--font-mono)] text-[#EDE3D6]">
                        {ds.rawPreview}
                      </pre>
                    )}
                  </article>
                )
              })}
            </div>
          )}
        </div>
      </section>
    </div>
  )
}
