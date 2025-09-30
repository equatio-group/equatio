# equatio
Struggling to remember all the different terms for physical equations? Our game, [equatio](https://github.com/equatio-group/equatio) is here to help! Inspired by the NYT game [Connections](https://www.nytimes.com/games/connections), it is programmed in [Python](https://www.python.org/), using [pygame](https://www.pygame.org/docs/).

## How to run
1. Install [Python](https://www.python.org/downloads/) 3.9+ (if not already satisfied)
2. Clone the repository: `git clone https://github.com/equatio-group/equatio.git`
3. Create a virtual environment: `python -m  venv .venv`
4. Activate the virtual environment:
    - on Linux/ macOS: `source .venv/bn/activate`
    - on Windows(CMD): `.venv\Scripts\activate`
    - on Windows (PowerShell): `.venv\Scripts\Activate.ps1`
4. Install dependencies: `pip install -r requirements.txt`
5. Start the game: `python -m src/equatio/main.py`

## How to play
By default, you can play the game with a set of 16 terms from the following equations:

- Ideal gas law,
- Bernoulli equation,
- Gibbs energy for homogenic nucleation,
- Adiabatic temperature gradient, and
- Kinetic energy equation of the mean flow in turbulent systems.

The aim is to find groups of terms that belong to the same physical equation.
1. When the game starts, you will see a board with sixteen cards, each showing one of the terms. At the bottom there will be an empty equation with placeholders for up to four terms on either side of the equal sign.
2. You can now drag and drop the terms from the board to the equation bar. Note that the order of the terms on one side of the equation does not matter. It also does not matter if the original left-side terms end up on the right and vice versa, as long as the terms do not get mixed up between the sides.
3. If you think you have combined the right terms for one of the equations, you can click on the check button.
4. If you are correct, the equation bar will empty, and you can move on to the next equation. Otherwise, the terms will be returned to the board.
5. The game ends when you have found all five equations correctly.

You can quit the game at any time by clicking on the Quit button.

Have fun playing!

## Project status
This version can be played using a standard set of sixteen terms and five equations (see [above](#how-to-play)). You can change the set of equations and terms by editing the `standard_set.json` file in the `data/` folder. However, the game currently does not work properly with more than 16 terms in the set and more than four terms per equation side. You also need to follow the given `JSON` structure and use the correct $\LaTeX$ code (with double backslashes instead of single backslashes) for [Matplotlib](https://matplotlib.org/) to display the terms correctly.

Support for a variable set sizes and a more user-friendly way to create, save, load, and modify custom equation sets is planned for future versions. Also, the implementation of checks in main.py will be simplified by using already implemented class methods from EquationSet, Equation, and Term. Furthermore, the scaling of sprites will be improved to work flexibly with different sizes of $\LaTeX$ term representations.