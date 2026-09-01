from __future__ import annotations
import math, statistics

def wilson_interval(successes, n, confidence=0.95):
    if n <= 0: return (None, None)
    z = 1.959963984540054
    p = successes / n
    denom = 1 + z*z/n
    center = (p + z*z/(2*n)) / denom
    half = z * math.sqrt((p*(1-p) + z*z/(4*n))/n) / denom
    return max(0, center-half), min(1, center+half)

def mean_ci(values, confidence=0.95):
    xs = [float(x) for x in values if x is not None]
    if not xs: return (None, None, None)
    mean = sum(xs)/len(xs)
    if len(xs) == 1: return (mean, mean, mean)
    half = 1.959963984540054 * statistics.stdev(xs) / math.sqrt(len(xs))
    return mean, mean-half, mean+half
