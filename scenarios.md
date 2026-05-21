# Scenarios — Multimodel PM

Legenda typów: `UNIT` = test jednostkowy, `INT` = test integracyjny (mockowana Ollama)
Legenda statusów: `todo` = do zrobienia, `done` = PR przeszło, `cancelled` = wycofano z architektury

---

## Session (`app/session/`)

| ID | Typ | Opis | Status |
|---|---|---|---|
| S-01 | UNIT | `create_session()` zwraca Session z poprawnym modelem i pustą historią | done |
| S-02 | UNIT | `create_session()` z nieznanym modelem rzuca `ValueError` | done |
| S-03 | UNIT | `reset_session()` czyści historię ale zachowuje model | done |
| S-04 | UNIT | `session` ma unikalny `session_id` przy każdym wywołaniu `create_session()` | done |

---

## Context Loader (`app/agent/nodes.py`)

| ID | Typ | Opis | Status |
|---|---|---|---|
| C-01 | UNIT | `load_project_context()` zwraca treść PROJECT.md gdy plik istnieje | done |
| C-02 | UNIT | `load_project_context()` zwraca `None` gdy PROJECT.md nie istnieje | done |
| C-03 | UNIT | `load_system_prompt()` zwraca treść pliku system prompt | todo |
| C-04 | UNIT | `build_prompt()` łączy system_prompt + project_context w jeden message | todo |
| C-05 | UNIT | `build_prompt()` pomija project_context gdy jest `None` | todo |
| C-06 | UNIT | `load_agents_md()` zwraca treść AGENTS.md gdy plik istnieje | todo |
| C-07 | UNIT | `load_agents_md()` zwraca `None` gdy AGENTS.md nie istnieje | todo |

---

## AgentState (`app/agent/state.py`)

| ID | Typ | Opis | Status |
|---|---|---|---|
| AS-01 | UNIT | `AgentState` jest Pydantic BaseModel z polami: `messages`, `session_id`, `model_name`, `recursion_count`, `retry_count`, `last_error`, `error_node`, `error_type`, `summary`, `spawned_agents` | done |
| AS-02 | UNIT | `extra="forbid"` rzuca `ValidationError` dla nieznanych pól | done |
| AS-03 | UNIT | `recursion_count > 25` rzuca `ValidationError` | done |
| AS-04 | UNIT | Domyślne wartości: `messages=[]`, `recursion_count=0`, `retry_count=0`, pola Optional domyślnie `None` | done |

---

## Narzędzia plików (`app/agent/tools.py`)

| ID | Typ | Opis | Status |
|---|---|---|---|
| T-01 | UNIT | `read_file()` zwraca treść pliku gdy istnieje | todo |
| T-02 | UNIT | `read_file()` zwraca error dict gdy plik nie istnieje | todo |
| T-03 | UNIT | `read_file()` zwraca error dict gdy brak uprawnień | todo |
| T-04 | UNIT | `write_file()` tworzy plik z podaną treścią | todo |
| T-05 | UNIT | `write_file()` zwraca error dict gdy katalog nie istnieje | todo |
| T-06 | UNIT | `list_directory()` zwraca listę plików w katalogu | todo |
| T-07 | UNIT | `list_directory()` zwraca error dict gdy katalog nie istnieje | todo |
| T-08 | UNIT | `delete_file()` usuwa plik i zwraca status ok | todo |
| T-09 | UNIT | `delete_file()` zwraca error dict gdy plik nie istnieje | todo |
| T-10 | UNIT | `search_in_files()` zwraca listę plików zawierających frazę | todo |
| T-11 | UNIT | `search_in_files()` zwraca pustą listę gdy fraza nie znaleziona | todo |

---

## Graf agenta (`app/agent/graph.py`, `nodes.py`)

| ID | Typ | Opis | Status |
|---|---|---|---|
| G-01 | INT | Graf przyjmuje wiadomość użytkownika i zwraca odpowiedź (mock model) | todo |
| G-02 | INT | Graf ładuje context i dodaje go jako system message przed pierwszym wywołaniem modelu | todo |
| G-03 | INT | Graf kończy się gdy model nie zwróci `tool_call` (brak dalszych kroków w grafie) | todo |
| G-04 | INT | Graf wywołuje `tool_node` gdy model zwróci `tool_call` | todo |
| G-05 | INT | Graf wraca do `call_model` po wykonaniu narzędzia | todo |
| G-06 | INT | Graf zatrzymuje się po `recursion_limit` krokach | todo |
| G-07 | UNIT | Router zwraca `"tool_node"` gdy response zawiera `tool_call` | todo |
| G-08 | UNIT | Router zwraca `"done"` gdy response nie zawiera `tool_call` | todo |
| G-09 | UNIT | Router zwraca `"compress"` gdy liczba wiadomości > `COMPRESSION_THRESHOLD` | todo |

