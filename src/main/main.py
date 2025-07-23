########## IMPORTS ##########
from tkinter import Tk
from minesweeper import Minesweeper
########## MAIN FUNCTION ##########
def main() :
    # create window
    root = Tk()
    # create game instance
    game = Minesweeper(root)
    # make window non-resizeable
    root.resizable(False, False)
    # run game
    root.mainloop()

if __name__ == "__main__" :
    main()
