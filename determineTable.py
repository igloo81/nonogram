import math
import unittest

'''
Het kan werken, maar het is niet al te interessant tbh
het voelt te gammel aan
Nodig:
- fixen preprocess
- use grid (improve maybe, remove beta parameter, the grid should be square)
- extract the digits

- POC (python)
- Unit tested (kotlin?)
- Whole lot of things through it
'''



def determineIndex(coordinate, start, slope):
    return round((coordinate - start) / slope)

'''
Returns the optimal A, alpha, B and beta
foundDigits should be of the form [((x,y), digit), ..]
'''
def findParameters(foundDigits):
    (rowStartValues, columnStartValues) = getStartParameters(foundDigits)
    
    # fixate columns and rows separately, this must be 100% correct...

    (a, alpha) = rowStartValues[0][1]
    (b, beta) = columnStartValues[0][1]
    return (a, alpha, b, beta)

# Get decent start candidates for a, alpha, b and beta. The values for alpha and beta can be too small.
# A and B might not start at 0 either
def getStartParameters(foundDigits):
    centers = [(box[0] + box[2]/2, box[1] + box[3]/2) for box,_ in foundDigits]
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
        key= lambda tuple: -tuple[0]
        )
    (a, alpha) = rowStartValues[0][1]

    columnStartValues = sorted(
        [
            (computeCosts(foundDigits, a, alpha, b, beta), (b, beta))
            for b in ys for beta in betas
        ],
        key= lambda tuple: -tuple[0]
        )
        
    return rowStartValues, columnStartValues


def computeCosts(foundDigits, A, alpha, B, beta):
    costs = 0
    for (box, _) in foundDigits:
        center = (box[0] + box[2]/2, box[1] + box[3]/2)
        predictionX = round((center[0] - A) / alpha) * alpha + A
        predictionY = round((center[1] - B) / beta) * beta + B

        if (predictionX - alpha/2 < box[0] and predictionX + alpha/2 > box[0] + box[2]):    # todo, both must hold!
            costs += math.exp(-abs(predictionX - center[0]))
        if (predictionY - beta/2 < box[1] and predictionY + beta/2 > box[1] + box[3]):
            costs += math.exp(-abs(predictionY - center[1]))
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
    
def divideOverLeftAndTop(foundDigits, A, alpha, B, beta):   # naming with distributeDigitsOverLeftAndTop
    digitsInGrid = putDigitsInGrid(foundDigits, A, alpha, B, beta)
    (lefties, toppies) = distributeDigitsOverLeftAndTop(digitsInGrid)
    return (lefties, toppies)


# putDigitsInGrid = [(x,y,digit)]
def putDigitsInGrid(foundDigits, A, alpha, B, beta):
    digitsInGrid = []
    for (box, digit) in foundDigits:
        center = (box[0] + box[2]/2, box[1] + box[3]/2)
        indexX = round((center[0] - A) / alpha)
        indexY = round((center[1] - B) / beta)
        predictionX = indexX * alpha + A
        predictionY = indexY * beta + B
        if (
            predictionX - alpha/2 < box[0] and predictionX + alpha/2 > box[0] + box[2] and
            predictionY - beta/2 < box[1] and predictionY + beta/2 > box[1] + box[3]
            ):
            digitsInGrid.append((indexX, indexY, digit))
    return digitsInGrid
    
def distributeDigitsOverLeftAndTop(digitsInGrid):
    lefties = []
    toppies = []

    sumLeftMinusTop = 0
    while (len(digitsInGrid) > 0):
        if (sumLeftMinusTop < 0):
            candidateIndex = sorted([index for index in range(0, len(digitsInGrid))], key=lambda index: digitsInGrid[index][0])[0]
            candidate = digitsInGrid[candidateIndex]
            sumLeftMinusTop += candidate[2]
            lefties.append(candidate)
            digitsInGrid.pop(candidateIndex)
        else:
            candidateIndex = sorted([index for index in range(0, len(digitsInGrid))], key=lambda index: digitsInGrid[index][1])[0]
            candidate = digitsInGrid[candidateIndex]
            sumLeftMinusTop -= candidate[2]
            toppies.append(candidate)
            digitsInGrid.pop(candidateIndex)
    return (lefties, toppies)



class TestComputations(unittest.TestCase):
    def test_compute(self):
        foundDigits = [((46, 143, 6, 10), 1), ((27, 143, 6, 10), 1), ((45, 123, 7, 10), 3), ((46, 103, 6, 10), 1), ((45, 83, 7, 10), 3), ((45, 63, 8, 10), 1), ((150, 41, 6, 10), 1), ((129, 41, 7, 10), 2), ((110, 41, 6, 10), 1), ((89, 41, 7, 10), 4), ((69, 41, 7, 10), 2), ((150, 22, 6, 10), 1), ((109, 22, 7, 10), 2)]
        
        actual = findParameters(foundDigits)
        (A, alpha, B, beta) = actual
        #         costs = [computeCosts(foundDigits, 70, 21, 67, 20),computeCosts(foundDigits, 70, 21, 67, 30)]
        print(computeCosts(foundDigits, 70, 21, 67, 20))
        print(computeCosts(foundDigits, 70, 21, 67, 40))
        print(computeCosts(foundDigits, A, alpha, B, beta))

        expected = (70, 21, 67, 21)
        # todo !
        # self.assertEqual((alpha, beta), (expected[1], expected[3]))    # the size off the cells
        #self.assertEqual((A % alpha, B % beta), (expected[0] % expected[1], expected[2] % expected[3]))    # the offsets

        (lefties, toppies) = divideOverLeftAndTop(foundDigits, A, alpha, B, beta)

        
        
if __name__ == "__main__":
    unittest.main()
