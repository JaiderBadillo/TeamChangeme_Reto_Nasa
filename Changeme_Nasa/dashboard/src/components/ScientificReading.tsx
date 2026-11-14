import { useEffect, useState } from 'react'

export function useReading<T>(url: string) {
  const [result, setResult] = useState<{ url: string; data?: T; error?: string }>()
  const [attempt, setAttempt] = useState(0)
  useEffect(() => {
    if (!url) return
    const controller = new AbortController()
    fetch(url, { signal: controller.signal })
      .then(async (response) => {
        const body = await response.json()
        if (!response.ok) throw new Error(body.error ?? 'Request failed')
        return body as T
      })
      .then((data) => { if (!controller.signal.aborted) setResult({ url, data }) })
      .catch((error: unknown) => {
        if (!controller.signal.aborted) setResult({ url, error: error instanceof Error ? error.message : 'Request failed' })
      })
    return () => controller.abort()
  }, [url, attempt])
  const current = result?.url === url ? result : undefined
  return { ...current, retry: () => { setResult(undefined); setAttempt((value) => value + 1) } }
}

export function RequestStatus({ error, retry }: { error?: string; retry: () => void }) {
  return error
    ? <p role="alert">{error} <button className="svg-input px-2" onClick={retry}>Retry</button></p>
    : <p role="status">Loading NASA records…</p>
}