---

## Kolejka requestów (`app/queue/request_queue.py`)

> ⚠️ **Cancelled** — kolejkowanie delegowane do Ollamy via `OLLAMA_NUM_PARALLEL` i `OLLAMA_MAX_QUEUE`. Moduł `queue/` nie powstanie.

| ID | Typ | Opis | Status |
|---|---|---|---|
| Q-01 | UNIT | `RequestQueue.add()` dodaje request do kolejki | cancelled |
| Q-02 | UNIT | `RequestQueue` przetwarza requesty w kolejności FIFO | cancelled |
| Q-03 | UNIT | `RequestQueue.cancel()` usuwa oczekujący request z kolejki | cancelled |
| Q-04 | INT | Dwa agenty wysyłające jednocześnie nie blokują się wzajemnie | cancelled |

---

## Obsługa błędów (`app/agent/nodes.py`)

| ID | Typ | Opis | Status |
|---|---|---|---|
| E-01 | UNIT | `error_handler` inkrementuje `retry_count` i ustawia `last_error`, `error_node`, `error_type` w stanie | todo |
| E-02 | UNIT | `error_handler` zwraca `Command` z przejściem do retry gdy `retry_count` < 3 | todo |
| E-03 | UNIT | `error_handler` zwraca `Command` z przejściem do escalate gdy `retry_count` >= 3 | todo |
| E-04 | INT | Agent ponawia wywołanie modelu po błędnym output (max 3 razy) | todo |
| E-05 | INT | Agent zwraca błąd do użytkownika po 3 nieudanych próbach | todo |
| E-06 | INT | Narzędzia zwracają error string zamiast rzucać wyjątek | todo |

---

## Kompresja kontekstu (`app/agent/nodes.py`)

| ID | Typ | Opis | Status |
|---|---|---|---|
| K-01 | UNIT | `compress_history()` zachowuje system message jako pierwszy element | todo |
| K-02 | UNIT | `compress_history()` redukuje historię do 2 wiadomości (system + summary) | todo |
| K-03 | UNIT | `compress_history()` wynik zawiera tag `[Skompresowany kontekst]` | todo |
| K-04 | INT | `compress_node` wywołuje mały model (`gemma3:4b`) nie model roboczy | todo |
| K-05 | INT | Graf przekierowuje do `compress_node` gdy `messages > THRESHOLD` | todo |
| K-06 | INT | Po kompresji graf kontynuuje odpowiedź użytkownikowi | todo |

---

## Backslash Commands (`app/tui/`)

| ID | Typ | Opis | Status |
|---|---|---|---|
| B-01 | UNIT | `parse_command("\new")` zwraca `Command.NEW` | todo |
| B-02 | UNIT | `parse_command("\reset")` zwraca `Command.RESET` | todo |
| B-03 | UNIT | `parse_command("\compress")` zwraca `Command.COMPRESS` | todo |
| B-04 | UNIT | `parse_command("\model gemma:7b")` zwraca `Command.MODEL` z arg `"gemma:7b"` | todo |
| B-05 | UNIT | `parse_command("\spawn")` zwraca `Command.SPAWN` | todo |
| B-06 | UNIT | `parse_command("\mcp http://...")` zwraca `Command.MCP` z arg url | todo |
| B-07 | UNIT | `parse_command("\skills")` zwraca `Command.SKILLS` | todo |
| B-08 | UNIT | `parse_command("\stop")` zwraca `Command.STOP` | todo |
| B-09 | UNIT | `parse_command("\help")` zwraca `Command.HELP` | todo |
| B-10 | UNIT | `parse_command("zwykły tekst")` zwraca `None` (nie jest komendą) | todo |
| B-11 | UNIT | `parse_command("\model")` bez arg zwraca błąd brakującego argumentu | todo |

