# Pół automatyczny system modelowania zagrożeń dla łańcucha dostaw oprogramowania

Repozytorium zawiera szczegóły badawcze oraz eksperymentalną implementację półautomatycznego systemu rozwijanego w ramach badań nad półautomatycznym modelowaniem zagrożeń dla łańcucha dostaw oprogramowania z wykorzystaniem dużych modeli językowych (LLM).

## Cel projektu
Celem jest zbadanie, w jakim stopniu duże modele językowe mogą wspierać identyfikacje zagrożeń jednocześnie zachowując jawne powiązanie wygenerowanych zagrożeń z archotekturą analizowanego systemu.

Podejście zakłąda wykorzystanie ustrukturyzowanego opisu łańcucha dostaw oprogramowania oraz automatycznej walidacji wyników generowanych przez model językowy.

## Ogólne koncepcja
Analiza obejmuje cztery główne etapy:
1. Reprezentacja systemu
Łańcuch dostaw opisany jest w kontrolowanym, ustrukturyzowanym formacjcie obejmującym komponenty, zasoby, przepływy, relacje oraz granice zaufania.
2. Generowanie zagrożeń
Model językowy analizuje reprezentację systemu i generuje potencjalne scenariusze zagrożeń.
3. Powiązanie zagrożeń z architekturą
Każde wygenerowane zagrożenie musi wskazywać konkretne elementy analizowanego systemu, których dotyczy np. komponenty, relacje, zasoby lub przepływy
4. Walidacja strukturalna
Wyniki generowane przez model są automatycznie weryfikowane względem wejściowego modelu systemu. Walidacja sprawdza poprawność odwołań do elementów architektury oraz zgodność wyniku z wymaganym schematem danych.

Po zakończeniu walidacji wyniki zostają poddane ocenie przez eksperta pod kątem poprawności, istotności oraz jakości zidentyfikowanych zagrożeń.

## Struktura repozytorium
```text
.
├── analysis/ # Analiza wyników eksperymentów 
├── annotation/ # Materiały związane z oceną i anotacją ekspercką 
├── cases/ # Przypadki testowe łańcuchów dostaw oprogramowania 
├── experiments/ # Konfiguracje i artefakty eksperymentów 
├── paper/ # Materiały związane z przygotowaniem publikacji 
├── prompts/ # Prompty i szablony promptów dla modeli LLM 
├── results/ # Surowe i przetworzone wyniki eksperymentów 
├── schema/ # Schematy reprezentacji systemu i zagrożeń 
├── src/ # Kod źródłowy prototypowego rozwiązania 
└── README.md
```

## Etap prac
Projekt znajduje sie na etapie projektowania i przygotowania środowiska. W pierwszej kolejności rozwijane będą:
- schemat reprezentacji łańcucha dostaw oprogramowania,
- schemat reprezentacji wygenerowanych zagrożeń,
- referencyjne przypadki testowe, 
- mechanizm generowania zagrożeń z wykorzystaniem LLM,
- mechanizm automatycznej walidacji strukturalnej,
- metodologia eksperementyalnej i eksperckiej oceny wyników.

## Główny cel badawczy
Celem **nie** jest pełna automatyzacja procesu modelowania zagrożeń.
Badanie koncetruje się na sprawdzeniu, czy generowanie zagrożeń przez modele LLM można skutecznie połączyć z uporządkowaną reprezentacją systemu, jawnym śledzeniem zagrożeń oraz automatyczną walidacją tworząc wynik który może zostać oceniony przez eskpertów.