import { useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { setAccessToken } from '../lib/auth';

export function AuthCallback() {
  const [params] = useSearchParams();
  const navigate = useNavigate();

  useEffect(() => {
    const token = params.get('token');
    if (token) setAccessToken(token);
    navigate('/', { replace: true });
  }, [navigate, params]);

  return <div style={{ padding: 16 }}>Signing you in…</div>;
}
