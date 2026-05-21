# Multimodel PM — Opis projektu (PRD)

## Cel
Terminalowa aplikacja agentowa (wzorowana na Claude Code / Gemini CLI)
działająca z lokalnymi modelami przez Ollama. Użytkownik wydaje polecenia
agentowi, który wykonuje zadania na plikach i katalogach systemu.

## Stack techniczny
- **Język:** Python
- **TUI:** Textual
- **Agent orchestration:** LangGraph
- **LLM backend:** Ollama (langchain-ollama)
- **AgentState:** Pydantic `BaseModel` z `extra="forbid"` + reducery LangGraph
- **MCP:** mcp (oficjalny Python SDK, tylko remote servers na start)
- **Persistencja sesji:** LangGraph SQLite checkpointer

## Modele (lokalne przez Ollama)
Aktualnie dostępne: gemma3:4b, gemma:7b, gemma:2b, gemma:security
- Model roboczy (agent): wybierany przez użytkownika z dostępnych
- Model kompresji kontekstu: gemma3:4b (szybki, lekki)

## Wymagania funkcjonalne

### Agent
- Agent AI wykonuje zadania zlecone przez użytkownika
- Podstawowe narzędzia: operacje na plikach i katalogach (read, write, list, delete, search)
- Agent zawsze ładuje PROJECT.md jako kontekst systemowy projektu
- Istnieje oddzielny system prompt określający zachowanie agenta
- System respektuje pliki AGENTS.md zgodnie ze standardem rynkowym

### Skille
- Możliwość dodawania skillów zgodnych ze standardem SKILL.md
- Każdy skill może mieć przypisany konkretny model (z dostępnych w Ollama)

### Wieloagentowość
- Supervisor pattern przez tool-calling (nie dedykowana biblioteka langgraph-supervisor)
- `\spawn` używa `Command` object z LangGraph do handoff do sub-agenta
- Każdy sub-agent dostaje izolowany kontekst (tylko task, working_dir, potrzebne tools)
- Każdy agent ma własne połączenia MCP
- Limit kroków agenta: `recursion_count` walidowany przez Pydantic validator (max 25)
- Kolejkowanie Ollamy przez env vars (`OLLAMA_NUM_PARALLEL`, `OLLAMA_MAX_QUEUE`) — nie własna warstwa queue

### Zarządzanie kontekstem
- Czyszczenie kontekstu: nowa sesja lub reset obecnej
- Kompresja kontekstu: compress_node w LangGraph, używa gemma3:4b, batchowo
- Strategia kompresji: cold/hot split — ostatnie 6 wiadomości nietykalnie (hot), reszta kompresowana
- Trigger kompresji: gdy token_count > 75% okna kontekstu modelu
- Kompresja tool outputs: pliki > 2000 tokenów są podsumowywane przed wejściem do stanu

### Obsługa błędów
- Tagowanie stanu: `retry_count`, `last_error`, `error_node`, `error_type` w AgentState
- Retry: max 3 próby, błąd dodawany jako feedback do kolejnego call_model
- Po 3 próbach: dedykowana ścieżka "exhausted" — informacja do użytkownika, reset retry_count
- Narzędzia zwracają opisowe błędy jako string — nie rzucają wyjątków do grafu
- Błędy sub-agentów: supervisor dostaje `SUB_AGENT_FAILED: ...` jako string, nie exception

### MCP
- Obsługa remote MCP servers
- Każdy agent ma własną pulę połączeń MCP

### At-Mentions (`@plik`)
- Użytkownik wpisuje `@` + min. 2 znaki → dropdown z pasującymi plikami projektu (filtrowanie po prefiksie nazwy)
- Wybrany plik wstrzykiwany jako osobny system message: `{"role": "system", "content": "[Załącznik: <nazwa>]\n<treść>"}` — przed wiadomością użytkownika
- Pliki pomijane: `.git`, `__pycache__`, `.venv`, foldery z `.gitignore`
- Limit wyników dropdown: `MAX_FILE_SUGGESTIONS` (stała nazwana)
- Duże pliki (> 2000 tokenów): podsumowywane przed wstrzyknięciem (ta sama logika co `compress_node`)
- Moduł: `app/tui/at_mention.py` + widget w `app/tui/`

