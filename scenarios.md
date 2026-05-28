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
| C-03 | UNIT | `load_system_prompt()` zwraca treść pliku system prompt | done |
| C-04 | UNIT | `build_prompt()` łączy system_prompt + agents_context + project_context w jeden system message | done |
| C-04b | UNIT | `build_prompt()` zachowuje kolejność: agents_context przed project_context | done |
| C-05 | UNIT | `build_prompt()` pomija project_context gdy jest `None` | done |
| C-05b | UNIT | `build_prompt()` pomija agents_context gdy jest `None` | done |
| C-06 | UNIT | `load_agents_md()` zwraca treść AGENTS.md gdy plik istnieje | done |
| C-07 | UNIT | `load_agents_md()` zwraca `None` gdy AGENTS.md nie istnieje | done |
| C-08 | UNIT | `load_system_prompt()` rzuca `RuntimeError` gdy plik nie istnieje (wymagany) | done |
| C-09 | UNIT | `load_system_prompt()` rzuca `RuntimeError` gdy brak uprawnień | done |
| C-10 | UNIT | `load_project_context()` rzuca `RuntimeError` gdy brak uprawnień | done |
| C-11 | UNIT | `load_agents_md()` rzuca `RuntimeError` gdy brak uprawnień | done |

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
| T-01 | UNIT | `read_file()` zwraca treść pliku gdy istnieje | done |
| T-02 | UNIT | `read_file()` zwraca error dict gdy plik nie istnieje | done |
| T-03 | UNIT | `read_file()` zwraca error dict gdy brak uprawnień | done |
| T-04 | UNIT | `write_file()` tworzy plik z podaną treścią | done |
| T-05 | UNIT | `write_file()` zwraca error dict gdy katalog nie istnieje | done |
| T-06 | UNIT | `list_directory()` zwraca listę plików w katalogu | done |
| T-07 | UNIT | `list_directory()` zwraca error dict gdy katalog nie istnieje | done |
| T-08 | UNIT | `delete_file()` usuwa plik i zwraca status ok | done |
| T-09 | UNIT | `delete_file()` zwraca error dict gdy plik nie istnieje | done |
| T-10 | UNIT | `search_in_files()` zwraca listę plików zawierających frazę | done |
| T-11 | UNIT | `search_in_files()` zwraca pustą listę gdy fraza nie znaleziona | done |
| T-12 | UNIT | `read_file()` rozpoznaje unikalną nazwę pliku rekurencyjnie w projekcie (np. `manager.py`) | done |
| T-13 | UNIT | `read_file()` zwraca błąd z kandydatami gdy nazwa pliku jest niejednoznaczna | done |

---

## Graf agenta (`app/agent/graph.py`, `nodes.py`)

| ID | Typ | Opis | Status |
|---|---|---|---|
| G-01 | INT | Graf przyjmuje wiadomość użytkownika i zwraca odpowiedź (mock model) | done |
| G-02 | INT | Graf ładuje context i dodaje go jako system message przed pierwszym wywołaniem modelu | done |
| G-03 | INT | Graf kończy się gdy model nie zwróci `tool_call` (brak dalszych kroków w grafie) | done |
| G-04 | INT | Graf wywołuje `tool_node` gdy model zwróci `tool_call` | done |
| G-05 | INT | Graf wraca do `call_model` po wykonaniu narzędzia | done |
| G-06 | INT | Graf zatrzymuje się po `recursion_limit` krokach | done |
| G-07 | UNIT | Router zwraca `"tool_node"` gdy response zawiera `tool_call` | done |
| G-08 | UNIT | Router zwraca `"done"` gdy response nie zawiera `tool_call` | done |
| G-09 | UNIT | Router zwraca `"compress"` gdy liczba wiadomości > `COMPRESSION_THRESHOLD` | done |

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

## Obsługa błędów (`app/agent/nodes.py`, `graph.py`)

