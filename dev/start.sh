#!/bin/bash

# prendi la directory dello script
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR" || exit 1  # entra in quella directory

# elegant print command
print_info() {
    echo "[i] $1"
}

RELOAD_CODE=3
ENV_DIR="venv"

if [ ! -d "$ENV_DIR" ]; then
    print_info "Creazione ambiente virtuale"
    python3 -m venv "$ENV_DIR"
fi

source "$ENV_DIR/bin/activate"
print_info "Ambiente virtuale attivato"

which python
which pip
python --version
pip --version


if [ -f "requirements.txt" ]; then
    print_info "Controllo dipendenze"
    while read package; do
        pkg_name=$(echo "$package" | cut -d'=' -f1)
        if ! pip show "$pkg_name" > /dev/null 2>&1; then
            print_info "Installazione di $package"
            pip install "$package"
        else
            print_info "$pkg_name è già installato"
        fi
    done < requirements.txt
fi

print_info "Avvio del BOT (DEVELOPMENT VERSION)"

while true; do
    python3 bot.py
    EXIT_CODE=$?
    if [ $EXIT_CODE -eq $RELOAD_CODE ]; then
        print_info "Reload del BOT"
        sleep 1
    else
        print_info "Chiusura del BOT con codice $EXIT_CODE"
        break
    fi
done
