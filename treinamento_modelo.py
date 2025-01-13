from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import joblib
from preparar_dataset import *

# Dividindo os dados em treino e teste
x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=42)

# Treinando o modelo
modelo = RandomForestClassifier(n_estimators=100, random_state=42)
modelo.fit(x_train, y_train)

# Avaliando o modelo
y_pred = modelo.predict(x_test)
print(f"Acurácia no conjunto de teste: {accuracy_score(y_test, y_pred) * 100:.2f}%")

# Salvando o modelo treinado
joblib.dump(modelo, 'C:\\xampp\\htdocs\\api_jogo_da_velha\\modelos_treinamentos\\modelo_treinado.joblib')
print("Modelo salvo como 'modelo_treinado.joblib'")