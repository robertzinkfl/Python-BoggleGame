"""
Robert Zink
rjz11@my.fsu.edu
CIS4930 - Summer 2017
Final: Boggle
4 August 2017
"""

from __future__ import print_function
from PyQt5 import QtWidgets, QtGui, QtCore

import sys
import random
import enchant
import shelve
import datetime


class BoggleGameWindow(QtWidgets.QMainWindow):
    """ BoggleGameWindow class
    The main window of the Boggle Application. Handles the creation of the app window,
    as well as pre- and post-game functions including saving and loading
    """
    def __init__(self):
        """ Function: __init__
        Sets up the window, including the menu bar and window geometry, then calls setup()
        """
        QtWidgets.QMainWindow.__init__(self)
        menu_bar = self.menuBar()
        menu_bar.setNativeMenuBar(False)
        game_menu = menu_bar.addMenu('Game')

        new_game_action = QtWidgets.QAction('New', self)
        new_game_action.triggered.connect(self.setup)
        game_menu.addAction(new_game_action)

        save_game_action = QtWidgets.QAction('Save', self)
        save_game_action.triggered.connect(self.save_game)
        game_menu.addAction(save_game_action)

        load_game_action = QtWidgets.QAction('Load', self)
        load_game_action.triggered.connect(self.load_game)
        game_menu.addAction(load_game_action)

        self.setGeometry(200, 200, 600, 400)

        self.setup()

    def setup(self):
        """ Function: setup
        Starts the Boggle game by creating a new instance of BoggleGame
        :return:
        """
        self.setWindowTitle('Boggle')
        self.game = BoggleGame(self)
        self.setCentralWidget(self.game)

        self.show()

    def start_game(self):
        """ Function: start_game
        This function is used to call setup again, creating a new BoggleGame
        :return:
        """
        self.setup()

    def save_game(self):
        """ Function: save_game
        Used to save an instance of BoggleGame. Stores the time, dice, and entered words
        in a shelf file with the name 'boggleshelf.db'
        :return:
        """
        time = self.game.game_timer.time_left
        entered = self.game.word_list
        dice = self.game.game_dice
        s = shelve.open('boggleshelf.db')
        dt = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        s[dt] = {'time': time, 'entered': entered, 'dice': dice}
        s.close()

    def load_game(self):
        """ Function: load_game
        This function opens up a dialog box with a list of games in the shelf file 'boggleshelf.db'
        If a selection in the list is clicked, load the game with load_from_save
        :return:
        """
        self.dialog = QtWidgets.QDialog()
        dialog_layout = QtWidgets.QVBoxLayout()
        dialog_text = QtWidgets.QLabel()
        dialog_text.setText('Select a game to load:')
        dialog_layout.addWidget(dialog_text)
        dialog_list = QtWidgets.QListWidget()
        s = shelve.open('boggleshelf.db')

        for item in s.keys():
            dialog_list.addItem(item)

        s.close()

        dialog_list.itemClicked.connect(lambda: self.load_from_save(dialog_list.selectedIndexes()[0].data()))

        dialog_layout.addWidget(dialog_list)
        self.dialog.setLayout(dialog_layout)
        self.dialog.exec_()

    def load_from_save(self, savefile):
        """ Function: load_from_save
        Loads a game from a savefile. Closes the dialog opened by load_game,
        and loads the objects from shelve s with key savefile
        :param savefile: The key for the shelve
        :return:
        """
        self.dialog.close()
        s = shelve.open('boggleshelf.db')
        val = s[str(savefile)]
        self.game = BoggleGame(self, val)
        self.setCentralWidget(self.game)
        self.show()


class BoggleDiceGrid(QtWidgets.QWidget):
    """ BoggleDiceGrid class
    Widget that represents a 4x4 grid of Boggle Dice
    """
    def __init__(self, parent, dice):
        """ Function: __init__
        Initializes the widget, calling setup and setting the dice from BoggleGame
        :param parent: The parent widget (BoggleGame)
        :param dice: The dice rolled in the BoggleGame instance
        """
        QtWidgets.QWidget.__init__(self, parent)
        self.dice = dice
        self.setup()

    def setup(self):
        """ Function: setup
        Sets up the BoggleDiceGrid by creating a grid layout and adding 16 DiceFace to it
        :return:
        """
        self.grid = QtWidgets.QGridLayout()
        self.boxes = [DiceFace(self, i) for i in range(16)]

        row = 1
        col = 1
        for item in self.boxes:
            if col < 5:
                self.grid.addWidget(item, row, col, 1, 1)
                col = col + 1
            else:
                row = row + 1
                col = 1
                self.grid.addWidget(item, row, col, 1, 1)
                col = col + 1

        for item in self.boxes:
            item.set_dice(self.dice[item.number])

        self.setLayout(self.grid)


