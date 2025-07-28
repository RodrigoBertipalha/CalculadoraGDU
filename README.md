# 🌾 Calculadora de GDU

Sistema web para cálculo de Graus-Dia de Crescimento (GDU) em culturas agrícolas baseado em dados climáticos e datas de campo.

## ✨ Visão Geral

A Calculadora de GDU é uma aplicação web desenvolvida em Python com Flask, que permite ao usuário enviar um arquivo Excel (.xlsx) com dados de plantio e florescimento, faz o cálculo dos GDU acumulados entre as datas indicadas, e retorna um arquivo processado pronto para download. O cálculo utiliza uma base climática fixa para o ano de 2025.

---

## 🚀 Funcionalidades

- **Upload de Excel:** Envie sua planilha de dados de campo (.xlsx).
- **Configuração dinâmica:** Defina os nomes das colunas de Data de Plantio, Florescimento Fêmea (SFWD) e, opcionalmente, Florescimento Macho (PFWD) via interface.
- **Cálculo automático:** O sistema calcula dias e GDU acumulado entre plantio e florescimento para cada linha.
- **Suporte a dois tipos de florescimento:** Calcule para SFWD (obrigatório) e PFWD (opcional).
- **Mensagens detalhadas:** Feedback visual sobre o sucesso ou erros no processamento.
- **Download do resultado:** Baixe imediatamente a planilha processada.

---

## 🖥️ Como Usar

1. **Rode o projeto:**
   - Instale as dependências (`poetry install` ou `pip install -r requirements.txt`).
   - Certifique-se de ter o arquivo de base climática em `base_clima/temperaturas_2025.xlsx`.
   - Execute:  
     ```bash
     gunicorn --bind 0.0.0.0:5000 main:app
     ```
     ou simplesmente:
     ```bash
     python main.py
     ```

2. **No navegador:**
   - Acesse `http://localhost:5000`.
   - Clique em **Configurar Colunas** para ajustar os nomes das colunas conforme sua planilha.
   - Faça upload do seu arquivo `.xlsx`.
   - Marque ou desmarque a opção de cálculo para PFWD conforme desejar.
   - Clique em **Calcular GDU**.
   - Baixe o arquivo processado.

---

## 📁 Estrutura do Projeto

```
CalculadoraGDU/
│
├── main.py                # Backend Flask com lógica do processamento
├── templates/
│   └── index.html         # Interface web responsiva
├── base_clima/
│   └── temperaturas_2025.xlsx  # Planilha climática fixa
├── uploads/               # Arquivos enviados pelo usuário
├── results/               # Arquivos processados prontos para download
├── .gitignore
├── pyproject.toml
├── poetry.lock
└── .replit
```

---

## 📊 Como funciona o cálculo

- O sistema lê as datas de plantio e florescimento do seu arquivo.
- Para cada linha:
  - Calcula a soma de GDU diária entre as datas usando a base climática (GDU = média das temperaturas mín. e máx. - 10°C).
  - Retorna também o número de dias entre as datas.
- Se optar, calcula também para a data de florescimento macho (PFWD).

---

## ⚠️ Observações

- O nome das colunas deve coincidir exatamente com o configurado na interface.
- Aceita apenas arquivos Excel `.xlsx`.
- O sistema usa uma base climática fixa para o ano de 2025 (pode ser adaptado para outras bases).
- O arquivo processado mantém o mesmo nome do arquivo enviado.

---

## 🛠️ Tecnologias Utilizadas

- Python 3.11
- Flask
- pandas, openpyxl
- HTML, CSS (interface moderna)
- gunicorn (produção)

---

## 📄 Licença

Este projeto é open-source. Modifique e utilize conforme desejar!

---

## 🤝 Colabore

Sugestões e melhorias são bem-vindas! Abra uma issue ou envie um pull request.
