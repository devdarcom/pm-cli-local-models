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
- Możliwość spawnowania więcej niż 1 agenta (praca równoległa lub sekwencyjna)
- Kolejkowanie requestów do Ollamy (jeden punkt dostępu, FIFO)
- Każdy agent ma własne połączenia MCP
- Limit kroków agenta: recursion_limit (ochrona przed pętlą)

### Zarządzanie kontekstem
- Czyszczenie kontekstu: nowa sesja lub reset obecnej
- Kompresja kontekstu: osobny node w grafie LangGraph, używa małego modelu
- Kompresja działa batchowo (nie streaming) by nie obciążać RAM

### Obsługa błędów
- Błędny output modelu: automatyczny retry (max 3 próby) z feedbackiem błędu
- Błąd narzędzia: error handler per node, agent dostaje komunikat i próbuje inaczej
- Pętla agenta: recursion_limit=25 (konfigurowalne)

### MCP
- Obsługa remote MCP servers
- Każdy agent ma własną pulę połączeń MCP

### Interfejs (backslash commands)
Wszystkie komendy wywoływane przez `\`:
- `\new` — nowa sesja (nowy agent, czysty kontekst)
- `\reset` — reset kontekstu obecnego agenta
- `\compress` — ręczna kompresja kontekstu
- `\model <name>` — zmiana modelu
- `\spawn` — spawnowanie sub-agenta
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
├── AGENTS.md                # Zasady clean code dla agenta i developerów
├── opis-projektu.md         # Ten plik — PRD projektu
│
├── app/
│   ├── tui/                 # Textual — ekrany, widgety
│   │   ├── app.py
│   │   └── widgets/
│   │
│   ├── agent/               # LangGraph — definicja grafu agenta
│   │   ├── graph.py         # Definicja grafu i węzłów
│   │   ├── nodes.py         # Logika węzłów (call_model, tool_node, compress...)
│   │   ├── state.py         # AgentState
│   │   └── tools.py         # Narzędzia do plików i katalogów
│   │
│   ├── skills/              # Skille zgodne ze standardem SKILL.md
│   ├── queue/               # Kolejkowanie requestów do Ollamy
│   ├── mcp/                 # Obsługa remote MCP
│   └── session/             # Zarządzanie sesjami, persistencja SQLite
│
├── config.yaml              # Konfiguracja (modele, limity, MCP servers)
└── requirements.txt
```

## Graf LangGraph — uproszczona wizualizacja

```
[START]
   │
   ▼
[load_context]        ← ładuje PROJECT.md, AGENTS.md, skille
   │
   ▼
[call_model]          ← wysyła do Ollamy (przez kolejkę)
   │
   ├── tool_call? ──► [tool_node] ──► (z powrotem do call_model)
   │                       │
   │                   error? ──► [error_handler] ──► retry lub user
   │
   ├── compress? ───► [compress_node]  ← mały model, batchowo
   │
   └── done ────────► [output_to_user]

[recursion_limit=25] na całej pętli call_model → tool_node
```

## Kolejność implementacji

1. `requirements.txt` + środowisko wirtualne
2. Prosty graph.py z LangGraph + połączenie z Ollama
3. Podstawowe narzędzia (read/write/list plików)
4. TUI w Textual (tylko chat input/output)
5. Backslash commands
6. Kompresja kontekstu
7. Wieloagentowość + kolejkowanie
8. Skille + MCP
