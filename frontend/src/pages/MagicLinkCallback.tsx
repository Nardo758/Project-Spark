import { useEffect, useState } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { setAccessToken } from '../lib/auth'
import { fetchJson } from '../lib/http'

type MagicVerifyResponse = {
  access_token: string
  token_type: string
  user: unknown
}

export function MagicLinkCallback() {
  const [params] = useSearchParams()
  const navigate = useNavigate()
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const token = params.get('token')
    const next = params.get('next') || '/'
    if (!token) {
      setError('Missing magic link token. Please request a new link.')
      return
    }

    ;(async () => {
      try {
        const data = await fetchJson<MagicVerifyResponse>('/magic-link/verify', {
          method: 'POST',
          body: JSON.stringify({ token }),
          auth: false,
        })
        setAccessToken(data.access_token)
        if (data.user) localStorage.setItem('user', JSON.stringify(data.user))
        navigate(next, { replace: true })
      } catch (e) {
        setError(e instanceof Error ? e.message : 'Failed to verify magic link.')
      }
    })()
  }, [navigate, params])

  if (error) {
    return (
      <div style={{ maxWidth: 520, margin: '32px auto', padding: 16 }}>
        <h1>Sign-in link error</h1>
        <p style={{ color: '#dc2626' }}>{error}</p>
        <a href="/login">Back to login</a>
      </div>
    )
  }

  return <div style={{ padding: 16 }}>Signing you in…</div>
}

