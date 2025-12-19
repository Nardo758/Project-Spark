export function Pricing() {
  return (
    <div style={{ padding: 16 }}>
      <h1>Pricing</h1>
      <p>Next: implement the “freshness-first” tiers + checkout flows using existing FastAPI endpoints.</p>
      <ul>
        <li>Free → ARCHIVE preview + optional unlocks</li>
        <li>Pro → VALIDATED</li>
        <li>Business → FRESH</li>
        <li>Enterprise → HOT</li>
      </ul>
    </div>
  );
}
