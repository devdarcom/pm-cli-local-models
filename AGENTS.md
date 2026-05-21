# AGENTS.md 

## Zasady Clean Code dla projektu Multimodel PM

Ten plik definiuje standardy pisania kodu w projekcie. Obowiązuje zarówno
developerów jak i agentów AI generujących kod. Każda zasada zawiera
przykład złego i poprawnego kodu w Pythonie.

---

### 1. Znaczące nazwy zmiennych i funkcji

Nazwy powinny wyjaśniać intencję — nie wymagać komentarza.

```python
# ŹLE
def proc(d, n):
    r = []
    for i in d:
        if i > n:
            r.append(i)
    return r
```

```python
# DOBRZE
def filter_messages_above_token_limit(messages: list[dict], limit: int) -> list[dict]:
    return [msg for msg in messages if msg["tokens"] > limit]
```

---

### 2. Funkcje robią jedną rzecz (Single Responsibility)

Funkcja powinna mieć jeden powód do zmiany. Jeśli nazwa zawiera "i", "oraz",
"a także" — podziel ją.

```python
# ŹLE
def load_and_validate_and_send_message(path: str, model: str):
    with open(path) as f:
        content = f.read()
    if len(content) > 4096:
        content = content[:4096]
    response = ollama.chat(model=model, messages=[{"role": "user", "content": content}])
    print(response["message"]["content"])
```

```python
# DOBRZE
def load_file(path: str) -> str:
    with open(path) as f:
        return f.read()

def truncate_to_token_limit(text: str, limit: int = 4096) -> str:
    return text[:limit]

def send_to_model(content: str, model: str) -> str:
    response = ollama.chat(model=model, messages=[{"role": "user", "content": content}])
    return response["message"]["content"]
```

---

### 3. Unikaj magicznych liczb i stringów

Stałe powinny mieć nazwę opisującą ich znaczenie.

```python
# ŹLE
def should_compress(messages: list) -> bool:
    return len(messages) > 25

def get_model() -> str:
    return "gemma3:4b"
```

```python
# DOBRZE
COMPRESSION_THRESHOLD = 25
DEFAULT_COMPRESSION_MODEL = "gemma3:4b"

def should_compress(messages: list) -> bool:
    return len(messages) > COMPRESSION_THRESHOLD

def get_compression_model() -> str:
    return DEFAULT_COMPRESSION_MODEL
```

---

### 4. Obsługa błędów — nie połykaj wyjątków

Złap konkretny wyjątek i zaloguj lub propaguj z kontekstem. Nigdy nie używaj
gołego `except:` bez obsługi.

```python
# ŹLE
def read_project_context(path: str) -> str:
    try:
        with open(path) as f:
            return f.read()
    except:
        return ""
```

```python
# DOBRZE
def read_project_context(path: str) -> str | None:
    try:
        with open(path) as f:
            return f.read()
    except FileNotFoundError:
        return None
    except PermissionError as e:
        raise RuntimeError(f"Brak uprawnień do odczytu {path}") from e
```

#### 4a. Plik opcjonalny vs wymagany

Różne pliki mają różny kontrakt błędu. Stosuj konsekwentnie jeden z dwóch wzorców:

**Plik opcjonalny** — brak pliku jest normalnym stanem (np. `PROJECT.md`, `AGENTS.md`):
```python
# FileNotFoundError → return None (brak pliku jest OK)
# PermissionError   → raise RuntimeError (brak uprawnień jest zawsze błędem)
# UnicodeDecodeError → raise RuntimeError (plik jest uszkodzony)
def load_optional_file(path: Path) -> Optional[str]:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return None
    except PermissionError as e:
        raise RuntimeError(f"Brak uprawnień do odczytu {path}") from e
    except UnicodeDecodeError as e:
        raise RuntimeError(f"Nie można odczytać {path} jako UTF-8") from e
```

