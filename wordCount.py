import sys        # command line arguments
import re         # regular expression tools

if len(sys.argv) is not 3:
    print("Correct usage: wordCount.py <input text file> <output file>")
    exit()

inputF = sys.argv[1]
outputF = sys.argv[2]
wordList = []
count = []
index = 0

with open(inputF, 'r') as txtF:
    for line in txtF:
        words = filter(None, re.split("[.,!?:;\- \n\"]+", line))
        print words
        for item in words:
            if item.lower() not in wordList:
                wordList.append(item.lower())
                count.append(0)
    wordList.sort()
    txtF.close()
print wordList

for item in wordList:
    with open(inputF, 'r') as txtF:
        for line in txtF:
            words = filter(None, re.split("[.,!?:;\- \n\"]+", line))
            for i in words:
                if i.lower() == item:
                    count[index] += 1
        txtF.close()
    index += 1
print count
index = 0

output = open(outputF, "w")
for item in wordList:
    output.write(item + " " + str(count[index]) + "\n")
    index += 1
output.close()
