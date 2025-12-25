/**
 * OppGrid Auth Helpers
 *
 * Centralizes auth redirect + token retrieval to prevent flow drift.
 */
(function () {
  if (window.OppGridAuth) return;

  function getCurrentLocationPath() {
    return window.location.pathname + window.location.search + window.location.hash;
  }

  function getAccessToken() {
    return localStorage.getItem('access_token');
  }

  function buildSigninUrl(redirectValue) {
    const redirect = redirectValue ?? getCurrentLocationPath();
    return `signin.html?redirect=${encodeURIComponent(redirect)}`;
  }

  function redirectToSignin(options = {}) {
    const url = buildSigninUrl(options.redirect);
    window.location.href = url;
  }

  /**
   * Require auth for a page/flow.
   * Returns true if token exists, otherwise redirects to sign-in and returns false.
   */
  function requireAuth(options = {}) {
    const token = getAccessToken();
    if (token) return true;
    redirectToSignin(options);
    return false;
  }

  window.OppGridAuth = {
    getAccessToken,
    getCurrentLocationPath,
    buildSigninUrl,
    redirectToSignin,
    requireAuth,
  };
})();