> Routing retry/escalate przez conditional edges grafu (nie LangGraph `Command`).

| ID | Typ | Opis | Status |
|---|---|---|---|
| E-01 | UNIT | `error_handler` inkrementuje `retry_count` i dodaje feedback błędu do `messages` | done |
| E-02 | UNIT | Router kieruje do `error_handler` → `call_model` gdy `retry_count` < 3 | done |
| E-03 | UNIT | Router kieruje do `escalate_to_user` gdy `retry_count` >= 3 | done |
| E-04 | INT | Agent ponawia wywołanie modelu po błędnym output (max 3 razy) | done |
| E-05 | INT | Agent zwraca błąd do użytkownika po 3 nieudanych próbach | done |
| E-06 | INT | Narzędzia zwracają error dict zamiast rzucać wyjątek | done |

---

## Kompresja kontekstu (`app/agent/nodes.py`)

| ID | Typ | Opis | Status |
|---|---|---|---|
| K-01 | UNIT | `compress_history()` zachowuje system message jako pierwszy element | done |
| K-02 | UNIT | `compress_history()` redukuje historię do 2 wiadomości (system + summary) | done |
| K-03 | UNIT | `compress_history()` wynik zawiera tag `[Skompresowany kontekst]` | done |
| K-04 | INT | `compress_node` wywołuje mały model (`gemma3:4b`) nie model roboczy | done |
| K-05 | INT | Graf przekierowuje do `compress_node` gdy `messages > THRESHOLD` | done |
| K-06 | INT | Po kompresji graf kontynuuje odpowiedź użytkownikowi | done |

---

## Backslash Commands (`app/tui/`)

| ID | Typ | Opis | Status |
|---|---|---|---|
| B-01 | UNIT | `parse_command("\new")` zwraca `Command.NEW` | done |
| B-02 | UNIT | `parse_command("\reset")` zwraca `Command.RESET` | done |
| B-03 | UNIT | `parse_command("\compress")` zwraca `Command.COMPRESS` | done |
| B-04 | UNIT | `parse_command("\model llama3.2:3b")` zwraca `Command.MODEL` z arg `"llama3.2:3b"` | done |
| B-05 | UNIT | `parse_command("\spawn")` zwraca `Command.SPAWN` | done |
| B-06 | UNIT | `parse_command("\mcp http://...")` zwraca `Command.MCP` z arg url | done |
| B-07 | UNIT | `parse_command("\skills")` zwraca `Command.SKILLS` | todo |
| B-08 | UNIT | `parse_command("\stop")` zwraca `Command.STOP` | todo |
| B-09 | UNIT | `parse_command("\help")` zwraca `Command.HELP` | todo |
| B-10 | UNIT | `parse_command("zwykły tekst")` zwraca `None` (nie jest komendą) | todo |
| B-11 | UNIT | `parse_command("\model")` bez arg zwraca błąd brakującego argumentu | todo |
| BL-01 | UNIT | Po `parse_command("\new")` chat loop tworzy nową sesję i czyści historię konwersacji | done |
| BL-02 | UNIT | Po `parse_command("\reset")` chat loop czyści historię obecnej sesji, zachowując model i `session_id` | done |
| BL-03 | UNIT | Po `parse_command("\compress")` chat loop uruchamia ścieżkę kompresji kontekstu aktywnej sesji | done |
| BL-04 | UNIT | Po `parse_command("\model llama3.2:3b")` chat loop aktualizuje model aktywnej sesji | done |
| BL-05 | UNIT | Po `parse_command("\spawn")` chat loop uruchamia flow tworzenia sub-agenta | done |
| BL-06 | UNIT | Po `parse_command("\mcp <url>")` chat loop inicjuje podpięcie MCP do aktywnego agenta | done |
| BL-07 | UNIT | Po `parse_command("\skills")` chat loop zwraca listę dostępnych skillów | todo |
| BL-08 | UNIT | Po `parse_command("\stop")` chat loop kończy działanie aktywnej sesji | todo |
| BL-09 | UNIT | Po `parse_command("\help")` chat loop zwraca listę dostępnych komend | todo |
| BL-10 | UNIT | Dla zwykłego tekstu (`parse_command(...) == None`) chat loop wykonuje standardowe wywołanie modelu | todo |
| BL-11 | UNIT | Po błędzie parsera `\model` bez argumentu chat loop zwraca czytelny komunikat i nie zmienia stanu sesji | todo |

