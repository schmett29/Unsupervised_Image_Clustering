import os
import sys
from Image import Image

def readImages(queryPath):
    files = os.listdir(queryPath)
    return_array = []
    for file in files:
        print queryPath + file
        img = Image(queryPath+"/"+file)
        return_array.append(img)
    return return_array

def main(argv):
    queryPath = argv[1]
    queryImages = readImages(queryPath)
    print queryImages

if __name__ == '__main__':
    main(sys.argv)


