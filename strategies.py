import json
import game_engine as bj

#Three basic strategies
def always_stand(player_hand, up_card):
        
    return 'stand'

def always_hit(player_hand, up_card):

    return 'hit'

def always_hit_u17_stand_weak_up_card(player_hand, up_card):

    total, soft = player_hand.total_value()

    if up_card <= 6:
        if total >= 12:
            return 'stand'
        else:
            return 'hit'
    else:
        if total < 17:
            return 'hit'
        else:
            return 'stand'


def mimic_dealer(player_hand, up_card):
    #Plays exactly like the dealer: hit below 17, and hit soft 17
    total, soft = player_hand.total_value()
    if total < 17 or (total == 17 and soft):
        return 'hit'
    return 'stand'

#advanced functions----------

def forced_first(first_action, then_strategy):

    first_move = True

    def strategy(player_hand, up_card):
        nonlocal first_move
        if first_move:
            first_move = False
            return first_action
        return then_strategy(player_hand, up_card)

    return strategy

def best_legal_action(evs, player_hand):
    legal = {}
    for action, ev in evs.items():
        if action == 'double' and len(player_hand.cards) != 2:
            continue
        if action == 'split' and player_hand.split_depth >= bj.MAX_SPLITS:
            continue
        legal[action] = ev
    return max(legal, key=legal.get)


def table_strategy(table, fallback=always_hit_u17_stand_weak_up_card):
    #Builds a strategy that plays from the table, using the fallback
    #for any situation the table doesn't contain yet

    def strategy(player_hand, up_card):
        cards = player_hand.cards
        total, soft = player_hand.total_value()

        is_pair = len(cards) == 2 and bj.VALUES[cards[0][0]] == bj.VALUES[cards[1][0]]

        # Try the pair entry first, then the soft/hard entry
        keys = []
        if is_pair:
            keys.append(('pair', bj.up_card_value(cards[0]), up_card))
        if soft:
            keys.append(('soft', total, up_card))
        else:
            keys.append(('hard', total, up_card))

        for key in keys:
            if key in table:
                return best_legal_action(table[key], player_hand)

        return fallback(player_hand, up_card)

    return strategy


def load_table(path):
    #Reads a saved table and converts its keys back into tuples
    with open(path) as f:
        data = json.load(f)
    table = {}
    for key, evs in data.items():
        section, total, up = key.split(',')
        table[(section, int(total), int(up))] = evs
    return table