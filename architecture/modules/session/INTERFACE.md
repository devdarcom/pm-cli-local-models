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

## Change Rules

- Any session API change must keep unit coverage for:
  - create,
  - reset,
  - invalid model path,
  - unique session ID path.
