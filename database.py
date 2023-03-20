# 6
PRICES = [
    'open', 'high', 'low', 'close',
    'vwap', 'returns'
]

# 3
VOLUMES = [
    'volume', 'adv20', 'cap'
]

# 5
one_OP_one = [
    '+', '-', '*', '/', '^'
]

# 7
OP_one = [
    '', 'rank', 'sigmoid', 'exp',
    'fraction', 'log', 'log_diff', 'scale'
]

# 2
UNARY_OP = ['', '-']

# 15
TS_OP_1D1P = [
    'ts_product', 'ts_std_dev',
    'ts_sum', 'ts_entropy', 'ts_av_diff', 'ts_arg_max',
    'ts_decay_linear', 'ts_delay', 'ts_delta', 'ts_ir',
    'ts_max', 'ts_max_diff', 'ts_median', 'ts_min',
    'ts_min_diff',

]

TS_OP_1D2P = [
    'ts_corr'
]

GROUP_OP_1D1P = [
    'group_zscore', 'group_std_dev', 'group_rank',
    'group_sum', 'group_scale', 'group_max',
    'group_median'
]

GROUP_DT = [
    'market', 'sector', 'industry', 'subindustry'
]

P_or_M = [
    '', '-'
]

DEAL_WITH_WEIGHT = [
    'rank', 'sigmoid', ''
]

IF_ELSE = [
    '?', ':'
]

CONDITION = [
    '>', '<', '='
]