**Plik wymagany** — brak pliku to błąd konfiguracji (np. `system_prompt.md`):
```python
# FileNotFoundError → raise RuntimeError (agent nie może działać bez tego pliku)
# PermissionError   → raise RuntimeError
# UnicodeDecodeError → raise RuntimeError
def load_required_file(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as e:
        raise RuntimeError(f"Wymagany plik nie istnieje: {path}") from e
    except PermissionError as e:
        raise RuntimeError(f"Brak uprawnień do odczytu {path}") from e
    except UnicodeDecodeError as e:
        raise RuntimeError(f"Nie można odczytać {path} jako UTF-8") from e
```

Zasada: **zawsze chainuj wyjątki przez `from e`** — zachowuje oryginalny traceback.

---

### 5. Typowanie (Type Hints)

Każda funkcja publiczna powinna mieć adnotacje typów. Ułatwia to czytanie
kodu i wyłapywanie błędów statyczną analizą.

```python
# ŹLE
def build_prompt(system, history, user_input):
    messages = [{"role": "system", "content": system}]
    messages.extend(history)
    messages.append({"role": "user", "content": user_input})
    return messages
```

```python
# DOBRZE
def build_prompt(
    system_prompt: str,
    history: list[dict[str, str]],
    user_input: str,
) -> list[dict[str, str]]:
    messages = [{"role": "system", "content": system_prompt}]
    messages.extend(history)
    messages.append({"role": "user", "content": user_input})
    return messages
```

---

### 6. Nie powtarzaj się (DRY — Don't Repeat Yourself)

Jeśli ten sam fragment kodu pojawia się w dwóch miejscach, wydziel go
do funkcji pomocniczej.

```python
# ŹLE
def handle_file_read_tool(path: str):
    if not os.path.exists(path):
        return {"error": f"Plik {path} nie istnieje"}
    with open(path) as f:
        return {"content": f.read()}

def handle_file_append_tool(path: str, content: str):
    if not os.path.exists(path):
        return {"error": f"Plik {path} nie istnieje"}
    with open(path, "a") as f:
        f.write(content)
    return {"status": "ok"}
```

```python
# DOBRZE
def assert_file_exists(path: str) -> dict | None:
    if not os.path.exists(path):
        return {"error": f"Plik {path} nie istnieje"}
    return None

def handle_file_read_tool(path: str) -> dict:
    if error := assert_file_exists(path):
        return error
    with open(path) as f:
        return {"content": f.read()}

def handle_file_append_tool(path: str, content: str) -> dict:
    if error := assert_file_exists(path):
        return error
    with open(path, "a") as f:
        f.write(content)
    return {"status": "ok"}
```

---

### 7. Małe funkcje i krótkie klasy

Funkcja dłuższa niż ~20 linii to sygnał do refactoringu. Klasa z więcej niż
~5 metodami publicznymi prawdopodobnie robi za dużo.

```python
# ŹLE
def run_agent_step(state):
    messages = state["messages"]
    model = state["model"]
    system_prompt = open("system.md").read()
    project_context = open("PROJECT.md").read() if os.path.exists("PROJECT.md") else ""
    full_messages = [
        {"role": "system", "content": system_prompt + "\n\n" + project_context},
        *messages,
    ]
    response = ollama.chat(model=model, messages=full_messages)
    content = response["message"]["content"]
    tool_calls = extract_tool_calls(content)
    if tool_calls:
        results = [execute_tool(tc) for tc in tool_calls]
        messages.append({"role": "assistant", "content": content})
        messages.append({"role": "tool", "content": str(results)})
        return {**state, "messages": messages}
    return {**state, "messages": messages, "done": True}
```

```python
# DOBRZE
def build_system_messages(system_prompt: str, project_context: str | None) -> list[dict]:
    content = system_prompt
    if project_context:
        content += f"\n\n{project_context}"
    return [{"role": "system", "content": content}]

def call_model(messages: list[dict], model: str) -> str:
    response = ollama.chat(model=model, messages=messages)
    return response["message"]["content"]

def run_agent_step(state: dict) -> dict:
    system_msgs = build_system_messages(
        load_system_prompt(),
        load_project_context(),
    )
    full_messages = system_msgs + state["messages"]
    content = call_model(full_messages, state["model"])
    return handle_model_response(state, content)
```