---

## Zmiana modelu (`app/session/`)

| ID | Typ | Opis | Status |
|---|---|---|---|
| M-01 | UNIT | `set_model()` aktualizuje model w sesji gdy model jest na liście dostępnych | todo |
| M-02 | UNIT | `set_model()` zwraca błąd gdy model nie jest dostępny | todo |
| M-03 | INT | `available_models()` zwraca listę z Ollamy (mock: `["llama3.2:3b", "qwen2.5:3b"]`) | todo |

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

## At-Mentions (`app/tui/`)

> Użytkownik wpisuje `@` + min. 2 znaki → pojawia się dropdown z pasującymi plikami projektu.
> Wybrany plik jest wstrzykiwany jako osobny system message (`{"role": "system", "content": "[Załącznik: <nazwa>]\n<treść>"}`) przed wiadomością użytkownika.
> Pliki z `.gitignore`, `__pycache__`, `.venv`, `.git` są pomijane.

| ID | Typ | Opis | Status |
|---|---|---|---|
| AT-01 | UNIT | `suggest_files(prefix, project_dir)` zwraca pliki których nazwa zaczyna się od `prefix` | todo |
| AT-02 | UNIT | `suggest_files()` zwraca pustą listę gdy żaden plik nie pasuje do `prefix` | todo |
| AT-03 | UNIT | `suggest_files()` pomija katalogi z listy wykluczeń (`.git`, `__pycache__`, `.venv`) | todo |
| AT-04 | UNIT | `suggest_files()` zwraca maksymalnie `MAX_FILE_SUGGESTIONS` wyników | todo |
| AT-05 | UNIT | `resolve_at_mention(filename, project_dir)` zwraca treść pliku jako system message dict | todo |
| AT-06 | UNIT | `resolve_at_mention()` zwraca `None` gdy plik nie istnieje | todo |
| AT-07 | UNIT | `extract_at_mention(text)` zwraca token `@plik` z tekstu gdy jest obecny | todo |
| AT-08 | UNIT | `extract_at_mention(text)` zwraca `None` gdy brak tokenu `@` z min. 2 znakami | todo |
| AT-09 | INT | Wpisanie `@` + 2 znaki w TUI wywołuje `suggest_files()` i pokazuje dropdown | todo |
| AT-10 | INT | Wybranie pliku z dropdown wstrzykuje go jako system message przed wiadomością użytkownika | todo |

---

## Poprawki i dług techniczny (`FX`)

> Scenariusze wynikające z code review całości — naprawiają bugi, dead code i rozbieżności między PRD a implementacją.

