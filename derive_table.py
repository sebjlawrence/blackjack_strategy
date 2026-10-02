import random
import json
import game_engine as bj
import strategies as strats

N = 100         
SEED = 696969 #seed for random set

UP_RANKS = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'A']   

# Representative hands for each situation, in the order they're filled
#AI disclaimer. AI was used for generating this table as I didn't particularly want to write this out by hand.
#I also got some help with the formatting of the JSON so it looked pretty
HARD_HIGH = {20: ['10', 'K'], 19: ['10', '9'], 18: ['10', '8'], 17: ['10', '7'],
             16: ['10', '6'], 15: ['10', '5'], 14: ['10', '4'], 13: ['10', '3'],
             12: ['10', '2']}
SOFT = {20: ['A', '9'], 19: ['A', '8'], 18: ['A', '7'], 17: ['A', '6'],
        16: ['A', '5'], 15: ['A', '4'], 14: ['A', '3'], 13: ['A', '2']}
HARD_LOW = {11: ['9', '2'], 10: ['7', '3'], 9: ['6', '3'], 8: ['5', '3'],
            7: ['5', '2'], 6: ['4', '2'], 5: ['3', '2']}
PAIRS = {11: ['A', 'A'], 10: ['10', '10'], 9: ['9', '9'], 8: ['8', '8'],
         7: ['7', '7'], 6: ['6', '6'], 5: ['5', '5'], 4: ['4', '4'],
         3: ['3', '3'], 2: ['2', '2']}

LETTERS = {'hit': 'H', 'stand': 'S', 'double': 'D', 'split': 'P'}


def evaluate(table, player_ranks, up_rank, action):
    #Average result of forcing this action first, then following the table
    shoe = bj.Shoe(6)
    then_strategy = strats.table_strategy(table)
    total = 0

    for i in range(N):
        # Common random numbers: round i gets the same cards for every action otherwise N would have to be even larger to deal with extra randomness
        random.seed(SEED + i)
        shoe.reshuffle()

        strategy = strats.forced_first(action, then_strategy)
        total += bj.play_from_position(shoe, strategy, player_ranks, up_rank)

    return total / N


def fill_section(table, section, hands, actions):
    for total, ranks in hands.items():
        for up_rank in UP_RANKS:
            up = bj.up_card_value([up_rank, 'Hearts'])
            evs = {action: evaluate(table, ranks, up_rank, action) for action in actions}
            table[(section, total, up)] = evs

            best = max(evs, key=evs.get)
            print(f'{section} {total} vs {up}: {best}  {evs}')


def save_table(table, path):
    #JSON can't store tuple keys, so turn each key into a string
    data = {f'{s},{t},{u}': evs for (s, t, u), evs in table.items()}
    with open(path, 'w') as f:
        json.dump(data, f, indent=1)


def print_chart(table, section, totals):
    print(f'\n{section.upper():>6}  ' + ' '.join(f'{u:>2}' for u in range(2, 12)))
    for t in totals:
        row = []
        for u in range(2, 12):
            evs = table[(section, t, u)]
            best = max(evs, key=evs.get)
            row.append(f'{LETTERS[best]:>2}')
        print(f'{t:>6}  ' + ' '.join(row))


if __name__ == '__main__':
    table = {}
    three_actions = ['hit', 'stand', 'double']

    #done in this order so that every event can only come from something found in an earlier table
    #This prevents the fallback function being called unnecessarily
    fill_section(table, 'hard', HARD_HIGH, three_actions)
    fill_section(table, 'soft', SOFT, three_actions)
    fill_section(table, 'hard', HARD_LOW, three_actions)

    # Two passes, so resplits use the first pass's pair decisions
    for _ in range(2):
        fill_section(table, 'pair', PAIRS, three_actions + ['split'])

    save_table(table, 'basic_strategy.json')

    print_chart(table, 'hard', list(range(20, 4, -1)))
    print_chart(table, 'soft', list(range(20, 12, -1)))
    print_chart(table, 'pair', list(range(11, 1, -1)))