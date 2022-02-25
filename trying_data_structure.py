import numpy as np

n1 = [[[1, 0], [0, 1], [0, 0]], [[0, 0], [0, 0], [0, 0]],
      [[0, 0], [0, 0], [0, 0]], [[1, 0], [0, 0], [0, 0]],
      [[0, 0], [0, 0], [1, 0]]]

n2 = [[[1, 0], [0, 0], [0, 0]], [[0, 0], [0, 0], [0, 0]],
      [[1, 0], [0, 0], [0, 0]], [[0, 0], [0, 0], [1, 0]],
      [[0, 0], [0, 1], [0, 0]]]

dec_var = np.array([n1, n2])

print(dec_var[:, :, :, :1])
print(dec_var.shape)
print(np.sum(dec_var[0, :, :, :], axis=(2)).all() > 1)

aux_shift= np.sum(dec_var, axis=3)
aux_day = np.sum(aux_shift, axis=2)
aux_weekend = aux_day
print(dec_var)
print(aux_shift)
print(aux_day)
print(aux_day.any() > 0)
sum([False, True, False])