# ADR-005: Model selection and capability policy

## Status
Accepted

## Context
Different tasks require different model capabilities. Tool-calling flow and
compression have distinct runtime requirements.

## Decision
- Session model must be selected from approved tool-capable models in
  `app/session/manager.py`.
- Compression uses a dedicated lightweight model (`gemma3:4b`) independent from
  current session model.
- Model binding for main execution path is cached by model name to avoid
  repeated client setup per call.

## Consequences
- Tool execution flow stays compatible with selected session models.
- Compression cost/latency is controlled independently.
- Runtime overhead from repeated model binding is reduced.
