from flask import Flask, request, jsonify
import json
import random
import os
import joblib
import numpy as np
import logging

# Inicializando o Flask
app = Flask(__name__)

# Caminho para os arquivos de persistência
ARQUIVO_JOGADORES = 'jogadores.json'
ARQUIVO_JOGOS = 'jogos.json'

# Carregamento do modelo de Machine Learning
CAMINHO_MODELO = 'C:\\xampp\\htdocs\\api_jogo_da_velha\\modelos_treinamentos\\modelo_treinado.joblib'
modelo = joblib.load(CAMINHO_MODELO)

# Função para carregar os dados de jogadores
def carregar_jogadores():
    if os.path.exists(ARQUIVO_JOGADORES):
        with open(ARQUIVO_JOGADORES, 'r') as f:
            return json.load(f)
    return {}

# Função para salvar os dados de jogadores
def salvar_jogadores():
    with open(ARQUIVO_JOGADORES, 'w') as f:
        json.dump(jogadores, f, indent=4)

# Função para carregar os dados de jogos
def carregar_jogos():
    if os.path.exists(ARQUIVO_JOGOS):
        with open(ARQUIVO_JOGOS, 'r') as f:
            return json.load(f)
    return {}

# Função para salvar os dados de jogos
def salvar_jogos():
    with open(ARQUIVO_JOGOS, 'w') as f:
        json.dump(jogos, f, indent=4)

# Carregar jogadores e jogos ao iniciar o app
jogadores = carregar_jogadores()
jogos = carregar_jogos()

# Função para criar um tabuleiro vazio
def criar_tabuleiro():
    return [["" for _ in range(3)] for _ in range(3)]

# Função para verificar vitória
def verificar_vitoria(tabuleiro):
    for linha in tabuleiro:
        if linha[0] == linha[1] == linha[2] != "":
            return True
    for col in range(3):
        if tabuleiro[0][col] == tabuleiro[1][col] == tabuleiro[2][col] != "":
            return True
    if tabuleiro[0][0] == tabuleiro[1][1] == tabuleiro[2][2] != "":
        return True
    if tabuleiro[0][2] == tabuleiro[1][1] == tabuleiro[2][0] != "":
        return True
    return False

# Função para verificar empate
def verificar_empate(tabuleiro):
    for linha in tabuleiro:
        if "" in linha:
            return False
    return True

# Configuração básica de logging
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")

# Função para processar a jogada da máquina
def jogada_maquina(tabuleiro):
    # Obter o estado do tabuleiro como entrada para o modelo
    entrada_modelo = []
    for linha in tabuleiro:
        for celula in linha:
            if celula == "X":
                entrada_modelo.append(1)
            elif celula == "O":
                entrada_modelo.append(-1)
            else:
                entrada_modelo.append(0)

    logging.debug(f"Entrada para o modelo: {entrada_modelo}")

    # Prever posição usando o modelo
    posicao_prevista = modelo.predict([entrada_modelo])[0]
    logging.debug(f"Posição prevista pelo modelo: {posicao_prevista}")

    # Converter posição prevista para coordenadas no tabuleiro
    linha_prevista = posicao_prevista // 3
    coluna_prevista = posicao_prevista % 3
    logging.debug(f"Coordenadas previstas: linha={linha_prevista}, coluna={coluna_prevista}")

    # Verificar se a posição prevista está livre
    if tabuleiro[linha_prevista][coluna_prevista] == "":
        return linha_prevista, coluna_prevista

    # Tentar encontrar outra posição válida caso a prevista esteja ocupada
    logging.warning("Jogada prevista está ocupada, buscando nova posição válida.")
    for linha in range(3):
        for coluna in range(3):
            if tabuleiro[linha][coluna] == "":
                logging.debug(f"Posição alternativa encontrada: linha={linha}, coluna={coluna}")
                return linha, coluna

    # Retornar None se não houver posições disponíveis
    return None, None

