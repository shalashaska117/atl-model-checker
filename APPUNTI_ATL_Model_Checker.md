# APPUNTI - ATL Model Checker

Questi appunti spiegano il progetto in modo diretto, per ripetere e preparare la presentazione. Non sono scritti in stile formale da consegnare al professore, ma servono per capire bene cosa dire e perché il programma funziona.

## Idea generale

Il progetto è un piccolo ATL model checker.

ATL significa Alternating-time Temporal Logic.

L'idea è questa:

Non voglio solo sapere se in un grafo esiste un percorso che arriva a un certo obiettivo. Voglio sapere se un agente, o un gruppo di agenti, ha una strategia per garantire quell'obiettivo anche se gli altri agenti provano a impedirlo.

Questa è la differenza fondamentale:

    CTL: esiste un cammino?
    ATL: una coalizione ha una strategia?

Quindi il progetto non è semplicemente un CTL checker. È un checker strategico.

## Il gioco

Il gioco è tra due agenti:

    Controller
    Environment

Il Controller è il sistema intelligente che vogliamo verificare.

L'Environment rappresenta l'ambiente esterno, cioè disturbi, guasti, input ostili o eventi non controllabili.

Ogni turno funziona così:

    1. Siamo in uno stato.
    2. Controller sceglie un'azione.
    3. Environment sceglie un'azione.
    4. Le due azioni insieme decidono il prossimo stato.

Quindi non è:

    stato -> prossimo stato

ma:

    stato + azione Controller + azione Environment -> prossimo stato

Questa è la cosa più importante da ricordare.

## Stati

Ci sono tre stati.

### start

    labels = {safe}

Vuol dire che il sistema è sicuro, ma non è ancora arrivato al goal.

### unstable

    labels = {}

Vuol dire che il sistema non è safe e non è goal. È lo stato brutto.

### goal

    labels = {safe, goal}

Vuol dire che il sistema è arrivato all'obiettivo ed è sicuro.

Nel progetto goal è assorbente: una volta arrivato lì, rimane lì.

## Azioni

Il Controller può scegliere:

    wait
    repair

wait significa: non fare nulla.

repair significa: intervieni, correggi, applica una contromisura.

L'Environment può scegliere:

    calm
    disturb

calm significa: non disturbo.

disturb significa: provo a disturbare il sistema.

## Cosa succede da start

Da start ci sono 4 combinazioni, perché il Controller ha 2 mosse e l'Environment ha 2 mosse.

### Caso 1

    Controller = repair
    Environment = calm
    Next state = goal

Il Controller interviene, l'ambiente non disturba, si raggiunge goal.

### Caso 2

    Controller = repair
    Environment = disturb
    Next state = goal

Il Controller interviene e riesce comunque a raggiungere goal anche se l'ambiente disturba.

Questa è una scelta forte del modello. Serve a mostrare un caso in cui il Controller può forzare goal in un passo.

### Caso 3

    Controller = wait
    Environment = calm
    Next state = start

Nessuno fa niente. Il sistema resta sicuro, ma non avanza.

### Caso 4

    Controller = wait
    Environment = disturb
    Next state = unstable

Il Controller non interviene e l'ambiente disturba, quindi il sistema diventa unstable.

Riassunto da start:

    repair + calm    -> goal
    repair + disturb -> goal
    wait   + calm    -> start
    wait   + disturb -> unstable

Conclusione:

Da start, repair è una mossa vincente per il Controller.

Perché?

Perché qualunque cosa faccia l'Environment, se il Controller sceglie repair, il prossimo stato è goal.

Quindi è vera la formula:

    <<Controller>> X goal

che significa:

    il Controller può forzare goal al prossimo passo.

## Cosa succede da unstable

Da unstable:

    repair + calm    -> start
    repair + disturb -> unstable
    wait   + calm    -> unstable
    wait   + disturb -> unstable

Qui il Controller è in difficoltà.

