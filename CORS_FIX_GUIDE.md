# CORS Configuration Guide (Replit)

The application now runs entirely inside Replit, so the default configuration allows all origins for development. You only need to change anything if you attach a **custom domain** or expose the API publicly outside the default Replit URL.

---

## 1. Default behavior

- `server.py` serves both the frontend and a proxy to the backend, so requests originate from the same host (e.g., `https://my-app.username.repl.co`).
- `backend/app/main.py` loads `BACKEND_CORS_ORIGINS` from your environment. `.replit` sets it to `"*"`, which is acceptable for internal preview URLs.

No additional configuration is required while you stay inside the standard Replit domain.

---

## 2. When to restrict origins

Switch to an explicit list if:

- You connected a custom domain (e.g., `https://app.yourdomain.com`)
- You expose the API to another site or native client
- You want to enforce strict production rules

Update the `BACKEND_CORS_ORIGINS` secret in Replit. Example:

```
BACKEND_CORS_ORIGINS=["https://app.yourdomain.com","https://api.yourdomain.com"]
```

Guidelines:
- Always include the full scheme (`https://`)
- Include every origin that will call the API
- Separate entries with commas and wrap the list in square brackets

---

## 3. How to update the value

1. In your Repl, open **Tools → Secrets**
2. Add or edit `BACKEND_CORS_ORIGINS`
3. Click **Run** (or redeploy) so FastAPI picks up the new setting
4. Reload your frontend and retest the API calls

---

## 4. Testing the configuration

- Open your site and perform the action that previously failed
- Watch the browser console for CORS messages
- Use `curl -H "Origin: https://app.yourdomain.com" https://<repl-url>/api/v1/health -v` to confirm allowed origins are echoed back in the `access-control-allow-origin` header

If the header does not match your Origin, verify the JSON array is valid and that the string matches exactly.

---

## 5. Troubleshooting

| Symptom | Fix |
| --- | --- |
| `No Access-Control-Allow-Origin header` | Ensure `BACKEND_CORS_ORIGINS` contains the requesting domain |
| `CORS origin denied` | JSON list may be malformed—make sure you use double quotes and brackets |
| Works locally but not on custom domain | Add the custom domain to the list and redeploy |

By keeping everything hosted on Replit and controlling CORS through a single environment variable, you can tighten or loosen access without touching the codebase.
