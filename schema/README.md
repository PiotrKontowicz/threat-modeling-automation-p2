# Schemat reprezentacji łańcucha dostaw oprogramowania

Katalog `schema/` zawiera specyfikację ustrukturyzowanej reprezentacji łańcucha dostaw oprogramowania wykorzystywanej jako dane wejściowe w procesie półautomatycznego modelowania zagrożeń.

Celem reprezentacji jest dostarczenie modelowi LLM jednoznacznego i możliwego do automatycznej walidacji opisu analizowanego systemu.

## Założenia

Reprezentacja powinna:

* opisywać najważniejsze elementy łańcucha dostaw oprogramowania;
* jawnie reprezentować relacje pomiędzy elementami;
* umożliwiać opis przepływów danych lub artefaktów;
* umożliwiać reprezentację granic zaufania;
* wykorzystywać jednoznaczne identyfikatory elementów;
* umożliwiać odwoływanie się do elementów reprezentacji z poziomu wygenerowanych zagrożeń;
* umożliwiać automatyczną walidację strukturalną;
* stanowić podstawę do zapewnienia traceability pomiędzy architekturą systemu a wygenerowanymi zagrożeniami.

## Struktura reprezentacji systemu

Każdy analizowany przypadek łańcucha dostaw oprogramowania jest zapisywany jako dokument JSON zgodny z określoną w projekcie strukturą.

Reprezentacja systemu składa się z czterech głównych części:

```json
{
  "metadata": {},
  "elements": [],
  "relationships": [],
  "flows": []
}
```

Poszczególne części pełnią następujące funkcje:

* `metadata` — zawiera informacje opisujące analizowany przypadek;
* `elements` — zawiera elementy występujące w analizowanym systemie;
* `relationships` — opisuje relacje pomiędzy elementami;
* `flows` — opisuje przepływy danych lub artefaktów pomiędzy elementami.

Taka struktura pozwala oddzielić opis elementów architektury od informacji o zależnościach i przepływach zachodzących pomiędzy nimi.

## Metadane (`metadata`)

Sekcja `metadata` zawiera informacje opisujące analizowany przypadek.

Przewidywana struktura obejmuje:

```json
{
  "metadata": {
    "title": "...",
    "version": "...",
    "date": "...",
    "description": "...",
    "authors": [],
    "organization": "..."
  }
}
```

### Pola

| Pole           | Znaczenie                                                    |
| -------------- | ------------------------------------------------------------ |
| `title`        | Nazwa analizowanego systemu lub przypadku                    |
| `version`      | Wersja reprezentacji                                         |
| `date`         | Data przygotowania reprezentacji                             |
| `description`  | Krótki opis analizowanego systemu                            |
| `authors`      | Autorzy reprezentacji                                        |
| `organization` | Organizacja związana z analizowanym systemem lub przypadkiem |

Metadane nie reprezentują elementów architektury systemu. Służą przede wszystkim do identyfikacji konkretnego przypadku oraz wersji reprezentacji wykorzystywanej w eksperymencie.

## Elementy (`elements`)

Sekcja `elements` opisuje elementy występujące w analizowanym łańcuchu dostaw oprogramowania.

Każdy element posiada unikalny identyfikator oraz określony typ.

Na obecnym etapie przewidziane są cztery podstawowe typy:

```text
component
process
resource
trust_boundary
```

### `component`

Reprezentuje element techniczny lub organizacyjny uczestniczący w łańcuchu dostaw oprogramowania.

Przykładami mogą być:

* repozytorium kodu źródłowego;
* system CI/CD;
* registry pakietów;
* registry kontenerów;
* system podpisywania;
* środowisko wdrożeniowe;
* zewnętrzna usługa;
* komponent infrastruktury.

### `process`

Reprezentuje operację lub etap realizowany w ramach łańcucha dostaw oprogramowania.

Przykładami mogą być:

* budowanie oprogramowania;
* wykonywanie testów;
* pobieranie zależności;
* podpisywanie artefaktu;
* publikowanie pakietu;
* wdrażanie aplikacji.

Rozdzielenie `component` i `process` pozwala odróżnić element uczestniczący w określonej operacji od samej operacji.

### `resource`

Reprezentuje dane lub artefakty istotne z punktu widzenia działania i bezpieczeństwa łańcucha dostaw.

Przykładami mogą być:

* kod źródłowy;
* commit;
* zależność;
* pakiet;
* obraz kontenera;
* artefakt wynikowy;
* konfiguracja;
* sekret;
* SBOM;
* provenance;
* podpis cyfrowy.

### `trust_boundary`

Reprezentuje granicę zaufania występującą w analizowanym systemie.

Granica zaufania wskazuje miejsce, w którym zmienia się poziom zaufania, odpowiedzialność organizacyjna lub domena bezpieczeństwa.

Może przykładowo oddzielać:

* organizację od zewnętrznego dostawcy;
* środowisko deweloperskie od infrastruktury produkcyjnej;
* usługę zewnętrzną od infrastruktury wewnętrznej.

## Identyfikatory elementów

Każdy element musi posiadać unikalny identyfikator.

Identyfikatory służą do tworzenia jednoznacznych odwołań pomiędzy poszczególnymi częściami reprezentacji oraz do późniejszego powiązania wygenerowanych zagrożeń z elementami analizowanego systemu.

Przykład:

```json
{
  "id": "repo_1",
  "type": "component"
}
```

Identyfikator:

* musi być unikalny w obrębie danego przypadku;
* nie powinien zmieniać się pomiędzy uruchomieniami eksperymentu wykorzystującymi tę samą wersję reprezentacji;
* może być wskazywany przez model LLM jako element związany z wygenerowanym zagrożeniem.

## Relacje (`relationships`)