# Rota para realizar uma jogada
@app.route('/api/play', methods=['POST'])
def play_turn():
    global jogos
    data = request.json
    jogo_id = data.get('jogo_id')
    player_id = data.get('player_id')
    linha = data.get('linha')
    coluna = data.get('coluna')

    # Carregar o estado mais recente dos jogos
    jogos = carregar_jogos()

    logging.debug(f"Dados recebidos: jogo_id={jogo_id}, player_id={player_id}, linha={linha}, coluna={coluna}")

    # Verificar se o jogo existe
    if str(jogo_id) not in jogos:
        return jsonify({"erro": "Jogo não encontrado"}), 404

    jogo = jogos[str(jogo_id)]
    tabuleiro = jogo["tabuleiro"]

    # Verificar se é o turno do jogador certo
    if jogo["turno"] != player_id:
        return jsonify({"erro": "Não é o seu turno"}), 400

    # Verificar se a posição está vazia
    if tabuleiro[linha][coluna] != "":
        return jsonify({"erro": "Posição já ocupada"}), 400

    # Registrar a jogada
    simbolo = "X" if player_id == jogo["player_1_id"] else "O"
    tabuleiro[linha][coluna] = simbolo

    logging.debug(f"Jogada registrada: simbolo={simbolo}, tabuleiro={tabuleiro}")

    # Verificar vitória ou empate
    if verificar_vitoria(tabuleiro):
        resultado = "vitória" if player_id == jogo["player_1_id"] else "derrota"
    elif verificar_empate(tabuleiro):
        resultado = "empate"
    else:
        resultado = "continua"

    # Alterar o turno para o próximo jogador ou a máquina
    if resultado == "continua":
        if player_id == jogo["player_1_id"]:
            jogo["turno"] = jogo["player_2_id"]
            if jogo["player_2_id"]:
                # Máquina realiza sua jogada
                linha_maquina, coluna_maquina = jogada_maquina(tabuleiro)
                if linha_maquina is not None and coluna_maquina is not None and tabuleiro[linha_maquina][coluna_maquina] == "":
                    tabuleiro[linha_maquina][coluna_maquina] = "O"
                    logging.debug(f"Máquina jogou: linha={linha_maquina}, coluna={coluna_maquina}, tabuleiro={tabuleiro}")

                    if verificar_vitoria(tabuleiro):
                        resultado = "derrota"
                    elif verificar_empate(tabuleiro):
                        resultado = "empate"
                    else:
                        jogo["turno"] = jogo["player_1_id"]
                else:
                    logging.error("Jogada inválida da máquina ou posição já ocupada!")
        else:
            jogo["turno"] = jogo["player_1_id"]

    # Atualizar o estado do jogo
    salvar_jogos()

    logging.debug(f"Estado atualizado: jogo_id={jogo_id}, resultado={resultado}, turno={jogo['turno']}")

    return jsonify({
        "jogo_id": jogo_id,
        "tabuleiro": tabuleiro,
        "resultado": resultado,
        "turno": jogo["turno"]
    })

# Rota para registrar um jogador
@app.route('/api/register', methods=['POST'])
def register_player():
    data = request.json
    nome = data.get('nome')
    if not nome:
        return jsonify({"erro": "Nome é obrigatório"}), 400

    player_id = len(jogadores) + 1
    jogadores[player_id] = {"nome": nome, "vencidas": 0, "perdidas": 0, "empatadas": 0}
    # Salvar os dados dos jogadores
    salvar_jogadores()

    return jsonify({"player_id": player_id, "nome": nome})

# Rota para iniciar um jogo
@app.route('/api/start', methods=['POST'])
def start_game():
    data = request.json
    player_1_id = data.get('player_1_id')
    player_2_id = data.get('player_2_id')

    # Verificar se os jogadores existem
    if str(player_1_id) not in jogadores:
        return jsonify({"erro": "Jogador 1 não encontrado"}), 404
    if str(player_2_id) not in jogadores:
        return jsonify({"erro": "Jogador 2 não encontrado"}), 404
    
    # Verificar se os IDs dos jogadores são diferentes
    if player_1_id == player_2_id:
        return jsonify({"erro": "Os jogadores devem ser diferentes"}), 400

    # Criar um novo jogo
    jogo_id = len(jogos) + 1
    tabuleiro = criar_tabuleiro()
    jogos[jogo_id] = {
        "tabuleiro": tabuleiro,
        "player_1_id": player_1_id,
        "player_2_id": player_2_id,
        "turno": player_1_id  # Inicia com o jogador 1
    }
    # Salvar os dados dos jogos
    salvar_jogos()

    return jsonify({
        "jogo_id": jogo_id,
        "tabuleiro": tabuleiro,
        "player_1_id": player_1_id,
        "player_2_id": player_2_id,
        "turno": player_1_id
    })

