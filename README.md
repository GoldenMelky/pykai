# Mikai x Flipper x Android

## Prerequisiti
Automate

> Per attendere l’usb del flipper e auto connettersi e eseguire i comandi su termux
> DA SCARICSRE DA F-DROID

Termux

> Per eseguire Mikai
> DA SCARICARE DA F-DROID

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

### Termux

Installiamo debian

```bash
pkg update
pkg upgrade -y
pkg install wget openssl-tool proot -y
wget https://raw.githubusercontent.com/EXALAB/AnLinux-Resources/master/Scripts/Installer/Debian/debian.sh
bash debian.sh
```

Adesso startiamo debian, installiamo le dipendenze e cloniamo la repo 

```bash
./start-debian.sh
```
```bash
mkdir -p /usr/share/keyrings
wget -qO- "https://pi-apps-coders.github.io/box64-debs/KEY.gpg" | gpg --dearmor -o /usr/share/keyrings/box64-archive-keyring.gp
echo "Types: deb
URIs: https://Pi-Apps-Coders.github.io/box64-debs/debian
Suites: ./
Signed-By: /usr/share/keyrings/box64-archive-keyring.gpg" | tee /etc/apt/sources.list.d/box64.sources >/dev/null

apt update
apt upgrade
apt install box64-generic-arm -y
apt install python3 git -y
git clone https://github.com/GoldenMelky/pykai/
cd pykai
ln -s ./bin/mikai ./mikai
```
​
Poi installa il flow che trovi nella repo, devi modificare i blocchi USB in modo che combacino con i tuoi ID del Flipper Zero (clicca Use attached device), dopodiche prega che funzioni