---

### 8. Komentarze wyjaśniają "dlaczego", nie "co"

Kod powinien być czytelny sam w sobie. Komentarz opisuje intencję lub
nieoczywiste ograniczenie, nie powtarza tego co kod już mówi.

```python
# ŹLE
# Iterujemy po wiadomościach
for msg in messages:
    # Sprawdzamy rolę
    if msg["role"] == "tool":
        # Dodajemy do listy
        tool_messages.append(msg)
```

```python
# DOBRZE
for msg in messages:
    if msg["role"] == "tool":
        # Ollama wymaga by tool messages były zgrupowane bezpośrednio
        # po assistant message — filtrujemy je osobno przed złożeniem promptu
        tool_messages.append(msg)
```

---

### 9. Używaj dataclass lub TypedDict zamiast surowych słowników

Struktury danych powinny mieć zdefiniowany kształt — ułatwia to refactoring
i czytelność.

```python
# ŹLE
def create_session(model, session_id, history):
    return {
        "model": model,
        "session_id": session_id,
        "history": history,
        "compressed": False,
    }
```

```python
# DOBRZE
from dataclasses import dataclass, field

@dataclass
class Session:
    model: str
    session_id: str
    history: list[dict[str, str]] = field(default_factory=list)
    compressed: bool = False

def create_session(model: str, session_id: str) -> Session:
    return Session(model=model, session_id=session_id)
```

---

### 10. Testy dla logiki krytycznej

Każda funkcja wpływająca na stan agenta lub przetwarzanie kontekstu powinna
mieć co najmniej jeden test jednostkowy.

```python
# ŹLE — brak testów dla funkcji kompresji kontekstu
def compress_history(messages: list[dict], summary: str) -> list[dict]:
    system = messages[0]
    return [system, {"role": "assistant", "content": f"[Skompresowany kontekst]: {summary}"}]
```

```python
# DOBRZE
def compress_history(messages: list[dict], summary: str) -> list[dict]:
    system = messages[0]
    return [system, {"role": "assistant", "content": f"[Skompresowany kontekst]: {summary}"}]


# tests/test_compress.py
def test_compress_history_preserves_system_message():
    messages = [
        {"role": "system", "content": "Jesteś agentem."},
        {"role": "user", "content": "Napisz kod."},
        {"role": "assistant", "content": "Oto kod..."},
    ]
    result = compress_history(messages, summary="Użytkownik prosił o kod.")
    assert result[0]["role"] == "system"
    assert result[0]["content"] == "Jesteś agentem."
    assert len(result) == 2
    assert "Skompresowany kontekst" in result[1]["content"]
```
## Multimodel PM — Architektura: Best Practices i Rekomendacje

---

## 1. Kolejka requestów do Ollamy — przemyśl, czy jej potrzebujesz

### Problem, który chcesz rozwiązać

W PRD zakładasz własną warstwę `queue/` jako "jeden punkt dostępu, FIFO" do Ollamy. Intuicja jest słuszna, ale Ollama od wersji 0.2 robi to natywnie — możesz zduplikować funkcjonalność, która już istnieje.

### Jak Ollama naprawdę działa pod spodem

Ollama to serwer Go (`ollama serve` na porcie 11434), który wrappuje `llama.cpp`. Wewnętrznie utrzymuje **worker pool** z KV-cache slotami na GPU. Każdy incoming request trafia do kolejki FIFO i czeka na wolny slot. Domyślnie Ollama uruchamia się z `OLLAMA_NUM_PARALLEL=1` — jeden request na raz, reszta w kolejce. To zachowanie **konserwatywne celowo**, żeby nie crashować na consumer hardware przy małej VRAM.

```
Request A ─┐
Request B ─┤──► [FIFO Queue] ──► [KV-cache slot 1] ──► GPU
Request C ─┘                 └──► [KV-cache slot 2] ──► GPU (jeśli NUM_PARALLEL > 1)
```

### Konfiguracja środowiskowa zamiast własnej kolejki

