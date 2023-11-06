import numpy as np
from scipy.stats import hypergeom, stats

gameturn = 3
wantinhand = 1
cardsindeck = 13

cardsinhand = 7 + gameturn
exactlyone = hypergeom.pmf(wantinhand, 100, cardsindeck, cardsinhand)
oneorless = hypergeom.cdf(wantinhand, 100, cardsindeck, cardsinhand)
k = np.arange(wantinhand)
zero = hypergeom.pmf(k, 100, cardsindeck, cardsinhand)
oneormore = 1 - zero[0]
print(round(exactlyone*100, 2))
print(round(oneorless*100, 2))
print(round(zero[0]*100, 2))
print(round(oneormore*100, 2))
