# Jogo da Velha com Flask e Machine Learning – API RESTful
Teste Prático: Jogo da Velha com Flask, Identificação de Jogadores e Machine Learning

Este projeto oferece uma API RESTful para um jogo da velha com suporte a jogadores humanos e uma IA treinada para jogar contra o usuário. A API está construída utilizando o framework **Flask** em Python e integra um modelo de aprendizado de máquina (ML) para melhorar o desempenho das jogadas da IA.

## Pré-requisitos

- Python 3.x
- Pip (gerenciador de pacotes do Python)
- Flask
- Joblib (para carregar o modelo de ML)
- Bibliotecas adicionais para o treinamento do modelo (consultar seção abaixo)

## Instalação e Configuração

### 1. Clonar o repositório

Primeiro, clone este repositório para a sua máquina local:

```bash
git clone https://github.com/Davidtricolor2021/API_jogo_da_velha.git
cd API_jogo_da_velha
```
### 2. Criar um ambiente virtual
É altamente recomendado criar um ambiente virtual para o projeto para evitar conflitos de dependências:

```bash
python -m venv venv
```
Ative o ambiente virtual:
Windows:

```bash
venv\Scripts\activate
```
MacOS/Linux:

```bash
source venv/bin/activate
```
### 3. Instalar as dependências
Instale as dependências necessárias usando o pip:

```bash
pip install -r requirements.txt
```
### 4. Arquivos de Persistência
Certifique-se de que os arquivos de persistência jogadores.json e jogos.json estão presentes na raiz do projeto. Se não existirem, eles serão criados automaticamente quando você iniciar o servidor Flask e interagir com a API.

### 5. Configuração do Modelo de IA
O modelo de IA está localizado em modelos_treinamentos/modelo_treinado.joblib. Para treinar o modelo, siga as instruções abaixo (detalhadas na seção Treinamento do Modelo).

Rodando o Servidor Flask
Para iniciar o servidor Flask, execute o seguinte comando:

```bash
python main.py
```
O servidor será iniciado em http://127.0.0.1:5000/ (ou o endereço e porta configurados).

### Interagindo com a API
### 1. Registrar Jogadores
Para registrar um jogador, envie uma requisição POST para /api/jogador com os dados do jogador:

Endpoint:
Exemplo de Requisição:
```bash
POST /api/register

curl -X POST "http://localhost:5000/api/register"
```
Corpo da requisição:

```json
{
  "nome": "Jogador 1"
}
```
Resposta:

```json
{
  "jogador_id": "123"
}
```

O jogador_id é gerado automaticamente e será utilizado para interações subsequentes.

### 2. Iniciar um Jogo contra a maquina ou outro jogador
Para iniciar um jogo, envie uma requisição POST para /api/jogo com os IDs dos jogadores:

Endpoint:
Exemplo de Requisição:
```bash
POST /api/start

curl -X POST "http://localhost:5000/api/start"
```
Corpo da requisição:

```json
{
  "player_1_id": "123",
  "player_2_id": "456"
}
```
Resposta:

```json
{
  "jogo_id": "789",
  "tabuleiro": [
    ["", "", ""],
    ["", "", ""],
    ["", "", ""]
  ],
  "turno": "123"
}
```
### 3.2. Realizar uma Jogada em um jogo contra a maquina
Para realizar uma jogada, envie uma requisição POST para /api/play com o jogo_id, ID do jogador e a posição da jogada:

Endpoint:
Exemplo de Requisição:
```bash
POST /api/play

curl -X POST "http://localhost:5000/api/play"
```
Corpo da requisição:

```json
{
	  "jogo_id": "77",
    "player_id": "1",
    "linha": 0,
    "coluna": 2
}
```
Resposta:

```json
{
    "jogo_id": "77",
    "resultado": "continua",
    "tabuleiro": [
        [
            "O",
            "O",
            "X"
        ],
        [
            "X",
            "X",
            "O"
        ],
        [
            "",
            "",
            ""
        ]
    ],
    "turno": "1"
}
```
O maquina realizara a sua jogada automaticamente e voce deve jogar novamente.

### 3.2. Realizar uma Jogada em um jogo contra outro jogador
Para realizar uma jogada, envie uma requisição POST para /api/move com a posição da jogada e o ID do jogador:

Endpoint:
Exemplo de Requisição:
```bash
POST /api/move

curl -X POST "http://localhost:5000/api/move"
```
Corpo da requisição:

```json
{
  "jogo_id": "789",
  "player_id": "123",
  "posicao": [1, 1]
}
```
Resposta:

```json
{
  "tabuleiro": [
    ["", "", ""],
    ["", "X", ""],
    ["", "", ""]
  ],
  "proximo_turno": "456"
}
```
O próximo jogador será automaticamente alternado.

