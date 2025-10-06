# ClassExit - Registro digitale delle uscite dall'aula

## Descrizione
ClassExit è un'applicazione web per la gestione delle uscite temporanee degli studenti da un'aula scolastica. Permette di registrare chi esce, quando esce e quando rientra, rispettando la regola che solo uno studente alla volta può essere fuori dall'aula.

## Funzionalità
- **Gestione di più classi**: Crea e gestisci diverse classi
- **Registrazione studenti**: Aggiungi studenti alle classi
- **Controllo uscite**: Solo uno studente per volta può uscire
- **Monitoraggio in tempo reale**: Visualizza chi è in aula e chi è fuori
- **Storico completo**: Cronologia di tutte le uscite di ogni studente
- **Interface moderna**: Design responsive con Bootstrap 5

## Tecnologie utilizzate
- Python 3.13
- Flask (web framework)
- TinyDB (database JSON)
- Bootstrap 5 (interfaccia grafica)
- Font Awesome (icone)

## Installazione e avvio

1. Assicurati che il virtual environment sia attivato
2. Le dipendenze sono già installate (Flask e TinyDB)
3. Avvia l'applicazione:
   ```
   python app.py
   ```
4. Apri il browser su `http://localhost:5000`

## Struttura del progetto
```
ProgettoClassExit/
├── app.py                 # Applicazione Flask principale
├── database.json          # Database TinyDB
├── templates/
│   ├── index.html         # Homepage con lista classi
│   ├── classe.html        # Gestione di una classe specifica
│   └── storico.html       # Storico uscite di uno studente
└── README.md              # Questo file
```

## Come usare l'applicazione

### 1. Creare una classe
- Dalla homepage, clicca su "Nuova Classe"
- Inserisci il nome della classe (es: "5A", "3B Informatica")
- Clicca "Crea Classe"

### 2. Aggiungere studenti
- Entra nella gestione di una classe
- Clicca su "Nuovo Studente"
- Inserisci nome e cognome
- Clicca "Aggiungi Studente"

### 3. Registrare uscite
- Dalla dashboard della classe, clicca "Uscita" accanto al nome dello studente
- Il sistema registrerà automaticamente data e ora
- Solo uno studente alla volta può essere fuori

### 4. Registrare rientri
- Clicca "Rientro" quando lo studente torna in aula
- Il sistema completerà automaticamente la registrazione

### 5. Consultare lo storico
- Clicca "Storico" accanto al nome dello studente
- Visualizza tutte le uscite passate con durata e orari

## Funzionalità avanzate implementate

### Gestione multi-classe
- Ogni classe è indipendente
- Possibilità di eliminare classi complete
- Navigazione facile tra le classi

### Controlli di sicurezza
- Un solo studente fuori per classe
- Validazione dei dati inseriti
- Controllo duplicati

### Interface utente
- Design moderno e responsivo
- Aggiornamento automatico ogni 30 secondi
- Indicatori visivi per stato studenti
- Timeline interattiva per lo storico

### Database strutturato
- Tabelle separate per classi, studenti e uscite
- Relazioni tra entità
- Storico completo mantenuto

## Note tecniche
- L'applicazione funziona completamente in locale
- Il database è un file JSON gestito da TinyDB
- L'interfaccia è ottimizzata per dispositivi mobili e desktop
- Auto-refresh per mantenere i dati aggiornati

## Possibili estensioni future
- Autenticazione docenti
- Esportazione dati in Excel
- Notifiche push per uscite prolungate
- Gestione permessi e giustificazioni
- API REST per integrazione con altri sistemi