Zamiast pisać własny Python queue manager, skonfiguruj Ollamę przez zmienne środowiskowe:

```bash
# .env lub systemd service
OLLAMA_NUM_PARALLEL=2          # ile równoległych inferencji (zależy od VRAM)
OLLAMA_MAX_LOADED_MODELS=3     # ile modeli trzymać załadowanych jednocześnie
OLLAMA_MAX_QUEUE=512           # max requestów w kolejce przed odrzuceniem (domyślnie 512)
OLLAMA_KEEP_ALIVE=10m          # jak długo trzymać model w VRAM po ostatnim użyciu
```

**Uwaga na pamięć:** `NUM_PARALLEL=2` przy kontekście 4K = efektywnie 8K VRAM zużycia na kontekst. Dla gemma3:4b na 8GB VRAM — bezpiecznie zostań przy `NUM_PARALLEL=1` lub `2`.

### Kiedy własna kolejka ma sens

Własna warstwa `queue/` w Pythonie jest uzasadniona tylko gdy potrzebujesz:

- **Priorytetyzacji** — np. requesty od użytkownika mają wyższy priorytet niż background compress_node
- **Backpressure na poziomie aplikacji** — chcesz odmówić spawnowania kolejnego agenta jeśli jest już N w kolejce
- **Observability** — metryki ile requestów czeka, średni czas oczekiwania

Jeśli żadne z powyższych nie jest wymagane na start — usuń `queue/` z pierwszej wersji i wróć do niego w iteracji. Zaoszczędzisz tygodnie implementacji.

### Rekomendacja dla projektu

Zacznij od konfiguracji Ollamy przez env vars. Jeśli przy wieloagentowości poczujesz potrzebę priorytetyzacji, dodaj prostą kolejkę `asyncio.PriorityQueue` zamiast własnego modułu. Obsłuż `HTTP 503` od Ollamy (kolejka pełna) jako sygnał do backpressure w aplikacji.

---

## 2. AgentState — Pydantic zamiast TypedDict

### Dlaczego TypedDict jest za słaby

`TypedDict` w LangGraph to częsty błąd początkujący. Nie waliduje typów w runtime, nie odrzuca nieznanych pól i nie daje sensownych błędów gdy stan się "zepsuje". Typowy scenariusz: zostawiasz debugowe pole `_tmp_test` w stanie podczas developmentu, zapominasz je usunąć, i kolejny node dostaje dane, których się nie spodziewał — bez żadnego błędu.

### Pydantic z `extra="forbid"`

```python
from pydantic import BaseModel, ConfigDict
from typing import Annotated
from langgraph.graph.message import add_messages
import operator

class AgentState(BaseModel):
    model_config = ConfigDict(extra="forbid")  # odrzuca nieznane pola przy wejściu

    # Historia wiadomości — wbudowany reducer do deduplikacji i mergowania
    messages: Annotated[list, add_messages]

    # Metadane sesji
    session_id: str
    model_name: str
    recursion_count: int = 0

    # Stan retry — tagowany, nie anonimowy
    retry_count: int = 0
    last_error: str | None = None

    # Kompresja — osobne pole, nie mixowane z messages
    summary: str | None = None  # wynik compress_node

    # Multi-agent
    spawned_agents: Annotated[list[str], operator.add] = []
```

### Reducery — krytyczne przy równoległych węzłach

Gdy dwa węzły wykonują się równolegle i oba modyfikują to samo pole, LangGraph domyślnie bierze **ostatnią wartość** — co w praktyce oznacza race condition. Rozwiązanie to reducer function:

```python
# Bez reducera — ostatni wygrywa (źle przy parallel execution)
errors: list[str]

# Z reducerem — oba wyniki są łączone
errors: Annotated[list[str], operator.add]
```

Dla `messages` używaj wbudowanego `add_messages` — robi automatyczną deduplikację po `id` wiadomości i zachowuje najnowszą wersję. Dla custom list (jak `spawned_agents`) wystarczy `operator.add`.

### Walidacja na granicy węzłów

