# Orbital Simulation Practical Project
# Rohit Prasad
# 2016-2017
# Last changed on 25/03/2016

# == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == ==
# MERGESORT
# == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == ==

def mergeSort(data):
    original = len(data)
    if len(data) > 1:
        middle = len(data) // 2
        right = data[middle:]
        left = data[:middle]

        mergeSort(left)
        mergeSort(right)

        x, y, z = 0, 0, 0
        while x < len(left) and y < len(right):
            if left[x] < right[y]:
                data[z] = left[x]
                x = x + 1
            else:
                data[z] = right[y]
                y = y + 1
            z = z + 1

        while x < len(left):
            data[z] = left[x]
            x = x + 1
            z = z + 1

        while y < len(right):
            data[z] = right[y]
            y = y + 1
            z = z + 1

        if len(data) == original:
            return data

# == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == ==
# TEXT COLOUR CHANGE
# == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == ==
def changeTextColour(text, colour):
    new_text = "<span style=\" color:{};\" >".format(colour)
    new_text += text
    new_text += "</span>"
    return new_text