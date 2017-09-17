##USAGE: should only be executed by Makefile, e.g. "make lev_matrix"

from GameUtils.PronunciationUtils.PronunciationUtils import PronunciationUtils
from GameUtils.Curriculum import Curriculum

import pandas as pd
import os
import numpy as np
from weighted_levenshtein.clev import levenshtein as lev


WPSM_PATH = '/GameUtils/PronunciationUtils/data/wpsm.csv'
myUtils = PronunciationUtils()
myCurriculum = [p for p in dir(Curriculum)
                       if isinstance(getattr(Curriculum, p), str)
                       and not p.startswith('__')]


def create_substitution_matrix():

    # read weighted phonemic similarity matrix,
    # downloaded from https://github.com/benhixon/benhixon.github.com/blob/master/wpsm.txt

    # load the matrix csv file into a dataframe
    df = pd.read_csv(os.getcwd() + WPSM_PATH, sep=',', header=0, index_col=0)

    arpabet_phonemes = df.keys()
    print(arpabet_phonemes)
    print(len(arpabet_phonemes))

    substitute_costs = np.ones((128, 128), #128 is size of ASCII table we care about
                               dtype=np.float64)  # make a 2D array of 1's. ASCII table
    # update the original substitution matrix
    lowest = 100
    lowkey1 = None
    lowkey2 = None

    highest = -100
    lowkey1 = None
    lowkey2 = None

    # calculate min/max values of non-diagonal wpsm scores
    for key1 in arpabet_phonemes:
        for key2 in arpabet_phonemes:
            if not key1 == key2:
                if (-1 * df[key1][key2]) < lowest:
                    lowkey1 = key1
                    lowkey2 = key2
                    lowest = -1 * df[key1][key2]  # "P/B"

                if (-1 * df[key1][key2]) > highest:
                    highkey1 = key1
                    highkey2 = key2
                    highest = -1 * df[key1][key2]

    print("lowest score was ")
    print(lowest)
    print(df[lowkey1][lowkey2])

    print("highest score was ")
    print(highest)
    print(df[highkey1][highkey2])

    range = highest - lowest
    print(normalize_wpsm_cost(highest, highest, lowest))
    print(normalize_wpsm_cost(lowest, highest, lowest))

    for key1 in arpabet_phonemes:
        for key2 in arpabet_phonemes:
            nkey1 = myUtils.arpabet_map[key1]
            nkey2 = myUtils.arpabet_map[key2]

            if (nkey1 == nkey2):
                substitute_costs[ord(nkey1), ord(
                    nkey2)] = 0.0  # use zero substitution cost for diagonal entries
            else:
                raw_cost = -1 * df[key1][key2]
                substitute_costs[ord(nkey1), ord(nkey2)] = normalize_wpsm_cost(raw_cost,
                                                                                    highest,
                                                                                    lowest)

    np.save(os.getcwd() + PronunciationUtils.PHONEME_SUB_COST_PATH, substitute_costs)
    np.savetxt(os.getcwd() + PronunciationUtils.PHONEME_SUB_COST_PATH + '.txt', substitute_costs)

def create_levenshtein_cost_matrix():
    weighted_levenshtein_distances = np.ones((len(myCurriculum), len(myCurriculum)),
                               dtype=np.float64)  # make a 2D array of 1's. ASCII table

    for i in range(0, len(myCurriculum)):
        for j in range(0, len(myCurriculum)):
            #yeah I know we're calculating it twice - TODO: Optimize
            weighted_levenshtein_distances[i][j] = measure_weighted_levenshtein_distance(
                myCurriculum[i], myCurriculum[j])


    np.save(os.getcwd() + PronunciationUtils.WEIGHTED_LEV_DISTANCE_PATH, weighted_levenshtein_distances)
    np.savetxt(os.getcwd() + PronunciationUtils.WEIGHTED_LEV_DISTANCE_PATH + '.txt', weighted_levenshtein_distances)


def measure_weighted_levenshtein_distance(word1, word2):
    # import weighted levenshtein library. if clev is missing, change the __init__.py in the weighted_levenshtein lib to add clev.so path to sys.
    # /anaconda3/lib/python3.6/site-packages/weighted_levenshtein
    # delete "from clev import *" in __init__.py

    # read the phoneme substitution costs from disk
    loaded_substitute_costs = np.load(os.getcwd() + myUtils.PHONEME_SUB_COST_PATH + '.npy')
    result = lev(myUtils.get_phonetic_similarity_rep(word1).encode(),
                 myUtils.get_phonetic_similarity_rep(word2).encode(),
                 substitute_costs=loaded_substitute_costs)

    # normalize the levenshtein score by taking max(str1,str2)
    denominator = max(len(word1), len(word2))
    normalized_score = (result / float(denominator))
    print("weighted-lev distance between " + word1 + " and " + word2 + " was " + str(normalized_score))
    return normalized_score

def normalize_wpsm_cost(raw_cost, highest, lowest):
    """
    converts a raw_cost into the range (0,1), given the highest and lowest wpsm costs
    See: https://stackoverflow.com/questions/5294955/how-to-scale-down-a-range-of-numbers-with-a-known-min-and-max-value
    """
    # print(raw_cost)
    # print("TURNED INTO")
    scaled_cost = ((1 - 0) * (raw_cost - lowest) / (highest - lowest))
    # print(str(scaled_cost) + '\n')
    return scaled_cost



create_substitution_matrix()
create_levenshtein_cost_matrix()