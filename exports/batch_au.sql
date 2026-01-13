
\- Address clustering for related wallets

\- Reputation checking system



\*\*3. Timeline Analyzer\*\* (\[timeline-analyzer.js\](../forensics/timeline-analyzer.js))

\- Chronological transaction analysis

\- Fund flow path tracing

\- Suspicious pattern detection (rapid transfers, automation, etc.)

\- Flagged address interaction tracking



\*\*4. Report Exporter\*\* (\[report-exporter.js\](../forensics/report-exporter.js))

\- Generate court-ready forensic reports

\- Export formats: JSON (data), CSV (transactions), Markdown (readable)

\- Executive summaries with statistics

\- Complete evidence documentation



\*\*5. Main CLI\*\* (\[index.js\](../forensics/index.js))

\- Interactive forensic investigation interface

\- 9 major investigation operations

\- Guided workflows for common scenarios



\### Enhanced Database Schema



\*\*New Tables:\*\*

\- \`transactions\` - Complete transaction history with timestamps

\- \`address\_attributions\` - Tagged addresses with risk levels
