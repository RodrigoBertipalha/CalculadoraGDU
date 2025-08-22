from flask import Flask, render_template, request, send_file, flash, after_this_request
import pandas as pd
import os
import xlsxwriter
import datetime
import shutil
import time
import threading
from pathlib import Path
import gc

# Configuração para limitar uso de memória
os.environ["OPENPYXL_NOTHREADED"] = "1"  # Desativa threads do openpyxl
os.environ["OMP_NUM_THREADS"] = "1"      # Limita threads OpenMP
os.environ["NUMEXPR_MAX_THREADS"] = "1"  # Limita threads NumExpr

# Configurações pandas para usar menos memória
pd.options.mode.chained_assignment = None
# Diminuir o tamanho do pool de strings
if hasattr(pd.options.mode, 'string_storage'):
    pd.options.mode.string_storage = 'python'

try:
    # Tenta importar e iniciar o monitor de memória em produção
    from memory_profile import init_memory_monitor
    init_memory_monitor()
    print("Monitor de memória iniciado")
except Exception as e:
    print(f"Monitor de memória não disponível: {e}")
    print("Continuando sem monitoramento de memória...")

app = Flask(__name__)
app.secret_key = 'segredo'
UPLOAD_FOLDER = 'uploads'
RESULT_FOLDER = 'results'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULT_FOLDER, exist_ok=True)

# Função para limpar arquivos antigos
def clean_old_files(directory, hours=1):
    """Limpa arquivos mais antigos que o número de horas especificado"""
    now = time.time()
    cutoff_time = now - (hours * 3600)
    
    try:
        for item in os.listdir(directory):
            item_path = os.path.join(directory, item)
            # Ignora o arquivo .gitkeep
            if item == '.gitkeep':
                continue
                
            if os.path.isfile(item_path):
                # Verifica a última modificação do arquivo
                if os.path.getmtime(item_path) < cutoff_time:
                    try:
                        os.remove(item_path)
                        print(f"Arquivo removido: {item_path}")
                    except Exception as e:
                        print(f"Erro ao remover arquivo {item_path}: {e}")
    except Exception as e:
        print(f"Erro ao limpar diretório {directory}: {e}")

# Configura a limpeza automática de arquivos a cada intervalo
def schedule_cleanup(interval=3600):  # intervalo em segundos (1 hora)
    """Agenda a limpeza periódica de arquivos"""
    while True:
        clean_old_files(UPLOAD_FOLDER)
        clean_old_files(RESULT_FOLDER)
        time.sleep(interval)

# Inicia a thread de limpeza
cleanup_thread = threading.Thread(target=schedule_cleanup)
cleanup_thread.daemon = True  # Thread termina quando o programa principal termina
cleanup_thread.start()

# Base climática fixa
clima_df = pd.read_excel(
    'base_clima/temperaturas_2025.xlsx',
    sheet_name='Fonte  Estação Terra Nova Temp.'
)

