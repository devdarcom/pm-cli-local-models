# Architecture Change Log

## 2026-05-22

- Added dedicated compression model path in graph flow (`K-04`).
- Enabled graph routing to compression threshold path (`K-05`).
- Ensured post-compression flow continues to final user response (`K-06`).
- Aligned router compression symbol output to `compress` (`G-09`).
- Hardened file read candidate lookup to ignore non-project directories like
  `.venv` for unique filename resolution (`T-12`).

## Notes

- Keep this file to roughly the last 2 weeks of architecture-impacting changes.
- Prefer short, impact-oriented bullets (what changed and why it matters).