Se sceglie repair e l'Environment è calm, riesce a tornare a start.

Ma se l'Environment sceglie disturb, il sistema resta unstable.

Quindi da unstable il Controller non può garantire goal, perché l'Environment può continuare a disturbare.

Questo è importante perché mostra che non tutti gli stati sono vincenti per il Controller.

## Cosa succede da goal

Da goal:

    qualunque azione -> goal

Quindi goal è assorbente.

Se siamo già in goal, l'obiettivo è già soddisfatto e il sistema resta safe.

## Cosa significa <<Controller>> F goal

Formula:

    <<Controller>> F goal

Lettura:

    Il Controller ha una strategia per arrivare prima o poi a goal.

Da start è vera.

Perché?

Perché basta scegliere repair e si arriva subito a goal.

La strategia è:

    start -> repair

Da goal è vera perché siamo già in goal.

Da unstable è falsa perché l'Environment può scegliere sempre disturb e impedire il progresso.

## Cosa significa <<Controller>> G safe

Formula:

    <<Controller>> G safe

Lettura:

    Il Controller ha una strategia per mantenere safe per sempre.

Da start è vera.

Perché?

Da start il Controller sceglie repair, arriva a goal, e goal è sempre safe.

Da goal è vera perché goal è safe e assorbente.

Da unstable è falsa perché unstable non è safe già all'inizio.

## Cosa significa <<Controller>> (safe U goal)

Formula:

    <<Controller>> (safe U goal)

Lettura:

    Il Controller può mantenere safe vero fino a quando raggiunge goal.

Da start è vera.

Perché:

    start è safe;
    scegliendo repair si va a goal;
    goal viene raggiunto subito;
    quindi safe non viene mai violato prima del goal.

Da goal è vera perché goal è già raggiunto.

Da unstable è falsa perché safe è già falso e goal non è vero.

## Cosa significa <<Environment>> F !safe

Formula:

    <<Environment>> F !safe

Lettura:

    L'Environment può forzare prima o poi uno stato non safe?

Da start è falsa.

Attenzione: da start esiste una combinazione che porta a unstable:

    wait + disturb -> unstable

Però questo non basta.

ATL non chiede:

    può succedere?

ATL chiede:

    l'Environment può forzarlo qualunque cosa faccia il Controller?

Da start, se il Controller sceglie repair, si va a goal, non a unstable.

Quindi l'Environment non può forzare !safe da start.

Questa è una delle frasi più importanti da dire.

## Cosa significa <<Environment>> G !goal

Formula:

    <<Environment>> G !goal

Lettura:

    L'Environment può mantenere goal falso per sempre?

Da start è falsa, perché il Controller può scegliere repair e andare a goal.

Da unstable è vera, perché l'Environment può scegliere sempre disturb e rimanere in unstable.

Strategia dell'Environment da unstable:

    unstable -> disturb

## Differenza tra possibilità e strategia

Questa è la parte teorica più importante.

Da start, è possibile arrivare a unstable?

Sì:

    Controller = wait
    Environment = disturb
    next = unstable

Però l'Environment può forzare unstable da start?

No.

Perché il Controller può scegliere repair e impedirlo.

Quindi:

    possibile non significa strategicamente garantibile.

Questa è la differenza tra CTL e ATL.

## Cosa fa il file main.py

main.py è la demo.

Fa queste cose:

    1. Crea il modello Controller vs Environment.
    2. Crea il model checker ATL.
    3. Stampa gli stati.
    4. Stampa gli agenti.
    5. Verifica una lista di formule ATL.
    6. Per ogni formula stampa gli stati che la soddisfano.
    7. Dice se la formula è vera in start.
    8. Se la formula è strategica, stampa anche una strategia testimone.

## Cosa fa build_controller_environment_model

Questa funzione crea il gioco.

Aggiunge gli agenti:

    Controller
    Environment

