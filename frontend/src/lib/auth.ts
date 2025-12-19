const TOKEN_KEYS = ['access_token', 'token'] as const;

export function getAccessToken(): string | null {
  for (const k of TOKEN_KEYS) {
    const v = localStorage.getItem(k);
    if (v) return v;
  }
  return null;
}

export function setAccessToken(token: string): void {
  localStorage.setItem('access_token', token);
  localStorage.setItem('token', token);
}

export function clearAccessToken(): void {
  for (const k of TOKEN_KEYS) localStorage.removeItem(k);
}

function parseCookies(): Record<string, string> {
  return document.cookie.split(';').reduce<Record<string, string>>((acc, c) => {
    const [rawKey, ...rest] = c.trim().split('=');
    const key = rawKey?.trim();
    if (!key) return acc;
    const val = rest.join('=');
    acc[key] = val;
    return acc;
  }, {});
}

function clearCookie(name: string): void {
  // Must match path used by server cookie; current backend uses path=/ (default).
  document.cookie = `${name}=; max-age=0; path=/`;
}

/**
 * Replit Auth cookie handoff:
 * backend sets short-lived cookies `auth_token` and `auth_user` after OIDC login,
 * then redirects to the app. We pick them up and convert to localStorage.
 */
export function processReplitAuthCookies(): { token?: string; user?: unknown } | null {
  if (typeof document === 'undefined') return null;
  const cookies = parseCookies();

  const out: { token?: string; user?: unknown } = {};

  if (cookies.auth_token) {
    try {
      const token = decodeURIComponent(cookies.auth_token);
      setAccessToken(token);
      out.token = token;
    } finally {
      clearCookie('auth_token');
    }
  }

  if (cookies.auth_user) {
    try {
      const b64 = decodeURIComponent(cookies.auth_user);
      const json = atob(b64);
      const user = JSON.parse(json) as unknown;
      localStorage.setItem('user', JSON.stringify(user));
      out.user = user;
    } catch {
      // If parsing fails, still clear cookie to avoid loops.
    } finally {
      clearCookie('auth_user');
    }
  }

  return out.token || out.user ? out : null;
}
