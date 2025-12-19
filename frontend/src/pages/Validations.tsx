import { useEffect, useState } from 'react';
import { fetchJson } from '../lib/http';
import { Link } from 'react-router-dom';

type IdeaValidationItem = {
  id: number;
  user_id: number;
  title: string;
  category: string;
  status: string;
  stripe_payment_intent_id?: string | null;
  amount_cents?: number | null;
  currency?: string | null;
  opportunity_score?: number | null;
  summary?: string | null;
  validation_confidence?: number | null;
  created_at: string;
};

type IdeaValidationList = {
  items: IdeaValidationItem[];
  total: number;
};

export function Validations() {
  const [data, setData] = useState<IdeaValidationList | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    fetchJson<IdeaValidationList>('/idea-validations/my?limit=50')
      .then((d) => {
        if (!cancelled) setData(d);
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
      <h1>My Idea Validations</h1>
      {data ? (
        data.items.length ? (
          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
              <thead>
                <tr>
                  <th style={{ textAlign: 'left', borderBottom: '1px solid #eee', padding: 8 }}>ID</th>
                  <th style={{ textAlign: 'left', borderBottom: '1px solid #eee', padding: 8 }}>Title</th>
                  <th style={{ textAlign: 'left', borderBottom: '1px solid #eee', padding: 8 }}>Category</th>
                  <th style={{ textAlign: 'left', borderBottom: '1px solid #eee', padding: 8 }}>Status</th>
                  <th style={{ textAlign: 'left', borderBottom: '1px solid #eee', padding: 8 }}>Score</th>
                  <th style={{ textAlign: 'left', borderBottom: '1px solid #eee', padding: 8 }}>Created</th>
                </tr>
              </thead>
              <tbody>
                {data.items.map((v) => (
                  <tr key={v.id}>
                    <td style={{ borderBottom: '1px solid #f0f0f0', padding: 8 }}>{v.id}</td>
                    <td style={{ borderBottom: '1px solid #f0f0f0', padding: 8 }}>
                      <Link to={`/validations/${v.id}`}>{v.title}</Link>
                    </td>
                    <td style={{ borderBottom: '1px solid #f0f0f0', padding: 8 }}>{v.category}</td>
                    <td style={{ borderBottom: '1px solid #f0f0f0', padding: 8 }}>{v.status}</td>
                    <td style={{ borderBottom: '1px solid #f0f0f0', padding: 8 }}>{v.opportunity_score ?? '—'}</td>
                    <td style={{ borderBottom: '1px solid #f0f0f0', padding: 8 }}>
                      {v.created_at ? new Date(v.created_at).toLocaleString() : '—'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <p>No validations yet.</p>
        )
      ) : error ? (
        <pre style={{ background: '#fff5f5', padding: 12, borderRadius: 8 }}>{error}</pre>
      ) : (
        <p>Loading…</p>
      )}

      <p style={{ marginTop: 12 }}>
        Create new ones from <Link to="/idea-engine">Idea Engine</Link>.
      </p>
    </div>
  );
}