Dodaj Pydantic validators dla pól krytycznych:

```python
from pydantic import field_validator

@field_validator("recursion_count")
@classmethod
def check_recursion_limit(cls, v):
    if v > 25:
        raise ValueError(f"recursion_count {v} przekroczył limit 25")
    return v
```

To "fail fast" zamiast cichego błędu głęboko w grafie.

---

## 3. Kompresja kontekstu — gdzie, kiedy i jak

### Dlaczego naiwna kompresja szkodzi

Najczęstszy błąd: kompresja uruchamia się "na końcu" lub "co N wiadomości", obcinając kontekst równomiernie. Problem — agent jest w połowie zadania, ma w pamięci aktualny stan pliku, wynik ostatniego narzędzia i plan następnych kroków. Wrzucenie tego wszystkiego do modelu kompresji niszczy "working memory" i agent nie może kontynuować.

### Strategia: zachowaj "hot context"

Podział kontekstu na dwie strefy:

```
[  COLD CONTEXT  ][      HOT CONTEXT      ]
[-- summarized --][-- verbatim, nietykalny --]
                   ^
                   ostatnie K wiadomości (np. 10-15% okna)
```

Hot context to co najmniej: ostatnia wiadomość od użytkownika, ostatni tool call i jego wynik, aktualny plan agenta (jeśli jest). Nigdy nie kompresuj hot context — nawet jeśli okno jest przepełnione. Zamiast tego najpierw skompresuj cold context.

### Implementacja w LangGraph

```python
# nodes.py

COMPRESS_THRESHOLD = 0.75  # kompresuj gdy jesteś na 75% okna kontekstu
HOT_CONTEXT_MESSAGES = 6   # ostatnie N wiadomości są zawsze verbatim

def should_compress(state: AgentState) -> bool:
    """Conditional edge — wyzwalacz kompresji."""
    token_count = estimate_tokens(state.messages)
    model_ctx_window = get_model_context_window(state.model_name)
    return token_count > model_ctx_window * COMPRESS_THRESHOLD

async def compress_node(state: AgentState) -> dict:
    """
    Kompresuje cold context. Hot context (ostatnie N wiadomości) pozostaje nienaruszony.
    Używa małego, szybkiego modelu (gemma3:4b) — nie blokuje głównego agenta.
    """
    cold_messages = state.messages[:-HOT_CONTEXT_MESSAGES]
    hot_messages = state.messages[-HOT_CONTEXT_MESSAGES:]

    if not cold_messages:
        return {}  # nic do kompresji

    summary_prompt = f"""
    Poprzednie podsumowanie (jeśli istnieje): {state.summary or 'brak'}

    Wiadomości do skompresowania:
    {format_messages(cold_messages)}

    Zadanie: Stwórz zwięzłe podsumowanie zachowujące:
    - Decyzje i kroki wykonane przez agenta
    - Stan plików/katalogów po ostatnich operacjach
    - Nierozwiązane problemy i błędy
    - Aktualny cel zadania
    """

    # Batchowo (nie streaming) — mniejsze zużycie RAM
    new_summary = await call_model_batch(
        model="gemma3:4b",
        prompt=summary_prompt
    )

    # Zastąp cold messages jedną wiadomością-podsumowaniem
    summary_message = SystemMessage(content=f"[PODSUMOWANIE KONTEKSTU]\n{new_summary}")

    return {
        "messages": [summary_message] + hot_messages,
        "summary": new_summary
    }
```

### Kompresja tool outputs — często pomijana

Odczyt dużego pliku (np. 500-liniowy plik kodu) wpycha ogromną ilość tokenów do kontekstu. Zamiast tego kompresuj output narzędzi **zanim** trafi do stanu:

```python
async def read_file_tool(path: str, state: AgentState) -> str:
    content = await read_file(path)

    # Jeśli plik jest duży, daj agentowi podsumowanie + możliwość zapytania o fragment
    if estimate_tokens(content) > 2000:
        summary = await summarize_file(content, model="gemma3:4b")
        return f"[PLIK: {path} — {len(content)} znaków]\n{summary}\n\nUżyj read_file_chunk(path, start, end) aby odczytać konkretny fragment."

    return content
```

