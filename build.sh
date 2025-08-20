#!/usr/bin/env bash

# Exit on error
set -o errexit

# Upgrade pip
pip install --upgrade pip

# Install dependencies from requirements.txt
pip install -r requirements.txt

# Garantir que xlsxwriter seja instalado (como precaução extra)
pip install xlsxwriter

# Imprimir as dependências instaladas para verificação
pip list
