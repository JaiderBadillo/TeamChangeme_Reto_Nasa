import { createContext, useContext, useMemo, useState, type ReactNode } from 'react'

export type DataRow = Record<string, string | number | boolean | null>

export interface UploadedDataset {
  id: string
  name: string
  sourceType: 'upload' | 'api'
  format: 'json' | 'csv'
  sizeBytes: number
  uploadedAt: string
  columns: string[]
  numericColumns: string[]
  rows: DataRow[]
  rawPreview: string
}

interface DataStoreContextValue {
  datasets: UploadedDataset[]
  activeDataset: UploadedDataset | null
  activeDatasetId: string | null
  setActiveDatasetId: (id: string | null) => void
  uploadFiles: (files: FileList | File[]) => Promise<{ added: number; errors: string[] }>
  connectApiEndpoint: (url: string) => Promise<{ ok: boolean; message: string }>
  removeDataset: (id: string) => void
  clearAll: () => void
}

const DataStoreContext = createContext<DataStoreContextValue | null>(null)

function coerceCell(val: string): string | number | boolean | null {
  const trimmed = val.trim()
  if (trimmed === '' || trimmed.toLowerCase() === 'null' || trimmed.toLowerCase() === 'na') return null
  if (trimmed.toLowerCase() === 'true') return true
  if (trimmed.toLowerCase() === 'false') return false
  const num = Number(trimmed)
  if (!Number.isNaN(num) && /^-?\d+(\.\d+)?([eE][+-]?\d+)?$/.test(trimmed)) return num
  return trimmed
}

function parseCsvRows(text: string): DataRow[] {
  const lines = text
    .replace(/\r\n/g, '\n')
    .replace(/\r/g, '\n')
    .split('\n')
    .filter((l) => l.trim().length > 0)
  if (lines.length < 2) return []

  const splitLine = (line: string): string[] => {
    const out: string[] = []
    let cur = ''
    let inQuotes = false
    for (let i = 0; i < line.length; i++) {
      const ch = line[i]
      if (ch === '"') {
        if (inQuotes && line[i + 1] === '"') {
          cur += '"'
          i++
        } else {
          inQuotes = !inQuotes
        }
      } else if (ch === ',' && !inQuotes) {
        out.push(cur)
        cur = ''
      } else {
        cur += ch
      }
    }
    out.push(cur)
    return out
  }

  const headers = splitLine(lines[0]).map((h, i) => h.trim() || `column_${i + 1}`)
  return lines.slice(1).map((line) => {
    const vals = splitLine(line)
    const row: DataRow = {}
    headers.forEach((h, idx) => {
      row[h] = coerceCell(vals[idx] ?? '')
    })
    return row
  })
}

function flattenPrimitiveRow(obj: Record<string, unknown>, prefix = ''): DataRow {
  const result: DataRow = {}
  for (const [k, v] of Object.entries(obj)) {
    const key = prefix ? `${prefix}.${k}` : k
    if (v === null || typeof v === 'string' || typeof v === 'number' || typeof v === 'boolean') {
      result[key] = v
    } else if (Array.isArray(v)) {
      result[key] = v.length
    } else if (typeof v === 'object') {
      Object.assign(result, flattenPrimitiveRow(v as Record<string, unknown>, key))
    }
  }
  return result
}

function extractJsonRows(parsed: unknown): DataRow[] {
  if (Array.isArray(parsed)) {
    return parsed
      .filter((item): item is Record<string, unknown> => item !== null && typeof item === 'object')
      .map((item) => flattenPrimitiveRow(item))
  }
  if (parsed && typeof parsed === 'object') {
    for (const val of Object.values(parsed as Record<string, unknown>)) {
      if (Array.isArray(val) && val.length > 0 && typeof val[0] === 'object') {
        return val
          .filter((item): item is Record<string, unknown> => item !== null && typeof item === 'object')
          .map((item) => flattenPrimitiveRow(item))
      }
    }
    return [flattenPrimitiveRow(parsed as Record<string, unknown>)]
  }
  return []
}

