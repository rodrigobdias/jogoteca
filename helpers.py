import os
from jogoteca import app

def recupera_imagem(id):
    for nome_arquivo in os.listdir(app.config['UPLOAD_PATH']):
        if '{0}{1}'.format('capa_', id) in nome_arquivo:
            return nome_arquivo

def deleta_arquivo(id):
    arquivo = recupera_imagem(id)
    if arquivo is not None:
        os.remove(os.path.join(app.config['UPLOAD_PATH'], arquivo))