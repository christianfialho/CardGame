"""
Course: CSE 251
Lesson Week: 02 - Team Activity
File: team.py
Author: Brother Comeau

Purpose: Playing Card API calls

Instructions:

- Review instructions in I-Learn.

"""

from datetime import datetime, timedelta, date
import threading
import requests
from abc import ABC,abstractmethod
from os.path import exists
from cse251 import * # Include cse 251 common Python files
set_working_directory(__file__)

class Request_thread(threading.Thread):
    def __init__(self, url:str ):
        super().__init__()
        self.url = url
        self.data = {}

    def run(self):
        response = requests.get(self.url)
        i = 0 # retry the request 3 times if not successful
        while response.status_code != 200 and i<3:
            response = requests.get(self.url)
        if response.status_code == 200:
            self.data = response.json()
        else:
            print('Error in requesting ID')


class Deck:
    # a mirror of the deck of cards api
    def __init__(self, deck_id=r"new/?jokers_enabled=true"):
        deck_data = self.ping_deck(deck_id)
        if deck_data['success']:
            self.id = deck_data['deck_id'] # if deck_id=="new", will set new id
            self.remaining = deck_data['remaining']
        self.piles = {}
        if "piles" in deck_data.keys():
            for pile in deck_data['piles'].items():
                self.piles[pile[0]] = Pile(pile[0],self.id)
                self.piles[pile[0]].load()

    def ping_deck(self,deck_id=""):
        # check if deck id is valid on server, return basic data
        # deck_id = "new"  will create a new deck
        # deck_id = "new/?jokers_enabled=true"  will create a new deck with 2 Jokers in it
        if deck_id=="":
            deck_id = self.id
        url = rf"https://deckofcardsapi.com/api/deck/{deck_id}"
        rt = Request_thread(url)
        rt.start()
        rt.join()
        return rt.data

    def reshuffle(self,remaining_only=False):
        url = rf"https://deckofcardsapi.com/api/deck/{self.id}/shuffle{r'?remaining=true'*(remaining_only)}"
        rt = Request_thread(url)
        rt.start()
        rt.join()
        self.remaining = rt.data['remaining']
        # print(self.remaining)

    def draw_card(self,count):
        if self.remaining >= count >= 1:
            rt = Request_thread(rf"https://deckofcardsapi.com/api/deck/{self.id}/draw/?count={count}")
            rt.start()
            rt.join()
            if not rt.data == None:
                self.remaining = rt.data['remaining']
                return list(map(lambda d: d['code'],rt.data['cards']))

    def add_to_pile(self,cards,pile_name):
        if not pile_name in self.piles.keys():
            self.piles[pile_name] = Pile(pile_name,self.id)

        self.piles[pile_name].add(cards)

    def cards_remaining(self):
        return self.remaining


class Pile:
    def __init__(self,name,deck_id):
        self.name = name
        self.id = deck_id
        self.cards = []

    def load(self):
        url = rf"https://deckofcardsapi.com/api/deck/{self.id}/pile/{self.name}/list"
        rt = Request_thread(url)
        rt.start()
        rt.join()
        self.cards += list(map(lambda d:d["code"],rt.data['piles'][self.name]["cards"]))
        self.cards = []

    def add(self,cards):
        url = rf"https://deckofcardsapi.com/api/deck/{self.id}/pile/{self.name}/add/?cards={','.join(cards)}"
        rt = Request_thread(url)
        rt.start()
        rt.join()
        if rt.data["success"]:
            self.cards += cards

    def draw(self,cards=None,bottom=False,random=False,count=0):
        # draws 1 card from top by default
        if bottom and random:
            raise ValueError("Cannot include both arguments 'bottom' and 'random'")
        if cards and count:
            raise ValueError("Cannot include both arguments 'cards' and 'count'")
        url = rf"https://deckofcardsapi.com/api/deck/{self.id}/pile/{self.name}/draw"
        url = url + (bottom)*"/bottom/" + (random)*"/random/" + (count>0)*("/?count="+count)
        if not cards==None:
            url = url + "/?cards=" + ",".join(cards)
        rt = Request_thread(url)
        rt.start()
        rt.join()
        drawn_cards = list(map(lambda d:d["code"],rt.data["cards"]))
        for card in drawn_cards:
            self.card.remove(card)
        return drawn_cards
        
    def shuffle(self):
        url = rf"https://deckofcardsapi.com/api/deck/{self.id}/pile/{self.name}/shuffle"
        rt = Request_thread(url)
        rt.start()
        rt.join()


