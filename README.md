# Multimodel PM

Lokalny agent AI działający przez Ollama. Czyta pliki projektu, wykonuje narzędzia i odpowiada w pętli ReAct.

## Wymagania

- Python 3.9+
- [Ollama](https://ollama.com) zainstalowana i uruchomiona lokalnie

## Setup

```bash
# 1. Sklonuj repo i wejdź do katalogu
cd multimodel-pm

# 2. Utwórz i aktywuj virtualenv
python3 -m venv .venv
source .venv/bin/activate

# 3. Zainstaluj zależności
pip install -r requirements.txt

# 4. Pobierz model (jeśli jeszcze nie masz)
ollama pull gemma3:4b
```

## Uruchomienie

```bash
# Upewnij się że Ollama działa (jeśli nie — uruchom w osobnym terminalu)
ollama serve

# Uruchom agenta
python main.py
```

Agent uruchamia się w terminalu i czeka na wiadomości. Wpisz `exit` żeby zakończyć.

```
Agent gotowy (model: gemma3:4b). Wpisz 'exit' aby zakończyć.

Ty: przeczytaj plik main.py
Agent: [odpowiedź agenta]

Ty: exit
Do widzenia.
```

> Jeśli Ollama jest już uruchomiona (błąd `address already in use`), pomiń `ollama serve` — serwer działa w tle.

## Testy

```bash
.venv/bin/pytest tests/ -v
```

## Struktura projektu

```
app/
  agent/
    graph.py      # graf LangGraph (ReAct loop)
    nodes.py      # węzły grafu i ładowanie kontekstu
    state.py      # schemat stanu agenta (Pydantic)
    tools.py      # narzędzia: read_file, list_directory
  session/
    manager.py    # tworzenie i resetowanie sesji
tests/
  unit/           # testy jednostkowe
  integration/    # testy integracyjne grafu
main.py           # entry point CLI
system_prompt.md  # systemowy prompt agenta
```
