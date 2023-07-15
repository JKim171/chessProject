# imports
import tkinter as tk
from tkinter import filedialog
import ttkbootstrap as ttk
import chess.pgn
import io
import itertools
import os
os.environ['path'] += r';C:\Program Files\UniConvertor-2.0rc5\dlls'
from cairosvg import svg2png
from PIL import ImageTk, Image
import time

# setting up the GUI window

class MainApplication:

    def __init__(self):
        self.root = ttk.Window(title="Chess Opening Analyzer", size=(800, 800), themename="darkly")
        self.numberOfMoves = 1
        self.selectedColor = tk.StringVar()
        self.selectedColor = None

        self.title = ttk.Label(self.root, text="Chess Opening Analyzer", font=("SimHei", 32), bootstyle="primary")
        self.title.pack(padx=10, pady=10)

        self.numberMovesTitle = ttk.Label(self.root, text="How many moves would you like to analyze in the opening?",
                                          font=("SimHei", 16), bootstyle="primary")
        self.numberMovesTitle.pack(padx=10, pady=(50, 20))

        self.numberMoves = ttk.Scale(self.root, from_=1, to=10, length=500, bootstyle="primary",
                                     command=lambda x: self.scaler(self.numberMovesLabel, self.numberMoves))
        self.numberMoves.pack(padx=10, pady=(10, 0))

        self.numberMovesLabel = ttk.Label(self.root, text="1", font=("SimHei", 16), bootstyle="primary")
        self.numberMovesLabel.pack(padx=10, pady=10)

        self.whiteButton = ttk.Radiobutton(self.root, text="White", value="white", variable=self.selectedColor, bootstyle="primary-outline-toolbutton", command=self.updateRadioButtonWhite)
        self.whiteButton.pack(padx=10, pady=20)

        self.blackButton = ttk.Radiobutton(self.root, text="Black", value="black", variable=self.selectedColor, bootstyle="primary-outline-toolbutton", command=self.updateRadioButtonBlack)
        self.blackButton.pack(padx=10, pady=20)

        self.uploadButton = ttk.Button(self.root, text='Upload a PGN file with your chess games',
                                       command=self.UploadAction)
        self.uploadButton.pack(padx=10, pady=50)

        self.submitButton = ttk.Button(self.root, text="Submit", command=self.calculateOpenings)
        self.submitButton.pack(side="bottom", padx=10, pady=120)

        self.root.mainloop()

    def updateRadioButtonWhite(self):
        self.selectedColor = "white"

    def updateRadioButtonBlack(self):
        self.selectedColor = "black"

    # scaler for the slider so it shows the number
    def scaler(self, label, scale):
        label.config(text=f'{int(scale.get())}')
        self.numberOfMoves = int(scale.get())

    def UploadAction(self, event=None):
        self.filename = filedialog.askopenfilename(filetypes=(("PGN files", "*.PGN"),))
        print('Selected:', self.filename)
        self.filenameLabel = ttk.Label(self.root, text=self.filename, bootstyle="primary")
        self.filenameLabel.pack()

    def calculateOpenings(self):  # Caclulates openings and also displays the next window

        # creating dictionary which will have info from pgn file
        data = {}
        print(self.selectedColor)
        # importing important data from the pgn into dictionary
        file = self.filename

        with open(file, 'r') as f:
            for line in f.readlines():
                if line[:2] == "1.":
                    firstMoves = line.split(str(self.numberOfMoves + 1) + ".")[0]
                    if self.selectedColor == "white":
                        if firstMoves not in data:
                            data[firstMoves] = [0, 0, 0]
                        if "1-0" in line[-10:]:
                            data[firstMoves][0] += 1
                        elif "1/2-1/2" in line[-10:]:
                            data[firstMoves][1] += 1
                        elif "0-1" in line[-10:]:
                            data[firstMoves][2] += 1
                    elif self.selectedColor == "black":
                        if firstMoves not in data:
                            data[firstMoves] = [0, 0, 0]
                        if "0-1" in line[-10:]:
                            data[firstMoves][0] += 1
                        elif "1/2-1/2" in line[-10:]:
                            data[firstMoves][1] += 1
                        elif "1-0" in line[-10:]:
                            data[firstMoves][2] += 1
        for key, value in data.items():
            numberOfGames = value[0] + value[2] + (value[1] * 0.5)  # Gives draws half of the impact
            if value[0] == 0 and value[2] == 0:
                winRate = 0.5
            else:
                winRate = value[0] / (value[0] + value[2])
            impactFactor = (winRate - 0.5) * numberOfGames
            value.append(impactFactor)

        # Notes: algorithm will be (winRate - 0.5) * numberOfGames = Impact Factor,   Organize by impact factor

        sortedData = dict(sorted(data.items(), key=lambda item: item[1][3]))
        print(sortedData)

        # Creating the png chessboard of the position
        fen = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'
        board = chess.Board(fen)
        if self.selectedColor == "white":
            boardsvg = chess.svg.board(board=board)
        elif self.selectedColor == "black":
            boardsvg = chess.svg.board(board=board, orientation=chess.BLACK)
        f = open("BoardVisualised.SVG", "w")
        f.write(boardsvg)
        f.close()

        svg2png(file_obj=open("BoardVisualised.SVG", "rb"), write_to='output.png')

        # Resizing the image
        tempBoardImage = Image.open('output.png')
        resizeBoardImage = tempBoardImage.resize((400,400))
        resizeBoardImage.save("output.png")

        boardImage = ImageTk.PhotoImage(Image.open("output.png"))

        # Setting up the new window with information
        top = ttk.window.Toplevel(title="Chess Opening Analyzer", size=(800, 800))
        boardLabel = ttk.Label(top, image=boardImage)
        boardLabel.image = boardImage
        boardLabel.pack(side="top")

        # Create Multiple Buttons with different commands
        button_dict = {}
        leftButtonFrame = tk.Frame(top)
        leftButtonFrame.pack(side="left", anchor="sw", pady=10)
        leftLabel = ttk.Label(leftButtonFrame, text="Your weakest openings:", bootstyle="primary", font=("SimHei", 16))
        leftLabel.pack(side="top", padx=10, pady=10, anchor="nw")
        for key, value in itertools.islice(sortedData.items(), 5):
            def func(x=key): # In future this function will update the board state
                pgn = io.StringIO(x)
                currentGame = chess.pgn.read_game(pgn)
                board = currentGame.board()
                for move in currentGame.mainline_moves():
                    board.push(move)
                    if self.selectedColor == "white":
                        boardsvg = chess.svg.board(board=board)
                    elif self.selectedColor == "black":
                        boardsvg = chess.svg.board(board=board, orientation=chess.BLACK)
                    f = open("BoardVisualised.SVG", "w")
                    f.write(boardsvg)
                    f.close()

                    svg2png(file_obj=open("BoardVisualised.SVG", "rb"), write_to='output.png')

                    # Resizing the image
                    tempBoardImage = Image.open('output.png')
                    resizeBoardImage = tempBoardImage.resize((400, 400))
                    resizeBoardImage.save("output.png")

                    boardImage = ImageTk.PhotoImage(Image.open("output.png"))
                    boardLabel.configure(image=boardImage)
                    boardLabel.image = boardImage
                    boardLabel.pack(side="top")
                    top.update_idletasks()
                    time.sleep(0.5)


            button_dict[key] = tk.Button(leftButtonFrame, text=key, command=func, width=50, justify="left", wraplength=320)
            button_dict[key].pack(side="top", anchor="w", padx=20, pady=10)

        sortedData = dict(reversed(list(sortedData.items())))
        button_dict = {}
        rightButtonFrame = tk.Frame(top)
        rightButtonFrame.pack(side="right", anchor="se", pady=10)
        rightLabel = ttk.Label(rightButtonFrame, text="Your strongest openings:", bootstyle="primary", font=("SimHei", 16))
        rightLabel.pack(side="top", padx=10, pady=10, anchor="nw")
        for key, value in itertools.islice(sortedData.items(), 5):
            def func(x=key):  # In future this function will update the board state
                pgn = io.StringIO(x)
                currentGame = chess.pgn.read_game(pgn)
                board = currentGame.board()
                for move in currentGame.mainline_moves():
                    board.push(move)
                    if self.selectedColor == "white":
                        boardsvg = chess.svg.board(board=board)
                    elif self.selectedColor == "black":
                        boardsvg = chess.svg.board(board=board, orientation=chess.BLACK)
                    f = open("BoardVisualised.SVG", "w")
                    f.write(boardsvg)
                    f.close()

                    svg2png(file_obj=open("BoardVisualised.SVG", "rb"), write_to='output.png')

                    # Resizing the image
                    tempBoardImage = Image.open('output.png')
                    resizeBoardImage = tempBoardImage.resize((400, 400))
                    resizeBoardImage.save("output.png")

                    boardImage = ImageTk.PhotoImage(Image.open("output.png"))
                    boardLabel.configure(image=boardImage)
                    boardLabel.image = boardImage
                    boardLabel.pack(side="top")
                    top.update_idletasks()
                    time.sleep(0.5)

            button_dict[key] = tk.Button(rightButtonFrame, text=key, command=func, width=50, justify="left", wraplength=320)
            button_dict[key].pack(side="top", anchor="w", padx=20, pady=10)


MainApplication()