##### Resultado do Jogo
Se o jogo terminar, o resultado será retornado junto com o estado final do tabuleiro. Um dos seguintes cenários pode ocorrer:

Vitória:

```json
{
  "resultado": "Jogador 123 venceu!",
  "tabuleiro": [
    ["X", "O", "X"],
    ["O", "X", "O"],
    ["X", "", ""]
  ]
}
```
Empate:

```json
{
  "resultado": "Empate!",
  "tabuleiro": [
    ["X", "O", "X"],
    ["X", "O", "X"],
    ["X", "X", "O"]
  ]
}
```
### 4. Obter as estatísticas de um jogador

Endpoint:
Exemplo de Requisição:
```bash
GET /api/estatisticas-jogador/<player_id>

curl -X GET "http://localhost:5000/api/estatisticas-jogador/1"
```
Resposta de Sucesso (200):

```json
{
    "nome": "João",
    "vitorias": 10,
    "derrotas": 5,
    "empates": 2
}
```
Resposta de Erro (404 - Jogador não encontrado):

```json
{
    "erro": "Jogador não encontrado"
}
```
### 5. Listar todos os jogadores e suas estatísticas

Endpoint:
Exemplo de Requisição:
```bash
GET /api/jogadores

curl -X GET "http://localhost:5000/api/jogadores"
```
Resposta de Sucesso (200):

```json
{
    "1": {
        "nome": "João",
        "vencidas": 10,
        "perdidas": 5,
        "empatadas": 2
    },
    "2": {
        "nome": "Maria",
        "vencidas": 7,
        "perdidas": 8,
        "empatadas": 3
    }
}
```

### 6. Obter o histórico de um jogador com feedback

Endpoint:
Exemplo de Requisição:
```bash
GET /api/jogador/<player_id>/historico

curl -X GET "http://localhost:5000/api/jogador/1/historico"
```
Resposta de Sucesso (200):

```json
{
    "jogador_id": 1,
    "nome": "João",
    "historico": [
        {
            "resultado": "Vitórias",
            "quantidade": 10,
            "feedback": "Vitória merecida! Não esqueça de ajustar sua estratégia conforme o adversário muda o padrão."
        },
        {
            "resultado": "Derrotas",
            "quantidade": 5,
            "feedback": "Cada derrota é uma oportunidade de aprendizado. Priorize o centro do tabuleiro nas próximas partidas."
        },
        {
            "resultado": "Empates",
            "quantidade": 2,
            "feedback": "Bom empate! Pense em formas de forçar o oponente a cometer erros."
        }
    ]
}
```
Resposta de Erro (404 - Jogador não encontrado):

```json
{
    "erro": "Jogador não encontrado"
}
```
### 7. Obter a melhor jogada sugerida pela IA

Endpoint:
Exemplo de Requisição:
```bash
GET /api/ai-move?jogo_id=<jogo_id>

curl -X GET "http://localhost:5000/api/ai-move?jogo_id=1"
```
Resposta de Sucesso (200):

```json
{
    "melhor_jogada": {
        "x": 2,
        "y": 0
    },
    "tabuleiro": [
        ["X", "O", ""],
        ["", "X", "O"],
        ["", "", ""]
    ]
}
```
Resposta de Erro (400 - Parâmetro ausente):

```json
{
    "erro": "O parâmetro 'jogo_id' é obrigatório"
}
```
Resposta de Erro (404 - Jogo não encontrado):

```json
{
    "erro": "Jogo não encontrado"
}
```
Resposta de Erro (500 - Erro na IA):

```json
{
    "erro": "Erro ao processar a jogada: Modelo não treinado."
}
```

### Treinamento do Modelo
### 1. Conjunto de Dados Histórico
O modelo de IA foi treinado utilizando um conjunto de dados histórico de jogos anteriores, onde foram registradas as jogadas e os resultados. Este conjunto de dados está localizado em *jogos.json*.

### 2. Como Treinar o Modelo
Para treinar o modelo, você precisará do conjunto de dados de jogos anteriores. Siga os passos abaixo:

Certifique-se de que os dados históricos estão presentes no arquivo *jogos.json* com o formato adequado.
Execute o script de treinamento para gerar o modelo:

```bash
python treinamento_modelo.py
```
Este script irá treinar o modelo utilizando os dados históricos, gerar o modelo treinado e salvar o arquivo modelo_treinado.joblib.

### 3. Melhorando o Desempenho da IA
A IA pode melhorar à medida que mais jogos são registrados e alimentados ao modelo. O modelo foi desenvolvido para identificar padrões de jogadas vencedoras e evitar movimentos prejudiciais com base nos jogos passados. Quanto maior o conjunto de dados, mais precisa se torna a IA.

### Testes
Se desejar rodar testes para garantir que a API esteja funcionando corretamente, você pode usar a ferramenta Postman ou cURL para interagir com a API ou escrever testes automatizados usando o framework unittest.