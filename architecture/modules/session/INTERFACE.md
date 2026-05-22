# Session Module Interface

## Scope
`app/session/*`

## Public Contracts

- Session creation validates model selection.
- Session reset keeps model and clears conversation state.
- Session identity is unique per creation call.

## Invariants

- Session model must be from allowed models list.
- Session ID uniqueness is required for agent/session separation.
- Session model policy must keep tool-calling compatibility.
- Compression model selection is independent from session model selection.

## Change Rules

- Any session API change must keep unit coverage for:
  - create,
  - reset,
  - invalid model path,
  - unique session ID path.
- Any change to model allowlist policy should be reflected in architecture ADRs.
