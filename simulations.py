import math
import random
import time
import game_engine as bj
import strategies as strats

N = 5000000
SEED = 6969


def evaluate_strategy(strategy, n=N, seed=SEED):
    #Plays n rounds and returns the mean result, standard deviation, and 95% margin
    random.seed(seed)
    shoe = bj.Shoe(6)
    total = 0
    total_sq = 0

    for _ in range(n):
        result = bj.play_round(shoe, strategy)
        total += result
        total_sq += result * result

    mean = total / n
    variance = (total_sq / n - mean ** 2) * n / (n - 1)
    stdev = math.sqrt(variance)
    margin = 1.96 * stdev / math.sqrt(n)

    return mean, stdev, margin


table = strats.load_table('basic_strategy_N=20000.json')

STRATEGIES = [
    ('Always hit', strats.always_hit),
    ('Always stand', strats.always_stand),
    ('Mimic the dealer', strats.mimic_dealer),
    ('Up-card heuristic', strats.always_hit_u17_stand_weak_up_card),
    ('Derived basic strategy', strats.table_strategy(table)),
]


print(f'{"Strategy":<24}{"Mean":>10}{"95% CI":>24}{"Std dev":>10}{"Time":>8}')

for name, strategy in STRATEGIES:
    start = time.time()
    mean, stdev, margin = evaluate_strategy(strategy)
    elapsed = time.time() - start

    ci = f'{(mean - margin) * 100:.2f}% to {(mean + margin) * 100:.2f}%'
    print(f'{name:<24}{mean * 100:>9.2f}%{ci:>24}{stdev:>10.3f}{elapsed:>7.0f}s')