import { useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { processReplitAuthCookies, setAccessToken } from '../lib/auth';

export function AuthCallback() {
  const [params] = useSearchParams();
  const navigate = useNavigate();

  useEffect(() => {
    // 1) Prefer Replit Auth cookie handoff (auth_token/auth_user).
    processReplitAuthCookies();

    // 2) Back-compat: allow ?token=... callbacks too.
    const token = params.get('token');
    if (token) setAccessToken(token);

    const next = params.get('next') || '/';
    navigate(next, { replace: true });
  }, [navigate, params]);

  return <div style={{ padding: 16 }}>Signing you in…</div>;
}
