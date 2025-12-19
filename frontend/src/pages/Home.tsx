import { useEffect, useState } from 'react';
import { fetchJson } from '../lib/http';

type Me = {
  id: number;
  email: string;
  name: string;
  is_admin?: boolean;
};

export function Home() {
  const [me, setMe] = useState<Me | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    fetchJson<Me>('/users/me')
      .then((data) => {
        if (!cancelled) setMe(data);
      })
      .catch((e: unknown) => {
        if (!cancelled) setError(e instanceof Error ? e.message : String(e));
      });
    return () => {
      cancelled = true;
    };
  }, []);

  return (
    <div style={{ padding: 16 }}>
      <h1>OppGrid (React)</h1>
      <p>This is the new React app scaffold. It will progressively replace the static HTML pages.</p>

      <h2>Auth check</h2>
      {me ? (
        <pre style={{ background: '#f7f7f7', padding: 12, borderRadius: 8 }}>{JSON.stringify(me, null, 2)}</pre>
      ) : error ? (
        <pre style={{ background: '#fff5f5', padding: 12, borderRadius: 8 }}>{error}</pre>
      ) : (
        <p>Loading…</p>
      )}
    </div>
  );
}