class BoggleGame(QtWidgets.QWidget):
    """ BoggleGame class
    The main game class, handling the UI layout and game logic
    """
    def __init__(self, parent, savefile=None):
        """ Function: __init__
        Sets up the lists necessary for the game, dice and neighbors
        If loading from a savefile, passes in the savefile's dict
        :param parent:
        :param savefile:
        """
        QtWidgets.QWidget.__init__(self, parent)
        self.savefile = savefile

        """ dice contains list of each possible side for 16 6-sided dice """
        self.dice = [['A', 'E', 'A', 'N', 'E', 'G'],
                     ['A', 'H', 'S', 'P', 'C', 'O'],
                     ['A', 'S', 'P', 'F', 'F', 'K'],
                     ['O', 'B', 'J', 'O', 'A', 'B'],
                     ['I', 'O', 'T', 'M', 'U', 'C'],
                     ['R', 'Y', 'V', 'D', 'E', 'L'],
                     ['L', 'R', 'E', 'I', 'X', 'D'],
                     ['E', 'I', 'U', 'N', 'E', 'S'],
                     ['W', 'N', 'G', 'E', 'E', 'H'],
                     ['L', 'N', 'H', 'N', 'R', 'Z'],
                     ['T', 'S', 'T', 'I', 'Y', 'D'],
                     ['O', 'W', 'T', 'O', 'A', 'T'],
                     ['E', 'R', 'T', 'T', 'Y', 'L'],
                     ['T', 'O', 'E', 'S', 'S', 'I'],
                     ['T', 'E', 'R', 'W', 'H', 'V'],
                     ['N', 'U', 'I', 'H', 'M', 'Qu']]

        """ neighbors contains the list of adjoining locations in the 4x4 grid """
        self.neighbors = [[1, 4, 5],
                          [0, 2, 4, 5, 6],
                          [1, 3, 5, 6, 7],
                          [2, 6, 7],
                          [0, 1, 5, 8, 9],
                          [0, 1, 2, 4, 6, 8, 9, 10],
                          [1, 2, 3, 5, 7, 9, 10, 11],
                          [2, 3, 6, 10, 11],
                          [4, 5, 9, 12, 13],
                          [4, 5, 6, 8, 10, 12, 13, 14],
                          [5, 6, 7, 9, 11, 13, 14, 15],
                          [6, 7, 10, 14, 15],
                          [8, 9, 13],
                          [8, 9, 10, 12, 14],
                          [9, 10, 11, 13, 15],
                          [10, 11, 14]]

        self.score = 0
        self.word_list = []
        self.scored = []
        self.setup()

    def setup(self):
        """ Function: setup
        Sets up the game dictionary, layout, dice, etc.
        If loading from a save, initializes game with saved variables
        :return:
        """
        self.d = enchant.Dict("en_US")
        self.vbox = QtWidgets.QVBoxLayout()
        self.top_hbox = QtWidgets.QHBoxLayout()
        self.bot_hbox = QtWidgets.QHBoxLayout()
        self.game_dice = self.roll_dice()

        if self.savefile:
            self.game_dice = self.savefile['dice']

        self.boggle_boxes = BoggleDiceGrid(self, self.game_dice)

        self.entered_words = QtWidgets.QTextEdit(self)

        if self.savefile:
            self.word_list = self.savefile['entered']
            for item in self.word_list:
                self.entered_words.append(item)

        self.word_entry = QtWidgets.QLineEdit(self)

        self.game_timer = GameTimer(self)

        if self.savefile:
            self.game_timer.set_time_left(self.savefile['time'])

        self.word_entry.returnPressed.connect(self.add_entered_word)

        self.top_hbox.addWidget(self.boggle_boxes, 1)
        self.top_hbox.addWidget(self.entered_words)

        self.bot_hbox.addWidget(self.word_entry)
        self.bot_hbox.addWidget(self.game_timer)

        self.vbox.addLayout(self.top_hbox)
        self.vbox.addLayout(self.bot_hbox)
        self.setLayout(self.vbox)

        self.game_timer.start_timer()

        self.show()

    def add_entered_word(self):
        """ Function: add_entered_word
        Adds a word entered by user into entered_words and word_list
        :return:
        """
        self.entered_words.append(self.word_entry.text())
        self.word_list.append(self.word_entry.text())
        self.word_entry.clear()

    def roll_dice(self):
        """ Function: roll_dice
        :return: A shuffled list containing one side from each dice
        """
        for item in self.dice:
            random.shuffle(item)
        rolled_dice = [item[0] for item in self.dice]
        random.shuffle(rolled_dice)
        return rolled_dice

    def calculate_score(self):
        """ Function: calculate_score
        Calculates the final score for the user by checking the word and testing its validity
        If the word is valid, it is scored and the points added to score
        :return: The score for the finished game
        """
        for item in self.word_list:
            if self.check_no_duplicates(item) is False:
                continue

            if self.check_length(item) is False:
                continue

            if self.check_word(item) is False:
                continue

            if self.check(item) is False:
                continue

            word_points = self.score_word(item)
            self.score = self.score + word_points
        return self.score

    def check_no_duplicates(self, item):
        """ Function: check_no_duplicates
        Adds an item to scored if it has not already been scored
        :param item: Item to check for duplicates in scored
        :return: Boolean, True if no duplicates of item found in scored
        """
        if item in self.scored:
            return False
        else:
            self.scored.append(item)
            return True

    def check_length(self, item):
        """ Function: check_length
        Checks that the length of item is valid
        :param item: Item to have its length checked
        :return: Boolean, True if word length is >2
        """
        if len(item) < 3:
            return False
        else:
            return True

    def check_word(self, item):
        """ Function: check_word
        Checks if word item is a dictionary word
        :param item: Item to be checked against an en_US PyEnchant dictionary
        :return: Boolean, True if item is found in dictionary
        """
        if self.d.check(item) is False:
            return False
        else:
            return True

    def locations_found(self, item, counter):
        """ Function: locations_found
        Creates a list of locations where the character of item[counter] is found in the game_dice
        :param item: The word being evaluated
        :param counter: The counter for the index of the char in word to check
        :return: List of found locations
        """
        found = [i for i, j in enumerate(self.game_dice) if j == item[counter]]
        return found

    def check(self, item):
        """ Function: check
        Creates a list containing the lists of locations of each letter
        Short-circuits to false if any list is empty (does not appear in grid)
        Relies on recursive function check_connecting to fully evaluate
        :param item: The word being evaluated
        :return: Boolean, True if item appears in valid grid locations in rolled_dice
        """
        letter_locs = []
        for x in range(len(item)):
            letter_locs.append(self.locations_found(item.upper(), x))

        if [] in letter_locs:
            return False

        if self.check_connecting(letter_locs, [], item, 0) is True:
            return True
        else:
            return False

    def check_connecting(self, letter_locs, used_locs, item, counter):
        """ Function: check_connecting
        Recursively calls itself in an attempt to verify a path through the grid exists for item
        :param letter_locs: A list of lists containing the locations of each letter in the grid
        :param used_locs: A list of locations in the grid that have already been visited
        :param item: The word being evaluated
        :param counter: How far along in the word the process is
        :return: Boolean, True if valid path for item is found in letter_locs
        """
        if counter == len(item) - 1:
            return True
        else:
            for loc in letter_locs[counter]:
                if loc in used_locs:
                    continue
                neighbors_current = set(self.neighbors[loc])
                next_locs = set(letter_locs[counter + 1])
                if not neighbors_current.isdisjoint(next_locs):
                    used_locs.append(loc)
                    return self.check_connecting(letter_locs, used_locs, item, counter + 1)
                else:
                    continue
            return False

    def score_word(self, item):
        """ Function: score_word
        Scores the word being evaluated
        :param item: The word being evaluated
        :return: Int, the score of the word in item
        """
        if len(item) == 3 or len(item) == 4:
            return 1
        elif len(item) == 5:
            return 2
        elif len(item) == 6:
            return 3
        elif len(item) == 7:
            return 5
        elif len(item) > 7:
            return 11
        else:
            return 0