# Garante que datas sejam datetime com formato brasileiro (dayfirst=True)
clima_df['data'] = pd.to_datetime(clima_df['data'], dayfirst=True)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        uploaded_files = request.files.getlist('files[]')
        col_plantio = request.form['col_plantio'].strip()
        col_sfwd = request.form['col_sfwd'].strip()
        col_pfwd = request.form['col_pfwd'].strip()

        if not uploaded_files or uploaded_files[0].filename == '':
            return render_template('index.html', 
                                  status_message='Nenhum arquivo foi selecionado.', 
                                  status_type='error')

        # Lista para armazenar nomes de arquivos processados
        processed_filenames = []
        total_erros = 0
        total_linhas_validas = 0
        total_gdu_alto = 0
        
        # Processar cada arquivo enviado
        for file in uploaded_files:
            try:
                # Armazena o nome original do arquivo
                original_filename = file.filename
                filepath = os.path.join(UPLOAD_FOLDER, original_filename)
                file.save(filepath)
                
                # Verificar tamanho do arquivo e mostrar aviso
                file_size_kb = os.path.getsize(filepath) / 1024
                print(f"Arquivo: {original_filename}, Tamanho: {file_size_kb:.2f}KB")
                
                # Definir o tamanho do chunk baseado no tamanho do arquivo
                chunk_size = 50  # Padrão para arquivos pequenos
                if file_size_kb > 200:
                    chunk_size = 25  # Arquivos médios
                if file_size_kb > 500:
                    chunk_size = 10  # Arquivos grandes
                
                # Usar o processador em chunks para arquivos grandes
                from chunk_processor import process_excel_in_chunks
                
                # Processar o arquivo em chunks
                df_result, erros_chunk, linhas_validas_chunk, gdu_alto_chunk = process_excel_in_chunks(
                    filepath, 
                    clima_df,
                    chunk_size=chunk_size,
                    col_plantio=col_plantio,
                    col_sfwd=col_sfwd,
                    col_pfwd=col_pfwd
                )
                
                erros = erros_chunk
                linhas_validas = linhas_validas_chunk
                
                # Forçar coleta de lixo após processamento
                import gc
                gc.collect()
            except Exception as e:
                print(f"Erro ao carregar o arquivo {file.filename}: {e}")
                continue
        
            # Verificar se as colunas necessárias existem no DataFrame
            # O processamento agora é feito em chunks pelo chunk_processor.py
            # Verificar se o processamento de chunks foi bem-sucedido
            if df_result.empty:
                print(f"Erro: Falha ao processar o arquivo {original_filename}")
                continue
                
            # Verificar automaticamente se a coluna PFWD existe (já feito no chunk_processor)
            incluir_pfwd_atual = col_pfwd in df_result.columns
            
            # Não precisamos mais processar linha por linha porque o chunk_processor
            # já fez todo o processamento necessário
                # O processamento linha por linha foi movido para o chunk_processor
                # Não precisamos mais desse código, pois o df_result já vem com os cálculos feitos
                
                # Verificar quantos valores de GDU acumulado estão acima do limite
                try:
                    # Calcular quantos registros têm GDU acumulado acima de 1200
                    gdu_alto = df_result[pd.to_numeric(df_result['gdu_acumulado'], errors='coerce') > 1200].shape[0]
                    gdu_pfwd_alto = 0
                    if incluir_pfwd_atual and 'gdu_acumulado_pfwd' in df_result.columns:
                        gdu_pfwd_alto = df_result[pd.to_numeric(df_result['gdu_acumulado_pfwd'], errors='coerce') > 1200].shape[0]
                    
                    arquivo_gdu_alto = gdu_alto + gdu_pfwd_alto
                except Exception as e:
                    print(f"Erro ao calcular GDU alto: {e}")
                    arquivo_gdu_alto = 0
                # Este trecho foi movido para cima no código
                total_gdu_alto += arquivo_gdu_alto
                total_erros += erros
                total_linhas_validas += linhas_validas
                    
                # Usa o nome original do arquivo para o resultado
                output_filename = original_filename
                output_path = os.path.join(RESULT_FOLDER, output_filename)
                
                # Salvar o arquivo com formatação melhorada usando XlsxWriter
                with pd.ExcelWriter(output_path, engine='xlsxwriter', mode='w') as writer:
                    # Salvar em blocos pequenos para reduzir o uso de memória
                    batch_size = 1000
                    total_rows = len(df_result)
                    
                    # Se o arquivo é grande, salvar em lotes para economizar memória
                    if total_rows > batch_size:
                        print(f"Salvando arquivo grande em lotes de {batch_size} linhas")
                        # Primeiro, salve o cabeçalho
                        df_result.iloc[0:0].to_excel(writer, index=False, sheet_name='GDU')
                        
                        # Depois salve cada lote
                        for start_row in range(0, total_rows, batch_size):
                            end_row = min(start_row + batch_size, total_rows)
                            print(f"Salvando linhas {start_row} a {end_row}")
                            if start_row == 0:
                                # Primeira vez inclui o cabeçalho
                                df_result.iloc[start_row:end_row].to_excel(writer, index=False, sheet_name='GDU')
                            else:
                                # Depois, anexar sem cabeçalho
                                df_result.iloc[start_row:end_row].to_excel(
                                    writer, index=False, sheet_name='GDU', startrow=start_row+1, header=False
                                )
                            
                            # Limpar memória após cada lote
                            gc.collect()
                    else:
                        # Para arquivos pequenos, salvar normalmente
                        df_result.to_excel(writer, index=False, sheet_name='GDU')
                    
                    # Acessar o workbook e o worksheet para formatação
                    workbook = writer.book
                    worksheet = writer.sheets['GDU']
                    
                    # Definir formatos
                    header_format = workbook.add_format({
                        'bold': True,
                        'bg_color': '#4facfe',
                        'font_color': 'white',
                        'border': 1
                    })
                    
                    # Formatar cabeçalhos
                    for col_num, value in enumerate(df_result.columns.values):
                        worksheet.write(0, col_num, value, header_format)
                        
                    # Ajustar largura das colunas - somente para as primeiras 100 colunas para economizar tempo
                    for i, col in enumerate(df_result.columns[:100]):
                        # Calcular largura baseada apenas nas primeiras 100 linhas para economizar processamento
                        sample = df_result.iloc[:100][col].astype(str) if len(df_result) > 100 else df_result[col].astype(str)
                        max_len = max(sample.map(len).max(), len(str(col))) + 2
                        worksheet.set_column(i, i, max_len)
                
                # Adicionar à lista de arquivos processados
                processed_filenames.append(output_filename)
                print(f"Arquivo {original_filename} processado com sucesso e adicionado à lista.")
                
                # Forçar coleta de lixo após processamento completo do arquivo
                gc.collect()
                
            except Exception as e:
                print(f"Erro ao finalizar o processamento do arquivo {original_filename}: {e}")
                continue

        # Determina a mensagem de status para todos os arquivos processados
        num_files = len(processed_filenames)
        print(f"Total de arquivos processados: {num_files}")
        print(f"Lista de arquivos: {processed_filenames}")
        
        if num_files == 0:
            status_message = 'Erro: nenhum arquivo foi processado.'
            status_type = 'error'
        elif total_linhas_validas == 0:
            status_message = 'Erro: nenhuma linha pôde ser calculada em nenhum arquivo.'
            status_type = 'error'
        elif total_erros > 0:
            status_message = f'Cálculo realizado com alguns erros. {total_linhas_validas} linhas processadas com sucesso, {total_erros} com erro em {num_files} arquivos.'
            # Adiciona aviso de GDU alto se necessário
            if total_gdu_alto > 0:
                status_message += f' ATENÇÃO: {total_gdu_alto} linhas com GDU acima de 1200.'
            status_type = 'warning'
        else:
            status_message = f'Cálculo realizado com sucesso! {total_linhas_validas} linhas processadas em {num_files} arquivos.'
            # Adiciona aviso de GDU alto se necessário
            if total_gdu_alto > 0:
                status_message += f' ATENÇÃO: {total_gdu_alto} linhas com GDU acima de 1200.'
            status_type = 'success'

        # Limpeza imediata dos arquivos de upload (não são mais necessários)
        try:
            for file in uploaded_files:
                original_filename = file.filename
                filepath = os.path.join(UPLOAD_FOLDER, original_filename)
                if os.path.exists(filepath):
                    os.remove(filepath)
                    print(f"Arquivo de upload removido: {filepath}")
        except Exception as e:
            print(f"Erro ao remover arquivos de upload: {e}")
            
        # Renderiza a página com o resultado e links para download
        return render_template('index.html', 
                             download_ready=True, 
                             status_message=status_message, 
                             status_type=status_type,
                             filenames=processed_filenames)

    return render_template('index.html')

