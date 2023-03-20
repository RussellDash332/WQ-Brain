from database import GROUP_DT, GROUP_OP_1D1P, PRICES, TS_OP_1D2P, VOLUMES, TS_OP_1D1P, UNARY_OP, one_OP_one, OP_one, P_or_M, DEAL_WITH_WEIGHT, IF_ELSE, CONDITION

def price_vs_volume():
    D1 = [1, 5, 10, 50]
    D2 = [1, 5, 10, 50]
    commands = []
    for price in PRICES:
        for volume in VOLUMES:
            for ts_op_1d1p in TS_OP_1D1P:
                for unary in UNARY_OP:
                    for one_op_one in one_OP_one:
                        for op_one in OP_one:
                            for d1 in D1:
                                for d2 in D2:
                                    command = f'{unary}{ts_op_1d1p}({op_one}(ts_median({price}, {d1}) {one_op_one} ts_median({volume}, {d1})), {d2})'
                                    commands.append(command)
    return commands

def volume_vs_price():
    D1 = [1, 5, 10, 50]
    D2 = [1, 5, 10, 50]
    commands = []
    for price in PRICES:
        for volume in VOLUMES:
            for ts_op_1d1p in TS_OP_1D1P:
                for unary in UNARY_OP:
                    for one_op_one in one_OP_one:
                        for op_one in OP_one:
                            for d1 in D1:
                                for d2 in D2:
                                    command = f'{unary}{ts_op_1d1p}({op_one}(ts_median({volume}, {d1}) {one_op_one} ts_median({price}, {d1})), {d2})'
                                    commands.append(command)
    return commands

def price_vs_price():
    D1 = [1, 5, 10, 50]
    D2 = [1, 5, 10, 50]
    commands = []
    for price1 in PRICES:
        for price2 in PRICES:
            if price1 == price2:
                continue
            for ts_op_1d1p in TS_OP_1D1P:
                for unary in UNARY_OP:
                    for one_op_one in one_OP_one:
                        for op_one in OP_one:
                            for d1 in D1:
                                for d2 in D2:
                                    command = f'{unary}{ts_op_1d1p}({op_one}(ts_median({price1}, {d1}) {one_op_one} ts_median({price2}, {d1})), {d2})'
                                    commands.append(command)
    return commands

def scale_and_corr():
    D1 = [1, 5, 10, 50]
    D2 = [1, 5, 10, 50]
    commands = []
    for price in PRICES:
        for one_op_one in one_OP_one:
                for d1 in D1:
                    for d2 in D2:
                        command = f'(scale(((ts_sum({price}, {d1}){one_op_one}{d1})-{price})) + (20*scale(ts_corr({price}, ts_delay({price}, {d2}), 230))))'
                        commands.append(command)
    return commands

def from_wq():
    commands = []
    for price1 in PRICES:
        for price2 in PRICES:
            if price1 == price2:
                continue
            for price3 in PRICES:
                for price4 in PRICES:
                    if price3 == price4:
                        continue
                    for p_or_m in P_or_M:
                        for group_op in GROUP_OP_1D1P:
                            command = f'{group_op}({p_or_m}({price1} - {price2})/({price3} - {price4}), subindustry)'
                            commands.append(command)
    return commands

def sample_1():
    commands = []
    for price1 in PRICES:
        for price2 in PRICES:
            if price1 == price2:
                continue
            for ts_op_1d1p in TS_OP_1D1P:
                command = f'rank((1 * ((open - close) / ts_decay_linear(rank({ts_op_1d1p}({price1}, 10)), 2))))'
                commands.append(command)
    return commands

def sample_2():
    D1 = [1, 2, 5, 10, 20, 30, 50, 100] 
    D2 = [2, 5, 10, 20, 30, 50, 100, 120]
    commands = []
    for d1 in D1:
        for d2 in D2:
            command = f'close>open?-rank(ts_mean(close, {d1})):rank(ts_mean(close, {d2}))'
            commands.append(command)
    return commands

funcs = [price_vs_volume, volume_vs_price, price_vs_price, scale_and_corr, from_wq, sample_1, sample_2]
[print(f.__name__, len(f())) for f in funcs]