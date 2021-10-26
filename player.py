# Creamos la clase para el jugador

class Player:
    def __init__(self):
        self.name = self.set_name()
        self.balance = 1000
        self.cards = []
        self.bets = []
        self.status = []
        self.veredict = []
        self.totals = []

    def set_name(self):
        name = input('Ingresa tu nombre: ')
        return name

    def bet(self):
        print(
            f"Tu balance actual es de {self.balance}. Ingresa tu apuesta, recuerda que tiene que ser un número entero")
        while True:
            try:
                bet = int(input('Apuesta: '))
                if bet <= self.balance:
                    self.bets.append(bet)
                    self.balance -= bet
                    break
                else:
                    print("No puedes apostar más de lo que tienes en tu balance. Intenta una apuesta menor.")

            except ValueError:
                print("No ingresaste un número intentalo de nuevo.")