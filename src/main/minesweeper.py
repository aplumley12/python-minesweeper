import tkinter as tk
from tkinter.font import Font
from tkinter import simpledialog
from tkinter import messagebox
from PIL import Image
from PIL import ImageTk
import json
import os
import sys
import numpy as np
from datetime import datetime

class Minesweeper :
    def __init__(self, master=None) :
        '''
        Main method. Initializes the game with the default settings.
        '''
        # SET DEFAULT ATTRIBUTE SETTINGS #
        # gui root
        self.master = master
        # game status (default -> False)
        self.won = False
        # game difficulty (default -> beginner)
        self.difficulty = "easy"
        # grid dimensions (default -> 9x9)
        self.grid_rows = 9
        self.grid_cols = 9
        # number of bombs on the grid (default -> 10)
        self.bomb_count = 10
        # root geometry (default -> 330x405)
        self.gmtry = "330x405"
        # dark mode setting (default -> False)
        self.dark_mode = False

        # TRACK GAME PROGRESS #
        # array of uncovered grid cells
        self.uncovered = []
        # array of placed bomb coordinates
        self.bomb_locations = []
        # number of placed flags
        self.flag_placements = 0
        # initialize counter (without starting it)
        self.counter = None

        # HANDLE HIGH SCORES #
        self.high_scores_file = os.path.join(os.path.dirname(__file__), '..', 'resources', 'highscores.json')
        self.high_scores = self.getHighScores()

        # HASHMAPS #
        # Add dark mode color schemes
        self.light_theme = {
                        "bg_main" : "gray",
                       "bg_frame" : "gray", 
                        "bg_cell" : "darkgray",
              "bg_cell_uncovered" : "gray",
         "bg_bomb_cell_uncovered" : "red",
                    "bg_bomb_win" : "green",
                     "bg_counter" : "black",
                     "fg_counter" : "red",
                      "bg_button" : "darkgray",
                        "bg_help" : "darkgray",
                   "fg_help_text" : "black",
                      "bg_scores" : "darkgray",
                 "fg_scores_text" : "black",
                    u"\U0001F4A3" : "black",
                              "0" : "gray",
                              "1" : "blue",
                              "2" : "green",
                              "3" : "red",
                              "4" : "darkblue",
                              "5" : "maroon",
                              "6" : "gold",
                              "7" : "darkviolet",
                              "8" : "black"

        }
        
        self.dark_theme = {
                        "bg_main" : "#2b2b2b",
                       "bg_frame" : "#2b2b2b",
                        "bg_cell" : "#404040", 
              "bg_cell_uncovered" : "#505050",
         "bg_bomb_cell_uncovered" : "tomato",
                    "bg_bomb_win" : "limegreen",
                     "bg_counter" : "#1a1a1a",
                     "fg_counter" : "#00ff00",
                      "bg_button" : "#404040",
                        "bg_help" : "#404040",
                   "fg_help_text" : "whitesmoke",
                      "bg_scores" : "#404040",
                 "fg_scores_text" : "whitesmoke",
                    u"\U0001F4A3" : "black",
                              "0" : "#505050",
                              "1" : "lightskyblue",
                              "2" : "limegreen",
                              "3" : "tomato",
                              "4" : "deepskyblue",
                              "5" : "indianred",
                              "6" : "yellow",
                              "7" : "pink",
                              "8" : "whitesmoke"
        }

        self.font_dict = {
            "counter" : Font(self.master, family='OCR A Extended', name='OCR A Extended', size=17, weight='bold'),
               "cell" : Font(self.master, size=15),
               "bomb" : Font(self.master, size=13),
             "scores" : Font(self.master, size=10)
        }

        self.img_dict = {
            "default" : "smile.png",
               "lose" : "lose.png"
        }

        # BUILD GAME #
        # create grid of integers
        self.grid = self.buildGrid()

        # build window
        self.buildWindow()
        self.buildCovers()

    ########## BASIC WINDOW SETUP ##########
    def buildWindow(self) :
        '''
        Creates the main game window.
        '''
        # window title
        self.master.title("Minesweeper")
        # window dimensions
        self.master.geometry(self.gmtry)

        # add main frame
        self.main_frame = tk.Frame(master=self.master)
        self.main_frame.pack(fill='both', expand=True)

        # create and add info frame
        self.buildInfoFrame()
        # create and add grid frame
        self.buildGridFrame()
        # create and add menu
        self.buildMenu()

    def buildInfoFrame(self) :
        '''
        Creates the frame for the reset button, timer, and flag counter.
        '''
        theme = self.dark_theme if self.dark_mode else self.light_theme
        
        # add info frame to main frame
        self.info_frame = tk.Frame(master=self.main_frame, relief="ridge", borderwidth=7, pady=5, bg=theme["bg_frame"])
        self.info_frame.pack(fill='x', anchor='n', expand=True)

        # add bomb counter to info frame
        self.flag_frame = tk.Frame(master=self.info_frame, relief="sunken", borderwidth=5, height=40, width=80, padx=1, pady=1, bg=theme["bg_counter"])
        self.flag_frame.pack(side='left', padx=10)
        self.flag_count = tk.Label(master=self.flag_frame, text=f"{(self.bomb_count % 1000) // 100}{(self.bomb_count % 100) // 10}{self.bomb_count % 10}", font=self.font_dict["counter"], fg=theme["fg_counter"], bg=theme["bg_counter"])
        self.flag_count.pack_propagate(False) # non-resizeable
        self.flag_count.pack()

        # add timer to info frame
        self.timer_frame = tk.Frame(master=self.info_frame, relief="sunken", borderwidth=5, height=40, width=80, padx=1, pady=1, bg=theme["bg_counter"])
        self.timer_frame.pack(side='right', padx=10)
        self.timer = tk.Label(master=self.timer_frame, text="000", font=self.font_dict["counter"], fg=theme["fg_counter"], bg=theme["bg_counter"])
        self.timer.pack_propagate(False) # non-resizeable
        self.timer.pack()

        # add reset button to info frame
        img = self.getButtonImage()
        self.reset_button = tk.Button(master=self.info_frame, image=img, bd=1, bg=theme["bg_button"], command=self.gameReset)
        self.reset_button.image = img # prevent garbage collection of image
        self.reset_button.pack()

    def buildGridFrame(self) :
        '''
        Creates the frame for the mine field.
        '''
        theme = self.dark_theme if self.dark_mode else self.light_theme
        
        # add grid frame to main frame
        frame_height = abs(self.main_frame.winfo_screenmmheight() - self.info_frame.winfo_screenheight()) # fill space not occupied by button_frame
        self.grid_frame = tk.Frame(master=self.main_frame, relief="ridge", borderwidth=7, height=frame_height, padx=5, pady=5, bg=theme["bg_frame"])
        self.grid_frame.pack(fill='both', anchor='s', expand=True)

        # add grid covers to grid frame
        self.buildCovers()
    
    ########## MINEFIELD SETUP AND BINDINGS ##########
    def buildCovers(self) :
        '''
        Creates the cell covers for the mine field.
        '''
        theme = self.dark_theme if self.dark_mode else self.light_theme
        
        for r in range(self.grid_rows) :
            for c in range(self.grid_cols) :
                # retrieve contents from integer grid
                content = self.grid[r][c]
                # use label for proper left- and right-click bindings
                cell = tk.Label(master=self.grid_frame, name=f"[{r},{c}]", width=2, height=1, 
                             relief="raised", borderwidth=4, highlightbackground="dimgray", 
                             highlightthickness=1, bg=theme["bg_cell"])
                if content == 0 :
                    cell.config(text=content, font=self.font_dict["cell"], fg=theme["bg_cell"])
                # configure text based on content (color blends with background until left-clicked)
                elif content > 0 :
                    cell.config(text=content, font=self.font_dict["cell"], fg=theme["bg_cell"])
                # set bomb unicode character
                else :
                    cell.config(text=u"\U0001F4A3", font=self.font_dict["cell"], fg=theme["bg_cell"])

                # make cell non-resizeable
                cell.grid_propagate(False)
                # place cell in grid (no padding between cells)
                cell.grid(row=r, column=c)

                # bind left-click
                cell.bind(sequence="<Button-1>", func=self.uncoverCell)
                # bind right-click
                cell.bind(sequence="<Button-3>", func=self.addFlag)

                # add flag container as a child widget
                self.buildFlag(r, c)

    def buildFlag(self, row, col) :
        '''
        Creates the flag labels.
        '''
        theme = self.dark_theme if self.dark_mode else self.light_theme
        
        # create flag label with flag unicode character
        flag = tk.Label(master=self.grid_frame, text=u"\U0001F3F2", font=self.font_dict["bomb"], 
                    fg="crimson", width=2, height=1, padx=0, pady=0, relief="flat", bg=theme["bg_cell"])
        
        # make label non-resizeable
        flag.grid_propagate(False)
        # place flag label in grid below cell
        flag.grid(row=row, column=col)
        flag.lower()

        # bind right-click
        flag.bind(sequence="<Button-3>", func=self.removeFlag)

    def buildGrid(self) :
        '''
        Randomly places hidden bombs in the mine field.
        '''
        # initialize grid of zeros
        grid = np.zeros(shape=(self.grid_rows, self.grid_cols), dtype=int)

        # randomly place bombs
        for bomb in range(self.bomb_count) :
            while(True) :
                row = np.random.randint(self.grid_rows)
                col = np.random.randint(self.grid_cols)
                # place the bomb if the cell is empty
                if(grid[row][col] == 0) :
                    grid[row][col] = -1 # signifies a bomb
                    # append coordinates to bomb locations
                    self.bomb_locations.append((row, col))
                    break

        # calculate number of adjacent bombs for each cell
        for row in range(self.grid_rows) :
            for col in range(self.grid_cols) :
                if(grid[row][col] < 0) :
                    grid = self.updateCounts(grid, row, col)

        return grid
    
    def updateCounts(self, grid, row, col) :
        '''
        Calculates the number of neighboring cells that contain bombs.
        '''
        # northern cells
        if row - 1 >= 0 :
            # north cell
            if grid[row - 1][col] >= 0 :
                grid[row - 1][col] += 1
            # north east cell
            if (col + 1 < len(grid[0])) and grid[row - 1][col + 1] >= 0 :
                grid[row - 1][col + 1] += 1
            # north west cell
            if (col - 1 >= 0) and grid[row - 1][col - 1] >= 0 :
                grid[row - 1][col - 1] += 1

        # southern cells
        if row + 1 < len(grid) :
            # south cell
            if grid[row + 1][col] >= 0 :
                grid[row + 1][col] += 1
            # south east cell
            if (col + 1 < len(grid[0])) and grid[row + 1][col + 1] >= 0 :
                grid[row + 1][col + 1] += 1
            # south west cell
            if (col - 1 >= 0) and (grid[row + 1][col - 1] >= 0) :
                grid[row + 1][col - 1] += 1
    
        # east cell
        if (col + 1 < len(grid[0])) and (grid[row][col + 1] >= 0) :
            grid[row][col + 1] += 1

        # west cell 
        if (col - 1 >= 0) and (grid[row][col - 1] >= 0) :
            grid[row][col - 1] += 1
        
        # return the updated grid
        return grid
    
    def uncoverCell(self, event=None, row=-1, col=-1) :
        '''
        Left-click binding for grid cells. Displays the contents (e.g., bomb, clue, nothing)
        '''
        theme = self.dark_theme if self.dark_mode else self.light_theme
        
        # start timer on first click
        if self.counter == None :
            self.counter = 0 # init counter to 0
            self.updateTimer()

        # check if cell contains a bomb
        if(event.widget.cget("text") == u"\U0001F4A3") :
            # remove current coordinates from bomb locations array
            self.bomb_locations.remove((event.widget.grid_info()['row'], event.widget.grid_info()['column']))
            # update cell appearance
            event.widget.configure(relief="flat", fg="black", highlightbackground="dimgray", highlightthickness=1, bg=theme["bg_bomb_cell_uncovered"])
            # end the game
            self.gameOver(win=False)

        # cell does not contain a bomb
        else :
            # add current coordinates to uncovered cells array
            self.uncovered.append((row, col))
            # update text color
            color = theme[event.widget.cget("text")]
            event.widget.configure(relief="flat", fg=color, highlightbackground="dimgray", highlightthickness=1, bg=theme["bg_cell_uncovered"])
            # disable function bindings
            event.widget.unbind(sequence="<Button 1>")
            event.widget.unbind(sequence="<Button 3>")

            # if cell contains a 0, uncover surrounding 0s
            if event.widget.cget("text") == "0" :
                # retrieve row and column of clicked cell
                row = event.widget.grid_info()['row']
                col = event.widget.grid_info()['column']
                for r in range(max(0, row - 1), min(len(self.grid) - 1, row + 1) + 1) :
                    for c in range(max(0, col - 1), min(len(self.grid) - 1, col + 1) + 1) :
                        # do not uncover a cell that is already uncovered
                        if (r, c) in self.uncovered :
                            continue
                        # simulate left-click to uncover cell
                        self.grid_frame.nametowidget(f"[{r},{c}]").event_generate("<Button-1>")

            # end game if all non-bomb cells are uncovered
            if ((len(self.uncovered) >= (self.grid_rows * self.grid_cols) - self.bomb_count)) :
                self.gameOver(win=True)

    def addFlag(self, event) :
        '''
        Right-click binding for grid cells. Plants a flag over a suspected bomb.
        '''
        # start timer on first click
        if self.counter == None :
            self.counter = 0 # init counter to 0
            self.updateTimer()

        # push cell to the back (reveals flag label)
        event.widget.lower()
        # disable cell bindings
        event.widget.unbind(sequence="<Button-1>")
        event.widget.unbind(sequence="<Button-3>")

        # increment flag count by 1
        self.flag_placements += 1
        # update the flag count label text of there are not more flags than bombs
        if (self.bomb_count >= self.flag_placements) :
            self.setFlagCount()
    
    def removeFlag(self, event) :
        '''
        Right-click binding for flag labels. Removes a flag from a grid cell.
        '''
        # push flag label under cell
        event.widget.lower()
        # get grid coordinates
        flag_row = event.widget.grid_info()['row']
        flag_col = event.widget.grid_info()['column']
        # renable bindings
        self.grid_frame.nametowidget(f"[{flag_row},{flag_col}]").bind(sequence="<Button-1>", func=self.uncoverCell)
        self.grid_frame.nametowidget(f"[{flag_row},{flag_col}]").bind(sequence="<Button-3>", func=self.addFlag)
        
        # decrement flag count
        self.flag_placements -= 1
        # update flag count label text if there are not more flags than bombs
        if (self.bomb_count >= self.flag_placements) :
            self.setFlagCount()

    def gameReset(self) :
        '''
        Left-click binding for the reset button. Reloads the game with the chosen difficulty setting.
        '''
        # change resest button image back to default
        img = self.getButtonImage()
        self.reset_button.configure(image=img)
        self.reset_button.image = img # prevent garbage collection of image

        # remove all cells
        for cell in self.grid_frame.winfo_children() :
            cell.destroy()
        
        # reset attributes
        self.uncovered.clear()
        self.bomb_locations.clear()
        self.flag_placements = 0
        self.counter = None

        # reset info labels
        self.timer.configure(text="000")
        self.flag_count.configure(text=f"{(self.bomb_count % 1000) // 100}{(self.bomb_count % 100) // 10}{self.bomb_count % 10}")

        # create new grid and cell covers
        self.grid = self.buildGrid()
        self.buildCovers()

    ########## MENU BAR SETUP AND BINDINGS ##########
    def buildMenu(self) :
        '''
        Creates the menu bar.
        '''
        # add main menu bar
        menu_bar = tk.Menu(master=self.master)

        # add game tab to menu bar
        menu_game = tk.Menu(master=menu_bar, tearoff=False)
        menu_bar.add_cascade(menu=menu_game, label='Game')

        # add high scores pop-up to game tab
        menu_game.add_command(label='High Scores', command=self.showHighScores)
        # add directions pop-up to game tab
        menu_game.add_command(label='Help', command=self.showDirections)

        # add options tab to menu bar
        menu_options = tk.Menu(master=menu_bar, tearoff=False)
        menu_bar.add_cascade(menu=menu_options, label='Options')

        # add difficulty menu to options tab
        menu_difficulty = tk.Menu(master=menu_options, tearoff=False)
        menu_options.add_cascade(menu=menu_difficulty, label='Difficulty', command=None)

        # add difficulty settings to difficulty submenu
        menu_difficulty.add_radiobutton(label='Easy', command=lambda:self.setDifficulty("easy"))
        menu_difficulty.add_radiobutton(label='Hard', command=lambda:self.setDifficulty("hard"))

        # add dark mode toggle to options tab
        menu_options.add_checkbutton(label='Dark Mode', command=self.toggleDarkMode)

        # display menu
        self.master.configure(menu=menu_bar)

    ########## HANDLE GAME LOGIC ##########
    def gameOver(self, win) :
        '''
        Handles game completion for player wins and losses.
        '''
        theme = self.dark_theme if self.dark_mode else self.light_theme
        
        # stop timer
        player_time = self.counter
        self.counter = None
        # unbind all cells
        for cell in self.grid_frame.winfo_children() :
            try :
                cell.unbind("<Button-1>")
                cell.unbind("<Button-3>")
            except tk.TclError:
                pass
        
        # player won
        if win :
            for coord in self.bomb_locations :
                self.grid_frame.nametowidget(f"[{coord[0]},{coord[1]}]").configure(relief="flat", fg="black", highlightbackground="dimgray", highlightthickness=1, bg=theme["bg_bomb_win"])
                self.grid_frame.nametowidget(f"[{coord[0]},{coord[1]}]").tkraise()
            
            # Check for high score
            if player_time is not None:
                self.checkHighScore(player_time)

        # player lost
        if not win :
            # change reset button image
            img = self.getButtonImage("lose")
            self.reset_button.configure(image=img)
            self.reset_button.image = img # prevent garbage collection of image
            # display all bomb locations
            for bomb in self.bomb_locations :
                self.grid_frame.nametowidget(f"[{bomb[0]},{bomb[1]}]").configure(relief="flat", fg="black", highlightbackground="dimgray", highlightthickness=1, bg=theme["bg_cell_uncovered"])
                self.grid_frame.nametowidget(f"[{bomb[0]},{bomb[1]}]").tkraise()

    ########## SET METHODS ##########
    def updateTimer(self) :
        '''
        Increments the timer label text once every second.
        '''
        # check if timer should be initiated
        if self.counter != None :
            # iterate second counter 
            self.counter += 1
            # configure display
            self.timer.configure(text=f"{(self.counter % 1000) // 100}{(self.counter % 100) // 10}{self.counter % 10}")
            # update every second
            self.master.after(1000, self.updateTimer)

    def setFlagCount(self) :
        '''
        Decrements the number of remaining bombs based on the number of flag placements.
        '''
        updated_text = self.bomb_count - self.flag_placements
        self.flag_count.configure(text=f"{(updated_text % 1000) // 100}{(updated_text % 100) // 10}{updated_text % 10}")

    def setDifficulty(self, selected) :
        '''
        Resets the game with a chosen difficulty setting.
        '''
        # easy mode settings
        if(selected == "easy") :
            self.difficulty = "easy"
            self.grid_rows = 9
            self.grid_cols = 9
            self.bomb_count = 10
            self.master.geometry("330x405")
        # hard mode settings
        else :
            self.difficulty = "hard"
            self.grid_rows = 16
            self.grid_cols = 16
            self.bomb_count = 40
            self.master.geometry("568x650")     

        # reset the game with the new difficulty setting
        self.gameReset()

    def toggleDarkMode(self):
        '''
        Toggles dark mode on and off and refreshes the UI.
        '''
        self.dark_mode = not self.dark_mode
        self.refreshUI()
    
    def refreshUI(self):
        '''
        Refreshes the entire UI to apply the current theme.
        '''
        theme = self.dark_theme if self.dark_mode else self.light_theme
        
        # Update main window background
        self.master.configure(bg=theme["bg_main"])
        
        # Update main frame
        self.main_frame.configure(bg=theme["bg_main"])
        
        # Update info frame and its components
        self.info_frame.configure(bg=theme["bg_frame"])
        self.flag_frame.configure(bg=theme["bg_counter"])
        self.flag_count.configure(fg=theme["fg_counter"], bg=theme["bg_counter"])
        self.timer_frame.configure(bg=theme["bg_counter"])
        self.timer.configure(fg=theme["fg_counter"], bg=theme["bg_counter"])
        self.reset_button.configure(bg=theme["bg_button"])
        
        # Update grid frame
        self.grid_frame.configure(bg=theme["bg_frame"])
        
        # Update all cells and flags
        for child in self.grid_frame.winfo_children():
            if child.winfo_class() == 'Label':
                # Check if it's a cell or flag by examining its text
                text = child.cget("text")
                if text == u"\U0001F3F2":  # Flag
                    child.configure(bg=theme["bg_cell"])
                else:  # Cell
                    # Check if cell is uncovered (has flat relief)
                    if child.cget("relief") == "flat":
                        child.configure(bg=theme["bg_cell_uncovered"], fg=theme[child.cget("text")])
                    else:
                        child.configure(bg=theme["bg_cell"])
                        # Update hidden text color to match background
                        if text in ["0"] or text.isdigit():
                            child.configure(fg=theme["bg_cell"])
                        elif text == u"\U0001F4A3":
                            child.configure(fg=theme["bg_cell"])

    ########## GET METHODS ##########
    def showDirections(self) :
        '''
        Left-click binding for the 'Help' command under the 'Game' tab.
        Displays the game rules in a child window.
        '''
        theme = self.dark_theme if self.dark_mode else self.light_theme
        
        # create toplevel window
        self.help_window = tk.Toplevel()
        self.help_window.title("Help")
        self.help_window.grab_set() # prevent interaction with main window when open
        # set dimensions
        self.help_window.geometry("300x350")
        self.help_window.resizable(False, False)
        # set background color
        self.help_window.configure(bg=theme["bg_frame"])

        # create title frame
        title_frame = tk.Frame(master=self.help_window, bg=theme["bg_frame"], padx=5, pady=5,
                               relief="ridge", borderwidth=7)
        title_frame.pack(fill="both")

        # create directions frame
        directions_frame = tk.Frame(master=self.help_window, bg=theme["bg_frame"], padx=5, pady=5,
                                relief="ridge", borderwidth=7)
        directions_frame.pack(fill="both")
        # create title label
        title_label = tk.Label(master=title_frame, text="HOW TO PLAY", font=self.font_dict["counter"],
                                   fg=theme["fg_counter"], bg=theme["bg_counter"], padx=3, pady=3, relief="sunken", borderwidth=5)
        
        # create text field for displaying game directions
        directions_text = tk.Text(master=directions_frame, wrap="word", bg=theme["bg_help"], pady=5, padx=5, 
                                  relief="raised", borderwidth=4)
        
        title_label.pack(fill="x")
        directions_text.pack(fill="both")

        # customize directions text
        summary_heading = "WHAT IS MINESWEEPER?\n"
        summary = "Minesweeper is a logic puzzle game featuring a grid that contains some number of hidden mines." \
                  " Uncovering a cell that does not contain a bomb reveals a clue about how many neighboring cells contain bombs." \
                  " The goal of this game is to uncover every cell without detonating any mines."
        controls_heading = "\n\nCONTROLS\n"
        controls = u"\U0001F4A3" + "  LEFT-CLICK on a cell to uncover it\n" \
                   u"\U0001F4A3" + "  RIGHT-CLICK on a cell suspected to contain a\n      bomb to place or remove a flag\n" \
                   u"\U0001F4A3" + "  LEFT-CLICK the button between the counter and\n      timer to reset the game"
        
        # insert headings and text blocks
        directions_text.insert("end", summary_heading, "heading_1")
        directions_text.insert("end", summary, "text_1")
        directions_text.insert("end", controls_heading, "heading_2")
        directions_text.insert("end", controls, "text_2")

        # add tags
        directions_text.tag_config(tagName="heading_1", font=Font(size=10, weight="bold"), underline=True, foreground=theme["fg_help_text"])
        directions_text.tag_config(tagName="text_1", font=Font(size=8), foreground=theme["fg_help_text"])
        directions_text.tag_config(tagName="heading_2", font=Font(size=10, weight="bold"), underline=True, foreground=theme["fg_help_text"])
        directions_text.tag_config(tagName="text_2", font=Font(size=8), foreground=theme["fg_help_text"])

        # read only
        directions_text.configure(state="disabled")

    def getButtonImage(self, img_name="default") :
        '''
        Loads, resizes, and returns an image.
        '''
        # access resource directory
        rdir_path = os.path.join(os.path.dirname(__file__), '..', 'resources')
        im_path = os.path.join(rdir_path, self.img_dict[img_name])
        # access image
        img = Image.open(im_path)
        # resize image
        img = img.resize(size=(31, 31))
        # add padding
        new_img = Image.new(mode=img.mode, size=(37, 37))
        new_img.paste(img, box=(3, 3))

        return ImageTk.PhotoImage(new_img)
    
    ########## HANDLE HIGH SCORES ##########
    def getHighScores(self) :
        '''
        Loads the high scores json file and returns its contents. 
        If the file does not exist, one is created.
        '''
        default_scores = {"easy": [], "hard": []}
        
        # load json file if it exists
        if os.path.exists(self.high_scores_file) :
            try :
                with open(self.high_scores_file, 'r') as file :
                    return json.load(file)
            except (json.JSONDecodeError, FileNotFoundError) :
                return default_scores
        
        return default_scores
    
    def setHighScores(self) :
        '''
        Attempts to save high scores to a json file.
        '''
        try :
            with open(self.high_scores_file, 'w') as file :
                json.dump(self.high_scores, file, indent=2)
        except Exception as e :
            messagebox.showerror("Error", f"Unable to save high scores: {e}")
    
    def checkHighScore(self, player_time) :
        '''
        Checks if the player finished the game with a time in the top three.
        '''
        current_high_scores = self.high_scores[self.difficulty]

        is_high_score = False
        # if there are fewer than 3 entries, it is automatically a high score
        if len(current_high_scores) < 3 :
            is_high_score = True
        else :
            # check if the player's time is less than the 3rd place time
            third_place_time = max(entry['time'] for entry in current_high_scores)
            if player_time < third_place_time :
                is_high_score = True

        if is_high_score :
            # ask player for username
            username = simpledialog.askstring(
                "New High Score!", 
                f"Congratulations! You achieved a high score!\nTime: {player_time} seconds\nDifficulty: {self.difficulty.title()}\n\nEnter your name:",
                initialvalue="Player"
            )

            # player chose to enter their username 
            if username :
                # add new high score
                new_high_score = {
                    'name': username.strip(),
                    'time': player_time,
                    'date': datetime.now().strftime("%Y-%m-%d")
                }
            
            # add new high score to current list of high scores
            current_high_scores.append(new_high_score)
            # sort from highest to lowest time
            current_high_scores.sort(key=lambda x: x['time'])
            # keep smallest 3 times
            self.high_scores[self.difficulty] = current_high_scores[:3]

            # update json file with new high scores
            self.setHighScores()

            # display updated high scores list
            self.showHighScores()

    def showHighScores(self) :
        '''
        Displays the top 3 high scores (best times) for both game difficulties 
        in a custom message box.
        '''
        theme = self.dark_theme if self.dark_mode else self.light_theme
        
        # create toplevel window
        self.high_scores_display = tk.Toplevel()
        self.high_scores_display.title("")
        self.high_scores_display.grab_set() # prevent interaction with main window when open
        # set dimensions
        self.high_scores_display.geometry("250x300")
        # set background color
        self.high_scores_display.configure(bg=theme["bg_frame"])

        # create title frame
        title_frame = tk.Frame(master=self.high_scores_display, bg=theme["bg_frame"], padx=5, pady=5,
                               relief="ridge", borderwidth=7)
        title_frame.pack(fill="both", expand=True)

        # create scores frame
        scores_frame = tk.Frame(master=self.high_scores_display, bg=theme["bg_frame"], padx=5, pady=5,
                                relief="ridge", borderwidth=7)
        scores_frame.pack(fill="both", expand=True)
        # create title label
        title_label = tk.Label(master=title_frame, text="HIGH SCORES", font=self.font_dict["counter"],
                                   fg=theme["fg_counter"], bg=theme["bg_counter"], padx=3, pady=3, relief="sunken", borderwidth=5)
        
        # create text field for displaying high scores
        scores_text = tk.Text(master=scores_frame, wrap="none", bg=theme["bg_scores"], relief="raised", borderwidth=4)
        
        title_label.pack(fill="x", expand=True)
        scores_text.pack(fill="both", expand=True)

        # customize scores text
        for difficulty in ["easy", "hard"] :
            scores_text.insert("end", f"\n{difficulty.upper()} MODE\n", f"{difficulty}_mode")
            scores_text.tag_config(tagName=f"{difficulty}_mode", font=Font(size=10, weight="bold"), foreground=theme["fg_scores_text"])

            high_scores = self.high_scores[difficulty]

            if not high_scores :
                scores_text.insert("end", "1.\n2.\n3.", "blank_scores")
                scores_text.tag_config(tagName="blank_scores", font=Font(size=8, weight="bold"), 
                                       foreground=theme["fg_scores_text"])
            
            else :
                for i, high_score in enumerate(high_scores, 1) :
                    scores_text.insert("end", str(i) + ".  ", "place")
                    scores_text.tag_config(tagName="place", font=Font(size=8, weight="bold"),
                                           foreground=theme[str(i)])
                    scores_text.insert("end", f"{high_score['name']} | {high_score['time']}s | {high_score['date']}\n", "player")
                    scores_text.tag_config(tagName="player", foreground=theme["fg_scores_text"])
                
            scores_text.insert("end", "\n")

        # read only
        scores_text.configure(state="disabled")
