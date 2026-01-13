
https://preview.redd.it/0ha5th29447g1.png?width=567&format=png&auto=webp&s=e2147a4ee8ec5816c2a6a3832b88baa06e6029c5

\# Project Summary



\## FUCKIN-DANS-ASS - Blockchain Forensic Toolkit



\*\*Target:\*\* Illegal casino operations using "Dan" as a common alias/pseudonym in underground gambling networks.



\## Mission



Build irrefutable blockchain evidence of illegal casino operations, fraud, and money laundering through comprehensive on-chain analysis and attribution.



\## What Was Built



\### Core Forensic System (\`forensics/\`)



\*\*1. Transaction Fetcher\*\* (\[transaction-fetcher.js\](../forensics/transaction-fetcher.js))

\- Fetches complete transaction history for any address

\- Supports all major EVM chains via Alchemy API

\- Collects incoming AND outgoing transactions

\- Stores in SQLite for persistent investigation



\*\*2. Attribution Manager\*\* (\[attribution-manager.js\](../forensics/attribution-manager.js))

\- Tag addresses with labels (hack, fraud, scam, victim, etc.)

\- Risk level classification (critical, high, medium, low, info)

\- Event registry for known illegal operations
