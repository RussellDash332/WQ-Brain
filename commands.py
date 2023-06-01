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

# from https://arxiv.org/ftp/arxiv/papers/1601/1601.00991.pdf and https://github.com/drtienduong/101alpha/blob/master/101alpha_Convert.txt
def from_arxiv():
    return [
        '(rank(ts_arg_max(signed_power(((returns < 0) ? ts_std_dev(returns, 20) : close), 2.), 5)) -0.5)',
        '(-1 * ts_corr(rank(ts_delta(log(volume), 2)), rank(((close - open) / open)), 6))',
        '(-1 * ts_corr(rank(open), rank(volume), 10))',
        '(-1 * Ts_Rank(rank(low), 9))',
        '(rank((open - (ts_sum(vwap, 10) / 10))) * (-1 * abs(rank((close - vwap)))))',
        '(-1 * ts_corr(open, volume, 10)) ',
        '((ts_mean(volume,20) < volume) ? ((-1 * ts_rank(abs(ts_delta(close, 7)), 60)) * sign(ts_delta(close, 7))) : (-1 * 1))',
        '(-1 * rank(((ts_sum(open, 5) * ts_sum(returns, 5)) - ts_delay((ts_sum(open, 5) * ts_sum(returns, 5)), 10)))) ',
        '((0 < ts_min(ts_delta(close, 1), 5)) ? ts_delta(close, 1) : ((ts_max(ts_delta(close, 1), 5) < 0) ? ts_delta(close, 1) : (-1 * ts_delta(close, 1)))) ',
        'rank(((0 < ts_min(ts_delta(close, 1), 4)) ? ts_delta(close, 1) : ((ts_max(ts_delta(close, 1), 4) < 0) ? ts_delta(close, 1) : (-1 * ts_delta(close, 1))))) ',
        '((rank(ts_max((vwap - close), 3)) + rank(ts_min((vwap - close), 3))) * rank(ts_delta(volume, 3)))',
        '(sign(ts_delta(volume, 1)) * (-1 * ts_delta(close, 1)))',
        '(-1 * rank(ts_covariance(rank(close), rank(volume), 5)))',
        '((-1 * rank(ts_delta(returns, 3))) * ts_corr(open, volume, 10))',
        '(-1 * ts_sum(rank(ts_corr(rank(high), rank(volume), 3)), 3))',
        '(-1 * rank(ts_covariance(rank(high), rank(volume), 5)))',
        '(((-1 * rank(ts_rank(close, 10))) * rank(ts_delta(ts_delta(close, 1), 1))) *rank(ts_rank((volume / ts_mean(volume,20)), 5)))',
        '(-1 * rank(((ts_std_dev(abs((close - open)), 5) + (close - open)) + ts_corr(close, open,10))))',
        '((-1 * sign(((close - ts_delay(close, 7)) + ts_delta(close, 7)))) * (1 + rank((1 + ts_sum(returns,250)))))',
        '(((-1 * rank((open - ts_delay(high, 1)))) * rank((open - ts_delay(close, 1)))) * rank((open -ts_delay(low, 1))))',
        '((((ts_sum(close, 8) / 8) + ts_std_dev(close, 8)) < (ts_sum(close, 2) / 2)) ? (-1 * 1) : (((ts_sum(close,2) / 2) < ((ts_sum(close, 8) / 8) - ts_std_dev(close, 8))) ? 1 : (((1 < (volume / ts_mean(volume,20))) || ((volume /ts_mean(volume,20)) == 1)) ? 1 : (-1 * 1))))',
        '(-1 * (ts_delta(ts_corr(high, volume, 5), 5) * rank(ts_std_dev(close, 20))))',
        '(((ts_sum(high, 20) / 20) < high) ? (-1 * ts_delta(high, 2)) : 0)',
        '((((ts_delta((ts_sum(close, 100) / 100), 100) / ts_delay(close, 100)) < 0.05) ||((ts_delta((ts_sum(close, 100) / 100), 100) / ts_delay(close, 100)) == 0.05)) ? (-1 * (close - ts_min(close,100))) : (-1 * ts_delta(close, 3)))',
        'rank(((((-1 * returns) * ts_mean(volume,20)) * vwap) * (high - close)))',
        '(-1 * ts_max(ts_corr(ts_rank(volume, 5), ts_rank(high, 5), 5), 3))',
        '((0.5 < rank((ts_sum(ts_corr(rank(volume), rank(vwap), 6), 2) / 2.0))) ? (-1 * 1) : 1)',
        'scale(((ts_corr(ts_mean(volume,20), low, 5) + ((high + low) / 2)) - close))',
        '(min(ts_product(rank(rank(scale(log(ts_sum(ts_min(rank(rank((-1 * rank(ts_delta((close - 1),5))))), 2), 1))))), 1), 5) + ts_rank(ts_delay((-1 * returns), 6), 5))',
        '(((1.0 - rank(((sign((close - ts_delay(close, 1))) + sign((ts_delay(close, 1) - ts_delay(close, 2)))) +sign((ts_delay(close, 2) - ts_delay(close, 3)))))) * ts_sum(volume, 5)) / ts_sum(volume, 20))',
        '((rank(rank(rank(ts_decay_linear((-1 * rank(rank(ts_delta(close, 10)))), 10)))) + rank((-1 *ts_delta(close, 3)))) + sign(scale(ts_corr(ts_mean(volume,20), low, 12))))',
        '(scale(((ts_sum(close, 7) / 7) - close)) + (20 * scale(ts_corr(vwap, ts_delay(close, 5),230))))',
        'rank((-1 * ((1 - (open / close))^1)))',
        'rank(((1 - rank((ts_std_dev(returns, 2) / ts_std_dev(returns, 5)))) + (1 - rank(ts_delta(close, 1)))))',
        '((Ts_Rank(volume, 32) * (1 - Ts_Rank(((close + high) - low), 16))) * (1 -Ts_Rank(returns, 32)))',
        '(((((2.21 * rank(ts_corr((close - open), ts_delay(volume, 1), 15))) + (0.7 * rank((open- close)))) + (0.73 * rank(Ts_Rank(ts_delay((-1 * returns), 6), 5)))) + rank(abs(ts_corr(vwap,ts_mean(volume,20), 6)))) + (0.6 * rank((((ts_sum(close, 200) / 200) - open) * (close - open)))))',
        '(rank(ts_corr(ts_delay((open - close), 1), close, 200)) + rank((open - close)))',
        '((-1 * rank(Ts_Rank(close, 10))) * rank((close / open)))',
        '((-1 * rank((ts_delta(close, 7) * (1 - rank(ts_decay_linear((volume / ts_mean(volume,20)), 9)))))) * (1 +rank(ts_sum(returns, 250))))',
        '((-1 * rank(ts_std_dev(high, 10))) * ts_corr(high, volume, 10))',
        '(((high * low)^0.5) - vwap)',
        '(rank((vwap - close)) / rank((vwap + close)))',
        '(ts_rank((volume / ts_mean(volume,20)), 20) * ts_rank((-1 * ts_delta(close, 7)), 8))',
        '(-1 * ts_corr(high, rank(volume), 5))',
        '(-1 * ((rank((ts_sum(ts_delay(close, 5), 20) / 20)) * ts_corr(close, volume, 2)) *rank(ts_corr(ts_sum(close, 5), ts_sum(close, 20), 2))))',
        '((0.25 < (((ts_delay(close, 20) - ts_delay(close, 10)) / 10) - ((ts_delay(close, 10) - close) / 10))) ?(-1 * 1) : (((((ts_delay(close, 20) - ts_delay(close, 10)) / 10) - ((ts_delay(close, 10) - close) / 10)) < 0) ? 1 :((-1 * 1) * (close - ts_delay(close, 1)))))',
        '((((rank((1 / close)) * volume) / ts_mean(volume,20)) * ((high * rank((high - close))) / (ts_sum(high, 5) /5))) - rank((vwap - ts_delay(vwap, 5))))',
        '(group_neutralize(((ts_corr(ts_delta(close, 1), ts_delta(ts_delay(close, 1), 1), 250) *ts_delta(close, 1)) / close), subindustry) / ts_sum(((ts_delta(close, 1) / ts_delay(close, 1))^2), 250))',
        '(((((ts_delay(close, 20) - ts_delay(close, 10)) / 10) - ((ts_delay(close, 10) - close) / 10)) < (-1 *0.1)) ? 1 : ((-1 * 1) * (close - ts_delay(close, 1))))',
        '(-1 * ts_max(rank(ts_corr(rank(volume), rank(vwap), 5)), 5))',
        '(((((ts_delay(close, 20) - ts_delay(close, 10)) / 10) - ((ts_delay(close, 10) - close) / 10)) < (-1 *0.05)) ? 1 : ((-1 * 1) * (close - ts_delay(close, 1))))',
        '((((-1 * ts_min(low, 5)) + ts_delay(ts_min(low, 5), 5)) * rank(((ts_sum(returns, 240) -ts_sum(returns, 20)) / 220))) * ts_rank(volume, 5))',
        '(-1 * ts_delta((((close - low) - (high - close)) / (close - low)), 9))',
        '((-1 * ((low - close) * (open^5))) / ((low - high) * (close^5)))',
        '(-1 * ts_corr(rank(((close - ts_min(low, 12)) / (ts_max(high, 12) - ts_min(low,12)))), rank(volume), 6))',
        '(0 - (1 * (rank((ts_sum(returns, 10) / ts_sum(ts_sum(returns, 2), 3))) * rank((returns * cap)))))',
        '(0 - (1 * ((close - vwap) / ts_decay_linear(rank(ts_arg_max(close, 30)), 2))))',
        '(-1 * Ts_Rank(ts_decay_linear(ts_corr(group_neutralize(vwap, sector), volume,4), 8), 6))',
        '(-1 * Ts_Rank(ts_decay_linear(ts_corr(group_neutralize(((vwap * 0.728317) + (vwap *(1 - 0.728317))), industry), volume, 4), 16), 8))',
        '(0 - (1 * ((2 * scale(rank(((((close - low) - (high - close)) / (high - low)) * volume)))) -scale(rank(ts_arg_max(close, 10))))))',
        '(rank((vwap - ts_min(vwap, 16))) < rank(ts_corr(vwap, ts_mean(volume,180), 17)))',
        '((rank(ts_corr(vwap, ts_sum(ts_mean(volume,20), 22), 10)) < rank(((rank(open) +rank(open)) < (rank(((high + low) / 2)) + rank(high))))) * -1)',
        '((rank(ts_decay_linear(ts_delta(group_neutralize(close, industry), 2), 8))- rank(ts_decay_linear(ts_corr(((vwap * 0.318108) + (open * (1 - 0.318108))), ts_sum(ts_mean(volume,180),37), 14), 12))) * -1)',
        '((rank(ts_corr(ts_sum(((open * 0.178404) + (low * (1 - 0.178404))), 13),ts_sum(ts_mean(volume,120), 13), 17)) < rank(ts_delta(((((high + low) / 2) * 0.178404) + (vwap * (1 -0.178404))), 4 ))) * -1)',
        '((rank(ts_corr(((open * 0.00817205) + (vwap * (1 - 0.00817205))), ts_sum(ts_mean(volume,60),9), 6)) < rank((open - ts_min(open, 14)))) * -1)',
        '((rank(ts_decay_linear(ts_delta(vwap, 4), 7)) + Ts_Rank(ts_decay_linear(((((low* 0.96633) + (low * (1 - 0.96633))) - vwap) / (open - ((high + low) / 2))), 11), 7)) * -1)',
        '((rank((high - ts_min(high, 2)))^rank(ts_corr(group_neutralize(vwap,sector), group_neutralize(ts_mean(volume,20), subindustry), 6))) * -1)',
        '((Ts_Rank(ts_corr(rank(high), rank(ts_mean(volume,15)), 9), 14) <rank(ts_delta(((close * 0.518371) + (low * (1 - 0.518371))), 1))) * -1)',
        '((rank(ts_max(ts_delta(group_neutralize(vwap, industry), 3),5))^Ts_Rank(ts_corr(((close * 0.490655) + (vwap * (1 - 0.490655))), ts_mean(volume,20), 5),9)) * -1)',
        '((rank(ts_delta(vwap, 1))^Ts_Rank(ts_corr(group_neutralize(close,industry), ts_mean(volume,50), 18), 18)) * -1)',
        'max(Ts_Rank(ts_decay_linear(ts_corr(Ts_Rank(close, 3), Ts_Rank(ts_mean(volume,180),12), 18), 4), 16), Ts_Rank(ts_decay_linear((rank(((low + open) - (vwap +vwap)))^2), 16), 4))',
        '(rank(ts_decay_linear(ts_corr(((high + low) / 2), ts_mean(volume,40), 9), 10)) /rank(ts_decay_linear(ts_corr(Ts_Rank(vwap, 4), Ts_Rank(volume, 19), 7),3)))',
        '(max(rank(ts_decay_linear(ts_delta(vwap, 5), 3)),Ts_Rank(ts_decay_linear(((ts_delta(((open * 0.147155) + (low * (1 - 0.147155))), 2) / ((open *0.147155) + (low * (1 - 0.147155)))) * -1), 3), 17)) * -1)',
        '((rank(ts_corr(close, ts_sum(ts_mean(volume,30), 37), 15)) <rank(ts_corr(rank(((high * 0.0261661) + (vwap * (1 - 0.0261661)))), rank(volume), 11)))* -1)',
        '(rank(ts_corr(vwap, volume, 4)) < rank(ts_corr(rank(low), rank(ts_mean(volume,50)),12)))',
        '(max(rank(ts_decay_linear(ts_delta(vwap, 1), 12)),Ts_Rank(ts_decay_linear(Ts_Rank(ts_corr(group_neutralize(low, sector), ts_mean(volume,81),8), 20), 17), 19)) * -1)',
        'min(rank(ts_decay_linear(((((high + low) / 2) + high) - (vwap + high)), 20)),rank(ts_decay_linear(ts_corr(((high + low) / 2), ts_mean(volume,40), 3), 6)))',
        '(rank(ts_corr(ts_sum(((low * 0.352233) + (vwap * (1 - 0.352233))), 20),ts_sum(ts_mean(volume,40), 20), 7))^rank(ts_corr(rank(vwap), rank(volume), 6)))',
        '(rank(ts_delta(group_neutralize(((close * 0.60733) + (open * (1 - 0.60733))),sector), 1)) < rank(ts_corr(Ts_Rank(vwap, 4), Ts_Rank(ts_mean(volume,150),9), 15)))',
        '((rank(Sign(ts_delta(group_neutralize(((open * 0.868128) + (high * (1 - 0.868128))),industry), 4)))^Ts_Rank(ts_corr(high, ts_mean(volume,10), 5), 6)) * -1)',
        '((rank(Log(ts_product(rank((rank(ts_corr(vwap, ts_sum(ts_mean(volume,10), 50),9))^4)), 15))) < rank(ts_corr(rank(vwap), rank(volume), 5))) * -1)',
        '(min(rank(ts_decay_linear(ts_delta(open, 2), 15)),Ts_Rank(ts_decay_linear(ts_corr(group_neutralize(volume, sector), ((open * 0.634196) +(open * (1 - 0.634196))), 17), 7), 13)) * -1)',
        '((rank(ts_delay(((high - low) / (ts_sum(close, 5) / 5)), 2)) * rank(rank(volume))) / (((high -low) / (ts_sum(close, 5) / 5)) / (vwap - close)))',
        'signed_power(Ts_Rank((vwap - ts_max(vwap, 15)), 21), ts_delta(close,5))',
        '(rank(ts_corr(((high * 0.876703) + (close * (1 - 0.876703))), ts_mean(volume,30),10))^rank(ts_corr(Ts_Rank(((high + low) / 2), 4), Ts_Rank(volume, 10),7)))',
        '((Ts_Rank(ts_corr(close, ts_sum(ts_mean(volume,20), 14), 6), 20) < rank(((open+ close) - (vwap + open)))) * -1)',
        '(max(rank(ts_decay_linear(ts_delta(((close * 0.369701) + (vwap * (1 - 0.369701))),2), 3)), Ts_Rank(ts_decay_linear(abs(ts_corr(group_neutralize(ts_mean(volume,81),industry), close, 13)), 5), 14)) * -1)',
        'min(rank(ts_decay_linear(((rank(open) + rank(low)) - (rank(high) + rank(close))),8)), Ts_Rank(ts_decay_linear(ts_corr(Ts_Rank(close, 8), Ts_Rank(ts_mean(volume,60),21), 8), 7), 3))',
        '(Ts_Rank(ts_decay_linear(ts_corr(((low * 0.967285) + (low * (1 - 0.967285))), ts_mean(volume,10),7), 6), 4) - Ts_Rank(ts_decay_linear(ts_delta(group_neutralize(vwap,industry), 3), 10), 15))',
        '((rank((close - ts_max(close, 5)))^Ts_Rank(ts_corr(group_neutralize(ts_mean(volume,40),subindustry), low, 5), 3)) * -1)',
        '((Ts_Rank(ts_decay_linear(ts_decay_linear(ts_corr(group_neutralize(close,industry), volume, 10), 16), 4), 5) -rank(ts_decay_linear(ts_corr(vwap, ts_mean(volume,30), 4), 3))) * -1)',
        'min(Ts_Rank(ts_decay_linear(((((high + low) / 2) + close) < (low + open)), 15),19), Ts_Rank(ts_decay_linear(ts_corr(rank(low), rank(ts_mean(volume,30)), 8), 7),7))',
        '(Ts_Rank(ts_decay_linear(ts_corr(group_neutralize(vwap, industry), ts_mean(volume,81),17), 20), 8) / rank(ts_decay_linear(ts_delta(((close * 0.524434) + (vwap * (1 -0.524434))), 3), 16)))',
        '((rank((vwap - ts_min(vwap, 12)))^Ts_Rank(ts_corr(Ts_Rank(vwap,20), Ts_Rank(ts_mean(volume,60), 4), 18), 3)) * -1)',
        '(rank((open - ts_min(open, 12))) < Ts_Rank((rank(ts_corr(ts_sum(((high + low)/ 2), 19), ts_sum(ts_mean(volume,40), 19), 13))^5), 12))',
        '(max(Ts_Rank(ts_decay_linear(ts_corr(rank(vwap), rank(volume), 4),4), 8), Ts_Rank(ts_decay_linear(ts_arg_max(ts_corr(Ts_Rank(close, 7),Ts_Rank(ts_mean(volume,60), 4), 4), 12), 14), 13)) * -1)',
        '((rank(ts_decay_linear(ts_delta(group_neutralize(((low * 0.721001) + (vwap * (1 - 0.721001))),industry), 3), 20)) - Ts_Rank(ts_decay_linear(Ts_Rank(ts_corr(Ts_Rank(low,8), Ts_Rank(ts_mean(volume,60), 17), 5), 19), 16), 7)) * -1)',
        '(rank(ts_decay_linear(ts_corr(vwap, ts_sum(ts_mean(volume,5), 26), 5), 7)) -rank(ts_decay_linear(Ts_Rank(ts_arg_min(ts_corr(rank(open), rank(ts_mean(volume,15)), 21), 9),7), 8)))',
        '((rank(ts_corr(ts_sum(((high + low) / 2), 20), ts_sum(ts_mean(volume,60), 20), 9)) <rank(ts_corr(low, volume, 6))) * -1)',
        '(0 - (1 * (((1.5 * scale(group_neutralize(group_neutralize(rank(((((close - low) - (high -close)) / (high - low)) * volume)), subindustry), subindustry))) -scale(group_neutralize((ts_corr(close, rank(ts_mean(volume,20)), 5) - rank(ts_arg_min(close, 30))),subindustry))) * (volume / ts_mean(volume,20)))))',
        '((close - open) / ((high - low) + 0.001))'
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