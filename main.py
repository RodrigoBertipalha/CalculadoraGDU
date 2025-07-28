from flask import Flask, render_template, request, send_file
import pandas as pd
import os
from datetime import datetime

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
RESULT_FOLDER = 'results'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULT_FOLDER, exist_ok=True)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        file = request.files['file']
        plantio = request.form['plantio']
        florescimento = request.form['florescimento']

        filepath = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(filepath)

        df = pd.read_csv(filepath)

        # Limpeza dos dados
        df['temp_min'] = df['temp_min'].clip(lower=10)
        df['temp_max'] = df['temp_max'].clip(upper=40)

        # Conversão de datas
        df['data'] = pd.to_datetime(df['data'], dayfirst=True)
        plantio = pd.to_datetime(plantio, dayfirst=True)
        florescimento = pd.to_datetime(florescimento, dayfirst=True)

        # Filtro por intervalo
        intervalo = df[(df['data'] >= plantio) & (df['data'] <= florescimento)].copy()

        # Cálculo do GDU
        intervalo['GDU'] = ((intervalo['temp_max'] + intervalo['temp_min']) / 2) - 10
        intervalo['GDU_acumulado'] = intervalo['GDU'].cumsum()

        # Exportar .xlsx
        output_path = os.path.join(RESULT_FOLDER, 'resultado_gdu.xlsx')
        intervalo.to_excel(output_path, index=False)

        return send_file(output_path, as_attachment=True)

    return render_template('index.html')

app.run(host='0.0.0.0', port=81)
