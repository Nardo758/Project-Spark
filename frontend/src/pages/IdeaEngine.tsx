import { CardElement, Elements, useElements, useStripe } from '@stripe/react-stripe-js';
import { loadStripe, type Stripe } from '@stripe/stripe-js';
import { useCallback, useEffect, useMemo, useState } from 'react';
import { Link } from 'react-router-dom';
import { fetchJson } from '../lib/http';
import { getAccessToken } from '../lib/auth';

type GeneratedIdea = {
  refined_idea: string;
  title: string;
  problem_statement: string;
  target_audience: string;
  unique_value_proposition: string;
  category: string;
  preview_score: number;
  preview_insights: string[];
};

type CreatePaymentIntentResponse = {
  idea_validation_id: number;
  client_secret: string;
  payment_intent_id: string;
  amount_cents: number;
  currency: string;
};

type ValidationDetail = {
  id: number;
  status: string;
  result?: Record<string, unknown> | null;
  opportunity_score?: number | null;
  summary?: string | null;
  validation_confidence?: number | null;
};

type StripeKeyResponse = { publishable_key: string };

function toSigninHref() {
  return `/signin.html?redirect=${encodeURIComponent('/idea-engine')}`;
}

function PaymentPanel(props: {
  generated: GeneratedIdea;
  stripePromise: Promise<Stripe | null>;
  onValidated: (record: ValidationDetail) => void;
}) {
  return (
    <Elements stripe={props.stripePromise}>
      <PaymentPanelInner generated={props.generated} onValidated={props.onValidated} />
    </Elements>
  );
}

function PaymentPanelInner(props: { generated: GeneratedIdea; onValidated: (record: ValidationDetail) => void }) {
  const stripe = useStripe();
  const elements = useElements();

  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  const payAndValidate = useCallback(async () => {
    setError(null);

    if (!getAccessToken()) {
      window.location.href = toSigninHref();
      return;
    }

    if (!stripe || !elements) {
      setError('Payment system not ready yet.');
      return;
    }

    const card = elements.getElement(CardElement);
    if (!card) {
      setError('Card input not ready.');
      return;
    }

    setBusy(true);
    try {
      const pi = await fetchJson<CreatePaymentIntentResponse>('/idea-validations/create-payment-intent', {
        method: 'POST',
        body: JSON.stringify({
          idea: props.generated.refined_idea,
          title: props.generated.title,
          category: props.generated.category,
          amount_cents: 999,
        }),
      });

      const confirm = await stripe.confirmCardPayment(pi.client_secret, {
        payment_method: { card },
      });

      if (confirm.error) throw new Error(confirm.error.message ?? 'Payment failed');
      if (!confirm.paymentIntent || confirm.paymentIntent.status !== 'succeeded') {
        throw new Error(`Payment not completed (${confirm.paymentIntent?.status ?? 'unknown'})`);
      }

      const record = await fetchJson<ValidationDetail>(`/idea-validations/${pi.idea_validation_id}/run`, {
        method: 'POST',
        body: JSON.stringify({ payment_intent_id: confirm.paymentIntent.id }),
      });

      props.onValidated(record);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setBusy(false);
    }
  }, [elements, props, stripe]);

  return (
    <div style={{ border: '1px solid #eee', borderRadius: 12, padding: 16, marginTop: 16 }}>
      <h3>Full validation (one-time)</h3>
      <p style={{ marginTop: 6 }}>
        Price: <b>$9.99</b>. This saves a report to <Link to="/validations">My Validations</Link>.
      </p>

      <div style={{ marginTop: 12, padding: 12, border: '1px solid #e5e5e5', borderRadius: 8 }}>
        <CardElement options={{ hidePostalCode: true }} />
      </div>

      {error ? (
        <div style={{ marginTop: 12, background: '#fff5f5', padding: 12, borderRadius: 8 }}>{error}</div>
      ) : null}

      <button style={{ marginTop: 12 }} onClick={payAndValidate} disabled={busy || !stripe || !elements}>
        {busy ? 'Processing…' : 'Pay & Run Validation'}
      </button>

      {!getAccessToken() ? (
        <p style={{ marginTop: 8 }}>
          You must <a href={toSigninHref()}>sign in</a> to purchase validations.
        </p>
      ) : null}
    </div>
  );
}

