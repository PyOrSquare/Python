# Your client has sent you a long list of names for use in your performance test scripts, the test engineer started writing a script
# to validate the format of the names but had to leave and has asked you to finish it.
# Your task is to complete the validate_name function to complete the script.



def validate_name(name):
    '''
    Returns True if the name is valid, False if not based off the following rules
    - the name has a max character length of 20
    - the name consists of only alpha characters (ie a-zA-Z) and space characters
    '''
    result = 1

    if (len(name.strip()) > 20):
        result = 0
    else:
        for ch in name:
            n = ord(ch)
            if ch.isalpha() or ch.isspace():
                print('%s ****** n=%d   and Len=%d' % (name, n, len(name)))
                result = 1
                continue
            else:
                result = 0
                print('%s ****** n=%d   and Len=%d'% (name,n,len(name)))
                break
    return result


# Extension exercises
# - Complete the validate_name2 function
# - Save the list of valid names to a file

def validate_name2(name):
    '''
     Appends the results to the name file based on the Rule
         if the name is valid, False if not based off the following rules
    - the name has a max character length of 20
    - the name consists of only alpha characters (ie a-zA-Z) and space characters
    '''
    result = 1

    if (len(name.strip()) > 20):
        result = 0
    else:
        for ch in name:
            #n = ord(ch)
            if ch.isalpha() or ch.isspace():
                result = 1
                continue
            else:
                result = 0
                #print('%s ****** n=%d   and Len=%d'% (name,n,len(name)))
                break
    if (result==1):
        vf = open('valid_names.txt', 'a')
        vf.write(name.rstrip())
        #print name.rstrip()
        vf.close()
    else:
        ef = open('invalid_names.txt', 'a')
        ef.write(name.rstrip())
        ef.close()
        #print ('Invalid %s' %name.rstrip())
    return result


def main():
    with open('names.txt') as f:
        lines = f.readlines()
    f.closed

    valid_names = []
    invalid_names = []

    for line in lines:
        name = line
        valid = validate_name2(name)
        #print (valid)
        if valid == 1:
            valid_names.append(name)
        else:
            invalid_names.append(name)

    print("Total count of records imported: " + str((len(valid_names) + len(invalid_names))))
    print("Count of imported records that meet the selected criteria: " + str(len(valid_names)))
    print("list of invalid names")
    print("---------------------")

    for name in invalid_names:
        print(name.rstrip())


if __name__ == "__main__":
    main()