Aggiunge gli stati:

    start
    unstable
    goal

Aggiunge le azioni:

    Controller: wait, repair
    Environment: calm, disturb

Poi aggiunge tutte le transizioni.

Alla fine controlla che il modello sia totale.

Totale significa:

    per ogni stato e per ogni combinazione di azioni deve esistere un prossimo stato.

Questo è importante perché il gioco non deve avere buchi.

## Cosa fa il parser

Il parser prende una stringa tipo:

    <<Controller>> F goal

E la trasforma in una struttura interna, cioè un AST.

AST significa Abstract Syntax Tree.

Per esempio:

    <<Controller>> F goal

viene trasformata concettualmente in:

    StrategicEventually({Controller}, Atom(goal))

Il checker non lavora direttamente sulle stringhe. Lavora su questi oggetti.

## Cosa fa il checker

Il checker calcola quali stati soddisfano una formula.

Se gli passo:

    <<Controller>> F goal

lui restituisce:

    {start, goal}

Perché da start il Controller può forzare goal, e in goal il goal è già vero.

## Cos'è Sat(phi)

Nel codice checker.sat(formula) calcola:

    Sat(phi) = insieme degli stati in cui phi è vera

Esempio:

    Sat(goal) = {goal}
    Sat(safe) = {start, goal}
    Sat(!safe) = {unstable}
    Sat(<<Controller>> F goal) = {start, goal}

## Cos'è Pre_A(X)

Questa è la funzione teorica fondamentale.

Pre_A(X) significa:

    stati da cui la coalizione A può forzare il prossimo stato dentro X.

Formula mentale:

    esiste una mossa della coalizione A
    tale che
    per ogni mossa degli altri agenti
    il prossimo stato è in X

Per il Controller da start e X = {goal}:

Provo repair:

    repair + calm    -> goal
    repair + disturb -> goal

Tutti i risultati sono in X.

Quindi start è in Pre_Controller({goal}).

Provo wait:

    wait + calm    -> start
    wait + disturb -> unstable

Non tutti i risultati sono in X.

Quindi wait non è una mossa vincente.

## Come viene calcolato <<A>> F phi

Per <<A>> F phi il checker usa un least fixed point.

Tradotto semplice:

    1. Parti dagli stati dove phi è già vero.
    2. Guarda quali stati possono forzare un passo verso quelli già vincenti.
    3. Aggiungili.
    4. Ripeti finché non puoi aggiungere più nulla.

Esempio per <<Controller>> F goal:

    Stati inizialmente vincenti: {goal}

Poi il checker guarda chi può forzare un passo verso goal.

Da start, Controller può scegliere repair e forzare goal.

Quindi aggiunge start.

    Stati vincenti: {goal, start}

Da unstable non riesce ad aggiungere nulla, perché Environment può disturbare.

Risultato finale:

    {goal, start}

## Come viene calcolato <<A>> G phi

Per <<A>> G phi il checker usa un greatest fixed point.

Tradotto semplice:

    1. Parti da tutti gli stati dove phi è vero.
    2. Tieni solo quelli da cui la coalizione può restare dentro questo insieme.
    3. Ripeti finché l'insieme non cambia più.

Esempio per <<Controller>> G safe:

Stati safe:

    {start, goal}

Da start, Controller può scegliere repair e andare a goal, che è safe.

Da goal, si resta in goal.

Quindi il risultato resta:

    {start, goal}

## Come viene calcolato <<A>> (phi U psi)

Per until:

    <<A>> (phi U psi)

il checker fa:

    1. Parti dagli stati dove psi è vero.
    2. Aggiungi stati dove phi è vero e da cui A può forzare un passo verso gli stati vincenti.
    3. Ripeti.

Esempio:

    <<Controller>> (safe U goal)

Parto da:

    {goal}

Da start:

    safe è vero
    Controller può forzare goal

Quindi aggiungo start.