class GameTimer(QtWidgets.QLCDNumber):
    """ GameTimer class
    Widget to control the game timer, and the timer LCD display
    """
    def __init__(self, parent):
        """ Function: __init__
        Calls the setup function
        :param parent: The parent widget (BoggleGame)
        """
        QtWidgets.QLCDNumber.__init__(self, parent)
        self.setup()

    def setup(self):
        """ Function: setup
        Creates the timer (set to 3 minutes)
        :return:
        """
        self.timer = QtCore.QTimer()
        self.time_left = 180
        self.setNumDigits(4)
        self.timer.timeout.connect(self.timer_tick)

        self.show()

    def updateLCD(self):
        """ Function: updateLCD
        Updates the time remaining that is displayed on the LCD
        :return:
        """
        displayed_time = "%d:%02d" % (self.time_left / 60, self.time_left % 60)
        self.display(displayed_time)

    def start_timer(self):
        """ Function: start_timer
        Starts the timer
        :return:
        """
        self.updateLCD()
        self.timer.start(1000)

    def timer_tick(self):
        """ Function: timer_tick
        At every timeout, subtracts a second from time_left
        Once time_left reaches 0, ends the game
        :return:
        """
        self.time_left -= 1
        self.updateLCD()
        if self.time_left <= 0:
            self.timer.stop()
            popup = EndGameBox(self.parent().calculate_score())
            reply = popup.exec_()
            if reply == QtWidgets.QMessageBox.Yes:
                self.parent().parent().start_game()
            else:
                sys.exit()

    def set_time_left(self, time_to_set):
        """ Function: set_time_left
        Allows the time to be set manually
        Used when a game is being loaded from a save
        :param time_to_set: The time to set on the timer
        :return:
        """
        self.time_left = time_to_set


