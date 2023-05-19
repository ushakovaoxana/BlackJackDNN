import numpy as np
import random
import pandas as pd
import matplotlib.pyplot as plt
#import seaborn as sns
#import sklearn.metrics as metrics
from keras.models import Sequential
from keras.layers import Dense, LSTM, Flatten, Dropout

# This function lists out all permutations of ace values in the array sum_array
# For example, if you have 2 aces, there are 4 permutations:
#     [[1,1], [1,11], [11,1], [11,11]]
# These permutations lead to 3 unique sums: [2, 12, 22]
# Of these 3, only 2 are <=21 so they are returned: [2, 12]
def get_ace_values(temp_list):
    sum_array = np.zeros((2**len(temp_list), len(temp_list)))
    # This loop gets the permutations
    for i in range(len(temp_list)):
        n = len(temp_list) - i
        half_len = int(2**n * 0.5)
        for rep in range(int(sum_array.shape[0]/half_len/2)):
            sum_array[rep*2**n : rep*2**n+half_len, i] = 1
            sum_array[rep*2**n+half_len : rep*2**n+half_len*2, i] = 11
    # Only return values that are valid (<=21)
    # return list(set([int(s) for s in np.sum(sum_array, axis=1) if s<=21]))
    return [int(s) for s in np.sum(sum_array, axis=1)]

# Convert num_aces, an int to a list of lists
# For example if num_aces=2, the output should be [[1,11],[1,11]]
# I require this format for the get_ace_values function
def ace_values(num_aces):
    temp_list = []
    for i in range(num_aces):
        temp_list.append([1,11])
    return get_ace_values(temp_list)


# Make a deck
def make_decks(num_decks, card_types):
    new_deck = []
    for i in range(num_decks):
        for j in range(4):
            new_deck.extend(card_types)
    random.shuffle(new_deck)
    return new_deck


# Total up value of hand
def total_up(hand):
    aces = 0
    total = 0

    for card in hand:
        if card != 'A':
            total += card
        else:
            aces += 1

    # Call function ace_values to produce list of possible values for aces in hand
    ace_value_list = ace_values(aces)
    final_totals = [i + total for i in ace_value_list if i + total <= 21]

    if final_totals == []:
        return min(ace_value_list) + total
    else:
        return max(final_totals)


# Play a game of blackjack (after the cards are dealt)
def play_game(dealer_hand, player_hands, blackjack, curr_player_results, dealer_cards, hit_stay):
    action = 0
    # Dealer checks for 21
    if set(dealer_hand) == blackjack:
        for player in range(players):
            if set(player_hands[player]) != blackjack:
                curr_player_results[0, player] = -1
            else:
                curr_player_results[0, player] = 0
    else:
        for player in range(players):
            # Players check for 21
            if set(player_hands[player]) == blackjack:
                curr_player_results[0, player] = 1
            else:
                # Hit randomly, check for busts
                if (hit_stay >= 0.5) and (total_up(player_hands[player]) != 21):
                    player_hands[player].append(dealer_cards.pop(0))
                    action = 1
                    live_total.append(total_up(player_hands[player]))
                    if total_up(player_hands[player]) > 21:
                        curr_player_results[0, player] = -1

    # Dealer hits based on the rules
    while total_up(dealer_hand) < 17:
        dealer_hand.append(dealer_cards.pop(0))
    # Compare dealer hand to players hand but first check if dealer busted
    if total_up(dealer_hand) > 21:
        for player in range(players):
            if curr_player_results[0, player] != -1:
                curr_player_results[0, player] = 1
    else:
        for player in range(players):
            if total_up(player_hands[player]) > total_up(dealer_hand):
                if total_up(player_hands[player]) <= 21:
                    curr_player_results[0, player] = 1
            elif total_up(player_hands[player]) == total_up(dealer_hand):
                curr_player_results[0, player] = 0
            else:
                curr_player_results[0, player] = -1

    return curr_player_results, dealer_cards, action


stacks = 50000
players = 1
num_decks = 1

card_types = ['A', 2, 3, 4, 5, 6, 7, 8, 9, 10, 10, 10, 10]

dealer_card_feature = []
player_card_feature = []
player_live_total = []
player_live_action = []
player_results = []

for stack in range(stacks):
    blackjack = set(['A', 10])
    dealer_cards = make_decks(num_decks, card_types)
    while len(dealer_cards) > 20:

        curr_player_results = np.zeros((1, players))

        dealer_hand = []
        player_hands = [[] for player in range(players)]
        live_total = []
        live_action = []

        # Deal FIRST card
        for player, hand in enumerate(player_hands):
            player_hands[player].append(dealer_cards.pop(0))
        dealer_hand.append(dealer_cards.pop(0))
        # Deal SECOND card
        for player, hand in enumerate(player_hands):
            player_hands[player].append(dealer_cards.pop(0))
        dealer_hand.append(dealer_cards.pop(0))

        # Record the player's live total after cards are dealt
        live_total.append(total_up(player_hands[player]))

        if stack < 25000:
            hit_stay = 1
        else:
            hit_stay = 0
        curr_player_results, dealer_cards, action = play_game(dealer_hand, player_hands,
                                                              blackjack, curr_player_results,
                                                              dealer_cards, hit_stay)

        # Track features
        dealer_card_feature.append(dealer_hand[0])
        player_card_feature.append(player_hands)
        player_results.append(list(curr_player_results[0]))
        player_live_total.append(live_total)
        player_live_action.append(action)


print(sum(pd.DataFrame(player_results)[0].value_counts()))