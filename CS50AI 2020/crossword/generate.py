import sys

from crossword import *


class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        w, h = draw.textsize(letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """
        for word in self.domains:
            new_domains = []
            for w in self.domains[word]:
                if len(w) == word.length:
                    new_domains.append(w)
            self.domains[word] = new_domains


    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        revised = False

        x_domain = self.domains[x].copy()
        y_domain = self.domains[y]

        overlap = self.crossword.overlaps[x,y]
        if overlap == None:
            return False
        
        # index of both word that intersect
        i, j = overlap
        print(f"Over lap index value: ",i , j)
        
        for x_word in x_domain:
            if not any(
                map(lambda y_word: (x_word != y_word) and (x_word[i] == y_word[j]), y_domain)
                ):
            # for y_word in y_domain:
            #     if not (x_word != y_word and (x_word[i] == y_word[j])):
                print(f"removed word:", x_word)
                self.domains[x].remove(x_word)
                revised = True
        return revised


    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        queue = list()
        if arcs == None:
            for vp in self.crossword.overlaps:
                if self.crossword.overlaps[vp] is not None:
                    queue.append((vp[0], vp[1]))
        else:
            queue = list(arcs)

        result = False
        while len(queue) >0:
            x, y = queue.pop(0)
            if self.revise(x,y):
                result = True
                if len(self.domains[x]) == 0:
                    return False
                # remove all of the remaining values from a domain
                domain = self.crossword.neighbors(x) - {y}
                for k in domain:
                    # add additional arcs to your queue to ensure that other arcs stay consistent.
                    queue.append({k, x})
        return result


    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """

        # all crossword has be assigned
        if len(assignment) == len(self.crossword.variables):
            return True
        else:
            return False


    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """

        # for key, val in assignment.items():
        #     if key.length != len(val):
        #         return False
        
    

        for v1 in assignment:
            for v2 in assignment:
                if v1 == v2:
                    continue
                overlap = self.crossword.overlaps[v1, v2]
                if overlap is None:
                    continue
                if assignment[v1][overlap[0]] != assignment[v2][overlap[1]]:
                    return False
        return True


    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        def count(item, neighors):
            n = 0
            for neighbor in neighors:
                i, j = self.crossword.overlaps[var, neighbor]
                for n_item in self.domains[neighbor]:
                    if item[i] != n_item[j]:
                        n += 1
            return n

        #ruled out for neighboring unassigned variables.
        neighbors = self.crossword.neighbors(var) - set(assignment)
        # l = count(self.domains[var], neighbors)
        # sorted_l = sorted(l)
        # printf("list ", l)
        return sorted(
            list(self.domains[var]), key=lambda item: count(item, neighbors)
        )



    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        list_val = []
        for v in self.crossword.variables:
            if v not in assignment:
                list_val.append(v)
        k = 0
        
        for i in range (1, len(list_val)):
            i_domainsize = len(self.domains[list_val[i]])
            k_domainsize = len(self.domains[list_val[k]])

            # if find the smaller domain size update i
            if i_domainsize < k_domainsize:
                k = i
            elif i_domainsize > k_domainsize:
                continue
            
            # if they are equal
            k_degree = len(self.crossword.neighbors(list_val[k]))
            i_degree = len(self.crossword.neighbors(list_val[i]))

            if i_degree > k_degree:
                k = i
        return list_val[k]


    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        if len(assignment) == len(self.crossword.variables):
            return assignment
        
        var = self.select_unassigned_variable(assignment)

        for value in self.order_domain_values(var, assignment):
            new_assignment = assignment.copy()
            new_assignment[var] = value
            if self.consistent(new_assignment):
                result = self.backtrack(new_assignment)
                neighbors = self.crossword.neighbors(var)
                arcs = [(neighbor, var) for neighbor in neighbors]
                # for neighbor in neighbors:
                #     arcs.append((neighbor, var))
                assign = True
                
                while assign:
                    assign = False
                    if not self.ac3(arcs):
                        continue    
                    for neighbor in neighbors:
                        if len(self.domains[neighbor]) == 1:
                            item = self.domains[neighbor].pop()
                            self.domains[neighbor].append(item)
                            new_assignment[neighbor] = item
                            assign = True
                            nns = self.crossword.neighbors(neighbor)
                            arcs += [(nn, neighbor) for nn in nns]
                            # for n in nns:
                            #     arcs += [(n, neighbor)]

                if result is not None:
                    return result
        return None



def main():

    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()
