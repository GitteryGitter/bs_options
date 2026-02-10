from dataclasses import dataclass
import math
from scipy.stats import norm
import numpy as np
import os

@dataclass
class OptionParams:
    under: float # Current price of the underlying (S)
    strike: float # Strike price (K)
    dividend: float # Dividend payed out by the underlying asset
    maturity: float # Time to maturity in years (T)
    rate: float # Risk-free interest rate (r)
    volatility: float # Volatility (sigma)
    call: bool # Is it a call?
    name: str # name of the option


class Option:
    def __init__(self, params: OptionParams):
        self.under = params.under
        self.strike = params.strike
        self.dividend = params.dividend
        self.mat = params.maturity
        self.r = params.rate
        self.vol = params.volatility
        self.call = params.call
        self.name = params.name

    def get_params(self) -> tuple:
        return self.under, self.strike, self.mat, self.r, self.vol, self.dividend


    def d1(self) -> float:
        U, S, M, R, V, q = self.get_params()

        return (math.log( U / S ) + ( R - q + 0.5 * V ** 2 ) * M ) / ( V * math.sqrt(M))


    def delta(self) -> float:
        """
        Computes the change of the option in respondse to the change of the underlying asset.
        """
        _, _, M, _, _, q = self.get_params()
        d1 = self.d1()

        if self.call == True:
            return math.exp(-q * M) * norm.cdf(d1)      
        else:
            return math.exp(-q * M) * ( norm.cdf(d1) - 1 )


    def gamma(self) -> float:
        """"
        Computes the sensitivity of delta with respect to the price of the underlying asset.
        """
        U, _, M, _, V, q = self.get_params()  
        d1 = self.d1()

        return math.exp(-q * M) * norm.pdf(d1) / ( U * V * math.sqrt(M) )


    def vega(self) -> float:
        U, _, M, _, _, q = self.get_params()
        d1 = self.d1()
        
        return U * math.exp(-q * M) * math.sqrt(M) * norm.pdf(d1)


    def theta(self) -> float:
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


    def rho(self) -> float:
        _, S, M, R, V, _ = self.get_params()
        d1 = self.d1()
        d2 = d1 - V * math.sqrt(M)

        if self.call == True:
            return S * M * math.exp(- R * M) * norm.cdf(d2)    
        else:
            return - S * M * math.exp(- R * M) * norm.cdf(-d2)
            
        
    def price(self) -> float:
        """Computes the Black-Scholes option price"""
        U, S, M, R, V, q = self.get_params()
        d1 = self.d1()
        d2 = d1 - V * math.sqrt(M)
        
        if self.call:
            return U * math.exp(-q * M) * norm.cdf(d1) - S * math.exp(-R * M) * norm.cdf(d2)
        else:
            return S * math.exp(-R * M) * norm.cdf(-d2) - U * math.exp(-q * M) * norm.cdf(-d1)
    

    def brown_simul(self, n_simuls: int =250, n_steps: int = None, drift: float = None, sigma: float = None) -> np.ndarray:
        """Geometric Brownian Motion simulation engine"""
        U, _, M, R, V, q = self.get_params()
        
        mu = drift if drift is not None else (R - q)
        sig = sigma if sigma is not None else V

        if n_steps == None:
            n_steps = int(M * 252)

        n_steps -= 1

        dt = M / n_steps
        shocks = np.random.standard_normal((n_steps, n_simuls))

        returns = (mu - 0.5 * sig ** 2) * dt + sig * shocks * np.sqrt(dt)

        sum = np.cumsum(returns, axis = 0)

        paths = U * np.exp(sum)
        U_array = np.full(n_simuls, U)
        final = np.vstack([U_array, paths])

        return final
        
                
    def price_simul(self, n_simuls: int = 250, n_steps: int = None, drift: float = None, sigma: float = None) -> np.ndarray:
        """
        COmputes the prices of the option based on the brownian motion simulation.
        """
        _, S, M, R, V, q = self.get_params()

        paths = self.brown_simul(n_simuls=n_simuls, n_steps = n_steps, drift = drift, sigma = sigma)

        n_steps = paths.shape[0]
        rem = np.linspace(M, 1e-10, n_steps)
        rem = np.reshape(rem, (n_steps, 1))
 

        d1 = (np.log( paths / S ) + ( R - q + 0.5 * V ** 2 ) * rem ) / ( V * np.sqrt(rem))
        d2 = d1 - V * np.sqrt(rem)

        if self.call:
            prices = paths * np.exp(-q * rem) * norm.cdf(d1) - S * np.exp(-R * rem) * norm.cdf(d2)
            prices[-1, :] = np.maximum(paths[-1, :] - S, 0)
        else:
            prices = S * np.exp(-R * rem) * norm.cdf(-d2) - paths * np.exp(-q * rem) * norm.cdf(-d1)
            prices[-1, :] = np.maximum(S - paths[-1, :], 0)

        return prices
    

    def plot_3d(self, xax: str = "M", yax: str = "U") -> np.ndarray:
        """
        Returns an array for a 3-dimensional plot of the option price.
        Usage: specify x and y by passing a single char string.
        Available choices: maturity (M), underlying price (U), strike price (S), volatility (V).
        """
        assert xax != yax
        assert xax in ["M", "U", "S", "V"]
        assert yax in ["M", "U", "S", "V"]
        
        U, S, M, R, V, q = self.get_params()

        if xax == "M":
            x = np.linspace(M, 1e-10, 100)
        elif xax == "U":
            x = np.linspace(U * 0.85, U * 1.15, 100)
        elif xax == "S":
            x = np.linspace(S * 0.85, S * 1.15, 100)
        else:
            x = np.linspace(V * 0.85, V * 1.15, 100)
        
        if yax == "M":
            y = np.linspace(M, 1e-10, 100)
        elif yax == "U":
            y = np.linspace(U * 0.85, U * 1.15, 100)
        elif yax == "S":
            y = np.linspace(S * 0.85, S * 1.15, 100)
        else:
            y = np.linspace(V * 0.85, V * 1.15, 100)

        X, Y = np.meshgrid(x, y)

        if xax == "M":
            M = X
        elif xax == "U":
            U = X
        elif xax == "S":
            S = X
        else:
            V = X
        
        if yax == "M":
            M = Y
        elif yax == "U":
            U = Y
        elif yax == "S":
            S = Y
        else:
            V = Y

        d1 = (np.log( U / S ) + ( R - q + 0.5 * V ** 2 ) * M ) / ( V * np.sqrt(M))
        d2 = d1 - V * np.sqrt(M)

        if self.call:
            z =  U * np.exp(-q * M) * norm.cdf(d1) - S * np.exp(-R * M) * norm.cdf(d2)
        else:
            z =  S * np.exp(-R * M) * norm.cdf(-d2) - U * np.exp(-q * M) * norm.cdf(-d1)
        
        return (X, Y, z)


    def implied_volatility(self) -> float:
        """
        Computes the implied volatility
        """
        pass

    
    def get_info(self) -> None:
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
        under = 278.12,
        strike = 277.50,
        dividend = 0.0037,
        maturity = 3,
        rate  = 0.0345,
        volatility = 0.2434,
        call = True,
        name = "Apple"
    )

    option1 = Option(parameters)

    option1.get_info()

    X, Y, z = option1.plot_3d(xax = "M", yax = "V")

    import matplotlib.pyplot as plt
    def make_plot(data, xlab = '', ylab = ''):
        
        X, Y, z = data
        fig = plt.figure(figsize=(11, 7))
        ax = fig.add_subplot(projection="3d")
        ax.view_init(elev=25)


        surf = ax.plot_surface(
            X, Y, z,
            cmap="plasma",
            antialiased=True
        )
        ax.plot_wireframe(
            X, Y, z,
            rstride=10,
            cstride=10,
            color="black",
            alpha=0.35
        )
        ax.set_box_aspect((2.5, 2.5, 1))
        
        ax.set_xlabel(xlab, labelpad=10)
        ax.set_ylabel(ylab, labelpad=10)
        ax.set_zlabel("Price of the option", labelpad=10)
        plt.title('Price of the option depending on ' + xlab + ' and ' + ylab)

        fig.colorbar(surf, shrink=0.6, aspect=15, pad = 0.12)
        plt.tight_layout()

        plt.show()

    plot_data = option1.plot_3d(xax = "M", yax = "V")

    make_plot(data = plot_data, xlab = "Time to maturity", ylab = "Volatility")


