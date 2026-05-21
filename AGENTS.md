# AGENTS.md — Zasady Clean Code dla projektu Multimodel PM

Ten plik definiuje standardy pisania kodu w projekcie. Obowiązuje zarówno
developerów jak i agentów AI generujących kod. Każda zasada zawiera
przykład złego i poprawnego kodu w Pythonie.

---

## 1. Znaczące nazwy zmiennych i funkcji

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

## 2. Funkcje robią jedną rzecz (Single Responsibility)

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

## 3. Unikaj magicznych liczb i stringów

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

## 4. Obsługa błędów — nie połykaj wyjątków

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

---

## 5. Typowanie (Type Hints)

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

## 6. Nie powtarzaj się (DRY — Don't Repeat Yourself)

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

## 7. Małe funkcje i krótkie klasy

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

## 8. Komentarze wyjaśniają "dlaczego", nie "co"

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

## 9. Używaj dataclass lub TypedDict zamiast surowych słowników

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

## 10. Testy dla logiki krytycznej

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
