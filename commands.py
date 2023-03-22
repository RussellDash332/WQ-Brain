from database import *

def from_wq_1():
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

def from_wq_2():
    return [
        'group_neutralize(volume/(ts_sum(volume,60)/60),sector)',
        'ts_step(20)*volume/(ts_sum(volume,60)/60)',
        'rank(close+ts_product(close, 5)^(0.2))',
        'ts_corr(rank(close), rank(volume/(ts_sum(volume,20)/20)), 5)',
        'rank(scale(ts_sum(-returns, 5), scale=1, longscale=1, shortscale=1) + scale(ts_decay_linear(volume/(ts_sum(volume,20)/20),5,dense=false), scale=1, longscale=1, shortscale=1))',
        'rank(group_mean(ts_delta(close,5),1,subindustry)-ts_delta(close,5))',
        '(rank(eps/last_diff_value(eps,5))>0.7 || volume>ts_delay(volume,1))?rank(-ts_delta(close,5)):-1',
        'trade_when((ts_arg_max(volume,5)<1) && (volume>=ts_sum(volume,5)/5),-rank(ts_delta(close,2)),-1)',
        'trade_when((ts_arg_min(volume,5)>3) || (volume>=ts_sum(volume,5)/5),-rank((high+low)/2-close),-1)',
        'log(pasteurize(vwap/close))',
        'rank(ts_covariance(ts_std_dev(-returns,22),(vwap-close),22))',
        '-ts_rank((ts_regression(close,close,20,LAG=1,RETTYPE=3)-ts_sum(ts_delay(close,1),2)/2)/close,60)*(1-rank(volume/(ts_sum(volume,30)/30)))',
        '-ts_sum(close-min(low,ts_delay(close,1)),5)/ts_sum(max(high,ts_delay(close,1))-low,5))',
        '-rank(close-ts_max(high,5))/(ts_max(high,5)-ts_min(low,5))'
    ]

def from_wq_3():
    return sum([[
        *[f'{op}(pasteurize({p1}/{p2}, {d}))' for op in OP_one for d in [2, 3, 5, 7]],
        *[f'-ts_mean({p1}, {d1})*rank(sigmoid(ts_mean({p2}, {d2})))' for d1 in [17, 23] for d2 in [30, 60]],
        *[f'-(power(ts_mean({p1} - {p2}, {d}), {p}) / (power(ts_mean(high - low, {d}), {p}) + {eps}))' for eps in [0.001, 0.005] for d in [13, 17, 19] for p in [1.5, 1.7, 1.9]],
        *[f'power(rank(-returns*adv20*vwap*({p1} - {p2}))*rank(-returns*adv20*vwap*(open - low)), {p})*rank(-(close - ts_mean(close, {d})))' for d in [30, 45, 60] for p in [1.5, 1.7, 1.9]]
    ] for p1 in PRICES for p2 in PRICES if p1 != p2], start=[])

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