@app.route('/download/<filename>')
def download(filename):
    output_path = os.path.join(RESULT_FOLDER, filename)
    
    # Verificar se o arquivo existe
    if not os.path.exists(output_path):
        flash('Arquivo não encontrado. Ele pode ter sido removido automaticamente.', 'error')
        return render_template('index.html', status_message='Arquivo não encontrado.', status_type='error')
    
    @after_this_request
    def cleanup(response):
        # Tentar excluir o arquivo após o download
        # Às vezes o arquivo pode estar em uso, então tratamos a exceção
        try:
            # Aguarda um pouco para garantir que o download foi concluído
            def remove_file():
                time.sleep(5)  # Aguarda 5 segundos
                if os.path.exists(output_path):
                    try:
                        os.remove(output_path)
                        print(f"Arquivo removido após download: {output_path}")
                    except Exception as e:
                        print(f"Erro ao remover arquivo {output_path} após download: {e}")
            
            # Inicia uma thread para remover o arquivo
            thread = threading.Thread(target=remove_file)
            thread.daemon = True
            thread.start()
        except Exception as e:
            print(f"Erro ao tentar configurar a limpeza do arquivo {output_path}: {e}")
        return response
    
    return send_file(output_path, as_attachment=True)

# Função que limpa todos os arquivos nos diretórios (exceto .gitkeep)
def clean_all_files():
    """Limpa todos os arquivos temporários nos diretórios de upload e resultados"""
    for directory in [UPLOAD_FOLDER, RESULT_FOLDER]:
        try:
            # Garante que o diretório existe antes de tentar listá-lo
            os.makedirs(directory, exist_ok=True)
            
            # Lista e remove arquivos
            for item in os.listdir(directory):
                item_path = os.path.join(directory, item)
                if os.path.isfile(item_path) and item != '.gitkeep':
                    try:
                        os.remove(item_path)
                        print(f"Arquivo removido durante inicialização: {item_path}")
                    except Exception as e:
                        print(f"Erro ao remover arquivo {item_path}: {e}")
        except Exception as e:
            print(f"Erro ao limpar diretório {directory}: {e}")

if __name__ == '__main__':
    # Limpa todos os arquivos temporários na inicialização
    clean_all_files()
    print("Aplicação inicializada! Acesse http://localhost:5000 para usar a calculadora de GDU.")
    app.run(debug=True, port=5000)
