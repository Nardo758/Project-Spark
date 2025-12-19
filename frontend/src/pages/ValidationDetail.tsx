import { useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { fetchJson } from '../lib/http';

function asString(v: unknown): string | null {
  if (typeof v === 'string') return v;
  if (typeof v === 'number') return String(v);
  return null;
}

function asNumber(v: unknown): number | null {
  if (typeof v === 'number' && Number.isFinite(v)) return v;
  if (typeof v === 'string' && v.trim() && Number.isFinite(Number(v))) return Number(v);
  return null;
}

function asStringArray(v: unknown): string[] {
  if (!Array.isArray(v)) return [];
  return v.map((x) => asString(x)).filter((x): x is string => Boolean(x));
}

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

            <div style={{ display: 'flex', gap: 12, marginTop: 12, flexWrap: 'wrap' }}>
              <button
                onClick={() => {
                  if (!data.result) return;
                  const blob = new Blob([JSON.stringify(data.result, null, 2)], { type: 'application/json' });
                  const url = URL.createObjectURL(blob);
                  const a = document.createElement('a');
                  a.href = url;
                  a.download = `idea-validation-${data.id}.json`;
                  a.click();
                  URL.revokeObjectURL(url);
                }}
                disabled={!data.result}
              >
                Download JSON
              </button>
              {data.summary ? (
                <button
                  onClick={() => {
                    void navigator.clipboard?.writeText(data.summary ?? '');
                  }}
                >
                  Copy summary
                </button>
              ) : null}
            </div>
          </div>

          {data.result ? (
            <>
              <div style={{ marginTop: 16, display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 12 }}>
                <div style={{ border: '1px solid #eee', borderRadius: 12, padding: 12 }}>
                  <div style={{ fontSize: 12, color: '#666' }}>Market size</div>
                  <div style={{ fontWeight: 700 }}>{asString(data.result.market_size_estimate) ?? '—'}</div>
                </div>
                <div style={{ border: '1px solid #eee', borderRadius: 12, padding: 12 }}>
                  <div style={{ fontSize: 12, color: '#666' }}>Competition</div>
                  <div style={{ fontWeight: 700 }}>{asString(data.result.competition_level) ?? '—'}</div>
                </div>
                <div style={{ border: '1px solid #eee', borderRadius: 12, padding: 12 }}>
                  <div style={{ fontSize: 12, color: '#666' }}>Urgency</div>
                  <div style={{ fontWeight: 700 }}>{asString(data.result.urgency_level) ?? '—'}</div>
                </div>
                <div style={{ border: '1px solid #eee', borderRadius: 12, padding: 12 }}>
                  <div style={{ fontSize: 12, color: '#666' }}>Revenue potential</div>
                  <div style={{ fontWeight: 700 }}>{asString(data.result.revenue_potential) ?? '—'}</div>
                </div>
                <div style={{ border: '1px solid #eee', borderRadius: 12, padding: 12 }}>
                  <div style={{ fontSize: 12, color: '#666' }}>Time to market</div>
                  <div style={{ fontWeight: 700 }}>{asString(data.result.time_to_market) ?? '—'}</div>
                </div>
                <div style={{ border: '1px solid #eee', borderRadius: 12, padding: 12 }}>
                  <div style={{ fontSize: 12, color: '#666' }}>Pain intensity</div>
                  <div style={{ fontWeight: 700 }}>
                    {asNumber(data.result.pain_intensity) != null ? `${asNumber(data.result.pain_intensity)}/10` : '—'}
                  </div>
                </div>
              </div>

              <div style={{ marginTop: 16, border: '1px solid #eee', borderRadius: 12, padding: 16 }}>
                <h3 style={{ marginTop: 0 }}>Business model suggestions</h3>
                <ul>
                  {asStringArray(data.result.business_model_suggestions).map((x, i) => (
                    <li key={i}>{x}</li>
                  ))}
                </ul>
              </div>

              <div style={{ marginTop: 12, border: '1px solid #eee', borderRadius: 12, padding: 16 }}>
                <h3 style={{ marginTop: 0 }}>Competitive advantages</h3>
                <ul>
                  {asStringArray(data.result.competitive_advantages).map((x, i) => (
                    <li key={i}>{x}</li>
                  ))}
                </ul>
              </div>

              <div style={{ marginTop: 12, border: '1px solid #eee', borderRadius: 12, padding: 16 }}>
                <h3 style={{ marginTop: 0 }}>Key risks</h3>
                <ul>
                  {asStringArray(data.result.key_risks).map((x, i) => (
                    <li key={i}>{x}</li>
                  ))}
                </ul>
              </div>

              <div style={{ marginTop: 12, border: '1px solid #eee', borderRadius: 12, padding: 16 }}>
                <h3 style={{ marginTop: 0 }}>Next steps</h3>
                <ol>
                  {asStringArray(data.result.next_steps).map((x, i) => (
                    <li key={i}>{x}</li>
                  ))}
                </ol>
              </div>

              <div style={{ marginTop: 12, border: '1px solid #eee', borderRadius: 12, padding: 16 }}>
                <h3 style={{ marginTop: 0 }}>Market trends</h3>
                <ul>
                  {asStringArray(data.result.market_trends).map((x, i) => (
                    <li key={i}>{x}</li>
                  ))}
                </ul>
              </div>

              <details style={{ marginTop: 16 }}>
                <summary>Raw JSON</summary>
                <pre style={{ background: '#f7f7f7', padding: 12, borderRadius: 8, overflowX: 'auto' }}>
                  {JSON.stringify(data.result, null, 2)}
                </pre>
              </details>
            </>
          ) : (
            <div style={{ marginTop: 16, background: '#fffdf0', padding: 12, borderRadius: 8 }}>
              No result saved yet. Status: <b>{data.status}</b>
            </div>
          )}
        </>
      ) : error ? (
        <pre style={{ marginTop: 12, background: '#fff5f5', padding: 12, borderRadius: 8 }}>{error}</pre>
      ) : (
        <p style={{ marginTop: 12 }}>Loading…</p>
      )}
    </div>
  );
}
