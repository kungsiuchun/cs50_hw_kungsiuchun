import nltk
import sys


TERMINALS = """
Adj -> "country" | "dreadful" | "enigmatical" | "little" | "moist" | "red"
Adv -> "down" | "here" | "never"
Conj -> "and" | "until"
Det -> "a" | "an" | "his" | "my" | "the"
N -> "armchair" | "companion" | "day" | "door" | "hand" | "he" | "himself"
N -> "holmes" | "home" | "i" | "mess" | "paint" | "palm" | "pipe" | "she"
N -> "smile" | "thursday" | "walk" | "we" | "word"
P -> "at" | "before" | "in" | "of" | "on" | "to"
V -> "arrived" | "came" | "chuckled" | "had" | "lit" | "said" | "sat"
V -> "smiled" | "tell" | "were"
"""

NONTERMINALS = """
S -> SS | SS Conj SS | SS P SS
SS -> NP | VP | NP VP
NP -> NN | Det NN
VP -> VV | VV PP | VV NP | VV NP PP
VV -> V | Adv V | V Adv
NN -> N | AS N
AS -> Adj | Adj AS
PP -> P NP | P NP Adv
"""
# I had a little moist red paint in the palm of my hand.
# N V DET ADJ ADJ ADJ N P DET N P DET N
# I had a country walk on Thursday and came home in a dreadful mess.
# N V DET ADJ N P N CONJ V N P DET ADJ N
# Holmes sat in the red armchair and he chuckled.
grammar = nltk.CFG.fromstring(NONTERMINALS + TERMINALS)
parser = nltk.ChartParser(grammar)


def main():

    # If filename specified, read sentence from file
    if len(sys.argv) == 2:
        with open(sys.argv[1]) as f:
            s = f.read()

    # Otherwise, get sentence as input
    else:
        s = input("Sentence: ")

    # Convert input into list of words
    s = preprocess(s)

    # Attempt to parse sentence
    try:
        trees = list(parser.parse(s))
    except ValueError as e:
        print(e)
        return
    if not trees:
        print("Could not parse sentence.")
        return

    # Print each tree with noun phrase chunks
    for tree in trees:
        tree.pretty_print()

        print("Noun Phrase Chunks")
        for np in np_chunk(tree):
            print(" ".join(np.flatten()))


def preprocess(sentence):
    """
    Convert `sentence` to a list of its words.
    Pre-process sentence by converting all characters to lowercase
    and removing any word that does not contain at least one alphabetic
    character.
    """
    f = [ word for word in nltk.word_tokenize(sentence.lower())]
    b = []
    for c in f:
        if c.isalpha():
            b.append(c)

    return b

    



def np_chunk(tree):
    """
    Return a list of all noun phrase chunks in the sentence tree.
    A noun phrase chunk is defined as any subtree of the sentence
    whose label is "NP" that does not itself contain any other
    noun phrases as subtrees.
    """
    t = [ subtree for subtree in tree.subtrees()]
    b = []
    for c in t:
        if c.label() =='NP':
            b.append(c)
    return b


if __name__ == "__main__":
    main()
