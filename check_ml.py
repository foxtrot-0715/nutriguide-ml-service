import joblib

# Путь к модели
model = joblib.load('app/models/food_model.joblib')

# Проверяем на чем-нибудь вкусном
test_foods = ["Борщ", "Куриная грудка", "Пицца Маргарита"]

for food in test_foods:
    prediction = model.predict([food.lower()])[0]
    print(f"--- {food} ---")
    print(f"Белки: {prediction[0]:.1f}г, Жиры: {prediction[1]:.1f}г, Углеводы: {prediction[2]:.1f}г, Калории: {int(prediction[3])}")
