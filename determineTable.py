import math
import unittest

'''

- de wikipedia sample gaat goed!
- sample gaat goed!
- sample3 gaat goed
- sample5 faalt op herkennen van enen. Door het rescalen oid worden de enen hol van binnen

- sample4 faalt door bepaling grid
- andere langt niet altijd
    issues door verwijderen lijnen met thresholds
    het herkennen van drieen gaat ook soms fout omdat
    herkennen van digits met twee cijfers is iffy, doordat extract_digit_image_from_contour een vierkante slice pakt (ipv met nullen te beginnen en dan het rechthoekige stukje er in te frotten)
    digit grid herkennen gaat fout in sample4 doordat y een andere step heeft en omdat het nogal precies komt (misschien werken met min & max)!

- POC (python)
- Unit tested (kotlin?)
- Whole lot of things through it
- double digit numbers
'''

class NonogramContour:
    def __init__(self, contour, bounding_rect, digit, digit_image, digit_image_resized):
        self.contour = contour
        self.bounding_rect = bounding_rect
        self.digit = digit
        self.digit_image = digit_image
        self.digit_image_resized = digit_image_resized


def compute_grid_parameters(contours):
    # First on the rows
    centers = [(contour.bounding_rect[0] + contour.bounding_rect[2]/2, contour.bounding_rect[1] + contour.bounding_rect[3]/2) for contour in contours]
    ((A, alpha), column_costs) = compute_axis_parameters(set([int(center[0]) for center in centers]))
    ((B, beta), row_costs) = compute_axis_parameters(set([int(center[1]) for center in centers]))
    return (A, alpha, B, beta)

def compute_axis_parameters(values):
    min_grid_size = 10
    max_grid_size = 100
    options = [((grid_offset, grid_size), compute_costs(values, grid_offset, grid_size)) for grid_size in range(min_grid_size, max_grid_size) for grid_offset in range(0, grid_size)]
    optimum = sorted(options, key=lambda tuple: -tuple[1])[0]
    return optimum


def compute_costs(values, offset, size):
    costs = 0
    for value in values:
        index = determineIndex(value, offset, size)
        difference = (offset + index * size) - value
        costs += math.exp(-abs(difference / size))
    return costs

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

        #if (predictionX - alpha/2 < box[0] and predictionX + alpha/2 > box[0] + box[2]):    # todo, both must hold!
        #    costs += math.exp(-abs(predictionX - center[0]))
        #if (predictionY - beta/2 < box[1] and predictionY + beta/2 > box[1] + box[3]):
        #    costs += math.exp(-abs(predictionY - center[1]))
        if (
            predictionX - alpha/2 < box[0] and predictionX + alpha/2 > box[0] + box[2] and 
            predictionY - beta/2 < box[1] and predictionY + beta/2 > box[1] + box[3]
            ):    # todo, both must hold!
            costs += math.exp(-abs(predictionX - center[0]) / alpha * 2)
            costs += math.exp(-abs(predictionY - center[1]) / beta * 2)
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
    numbersInGrid = combineDigits(digitsInGrid)
    (lefties, toppies, sumLeftMinusTop) = distributeDigitsOverLeftAndTop(numbersInGrid)
    return (lefties, toppies, sumLeftMinusTop)


# putDigitsInGrid = [(x,y,digit)]
def putDigitsInGrid(foundDigits, A, alpha, B, beta):
    digitsInGrid = {}
    for contour in foundDigits:
        center = (contour.bounding_rect[0] + contour.bounding_rect[2]/2, contour.bounding_rect[1] + contour.bounding_rect[3]/2)
        indexX = round((center[0] - A) / alpha)
        indexY = round((center[1] - B) / beta)
        predictionX = indexX * alpha + A
        predictionY = indexY * beta + B
        if (
            predictionX - alpha/2 <= contour.bounding_rect[0] and predictionX + alpha/2 >= contour.bounding_rect[0] + contour.bounding_rect[2] and
            predictionY - beta/2 <= contour.bounding_rect[1] and predictionY + beta/2 >= contour.bounding_rect[1] + contour.bounding_rect[3]
            ):
            digitsInGrid.setdefault((indexX, indexY), []).append((contour))
    return digitsInGrid
    
