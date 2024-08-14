# Made by Willians Varela and Elias Mebratu

import sys
import random
from typing import List, Tuple, Dict, Optional
from abc import ABC, abstractmethod

class Card:
    SUITS = "♠ ♡ ♢ ♣".split()
    RANKS = "2 3 4 5 6 7 8 9 10 J Q K A".split()

    def __init__(self, suit: str, rank: str) -> None :
        self.suit = suit
        self.rank = rank

    @property
    def suit(self) -> str:
        return self.__suit

    @property
    def rank(self) -> str:
        return self.__rank

    @suit.setter
    def suit(self, suit):
        if suit not in self.__class__.SUITS:
            raise ValueError("Invalid Card Suit")
        self.__suit = suit

    @rank.setter
    def rank(self, rank):
        if rank not in self.__class__.RANKS:
            raise ValueError("Invalid Card Rank")
        self.__rank = rank

    def __repr__(self) -> str :
        return f"{self.__suit}{self.__rank}"

    def __hash__(self):
        return hash((self.__suit, self.__rank))

    def __eq__(self, second) -> bool:
        return self.__suit == second.suit and self.__rank == second.rank

    def __gt__(self, second) -> bool:
        """
            Specifies whether this card is greater than another card
            NOTICE: if the suits are different, returns False.
        """
        rankNums = {rank: num for (rank, num) in zip(list("23456789")+["10"]+list("JQKA"), range(2,15))} 
        if second.suit == self.__suit:
            if rankNums[self.__rank] > rankNums[second.rank]:
                return True
        return False

class Trick:
        HEARTS_ALLOWED: bool = False

        def __init__(self, cards: Optional[Tuple[Card, ...]]=None):
            self.__cards: Tuple[Card,...] = cards

        @property
        def cards(self) -> Tuple[Card,...]:
            return self.__cards

        def get_points(self):
            points = 0
            for card in self.__cards:
                if card.suit == "♡":
                    points += 1
                elif card.suit == "♠" and card.rank == "Q":
                    points += 13
            return points

        def add_card(self, card: Card):
            if self.cards and len(self.cards) >= 4:
                raise ValueError("More than 4 cards cannot be added to a trick")
            if self.cards and card in self.cards:
                raise ValueError("The same card cannot be added to a trick twice")
            if self.__cards:
                self.__cards = (*self.__cards, card)
            else:
                self.__cards = (card,)

        def get_winCard_idx(self) -> int:
            """ returns the turn number in which the winner card of the trick was played """
            winIdx = 0
            maxCard: Card = self.__cards[0]
            for idx, card in enumerate(self.__cards):
                if card > maxCard:
                    winIdx = idx
                    maxCard = card
            return winIdx

class Deck:
    def __init__(self, **kwargs) -> None :
        """ 
        possible keyword arguments:
            cards: Optional[List[Card]]=None
            shuffle: bool=False
        """
        self.cards_setter(kwargs)

    def cards_getter(self) -> List[Card]:
        return self.__cards

    def cards_setter(self, kwargs):
        cards = kwargs["cards"] if "cards" in kwargs else None
        shuffle = kwargs["shuffle"] if "shuffle" in kwargs else False

        if not cards:
            cards = [Card(s, r) for r in Card.RANKS for s in Card.SUITS]
        if shuffle:
            random.shuffle(cards)
        self.__cards: List[Card] = cards

    cards = property(cards_getter, cards_setter)

    def __iter__(self) -> Card:
        yield from self.cards

    def deal(self) -> Tuple["Deck", "Deck", "Deck", "Deck"] :
        """Deal the cards in the deck into 4 hands"""
        cls = self.__class__
        return tuple(cls(cards=self.__cards[i::4]) for i in range(4))

class Player(ABC):
    def __init__(self, name: str, hand: Deck) -> None:
        self.name: str = name
        self.hand: Deck = hand
        self.tricksPointsSum: int = 0
        self.roundsPointsSum: int = 0

    @property
    def name(self) -> str:
        return self.__name

    @name.setter
    def name(self, name):
        self.__name = name

    @property
    def hand(self) -> Deck:
        return self._hand

    @hand.setter
    def hand(self, cards: Deck):
        self._hand = cards

    @property
    def tricksPointsSum(self) -> int:
        return self.__tricksPointsSum

    @tricksPointsSum.setter
    def tricksPointsSum(self, tricksPointsSum: int):
        self.__tricksPointsSum = tricksPointsSum

    @property
    def roundsPointsSum(self) -> int:
        return self.__roundsPointsSum

    @roundsPointsSum.setter
    def roundsPointsSum(self, roundsPointsSum: int):
        self.__roundsPointsSum = roundsPointsSum

    def play_card(self, trick: Trick) -> Trick:
        if Card("♣","2") in self._hand:
            yield self.__play_this(Card("♣","2"), trick)
        while True:
            playable = self.__get_playable_cards(trick)
            chosen_card = self._prompt_choice(playable)
            yield self.__play_this(chosen_card, trick)

    def __play_this(self, card: Card, trick: Trick) -> Trick:
        trick.add_card(card)
        print(f"{self.__name} -> {card}")
        self._hand.cards.remove(card)
        return trick

    def __get_playable_cards(self, trick: Trick) -> List[Card]:
        if not trick.cards:
            if Trick.HEARTS_ALLOWED:
                return self._hand.cards
            else:
                lst = list(filter(lambda card: card.suit != "♡" , self._hand))
                if lst:
                    return lst
                else:
                    Trick.HEARTS_ALLOWED = True
                    return self.__get_playable_cards(trick)
        else:
            trickSuit = trick.cards[0].suit
            if self.has_card(trickSuit):
                return list(filter(lambda card: card.suit == trickSuit, self._hand))
            else:
                Trick.HEARTS_ALLOWED = True
                return self._hand.cards

    def has_card(self, suit, rank: Optional[str] = None) -> bool:
        if rank:
            if Card(suit, rank) in self._hand:
                return True
        else:
            for card in self._hand:
                if card.suit == suit:
                    return True
        return False

    @abstractmethod
    def _prompt_choice(self, playable: Deck) -> Card:
        pass

