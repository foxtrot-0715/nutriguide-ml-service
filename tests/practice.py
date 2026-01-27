class Car:
    def __init__(self, brand, fuel):
        self.brand = brand  # Публичное поле (все видят)
        self.__fuel = fuel  # ПРИВАТНОЕ поле (инкапсуляция - "бак под замком")

    def drive(self, distance):
        # Расход: 1 литр на 1 км (для простоты)
        if self.__fuel >= distance:
            self.__fuel -= distance
            print(f"{self.brand} проехала {distance} км. Топлива осталось: {self.__fuel}")
        else: 
            print(f"у {self.brand} недостаточно топлива! Нужно заправиться.")

    def get_fuel_level(self):
        """Метод, чтобы безопасно узнать остаток топлива"""
        return self.__fuel
    
# Проверяем в деле:
my_car = Car("Toyota", 50)
my_car.drive(20)  # Сработает
my_car.drive(40)  # Напишет, что топлива мало

# Попробуй "взломать" машину:
# print(my_car.__fuel)  # <- Это вызовет ошибку! Мы защитили данные.
print(f"Текущий уровень: {my_car.get_fuel_level()}")

class Wallet:
    def __init__(self, initial_balance):
        self.__balance = initial_balance  # Скрываем баланс

    def top_up(self, amount):
        # Добавь логику пополнения здесь
        self.__balance += amount
        pass

    def get_balance(self):
        # Верни значение баланса здесь
        return self.__balance
        pass

    def spend(self, amount):
            if 0 < amount <= self.__balance:
                self.__balance -= amount
                return True
            return False

# Создаем кошелек
my_wallet = Wallet(1000)
# Пополняем
my_wallet.top_up(500)
# Проверяем
print(my_wallet.get_balance())

success = my_wallet.spend(2000) 
print(f"Покупка прошла? {success}")