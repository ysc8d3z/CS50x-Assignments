import cs50
import sys
import csv


def main():
    # Error message
    if len(sys.argv) != 3:
        print("Usage: python dna.py data.csv sequence.txt")
        sys.exit()

    # Open the CSV file and read contents into memory
    csvFile = sys.argv[1]
    with open(csvFile) as databaseFile:
        databaseReader = csv.reader(databaseFile)
        allSequences = next(databaseReader)[1:] # Save sequences in the header for comparison

    # Open the DNA sequence and read contents into memory
        txtFile = sys.argv[2]
        with open(txtFile) as sequenceFile:
            sequenceReader = sequenceFile.read()
            maxReps = [get_longest_run(sequenceReader, seq) for seq in allSequences]  # List Comprehension // Find max values of each sequence
            # ^for seq in header:
            #      maxReps.append(seq)
        print_match(databaseReader, maxReps) # Compare values


# For each STR, compute the longest run of consecutive repeats in the DNA sequence
def get_longest_run(s, sub):
    repCount = [0] * len(s)
    # Iterates through list of DNA checking if there is a full STR
    for i in range(len(s) - len(sub), -1, -1):  # for(int i = strlen(s) - strlen(sub); i > -1; i--) <- in C
        if s[i: i + len(sub)] == sub:
            if i + len(sub) > len(s) - 1:
                repCount[i] = 1
            else:
                repCount[i] = 1 + repCount[i + len(sub)]
    return max(repCount)


# Compare the STR counts against each row in the CSV file
def print_match(databaseReader, maxReps):
    for line in databaseReader:
        person = line[0]
        STRValues = [int(value) for value in line[1:]]
        if STRValues == maxReps:
            print(person)
            return
    print("No match")


if __name__ == "__main__":
    main()