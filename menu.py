import os
import sys

from option import Option, OptionParams

os.system("./ASCII_animations/donut")

# ──────────────────────────────────────────────
#  Helpers
# ──────────────────────────────────────────────

with open('intro.txt', 'r') as f:
    main_header = f.read()

def clear():
    os.system("clear")


def pause():
    input("\n  Press Enter to return to the menu...")


def prompt_float(label: str, default: float = None) -> float:
    while True:
        hint = f" [{default}]" if default is not None else ""
        raw = input(f"  {label}{hint}: ").strip()
        if raw == "":
            return default
        try:
            return float(raw)
        except ValueError:
            print("  ✗  Please enter a valid number.")


def prompt_bool(label: str, default: bool = True) -> bool:
    hint = "Y/n" if default else "y/N"
    while True:
        raw = input(f"  {label} [{hint}]: ").strip().lower()
        if raw == "":
            return default
        if raw in ("y", "yes"):
            return True
        if raw in ("n", "no"):
            return False
        print("  ✗  Please enter y or n.")


def prompt_str(label: str, default: str = "") -> str:
    hint = f" [{default}]" if default else ""
    raw = input(f"  {label}{hint}: ").strip()
    return raw if raw else default


def header(title: str):
    print(main_header)
    width = 61
    print(f"\n  {'=' * width}")
    print(f"  {title.center(width)}")
    print(f"  {'=' * width}\n")


# ──────────────────────────────────────────────
#  Menu class
# ──────────────────────────────────────────────