class EndGameBox(QtWidgets.QMessageBox):
    """ EndGameBox class
    The popup to display at the conclusion of a Boggle game
    """
    def __init__(self, score):
        """ Function: __init__
        Sets up the message box widget
        :param score: Int, the player's final score
        """
        QtWidgets.QMessageBox.__init__(self)
        self.score = score
        self.setText("Time's up!\nScore: " + str(score) + "\nWould you like to play again?")
        self.addButton(self.Yes)
        self.addButton(self.No)


class DiceFace(QtWidgets.QLabel):
    """ DiceFace class
    Widget to display a face of a Boggle dice as part of the grid
    """
    def __init__(self, parent, number):
        """ Function: __init__
        Sets the number of the dice, and calls setup
        :param parent: Parent widget (BoggleDiceGrid)
        :param number: The number of the dice
        """
        QtWidgets.QLabel.__init__(self, parent)
        self.number = number
        self.setup()

    def setup(self):
        """ Function: setup
        Sets up the dice face, with temporary text displaying the number of the dice
        :return:
        """
        self.setText(str(self.number))
        self.setFont(QtGui.QFont('SansSerif', 20))
        self.setAlignment(QtCore.Qt.AlignCenter)
        self.setStyleSheet('border: 1px solid black; background-color: white;')
        self.show()

    def set_dice(self, face):
        """ Function: set_dice
        Used to set the text of the DiceFace to the letter on the face of the dice in the current game
        :param face: The text to display
        :return:
        """
        self.setText(face)


class WelcomeMessageBox(QtWidgets.QMessageBox):
    """ WelcomeMessageBox class
    Widget that displays a message box at launch to ask user if they want to load a saved game
    """
    def __init__(self):
        """ Function: __init__
        Sets up the message box
        """
        QtWidgets.QMessageBox.__init__(self)
        self.setText('Would you like to start a new game, or load a saved game?')
        self.addButton('Start New Game', QtWidgets.QMessageBox.NoRole)
        self.addButton('Load Game', QtWidgets.QMessageBox.YesRole)


if __name__ == "__main__":
    """ Module final.py
    Launches the Boggle Game application
    """
    app = QtWidgets.QApplication(sys.argv)
    welcome_box = WelcomeMessageBox()
    ret = welcome_box.exec_()
    if ret == QtWidgets.QMessageBox.AcceptRole:
        main_window = BoggleGameWindow()
    else:
        main_window = BoggleGameWindow()
        main_window.load_game()
    app.exec_()
