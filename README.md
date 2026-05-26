##  Ewolucja Algorytmu i Architektury Sieci Neuronowej                                                                                                             
                                                                                                                                                                     
  ---
                                                                                                                                                                       
  ### 1. Wnioski z wczesnych wersji                                                                                                                                    
                                                                                                                                                                       
  Pierwsze iteracje opierały się na jednym globalnym modelu ogólnopolskim trenowanym na danych ze wszystkich miast jednocześnie. Testowano dwa podejścia:              
                                                            
  - **Model z cechą `centre_distance`** – dystans euklidesowy od centrum miasta jako szósty wymiar wektora wejściowego. Sieć uczyła się dominującego gradientu         
  radialnego (cena spada wraz z odległością od centrum), ignorując lokalne mikrostruktury cenowe poszczególnych dzielnic.
  - **Model z kodowaniem one-hot i skrzyżowaniem cech** (`input_size = 51`) – rozszerzenie wektora o reprezentację przynależności do miasta oraz iloczyny współrzędnych
   z wektorami one-hot. Zwiększona przestrzeń wejściowa pogorszyła gradient i nie rozwiązała problemu.                                                                 
   
  W obu przypadkach sieć o architekturze `[64, 32]` generowała **zniekształcenia przestrzenne**: koncentryczne okręgi wokół centrów miast, brak czytelnego podziału na 
  dzielnice oraz artefakty brzegowe wynikające z ekstrapolacji poza obszar treningu. Przyczyną było zbyt małe pojemność modelu wobec skali zróżnicowania wielu rynków  
  jednocześnie.
                                                                                                                                                                       
  ---                                                       

  ### 2. Finalna architektura: Batch Training (niezależne modele per miasto)
                                                                                                                                                                       
  **Wektor cech:** Rezygnacja z `centre_distance` i kodowania one-hot. Powrót do czystej, pięciowymiarowej reprezentacji:
                                                                                                                                                                       
  input_size = 5: [lat, lon, area_m2, floor, build_year]    
                                                                                                                                                                       
  **Mechanizm treningu:** Jedno kliknięcie „Uruchom trening" tworzy pojedynczy rekord `ModelRun` w bazie, jednak backend uruchamia sekwencyjną pętlę trenującą **6 w
  pełni niezależnych modeli** (Warszawa, Kraków, Wrocław, Gdańsk, Poznań, Łódź). Każdy model uczy się wyłącznie na odfiltrowanych danych z własnego rynku i zapisywany 
  jest jako osobny plik wag `{run_id}_{city}.pt`. Postęp wszystkich 6 faz raportowany jest jako ciągły licznik epok `[0, N×6)` widoczny w panelu treningowym.
                                                                                                                                                                       
  **Architektura sieci:** `PricePredictor` z domyślnymi warstwami ukrytymi `[128, 64, 32]` i dropout `0.2`. Większa pojemność modelu w połączeniu z jednorodnym,       
  jednorodnym pod względem rynku zbiorem treningowym pozwoliła sieci wyodrębnić lokalne mikrogradienty cenowe.
                                                                                                                                                                       
  **Robust Scaling:** Normalizacja cech oparta na **percentylach 1% i 99%** (`fit_stats` w `preprocessing.py`) zamiast globalnych wartości `min`/`max`. Eliminuje wpływ
   wartości skrajnych (outlierów cenowych), przywracając kontrast i rozpiętość kolorystyczną heatmapy. Granice normalizacji `lat`/`lon` wyznaczane są z danych
  treningowych danego miasta (percentyle 0,5% i 99,5%), co zapobiega ekstrapolacji poza obszar rzeczywistych obserwacji.                                               
                                                            
  ---

  ### 3. Usprawnienia UX i stabilizacja interfejsu

  **Tryb „Typowe mieszkanie":** Checkbox w panelu parametrów przełącza suwaki w tryb pasywny i przesyła do backendu wartości `null` zamiast konkretnych zakresów.      
  Backend zastępuje je medianą przedziału `[p25, p75]` wyestymowanego z danych treningowych dla danego miasta (`_resolve()` w `inference.py`). Zapobiega to
  zniekształceniom heatmapy dla nierealistycznych kombinacji parametrów (np. parter i 200 m²). Percentyle `p25`/`p75` są zapisywane w obiekcie `FeatureStats` wewnątrz 
  checkpointu i zwracane przez endpoint `/api/heatmap` jako pola `area_p25`, `floor_p25`, `year_p25` itd., co pozwala frontendowi inicjalizować suwaki wartościami
  rynkowymi specyficznymi dla wytrenowanego modelu.

  **Eliminacja race condition przy przełączaniu miast:** Automatyczne wykrywanie miasta z pozycji mapy (zdarzenie Leaflet `moveend`) zabezpieczone flagą referencyjną  
  `isProgrammaticMove` (`useRef<boolean>`) w komponencie `MapController`. Flaga ustawiana jest na `true` bezpośrednio przed każdym programowym ruchem mapy
  (`map.setView` lub `map.fitBounds`); pierwsza linia handlera `moveend` sprawdza flagę, zeruje ją i natychmiast przerywa wykonanie — blokując nadpisanie wyboru       
  użytkownika przez algorytm haversine. Kluczowe było scalenie dwóch wcześniej rozdzielonych efektów (`useEffect([currentCity])` i `useEffect([fitTrigger])`) w jeden,
  gwarantujące dokładnie jedno wywołanie operacji mapowej i jedno zdarzenie `moveend` na akcję użytkownika.

  **Pływający widżet zakresu cenowego:** Wartości `min_val` i `max_val` zwracane przez model eksponowane są jako nakładka absolutnie pozycjonowana w prawym górnym rogu
   mapy (`z-index: 1000`), z wyraźnym oznaczeniem kolorystycznym (niebieski — cena minimalna, szmaragdowy — cena maksymalna) i paskiem gradientu odpowiadającym skali
  kolorów heatmapy.       