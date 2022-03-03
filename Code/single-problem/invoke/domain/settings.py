from config import configuration

DEFAULTS = configuration.domain.settings.defaults


class Settings:

    def __init__(self, settings_spec):
        """
        Get all settings from settings spec file.
        If not in there, it takes default values
        """
        self.start = settings_spec["start"]
        self.end = settings_spec["end"]
        self.time_zone = settings_spec.get("time_zone", DEFAULTS.time_zone)
        self.cost_objective = settings_spec.get("cost_objective", DEFAULTS.cost_objective)
        self.rule_objective = settings_spec.get("rule_objective", DEFAULTS.rule_objective)
        self.fairness_objective = settings_spec.get("fairness_objective", DEFAULTS.fairness_objective)
        self.skill_objective = settings_spec.get("skill_objective", DEFAULTS.skill_objective)
        self.proficiency_objective = settings_spec.get("proficiency_objective", DEFAULTS.proficiency_objective)
        self.use_proficiency_per_hour = settings_spec.get("use_proficiency_per_hour", DEFAULTS.use_proficiency_per_hour)
        self.use_travel_expenses = settings_spec.get("use_travel_expenses", DEFAULTS.use_travel_expenses)
        self.split_skills = settings_spec.get("split_skills", DEFAULTS.split_skills)
        self.reduce_contract_hours_factor = settings_spec.get("reduce_contract_hours_factor",
                                                              DEFAULTS.reduce_contract_hours_factor)
        self.disallow_employee_mix = settings_spec.get("disallow_employee_mix", DEFAULTS.disallow_employee_mix)
        self.add_subshifts_to_output = settings_spec.get("add_subshifts_to_output", DEFAULTS.add_subshifts_to_output)

        # settings for all heuristics
        self.runtime = settings_spec.get("runtime", DEFAULTS.runtime)
        self.mip_gap = settings_spec.get("mip_gap")
        self.max_solutions = settings_spec.get("max_solutions")
        self.max_nodes = settings_spec.get("max_nodes")
        self.max_mip_gap_abs = settings_spec.get("max_mip_gap_abs")
        self.lp_method = settings_spec.get("lp_method")
        self.emphasis = settings_spec.get("emphasis")
        self.logging = settings_spec.get("logging", DEFAULTS.logging)
        self.seed = settings_spec.get("seed", DEFAULTS.seed)
        self.linear_relaxation = settings_spec.get("linear_relaxation", DEFAULTS.linear_relaxation)
        self.preprocess = settings_spec.get("preprocess", DEFAULTS.preprocess)
        self.pump_passes = settings_spec.get("pump_passes")
        self.search_progress_log_size = settings_spec.get("search_progress_log_size", DEFAULTS.search_progress_log_size)

        # Settings for the Shifting Window Heuristic
        self.run_shifting_window = settings_spec.get("run_shifting_window", DEFAULTS.run_shifting_window)
        shifting_window_settings = settings_spec.get("shifting_window_settings", settings_spec)
        self.shifting_window_day_size = shifting_window_settings.get("shifting_window_day_size",
                                                                     DEFAULTS.shifting_window_day_size)
        self.fix_window_day_size = shifting_window_settings.get("fix_window_day_size", DEFAULTS.fix_window_day_size)
        self.include_shifts_days = shifting_window_settings.get("include_shifts_days", DEFAULTS.include_shifts_days)
        self.fix_drop_ratio = shifting_window_settings.get("fix_drop_ratio", DEFAULTS.fix_drop_ratio)
        self.return_shifting_window_results = shifting_window_settings.get('return_shifting_window_results',
                                                                           DEFAULTS.return_shifting_window_results)

        # Settings for the Improvement Heuristic
        self.improve_results = settings_spec.get("improve_results", DEFAULTS.improve_results)
        k_opt_settings = settings_spec.get("improvement_heuristic_settings", settings_spec)
        self.improve_time_limit = k_opt_settings.get("improve_time_limit", DEFAULTS.improve_time_limit)
        self.acceptance_gap_improvement = k_opt_settings.get("acceptance_gap_improvement",
                                                             DEFAULTS.acceptance_gap_improvement)
        self.batch_size = k_opt_settings.get("batch_size")
        self.number_of_unassigned_shifts = k_opt_settings.get("number_of_unassigned_shifts",
                                                              DEFAULTS.number_of_unassigned_shifts)

        self.run_combined_heuristic = self.run_shifting_window and self.improve_results
