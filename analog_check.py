# analog_check.py
#
# Created on: 02/24/2021
#     Author: Anyka
#      		  Phoebe Luo
import xlrd


# Get rid of unnecessary enters, tabs, or spaces at the beginning of text
def remove(text):
    while text[0] == "\n" or text[0] == "\t" or text[0] == " ":
        text = text.strip("\n")
        text = text.strip("\t")
        text = text.strip(" ")
    return text


# Get rid of unnecessary enters, tabs, or spaces at the beginning of text for a list
def removelist(textlist):
    index = 0
    for element in textlist:
        textlist[index] = remove(element)
        index = index + 1
    return textlist


# Get list_excel and list_text from files
def getlist(list1, list2):
    # 1. Get list1 from Excel
    data = xlrd.open_workbook(
        r"C:\Users\anyka\Desktop\luozixin\M9 - Python\Snowbird3_analog_digital_interface_V1.0.1.xls")
    table = data.sheet_by_name("summary")  # default sheet name "summary"

    for col in range(table.ncols):
        if table.cell_value(0, col) == "Analog Port Name":  # default column name "Analog Port Name" found
            break
    else:
        print("Error: \"Analog Port Name\" not found")  # end program if column name "Analog Port Name" not found
        exit(0)
    list1[:] = table.col_values(col, 1, table.nrows)  # update list with found column

    index1 = 0
    for element in list1:
        if element.find("<") >= 0:  # get rid of unnecessary bit width content
            list1[index1] = element[0:element.find("<")]
        index1 = index1 + 1
    # print("list_excel:\n", list1)

    # 2. Get list2 from Text
    with open(r"C:\Users\anyka\Desktop\luozixin\M9 - Python\SBD3_analog_top_V1", "rt") as file:
        content = file.read()
    if content.find("module") < 0:
        print("Error: \"module\" not found")
        exit(0)  # end program if keyword "module" not found
    string = content[content.find("(") + 1:content.find(");")]
    string = string.strip(" ")  # get rid of unnecessary space

    element_start = element_end = 0
    while element_end < len(string):
        if string[element_end] == ",":
            element_content = string[element_start:element_end]
            element_content = remove(element_content)  # get rid of unnecessary enters, tabs, or spaces
            list2.append(element_content)
            element_start = element_end + 1
        element_end = element_end + 1
    #  print("list_text:\n", list2)

    # 3. Return lists
    return list1
    return list2


# Compare list_excel and list_text from files
def comparelist(list1, list2):
    set1 = set(list1).difference(set(list2))
    set1 = sorted(list(set1))
    set2 = set(list2).difference(set(list1))
    set2 = sorted(list(set2))
    print("Analog port name found in Excel but not Verilog:")
    print(set1)
    print("")
    print("Analog port name found in Verilog but not Excel:")
    print(set2)


def getwidth(dict1, dict2):
    # 1. Get list1 from Excel and extract name and width into dict1
    list1 = []
    data = xlrd.open_workbook(
        r"C:\Users\anyka\Desktop\luozixin\M9 - Python\Snowbird3_analog_digital_interface_V1.0.1.xls")
    table = data.sheet_by_name("summary")  # default sheet name "summary"

    for col in range(table.ncols):
        if table.cell_value(0, col) == "Analog Port Name":  # default column name "Analog Port Name" found
            break
    else:
        print("Error: \"Analog Port Name\" not found")  # end program if column name "Analog Port Name" not found
        exit(0)
    list1[:] = table.col_values(col, 1, table.nrows)  # update list with found column

    for element in list1:
        if element.find("<") >= 0:  # input bit width into dict in the format 0:a
            key = element[0:element.find("<")]
            width = element[element.find("<") + 1:len(element) - 1]
            dict1[key] = width
        else:
            key = element
            dict1[key] = "1"  # input bit width 1
    # print(str(dict1))

    # 2. Get list2 from Text and extract name and width into dict2
    with open(r"C:\Users\anyka\Desktop\luozixin\M9 - Python\SBD3_analog_top_V1", "rt") as file:
        content = file.read()

    # end program if keywords "input", "inout", or "output" not found
    if content.find("input") < 0 and content.find("output") < 0 and content.find("inout") < 0:
        print("Error: \"input\", \"inout\", or \"output\" not found")
        exit(0)

    # get rid of unnecessary content before keywords "input", "inout", or "output"
    content = content[content.find(");") + 2:]
    content = content[:content.find("specify")]
    content = remove(content)
    # print(content)

    while content.find("input") >= 0 or content.find("output") >= 0 or content.find("inout") >= 0:
        # print("\n-------------------------------------\n")
        if content.find("input") == 0 or content.find("inout") == 0 or content.find("output") == 0:
            # print("***** step1 *****")
            content = content[content.find(" ") + 1:]
            content = remove(content)
            # print(content)
            if content[0] == "[":  # the case when bit width is not 1
                # print("***** step2 *****")
                width = content[content.find("[") + 1:content.find("]")]
                # print(width)
                content = content[content.find(" ") + 1:]
                key = content[0:content.find(";")]
                if key.find(",") < 0:  # the case when there is only one key
                    dict2[key] = width
                else:  # the case when there are multiple keys
                    key_list = key.split(",")
                    key_list = removelist(key_list)
                    # print("key_list is\n", key_list)
                    for element in key_list:
                        dict2[element] = width
            else:  # the case when bit width is 1
                # print("***** step2 *****")
                width = "1"
                key = content[0:content.find(";")]
                if key.find(",") < 0:  # the case when there is only one key
                    # print("----------------------im in there is only on key section------------------------")
                    dict2[key] = width
                else:  # the case when there are multiple keys
                    # print("----------------------im in there are multiple keys section------------------------")
                    key_list = key.split(",")
                    key_list = removelist(key_list)
                    # print("key_list is\n", key_list)
                    for element in key_list:
                        dict2[element] = width
        if content.find("\n") <= 0:
            break
        content = content[content.find(";") + 1:]
        content = remove(content)
    # print(dict2)

    # 3. Return sorted dictionaries
    dict1 = sorted(dict1.items())
    dict2 = sorted(dict2.items())

    return dict1
    return dict2


def comparewidth(dict1, dict2):
    dict_diff = {}
    dict1_key = dict1.keys()
    dict2_key = dict2.keys()
    for element1 in dict1_key:
        for element2 in dict2_key:
            if element1 == element2:
                if dict1[element1] != dict2[element2]:
                    dict_diff[element1] = " has bit width " + dict1[element1] + " in Excel and " + dict2[element2] + " in Verilog"
    print("Bit width comparison of Excel and Verilog:")
    dict_key = dict_diff.keys()
    for element3 in dict_key:
        print("Analog port name ", element3, dict_diff[element3])


print("-------------------- Compare Analog Port Name --------------------")
list_excel = []
list_text = []
getlist(list_excel, list_text)
comparelist(list_excel, list_text)

print("")
print("-------------------- Compare Bit Width --------------------")
dict_excel = {}
dict_text = {}
getwidth(dict_excel, dict_text)
comparewidth(dict_excel, dict_text)
