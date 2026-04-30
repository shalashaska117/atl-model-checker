# ATL Model Checker

## Titolo del progetto

Strategic Verification of Open Systems using Alternating-time Temporal Logic

## Obiettivo

Questo progetto implementa un piccolo model checker per un frammento finito di ATL, Alternating-time Temporal Logic. L'obiettivo non è costruire un tool industriale completo, ma realizzare un prototipo leggibile e formalmente fondato che mostri come verificare proprietà strategiche di sistemi multi-agente.

Il punto centrale è distinguere tra:

- verifica di percorsi, tipica di CTL;
- verifica di strategie, tipica di ATL.

In CTL si chiede, ad esempio, se esiste un cammino che raggiunge uno stato obiettivo. In ATL si chiede invece se una coalizione di agenti possiede una strategia per forzare il raggiungimento di tale obiettivo, indipendentemente dalle scelte degli altri agenti.

## Motivazione teorica

Il progetto si basa sull'idea che molti sistemi di interesse in intelligenza artificiale simbolica, verifica formale e sistemi multi-agente non siano sistemi chiusi, ma sistemi aperti. Un sistema aperto interagisce con un ambiente esterno, e il suo comportamento non dipende solo dalle decisioni interne, ma anche dalle decisioni dell'ambiente.

Per questo motivo, una semplice struttura di Kripke non è sufficiente a rappresentare esplicitamente chi controlla quale transizione. Il progetto utilizza quindi una Concurrent Game Structure, in cui ogni transizione dipende da una joint action, cioè dalla combinazione delle azioni scelte simultaneamente da tutti gli agenti.

## Modello formale

Il modello implementato è una Concurrent Game Structure finita.

Una Concurrent Game Structure può essere vista come una tupla composta da:

- un insieme finito di stati S;
- un insieme finito di agenti Ag;
- per ogni stato e agente, un insieme di azioni disponibili;
- una funzione di transizione delta;
- una funzione di labeling L che assegna a ogni stato le proposizioni atomiche vere in quello stato.

Nel progetto, la funzione di transizione ha la forma:

    delta(state, joint_action) = next_state

Dove una joint_action contiene una scelta per ogni agente.

Nel caso del modello dimostrativo:

    Agents = {Controller, Environment}

Il Controller rappresenta l'agente che vogliamo verificare. L'Environment rappresenta l'ambiente esterno, potenzialmente avversario.

## Stati del modello dimostrativo

Il modello principale contiene tre stati:

### start

Etichette:

    {safe}

Significato:

Il sistema è sicuro, ma non ha ancora raggiunto l'obiettivo.

### unstable

Etichette:

    {}

Significato:

Il sistema non è sicuro e non ha raggiunto l'obiettivo. È uno stato problematico.

### goal

Etichette:

    {safe, goal}

Significato:

Il sistema ha raggiunto l'obiettivo ed è sicuro. Nel modello demo, goal è assorbente: una volta raggiunto, il sistema resta in goal.

## Azioni degli agenti

Il Controller può scegliere:

    wait
    repair

L'Environment può scegliere:

    calm
    disturb

Interpretazione:

- wait: il Controller non interviene;
- repair: il Controller applica una contromisura;
- calm: l'ambiente non disturba;
- disturb: l'ambiente prova a disturbare il sistema.

## Transizioni del modello

Da start:

    delta(start, repair, calm)    = goal
    delta(start, repair, disturb) = goal
    delta(start, wait, calm)      = start
    delta(start, wait, disturb)   = unstable

Interpretazione:

Da start, repair è una mossa vincente forte per il Controller, perché porta a goal sia se l'ambiente è calmo sia se l'ambiente disturba. wait è invece rischiosa: se l'ambiente disturba, il sistema diventa unstable.

Da unstable:

    delta(unstable, repair, calm)    = start
    delta(unstable, repair, disturb) = unstable
    delta(unstable, wait, calm)      = unstable
    delta(unstable, wait, disturb)   = unstable

Interpretazione:

Da unstable, il Controller può recuperare solo se l'ambiente è calm. Se l'Environment continua a disturbare, il sistema resta unstable. Quindi da unstable il Controller non può forzare il raggiungimento di goal.

