# tuple_1 = (('200', '201'), ('476', '290'))
# tuple_2 = (('23', '54'), ('120', '100'))

# tabu = set()

# tabu.add(tuple_1)
# tabu.add(tuple_2)

# for i,value in enumerate(tabu):
#     print(i, value)
#     if i == 0:
#         to_delete = value
# tabu.discard(to_delete)

# tuple_3 = (('129','13'),('523','124'))

# if tuple_3 in tabu:
#     print('yupi')
#----------------------------------------------------------------
new_list = [1,2,3,4]
comp_list = [3,4,1,2]
#make a swap 
node = new_list[0]
new_list.pop(0)
new_list.append(node)

import numpy as np
np.random.seed()
#print(np.squeeze(np.random.normal(30,8,1)))

a = np.arange(6)
a2 = a[np.newaxis, :]
print(a)
print(a.shape)
print(a2)
print(a2.shape)
print(np.empty(4))

print(a2.reshape(3,2))