To wzorzec stosowany w Claude Code i Devin — nigdy nie wrzucaj całego pliku do kontekstu jeśli agent i tak nie przeczyta go w całości.

### Triggerowanie kompresji

W grafie LangGraph dodaj conditional edge po `call_model`:

```python
graph.add_conditional_edges(
    "call_model",
    lambda state: "compress" if should_compress(state) else "tools_or_output",
    {
        "compress": "compress_node",
        "tools_or_output": "tool_node"
    }
)

# Po kompresji wróć do call_model — nie do narzędzi
graph.add_edge("compress_node", "call_model")
```

---

## 4. Multi-agent: Supervisor pattern przez tool-calling

### Trzy wzorce i kiedy je stosować

**Supervisor (zalecany dla tego projektu)**
Jeden centralny agent-supervisor deleguje zadania sub-agentom przez tool calle. Supervisor wie o wszystkich sub-agentach, routuje do nich i agreguje wyniki.

```
User ──► Supervisor ──► [tool: spawn_agent("file_analyzer")]
                    └──► [tool: spawn_agent("code_writer")]
                    └──► [tool: aggregate_results]
```

**Swarm (elastyczniejszy, trudniejszy w debug)**
Agenci przekazują sobie kontrolę bezpośrednio przez obiekty `Command`. Brak centralnego koordynatora. Dobry gdy zadania są heterogeniczne i trudno przewidzieć routing z góry.

**Hierarchical (dla dużej skali)**
Supervisor supervisorów. Zbędne na tym etapie projektu.

### Dlaczego Supervisor przez tool-calling (nie subgraph)

LangChain oficjalnie rekomenduje **tool-calling approach** zamiast dedykowanej biblioteki `langgraph-supervisor`. Powód: tool-calling daje pełną kontrolę nad context engineeringiem i lepszy tracing — każda decyzja supervisora jest widoczna jako tool call w logach.

```python
# graph.py — supervisor wie o sub-agentach przez tools

@tool
async def spawn_file_agent(task: str, working_dir: str) -> str:
    """Spawnuj agenta do operacji na plikach. task: opis zadania."""
    sub_agent = FileAgent(task=task, working_dir=working_dir)
    result = await sub_agent.run()
    return result.summary  # supervisor dostaje tylko podsumowanie, nie cały kontekst

@tool
async def spawn_search_agent(query: str) -> str:
    """Spawnuj agenta do przeszukiwania kodu/plików."""
    ...
```

### Handoff przez `Command` — dla `\spawn`

Gdy użytkownik wywołuje `\spawn`, nie twórz nowego wątku aplikacji. Użyj `Command` object z LangGraph:

```python
from langgraph.types import Command

def spawn_subagent_node(state: AgentState) -> Command:
    """Przekazuje kontrolę do sub-agenta, zachowując parent state."""
    return Command(
        goto="sub_agent_node",
        update={
            "spawned_agents": [f"agent_{uuid4()}"],
            "parent_task": state.current_task
        },
        graph=Command.PARENT  # wróć do parent grafu po zakończeniu
    )
```

### Izolacja kontekstu sub-agentów

Każdy sub-agent powinien dostać **własny, izolowany kontekst** — nie kopię całego stanu supervisora. Przekazuj tylko to, co potrzebne:

```python
class SubAgentInput(BaseModel):
    task: str           # konkretne zadanie
    working_dir: str    # ograniczony zakres plików
    tools: list[str]    # tylko potrzebne narzędzia (principle of least privilege)
    # NIE przekazuj: pełna historia wiadomości, credentials, inne sesje
```

---

## 5. Obsługa błędów — tagowanie stanu i dedykowana ścieżka

### Problem z obecnym podejściem w PRD

PRD zakłada "automatyczny retry max 3 próby z feedbackiem błędu". To słuszne, ale brak tagowania stanu sprawia, że:
- Nie wiesz w którym retry jesteś podczas debugowania
- Nie masz dedykowanej ścieżki dla "exhausted retries" — co wtedy?
- Błąd w sub-agencie może cicho "wyciec" do parent agenta

