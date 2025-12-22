import { useCallback, useEffect, useMemo, useState } from 'react'
import { useAuthStore } from '../../stores/authStore'

type DataSourceStats = {
  received_last_24h: number
  pending_count: number
  error_count: number
  last_received_at?: string | null
  last_processed_at?: string | null
}

type DataSourceConfig = {
  source: string
  display_name?: string | null
  is_enabled: boolean
  rate_limit_per_minute: number
  has_secret: boolean
  stats: DataSourceStats
}

function fmtDate(iso?: string | null) {
  if (!iso) return '—'
  const d = new Date(iso)
  if (Number.isNaN(d.getTime())) return '—'
  return d.toLocaleString()
}

export default function DataSources() {
  const token = useAuthStore((s) => s.token)

  const [items, setItems] = useState<DataSourceConfig[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [saving, setSaving] = useState<Record<string, boolean>>({})
  const [rotatedSecret, setRotatedSecret] = useState<{ source: string; secret: string } | null>(null)
  const [processing, setProcessing] = useState<{ opportunities?: boolean; geography?: boolean }>({})

  const headers = useMemo(() => {
    const h: Record<string, string> = { 'Content-Type': 'application/json' }
    if (token) h.Authorization = `Bearer ${token}`
    return h
  }, [token])

  const refresh = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const res = await fetch('/api/v1/admin/data-sources', { headers })
      const data = await res.json().catch(() => null)
      if (!res.ok) throw new Error(data?.detail || 'Failed to load data sources')
      setItems(Array.isArray(data) ? data : [])
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to load data sources')
    } finally {
      setLoading(false)
    }
  }, [headers])

  useEffect(() => {
    refresh()
  }, [refresh])

  const updateLocal = (source: string, patch: Partial<DataSourceConfig>) => {
    setItems((prev) => prev.map((s) => (s.source === source ? { ...s, ...patch } : s)))
  }

  const save = async (source: string, patch: { display_name?: string | null; is_enabled?: boolean; rate_limit_per_minute?: number }) => {
    setSaving((m) => ({ ...m, [source]: true }))
    try {
      const res = await fetch(`/api/v1/admin/data-sources/${encodeURIComponent(source)}`, {
        method: 'PATCH',
        headers,
        body: JSON.stringify(patch),
      })
      const data = await res.json().catch(() => null)
      if (!res.ok) throw new Error(data?.detail || 'Failed to save')
      await refresh()
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to save')
    } finally {
      setSaving((m) => ({ ...m, [source]: false }))
    }
  }

  const rotate = async (source: string) => {
    setSaving((m) => ({ ...m, [source]: true }))
    setError(null)
    try {
      const res = await fetch(`/api/v1/admin/data-sources/${encodeURIComponent(source)}/rotate-secret`, {
        method: 'POST',
        headers,
      })
      const data = await res.json().catch(() => null)
      if (!res.ok) throw new Error(data?.detail || 'Failed to rotate secret')
      setRotatedSecret({ source, secret: String(data?.hmac_secret || '') })
      await refresh()
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to rotate secret')
    } finally {
      setSaving((m) => ({ ...m, [source]: false }))
    }
  }

  const runProcessing = async (kind: 'opportunities' | 'geography') => {
    setProcessing((p) => ({ ...p, [kind]: true }))
    setError(null)
    try {
      const endpoint =
        kind === 'opportunities' ? '/api/v1/admin/data-sources/process/opportunities?limit=50' : '/api/v1/admin/data-sources/process/geography?limit=100'
      const res = await fetch(endpoint, { method: 'POST', headers })
      const data = await res.json().catch(() => null)
      if (!res.ok) throw new Error(data?.detail || `Failed to process ${kind}`)
      await refresh()
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Processing failed')
    } finally {
      setProcessing((p) => ({ ...p, [kind]: false }))
    }
  }

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      <div className="flex items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl font-semibold text-gray-900">Data Sources Command Center</h1>
          <div className="mt-1 text-sm text-gray-600">Enable/disable sources, manage rate limits and secrets, and trigger processing.</div>
        </div>
        <div className="flex items-center gap-2">
          <button
            type="button"
            onClick={() => runProcessing('opportunities')}
            disabled={Boolean(processing.opportunities)}
            className="px-3 py-2 text-sm font-medium rounded-lg bg-black text-white hover:bg-gray-800 disabled:opacity-50"
          >
            Process Opportunities
          </button>
          <button
            type="button"
            onClick={() => runProcessing('geography')}
            disabled={Boolean(processing.geography)}
            className="px-3 py-2 text-sm font-medium rounded-lg bg-white border border-gray-200 hover:bg-gray-50 disabled:opacity-50"
          >
            Process Geography
          </button>
          <button
            type="button"
            onClick={refresh}
            className="px-3 py-2 text-sm font-medium rounded-lg bg-white border border-gray-200 hover:bg-gray-50"
          >
            Refresh
          </button>
        </div>
      </div>

      {error ? (
        <div className="mt-4 bg-red-50 border border-red-200 text-red-800 rounded-lg p-3 text-sm">{error}</div>
      ) : null}

      {rotatedSecret ? (
        <div className="mt-4 bg-amber-50 border border-amber-200 text-amber-900 rounded-lg p-4 text-sm">
          <div className="font-semibold">New secret for {rotatedSecret.source}</div>
          <div className="mt-1 font-mono break-all">{rotatedSecret.secret || '—'}</div>
          <div className="mt-2 text-amber-800">Copy this now. It won’t be shown again.</div>
          <button
            type="button"
            className="mt-3 px-3 py-2 text-sm font-medium rounded-lg bg-white border border-amber-200 hover:bg-amber-100"
            onClick={() => setRotatedSecret(null)}
          >
            Dismiss
          </button>
        </div>
      ) : null}

      <div className="mt-6 bg-white border border-gray-200 rounded-xl overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full text-sm">
            <thead className="bg-gray-50 border-b border-gray-200">
              <tr className="text-left text-gray-600">
                <th className="px-4 py-3 font-medium">Source</th>
                <th className="px-4 py-3 font-medium">Enabled</th>
                <th className="px-4 py-3 font-medium">Rate / min</th>
                <th className="px-4 py-3 font-medium">Secret</th>
                <th className="px-4 py-3 font-medium">24h</th>
                <th className="px-4 py-3 font-medium">Pending</th>
                <th className="px-4 py-3 font-medium">Errors</th>
                <th className="px-4 py-3 font-medium">Last received</th>
                <th className="px-4 py-3 font-medium">Last processed</th>
                <th className="px-4 py-3 font-medium">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {loading ? (
                <tr>
                  <td className="px-4 py-6 text-gray-600" colSpan={10}>
                    Loading…
                  </td>
                </tr>
              ) : items.length ? (
                items.map((s) => (
                  <tr key={s.source} className="text-gray-900">
                    <td className="px-4 py-3">
                      <div className="font-medium">{s.display_name || s.source}</div>
                      <div className="text-xs text-gray-500">{s.source}</div>
                    </td>
                    <td className="px-4 py-3">
                      <label className="inline-flex items-center gap-2">
                        <input
                          type="checkbox"
                          checked={s.is_enabled}
                          onChange={(e) => updateLocal(s.source, { is_enabled: e.target.checked })}
                        />
                        <span className="text-xs text-gray-600">{s.is_enabled ? 'On' : 'Off'}</span>
                      </label>
                    </td>
                    <td className="px-4 py-3">
                      <input
                        type="number"
                        min={1}
                        className="w-28 px-2 py-1 border border-gray-200 rounded-md"
                        value={s.rate_limit_per_minute}
                        onChange={(e) => updateLocal(s.source, { rate_limit_per_minute: Number(e.target.value || 0) })}
                      />
                    </td>
                    <td className="px-4 py-3">
                      <span className={`inline-flex px-2 py-0.5 rounded-full text-xs ${s.has_secret ? 'bg-green-50 text-green-700' : 'bg-gray-100 text-gray-700'}`}>
                        {s.has_secret ? 'Set' : 'Env'}
                      </span>
                    </td>
                    <td className="px-4 py-3">{s.stats?.received_last_24h ?? 0}</td>
                    <td className="px-4 py-3">{s.stats?.pending_count ?? 0}</td>
                    <td className="px-4 py-3">{s.stats?.error_count ?? 0}</td>
                    <td className="px-4 py-3">{fmtDate(s.stats?.last_received_at)}</td>
                    <td className="px-4 py-3">{fmtDate(s.stats?.last_processed_at)}</td>
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-2">
                        <button
                          type="button"
                          disabled={Boolean(saving[s.source])}
                          onClick={() =>
                            save(s.source, {
                              display_name: s.display_name || null,
                              is_enabled: s.is_enabled,
                              rate_limit_per_minute: s.rate_limit_per_minute,
                            })
                          }
                          className="px-3 py-1.5 text-xs font-medium rounded-md bg-black text-white hover:bg-gray-800 disabled:opacity-50"
                        >
                          Save
                        </button>
                        <button
                          type="button"
                          disabled={Boolean(saving[s.source])}
                          onClick={() => rotate(s.source)}
                          className="px-3 py-1.5 text-xs font-medium rounded-md bg-white border border-gray-200 hover:bg-gray-50 disabled:opacity-50"
                        >
                          Rotate secret
                        </button>
                      </div>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td className="px-4 py-6 text-gray-600" colSpan={10}>
                    No sources found.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}