### Interfejs (backslash commands)
Wszystkie komendy wywoływane przez `\`:
- `\new` — nowa sesja (nowy agent, czysty kontekst)
- `\reset` — reset kontekstu obecnego agenta
- `\compress` — ręczna kompresja kontekstu
- `\model <name>` — zmiana modelu
- `\spawn` — spawnowanie sub-agenta (przez LangGraph Command)
- `\mcp <url>` — podłączenie remote MCP server
- `\skills` — lista dostępnych skillów
- `\stop` — zakończenie sesji
- `\help` — lista wszystkich komend

### Potwierdzanie działań
- Agent pyta użytkownika przed wykonaniem destruktywnych operacji (Allow/Deny)

## Struktura katalogów

```
multimodel-pm/
├── main.py                  # Punkt wejścia, uruchamia TUI
├── PROJECT.md               # Kontekst systemowy projektu
├── AGENTS.md                # Zasady clean code + architektura dla agenta i developerów
├── opis-projektu.md         # Ten plik — PRD projektu
│
├── app/
│   ├── tui/                 # Textual — ekrany, widgety
│   │   ├── app.py
│   │   ├── at_mention.py    # suggest_files(), resolve_at_mention(), extract_at_mention()
│   │   └── widgets/
│   │
│   ├── agent/               # LangGraph — definicja grafu agenta
│   │   ├── graph.py         # Definicja grafu i węzłów
│   │   ├── nodes.py         # Logika węzłów (call_model, tool_node, compress...)
│   │   ├── state.py         # AgentState (Pydantic BaseModel)
│   │   └── tools.py         # Narzędzia do plików i katalogów
│   │
│   ├── skills/              # Skille zgodne ze standardem SKILL.md
│   ├── mcp/                 # Obsługa remote MCP
│   └── session/             # Zarządzanie sesjami, persistencja SQLite
│
├── .env                     # OLLAMA_NUM_PARALLEL, OLLAMA_MAX_QUEUE itp.
├── config.yaml              # Konfiguracja (modele, limity, MCP servers)
└── requirements.txt
```

> `queue/` usunięty — Ollama ma wbudowaną FIFO kolejkę konfigurowaną przez env vars.

## AgentState — Pydantic schema

```python
class AgentState(BaseModel):
    model_config = ConfigDict(extra="forbid")

    messages: Annotated[list, add_messages]  # reducer: deduplikacja po id
    session_id: str
    model_name: str
    recursion_count: int = 0  # walidowany: max 25

    retry_count: int = 0
    last_error: Optional[str] = None
    error_node: Optional[str] = None
    error_type: Optional[str] = None  # "tool_error" | "model_error" | "validation_error"

    summary: Optional[str] = None        # wynik compress_node
    spawned_agents: Annotated[list[str], operator.add] = []
```

## Graf LangGraph — wizualizacja

```
[START]
   │
   ▼
[load_context]        ← ładuje PROJECT.md, AGENTS.md, skille
   │
   ▼
[call_model]          ← wysyła do Ollamy bezpośrednio (Ollama kolejkuje wewnętrznie)
   │
   ├── should_compress? ──► [compress_node] ──► (z powrotem do call_model)
   │                         (cold context, hot nietykalny)
   │
   ├── tool_call? ──────► [tool_node] ──► (z powrotem do call_model)
   │                           │
   │                      error? → zwraca string błędu (nie exception)
   │
   ├── model_error? ────► [error_handler]
   │                           │
   │                      retry_count < 3 ──► call_model (z error feedbackiem)
   │                      retry_count >= 3 ──► [escalate_to_user]
   │
   └── done ────────────► [output_to_user]

[recursion_count] walidowany przez Pydantic, max 25
```

## Decyzje architektoniczne

| Obszar | Decyzja |
|---|---|
| Kolejka Ollamy | Env vars (`OLLAMA_NUM_PARALLEL`), nie własna warstwa `queue/` |
| AgentState | Pydantic `extra="forbid"` + reducery (nie `@dataclass`) |
| Kompresja | Hot/cold split, trigger na 75% okna, kompresja tool outputs |
| Multi-agent | Supervisor przez tool-calling + `Command` dla `\spawn` |
| Błędy narzędzi | Zwracają string błędu — nie rzucają wyjątków |
| Błędy agenta | Tagowane pola + dedykowana ścieżka "exhausted" |

## Kolejność implementacji

1. ✅ `requirements.txt` + środowisko wirtualne
2. `AgentState` (Pydantic) — **wymaga refaktoru AS-01 do AS-04**
3. Context Loader (nodes.py) — C-01 do C-07
4. Narzędzia plików (tools.py) — T-01 do T-11
5. Graf agenta (graph.py) — G-01 do G-09
6. TUI w Textual (tylko chat input/output)
7. Backslash commands
8. Kompresja kontekstu (compress_node)
9. Supervisor multi-agent + `\spawn`
10. Skille + MCP