Risultato:

    {goal, start}

## Cos'è la strategy extraction

Il programma non dice solo true o false.

Se una formula strategica è vera, prova anche a stampare una strategia.

Esempio:

    <<Controller>> F goal

Output:

    start -> repair
    goal -> objective already satisfied

Significa:

    da start il Controller deve scegliere repair;
    da goal non serve fare nulla perché l'obiettivo è già soddisfatto.

Questa parte è importante perché sembra più vicina alla sintesi:

    non solo verifico che una strategia esiste,
    ma ne mostro una.

## Come spiegare l'output

Quando vedi:

    Formula: <<Controller>> F goal
    Parsed : <<Controller>> F (goal)
    States : {'start', 'goal'}
    start  : True
    Strategy:
    - goal: objective already satisfied
    - start: choose {'Controller': 'repair'}

Devi dire:

Il checker ha verificato che la formula è vera negli stati start e goal. In particolare è vera nello stato iniziale start. La strategia testimone dice che da start il Controller deve scegliere repair. Da goal non serve scegliere una mossa per raggiungere goal, perché goal è già vero.

## Cosa dire al professore in breve

Puoi dire:

Ho implementato un piccolo ATL model checker su Concurrent Game Structures finite. Il modello rappresenta un sistema aperto con due agenti, Controller ed Environment. Le transizioni dipendono dalle joint actions degli agenti. Il checker supporta operatori booleani e operatori strategici ATL: next, eventually, always e until. La semantica è implementata tramite strategic predecessor e fixed point. Inoltre il programma estrae strategie testimoni per le formule strategiche vere.

## Frase chiave da ricordare

La frase più importante è:

    In ATL non verifico solo se esiste un cammino, ma se una coalizione ha una strategia per forzare una proprietà contro tutte le mosse degli agenti avversari.

## Possibile domanda del professore: perché repair + disturb = goal?

Risposta:

Nel modello demo repair rappresenta una contromisura forte, sufficiente a neutralizzare il disturbo dell'ambiente da start. Questa scelta serve a mostrare chiaramente una proprietà strategica forte: il Controller può forzare goal in un passo. Il modello può essere facilmente modificato in una versione più realistica in cui repair + disturb = start; in quel caso il Controller potrebbe garantire safety ma non necessariamente liveness.

Questa risposta è buona perché fai vedere che sai che è una scelta modellistica, non una verità assoluta.

## Possibile domanda: perché Environment non può forzare !safe da start?

Risposta:

Perché per forzare !safe, Environment dovrebbe avere una mossa che porta a !safe per ogni possibile risposta del Controller. Ma da start, se Controller sceglie repair, si va a goal, che è safe. Quindi Environment può causare !safe solo se Controller sceglie wait, ma non può garantirlo contro tutte le scelte del Controller.

## Possibile domanda: perché unstable soddisfa <<Environment>> G !goal?

Risposta:

Perché da unstable, Environment può scegliere sempre disturb. In questo modo il sistema resta unstable, e in unstable goal è falso. Quindi Environment ha una strategia per mantenere !goal per sempre.

## Possibile domanda: che relazione c'è con symbolic AI?

Risposta:

Il progetto usa rappresentazioni simboliche: stati, proposizioni atomiche, formule logiche e strategie esplicite. Non apprende da dati, ma ragiona formalmente su ciò che gli agenti possono garantire. Questo è un esempio di AI simbolica applicata alla verifica di sistemi multi-agente.

## Riassunto finale

Il progetto mostra:

    modello multi-agente;
    azioni simultanee;
    transizioni dipendenti da joint actions;
    formule ATL;
    model checking strategico;
    fixed point;
    estrazione di strategie.

La demo principale mostra che:

    Controller può forzare goal da start;
    Controller può mantenere safe da start;
    Environment non può forzare !safe da start;
    Environment può mantenere !goal da unstable.

Questa è la logica del gioco e del programma.
