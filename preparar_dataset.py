import json
import numpy as np
from sklearn.ensemble import RandomForestClassifier
import joblib

# Função para converter o JSON em X e y
def preparar_dataset(caminho_arquivo_json, caminho_modelo):
    # Carregar o modelo treinado
    modelo = joblib.load(caminho_modelo)

    with open(caminho_arquivo_json, 'r') as f:
        dados = json.load(f)

    x = []
    y = []

    for _, detalhes in dados.items():
        # Verifique se a chave 'tabuleiro' e 'turno' existem
        if 'tabuleiro' not in detalhes or 'turno' not in detalhes:
            print(f"Registro ignorado: {detalhes}")
            continue

        tabuleiro = detalhes['tabuleiro']
        turno = detalhes['turno']  # ID do jogador que fará a próxima jogada
        estado_jogo = []

        # Converter o tabuleiro para formato numérico
        for linha in tabuleiro:
            for celula in linha:
                if celula == 'X':
                    estado_jogo.append(1)
                elif celula == 'O':
                    estado_jogo.append(-1)
                else:
                    estado_jogo.append(0)

        # Usar o modelo para prever a melhor jogada
        estado_jogo_np = np.array(estado_jogo).reshape(1, -1)
        melhor_jogada = modelo.predict(estado_jogo_np)[0]

        # Adicionar o estado do tabuleiro (X) e a melhor jogada prevista (y)
        x.append(estado_jogo)
        y.append(melhor_jogada)

    return np.array(x), np.array(y)

# Chame a função para obter X e y
try:
    caminho_dataset = 'jogos.json'
    caminho_modelo_treinado = 'C:\\xampp\\htdocs\\api_jogo_da_velha\\modelos_treinamentos\\modelo_treinado.joblib'

    x, y = preparar_dataset(caminho_dataset, caminho_modelo_treinado)
    print("Entradas (x):", x)
    print("Saídas (y):", y)
except Exception as e:
    print(f"Erro ao preparar o dataset: {e}")