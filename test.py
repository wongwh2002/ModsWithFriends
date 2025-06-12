from pprint import pprint

testDict = {"first": [1, 2, 3, 4, 5]}

refArr = testDict["first"][:]

pprint(refArr)
pprint(testDict)

refArr[0] = 0
pprint(refArr)
pprint(testDict)


def test(testDict):
    testDict["first"][0] = 5
    pprint(testDict)


test(testDict)
pprint(testDict)
