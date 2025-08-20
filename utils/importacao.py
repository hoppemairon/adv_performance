import pandas as pd
import os

def importar_arquivo(path):
    # Se for um arquivo enviado pelo Streamlit, ele tem atributo 'name'
    if hasattr(path, 'name'):
        ext = os.path.splitext(path.name)[1].lower()
        if ext == '.csv':
            return pd.read_csv(path)
        elif ext in ['.xls', '.xlsx']:
            return pd.read_excel(path)
        else:
            raise ValueError(f'Formato de arquivo não suportado: {ext}')
    else:
        ext = os.path.splitext(path)[1].lower()
        if ext == '.csv':
            return pd.read_csv(path)
        elif ext in ['.xls', '.xlsx']:
            return pd.read_excel(path)
        else:
            raise ValueError('Formato de arquivo não suportado: {}'.format(ext))
