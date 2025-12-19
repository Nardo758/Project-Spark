import { useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { fetchJson } from '../lib/http';

type IdeaValidationDetail = {
  id: number;
  title: string;
  category: string;
  status: string;
  created_at?: string | null;
  opportunity_score?: number | null;
  summary?: string | null;
  validation_confidence?: number | null;
  result?: Record<string, unknown> | null;
  error_message?: string | null;
};

export function ValidationDetail() {
  const { id } = useParams();
  const [data, setData] = useState<IdeaValidationDetail | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    if (!id) return;

    fetchJson<IdeaValidationDetail>(`/idea-validations/${id}`)
      .then((d) => {
        if (!cancelled) setData(d);
      })
      .catch((e: unknown) => {
        if (!cancelled) setError(e instanceof Error ? e.message : String(e));
      });

    return () => {
      cancelled = true;
    };
  }, [id]);

  return (
    <div style={{ padding: 16, maxWidth: 900 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: 12 }}>
        <h1>Validation #{id}</h1>
        <Link to="/validations">Back to list</Link>
      </div>

      {data ? (
        <>
          <div style={{ marginTop: 12, border: '1px solid #eee', borderRadius: 12, padding: 16 }}>
            <h2 style={{ marginTop: 0 }}>{data.title}</h2>
            <p>
              <b>Category:</b> {data.category}
            </p>
            <p>
              <b>Status:</b> {data.status}
            </p>
            <p>
              <b>Score:</b> {data.opportunity_score ?? '—'}
            </p>
            {data.summary ? (
              <p>
                <b>Summary:</b> {data.summary}
              </p>
            ) : null}
            {data.validation_confidence != null ? (
              <p>
                <b>Confidence:</b> {data.validation_confidence}%
              </p>
            ) : null}
            {data.error_message ? (
              <p style={{ color: '#b91c1c' }}>
                <b>Error:</b> {data.error_message}
              </p>
            ) : null}
          </div>

          <div style={{ marginTop: 16 }}>
            <h3>Raw result</h3>
            {data.result ? (
              <pre style={{ background: '#f7f7f7', padding: 12, borderRadius: 8, overflowX: 'auto' }}>
                {JSON.stringify(data.result, null, 2)}
              </pre>
            ) : (
              <p>No result saved yet.</p>
            )}
          </div>
        </>
      ) : error ? (
        <pre style={{ marginTop: 12, background: '#fff5f5', padding: 12, borderRadius: 8 }}>{error}</pre>
      ) : (
        <p style={{ marginTop: 12 }}>Loading…</p>
      )}
    </div>
  );
}
