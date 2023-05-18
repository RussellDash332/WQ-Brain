from commands import *

# Just a sample
DATA = {
    'neutralizations': ['Subindustry', 'Industry', 'Sector', 'Market'],
    'decays': [10],
    'truncations': [0.1],
    'delays': [0, 1],
    'universes': ['TOP200', 'TOP500', 'TOP1000', 'TOP3000'],
    'alphas': sample_1() + from_wq_2() + sample_2()
}