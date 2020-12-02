import itertools
import random
from random import seed
import secrets

class Minesweeper():
    """
    Minesweeper game representation
    """

    def __init__(self, height=8, width=8, mines=8):

        # Set initial width, height, and number of mines
        self.height = height
        self.width = width
        self.mines = set()

        # Initialize an empty field with no mines
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)

        # Add mines randomly
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True

        # At first, player has found no mines
        self.mines_found = set()

    def print(self):
        """
        Prints a text-based representation
        of where mines are located.
        """
        for i in range(self.height):
            print("--" * self.width + "-")
            for j in range(self.width):
                if self.board[i][j]:
                    print("|X", end="")
                else:
                    print("| ", end="")
            print("|")
        print("--" * self.width + "-")

    def is_mine(self, cell):
        i, j = cell
        return self.board[i][j]

    def nearby_mines(self, cell):
        """
        Returns the number of mines that are
        within one row and column of a given cell,
        not including the cell itself.
        """

        # Keep count of nearby mines
        count = 0

        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                # Update count if cell in bounds and is mine
                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1

        return count

    def won(self):
        """
        Checks if all mines have been flagged.
        """
        return self.mines_found == self.mines


class Sentence():
    """
    Logical statement about a Minesweeper game
    A sentence consists of a set of board cells,
    and a count of the number of those cells which are mines.
    """

    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        """
        Returns the set of all cells in self.cells known to be mines.
        """
        if len(self.cells) <= self.count:
            return set(self.cells)
        return set()
        # result = set()
        # for x in self.cells:
        #     if x.count == 1:
        #         result.add()
        # return result


    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        # print("Inside known_safes function in sentence class")
        # result = set()
        # for x in self.cells:
        #     if x.count == 0:
        #         result.add()
        # return result
        if self.count == 0:
            return set(self.cells)
        return set()


    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        # print("Inside Sentence Class, mark_mine function , cell value =", cell)
        # if cell not in self.cells:
        #     return
        
        new_cell = self.cells.copy()
        if cell in new_cell:
            new_cell.remove(cell)
            self.cells = new_cell
            # Sentence(cell, 1)
            self.count = max(0, self.count -1)
        else:
            return


    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
        new_cell = self.cells.copy()
        if cell in new_cell:
            new_cell.remove(cell)
            self.cells = new_cell
            # Sentence(cell, 0)
        else:
            return


        # remove_cell = set()
        # # remove_cell = self.cells.copy()
        # for i in self.cells:
        #     if cell == i:
        #         remove_cell = cell
        #         print("remove cell=", remove_cell)
        #     Sentence(cell, 0)
        # if len(remove_cell) > 1:
        #     self.cells.remove(remove_cell)
        # print("Self.cells in sentence", self.cells)


        # for sentence in MinesweeperAI().knowledge:
        #     print("Inside Sentence Class, mark_safe function, cell value =", cell)
        #     print("inside loop: ")
        #     if cell in sentence:
        #         new_cell = list(sentence.cells - cell)
        #         sentence.cell = new_cell
        #     print("Sentence =", sentence.__str__())




class MinesweeperAI():
    """
    Minesweeper game player
    """

    def __init__(self, height=8, width=8):

        # Set initial height and width
        self.height = height
        self.width = width

        # Keep track of which cells have been clicked on
        self.moves_made = set()

        # Keep track of cells known to be safe or mines
        self.mines = set()
        self.safes = set()

        # List of sentences about the game known to be true
        self.knowledge = []

    def mark_mine(self, cell):
        """
        Marks a cell as a mine, and updates all knowledge
        to mark that cell as a mine as well.
        """
        self.mines.add(cell)
        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe(self, cell):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        """
        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)

    def add_knowledge(self, cell, count):
        """
        Called when the Minesweeper board tells us, for a given
        safe cell, how many neighboring cells have mines in them.

        This function should:
            1) mark the cell as a move that has been made
            2) mark the cell as safe
            3) add a new sentence to the AI's knowledge base
               based on the value of `cell` and `count`
            4) mark any additional cells as safe or as mines
               if it can be concluded based on the AI's knowledge base
            5) add any new sentences to the AI's knowledge base
               if they can be inferred from existing knowledge
        """
        self.moves_made.add(cell)
        self.mark_safe(cell)
        
        result = set()
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                if (i, j) == cell:
                    continue
                
                if 0 <= i < self.height and 0 <= j < self.width:
                    new_cell = (i,j)
                    if new_cell not in self.moves_made:
                        result.add(new_cell)
        new_sentence = Sentence(result, count)
        self.knowledge.append(new_sentence)
 
        for sentence in self.knowledge:
            # if sentence.count == 0:
            #     print("Check sentence == 0...", sentence)
            #     for i in sentence.cells:
            #         self.mark_safe(i)
            safes = sentence.known_safes()
            for safe in safes:
                self.mark_safe(safe)
        
        for sentence in self.knowledge:
            # if len(sentence.cells) == sentence.count:
            #     print("Check sentence == count...", sentence)
            #     for i in sentence.cells:
            #         self.mark_mine(i)
            mines = sentence.known_mines()
            for mine in mines:
                self.mark_mine(mine)
        

        for s1 in self.knowledge:
            for s2 in self.knowledge:
                    if s1.cells >= s2.cells:
                        continue   
                    if s1.cells.issubset(s2.cells):
                        print("Found subset.........")
                        print("Comparing....")
                        print("S1 =", s1)
                        print("S2 =", s2)
                        s2.cells = s2.cells - s1.cells
                        s2.count = max(0, s2.count - s1.count)
                        print("New sentence = ",s2)
                        # self.knowledge.append(s3)
                        
                    elif s2.cells.issubset(s1.cells):
                        print("Found subset.........")
                        print("Comparing....")
                        print("S1 =", s1)
                        print("S2 =", s2)
                        s1.cells = s1.cells - s2.cells
                        s1.count = max(0, s1.count - s2.count)
                        # self.knowledge.append(s3)
                        
        self.clean()
        
        print("safes =", [c for c in self.safes if c not in self.moves_made])
        print("Mines = ", self.mines)

        for sentence in self.knowledge:
            print("Sentence: ", sentence.__str__())
        

    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """
        for i in range(self.width):
            for j in range(self.height):
                cell = (i, j)
                if (cell in self.safes and cell not in self.moves_made):
                    print("Cell made by AI", cell)
                    return cell
        return None

    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """
        print("Making random move:")
        for i in range(self.width):
            for j in range(self.height):
                value1 = list(range(0, self.width - 1))
                value2 = list(range(0, self.height -1))
                val1 = secrets.choice(value1)
                val2 = secrets.choice(value2)
                cell = (val1, val2)
                if cell not in self.mines and cell not in self.moves_made:
                    print("Random move made: ", cell)
                    return cell
        return None

    def clean(self):
        new=[]
        for s in self.knowledge:
            if s not in new:
                if s.cells:
                    new.append(s)
        self.knowledge=new
