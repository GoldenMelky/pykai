# Mikai x Flipper x Android

## Prerequisiti
Automate

> Per attendere l’usb del flipper e auto connettersi e eseguire i comandi su termux

Termux

> Per eseguire Mikai

Termux:Tasker

> Per eseguire i comandi da Automate

USB Serial Telnet Server

> Bridge tra il flipper e termux

Serial USB Terminal

> Per inizializzare la comunicazione seriale

## Come funziona (Under the hood)

Il funzionamento si può dividere in due fasi, fase GUI e fase Terminale (background)

### GUI

In questa fase viene stabilita la connessione tra Android e Flipper Zero e viene avviato il bridge per Termux. Si chiama fase GUI perché per fare tutto ciò va a simulare dei tocchi sullo schermo.

* Inizio flow Automate
* Automate attende connessione Flipper Zero
* Viene aperta **Serial USB Terminal**

> Servono due applicazioni perché Serial USB Terminal inizializza la connessione seriale, senza di questa inizializzazione non si ottiene output dalla comunicazione seriale

* Viene connesso il dispositivo (click)
* Viene aperta **USB Serial Telnet Server**
* Viene startato il server Telnet (click)

### Terminale (background)

Qua avviene tutto il processo di download del file, modifica tramite mikai, e upload del file, non scriverò i passaggi perché non ho voglia, ci sono i commenti sullo script python

## Installazione

Dentro Termux esegui questo script

​
