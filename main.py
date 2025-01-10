from flask import Flask, request, jsonify

# Inicializando o Flask
app = Flask(__name__)

# Dados em memória (simulações para jogadores e jogos)
jogadores = {}
jogos = {}

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

# Rota para registrar um jogador
@app.route('/api/register', methods=['POST'])
def register_player():
    data = request.json
    nome = data.get('nome')
    if not nome:
        return jsonify({"erro": "Nome é obrigatório"}), 400

    player_id = len(jogadores) + 1
    jogadores[player_id] = {"nome": nome, "vencidas": 0, "perdidas": 0, "empatadas": 0}
    return jsonify({"player_id": player_id})

# Rota para iniciar um jogo
@app.route('/api/start', methods=['POST'])
def start_game():
    data = request.json
    player_1_id = data.get('player_1_id')
    player_2_id = data.get('player_2_id')

    # Verificar se os jogadores existem
    if player_1_id not in jogadores:
        return jsonify({"erro": "Jogador 1 não encontrado"}), 404
    if player_2_id not in jogadores:
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
    data = request.json
    jogo_id = data.get('jogo_id')
    player_id = data.get('player_id')
    x, y = data.get('posicao', (None, None))

    # Verificar se o jogo existe
    if jogo_id not in jogos:
        return jsonify({"erro": "Jogo não encontrado"}), 404

    # Obter informações do jogo
    jogo = jogos[jogo_id]
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
        return jsonify({"resultado": f"Jogador {player_id} venceu!", "tabuleiro": tabuleiro})
    if verificar_empate(tabuleiro):
        return jsonify({"resultado": "Empate!", "tabuleiro": tabuleiro})

    # Alternar turno para o próximo jogador
    jogo["turno"] = jogo["player_2_id"] if player_id == jogo["player_1_id"] else jogo["player_1_id"]

    return jsonify({
        "tabuleiro": tabuleiro,
        "proximo_turno": jogo["turno"]
    })

# Rota para listar todos os jogadores
@app.route('/api/jogadores', methods=['GET'])
def list_jogadores():
    return jsonify(jogadores)

# Rota para listar todos os jogos
@app.route('/api/jogos', methods=['GET'])
def list_jogos():
    return jsonify(jogos)

# Rota principal
@app.route('/')
def home():
    return "Bem-vindo a API do Jogo da Velha!"

# Inicializar o servidor
if __name__ == '__main__':
    app.run(debug=True)