import pprint


def print_list_or_dict(to_be_printed):
    # function to nicely print a dictionary or a list
    if type(to_be_printed) == dict:
        pprint.pprint(to_be_printed, sort_dicts=False)
    elif type(to_be_printed) == list:
        for element in range(len(to_be_printed)):
            print(str(element + 1) + ': ' + str(to_be_printed[element]))
    print('==========================================')