class HumanPlayer(Player):
    def _prompt_choice(self, playable: Deck) -> Card:
        rankNums = {rank: num for (rank, num) in zip(list("23456789")+["10"]+list("JQKA"), range(2,15))} 
        sortedPlayable = sorted(playable, key=lambda card: (card.suit, rankNums[card.rank]))

        [print(f"\t{idx}: {card} ", end="") for idx, card in enumerate(sortedPlayable)]
        print("(Rest: ", end="")
        for nonPlayableCard in list(set(self._hand.cards)-set(playable)):
            print(nonPlayableCard, end="")
            print(" ", end="")
        print(")")
        while True:
            print(f"\t{self.name}, choose card: ", end="")
            try:
                choiceCardIdx: int = int(input())
            except ValueError:
                continue
            if choiceCardIdx < len(sortedPlayable):
                break

        return sortedPlayable[choiceCardIdx]

class AutoPlayer(Player):
    def _prompt_choice(self, playable: Deck) -> Card:
        rankNums = {rank: num for (rank, num) in zip(list("23456789")+["10"]+list("JQKA"), range(2,15))} 
        sortedPlayable = sorted(playable, key=lambda card: (card.suit, rankNums[card.rank]))
        return sortedPlayable[0]

class Game:

    def __init__(self, numOfHumans: Optional[int] = 1, *playerNames: Optional[str]) -> None:
        """Set up the deck and create the 4 players"""
        self.__roundNumber: int = 1
        self.__names: List[str] = (list(playerNames) + "P1 P2 P3 P4".split())[:4]
        self.__players: List[Player] = [ HumanPlayer(name, hand) for name, hand in zip(self.__names[:numOfHumans], [None]*numOfHumans)]
        self.__players.extend((AutoPlayer(name, hand) for name, hand in zip(self.__names[numOfHumans:], [None]*(4-numOfHumans)) ))

    def __set_new_round(self):
        deck = Deck(shuffle=True)
        hands = deck.deal()
        for idx, player in enumerate(self.__players):
            player.hand = hands[idx]

    def play(self) -> int:
        """Play the card game"""

        while max(player.roundsPointsSum for player in self.__players) < 100:
            """ while no one has lost the whole game """ 

            self.__set_new_round()

            # continue the round by playing the rest of the tricks
            winnerPlayer: Optional[Player] = None
            while self.__players[0].hand.cards:
                trick = Trick()
                turnOrder = next(self.__player_order(winnerPlayer))
                for player in turnOrder:
                    trick = next(player.play_card(trick))
                winnerIdx = trick.get_winCard_idx()
                winnerPlayer = turnOrder[winnerIdx]
                winnerPlayer.tricksPointsSum += trick.get_points()
                turnOrder = self.__player_order(winnerPlayer)
                print(f"{winnerPlayer.name} wins the trick\n{'*'*17}")
            # end of round

            print(f"{'-'*50}\nEnd Of Round {self.__roundNumber}\n{'-'*50}")

            # save the round scores
            for player in self.__players:
                player.roundsPointsSum += player.tricksPointsSum
                print(f"{player.name}: {player.roundsPointsSum}")
                player.tricksPointsSum = 0

            # finish the round and reset it
            Trick.HEARTS_ALLOWED = False
            self.__roundNumber += 1
            print(f"{'-'*50}\n")

        #end of the whole game
        self.__announce_winner()
        return 0

    def __announce_winner(self) -> None:
        winnerName = min(self.__players, key=lambda player: player.roundsPointsSum).name
        print(f"{'*' * 50}\n{'*'*16} {winnerName} wins the game {'*'*16}\n{'*' * 50}")

    def __player_order(self, startPlayer: Player) -> List[Player]:
        """Rotate player order so that start goes first"""
        if not startPlayer:
            for player in self.__players:
                """ find the player that has the ♣2 card """
                if player.has_card("♣", "2"):
                    start_idx = self.__players.index(player)
                    yield self.__players[start_idx:] + self.__players[:start_idx]
                    break
        while True:
            start_idx = self.__players.index(startPlayer)
            yield self.__players[start_idx:] + self.__players[:start_idx]

if __name__ == "__main__":
    try:
        numOfHumans = int(sys.argv[1])
        if numOfHumans > 4 or numOfHumans < 0:
            raise ValueError("Number of human players cannot be less than 0 or more than 4")
        playerNames = sys.argv[2:2+numOfHumans]
    except (IndexError, ValueError):
        print("Number of human players is automatically set to 1")
        numOfHumans = 1
        playerNames = ()

    try:
        game = Game(numOfHumans, *playerNames)
        game.play()
    except EOFError:
        print("\nGame Aborted")