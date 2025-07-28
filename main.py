from flask import Flask, render_template, request, send_file, flash
import pandas as pd
import os

app = Flask(__name__)
app.secret_key = 'segredo'
UPLOAD_FOLDER = 'uploads'
RESULT_FOLDER = 'results'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULT_FOLDER, exist_ok=True)

# Base climática fixa
clima_df = pd.read_excel(
    'base_clima/temperaturas_2025.xlsx',
    sheet_name='Fonte  Estação Terra Nova Temp.'
)

# Garante que datas sejam datetime
clima_df['data'] = pd.to_datetime(clima_df['data'])

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        file = request.files['file']
        col_plantio = request.form['col_plantio'].strip()
        col_sfwd = request.form['col_sfwd'].strip()
        col_pfwd = request.form['col_pfwd'].strip()
        incluir_pfwd = 'incluir_pfwd' in request.form

        # Armazena o nome original do arquivo
        original_filename = file.filename
        filepath = os.path.join(UPLOAD_FOLDER, original_filename)
        file.save(filepath)

        df = pd.read_excel(filepath)
        df_result = df.copy()
        erros = 0
        linhas_validas = 0

        for i, row in df.iterrows():
            try:
                data_plantio = pd.to_datetime(row[col_plantio], dayfirst=True, errors='coerce')
                data_sfwd = pd.to_datetime(row[col_sfwd], dayfirst=True, errors='coerce')

                # Formata as datas originais para dd/mm/aaaa
                if not pd.isna(data_plantio):
                    df_result.at[i, col_plantio] = data_plantio.strftime('%d/%m/%Y')
                if not pd.isna(data_sfwd):
                    df_result.at[i, col_sfwd] = data_sfwd.strftime('%d/%m/%Y')

                if pd.isna(data_plantio) or pd.isna(data_sfwd) or str(data_plantio).upper() == "N/A" or str(data_sfwd).upper() == "N/A":
                    df_result.at[i, 'dias'] = ''
                    df_result.at[i, 'gdu_acumulado'] = ''
                    erros += 1
                else:
                    intervalo = clima_df[(clima_df['data'] > data_plantio) & (clima_df['data'] <= data_sfwd)].copy()
                    intervalo['GDU'] = ((intervalo['temp_min'] + intervalo['temp_max']) / 2) - 10
                    gdu_acumulado = intervalo['GDU'].sum()
                    dias = (data_sfwd - data_plantio).days

                    df_result.at[i, 'dias'] = dias
                    df_result.at[i, 'gdu_acumulado'] = round(gdu_acumulado, 2)
                    linhas_validas += 1

                if incluir_pfwd:
                    data_pfwd = pd.to_datetime(row[col_pfwd], dayfirst=True, errors='coerce')
                    
                    # Formata a data PFWD
                    if not pd.isna(data_pfwd):
                        df_result.at[i, col_pfwd] = data_pfwd.strftime('%d/%m/%Y')

                    if pd.isna(data_pfwd) or str(data_pfwd).upper() == "N/A":
                        df_result.at[i, 'dias_pfwd'] = ''
                        df_result.at[i, 'gdu_acumulado_pfwd'] = ''
                        erros += 1
                    else:
                        intervalo_pfwd = clima_df[(clima_df['data'] > data_plantio) & (clima_df['data'] <= data_pfwd)].copy()
                        intervalo_pfwd['GDU'] = ((intervalo_pfwd['temp_min'] + intervalo_pfwd['temp_max']) / 2) - 10
                        gdu_pfwd = intervalo_pfwd['GDU'].sum()
                        dias_pfwd = (data_pfwd - data_plantio).days

                        df_result.at[i, 'dias_pfwd'] = dias_pfwd
                        df_result.at[i, 'gdu_acumulado_pfwd'] = round(gdu_pfwd, 2)
                        linhas_validas += 1

            except Exception:
                df_result.at[i, 'dias'] = ''
                df_result.at[i, 'gdu_acumulado'] = ''
                if incluir_pfwd:
                    df_result.at[i, 'dias_pfwd'] = ''
                    df_result.at[i, 'gdu_acumulado_pfwd'] = ''
                erros += 1

        # Usa o nome original do arquivo para o resultado
        output_filename = original_filename
        output_path = os.path.join(RESULT_FOLDER, output_filename)
        df_result.to_excel(output_path, index=False)

        # Determina a mensagem de status
        if linhas_validas == 0:
            status_message = 'Erro: nenhuma linha pôde ser calculada.'
            status_type = 'error'
        elif erros > 0:
            status_message = f'Cálculo realizado com alguns erros. {linhas_validas} linhas processadas com sucesso, {erros} com erro.'
            status_type = 'warning'
        else:
            status_message = f'Cálculo realizado com sucesso! {linhas_validas} linhas processadas.'
            status_type = 'success'

        # Renderiza a página com o resultado e link para download
        return render_template('index.html', 
                             download_ready=True, 
                             status_message=status_message, 
                             status_type=status_type,
                             filename=output_filename)

    return render_template('index.html')

@app.route('/download/<filename>')
def download(filename):
    output_path = os.path.join(RESULT_FOLDER, filename)
    return send_file(output_path, as_attachment=True)
