from option import Option, OptionParams
import time


parameters = OptionParams(
    under = 690.62,
    strike = 691,
    dividend = 0.0105,
    maturity = 1,
    rate  = 0.0345,
    volatility = 0.1462,
    call = True,
    name = "SP500"
)

option1 = Option(parameters)

simuls = 1000000

start = time.time()

paths = option1.brown_simul(n_simuls=simuls)

end = time.time()

print(f"\n\nIt took {end - start:.4f} seconds to run {simuls} simulations.\nThe numpy array is {paths.nbytes / 1024**2:.4f} MB in size.")


# It took 0.0031 seconds to run 250 simulations.
# The numpy array is 0.4807 MB in size.


# It took 0.0119 seconds to run 1000 simulations.
# The numpy array is 1.9226 MB in size.


# It took 0.0892 seconds to run 10000 simulations.
# The numpy array is 19.2261 MB in size.


# It took 0.8582 seconds to run 100000 simulations.
# The numpy array is 192.2607 MB in size.


# It took 4.3058 seconds to run 500000 simulations.
# The numpy array is 961.3037 MB in size.


# It took 7.6498 seconds to run 750000 simulations.
# The numpy array is 1441.9556 MB in size.


# --maximum memory would allow--


# It took 7.0979 seconds to run 1000000 simulations.
# The numpy array is 961.3037 MB in size using float32.


# It took 9.0580 seconds to run 1200000 simulations.
# The numpy array is 1153.5645 MB in size using float32.


