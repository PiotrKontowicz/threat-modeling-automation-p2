# Schemat reprezentacji łańcucha dostaw oprogramowania
Katalog ```schema/``` zawiera specyfikację reprezentacji łańcucha dostaw oprogramowanai wykorzystywanej jako dane wejściowe w procesie. Reprezentacja ma na celu dostarczenie modelowi LLM jedznaczego i możliwego do automatycznej walidacji opisu systemu.

## Założenia
Przyjęty model powinien:
- reprezntować najważniejsze elementy łańcucha dostaw oprogramowania (wersja pilotażowa nie musi zawierać wszystkich możliwych opcji),
- jawnie przedstawia relacje pomiędzy elementami,
- pozwalać na opis przepływów danych lub artefaktów,
- wskazaywać reprezentację granic zaufania,
- wykorzystywać jednoznaczne identyfikatory elementów,
- pozwalać na odwoływanie się do elementów modeli z poziomu wygenerowanych zagrożeń,
- umożliwiać automatyczną walidację struktury,
- stawnowić podstawię do zapewnienia powiazanie pomiędzy archotekturą systemu a generowanymi zagrożęniami.