# Rota para realizar uma jogada
@app.route('/api/move', methods=['POST'])
def player_move():
    global jogos
    
    data = request.json
    jogo_id = data.get('jogo_id')
    player_id = data.get('player_id')
    x, y = data.get('posicao', (None, None))

    # Carregar o estado mais recente dos jogos
    jogos = carregar_jogos()

    # Verificar se o jogo existe
    if str(jogo_id) not in jogos:
        return jsonify({"erro": "Jogo não encontrado"}), 404

    # Obter informações do jogo
    jogo = jogos[str(jogo_id)]
    tabuleiro = jogo["tabuleiro"]

    # Verificar se é a vez do jogador
    if player_id != jogo["turno"]:
        return jsonify({"erro": "Não é a sua vez"}), 400

    # Verificar se a posição é válida
    if x is None or y is None or not (0 <= x < 3 and 0 <= y < 3):
        return jsonify({"erro": "Posição inválida"}), 400
    if tabuleiro[x][y] != "":
        return jsonify({"erro": "Posição já ocupada"}), 400

    # Realizar a jogada
    jogador_simbolo = "X" if player_id == jogo["player_1_id"] else "O"
    tabuleiro[x][y] = jogador_simbolo

    # Verificar condições de vitória ou empate
    if verificar_vitoria(tabuleiro):
        jogadores[str(player_id)]["vencidas"] += 1  # Atualiza vitórias
        outro_jogador = jogo["player_2_id"] if player_id == jogo["player_1_id"] else jogo["player_1_id"]
        jogadores[str(outro_jogador)]["perdidas"] += 1  # Atualiza derrotas
        # Salvar os dados dos jogadores e jogos
        salvar_jogadores()
        salvar_jogos()  # Salvar o estado do jogo após vitória
        return jsonify({"resultado": f"Jogador {player_id} venceu!", "tabuleiro": tabuleiro})

    if verificar_empate(tabuleiro):
        jogadores[str(jogo["player_1_id"])]["empatadas"] += 1
        jogadores[str(jogo["player_2_id"])]["empatadas"] += 1
        # Salvar os dados dos jogadores e jogos
        salvar_jogadores()
        salvar_jogos()  # Salvar o estado do jogo após empate
        return jsonify({"resultado": "Empate!", "tabuleiro": tabuleiro})

    # Alternar turno para o próximo jogador
    jogo["turno"] = jogo["player_2_id"] if player_id == jogo["player_1_id"] else jogo["player_1_id"]

    # Salvar os dados dos jogos após a jogada
    salvar_jogos()

    return jsonify({
        "tabuleiro": tabuleiro,
        "proximo_turno": jogo["turno"]
    })

# Rota que retorna as estatísticas do jogador (de acordo com o ID), como vitórias, derrotas e empates.
@app.route('/api/estatisticas-jogador/<player_id>', methods=['GET'])
def estatisticas_jogador(player_id):
    try:
        player_id = int(player_id)  
    except ValueError:
        return jsonify({"erro": "ID do jogador inválido"}), 400

    jogador = jogadores.get(str(player_id))
    if not jogador:
        return jsonify({"erro": "Jogador não encontrado"}), 404

    estatisticas = {
        "nome": jogador.get("nome", "Desconhecido"),
        "vitorias": jogador.get("vencidas", 0),
        "derrotas": jogador.get("perdidas", 0),
        "empates": jogador.get("empatadas", 0)
    }
    # Usando json.dumps para garantir que a ordem não seja alterada
    response = json.dumps(estatisticas, indent=4)
    return app.response_class(response, mimetype='application/json')

# Rota para listar todos os jogadores e suas estatisticas como vitórias, derrotas e empates.
@app.route('/api/jogadores', methods=['GET'])
def list_jogadores():
    response = json.dumps(jogadores, indent=4)
    return app.response_class(response, mimetype='application/json')

# Rota para listar todos os jogos e seu historico de jogadas
@app.route('/api/jogos', methods=['GET'])
def list_jogos():
    response = json.dumps(jogos, indent=4)
    return app.response_class(response, mimetype='application/json')

# Listas de mensagens de feedback
mensagens_vitorias = [
    "Parabéns! Continue usando estratégias que bloqueiam seu oponente.",
    "Ótimo trabalho! Sua estratégia está impecável.",
    "Vitória merecida! Não esqueça de ajustar sua estratégia conforme o adversário muda o padrão.",
    "Você mostrou domínio total do tabuleiro. Continue criando cenários de vitória múltipla.",
    "Excelente jogo! Suas habilidades de bloqueio e ataque estão bem afiadas."
]

mensagens_derrotas = [
    "Não desista! Tente antecipar as jogadas do seu oponente.",
    "Cada derrota é uma oportunidade de aprendizado. Priorize o centro do tabuleiro nas próximas partidas.",
    "Você chegou perto! Pense em formas de criar mais de uma linha de ataque.",
    "Não foi dessa vez, mas lembre-se: bloqueie o adversário com duas marcas alinhadas.",
    "Perder faz parte do processo. Experimente variar suas jogadas para surpreender o oponente."
]