### Tagowanie stanu — minimum

```python
class AgentState(BaseModel):
    # ...
    retry_count: int = 0
    last_error: str | None = None
    error_node: str | None = None   # który węzeł rzucił błąd
    error_type: str | None = None   # "tool_error" | "model_error" | "validation_error"
```

### Ścieżki w grafie dla błędów

```
[call_model]
     │
     ├── success ──────────────────────► [tool_node lub output]
     │
     └── model_error ──► [error_handler]
                               │
                               ├── retry_count < 3 ──► [call_model]  (z last_error w kontekście)
                               │
                               └── retry_count >= 3 ──► [escalate_to_user]
                                                               │
                                                               └── "Agent nie mógł wykonać zadania.
                                                                    Ostatni błąd: {last_error}"
```

```python
def error_handler_node(state: AgentState) -> dict:
    if state.retry_count >= 3:
        # Ścieżka "exhausted" — nie rzucaj exception, poinformuj użytkownika
        return {
            "messages": [AIMessage(content=f"⚠️ Nie udało się wykonać zadania po 3 próbach.\nOstatni błąd: {state.last_error}")],
            "retry_count": 0,
            "last_error": None
        }

    # Retry — dołącz błąd jako kontekst do następnego wywołania
    error_feedback = HumanMessage(
        content=f"[FEEDBACK BŁĘDU — próba {state.retry_count + 1}/3]\n{state.last_error}\n\nSpróbuj innego podejścia."
    )
    return {
        "messages": [error_feedback],
        "retry_count": state.retry_count + 1
    }
```

### Błędy w tool_node — nie propaguj wyjątków

Narzędzia powinny zwracać **opisowe błędy jako string**, nie rzucać wyjątków. Wyjątek nie obsłużony przez LangGraph może crashować cały graph run.

```python
# Źle
async def delete_file(path: str) -> str:
    os.remove(path)  # rzuci FileNotFoundError

# Dobrze
async def delete_file(path: str) -> str:
    try:
        os.remove(path)
        return f"✓ Usunięto plik: {path}"
    except FileNotFoundError:
        return f"BŁĄD: Plik nie istnieje: {path}"
    except PermissionError:
        return f"BŁĄD: Brak uprawnień do usunięcia: {path}"
```

### Cascading failures przy multi-agencie

Gdy sub-agent zawiedzie, supervisor nie powinien automatycznie powtarzać całego zadania. Wzorzec:

```python
@tool
async def spawn_file_agent(task: str) -> str:
    try:
        result = await run_subagent(task)
        return result
    except AgentExhaustedError as e:
        # Supervisor dostaje strukturyzowany błąd, może podjąć inną decyzję
        return f"SUB_AGENT_FAILED: {str(e)}\nMożliwe alternatywy: uprość zadanie lub poproś użytkownika o interwencję."
```

---

## Podsumowanie decyzji architektonicznych

| Obszar | Decyzja | Uzasadnienie |
|---|---|---|
| Kolejka Ollamy | Usuń `queue/`, skonfiguruj przez env vars | Ollama ma wbudowaną FIFO kolejkę; własna warstwa to duplikacja |
| AgentState | Pydantic `extra="forbid"` + reducery | Walidacja w runtime, brak cichych błędów przy parallel execution |
| Kompresja | Hot context verbatim + kompresja tool outputs | Nie niszczyć working memory; redukować tokeny przed wejściem do stanu |
| Multi-agent | Supervisor przez tool-calling + `Command` dla spawn | Lepszy tracing, rekomendowane przez LangChain od 2025 |
| Błędy | Tagowanie `retry_count`/`last_error`/`error_type` + dedykowana ścieżka exhausted | Brak cichych awarii, user zawsze dostaje informację |

---

*Dokument wygenerowany: maj 2026. Bazuje na aktualnym stanie LangGraph (pre-v1.0), Ollama v0.6.x i rekomendacjach LangChain.*