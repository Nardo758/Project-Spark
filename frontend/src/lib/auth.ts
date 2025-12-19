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