class Menu:
    """Terminal-based interface for the Option / Black-Scholes toolkit."""

    def __init__(self):
        self.options: dict = {}
        self.option: Option = None

    # ── Option definition ──────────────────────

    def _select_option(self):
        clear()
        header("Option selector")
        name = prompt_str("Which option would you like to select?  ")
        try:
            self.option = self.options[name]
        except KeyError:
            print(f"\n  The name {name} is not recognized")
            pause()


    def _define_option(self) -> None:
        clear()
        header("Define Option Parameters")

        params = OptionParams(
            name       = prompt_str("Option name", "MyOption"),
            under      = prompt_float("Underlying price (S)"),
            strike     = prompt_float("Strike price (K)"),
            dividend   = prompt_float("Continuous dividend yield (q)", 0.0),
            maturity   = prompt_float("Time to maturity in years (T)"),
            rate       = prompt_float("Risk-free rate (r)"),
            volatility = prompt_float("Volatility (sigma)"),
            call       = prompt_bool("Is it a Call? (No = Put)")
        )
        self.options[params.name] = Option(params)
        # os.system("./ASCII_animations/success")
        print(f"\n  ✓  Option '{params.name}' created successfully.")
        pause()

    # ── Guard ──────────────────────────────────

    def _require_option(self) -> bool:
        if self.option == None:
            print("\n  ✗  No option selected yet. Please create/select one first.")
            pause()
            return False
        return True

    # ── Sub-menus / actions ────────────────────

    def _show_info(self) -> None:
        if not self._require_option():
            return
        self.option.get_info()
        pause()

    def _show_greeks(self) -> None:
        if not self._require_option():
            return
        clear()
        header(f"Greeks  —  {self.option.name}")
        print(f"  {'Delta':<20} {self.option.delta():>18.6f}")
        print(f"  {'Gamma':<20} {self.option.gamma():>18.6f}")
        print(f"  {'Vega':<20}  {self.option.vega():>18.6f}")
        print(f"  {'Theta':<20} {self.option.theta():>18.6f}")
        print(f"  {'Rho':<20}   {self.option.rho():>18.6f}")
        pause()

    def _implied_vol(self) -> None:
        if not self._require_option():
            return
        clear()
        header("Implied Volatility")
        mp = prompt_float("Observed market price")
        try:
            iv = self.option.implied_volatility(mp)
            print(f"\n  Implied volatility: {iv:.6f}  ({iv * 100:.4f} %)")
        except ValueError as e:
            print(f"\n  ✗  Could not find implied volatility")
        pause()

    def _simulation(self) -> None:
        if not self._require_option():
            return
        clear()
        header("Monte-Carlo Simulation")
        n_simuls = int(prompt_float("Number of simulations", 250))
        n_steps  = prompt_float("Number of time steps (Enter for auto)", None)
        n_steps  = int(n_steps) if n_steps is not None else None
        drift    = prompt_float("Custom drift (Enter to use r-q)", None)
        sigma    = prompt_float("Custom sigma (Enter to use model vol)", None)

        print("\n  Running simulation …")
        paths, prices = self.option.price_simul(
            n_simuls=n_simuls,
            n_steps=n_steps,
            drift=drift,
            sigma=sigma,
        )
        final_prices = prices[-1, :]
        print(f"\n  Simulated payoff statistics ({n_simuls} paths):")
        print(f"  {'Mean':<20} {final_prices.mean():>12.4f}")
        print(f"  {'Std dev':<20} {final_prices.std():>12.4f}")
        print(f"  {'Min':<20} {final_prices.min():>12.4f}")
        print(f"  {'Max':<20} {final_prices.max():>12.4f}")

        want_plot = prompt_bool("\n  Plot simulation paths?")
        if want_plot:
            self._plot_simulation_paths(under = paths, prices = prices)

        pause()

    def _plot_simulation_paths(self, under, prices) -> None:
        try:
            import matplotlib.pyplot as plt
            import numpy as np

            fig, axes = plt.subplots(1, 2, figsize=(13, 5))

            # Underlying paths
            ax1 = axes[0]
            ax1.plot(under, alpha=0.4, linewidth=0.5, c = 'grey')
            ax1.set_title("Simulated Underlying Paths")
            ax1.set_xlabel("Time step")
            ax1.set_ylabel("Price")

            # Option price paths
            ax2 = axes[1]
            ax2.plot(prices, alpha=0.4, linewidth=0.5, c = 'grey')
            ax2.set_title("Simulated Option Price Paths")
            ax2.set_xlabel("Time step")
            ax2.set_ylabel("Option Price")

            plt.suptitle(f"{self.option.name} — Monte-Carlo Simulation", fontsize=13)
            plt.tight_layout()
            plt.show()
        except ImportError:
            print("  ✗  matplotlib not available.")

    def _plot_3d(self) -> None:
        if not self._require_option():
            return
        clear()
        header("3-D Surface Plot")

        axes_info = {
            "M": "Maturity",
            "U": "Underlying price",
            "S": "Strike price",
            "V": "Volatility",
        }
        z_info = ["price", "delta", "gamma", "vega", "theta", "rho"]

        print("  Available axes:  M (Maturity)  |  U (Underlying)  |  S (Strike)  |  V (Volatility)")
        print("  Available z:     " + "  |  ".join(z_info))

        while True:
            xax = input("\n  X-axis [M/U/S/V]: ").strip().upper()
            if xax in axes_info:
                break
            print("  ✗  Must be one of M, U, S, V.")

        while True:
            yax = input("  Y-axis [M/U/S/V]: ").strip().upper()
            if yax in axes_info and yax != xax:
                break
            print(f"  ✗  Must be one of M, U, S, V and different from '{xax}'.")

        while True:
            zax = input(f"  Z-axis [{'/'.join(z_info)}]: ").strip().lower()
            if zax in z_info:
                break
            print("  ✗  Invalid choice.")

        print("\n  Generating plot …")
        try:
            import matplotlib.pyplot as plt

            data = self.option.plot_3d(xax=xax, yax=yax, zax=zax)
            X, Y, z = data

            fig = plt.figure(figsize=(11, 7))
            ax = fig.add_subplot(projection="3d")
            ax.view_init(elev=25)

            surf = ax.plot_surface(X, Y, z, cmap="plasma", antialiased=True)
            ax.plot_wireframe(X, Y, z, rstride=10, cstride=10, color="black", alpha=0.35)
            ax.set_box_aspect((2.5, 2.5, 1))

            ax.set_xlabel(axes_info[xax], labelpad=10)
            ax.set_ylabel(axes_info[yax], labelpad=10)
            ax.set_zlabel(zax.capitalize(), labelpad=10)
            plt.title(f"{zax.capitalize()} depending on {axes_info[xax]} and {axes_info[yax]}")
            fig.colorbar(surf, shrink=0.6, aspect=15, pad=0.12)
            plt.tight_layout()
            plt.show()
        except ImportError:
            print("  ✗  matplotlib not available.")

        pause()

    # ── Main menu loop ─────────────────────────

    def _print_main_menu(self) -> None:
        clear()
        header("Black-Scholes Option Toolkit")

        status = f"Active option: {self.option.name}" if self.option else "No option selected"
        print(f"  {status}\n")

        options = [
            ("1", "Define / change option"),
            ("2", "Show full option info & price"),
            ("3", "Show Greeks"),
            ("4", "Compute implied volatility"),
            ("5", "Run Monte-Carlo simulation"),
            ("6", "3-D surface plot"),
            ("7", "Select option by name"),
            ("0", "Exit"),
        ]
        for key, label in options:
            print(f"  [{key}]  {label}")
        print()

    def run(self) -> None:
        dispatch = {
            "1": self._define_option,
            "2": self._show_info,
            "3": self._show_greeks,
            "4": self._implied_vol,
            "5": self._simulation,
            "6": self._plot_3d,
            "7": self._select_option,
        }

        while True:
            self._print_main_menu()
            choice = input("  Your choice: ").strip()

            if choice == "0":
                clear()
                os.system("./ASCII_animations/fire")
                clear()
                print("\n  Goodbye!\n")
                break
            elif choice in dispatch:
                dispatch[choice]()
            else:
                print("  ✗  Invalid choice. Please try again.")
                pause()


# ──────────────────────────────────────────────
#  Entry point
# ──────────────────────────────────────────────

if __name__ == "__main__":
    Menu().run()
