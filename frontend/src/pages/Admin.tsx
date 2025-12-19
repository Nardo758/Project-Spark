import { useEffect, useMemo, useState } from 'react';
import { fetchJson } from '../lib/http';

type AdminStats = {
  total_users: number;
  verified_users: number;
  total_opportunities: number;
  banned_users: number;
};

type StripeWebhookEvent = {
  stripe_event_id: string;
  event_type: string;
  livemode: boolean;
  status: 'processing' | 'processed' | 'failed' | string;
  attempt_count: number;
  stripe_created_at?: string | null;
  received_at?: string | null;
  updated_at?: string | null;
};

type StripeWebhookEventList = {
  items: StripeWebhookEvent[];
  total: number;
};

type PayPerUnlockAttempt = {
  id: number;
  user_id: number;
  opportunity_id: number;
  attempt_date: string; // YYYY-MM-DD
  status: 'created' | 'succeeded' | 'failed' | 'canceled' | string;
  stripe_payment_intent_id?: string | null;
  created_at?: string | null;
};

type PayPerUnlockAttemptList = {
  items: PayPerUnlockAttempt[];
  total: number;
};

export function Admin() {
  const [stats, setStats] = useState<AdminStats | null>(null);
  const [statsError, setStatsError] = useState<string | null>(null);

  const [events, setEvents] = useState<StripeWebhookEventList | null>(null);
  const [eventsError, setEventsError] = useState<string | null>(null);
  const [eventsStatus, setEventsStatus] = useState<string>('failed');

  const [attempts, setAttempts] = useState<PayPerUnlockAttemptList | null>(null);
  const [attemptsError, setAttemptsError] = useState<string | null>(null);
  const [attemptsStatus, setAttemptsStatus] = useState<string>('');
  const [attemptsDate, setAttemptsDate] = useState<string>('');

  useEffect(() => {
    let cancelled = false;
    fetchJson<AdminStats>('/admin/stats')
      .then((data) => {
        if (!cancelled) setStats(data);
      })
      .catch((e: unknown) => {
        if (!cancelled) setStatsError(e instanceof Error ? e.message : String(e));
      });
    return () => {
      cancelled = true;
    };
  }, []);

  const eventsQuery = useMemo(() => {
    const params = new URLSearchParams();
    params.set('limit', '50');
    if (eventsStatus) params.set('status_filter', eventsStatus);
    return params.toString();
  }, [eventsStatus]);

  useEffect(() => {
    let cancelled = false;
    fetchJson<StripeWebhookEventList>(`/admin/stripe/webhook-events?${eventsQuery}`)
      .then((data) => {
        if (!cancelled) setEvents(data);
      })
      .catch((e: unknown) => {
        if (!cancelled) setEventsError(e instanceof Error ? e.message : String(e));
      });
    return () => {
      cancelled = true;
    };
  }, [eventsQuery]);

  const attemptsQuery = useMemo(() => {
    const params = new URLSearchParams();
    params.set('limit', '50');
    if (attemptsStatus) params.set('status_filter', attemptsStatus);
    if (attemptsDate) params.set('attempt_date', attemptsDate);
    return params.toString();
  }, [attemptsDate, attemptsStatus]);

  useEffect(() => {
    let cancelled = false;
    fetchJson<PayPerUnlockAttemptList>(`/admin/stripe/pay-per-unlock-attempts?${attemptsQuery}`)
      .then((data) => {
        if (!cancelled) setAttempts(data);
      })
      .catch((e: unknown) => {
        if (!cancelled) setAttemptsError(e instanceof Error ? e.message : String(e));
      });
    return () => {
      cancelled = true;
    };
  }, [attemptsQuery]);

  return (
    <div style={{ padding: 16 }}>
      <h1>Admin (React)</h1>

      <section style={{ marginTop: 12 }}>
        <h2>Overview</h2>
        {stats ? (
          <pre style={{ background: '#f7f7f7', padding: 12, borderRadius: 8 }}>{JSON.stringify(stats, null, 2)}</pre>
        ) : statsError ? (
          <pre style={{ background: '#fff5f5', padding: 12, borderRadius: 8 }}>{statsError}</pre>
        ) : (
          <p>Loading…</p>
        )}
      </section>

      <section style={{ marginTop: 24 }}>
        <h2>Stripe webhook events</h2>
        <div style={{ display: 'flex', gap: 12, alignItems: 'center', marginBottom: 12, flexWrap: 'wrap' }}>
          <label style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
            Status
            <select
              value={eventsStatus}
              onChange={(e) => {
                setEvents(null);
                setEventsError(null);
                setEventsStatus(e.target.value);
              }}
            >
              <option value="">All</option>
              <option value="failed">failed</option>
              <option value="processing">processing</option>
              <option value="processed">processed</option>
            </select>
          </label>
          <button
            onClick={() => {
              setEvents(null);
              setEventsError(null);
              setEventsStatus('failed');
            }}
          >
            Show failures
          </button>
        </div>

        {events ? (
          events.items.length ? (
            <div style={{ overflowX: 'auto' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                <thead>
                  <tr>
                    <th style={{ textAlign: 'left', borderBottom: '1px solid #eee', padding: 8 }}>Event</th>
                    <th style={{ textAlign: 'left', borderBottom: '1px solid #eee', padding: 8 }}>Type</th>
                    <th style={{ textAlign: 'left', borderBottom: '1px solid #eee', padding: 8 }}>Status</th>
                    <th style={{ textAlign: 'left', borderBottom: '1px solid #eee', padding: 8 }}>Attempts</th>
                    <th style={{ textAlign: 'left', borderBottom: '1px solid #eee', padding: 8 }}>Mode</th>
                    <th style={{ textAlign: 'left', borderBottom: '1px solid #eee', padding: 8 }}>Received</th>
                  </tr>
                </thead>
                <tbody>
                  {events.items.map((ev) => (
                    <tr key={ev.stripe_event_id}>
                      <td style={{ borderBottom: '1px solid #f0f0f0', padding: 8, fontFamily: 'monospace' }}>
                        {ev.stripe_event_id}
                      </td>
                      <td style={{ borderBottom: '1px solid #f0f0f0', padding: 8 }}>{ev.event_type}</td>
                      <td style={{ borderBottom: '1px solid #f0f0f0', padding: 8 }}>{ev.status}</td>
                      <td style={{ borderBottom: '1px solid #f0f0f0', padding: 8 }}>{ev.attempt_count}</td>
                      <td style={{ borderBottom: '1px solid #f0f0f0', padding: 8 }}>{ev.livemode ? 'live' : 'test'}</td>
                      <td style={{ borderBottom: '1px solid #f0f0f0', padding: 8 }}>
                        {ev.received_at ? new Date(ev.received_at).toLocaleString() : '—'}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <p>No events found.</p>
          )
        ) : eventsError ? (
          <pre style={{ background: '#fff5f5', padding: 12, borderRadius: 8 }}>{eventsError}</pre>
        ) : (
          <p>Loading…</p>
        )}
      </section>

      <section style={{ marginTop: 24 }}>
        <h2>Pay-per-unlock attempts</h2>
        <div style={{ display: 'flex', gap: 12, alignItems: 'center', marginBottom: 12, flexWrap: 'wrap' }}>
          <label style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
            Status
            <select
              value={attemptsStatus}
              onChange={(e) => {
                setAttempts(null);
                setAttemptsError(null);
                setAttemptsStatus(e.target.value);
              }}
            >
              <option value="">All</option>
              <option value="created">created</option>
              <option value="succeeded">succeeded</option>
              <option value="failed">failed</option>
              <option value="canceled">canceled</option>
            </select>
          </label>
          <label style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
            Date
            <input
              type="date"
              value={attemptsDate}
              onChange={(e) => {
                setAttempts(null);
                setAttemptsError(null);
                setAttemptsDate(e.target.value);
              }}
            />
          </label>
          <button
            onClick={() => {
              setAttempts(null);
              setAttemptsError(null);
              setAttemptsStatus('');
              setAttemptsDate('');
            }}
          >
            Clear filters
          </button>
        </div>

        {attempts ? (
          attempts.items.length ? (
            <div style={{ overflowX: 'auto' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                <thead>
                  <tr>
                    <th style={{ textAlign: 'left', borderBottom: '1px solid #eee', padding: 8 }}>ID</th>
                    <th style={{ textAlign: 'left', borderBottom: '1px solid #eee', padding: 8 }}>User</th>
                    <th style={{ textAlign: 'left', borderBottom: '1px solid #eee', padding: 8 }}>Opp</th>
                    <th style={{ textAlign: 'left', borderBottom: '1px solid #eee', padding: 8 }}>Date</th>
                    <th style={{ textAlign: 'left', borderBottom: '1px solid #eee', padding: 8 }}>Status</th>
                    <th style={{ textAlign: 'left', borderBottom: '1px solid #eee', padding: 8 }}>PaymentIntent</th>
                  </tr>
                </thead>
                <tbody>
                  {attempts.items.map((a) => (
                    <tr key={a.id}>
                      <td style={{ borderBottom: '1px solid #f0f0f0', padding: 8 }}>{a.id}</td>
                      <td style={{ borderBottom: '1px solid #f0f0f0', padding: 8 }}>{a.user_id}</td>
                      <td style={{ borderBottom: '1px solid #f0f0f0', padding: 8 }}>{a.opportunity_id}</td>
                      <td style={{ borderBottom: '1px solid #f0f0f0', padding: 8 }}>{a.attempt_date}</td>
                      <td style={{ borderBottom: '1px solid #f0f0f0', padding: 8 }}>{a.status}</td>
                      <td style={{ borderBottom: '1px solid #f0f0f0', padding: 8, fontFamily: 'monospace' }}>
                        {a.stripe_payment_intent_id ?? '—'}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <p>No attempts found.</p>
          )
        ) : attemptsError ? (
          <pre style={{ background: '#fff5f5', padding: 12, borderRadius: 8 }}>{attemptsError}</pre>
        ) : (
          <p>Loading…</p>
        )}
      </section>

      <p style={{ marginTop: 24 }}>
        Note: this React admin will replace <code>admin.html</code> once we migrate the full module.
      </p>
    </div>
  );
}
