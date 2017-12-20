import csv

SurveyFile = 'Survey.csv'
TransposeFile = 'TransposeFile.csv'

f = open(SurveyFile, "r")
try:
    r = 1
    reader = csv.reader(f)
    for row in reader:
        if r == 1:
            header = row
        if r == 2:
            subheader = row
        r = r + 1
        if (r > 2):
            break

    # print header

    csv = open(TransposeFile, "w")
    csv.write('id, header, subheader, value\n')

    for row in reader:
        r = 0
        for column in row:
            if (r > 1):
                transrow = id + ',' + header[r] + ',' + subheader[r] + ',' + column + '\n'
                csv.write(transrow)
                print('%s,%s,%s,%s' % (id, header[r], subheader[r], column))
            elif r == 0:
                id = column
            r = r + 1

finally:
    f.close()
