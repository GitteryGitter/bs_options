from dataclasses import dataclass
import math
from scipy.stats import norm
import numpy as np
import os

@dataclass
class OptionParams:
    under: float # Current price of the underlying (S)
    strike: float # Strike price (K)
    divident: float # Divident payed out by the underlying asset
    maturity: float # Time to maturity in years (T)
    rate: float # Risk-free interest rate (r)
    volatility: float # Volatility (sigma)
    call: bool # Is it a call?
    name: str # name of the option


class Option:
    def __init__(self, params):
        self.under = params.under
        self.strike = params.strike
        self.divident = params.divident
        self.mat = params.maturity
        self.r = params.rate
        self.vol = params.volatility
        self.call = params.call
        self.name = params.name

    def get_params(self):
        return self.under, self.strike, self.mat, self.r, self.vol, self.divident


    def d1(self):
        U, S, M, R, V, q = self.get_params()

        return (math.log( U / S ) + ( R - q + 0.5 * V ** 2 ) * M ) / ( V * math.sqrt(M))


    def delta(self):
        """
        Computes the change of the option in respondse to the change of the underlying asset.
        """
        U, S, M, R, V, q = self.get_params()
        d1 = self.d1()

        if self.call == True:
            return math.exp(-q * M) * norm.cdf(d1)      
        else:
            return math.exp(-q * M) * ( norm.cdf(d1) - 1 )


    def gamma(self):
        """"
        Computes the sensitivity of delta with respect to the price of the underlying asset.
        """
        U, S, M, R, V, q = self.get_params()  
        d1 = self.d1()

        return math.exp(-q * M) * norm.pdf(d1) / ( U * V * math.sqrt(M) )


    def vega(self):
        U, S, M, R, V, q = self.get_params()
        d1 = self.d1()
        
        return U * math.exp(-q * M) * math.sqrt(M) * norm.pdf(d1)


    def theta(self):
        """
        Computes the sensitivity of the price of the option with respect to the change in the time to maturity.
        """
        U, S, M, R, V, q = self.get_params()
        d1 = self.d1()
        d2 = d1 - V * math.sqrt(M)

        if self.call == True:
            return (
                - ( U * math.exp(-q * M) * norm.pdf(d1) * V ) / ( 2 * math.sqrt(M) ) 
                + U * q * math.exp(-q * M) * norm.cdf(d1) 
                - R * S * math.exp( - R * M ) * norm.cdf(d2)   
            )
        else:
            return (
                - ( U * math.exp(-q * M) * norm.pdf(d1) * V ) / ( 2 * math.sqrt(M) ) 
                - q * U * math.exp(-q * M) * norm.cdf(-d1)
                + R * S * math.exp(- R * M) * norm.cdf( -d2 )
            )


    def rho(self):
        U, S, M, R, V, q = self.get_params()
        d1 = self.d1()
        d2 = d1 - V * math.sqrt(M)

        if self.call == True:
            return S * M * math.exp(- R * M) * norm.cdf(d2)    
        else:
            return - S * M * math.exp(- R * M) * norm.cdf(-d2)
            
        
    def price(self):
        """Computes the Black-Scholes option price"""
        U, S, M, R, V, q = self.get_params()
        d1 = self.d1()
        d2 = d1 - V * math.sqrt(M)
        
        if self.call:
            return U * math.exp(-q * M) * norm.cdf(d1) - S * math.exp(-R * M) * norm.cdf(d2)
        else:
            return S * math.exp(-R * M) * norm.cdf(-d2) - U * math.exp(-q * M) * norm.cdf(-d1)


    def price_evolv(self, mat = None):
        """Computes the Black-Scholes option price based on the current attributes of the option"""
        if mat == None:
            U, S, M, R, V, q = self.get_params()
        else:
            U, S, _, R, V, q = self.get_params()
            M = mat

        d1 = (math.log( U / S ) + ( R - q + 0.5 * V ** 2 ) * M ) / ( V * math.sqrt(M))
        d2 = d1 - V * math.sqrt(M)
        
        if self.call:
            return U * norm.cdf(d1) - S * math.exp(-R * M) * norm.cdf(d2)
        else:
            return S * math.exp(-R * M) * norm.cdf(-d2) - U * norm.cdf(-d1)
    

    def brown_simul(self, n_simuls=250, n_steps = None, drift = None, sigma = None, ):
        """Geometric Brownian Motion simulation engine"""
        U, S, M, R, V, q = self.get_params()
        
        mu = drift if drift is not None else (R - q)
        sig = sigma if sigma is not None else V
        if n_steps == None:
            n_steps = int(M * 252)
        print(n_steps)
        dt = M / n_steps
        shocks = np.random.standard_normal((n_steps, n_simuls))

        returns = (mu - 0.5 * sig ** 2) * dt + sig * shocks * np.sqrt(dt)
        # returns = (mu - 0.5 * sig ** 2) * dt + sig * shocks

        sum = np.cumsum(returns, axis = 0)

        paths = U * np.exp(sum)
        U_array = np.full(n_simuls, U)
        final = np.vstack([U_array, paths])

        return final
        
                

    def get_info(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        op_type = "Call" if self.call else "Put"
        print(f"""
        {self.name.center(56)}
        ={'=' * 56}
        | {'Metric':<25} | {'Value':>25} |
        {'-' * 57}
        | {'Price':<25} | {f"€{self.price():.2f}":>25} |
        | {'Strike':<25} | {f"€{self.strike:.2f}":>25} |
        | {'Time to maturity':<25} | {self.mat:>25.2f} |
        | {'Delta':<25} | {self.delta():>25.6f} |
        | {'Gamma':<25} | {self.gamma():>25.6f} |
        | {'Vega':<25} | {self.vega():>25.6f} |
        | {'Theta':<25} | {self.theta():>25.6f} |
        | {'Rho':<25} | {self.rho():>25.6f} |
        | {'Call or put':<25} | {op_type:>25} |
        ={'=' * 56}
        """)
        return None


if __name__ == "__main__":
    
    parameters = OptionParams(
        under = 200,
        strike = 190,
        divident = 0.0105,
        maturity = 1,
        rate  = 0.04,
        volatility = 0.2,
        call = True,
        name = "Opt_out"
    )
    option1 = Option(parameters)

    option1.get_info()
    paths = option1.brown_simul(drift=0)

    # import code; code.interact(local=locals())

    print(type(paths))
    print(paths.shape)

    import matplotlib.pyplot as plt

    maximum = max(paths[-1, :])
    for i in range(250):
        if paths[-1, i] == maximum:
            print(i)
            idx = i
    plt.figure(figsize=(10, 7))
    plt.subplot(2, 1, 1)
    plt.plot(paths, linewidth = 0.2, c = 'grey')
    plt.title("All simulations")
    plt.grid(alpha = 0.5)
    plt.subplot(2, 1, 2)
    plt.plot(paths[:, idx], c = 'grey')
    plt.title("Maximum at the end")
    plt.grid(alpha = 0.5)
    plt.tight_layout()
    # plt.show()
    plt.savefig("simul_test.pdf")
    print(norm.pdf(0))