| ID | Typ | Opis | Status |
|---|---|---|---|
| FX-01 | UNIT | `AGENT_TOOLS` eksponuje wszystkie 5 narzędzi: `read_file`, `list_directory`, `write_file`, `delete_file`, `search_in_files` | done |
| FX-02 | UNIT | `AgentState.messages` jest typowane `Annotated[list, add_messages]` — reducer LangGraph | done |
| FX-03 | UNIT | `Session` nie zawiera pola `history` (usunięte jako dead code) | done |
| FX-04 | UNIT | `call_model` inkrementuje `recursion_count` w zwracanym stanie | done |
| FX-05 | INT | `load_context_node` wstrzykuje system message tylko gdy `messages` są puste — nie przy każdym `graph.invoke()` | done |
| FX-06 | UNIT | `AVAILABLE_MODELS` zawiera modele ze wsparciem tools API (`llama3.2:3b`, `qwen2.5:3b`) zamiast modeli Gemma | done |
| FX-07 | UNIT | `call_model` nie tworzy nowego `ChatOllama` przy każdym wywołaniu — model konfigurowany raz | done |
| FX-08 | UNIT | `search_in_files` pomija pliki większe niż `MAX_SEARCH_FILE_SIZE` | done |
| FX-09 | UNIT | `search_in_files` przeszukuje rekurencyjnie podkatalogi (`rglob` zamiast `iterdir`) | done |
| FX-10 | UNIT | `AgentState` odrzuca nieznane pola przy inicjalizacji (`extra="forbid"`) — test walidacji | done |
| FX-11 | UNIT | CLI akumuluje historię konwersacji między turn'ami — agent pamięta poprzednie wiadomości | done |

---

## Scenariusze E2E (`tests/e2e/`)

> Implementowane po ukończeniu sekcji G (Graf agenta). Testują pełny przepływ z perspektywy użytkownika. Ollama mockowana na poziomie HTTP.

| ID | Typ | Opis | Status |
|---|---|---|---|
| BIZ-01 | E2E | Użytkownik wysyła pytanie → agent odpowiada używając lokalnego modelu (mock Ollama) | todo |
| BIZ-02 | E2E | Użytkownik wysyła pytanie → agent ładuje PROJECT.md i odpowiada z jego kontekstem | todo |
| BIZ-03 | E2E | Użytkownik używa `\reset` → nowa rozmowa zaczyna się bez pamięci poprzedniej | todo |
| BIZ-04 | E2E | Użytkownik pyta o plik → agent wywołuje `read_file` i zwraca treść | todo |
| BIZ-05 | E2E | Ollama zwraca błąd → agent ponawia 3 razy → informuje użytkownika o niepowodzeniu | todo |
| BIZ-06 | E2E | Użytkownik wysyła wiele wiadomości → po przekroczeniu progu historia zostaje skompresowana | todo |
| BIZ-07 | E2E | Użytkownik używa `\spawn` → powstaje sub-agent → `\list` pokazuje dwa aktywne agenty | todo |

---

## Podsumowanie

| Moduł | UNIT | INT | E2E | Łącznie | Done | Cancelled |
|---|---|---|---|---|---|---|
| Session | 4 | 0 | 0 | 4 | 4 | 0 |
| Context Loader | 13 | 0 | 0 | 13 | 13 | 0 |
| AgentState | 4 | 0 | 0 | 4 | 4 | 0 |
| Narzędzia plików | 13 | 0 | 0 | 13 | 13 | 0 |
| Graf agenta | 3 | 6 | 0 | 9 | 9 | 0 |
| Kolejka | 3 | 1 | 0 | 4 | 0 | 4 |
| Obsługa błędów | 3 | 3 | 0 | 6 | 6 | 0 |
| Kompresja | 3 | 3 | 0 | 6 | 6 | 0 |
| Backslash Commands | 22 | 0 | 0 | 22 | 12 | 0 |
| Zmiana modelu | 2 | 1 | 0 | 3 | 0 | 0 |
| Skille | 5 | 1 | 0 | 6 | 0 | 0 |
| MCP | 2 | 2 | 0 | 4 | 0 | 0 |
| Wieloagentowość | 3 | 1 | 0 | 4 | 0 | 0 |
| Potwierdzanie akcji | 2 | 3 | 0 | 5 | 0 | 0 |
| At-Mentions | 8 | 2 | 0 | 10 | 0 | 0 |
| Poprawki (FX) | 10 | 1 | 0 | 11 | 11 | 0 |
| Scenariusze E2E | 0 | 0 | 7 | 7 | 0 | 0 |
| **Łącznie** | **100** | **24** | **7** | **131** | **78** | **4** |
