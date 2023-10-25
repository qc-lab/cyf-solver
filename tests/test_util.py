from QHyper.util import (
    weighted_avg_evaluation, sort_solver_results, add_evaluation_to_results)

SOLVER_RESULTS = {
    '00000': 0.05214763286171284,
    '00001': 0.047456206684648256,
    '00010': 0.06747850816202812,
    '00011': 0.1207346328578372,
    '00100': 0.019935786631066668,
    '00101': 0.005007856642765267,
    '00110': 0.01005580974423947,
    '00111': 0.022499649875754597,
    '01000': 0.027125455378550354,
    '01001': 0.028211751547797856,
    '01010': 0.008350237539872896,
    '01011': 0.03202691762829461,
    '01100': 0.003062964564235747,
    '01101': 0.012204283239546117,
    '01110': 0.08663358863146411,
    '01111': 0.003494550808116975,
    '10000': 0.027125455378550347,
    '10001': 0.028211751547797856,
    '10010': 0.008350237539872908,
    '10011': 0.03202691762829463,
    '10100': 0.0030629645642357367,
    '10101': 0.012204283239546128,
    '10110': 0.08663358863146413,
    '10111': 0.0034945508081169743,
    '11000': 0.010496304111296366,
    '11001': 0.015135842196383593,
    '11010': 0.11572493713978199,
    '11011': 0.010027077049355402,
    '11100': 0.007232224863605771,
    '11101': 0.013160777387316473,
    '11110': 0.039326178047044726,
    '11111': 0.0413610770694037,
}


def score_function(x, p):
    if '10' == x[:2]:
        return p
    return x.count("1")*x.count("0")


def test_weighted_avg_evaluation():
    assert weighted_avg_evaluation(
        SOLVER_RESULTS, score_function, penalty=-1, limit_results=10,
        normalize=True
    ) == 3.5342418902991257


def test_sort_solver_results():
    assert sort_solver_results(SOLVER_RESULTS, limit_results=10) == {
        '00000': 0.05214763286171284,
        '00001': 0.047456206684648256,
        '00010': 0.06747850816202812,
        '00011': 0.1207346328578372,
        '01110': 0.08663358863146411,
        '10011': 0.03202691762829463,
        '10110': 0.08663358863146413,
        '11010': 0.11572493713978199,
        '11110': 0.039326178047044726,
        '11111': 0.0413610770694037,
    }


def test_add_evaluation_to_results():
    assert add_evaluation_to_results(
            SOLVER_RESULTS, score_function, -1) == {
        '00000': (0.05214763286171284, 0),
        '00001': (0.047456206684648256, 4),
        '00010': (0.06747850816202812, 4),
        '00011': (0.1207346328578372, 6),
        '00100': (0.019935786631066668, 4),
        '00101': (0.005007856642765267, 6),
        '00110': (0.01005580974423947, 6),
        '00111': (0.022499649875754597, 6),
        '01000': (0.027125455378550354, 4),
        '01001': (0.028211751547797856, 6),
        '01010': (0.008350237539872896, 6),
        '01011': (0.03202691762829461, 6),
        '01100': (0.003062964564235747, 6),
        '01101': (0.012204283239546117, 6),
        '01110': (0.08663358863146411, 6),
        '01111': (0.003494550808116975, 4),
        '10000': (0.027125455378550347, -1),
        '10001': (0.028211751547797856, -1),
        '10010': (0.008350237539872908, -1),
        '10011': (0.03202691762829463, -1),
        '10100': (0.0030629645642357367, -1),
        '10101': (0.012204283239546128, -1),
        '10110': (0.08663358863146413, -1),
        '10111': (0.0034945508081169743, -1),
        '11000': (0.010496304111296366, 6),
        '11001': (0.015135842196383593, 6),
        '11010': (0.11572493713978199, 6),
        '11011': (0.010027077049355402, 4),
        '11100': (0.007232224863605771, 6),
        '11101': (0.013160777387316473, 4),
        '11110': (0.039326178047044726, 4),
        '11111': (0.0413610770694037, 0)
    }