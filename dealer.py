# Creamos la clase para el Dealer
class Dealer:
    def __init__(self):
        self.name = 'Dealer'
        self.cards = []
        self.hidden_card = "https://deckofcardsapi.com/static/img/XX.png"
        self.totals = []
        self.status = 'Active'
        self.final = 0