import { useMemo, useState } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'
import { fetchJson } from '../lib/http'

type MagicLinkSendResponse = {
  message: string
  email: string
}

export function Login() {
  const location = useLocation()
  const navigate = useNavigate()

  const next = useMemo(() => {
    const params = new URLSearchParams(location.search)
    return params.get('next') || '/'
  }, [location.search])

  const [email, setEmail] = useState('')
  const [status, setStatus] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [sending, setSending] = useState(false)

  function startReplitAuth() {
    const redirectUrl = `/auth/callback?next=${encodeURIComponent(next)}`
    window.location.href = `/auth/login?redirect_url=${encodeURIComponent(redirectUrl)}`
  }

  async function sendMagicLink() {
    setError(null)
    setStatus(null)
    const trimmed = email.trim()
    if (!trimmed) {
      setError('Enter your email.')
      return
    }

    try {
      setSending(true)
      const res = await fetchJson<MagicLinkSendResponse>('/magic-link/send', {
        method: 'POST',
        body: JSON.stringify({ email: trimmed }),
        auth: false,
      })
      setStatus(res.message || 'Magic link sent. Check your email.')
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to send magic link.')
    } finally {
      setSending(false)
    }
  }

  return (
    <div style={{ maxWidth: 520, margin: '32px auto', padding: 16 }}>
      <h1 style={{ marginBottom: 8 }}>Sign in</h1>
      <p style={{ marginTop: 0, opacity: 0.8 }}>Use Replit Auth or get a magic link.</p>

      <div style={{ display: 'grid', gap: 12, marginTop: 20 }}>
        <button onClick={startReplitAuth} style={{ padding: '12px 14px', fontWeight: 600 }}>
          Continue with Replit
        </button>

        <div style={{ border: '1px solid #e7e5e4', borderRadius: 12, padding: 12 }}>
          <div style={{ fontWeight: 600, marginBottom: 8 }}>Magic link (email)</div>
          <div style={{ display: 'flex', gap: 8 }}>
            <input
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="you@example.com"
              type="email"
              style={{ flex: 1, padding: '10px 12px' }}
            />
            <button onClick={sendMagicLink} disabled={sending} style={{ padding: '10px 12px' }}>
              {sending ? 'Sending…' : 'Send'}
            </button>
          </div>
          {status && <div style={{ marginTop: 10, color: '#047857' }}>{status}</div>}
          {error && <div style={{ marginTop: 10, color: '#dc2626' }}>{error}</div>}
        </div>

        <button onClick={() => navigate('/')} style={{ padding: '10px 12px', opacity: 0.8 }}>
          Back to home
        </button>
      </div>
    </div>
  )
}