export function inspectColumns(rows: DataRow[]) {
  const colSet = new Set<string>()
  for (const r of rows) {
    Object.keys(r).forEach((k) => colSet.add(k))
  }
  const columns = Array.from(colSet)
  const numericColumns = columns.filter((col) =>
    rows.some((r) => typeof r[col] === 'number' && Number.isFinite(r[col])),
  )
  return { columns, numericColumns }
}

function buildDataset(
  name: string,
  format: 'json' | 'csv',
  sourceType: 'upload' | 'api',
  rawText: string,
): UploadedDataset {
  const rows = format === 'json' ? extractJsonRows(JSON.parse(rawText)) : parseCsvRows(rawText)
  if (rows.length === 0) {
    throw new Error(`No tabular rows found in ${name}.`)
  }
  const { columns, numericColumns } = inspectColumns(rows)
  return {
    id: `${Date.now()}-${Math.random().toString(36).slice(2, 8)}`,
    name,
    sourceType,
    format,
    sizeBytes: new Blob([rawText]).size,
    uploadedAt: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    columns,
    numericColumns,
    rows,
    rawPreview: rawText.slice(0, 3200),
  }
}

export function DataStoreProvider({ children }: { children: ReactNode }) {
  const [datasets, setDatasets] = useState<UploadedDataset[]>([])
  const [activeDatasetId, setActiveDatasetId] = useState<string | null>(null)

  const activeDataset = useMemo(
    () => datasets.find((d) => d.id === activeDatasetId) ?? datasets[0] ?? null,
    [datasets, activeDatasetId],
  )

  const uploadFiles = async (fileList: FileList | File[]) => {
    const files = Array.from(fileList)
    const created: UploadedDataset[] = []
    const errors: string[] = []

    for (const file of files) {
      try {
        const ext = file.name.toLowerCase().endsWith('.csv') ? 'csv' : 'json'
        const raw = await file.text()
        created.push(buildDataset(file.name, ext, 'upload', raw))
      } catch (err) {
        errors.push(`${file.name}: ${err instanceof Error ? err.message : 'Unable to parse file'}`)
      }
    }

    if (created.length > 0) {
      setDatasets((prev) => [...prev, ...created])
      setActiveDatasetId((curr) => curr ?? created[0].id)
    }

    return { added: created.length, errors }
  }

  const connectApiEndpoint = async (url: string) => {
    try {
      const res = await fetch(url)
      if (!res.ok) return { ok: false, message: `Endpoint returned HTTP ${res.status}` }
      const raw = await res.text()
      const ds = buildDataset(url.split('/').pop() || 'api-response.json', 'json', 'api', raw)
      setDatasets((prev) => [...prev, ds])
      setActiveDatasetId(ds.id)
      return { ok: true, message: `Loaded ${ds.rows.length} rows from endpoint.` }
    } catch (err) {
      return {
        ok: false,
        message: err instanceof Error ? err.message : 'Failed to fetch JSON endpoint.',
      }
    }
  }

  const removeDataset = (id: string) => {
    setDatasets((prev) => prev.filter((d) => d.id !== id))
    setActiveDatasetId((curr) => (curr === id ? null : curr))
  }

  const clearAll = () => {
    setDatasets([])
    setActiveDatasetId(null)
  }

  return (
    <DataStoreContext.Provider
      value={{
        datasets,
        activeDataset,
        activeDatasetId,
        setActiveDatasetId,
        uploadFiles,
        connectApiEndpoint,
        removeDataset,
        clearAll,
      }}
    >
      {children}
    </DataStoreContext.Provider>
  )
}

export function useDataStore() {
  const ctx = useContext(DataStoreContext)
  if (!ctx) throw new Error('useDataStore must be used inside DataStoreProvider')
  return ctx
}