Da goal:

    delta(goal, repair, calm)    = goal
    delta(goal, repair, disturb) = goal
    delta(goal, wait, calm)      = goal
    delta(goal, wait, disturb)   = goal

Interpretazione:

Goal è assorbente. Una volta raggiunto, nessuna azione può far uscire il sistema da goal.

## Linguaggio logico supportato

Il progetto supporta un frammento di ATL sufficiente a esprimere le proprietà strategiche principali.

Sono supportati:

    TRUE
    FALSE
    p
    !phi
    phi & psi
    phi | psi
    phi -> psi

Operatori strategici ATL:

    <<A>> X phi
    <<A>> F phi
    <<A>> G phi
    <<A>> (phi U psi)

Dove A è una coalizione di agenti.

## Significato degli operatori ATL

### Strategic Next

    <<A>> X phi

Significa:

La coalizione A ha una scelta di azioni tale che, qualunque azione scelgano gli agenti fuori da A, il prossimo stato soddisfa phi.

### Strategic Eventually

    <<A>> F phi

Significa:

La coalizione A ha una strategia per forzare prima o poi uno stato che soddisfa phi, qualunque cosa facciano gli agenti esterni alla coalizione.

### Strategic Always

    <<A>> G phi

Significa:

La coalizione A ha una strategia per mantenere phi vero per sempre.

### Strategic Until

    <<A>> (phi U psi)

Significa:

La coalizione A ha una strategia per forzare prima o poi psi, mantenendo phi vero fino al raggiungimento di psi.

## Operatore centrale: strategic predecessor

Il cuore teorico del progetto è l'operatore di predecessore strategico:

    Pre_A(X)

Uno stato s appartiene a Pre_A(X) se e solo se la coalizione A possiede una joint action tale che, per ogni possibile joint action degli agenti esterni ad A, il prossimo stato appartiene a X.

Formalmente:

    s in Pre_A(X)
    iff
    exists alpha_A such that for all alpha_not_A:
        delta(s, alpha_A union alpha_not_A) in X

Questa formula esprime la differenza fondamentale tra CTL e ATL.

In CTL si avrebbe una quantificazione sui cammini. In ATL si ha una quantificazione strategica sulle scelte degli agenti.

## Fixed point utilizzati

Gli operatori temporali strategici sono implementati tramite fixed point.

### <<A>> F phi

Strategic eventually viene calcolato come least fixed point.

Si parte dagli stati in cui phi è già vero. Poi si aggiungono iterativamente gli stati da cui la coalizione A può forzare l'ingresso nell'insieme corrente.

### <<A>> G phi

Strategic always viene calcolato come greatest fixed point.

Si parte dagli stati in cui phi è vero. Poi si rimuovono iterativamente gli stati da cui la coalizione A non riesce a rimanere dentro l'insieme candidato.

### <<A>> (phi U psi)

Strategic until viene calcolato come least fixed point.

Si parte dagli stati in cui psi è già vero. Poi si aggiungono gli stati in cui phi è vero e da cui la coalizione A può forzare l'ingresso nell'insieme già vincente.

## Proprietà verificate nella demo

### 1. Controller può forzare goal al prossimo passo

Formula:

    <<Controller>> X goal

Risultato atteso:

    true in start

Motivo:

Da start, il Controller può scegliere repair. Se Environment sceglie calm si va in goal. Se Environment sceglie disturb si va comunque in goal.

Quindi repair è una mossa vincente in un passo.

### 2. Controller può forzare goal prima o poi

Formula:

    <<Controller>> F goal

Risultato atteso:

    true in start

Motivo:

Poiché il Controller può già forzare goal in un passo da start, può certamente forzarlo eventualmente.

La strategia testimone è:

    start -> repair

### 3. Controller può mantenere safe per sempre

Formula:

    <<Controller>> G safe

Risultato atteso:

    true in start

Motivo:

Da start, scegliendo repair, il Controller forza il passaggio a goal. Goal è safe ed è assorbente. Quindi safe può essere mantenuto per sempre.

### 4. Controller può mantenere safe fino al goal

Formula:

    <<Controller>> (safe U goal)

Risultato atteso:

    true in start

Motivo:

Da start, safe è vero. Il Controller sceglie repair e raggiunge goal immediatamente. Quindi safe rimane vero fino al raggiungimento di goal.