def combineDigits(digitsInGrid):
    result = []
    for ((indexX, indexY), contours) in digitsInGrid.items():
        number = 0
        for contour in sorted(contours, key=lambda contour: contour.bounding_rect[0]):
            number = number * 10 + contour.digit
        result.append(((indexX, indexY), number))
    return result


def distributeDigitsOverLeftAndTop(digitsInGrid):
    lefties = []
    toppies = []

    sumLeftMinusTop = 0
    while (len(digitsInGrid) > 0):
        if (sumLeftMinusTop < 0):
            candidateIndex = sorted([index for index in range(0, len(digitsInGrid))], key=lambda index: digitsInGrid[index][0][0])[0]
            candidate = digitsInGrid[candidateIndex]
            sumLeftMinusTop += candidate[1]
            lefties.append(candidate)
            digitsInGrid.pop(candidateIndex)
        else:
            candidateIndex = sorted([index for index in range(0, len(digitsInGrid))], key=lambda index: digitsInGrid[index][0][1])[0]
            candidate = digitsInGrid[candidateIndex]
            sumLeftMinusTop -= candidate[1]
            toppies.append(candidate)
            digitsInGrid.pop(candidateIndex)
    return (lefties, toppies, sumLeftMinusTop)



class TestComputations(unittest.TestCase):
    def test_compute(self):
        foundDigits = [((46, 143, 6, 10), 1), ((27, 143, 6, 10), 1), ((45, 123, 7, 10), 3), ((46, 103, 6, 10), 1), ((45, 83, 7, 10), 3), ((45, 63, 8, 10), 1), ((150, 41, 6, 10), 1), ((129, 41, 7, 10), 2), ((110, 41, 6, 10), 1), ((89, 41, 7, 10), 4), ((69, 41, 7, 10), 2), ((150, 22, 6, 10), 1), ((109, 22, 7, 10), 2)]
        foundDigits = [((190, 1256, 10, 31), 2), ((133, 1256, 11, 31), 2), ((187, 1199, 20, 32), 4), ((131, 1199, 20, 32), 4), ((187, 1142, 20, 33), 3), ((131, 1142, 20, 33), 3), ((188, 1086, 19, 32), 5), ((130, 1086, 23, 32), 4), ((188, 1030, 19, 32), 5), ((131, 1029, 21, 33), 5), ((187, 973, 21, 32), 2), ((131, 973, 20, 32), 4), ((74, 973, 21, 32), 2), ((18, 973, 20, 32), 4), ((130, 917, 23, 31), 4), ((17, 917, 23, 31), 4), ((187, 916, 21, 32), 2), ((74, 916, 21, 33), 3), ((190, 860, 10, 32), 2), ((131, 860, 20, 32), 4), ((74, 860, 21, 32), 2), ((18, 860, 20, 32), 4), ((187, 804, 21, 31), 2), ((131, 804, 21, 32), 5), ((74, 804, 21, 32), 3), ((187, 747, 21, 32), 2), ((130, 747, 23, 32), 4), ((73, 747, 23, 32), 4), ((187, 691, 21, 31), 2), ((130, 691, 23, 31), 4), ((74, 691, 21, 32), 3), ((187, 634, 21, 32), 2), ((131, 634, 20, 32), 3), ((73, 634, 23, 32), 4), ((190, 578, 10, 31), 2), ((132, 578, 19, 32), 5), ((74, 578, 21, 32), 3), ((132, 522, 19, 31), 5), ((187, 521, 21, 32), 2), ((73, 521, 23, 32), 4), ((187, 465, 21, 31), 2), ((131, 465, 20, 31), 2), ((73, 465, 23, 31), 4), ((18, 465, 20, 32), 5), ((187, 408, 21, 32), 2), ((131, 408, 20, 32), 2), ((74, 408, 21, 32), 4), ((18, 408, 20, 32), 2), ((187, 352, 21, 32), 2), ((131, 352, 20, 32), 2), ((74, 352, 21, 32), 4), ((17, 352, 23, 32), 4), ((187, 295, 20, 32), 2), ((131, 295, 20, 32), 2), ((74, 295, 21, 32), 2), ((18, 295, 20, 32), 2), ((187, 239, 20, 32), 4), ((131, 239, 20, 32), 4), ((73, 239, 23, 32), 4), ((19, 239, 19, 32), 5), ((187, 183, 21, 31), 1), ((132, 183, 19, 32), 5), ((74, 183, 21, 31), 1), ((18, 182, 20, 33), 7), ((1884, 126, 10, 32), 2), ((1827, 126, 11, 32), 2), ((1768, 126, 21, 32), 4), ((1713, 126, 19, 32), 5), ((1655, 126, 21, 32), 1), ((1600, 126, 19, 32), 5), ((1541, 126, 23, 32), 4), ((1487, 126, 19, 32), 5), ((1429, 126, 23, 32), 4), ((1372, 126, 23, 32), 4), ((1317, 126, 20, 32), 1), ((1260, 126, 21, 32), 7), ((1204, 126, 20, 32), 7), ((1147, 126, 21, 32), 4), ((1091, 126, 20, 32), 1), ((1050, 126, 10, 32), 2), ((1024, 126, 10, 32), 2), ((979, 126, 19, 32), 5), ((920, 126, 23, 32), 4), ((864, 126, 23, 32), 4), ((808, 126, 21, 32), 1), ((752, 126, 20, 32), 2), ((696, 126, 20, 32), 7), ((639, 126, 21, 32), 7), ((583, 126, 20, 32), 7), ((526, 126, 21, 32), 8), ((470, 126, 20, 32), 1), ((412, 126, 23, 32), 4), ((357, 126, 20, 32), 2), ((303, 126, 10, 32), 2), ((246, 126, 11, 32), 2), ((1601, 70, 11, 31), 2), ((1545, 70, 11, 31), 2), ((1432, 70, 11, 31), 2), ((1316, 70, 23, 31), 4), ((1203, 70, 23, 31), 4), ((1093, 70, 11, 31), 2), ((1037, 70, 10, 31), 2), ((754, 70, 11, 31), 2), ((641, 70, 11, 31), 2), ((1373, 69, 21, 32), 2), ((1261, 69, 20, 33), 5), ((978, 69, 20, 33), 7), ((922, 69, 20, 33), 5), ((865, 69, 20, 33), 3), ((809, 69, 20, 32), 2), ((583, 69, 20, 32), 2), ((1206, 13, 11, 32), 2)]

        actual = findParameters(foundDigits)
        (A, alpha, B, beta) = actual
        #         costs = [computeCosts(foundDigits, 70, 21, 67, 20),computeCosts(foundDigits, 70, 21, 67, 30)]
        print(computeCosts(foundDigits, 70, 21, 67, 20))
        print(computeCosts(foundDigits, 70, 21, 67, 40))
        print(computeCosts(foundDigits, 141, 56, 142, 113))
        print(computeCosts(foundDigits, A, alpha, B, beta))
        print(actual)

        expected = (70, 21, 67, 21)
        # todo !
        # self.assertEqual((alpha, beta), (expected[1], expected[3]))    # the size off the cells
        #self.assertEqual((A % alpha, B % beta), (expected[0] % expected[1], expected[2] % expected[3]))    # the offsets

        (lefties, toppies) = divideOverLeftAndTop(foundDigits, A, alpha, B, beta)

        
        
if __name__ == "__main__":
    unittest.main()
