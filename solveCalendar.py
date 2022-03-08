#!/home/amin/miniconda3/bin/python

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import sys
import igraph as ig

class Coordinates:
    """A class to keep the location of each piece in cartesian coordinates"""
    def __init__(self, xlist, ylist):
        self.x = xlist
        self.y = ylist


class PuzzlePiece:
    """A class to instantiate puzzle pieces"""
    x = 0
    y = 0
    mir = False
    rot = 0

    def __init__(self, piece_id, xlist, ylist):
        self.piece_id = piece_id
        self.coords = Coordinates(xlist, ylist)
    
    def __str__(self):
        return (
            f"piece_id : {self.piece_id}\n"
            f"x : {self.x}\n"
            f"y : {self.y}\n"
            f"mirror: {self.mir}\n"
            f"rotate: {self.rot}\n"
            f"x-coords: {','.join(str(xval) for xval in self.coords.x)}\n"
            f"y-coords: {','.join(str(yval) for yval in self.coords.y)}"
        )
    
    def rotate(self):
        self.rot = self.rot + 1
        if(self.rot == 4):
            self.rot = 0
        self.coords = Coordinates(-(self.coords.y-self.y), self.coords.x-self.x)
        self.coords.x = self.coords.x + self.x
        self.coords.y = self.coords.y + self.y

    def mirror(self):
        self.mir = not (self.mir)
        self.coords = Coordinates(-(self.coords.x - self.x), self.coords.y)
        self.coords.x = self.coords.x + self.x

    def move(self, x, y):
        self.x = self.x + x
        self.y = self.y + y
        self.coords.x = self.coords.x + x
        self.coords.y = self.coords.y + y
        
    def reset(self):
        while(self.rot != 0):
            self.rotate()
        if(self.mir):
            self.mirror()
        self.move(-self.x, -self.y)


class PuzzleBoard:
    """A class to instantiate the puzzle board"""
    def __init__(self, month, day):
        self.board = None
        self.month = (3 + (month - 1) // 6, 3 + (month - 1) % 6)
        self.day = (5 + (day - 1) // 7, 3 + (day - 1) % 7)
        self.clear()

    def clear(self):
        self.board = np.zeros((13, 13), dtype=int)
        self.board[[0,1,2,10,11,12],:] = -1
        self.board[:,[0,1,2,10,11,12]] = -1
        self.board[3:5, 9] = -1
        self.board[9, 6:10] = -1
        self.board[self.month[0], self.month[1]] = -2
        self.board[self.day[0], self.day[1]] = -2

    def test_graph(self):
        """This function reduces the number of trials by checking for 
        bipartite graph generation on the puzzle board. If such a graph is 
        generated where one graph part includes a small number of tiles that 
        can never be covered with any pieces, this function stops that trial."""
        g = ig.Graph.Lattice([13, 13], circular=False)
        idx = list((self.board != 0).reshape(169))
        idx = list(np.where(idx)[0])
        g.delete_vertices(idx)
        if(g.is_connected()):
            return(True)
        else:
            thresh = 5
            for i in range(len(g.components())):
                thresh = min(thresh, len(g.components()[i]))
            if(thresh < 5):
                return(False)
            else:
                return(True)

    def show(self):
        plt.imshow(self.board)
        plt.show()

    def place(self, piece):
        self.board[piece.coords.x, piece.coords.y] = piece.piece_id
    
    def remove(self, piece):
        self.board[piece.coords.x, piece.coords.y] = 0
    
    def test(self, piece):
        if(np.sum(np.abs(self.board[piece.coords.x, piece.coords.y])) == 0):
            return(True)
        else:
            return(False)


def get_pieces(filename):
    df = pd.read_csv(filename)
    df = df.to_numpy()
    ids = np.unique(df[:, 0])
    pieces = []
    for i in range(len(ids)):
        idx = (df[:, 0] == i + 1)
        pieces.append(PuzzlePiece(ids[i], df[idx, 1], df[idx, 2]))
        print(f"Loaded piece {ids[i]}!")
    return(pieces)


def place_piece(board, pieces, i):
    """This function performs piece placement trials."""
    if(i > 7):
        print("All pieces tried!")
        print("Number of remaining empty tiles:")
        return(np.sum(board.board == 0))
    else:
        print(f"{pieces[i].piece_id}")  # Trying one piece at a time.

        for x in range(3, 10):
            for y in range(3, 10):

                if(board.board[x, y] == 0): # Try picked piece.
                    print(f"piece: {pieces[i].piece_id}, x: {x}, y: {y}")
                    pieces[i].move(x, y)

                    if(board.test(pieces[i])):
                        board.place(pieces[i])
                        if(board.test_graph()):
                            if(place_piece(board, pieces, i + 1) == 0):
                                return(0)
                        board.remove(pieces[i])
                    pieces[i].rotate() # rotate 90 and try again.

                    if(board.test(pieces[i])):
                        board.place(pieces[i])
                        if(board.test_graph()):
                            if(place_piece(board, pieces, i + 1) == 0):
                                return(0)
                        board.remove(pieces[i])
                    pieces[i].rotate() # rotate 180 and try again.

                    if(board.test(pieces[i])):
                        board.place(pieces[i])
                        if(board.test_graph()):
                            if(place_piece(board, pieces, i + 1) == 0):
                                return(0)
                        board.remove(pieces[i])
                    pieces[i].rotate() # rotate 270 and try again.

                    if(board.test(pieces[i])):
                        board.place(pieces[i])
                        if(board.test_graph()):
                            if(place_piece(board, pieces, i + 1) == 0):
                                return(0)
                        board.remove(pieces[i])
                    pieces[i].rotate()
                    pieces[i].mirror() # mirror and try again.

                    if(board.test(pieces[i])):
                        board.place(pieces[i])
                        if(board.test_graph()):
                            if(place_piece(board, pieces, i + 1) == 0):
                                return(0)
                        board.remove(pieces[i])
                    pieces[i].rotate() # mirror, rotate 90 and try again.

                    if(board.test(pieces[i])):
                        board.place(pieces[i])
                        if(board.test_graph()):
                            if(place_piece(board, pieces, i + 1) == 0):
                                return(0)
                        board.remove(pieces[i])
                    pieces[i].rotate() # mirror, rotate 180 and try again.

                    if(board.test(pieces[i])):
                        board.place(pieces[i])
                        if(board.test_graph()):
                            if(place_piece(board, pieces, i + 1) == 0):
                                return(0)
                        board.remove(pieces[i])
                    pieces[i].rotate() # mirror, rotate 270 and try again.

                    if(board.test(pieces[i])):
                        board.place(pieces[i])
                        if(board.test_graph()):
                            if(place_piece(board, pieces, i + 1) == 0):
                                return(0)

                        board.remove(pieces[i])

                    pieces[i].reset() # if none of the 8 configurations worked

    return(np.sum(board.board == 0))


def main():
    month = int(input("Enter month: "))
    day = int(input("Enter day: "))
    board = PuzzleBoard(month, day)
    pieces = get_pieces('pieces.csv')
    print(f"Number of empty tiles: {np.sum(board.board == 0)}")
    place_piece(board, pieces, 0)
    board.show()

if __name__ == '__main__':
    main()