### 5. Environment può forzare uno stato non safe?

Formula:

    <<Environment>> F !safe

Risultato atteso:

    false in start

Motivo:

Environment vorrebbe portare il sistema in unstable. Tuttavia, da start, se il Controller sceglie repair, il sistema va in goal indipendentemente dal disturbo. Quindi Environment non può forzare !safe contro tutte le possibili azioni del Controller.

### 6. Environment può mantenere goal falso per sempre?

Formula:

    <<Environment>> G !goal

Risultato atteso:

    false in start
    true in unstable

Motivo:

Da start il Controller può scegliere repair e raggiungere goal. Quindi Environment non può impedire goal per sempre.

Da unstable, invece, Environment può scegliere sempre disturb e mantenere il sistema in unstable, dove goal è falso.

### 7. Stati safe da cui Controller può forzare goal

Formula:

    safe & <<Controller>> F goal

Risultato atteso:

    {start, goal}

Motivo:

start è safe e il Controller può forzare goal. goal è già safe ed è già goal. unstable non è safe.

## Strategy extraction

Il progetto non si limita a dire se una formula è vera o falsa. Per le formule strategiche può anche estrarre una strategia testimone.

Esempio:

    <<Controller>> F goal

Strategia:

    start -> {Controller: repair}
    goal  -> objective already satisfied

Questo mostra il lato costruttivo del model checking ATL: quando una proprietà strategica è vera, il programma può mostrare come la coalizione può garantirla.

## Struttura del progetto

    atl-model-checker/
    |
    |-- model/
    |   |-- game_structure.py
    |
    |-- logic/
    |   |-- ast.py
    |   |-- parser.py
    |
    |-- model_checker/
    |   |-- atl_checker.py
    |
    |-- examples/
    |   |-- controller_env.py
    |
    |-- tests/
    |   |-- test_atl_checker.py
    |
    |-- main.py
    |-- README.md
    |-- requirements.txt

## Descrizione dei file

### model/game_structure.py

Definisce la Concurrent Game Structure. Gestisce stati, agenti, azioni, transizioni, labeling e totalità della relazione di transizione.

### logic/ast.py

Definisce le classi che rappresentano le formule logiche come alberi sintattici astratti.

### logic/parser.py

Trasforma formule scritte come stringhe in oggetti AST.

Esempio:

    <<Controller>> F goal

viene trasformata in una formula StrategicEventually con coalizione Controller e obiettivo Atom(goal).

### model_checker/atl_checker.py

Contiene la semantica del linguaggio. Calcola gli stati che soddisfano una formula e implementa gli operatori ATL tramite strategic predecessor e fixed point.

### examples/controller_env.py

Costruisce il modello dimostrativo Controller vs Environment.

### tests/test_atl_checker.py

Contiene test automatici per verificare coerenza tra modello, parser, AST, checker e strategy extraction.

### main.py

Esegue la demo, stampa gli stati, gli agenti, i risultati delle formule e le strategie testimoni.

## Come eseguire

Dalla cartella principale del progetto:

    python main.py

Per eseguire i test:

    python -m unittest discover -s tests

## Output atteso

L'output mostra:

- gli stati del modello;
- gli agenti;
- le formule verificate;
- la formula parsata;
- l'insieme degli stati soddisfacenti;
- il risultato nello stato iniziale start;
- una strategia testimone, se disponibile.

Esempio:

    Formula: <<Controller>> F goal
    Parsed : <<Controller>> F (goal)
    States : {'start', 'goal'}
    start  : True
    Strategy:
    - goal: objective already satisfied
    - start: choose {'Controller': 'repair'}

## Conclusione

Il progetto mostra un frammento essenziale ma formalmente significativo di ATL model checking. La demo evidenzia la differenza tra possibilità e garanzia strategica.

Il risultato principale è che il Controller può forzare il raggiungimento del goal e mantenere la sicurezza da start, mentre l'Environment non può forzare uno stato unsafe da start. Questo dimostra che il sistema non viene analizzato solo come grafo di transizioni, ma come gioco tra agenti con strategie.

Il progetto è quindi un prototipo compatto di symbolic AI applicata alla verifica formale di sistemi multi-agente.