export function IdeaEngine() {
  const [idea, setIdea] = useState('');
  const [generated, setGenerated] = useState<GeneratedIdea | null>(null);
  const [validation, setValidation] = useState<ValidationDetail | null>(null);

  const [stripeKey, setStripeKey] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    fetchJson<StripeKeyResponse>('/idea-engine/stripe-key', { auth: false })
      .then((d) => {
        if (!cancelled) setStripeKey(d.publishable_key);
      })
      .catch(() => {
        // Stripe might be unconfigured; keep UI usable for free generation.
      });

    return () => {
      cancelled = true;
    };
  }, []);

  const stripePromise = useMemo(() => {
    if (!stripeKey) return null;
    return loadStripe(stripeKey);
  }, [stripeKey]);

  const generate = useCallback(async () => {
    setError(null);
    setGenerated(null);
    setValidation(null);

    if (idea.trim().length < 20) {
      setError('Please enter a more detailed idea (20+ characters).');
      return;
    }

    setLoading(true);
    try {
      const data = await fetchJson<GeneratedIdea>('/idea-engine/generate', {
        method: 'POST',
        auth: false,
        body: JSON.stringify({ idea: idea.trim() }),
      });
      setGenerated(data);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setLoading(false);
    }
  }, [idea]);

  return (
    <div style={{ padding: 16, maxWidth: 900 }}>
      <h1>Idea Engine (React)</h1>
      <p>Generate an opportunity for free, then purchase a saved validation report.</p>

      <div style={{ marginTop: 12 }}>
        <textarea
          value={idea}
          onChange={(e) => setIdea(e.target.value)}
          placeholder="Describe your idea…"
          style={{ width: '100%', minHeight: 140, padding: 12 }}
        />
        <div style={{ display: 'flex', gap: 12, alignItems: 'center', marginTop: 8 }}>
          <button onClick={generate} disabled={loading}>
            {loading ? 'Generating…' : 'Generate'}
          </button>
          <a href="/idea-engine.html">Open legacy Idea Engine</a>
        </div>
      </div>

      {error ? <div style={{ marginTop: 12, background: '#fff5f5', padding: 12 }}>{error}</div> : null}

      {generated ? (
        <div style={{ marginTop: 16, border: '1px solid #eee', borderRadius: 12, padding: 16 }}>
          <h2>{generated.title}</h2>
          <p style={{ marginTop: 4 }}>
            <b>Category:</b> {generated.category}
          </p>
          <p style={{ marginTop: 8 }}>{generated.refined_idea}</p>

          <div style={{ marginTop: 12 }}>
            <p>
              <b>Problem:</b> {generated.problem_statement}
            </p>
            <p>
              <b>Audience:</b> {generated.target_audience}
            </p>
            <p>
              <b>UVP:</b> {generated.unique_value_proposition}
            </p>
            <p>
              <b>Preview score:</b> {generated.preview_score}/100
            </p>
          </div>

          {generated.preview_insights?.length ? (
            <div style={{ marginTop: 12 }}>
              <b>Preview insights</b>
              <ul>
                {generated.preview_insights.map((x, i) => (
                  <li key={i}>{x}</li>
                ))}
              </ul>
            </div>
          ) : null}

          {stripePromise ? (
            <PaymentPanel generated={generated} stripePromise={stripePromise} onValidated={(r) => setValidation(r)} />
          ) : (
            <div style={{ marginTop: 16, background: '#fffdf0', padding: 12, borderRadius: 8 }}>
              Stripe is not configured, so paid validations are unavailable right now.
            </div>
          )}

          {validation ? (
            <div style={{ marginTop: 16, background: '#f7f7f7', padding: 12, borderRadius: 8 }}>
              <div>
                Saved validation #{validation.id} ({validation.status}).
              </div>
              {validation.opportunity_score != null ? (
                <div style={{ marginTop: 6 }}>
                  <b>Score:</b> {validation.opportunity_score}
                  {validation.validation_confidence != null ? ` (confidence ${validation.validation_confidence}%)` : null}
                </div>
              ) : null}
              {validation.summary ? (
                <div style={{ marginTop: 6 }}>
                  <b>Summary:</b> {validation.summary}
                </div>
              ) : null}
              <div style={{ marginTop: 8 }}>
                <Link to={`/validations/${validation.id}`}>Open saved report</Link>
                {' · '}
                <Link to="/validations">View all</Link>
              </div>
            </div>
          ) : null}
        </div>
      ) : null}
    </div>
  );
}