# from https://arxiv.org/ftp/arxiv/papers/1601/1601.00991.pdf with minor modifications to compile properly
# disclaimer: adv{d} is changed to ts_sum(volume, d)/d
def from_arxiv():
    return [
        '(rank(ts_arg_max(signed_power(((returns < 0) ? stddev(returns, 20) : close), 2.), 5)) - 0.5',
        '(-1 * ts_corr(rank(ts_delta(log(volume), 2)), rank(((close - open) / open)), 6))',
        '(-1 * ts_corr(rank(open), rank(volume), 10))',
        '(-1 * ts_rank(rank(low), 9))',
        '(rank((open - (sum(vwap, 10) / 10))) * (-1 * abs(rank((close - vwap)))))',
        '(-1 * ts_corr(open, volume, 10))',
        '(((ts_sum(volume,20)/20) < volume) ? ((-1 * ts_rank(abs(ts_delta(close, 7)), 60)) * sign(ts_delta(close, 7))) : (-1 * 1))',
        '(-1 * rank(((sum(open, 5) * sum(returns, 5)) - ts_delay((sum(open, 5) * sum(returns, 5)), 10))))',
        '((0 < ts_min(ts_delta(close, 1), 5)) ? ts_delta(close, 1) : ((ts_max(ts_delta(close, 1), 5) < 0) ? ts_delta(close, 1) : (-1 * ts_delta(close, 1))))',
        'rank(((0 < ts_min(ts_delta(close, 1), 4)) ? ts_delta(close, 1) : ((ts_max(ts_delta(close, 1), 4) < 0) ? ts_delta(close, 1) : (-1 * ts_delta(close, 1)))))',
        '((rank(ts_max((vwap - close), 3)) + rank(ts_min((vwap - close), 3))) * rank(ts_delta(volume, 3)))',
        '(sign(ts_delta(volume, 1)) * (-1 * ts_delta(close, 1)))',
        '(-1 * rank(covariance(rank(close), rank(volume), 5)))',
        '((-1 * rank(ts_delta(returns, 3))) * ts_corr(open, volume, 10))',
        '(-1 * sum(rank(ts_corr(rank(high), rank(volume), 3)), 3))',
        '(-1 * rank(covariance(rank(high), rank(volume), 5)))',
        '(((-1 * rank(ts_rank(close, 10))) * rank(ts_delta(ts_delta(close, 1), 1))) * rank(ts_rank((volume / (ts_sum(volume,20)/20)), 5)))',
        '(-1 * rank(((stddev(abs((close - open)), 5) + (close - open)) + ts_corr(close, open, 10))))',
        '((-1 * sign(((close - ts_delay(close, 7)) + ts_delta(close, 7)))) * (1 + rank((1 + sum(returns, 250)))))',
        '(((-1 * rank((open - ts_delay(high, 1)))) * rank((open - ts_delay(close, 1)))) * rank((open - ts_delay(low, 1))))',
        '((((sum(close, 8) / 8) + stddev(close, 8)) < (sum(close, 2) / 2)) ? (-1 * 1) : (((sum(close, 2) / 2) < ((sum(close, 8) / 8) - stddev(close, 8))) ? 1 : (((1 < (volume / (ts_sum(volume,20)/20))) || ((volume / (ts_sum(volume,20)/20)) == 1)) ? 1 : (-1 * 1))))',
        '(-1 * (ts_delta(ts_corr(high, volume, 5), 5) * rank(stddev(close, 20))))',
        '(((sum(high, 20) / 20) < high) ? (-1 * ts_delta(high, 2)) : 0)',
        '((((ts_delta((sum(close, 100) / 100), 100) / ts_delay(close, 100)) < 0.05) || ((ts_delta((sum(close, 100) / 100), 100) / ts_delay(close, 100)) == 0.05)) ? (-1 * (close - ts_min(close, 100))) : (-1 * ts_delta(close, 3)))',
        'rank(((((-1 * returns) * (ts_sum(volume,20)/20)) * vwap) * (high - close)))',
        '(-1 * ts_max(ts_corr(ts_rank(volume, 5), ts_rank(high, 5), 5), 3))',
        '((0.5 < rank((sum(ts_corr(rank(volume), rank(vwap), 6), 2) / 2.0))) ? (-1 * 1) : 1)',
        'scale(((ts_corr((ts_sum(volume,20)/20), low, 5) + ((high + low) / 2)) - close))',
        '(min(product(rank(rank(scale(log(sum(ts_min(rank(rank((-1 * rank(ts_delta((close - 1), 5))))), 2), 1))))), 1), 5) + ts_rank(ts_delay((-1 * returns), 6), 5))',
        '(((1.0 - rank(((sign((close - ts_delay(close, 1))) + sign((ts_delay(close, 1) - ts_delay(close, 2)))) + sign((ts_delay(close, 2) - ts_delay(close, 3)))))) * sum(volume, 5)) / sum(volume, 20))',
        '((rank(rank(rank(decay_linear((-1 * rank(rank(ts_delta(close, 10)))), 10)))) + rank((-1 * ts_delta(close, 3)))) + sign(scale(ts_corr((ts_sum(volume,20)/20), low, 12)))) ',
        '(scale(((sum(close, 7) / 7) - close)) + (20 * scale(ts_corr(vwap, ts_delay(close, 5), 230))))',
        'rank((-1 * ((1 - (open / close))^1)))',
        'rank(((1 - rank((stddev(returns, 2) / stddev(returns, 5)))) + (1 - rank(ts_delta(close, 1)))))',
        '((ts_rank(volume, 32) * (1 - ts_rank(((close + high) - low), 16))) * (1 - ts_rank(returns, 32)))',
        '(((((2.21 * rank(ts_corr((close - open), ts_delay(volume, 1), 15))) + (0.7 * rank((open - close)))) + (0.73 * rank(ts_rank(ts_delay((-1 * returns), 6), 5)))) + rank(abs(ts_corr(vwap, (ts_sum(volume,20)/20), 6)))) + (0.6 * rank((((sum(close, 200) / 200) - open) * (close - open)))))',
        '(rank(ts_corr(ts_delay((open - close), 1), close, 200)) + rank((open - close)))',
        '((-1 * rank(ts_rank(close, 10))) * rank((close / open)))',
        '((-1 * rank((ts_delta(close, 7) * (1 - rank(decay_linear((volume / (ts_sum(volume,20)/20)), 9)))))) * (1 + rank(sum(returns, 250))))',
        '((-1 * rank(stddev(high, 10))) * ts_corr(high, volume, 10))',
        '(((high * low)^0.5) - vwap)',
        '(rank((vwap - close)) / rank((vwap + close)))',
        '(ts_rank((volume / (ts_sum(volume,20)/20)), 20) * ts_rank((-1 * ts_delta(close, 7)), 8))',
        '(-1 * ts_corr(high, rank(volume), 5))',
        '(-1 * ((rank((sum(ts_delay(close, 5), 20) / 20)) * ts_corr(close, volume, 2)) * rank(ts_corr(sum(close, 5), sum(close, 20), 2))))',
        '((0.25 < (((ts_delay(close, 20) - ts_delay(close, 10)) / 10) - ((ts_delay(close, 10) - close) / 10))) ? (-1 * 1) : (((((ts_delay(close, 20) - ts_delay(close, 10)) / 10) - ((ts_delay(close, 10) - close) / 10)) < 0) ? 1 : ((-1 * 1) * (close - ts_delay(close, 1)))))',
        '((((rank((1 / close)) * volume) / (ts_sum(volume,20)/20)) * ((high * rank((high - close))) / (sum(high, 5) / 5))) - rank((vwap - ts_delay(vwap, 5))))',
        '(group_neutralize(((ts_corr(ts_delta(close, 1), ts_delta(ts_delay(close, 1), 1), 250) * ts_delta(close, 1)) / close), subindustry) / sum(((ts_delta(close, 1) / ts_delay(close, 1))^2), 250))',
        '(((((ts_delay(close, 20) - ts_delay(close, 10)) / 10) - ((ts_delay(close, 10) - close) / 10)) < (-1 * 0.1)) ? 1 : ((-1 * 1) * (close - ts_delay(close, 1))))',
        '(-1 * ts_max(rank(ts_corr(rank(volume), rank(vwap), 5)), 5))',
        '(((((ts_delay(close, 20) - ts_delay(close, 10)) / 10) - ((ts_delay(close, 10) - close) / 10)) < (-1 * 0.05)) ? 1 : ((-1 * 1) * (close - ts_delay(close, 1))))',
        '((((-1 * ts_min(low, 5)) + ts_delay(ts_min(low, 5), 5)) * rank(((sum(returns, 240) - sum(returns, 20)) / 220))) * ts_rank(volume, 5))',
        '(-1 * ts_delta((((close - low) - (high - close)) / (close - low)), 9))',
        '((-1 * ((low - close) * (open^5))) / ((low - high) * (close^5)))',
        '(-1 * ts_corr(rank(((close - ts_min(low, 12)) / (ts_max(high, 12) - ts_min(low, 12)))), rank(volume), 6))',
        '(0 - (1 * (rank((sum(returns, 10) / sum(sum(returns, 2), 3))) * rank((returns * cap)))))',
        '(0 - (1 * ((close - vwap) / decay_linear(rank(ts_arg_max(close, 30)), 2))))',
        '(-1 * ts_rank(decay_linear(ts_corr(group_neutralize(vwap, sector), volume, 3), 7), 5))',
        '(-1 * ts_rank(decay_linear(ts_corr(group_neutralize(((vwap * 0.728317) + (vwap * (1 - 0.728317))), industry), volume, 4), 16), 8))',
        '(0 - (1 * ((2 * scale(rank(((((close - low) - (high - close)) / (high - low)) * volume)))) - scale(rank(ts_arg_max(close, 10))))))',
        '(rank((vwap - ts_min(vwap, 16))) < rank(ts_corr(vwap, (ts_sum(volume,180)/180), 17)))',
        '((rank(ts_corr(vwap, sum((ts_sum(volume,20)/20), 22), 9)) < rank(((rank(open) + rank(open)) < (rank(((high + low) / 2)) + rank(high))))) * -1)',
        '((rank(decay_linear(ts_delta(group_neutralize(close, industry), 2), 8)) - rank(decay_linear(ts_corr(((vwap * 0.318108) + (open * (1 - 0.318108))), sum((ts_sum(volume,180)/180), 37), 13), 12))) * -1)',
        '((rank(ts_corr(sum(((open * 0.178404) + (low * (1 - 0.178404))), 12), sum((ts_sum(volume,120)/120), 12), 16)) < rank(ts_delta(((((high + low) / 2) * 0.178404) + (vwap * (1 - 0.178404))), 3))) * -1)',
        '((rank(ts_corr(((open * 0.00817205) + (vwap * (1 - 0.00817205))), sum((ts_sum(volume,60)/60), 8), 6)) < rank((open - ts_min(open, 13)))) * -1)',
        '((rank(decay_linear(ts_delta(vwap, 3), 7)) + ts_rank(decay_linear(((((low * 0.96633) + (low * (1 - 0.96633))) - vwap) / (open - ((high + low) / 2))), 11), 6)) * -1)',
        '((rank((high - ts_min(high, 2)))^rank(ts_corr(group_neutralize(vwap, sector), group_neutralize((ts_sum(volume,20)/20), subindustry), 6))) * -1)',
        '((ts_rank(ts_corr(rank(high), rank((ts_sum(volume,15)/15)), 8), 13) < rank(ts_delta(((close * 0.518371) + (low * (1 - 0.518371))), 1))) * -1)',
        '((rank(ts_max(ts_delta(group_neutralize(vwap, industry), 2), 4))^ts_rank(ts_corr(((close * 0.490655) + (vwap * (1 - 0.490655))), (ts_sum(volume,20)/20), 4), 9)) * -1)',
        '((rank(ts_delta(vwap, 1))^ts_rank(ts_corr(group_neutralize(close, industry), (ts_sum(volume,50)/50), 17), 17)) * -1)',
        'max(ts_rank(decay_linear(ts_corr(ts_rank(close, 3), ts_rank((ts_sum(volume,180)/180), 12), 18), 4), 15), ts_rank(decay_linear((rank(((low + open) - (vwap + vwap)))^2), 16), 4))',
        '(rank(decay_linear(ts_corr(((high + low) / 2), (ts_sum(volume,40)/40), 8), 10)) / rank(decay_linear(ts_corr(ts_rank(vwap, 3), ts_rank(volume, 18), 6), 2)))',
        '(max(rank(decay_linear(ts_delta(vwap, 4), 2)), ts_rank(decay_linear(((ts_delta(((open * 0.147155) + (low * (1 - 0.147155))), 2) / ((open * 0.147155) + (low * (1 - 0.147155)))) * -1), 3), 16)) * -1)',
        '((rank(ts_corr(close, sum((ts_sum(volume,30)/30), 37), 15)) < rank(ts_corr(rank(((high * 0.0261661) + (vwap * (1 - 0.0261661)))), rank(volume), 11))) * -1)',
        '(rank(ts_corr(vwap, volume, 4)) < rank(ts_corr(rank(low), rank((ts_sum(volume,50)/50)), 12)))',
        '(max(rank(decay_linear(ts_delta(vwap, 1), 11)), ts_rank(decay_linear(ts_rank(ts_corr(group_neutralize(low, sector), (ts_sum(volume,81)/81), 8), 19), 17), 19)) * -1)',
        'min(rank(decay_linear(((((high + low) / 2) + high) - (vwap + high)), 20)), rank(decay_linear(ts_corr(((high + low) / 2), (ts_sum(volume,40)/40), 3), 5)))',
        '(rank(ts_corr(sum(((low * 0.352233) + (vwap * (1 - 0.352233))), 19), sum((ts_sum(volume,40)/40), 19), 6))^rank(ts_corr(rank(vwap), rank(volume), 5)))',
        '(rank(ts_delta(group_neutralize(((close * 0.60733) + (open * (1 - 0.60733))), sector), 1)) < rank(ts_corr(ts_rank(vwap, 3), ts_rank((ts_sum(volume,150)/150), 9), 14)))',
        '((rank(Sign(ts_delta(group_neutralize(((open * 0.868128) + (high * (1 - 0.868128))), industry), 4)))^ts_rank(ts_corr(high, (ts_sum(volume,10)/10), 5), 5)) * -1)',
        '((rank(Log(product(rank((rank(ts_corr(vwap, sum((ts_sum(volume,10)/10), 49), 8))^4)), 14))) < rank(ts_corr(rank(vwap), rank(volume), 5))) * -1)',
        '(min(rank(decay_linear(ts_delta(open, 1), 14)), ts_rank(decay_linear(ts_corr(group_neutralize(volume, sector), ((open * 0.634196) + (open * (1 - 0.634196))), 17), 6), 13)) * -1)',
        '((rank(ts_delay(((high - low) / (sum(close, 5) / 5)), 2)) * rank(rank(volume))) / (((high - low) / (sum(close, 5) / 5)) / (vwap - close)))',
        'signed_power(ts_rank((vwap - ts_max(vwap, 15)), 20), ts_delta(close, 4))',
        '(rank(ts_corr(((high * 0.876703) + (close * (1 - 0.876703))), (ts_sum(volume,30)/30), 9))^rank(ts_corr(ts_rank(((high + low) / 2), 3), ts_rank(volume, 10), 7)))',
        '((ts_rank(ts_corr(close, sum((ts_sum(volume,20)/20), 14), 6), 20) < rank(((open + close) - (vwap + open)))) * -1)',
        '(max(rank(decay_linear(ts_delta(((close * 0.369701) + (vwap * (1 - 0.369701))), 1), 2)), ts_rank(decay_linear(abs(ts_corr(group_neutralize((ts_sum(volume,81)/81), industry), close, 13)), 4), 14)) * -1)',
        'min(rank(decay_linear(((rank(open) + rank(low)) - (rank(high) + rank(close))), 8)), ts_rank(decay_linear(ts_corr(ts_rank(close, 8), ts_rank((ts_sum(volume,60)/60), 20), 8), 6), 2))',
        '(ts_rank(decay_linear(ts_corr(((low * 0.967285) + (low * (1 - 0.967285))), (ts_sum(volume,10)/10), 6), 5), 3) - ts_rank(decay_linear(ts_delta(group_neutralize(vwap, industry), 3), 10), 15))',
        '((rank((close - ts_max(close, 4)))^ts_rank(ts_corr(group_neutralize((ts_sum(volume,40)/40), subindustry), low, 5), 3)) * -1)',
        '((ts_rank(decay_linear(decay_linear(ts_corr(group_neutralize(close, industry), volume, 9), 16), 3), 4) - rank(decay_linear(ts_corr(vwap, (ts_sum(volume,30)/30), 4), 2))) * -1)',
        'min(ts_rank(decay_linear(((((high + low) / 2) + close) < (low + open)), 14), 18), ts_rank(decay_linear(ts_corr(rank(low), rank((ts_sum(volume,30)/30)), 7), 6), 6))',
        '(ts_rank(decay_linear(ts_corr(group_neutralize(vwap, industry), (ts_sum(volume,81)/81), 17), 19), 7) / rank(decay_linear(ts_delta(((close * 0.524434) + (vwap * (1 - 0.524434))), 2), 16)))',
        '((rank((vwap - ts_min(vwap, 11)))^ts_rank(ts_corr(ts_rank(vwap, 19), ts_rank((ts_sum(volume,60)/60), 4), 18), 2)) * -1)',
        '(rank((open - ts_min(open, 12))) < ts_rank((rank(ts_corr(sum(((high + low) / 2), 19), sum((ts_sum(volume,40)/40), 19), 12))^5), 11))',
        '(max(ts_rank(decay_linear(ts_corr(rank(vwap), rank(volume), 3), 4), 8), ts_rank(decay_linear(ts_arg_max(ts_corr(ts_rank(close, 7), ts_rank((ts_sum(volume,60)/60), 4), 3), 12), 14), 13)) * -1)',
        '((rank(decay_linear(ts_delta(group_neutralize(((low * 0.721001) + (vwap * (1 - 0.721001))), industry), 3), 20)) - ts_rank(decay_linear(ts_rank(ts_corr(ts_rank(low, 7), ts_rank((ts_sum(volume,60)/60), 17), 4), 18), 15), 6)) * -1)',
        '(rank(decay_linear(ts_corr(vwap, sum((ts_sum(volume,5)/5), 26), 4), 7)) - rank(decay_linear(ts_rank(ts_arg_min(ts_corr(rank(open), rank((ts_sum(volume,15)/15)), 20), 8), 6), 8)))',
        '((rank(ts_corr(sum(((high + low) / 2), 19), sum((ts_sum(volume,60)/60), 19), 8)) < rank(ts_corr(low, volume, 6))) * -1)',
        '(0 - (1 * (((1.5 * scale(group_neutralize(group_neutralize(rank(((((close - low) - (high - close)) / (high - low)) * volume)), subindustry), subindustry))) - scale(group_neutralize((ts_corr(close, rank((ts_sum(volume,20)/20)), 5) - rank(ts_arg_min(close, 30))), subindustry))) * (volume / (ts_sum(volume,20)/20)))))',
        '((close - open) / ((high - low) + 0.001))',
    ]

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

def sample_3():
    D = [1, 2, 5, 10, 20, 30, 50, 100] 
    commands = []
    for d in D:
        for p in PRICES:
            for p_or_m in P_or_M:
                for p_or_m_2 in P_or_M:
                    command = f'{p_or_m}rank({p_or_m_2}ts_mean({p}, {d}))'
                    commands.append(command)
    return commands

if __name__ == '__main__':
    funcs = [scale_and_corr, from_wq_1, from_wq_2, from_wq_3, from_arxiv, sample_1, sample_2, sample_3]
    [print(f.__name__, len(f())) for f in funcs]