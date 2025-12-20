import { useMemo, useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import SimplePage from '../../components/SimplePage'
import { useAuthStore } from '../../stores/authStore'

type ApiKey = {
  id: number
  name: string
  prefix: string
  is_active: boolean
  created_at?: string | null
  last_used_at?: string | null
  revoked_at?: string | null
}

export default function DeveloperPortal() {
  const token = useAuthStore((s) => s.token)
  const qc = useQueryClient()
  const [name, setName] = useState('My key')
  const [lastCreatedKey, setLastCreatedKey] = useState<string | null>(null)

  const keysQuery = useQuery({
    queryKey: ['developer-api-keys'],
    enabled: Boolean(token),
    queryFn: async (): Promise<ApiKey[]> => {
      const res = await fetch('/api/v1/developer/api-keys', { headers: { Authorization: `Bearer ${token}` } })
      const data = await res.json().catch(() => ({}))
      if (!res.ok) throw new Error(data?.detail || 'Failed to load keys')
      return data as ApiKey[]
    },
  })

  const createKey = useMutation({
    mutationFn: async () => {
      const res = await fetch('/api/v1/developer/api-keys', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
        body: JSON.stringify({ name, scopes: ['opportunities:read'] }),
      })
      const data = await res.json().catch(() => ({}))
      if (!res.ok) throw new Error(data?.detail || 'Failed to create key')
      return data as { api_key: string; key: ApiKey }
    },
    onSuccess: (data) => {
      setLastCreatedKey(data.api_key)
      qc.invalidateQueries({ queryKey: ['developer-api-keys'] })
    },
  })

  const revokeKey = useMutation({
    mutationFn: async (id: number) => {
      const res = await fetch(`/api/v1/developer/api-keys/${id}/revoke`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}` },
      })
      const data = await res.json().catch(() => ({}))
      if (!res.ok) throw new Error(data?.detail || 'Failed to revoke key')
      return data as ApiKey
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: ['developer-api-keys'] }),
  })

  const curlExample = useMemo(() => {
    const k = lastCreatedKey || '<YOUR_API_KEY>'
    return `curl -H "X-API-Key: ${k}" "https://YOUR_HOST/api/v1/public-api/opportunities?limit=5"`
  }, [lastCreatedKey])

  return (
    <SimplePage title="Developer portal" subtitle="Create API keys and use the OppGrid API (Business+).">
      {lastCreatedKey ? (
        <div className="mb-6 bg-emerald-50 border border-emerald-200 rounded-2xl p-5">
          <div className="text-sm font-semibold text-emerald-900">New API key (copy now — it won’t be shown again)</div>
          <div className="mt-2 font-mono text-sm text-emerald-900 break-all">{lastCreatedKey}</div>
        </div>
      ) : null}

      <div className="grid lg:grid-cols-3 gap-4">
        <div className="lg:col-span-2 bg-white border border-gray-200 rounded-2xl p-6">
          <div className="text-sm font-semibold text-gray-900">API keys</div>
          <div className="mt-4 flex flex-col sm:flex-row gap-2">
            <input
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="flex-1 px-3 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Key name"
            />
            <button
              type="button"
              onClick={() => createKey.mutate()}
              disabled={!token || !name.trim() || createKey.isPending}
              className="px-4 py-2 rounded-lg bg-black text-white hover:bg-gray-800 font-medium disabled:opacity-50"
            >
              Create key
            </button>
          </div>

          <div className="mt-5 space-y-2">
            {(keysQuery.data ?? []).map((k) => (
              <div key={k.id} className="flex items-center justify-between gap-3 border border-gray-200 rounded-xl p-4">
                <div>
                  <div className="text-sm font-medium text-gray-900">{k.name}</div>
                  <div className="text-xs text-gray-500">
                    prefix: <span className="font-mono">{k.prefix}</span> • {k.is_active ? 'active' : 'revoked'}
                  </div>
                </div>
                <button
                  type="button"
                  onClick={() => revokeKey.mutate(k.id)}
                  disabled={!k.is_active || revokeKey.isPending}
                  className="px-3 py-2 rounded-lg border border-gray-200 hover:bg-gray-50 font-medium text-sm disabled:opacity-50"
                >
                  Revoke
                </button>
              </div>
            ))}
            {keysQuery.data && keysQuery.data.length === 0 ? <div className="text-sm text-gray-600">No keys yet.</div> : null}
          </div>
        </div>

        <div className="bg-white border border-gray-200 rounded-2xl p-6">
          <div className="text-sm font-semibold text-gray-900">Quick start</div>
          <div className="mt-3 text-sm text-gray-700">
            Endpoint: <span className="font-mono">/api/v1/public-api/opportunities</span>
          </div>
          <pre className="mt-3 text-xs bg-gray-50 border border-gray-200 rounded-xl p-3 overflow-auto">{curlExample}</pre>
          <div className="mt-3 text-xs text-gray-500">Note: replace YOUR_HOST with your deployment host.</div>
        </div>
      </div>
    </SimplePage>
  )
}