---

## Zmiana modelu (`app/session/`)

| ID | Typ | Opis | Status |
|---|---|---|---|
| M-01 | UNIT | `set_model()` aktualizuje model w sesji gdy model jest na liście dostępnych | todo |
| M-02 | UNIT | `set_model()` zwraca błąd gdy model nie jest dostępny | todo |
| M-03 | INT | `available_models()` zwraca listę z Ollamy (mock: `["gemma3:4b", "gemma:7b"]`) | todo |

---

## Skille (`app/skills/`)

| ID | Typ | Opis | Status |
|---|---|---|---|
| SK-01 | UNIT | `load_skill()` czyta SKILL.md z katalogu skilla | todo |
| SK-02 | UNIT | `load_skill()` zwraca `None` gdy SKILL.md nie istnieje | todo |
| SK-03 | UNIT | `load_skill()` odczytuje przypisany model ze SKILL.md gdy jest podany | todo |
| SK-04 | UNIT | `load_skill()` używa domyślnego modelu gdy skill nie ma przypisanego | todo |
| SK-05 | UNIT | `list_skills()` zwraca listę nazw skillów z katalogu `skills/` | todo |
| SK-06 | INT | Graf używa modelu ze skilla zamiast modelu roboczego sesji | todo |

---

## MCP (`app/mcp/client.py`)

| ID | Typ | Opis | Status |
|---|---|---|---|
| MCP-01 | UNIT | `MCPClient.connect()` przechowuje url serwera | todo |
| MCP-02 | UNIT | `MCPClient` jest przypisany do konkretnego agenta (`agent_id`) | todo |
| MCP-03 | INT | `\mcp <url>` dodaje połączenie MCP do aktywnego agenta | todo |
| MCP-04 | INT | Dwa agenty mają osobne instancje `MCPClient` | todo |

---

## Wieloagentowość (`app/agent/`)

| ID | Typ | Opis | Status |
|---|---|---|---|
| A-01 | UNIT | `AgentManager.spawn()` tworzy nowego agenta z unikalnym id | todo |
| A-02 | UNIT | `AgentManager.get(agent_id)` zwraca właściwego agenta | todo |
| A-03 | UNIT | `AgentManager.list()` zwraca listę aktywnych agentów | todo |
| A-04 | INT | `\spawn` tworzy sub-agenta i przełącza aktywną sesję | todo |

---

## Potwierdzanie destruktywnych akcji (`app/agent/`)

| ID | Typ | Opis | Status |
|---|---|---|---|
| D-01 | UNIT | `is_destructive_tool()` zwraca `True` dla `delete_file` | todo |
| D-02 | UNIT | `is_destructive_tool()` zwraca `False` dla `read_file` i `list_directory` | todo |
| D-03 | INT | Agent przed `delete_file` pyta użytkownika (oczekuje na Allow/Deny) | todo |
| D-04 | INT | Agent nie wykonuje `delete_file` gdy użytkownik odpowie Deny | todo |
| D-05 | INT | Agent wykonuje `delete_file` gdy użytkownik odpowie Allow | todo |

---

## Podsumowanie

| Moduł | UNIT | INT | Łącznie | Done | Cancelled |
|---|---|---|---|---|---|
| Session | 4 | 0 | 4 | 4 | 0 |
| Context Loader | 7 | 0 | 7 | 2 | 0 |
| AgentState | 4 | 0 | 4 | 4 | 0 |
| Narzędzia plików | 11 | 0 | 11 | 0 | 0 |
| Graf agenta | 3 | 6 | 9 | 0 | 0 |
| Kolejka | 3 | 1 | 4 | 0 | 4 |
| Obsługa błędów | 3 | 3 | 6 | 0 | 0 |
| Kompresja | 3 | 3 | 6 | 0 | 0 |
| Backslash Commands | 11 | 0 | 11 | 0 | 0 |
| Zmiana modelu | 2 | 1 | 3 | 0 | 0 |
| Skille | 5 | 1 | 6 | 0 | 0 |
| MCP | 2 | 2 | 4 | 0 | 0 |
| Wieloagentowość | 3 | 1 | 4 | 0 | 0 |
| Potwierdzanie akcji | 2 | 3 | 5 | 0 | 0 |
| **Łącznie** | **63** | **21** | **84** | **10** | **4** |
