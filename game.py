from requests import request
import math
from cards import Cartas
from player import Player
from dealer import Dealer


# Creamos la clase para el juego (este es el cerebro del juego)

class Game:
    def __init__(self):
        self.player = Player()
        self.dealer = Dealer()
        self.card_images = Cartas()
        self.deck = self.initialize_deck()
        self.cards_remaining = 0
        self.turn = 'player'
        self.deal_cards()
        # self.print_game()

    # Creamos método para inicializar y revolver el deck de cartas haciendo una llamada al
    # API Deck of Cards y obtenemos el "Deck_id"
    def initialize_deck(self):
        cards = 'https://deckofcardsapi.com/api/deck/new/shuffle/?deck_count=6'
        response = request('GET', cards).json()
        return response['deck_id']

    # Creamos el método para tomar una carta de manera aleatoria haciendo uso de nuestro "deck_id" (almacenado en self.deck)
    # y haciendo otra llamada a otro endpoint del API Deck of Cards.
    # De la respuesta del API, tomamos la imagen, el valor, el código y el número de cartas restantes en el deck
    def draw(self):
        draw = f'https://deckofcardsapi.com/api/deck/{self.deck}/draw/?count=1'
        drawn_card = request('GET', draw).json()
        img = drawn_card['cards'][0]['images']['png']
        value = drawn_card['cards'][0]['value']
        code = drawn_card['cards'][0]['code']
        self.cards_remaining = drawn_card['remaining']
        return [img, value, code]

    # Creamos el método para repartir las cartas de manera inicial (una al jugador, una al dealer, una al jugador y una al dealer)
    # Dado que llamaremos esta función cada vez que se finalice una partida, comenzamos por reestablecer las variables de nuestras instancias de Player y Dealer
    # En caso que el jugado quede sin balance, se le pregunta si quiere jugar de nuevo y en caso de afirmativo se crea una nueva instancia del juevo
    def deal_cards(self):
        self.player.cards = []
        self.player.bets = []
        self.dealer.cards = []
        self.player.status = []
        self.player.totals = [[]]
        self.player.veredict = [[]]
        self.dealer.totals = [[]]
        self.dealer.status = 'Active'
        self.dealer.final = 0
        self.turn = 'player'
        if self.player.balance > 0:
            self.player.bet()
            self.player.cards.append([self.draw()])
            self.dealer.cards.append([self.draw()])
            self.player.cards[0].append(self.draw())
            self.dealer.cards[0].append(self.draw())
            self.player.status.append('Active')
            # self.player.totals.append([])
            # self.dealer.totals.append([])
            self.print_game()
            self.initial_bj_evaluation()
        else:
            resp = input('Ya no tienes balance, deseas comenzar un juego nuevo? (s) Sí, (n) No')
            if resp == 's':
                Game.__init__(self)

    # Creamos método para realizar los cálculos de suma de cartas en cada mano
    def hand_total(self, who):
        for i in range(0, len(who.cards)):
            hand = who.cards[i]
            hand_values = [card[1] for card in hand]
            total1 = 0
            total2 = 0
            for value in hand_values:
                if value == 'ACE':
                    total1 += 11
                    total2 += 1
                elif value == 'KING' or value == 'QUEEN' or value == 'JACK':
                    total1 += 10
                    total2 += 10
                else:
                    total1 += int(value)
                    total2 += int(value)
            if len(hand_values) == 2 and total1 == 21:
                total1 = 218
                total2 = 218
            ace_count = hand_values.count('ACE')
            if ace_count > 1 and total1 > 21 and len(hand_values) > 2:
                for i in range(ace_count):
                    while total1 > 21:
                        total1 -= 10
                        total2 = total1 + 10
            who.totals[i] = [total1, total2]

    # Creamos método para revisar si de un inicio el jugado o dealer tienen BlackJack
    def initial_bj_evaluation(self):
        self.hand_total(self.player)
        self.hand_total(self.dealer)
        if 218 in self.player.totals[0]:
            self.player.balance += self.player.bets[0] + math.floor(self.player.bets[0] * 3 / 2)
            self.player.veredict[0] = "BLACKJACK! YOU WIN! 3:2"
            self.player.status[0] = 'Inactive'
            return self.deal_cards()
        elif 218 in self.dealer.totals[0]:
            self.turn = 'Dealer'
            self.player.veredict[0] = "DEALER BLACKJACK - YOU LOSE!"
            self.player.status[0] = 'Inactive'
            self.print_game()
            return self.deal_cards()
        else:
            return self.player_action()

    # Creamos método para ofrecer al jugado la decisión sobre su juego con base en sus cartas, apuesta y balance.
    def player_action(self):
        for i in range(len(self.player.cards)):
            while self.player.status[i] == 'Active':
                if len(self.player.cards[i]) == 2 and self.player.cards[i][0][1] == self.player.cards[i][1][
                    1] and self.player.balance >= self.player.bets[i]:
                    action = input(
                        f'Ingresa tu acción JUEGO {i + 1} - (s) Split, (d) Double Down, (n) Hit - New Card, (h) Hold or Stand\n')
                    if action == 's':
                        return self.split(i)
                    if action == 'd':
                        return self.double_down(i)
                    if action == 'n':
                        return self.new_card(i)
                    if action == 'h':
                        self.player.status[i] = 'Inactive'
                        self.player.veredict.insert(i, "N/A")
                elif len(self.player.cards[i]) == 2 and self.player.balance >= self.player.bets[i]:
                    action = input(
                        f'Ingresa tu acción JUEGO {i + 1} - (d) Double Down, (n) Hit - New Card, (h) Hold or Stand\n')
                    if action == 'd':
                        return self.double_down(i)
                    if action == 'n':
                        return self.new_card(i)
                    if action == 'h':
                        self.player.status[i] = 'Inactive'
                        self.player.veredict.insert(i, "N/A")
                else:
                    action = input(f'Ingresa tu acción JUEGO {i + 1} - (n) Hit - New Card, (h) Hold or Stand\n')
                    if action == 'n':
                        return self.new_card(i)
                    if action == 'h':
                        self.player.status[i] = 'Inactive'
                        self.player.veredict.insert(i, "N/A")
        self.turn = 'Dealer'
        self.dealer_action()

    # Creamos método para la finalización de la mano del dealer, asegurádonos que se reparta cartas hasta que mínimo este en 17
    def dealer_action(self):
        if 'Active' not in self.player.status and self.player.totals[len(self.player.totals) - 1][0] > 21:
            self.print_game()
            return self.deal_cards()
        else:
            while self.dealer.status == 'Active':
                self.hand_total(self.dealer)
                self.print_game()
                if int(self.dealer.totals[0][0]) > 16 and int(self.dealer.totals[0][1]) > 16:
                    self.dealer.status = 'Inactive'
                    self.dealer.final = max(self.dealer.totals[0][0], self.dealer.totals[0][1])
                else:
                    self.dealer.cards[0].append(self.draw())
            return self.final_evaluation()

    # Creamos método para determinar ganador entre dealer y jugador y actualizar el balance con base en ganancias
    def final_evaluation(self):
        for cards in self.player.cards:
            i = self.player.cards.index(cards)
            if self.player.veredict[i] == 'N/A':
                player_final = max(int(self.player.totals[i][0]), int(self.player.totals[i][0]))
                if player_final > int(self.dealer.final) or int(self.dealer.final) > 21:
                    self.player.balance += self.player.bets[i] * 2
                    self.player.veredict[i] = 'Win'
                if player_final == int(self.dealer.final):
                    self.player.balance += self.player.bets[i]
                    self.player.veredict[i] = "Push"
                if player_final < int(self.dealer.final):
                    self.player.veredict[i] = "Lose"
        return self.deal_cards()

    # Creamos método para manejar el caso del Split en caso que el jugado desee hacerlo si tiene un par de mano
    def split(self, index):
        self.player.bets.insert(index, self.player.bets[index])
        self.player.balance -= self.player.bets[index]
        original1 = self.player.cards[index][0]
        original2 = self.player.cards[index][1]
        self.player.cards[index] = [original1, self.draw()]
        self.player.cards.append([original2, self.draw()])
        self.player.veredict.append([])
        self.player.status.append('Active')
        self.player.totals.append([])
        self.hand_total(self.player)
        if self.player.totals[index] == '21 - BLACKJACK!':
            self.player.balance += self.player.bets[index] + math.floor(self.player.bets[index] * 3 / 2)
            self.player.status[index] = 'Inactive'
            self.player.veredict[index] = "BLACKJACK! YOU WIN! 3:2"
        elif self.player.totals[index + 1] == '21 - BLACKJACK!':
            self.player.balance += self.player.bets[index + 1] + math.floor(self.player.bets[index + 1] * 3 / 2)
            self.player.status[index + 1] = 'Inactive'
            self.player.veredict[index + 1] = "BLACKJACK! YOU WIN! 3:2"
        self.print_game()
        self.player_action()

    # Creamos método para manejar el caso de doblar la apuesta
    def double_down(self, index):
        self.player.balance -= self.player.bets[index]
        self.player.bets[index] += self.player.bets[index]
        hand = self.player.cards[index].append(self.draw())
        self.print_game()
        self.hand_total(self.player)
        self.player.status[index] = 'Inactive'
        if self.player.totals[index][0] > 21 and self.player.totals[index][1] > 21:
            self.player.veredict[index] = 'Bust! - YOU LOSE'
        else:
            self.player.veredict[index] = 'N/A'
        return self.player_action()

    # Creamos método para manejar el caso en donde el jugado desee una carta adicional
    def new_card(self, index):
        self.player.cards[index].append(self.draw())
        self.hand_total(self.player)
        self.print_game()
        if self.player.totals[index][0] > 21 and self.player.totals[index][1] > 21:
            self.player.status[index] = 'Inactive'
            self.player.veredict[index] = 'Bust! - YOU LOSE'
        return self.player_action()

    def print_game(self):
        dealer_cards = ""
        player_cards = ""
        if self.turn == "player":
            print("Dealer's hand")
            print(self.card_images.card_dict[self.dealer.cards[0][1][2]])
            print(self.card_images.card_dict['HIDDEN'])  ## Cambiar por hidden card
        else:
            print("Dealer's hand")
            for card in self.dealer.cards[0]:
                print(self.card_images.card_dict[card[2]])

        for i in range(len(self.player.cards)):
            hand = self.player.cards[i]
            print(f"{self.player.name}'s hand {i + 1}")
            for card in hand:
                print(self.card_images.card_dict[card[2]])