import { useMemo, useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import SimplePage from '../../components/SimplePage'
import { useAuthStore } from '../../stores/authStore'

type Thread = {
  id: number
  thread_type: string
  user_a_id: number
  user_b_id: number
  context_type?: string | null
  context_id?: string | null
  last_message_at?: string | null
}

type Message = {
  id: number
  thread_id: number
  sender_id: number
  body: string
  created_at?: string | null
}

export default function Inbox() {
  const token = useAuthStore((s) => s.token)
  const userId = useAuthStore((s) => s.user?.id)
  const [activeThreadId, setActiveThreadId] = useState<number | null>(null)
  const [draft, setDraft] = useState('')
  const qc = useQueryClient()

  const threadsQuery = useQuery({
    queryKey: ['network-threads'],
    enabled: Boolean(token),
    queryFn: async (): Promise<Thread[]> => {
      const res = await fetch('/api/v1/network/threads', { headers: { Authorization: `Bearer ${token}` } })
      if (!res.ok) throw new Error('Failed to load threads')
      return (await res.json()) as Thread[]
    },
  })

  const messagesQuery = useQuery({
    queryKey: ['network-thread-messages', activeThreadId],
    enabled: Boolean(token && activeThreadId),
    queryFn: async (): Promise<Message[]> => {
      const res = await fetch(`/api/v1/network/threads/${activeThreadId}/messages`, { headers: { Authorization: `Bearer ${token}` } })
      if (!res.ok) throw new Error('Failed to load messages')
      return (await res.json()) as Message[]
    },
  })

  const sendMessage = useMutation({
    mutationFn: async () => {
      if (!token || !activeThreadId) return
      const res = await fetch(`/api/v1/network/threads/${activeThreadId}/messages`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
        body: JSON.stringify({ body: draft }),
      })
      const data = await res.json().catch(() => ({}))
      if (!res.ok) throw new Error(data?.detail || 'Failed to send message')
      return data as Message
    },
    onSuccess: () => {
      setDraft('')
      qc.invalidateQueries({ queryKey: ['network-thread-messages', activeThreadId] })
      qc.invalidateQueries({ queryKey: ['network-threads'] })
    },
  })

  const threadLabel = useMemo(() => {
    const t = (threadsQuery.data ?? []).find((x) => x.id === activeThreadId) || null
    if (!t) return 'Select a thread'
    const other = t.user_a_id === userId ? t.user_b_id : t.user_a_id
    return `Thread #${t.id} (user ${other})`
  }, [threadsQuery.data, activeThreadId, userId])

  return (
    <SimplePage title="Inbox" subtitle="Direct messages and lead connection threads (MVP).">
      <div className="grid lg:grid-cols-3 gap-4">
        <div className="bg-white border border-gray-200 rounded-2xl p-4">
          <div className="text-sm font-semibold text-gray-900">Threads</div>
          <div className="mt-3 space-y-2">
            {(threadsQuery.data ?? []).map((t) => (
              <button
                key={t.id}
                type="button"
                onClick={() => setActiveThreadId(t.id)}
                className={`w-full text-left p-3 rounded-xl border ${
                  activeThreadId === t.id ? 'border-purple-200 bg-purple-50' : 'border-gray-200 hover:bg-gray-50'
                }`}
              >
                <div className="text-sm font-medium text-gray-900">Thread #{t.id}</div>
                <div className="text-xs text-gray-500">
                  {t.context_type ? `${t.context_type}${t.context_id ? `:${t.context_id}` : ''}` : 'direct'}
                </div>
              </button>
            ))}
            {threadsQuery.data && threadsQuery.data.length === 0 ? <div className="text-sm text-gray-600">No threads yet.</div> : null}
          </div>
        </div>

        <div className="lg:col-span-2 bg-white border border-gray-200 rounded-2xl p-4">
          <div className="text-sm font-semibold text-gray-900">{threadLabel}</div>
          <div className="mt-3 h-[360px] overflow-auto border border-gray-200 rounded-xl p-3 bg-gray-50">
            {(messagesQuery.data ?? []).map((m) => (
              <div key={m.id} className={`mb-2 flex ${m.sender_id === userId ? 'justify-end' : 'justify-start'}`}>
                <div className={`max-w-[75%] rounded-xl px-3 py-2 text-sm ${m.sender_id === userId ? 'bg-black text-white' : 'bg-white border border-gray-200 text-gray-800'}`}>
                  {m.body}
                </div>
              </div>
            ))}
            {activeThreadId && messagesQuery.data && messagesQuery.data.length === 0 ? (
              <div className="text-sm text-gray-600">No messages yet.</div>
            ) : null}
            {!activeThreadId ? <div className="text-sm text-gray-600">Pick a thread to view messages.</div> : null}
          </div>

          <div className="mt-3 flex gap-2">
            <input
              value={draft}
              onChange={(e) => setDraft(e.target.value)}
              placeholder="Write a message…"
              className="flex-1 px-3 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              disabled={!activeThreadId}
            />
            <button
              type="button"
              onClick={() => sendMessage.mutate()}
              disabled={!activeThreadId || !draft.trim() || sendMessage.isPending}
              className="px-4 py-2 rounded-lg bg-black text-white hover:bg-gray-800 font-medium disabled:opacity-50"
            >
              Send
            </button>
          </div>
        </div>
      </div>
    </SimplePage>
  )
}

