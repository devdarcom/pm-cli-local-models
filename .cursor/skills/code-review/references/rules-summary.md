# AGENTS.md — Skrócona lista zasad do code review

Pełne przykłady (dobry/zły kod) znajdują się w `AGENTS.md` w katalogu projektu.
Ten plik służy jako szybki checklist podczas przeglądu PR.

## Zasada 1 — Znaczące nazwy
❌ Sygnały: nazwy jednoiiterowe (`d`, `r`, `i`), ogólne (`data`, `result`, `proc`, `tmp`)
✅ Wymagane: nazwa opisuje intencję bez potrzeby komentarza

## Zasada 2 — Single Responsibility
❌ Sygnały: funkcja zawiera słowa "i", "oraz" w opisie swojego działania; robi fetch + validate + save
✅ Wymagane: jedna funkcja = jeden powód do zmiany

## Zasada 3 — Brak magicznych liczb/stringów
❌ Sygnały: liczby (`25`, `3`, `4096`) lub stringi (`"gemma3:4b"`) wpisane bezpośrednio w logice
✅ Wymagane: stała z nazwą opisującą znaczenie (`COMPRESSION_THRESHOLD = 25`)

## Zasada 4 — Obsługa błędów
❌ Sygnały: gołe `except:` lub `except Exception:` bez logowania/propagacji; `return ""` na błędzie bez info
✅ Wymagane: konkretny wyjątek, kontekst błędu, propagacja z `from e`

## Zasada 5 — Type hints
❌ Sygnały: brak adnotacji na parametrach lub typie zwracanym funkcji publicznej
✅ Wymagane: `def foo(x: str, y: int) -> list[dict]:`

## Zasada 6 — DRY
❌ Sygnały: ten sam blok kodu (nawet lekko zmodyfikowany) w 2+ miejscach
✅ Wymagane: wspólna logika wydzielona do funkcji pomocniczej

## Zasada 7 — Małe funkcje
❌ Sygnały: funkcja > ~20 linii; klasa > ~5 metod publicznych
✅ Wymagane: każda funkcja mieści się na jednym ekranie

## Zasada 8 — Komentarze wyjaśniają "dlaczego"
❌ Sygnały: `# Iterujemy po wiadomościach`, `# Sprawdzamy rolę`, `# Zwracamy wynik`
✅ Wymagane: komentarz opisuje nieoczywiste ograniczenie lub intencję, nie narrację kodu

## Zasada 9 — Dataclass/TypedDict zamiast surowych dict
❌ Sygnały: `return {"model": model, "session_id": id, "history": []}` jako struktura danych
✅ Wymagane: `@dataclass class Session` gdy dane mają stały kształt

## Zasada 10 — Testy dla logiki krytycznej
❌ Sygnały: funkcja wpływająca na stan agenta lub przetwarzanie kontekstu bez testu
✅ Wymagane: co najmniej jeden test jednostkowy dla każdej takiej funkcji
