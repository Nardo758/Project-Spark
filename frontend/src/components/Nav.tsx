import { Link } from 'react-router-dom';
import { clearAccessToken, getAccessToken } from '../lib/auth';

export function Nav() {
  const authed = Boolean(getAccessToken());

  return (
    <div style={{ display: 'flex', gap: 12, padding: 12, borderBottom: '1px solid #eee' }}>
      <Link to="/">Home</Link>
      <Link to="/pricing">Pricing</Link>
      <Link to="/validations">My Validations</Link>
      <Link to="/admin">Admin</Link>
      <div style={{ marginLeft: 'auto' }}>
        {authed ? (
          <button
            onClick={() => {
              clearAccessToken();
              window.location.href = '/';
            }}
          >
            Sign out
          </button>
        ) : (
          <a href="/signin.html">Sign in (legacy)</a>
        )}
      </div>
    </div>
  );
}
