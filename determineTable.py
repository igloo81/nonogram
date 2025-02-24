import math
import unittest



def determineIndex(coordinate, start, slope):
    return round((coordinate - start) / slope)

'''
Returns the optimal A, alpha, B and beta
foundDigits should be of the form [((x,y), digit), ..]
'''
def findParameters(foundDigits):
    (rowStartValues, columnStartValues) = getStartParameters(foundDigits)
    
    # fixate columns and rows separately, this must be 100% correct...

    (a, alpha) = rowStartValues[1]
    (b, beta) = columnStartValues[1]
    return (a, alpha, b, beta)

# Get decent start candidates for a, alpha, b and beta. The values for alpha and beta can be too small.
# A and B might not start at 0 either
def getStartParameters(foundDigits):
    centers = [center for center,_ in foundDigits]
    xs = set([int(center[0]) for center in centers])
    ys = set([int(center[1]) for center in centers])
    alphas = set([x2 - x1 for x1 in xs for x2 in xs if x2- x1 > 0 and x2-x1 > 5])
    betas = set([y2 - y1 for y1 in ys for y2 in ys if y2 - y1 > 0 and y2-y1 > 5])   # make sure we don't take a value that is too low todo

    bCandidate = min(ys)
    betaCandidate = sum(betas)/len(betas)

    rowStartValues = sorted(
        [
            (computeCosts(foundDigits, a, alpha, bCandidate, betaCandidate), (a, alpha))
            for a in xs for alpha in alphas
        ],
        key= lambda tuple: tuple[0]
        )
    (a, alpha) = rowStartValues[0][1]

    columnStartValues = sorted(
        [
            (computeCosts(foundDigits, a, alpha, b, beta), (b, beta))
            for b in ys for beta in betas
        ],
        key= lambda tuple: tuple[0]
        )
        
    return rowStartValues, columnStartValues


def computeCosts(foundDigits, A, alpha, B, beta):
    costs = 0
    for (center, value) in foundDigits:
        predictionX  = round((center[0] - A) / alpha)
        predictionY = round((center[1] - B) / beta)
        costsX = (predictionX * alpha + A - center[0]) ** 2
        costsY = (predictionY * beta + B - center[1]) ** 2

        exponent = (math.exp(-costsX) + math.exp(-costsY))
        costs += 1/exponent
        costs += costsX
    return costs

def computeSkippedLines(coordinates, start, slope):
    indices = set([determineIndex(coordinate, start, slope) for coordinate in coordinates])
    lowest = min(indices)
    highest = max(indices)
    skipped = any(index not in indices for index in range(lowest, highest + 1))
    
    if (lowest != 0):
        return True
    else:
        return skipped

class TestComputations(unittest.TestCase):
    def test_compute(self):
        foundDigits = [((49.0, 148.0), 1),
            ((30.0, 148.0), 1),
            ((48.5, 128.0), 3),
            ((49.0, 108.0), 1),
            ((48.5, 88.0), 3),
            ((47.5, 67.5), 5),
            ((49.0, 68.0), 1),
            ((91.5, 45.5), 5),
            ((153.0, 46.0), 1),
            ((132.5, 46.0), 2),
            ((113.0, 46.0), 1),
            ((92.5, 46.0), 4),
            ((72.5, 46.0), 2),
            ((153.0, 27.0), 1),
            ((112.5, 27.0), 2)]
        
        actual = findParameters(foundDigits)
        self.assertEqual(actual, (70, 21, 67, 20))
        

        print(33)

if __name__ == "__main__":
    unittest.main()
