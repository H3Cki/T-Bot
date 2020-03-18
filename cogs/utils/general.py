

def splitList(lst,size):
    output = []

    while lst:
        if len(lst) <= size:
            output.append(lst)
            lst = None
        else:
            output.append(lst[:size])
            lst = lst[size:]
            
    return output


# l = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20]
# s = 3
# print('\n')
# print(f'Dividing list into chunk with size {s}')
# print(l)
# print(splitList(l,s))
# print('\n')