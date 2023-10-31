This pull request adds a new trading strategy "kelly_criterion" to the trader and adds the parameter TRADING_STRATEGY that contains the trading strategy in use. The favoured type of strategy can be set as an enviconment variable. The current trading strategy "bet_amount_per_conf_threshold" is still the default when starting the trader. The new trading strategy is the Kelly Criterion and it is explained here. 

Note: For utilizing the strategy in an effective way, the parameter SAMPLE_BETS_CLOSING_DAYS has also been added and can be set as an environment variable. It determines the amount of days until markets' closing times and makes the trader only bet on those markets that close wihtin SAMPLE_BETS_CLOSING_DAYS amount of days. Small values for this parameter ensure that wins can be redeemed within short periods of time and can also be reinvested earlier. As the Kelly Criterion places bets based on the amount of tokens that are available to bet, this leads to a steeper profit curve. It is also useful to gather trading data within short timeframes and make adjustments to the trader. 

# Introduction
The Kelly Criterion is the calculation rule for the Kelly fraction $f^*$, which is the portion of the gambling capital to be wagered in order to maximize the profit considering the payoff odds and the probability of winning. The calculation rule is given by

$$
f^* = \frac{bp - (1 - p)}{b},
$$

where $f^*$ is the Kelly fraction of the bankroll, which is the maximum available gambling capital, $b$ is the net odds received on the wager (bet amount excluded), $p$ is the probability of winning, and $(1-p)$ is the probability of losing ([Beygelzimer et. al., 2012](#references)).

In traditional betting frameworks, the odds for a bet are usually fixed when placing a bet and stay the same regardless of the betting amount. The Kelly Criterion was originally designed for static odds and faces some challenges when being used in scenarios with dynamic odds. In prediction markets run by Constant Product Market Makers (CPMMs) the odds depend on the bet amount. As the Kelly Criterion calculates the optimal bet amount based on the odds, there exist an interdependence of bet amount and odds. The following sections provide a way to calculate the optimal absolute Kelly bet amount depending on the Bankroll and number of outcome tokens for each outcome before placing the bet. The here derived function only applies for prediction markets run by CPMMs with binary outcomes.

# Kelly equation with dynamic odds
## General Equation
The Kelly formula can be converted into 

$$
f^* = \frac{Q \cdot p - 1}{Q - 1},
$$

where $Q$ is the gross payoff odds, i.e., in the event of a win, $Q$ times the amount wagered $( Q > 1 )$ will be received, including the initial investment. 

As the Kelly formula calculates the fraction $f^*$ of the bankroll $B$ (Maximum available gambling capital) to bet it can be written as

$$
f^*=\frac{X}{B},
$$

where $X$ is the absolute Kelly bet amount. Setting both equations equal to each other results in 

$$
\frac{X}{B} = \frac{Q \cdot p - 1}{Q - 1}
$$

## Odds Function
The odds $Q$ for a bet in a prediction market run by a CPMM are calculated as

$$
Q=\frac{n_r}{X},
$$

where $n_r$ is the number of the selected outcome token received from placing a bet X, if the market closes with the answer selected outcome.

To calculate the number of received tokens $n_r$, the general bet placement algorithm of a CPMM prediction market needs to be understood: When a user submits a bet placement transaction to a prediction market with binary outcomes, this transaction includes among other parameters the investment amount $X$ and the vote for the selected asset class. In the following explanations we denote asset class $A$ as the asset class of the selected outcome. CPMMs are designed to always keep the product of their asset amounts $R_A$ and $R_B$ constant when a trade is done. With this condition a trading function for binary CPMM prediction markets can be defined as: 

$$
φ(R) = R_A \cdot R_B.
$$

As $A$ and $B$ are the only two asset classes that the Market contains, Asset $A$ cannot simply be traded with a token that is not contained within the market. This would reduce $R_A$ while leaving $R_B$ untouched and violate the constant product rule. Therefore, a purchase is done in two steps. First, tokens of each asset class are purchased proportional to the current reserves represented by their weights, ensuring that the asset prices do not change ([Angeris et. al., 2021](#references)). Next the purchased tokens of the not voted asset class are swapped to tokens of the voted asset class. So the total number of received tokens is

$$
n_r = n_A + n_{swap},
$$

where $n_A$ represents the number of $A$ tokens purchased from step 1 and $n_{swap}$ is the number of $A$ tokens received from trading the in step 1 purchased $B$ tokens $n_B$ to $A$ tokens.

### Step 1: Proportional asset purchase
In the first step the bet amount is split by the number of asset classes $N=2$ in the market and tokens $n_i$ of each asset class are minted proportionally to the current reserves. It is important to understand that this operation does not reduce the number of asset in the market, but it creates new tokens in return for the investment amount that was sent along with the bet placement transaction. The number of tokens minted can be calculated as 

$$
n_i = \frac{X}{Np_i}.
$$

$p_i$ is the reported price of one token of asset class $i$ in terms of the numeraire, which is the collateral token (e.g. xDAI) that the market uses to provide and remove liquidity (e.g. xDAI). The reported prices are their unscaled prices $P_i$ relative to the unscaled price of the numeraire $P_n$. 

$$
p_i = \frac{P_i}{P_n} 
$$

Given the trading function $φ(R) = R_A \cdot R_B$ their gradient 

$$
P=∇φ(R)
$$

is denoted as the vector of unscaled prices ([Angeris et. al., 2021](#references)). This results in the unscaled prices $P_A=R_B$ and $P_B=R_A$. 

If we want to calculate the amount of assets that we get from sending $X$ to the market, we need to know their reported prices in the numeraire currency xDAI. The reported prices of assets in a prediction market always add up to 1 as only the tokens of one outcome will be worth 1 xDAI after market closing ([Chen & Pennock, 2012](#references)). Thus, the sum of the unscaled prices of assets in the market equals the unscaled price of the numeraire, which is also the sum of the partial derivatives of the trading function for each asset class: $P_n=R_A+R_B$. With this the prices $p_i$ can be calculated by

$$
p_A = \frac{R_B}{R_B+R_A} 
$$

$$
p_B = \frac{R_A}{R_B+R_A} 
$$

and the number of tokens minted for each asset class are:

$$
n_A = \frac{X(R_B + R_A)}{N\cdot R_B}
$$

$$
n_B = \frac{X(R_B + R_A)}{N\cdot R_A}.
$$

### Step 2: Swap to voted outcome asset

Next, the created assets $n_B$ of the not voted asset class $B$ are swapped to tokens of the voted asset class $A$. The number of received tokens from the swap is the difference in the reserves of asset class $A$ before and after the swap:

$$
n_{swap} = R_A - R_A^+
$$

$n_{swap}$ can be calculated using the trading function $φ(R) = R_A \cdot R_B$:

$$
φ(R^+) = φ(R)
$$ 

$$
R_A^+ \cdot R_B^+ = R_A \cdot R_B
$$ 

$$
R_A^+ = \frac{R_A \cdot R_B}{R_B^+}
$$

$R_A^+$ and $R_B^+$ represent the new asset reserves for asset class $A$ and $B$ after the trade. With $R_B^+ = R_B + n_B$ we get

$$
n_{swap} = R_A - \frac{R_A \cdot R_B}{R_B + \frac{X(R_B+R_A)}{N \cdot R_A}}.
$$

It follows

$$
n_r = \frac{X(R_B + R_A)}{N\cdot R_B} + R_A - \frac{R_A \cdot R_B}{R_B + \frac{X(R_B+R_A)}{N \cdot R_A}},
$$

and

$$
Q = \frac{\frac{X(R_B + R_A)}{N\cdot R_B} + R_A - \frac{R_A \cdot R_B}{R_B + \frac{X(R_B+R_A)}{N \cdot R_A}}}{X}
$$


## Solve Kelly function for $X$
The Odds depending on the investment amount $X$ can now be inserted in the original Kelly function and solved for $X$:

$$
f^* = \frac{\frac{\frac{X(R_B + R_A)}{N\cdot R_B} + R_A - \frac{R_A \cdot R_B}{R_B + \frac{X(R_B+R_A)}{N \cdot R_A}}}{X} \cdot p - 1}{\frac{\frac{X(R_B + R_A)}{N\cdot R_B} + R_A - \frac{R_A \cdot R_B}{R_B + \frac{X(R_B+R_A)}{N \cdot R_A}}}{X} - 1}
$$

For easier notation we replace $R_A$ with $a$, $R_B$ with $b$ and set $N=2$. After [simplification](https://www.symbolab.com/solver/functions-calculator/simplify%20%5Cfrac%7B%5Cfrac%7B%5Cfrac%7BX%5Cleft(b%20%2B%20a%5Cright)%7D%7B2b%7D%20%2B%20a%20-%20%5Cfrac%7Bab%7D%7Bb%20%2B%20%5Cfrac%7BX%5Cleft(b%2Ba%5Cright)%7D%7B2a%7D%7D%7D%7BX%7D%20%5Ccdot%20p%20-%201%7D%7B%5Cfrac%7B%5Cfrac%7BX%5Cleft(b%20%2B%20a%5Cright)%7D%7B2b%7D%20%2B%20a%20-%20%5Cfrac%7Bab%7D%7Bb%20%2B%20%5Cfrac%7BX%5Cleft(b%2Ba%5Cright)%7D%7B2a%7D%7D%7D%7BX%7D%20-%201%7D?or=input) the function looks as follows:


$$
f^* =\frac{-2xab-2xb^2-4b^2a+xpa^2+2xpab+xpb^2+4pa^2b+4pab^2}{xa^2-xb^2+4a^2b}
$$

Most prediction markets take fees for placing a bet based on the bet amount. The equation can be extended by a fee factor $f$ with $0 \leq f \leq 1$ that discounts the investment amount $X$:

$$
f^* =\frac{-2xfab-2xfb^2-4b^2a+xfpa^2+2xfpab+xfpb^2+4pa^2b+4pab^2}{xfa^2-xfb^2+4a^2b}
$$



Using $f^* = \frac{X}{B}$, the equation can be [solved](https://www.symbolab.com/solver/functions-calculator/%5Cfrac%7Bx%7D%7BB%7D%3D%5Cfrac%7B-2xfab-2xfb%5E%7B2%7D-4b%5E%7B2%7Da%2Bxfpa%5E%7B2%7D%2B2xfpab%2Bxfpb%5E%7B2%7D%2B4pa%5E%7B2%7Db%2B4pab%5E%7B2%7D%7D%7Bxfa%5E%7B2%7D-xfb%5E%7B2%7D%2B4a%5E%7B2%7Db%7D?or=input) for $X$:

$$
X=\frac{-4a^2b+Bb^2pf+2Babpf+Ba^2pf-2Bb^2-f2Babf\pm\sqrt{(4a^2b-Bb^2pf-2Babpf-Ba^2pf+2Bb^2f+2Babf)^2-4(a^2f-b^2f)(-4Bab^2p-4Ba^2bp+4Bab^2)}}{2(a^2f-b^2f)}
$$

Additionally if a prediction contains along with the probability score also a confidence score $c$, the probability $p$ can be reduced by $c$ with $0 \leq c \leq 1$, resulting in the updated equation:

$$
X=\frac{-4a^2b+Bb^2pcf+2Babpcf+Ba^2pcf-2Bb^2-f2Babf\pm\sqrt{(4a^2b-Bb^2pcf-2Babpcf-Ba^2pcf+2Bb^2f+2Babf)^2-4(a^2f-b^2f)(-4Bab^2pc-4Ba^2bpc+4Bab^2)}}{2(a^2f-b^2f)}
$$

# Conclusion
The solved equation for X calculates the Kelly bet amount for the outcome of a CPMM prediction market with binary outcomes based on the current reserves $R_i=a$, $R_B=b$, a probability $p$ obtained from an external source, the market fees $f$ and the current bankroll $B$, which is the total amount available to bet.

# References
**Angeris, G., Agrawal, A., Evans, A., Chitra, T., & Boyd, S.** (2021). *Constant Function Market Makers: Multi-Asset Trades via Convex Optimization*. arXiv preprint [arXiv:2107.12484 [math.OC]](https://arxiv.org/abs/2107.12484).

**Beygelzimer, A., Langford, J., & Pennock, D.** (2012). *Learning Performance of Prediction Markets with Kelly Bettors*. arXiv preprint [arXiv:1201.6655 [cs.AI]](https://arxiv.org/abs/1201.6655).

**Chen, Y., & Pennock, D. M.** (2012). *A Utility Framework for Bounded-Loss Market Makers*. arXiv preprint [arXiv:1206.5252 [cs.GT]](https://arxiv.org/abs/1206.5252).