Sekcja `relationships` opisuje kierunkowe relacje pomiędzy elementami reprezentacji systemu.

Podstawowa struktura relacji:

```json
{
  "source": "element_1",
  "target": "element_2",
  "type": "..."
}
```

gdzie:

* `source` wskazuje element źródłowy;
* `target` wskazuje element docelowy;
* `type` określa znaczenie relacji.

Wartości `source` i `target` muszą odnosić się do identyfikatorów elementów istniejących w sekcji `elements`.

Relacje mogą reprezentować operacje i zależności charakterystyczne dla łańcucha dostaw oprogramowania, przykładowo:

```text
create
modify
review
build
sign
verify
store
retrieve
publish
consume
depend
trigger
execute
deploy
authenticate
trust
```

Lista dozwolonych typów relacji zostanie formalnie zdefiniowana w schemacie JSON.

## Przepływy (`flows`)

Sekcja `flows` opisuje kierunkowe przepływy danych lub artefaktów pomiędzy elementami systemu.

Podstawowa struktura:

```json
{
  "source": "element_1",
  "target": "element_2",
  "data_type": "..."
}
```

gdzie:

* `source` wskazuje źródło przepływu;
* `target` wskazuje odbiorcę;
* `data_type` określa rodzaj przekazywanych danych lub artefaktu.

Przykładowe przepływy mogą przedstawiać:

```text
repozytorium → proces budowania : kod źródłowy

system CI → registry : artefakt binarny

registry → proces wdrożenia : obraz kontenera
```

## Relacje a przepływy

Sekcje `relationships` i `flows` opisują dwa różne aspekty analizowanego systemu.

Relacja opisuje znaczenie zależności pomiędzy elementami, przykładowo:

```text
pakiet A zależy od pakietu B
```

Przepływ opisuje natomiast przekazanie danych lub artefaktu pomiędzy elementami:

```text
repozytorium → proces budowania : kod źródłowy
```

Rozdzielenie tych informacji pozwala reprezentować zarówno strukturę zależności systemu, jak i sposób przemieszczania się danych i artefaktów w ramach łańcucha dostaw.

## Walidacja reprezentacji

Przed przekazaniem reprezentacji systemu do modelu LLM dokument JSON powinien przejść automatyczną walidację.

Podstawowe reguły walidacji obejmują:

1. Każdy element posiada unikalny identyfikator.
2. Każdy element posiada poprawny typ.
3. Każde `source` i `target` w `relationships` wskazuje istniejący element.
4. Każde `source` i `target` w `flows` wskazuje istniejący element.
5. Elementy posiadają pola wymagane dla swojego typu.
6. Dokument jest zgodny z formalnym JSON Schema.

Dokument niespełniający tych warunków nie powinien być przekazywany do etapu generowania zagrożeń.

## Powiązanie zagrożeń z reprezentacją systemu

Jednym z podstawowych założeń projektu jest możliwość prześledzenia związku pomiędzy elementami analizowanego systemu a zagrożeniami wygenerowanymi przez model LLM.

Ogólny przepływ wygląda następująco:

```text
analizowany system
        ↓
ustrukturyzowana reprezentacja systemu
        ↓
element / relacja / przepływ
        ↓
wygenerowane zagrożenie
        ↓
uzasadnienie zagrożenia
```

Wygenerowane zagrożenie powinno odwoływać się do identyfikatorów występujących w reprezentacji wejściowej.

Przykładowo, jeżeli zagrożenie wskazuje:

```text
repo_1
build_process_1
```

oba identyfikatory muszą istnieć w reprezentacji analizowanego przypadku.

Pozwala to automatycznie zweryfikować, czy model LLM odwołuje się do rzeczywistych elementów dostarczonych na wejściu.

Taka walidacja nie oznacza jednak, że samo zagrożenie jest poprawne merytorycznie. Ocena poprawności i znaczenia wygenerowanego scenariusza zagrożenia stanowi osobny etap procesu badawczego.

## Minimalny przykład

Poniższy dokument przedstawia minimalny przykład wykorzystania opisanej struktury:

```json
{
  "metadata": {
    "title": "Przykładowy łańcuch dostaw",
    "version": "0.1",
    "date": "2026-08-13",
    "description": "Minimalny przykład reprezentacji systemu.",
    "authors": [],
    "organization": ""
  },

  "elements": [
    {
      "id": "repository",
      "type": "component"
    },
    {
      "id": "build",
      "type": "process"
    },
    {
      "id": "source_code",
      "type": "resource"
    },
    {
      "id": "external_boundary",
      "type": "trust_boundary"
    }
  ],

  "relationships": [
    {
      "source": "repository",
      "target": "build",
      "type": "trigger"
    }
  ],

  "flows": [
    {
      "source": "repository",
      "target": "build",
      "data_type": "source_code"
    }
  ]
}
```

Przykład ma charakter minimalny i służy wyłącznie do przedstawienia ogólnej struktury reprezentacji. Przypadki wykorzystywane w eksperymentach będą zawierały bardziej szczegółowy opis analizowanego łańcucha dostaw.

## Pliki w katalogu `schema`

Docelowo katalog powinien zawierać:

```text
schema/
├── README.md
├── system.schema.json
└── threat.schema.json
```

* `README.md` — opis znaczenia i struktury reprezentacji systemu;
* `system.schema.json` — formalna definicja dokumentu wejściowego;
* `threat.schema.json` — formalna definicja struktury zagrożeń generowanych przez model LLM.

## Status

Schemat znajduje się obecnie na etapie projektowania.

Zmiany w strukturze reprezentacji powinny być wersjonowane, ponieważ sposób reprezentacji analizowanego systemu stanowi jeden z elementów proponowanej metody i może wpływać na wyniki eksperymentów.