class CardGameMenu:
    def __init__(self,game):
        self.game = game
        self.title = game.name
        self.savedata = {}
        self.exit = False
        self.saved_games_exist = self.read_saves(game)

    def print_menu(self):
        print(f'{"Welcome to " + self.title + "!":^50}')
        print("-"*50)
        print()
        print(f'{"n : New Game":^50}')
        print(f'{"j : Join Game":^50}')
        if self.saved_games_exist:
            print(f'{"l : Load Game":^50}')
        print(f'{"i : Instructions":^50}')
        print(f'{"x : Exit":^50}')
        print()
        print("-"*50)

    def read_saves(self,game):
        if exists("savefile.txt"):
            with open("savefile.txt", "r") as f:
                self.savedata = eval(f.read())
            for save in self.savedata.values():
                if save["game"]==game.name:
                    return True
        return False

    def run(self):
        self.print_menu()
        while self.exit==False:
            command = input(self.title + " Menu >")
            if self.is_valid_command(command):
                eval("self."+command+"()")
            else:
                print("Invalid command")
            print()

    def is_valid_command(self,command:str):
        if not hasattr(self,command):
            return False
        if len(command)>1:
            return False
        if not command.isalnum():
            return False
        return True
        
    def x(self):
        self.exit = True
        print("Exiting...")

    def i(self):
        self.game.i()

    def n(self):
        self.game.i()

    def l(self):
        print()
        print("Saved Games:")
        i = 1
        for save in self.savedata:
            print(f"{i}. {save[]}")


class Player:
    def __init__(self,game):
        self.game = game
        self.name = ""
        self.has_turn = False

    def set_name(self):
        name = ""
        while not is_valid_name(name):
            name = input("Nickname >")

    def is_valid_name(self,name:str):
        if len(name) > 12:
            print("Must be no longer than 12 characters.")
            return False
        if not name[0].isalpha():
            print("Must start with a letter")
            return False
        if not name.isalnum():
            print("Can only contain letters and numbers.")
            return False
        deck_data = self.game.deck.ping_deck()
        if "piles" in deck_data:
            for pilename in deck_data['piles']:
                if pilename.split("_")[0] == name:
                    print("Name already chosen in this game. Please choose another.")
                    return False
        return True


class CardGame(ABC):
    def __init__(self):
        self.quit = False
        self.player = ""
        self.deck = None #Deck('u0y8jiuncdet')
        self.name = "<CardGame>"
        self.instructions = ""
    
    def new(self):
        self.deck = Deck()
        d = self.deck
        self.player = input("Nickname >")
        whole_deck = d.draw_card(d.remaining)
        whole_deck.remove("X1")
        d.add_to_pile(["X1"],self.player + "_turn")
    def play(self):
        self.i()
        print()
        while self.quit==False:
            command = input(self.name + ">")
            if self.is_valid_command(command):
                eval("self."+command+"()")
            else:
                print("Invalid command")
            print()

    def is_valid_command(self,command:str):
        if not hasattr(self,command):
            return False
        if len(command)>1:
            return False
        if not command.isalnum():
            return False
        return True

    def q(self):
        self.quit = True
        print("Leaving game...")
        self.save_game()

    def i(self):
        print()
        print("Instructions:")
        print(self.instructions)
        print("press q to quit")
        print("press i for instructions")
        print("-"*50)

    @abstractmethod
    def save_game():
        pass


class GoFish(CardGame):
    def __init__(self):
        super().__init__()
        self.hand = {"A":[],"2":[],"3":[],"4":[],"5":[],"6":[],"7":[],"8":[],"9":[],"0":[],"J":[],"Q":[],"K":[]}
        self.complete_sets = []
        self.name = "Go Fish"
        self.instructions = \
        "press r to restart game\n" + \
        "press h to see cards in your hand\n" + \
        "press g to Go Fish! for a new card"
        
    def r(self):
        print("Shuffling...")
        self.deck.reshuffle()
        print("Drawing a new hand...")
        self.hand = {}
        for i in range(8):
            self.draw()
        self.h()

    def draw(self):
        card = self.deck.draw_card()
        self.hand[card[0]].append(card)

    def h(self):
        print("Hand:")
        print(" ".join(self.hand))

    def g(self):
        self.draw()
        self.h()

    def s(self):
        if not self.check_for_sets():
            self.show_sets()
            
    def check_for_sets(self):
        new_sets = 0 # count how many new ones
        for cardtype in self.hand.values():
            if len(cardtype) >= 2:
                a = cardtype.pop()
                b = cardtype.pop()
                self.complete_sets.append((a,b))
                new_sets += 1
        if new_sets>0:
            print(f"{new_sets} new set{'s'*(new_sets>1)} created!")
        return new_sets
    
    def show_sets(self):
        print("Complete Sets:")
        print(" ".join(self.complete_sets))

    def save_game(self):
        pile = []
        for tup in self.complete_set:
            for card in tup:
                pile.append(card)
        for cardtypes in self.hand.values():
            for card in cardtypes:
                pile.append(card)
        self.deck.send_to_pile(pile)


def main():
    game = GoFish()
    menu = CardGameMenu(game)
    menu.run()

if __name__ == '__main__':
    main()
    
