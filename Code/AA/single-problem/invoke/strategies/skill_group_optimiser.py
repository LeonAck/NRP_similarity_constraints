from strategies.optimiser import Optimiser

class SkillGroupOptimiser(object):
    def __init__(self, domain):
        self.domain = domain

    def find_solution(self):
        result = None
        for skillGroup in self.domain.employees.get_non_overlapping_skill_groups():
            if skillGroup != [999]:
                # set the right shifts and employees for the optimiser
                skill_group_employees = self.domain.employees.get_employees_skill_group(skillGroup)
                skill_group_shifts = self.domain.shifts.get_shifts_skill_group(skillGroup, max_size=500)
                print(
                    "currently optimising",
                    skillGroup,
                    "with",
                    len(skill_group_employees),
                    "employees and",
                    len(skill_group_shifts),
                    "shifts",
                )
                optimiser = Optimiser(
                    self.domain,
                    skill_group_employees,
                    skill_group_shifts
                )
                partial_result = optimiser.find_solution()
                if not result:
                    result = partial_result
                else:
                    result["shifts"] = result["shifts"] + partial_result["shifts"]
                    result["rule_violations"] = (
                            result["rule_violations"] + partial_result["rule_violations"]
                    )

        # optimiser.create_and_send_kpis(self.domain, result)
        return result
