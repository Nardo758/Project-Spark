import { useEffect, useState } from 'react';
import { fetchJson } from '../lib/http';

type AdminStats = {
  total_users: number;
  verified_users: number;
  total_opportunities: number;
  banned_users: number;
};

export function Admin() {
  const [stats, setStats] = useState<AdminStats | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    fetchJson<AdminStats>('/admin/stats')
      .then((data) => {
        if (!cancelled) setStats(data);
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
      <h1>Admin (React)</h1>
      {stats ? (
        <pre style={{ background: '#f7f7f7', padding: 12, borderRadius: 8 }}>{JSON.stringify(stats, null, 2)}</pre>
      ) : error ? (
        <pre style={{ background: '#fff5f5', padding: 12, borderRadius: 8 }}>{error}</pre>
      ) : (
        <p>Loading…</p>
      )}
      <p style={{ marginTop: 12 }}>
        Note: this will replace <code>admin.html</code> once the full module is migrated.
      </p>
    </div>
  );
}