mensagens_empates = [
    "Bom empate! Pense em formas de forçar o oponente a cometer erros.",
    "Empate sólido! Trabalhe em estratégias para transformar empates em vitórias.",
    "Boa defesa! Busque criar múltiplas possibilidades de vitória.",
    "Um empate é melhor que uma derrota! Continue aprimorando suas jogadas.",
    "Você conseguiu neutralizar o oponente! Tente ser mais ofensivo para garantir a vitória."
]

# Rota para obter histórico do jogador com feedback
@app.route('/api/jogador/<player_id>/historico', methods=['GET'])
def historico_jogador(player_id):
    try:
        player_id = int(player_id)  
    except ValueError:
        return jsonify({"erro": "ID do jogador inválido"}), 400

    jogador = jogadores.get(str(player_id))
    if not jogador:
        return jsonify({"erro": "Jogador não encontrado"}), 404

    historico = []

    # Gerar o histórico com feedbacks
    total_jogos = jogador["vencidas"] + jogador["perdidas"] + jogador["empatadas"]

    if total_jogos > 0:
        if jogador["vencidas"] > 0:
            historico.append({
                "resultado": "Vitórias",
                "quantidade": jogador["vencidas"],
                "feedback": random.choice(mensagens_vitorias)
            })

        if jogador["perdidas"] > 0:
            historico.append({
                "resultado": "Derrotas",
                "quantidade": jogador["perdidas"],
                "feedback": random.choice(mensagens_derrotas)
            })

        if jogador["empatadas"] > 0:
            historico.append({
                "resultado": "Empates",
                "quantidade": jogador["empatadas"],
                "feedback": random.choice(mensagens_empates)
            })
    else:
        historico.append({
            "resultado": "Nenhum jogo registrado",
            "feedback": "Comece a jogar para receber feedbacks e melhorar suas estratégias!"
        })

    # Usando json.dumps para garantir que a ordem não seja alterada
    resposta = json.dumps({
        "jogador_id": player_id,
        "nome": jogador.get("nome", "Jogador"),
        "historico": historico
    }, indent=4)

    return app.response_class(resposta, mimetype='application/json')

# Rota para sugerir a próxima jogada com base no modelo de Machine Learning.
@app.route('/api/ai-move', methods=['GET'])
def ai_move():
    # Obter o ID do jogo dos parâmetros da URL
    jogo_id = request.args.get('jogo_id')

    # Validar se o parâmetro 'jogo_id' foi fornecido
    if not jogo_id:
        return jsonify({"erro": "O parâmetro 'jogo_id' é obrigatório"}), 400
    
    # Carregar os jogos antes de manipular
    jogos = carregar_jogos()

    # Verificar se o jogo existe no dicionário 'jogos'
    if str(jogo_id) not in jogos:
        return jsonify({"erro": "Jogo não encontrado"}), 404

    # Obter o estado do jogo
    jogo = jogos[str(jogo_id)]
    tabuleiro = jogo["tabuleiro"]

    # Transformar o tabuleiro para um formato numérico esperado pelo modelo
    tabuleiro_numerico = [
        [1 if x == 'X' else -1 if x == 'O' else 0 for x in linha]
        for linha in tabuleiro
    ]
    # Preparar a entrada para o modelo
    entrada = np.array(tabuleiro_numerico).flatten().reshape(1, -1)

    try:
        melhor_jogada = modelo.predict(entrada)
        indice_melhor_jogada = int(melhor_jogada[0])

        # Verificar se a posição sugerida está vazia
        if tabuleiro_numerico[indice_melhor_jogada // 3][indice_melhor_jogada % 3] != 0:
            # Caso a posição sugerida seja inválida, procurar a próxima posição vazia
            for i in range(9):
                if tabuleiro_numerico[i // 3][i % 3] == 0:
                    indice_melhor_jogada = i
                    break
        # Converter o índice da melhor jogada para coordenadas (x, y)
        x, y = divmod(indice_melhor_jogada, 3)

        # Retornar a melhor jogada sugerida
        return jsonify({
            "melhor_jogada": {"x": x, "y": y},
            "tabuleiro": tabuleiro
        })

    except Exception as e:
        # Retornar erro caso algo dê errado durante a previsão
        return jsonify({"erro": f"Erro ao processar a jogada: {str(e)}"}), 500
    
# Rota principal
@app.route('/')
def home():
    return "Bem-vindo a API do Jogo da Velha!"

# Inicializar o servidor
if __name__ == '__main__':
    app.run(debug=True)