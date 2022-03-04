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

def check_swap(solution, info):
      # for both nurses check this
      # check whether the shift doesn't have a shift on that day h1
      # don't need to check coverage level as the coverage stays the same
      # check the shifts on the day before for forbidden successions
            # for some shifts we may not have to check, if not in successions
      # check whether each nurse has the right skill

      return None

def swap_assignments_operator(solution, nurse_1, nurse_2, shift_1, shift_2):
      """
      Function to change the nurses of two shifts after we have checked whether
      the shift is allowed
      :param solution:
      :param nurse_1:
      :param nurse_2:
      :return:
      """
      # swap nurse 1 from shift 1 to shift 2
      solution[nurse_1, shift_1[0], shift_1[1], shift_1[2]] = 0
      solution[nurse_1, shift_2[0], shift_2[1], shift_2[2]] = 1

      # swap nurse 2 from shift 2 to shift 1
      solution[nurse_2, shift_1[0], shift_1[1], shift_1[2]] = 1
      solution[nurse_2, shift_2[0], shift_2[1], shift_2[2]] = 0

      return solution

def assign_employee_operator(solution)

def check_employee_shift_skill_assignment(solution, employee, day, shift, skill):
      """
      Function to check whether nures
      :return:
      0 for unassigned
      1 for assigned
      """
      return dec_var[employee, day, shift, skill]