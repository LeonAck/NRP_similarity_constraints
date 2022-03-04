# Shift Fill

The shift fill algorithm takes as input a set of shifts and a set of employees, and returns a set of shifts assigned to employees as well as any rule violations. Any shifts that cannot be assigned are returned without an employee id. These shifts can be assigned manually through an overtime or bidding process.

The key benefits of this algorithm include:
* Ensure coverage of all required shifts
* Minimise overtime, premiums, and other scheduling costs
* Adhere to all relevant labor laws & rules as well as employee preferences
* Reduce manual scheduling effort by creating a very good schedule quickly

## Shift Fill Input


```json
{
    "title": "Shift Fill Input JSON",
    "type": "object",
    "properties": {
        "shifts":{
            "title":"existing shifts",
            "type": "array",
            "description": "list of existing shifts",
            "items": {
                "title": "Existing shift",
                "type": "object",
                "description": "Existing shift",
                "properties":{
                    "start": {
                        "type": "time in epoch",
                        "description": "start time of the shift"
                    },
                    "finish":{
                        "type": "time in epoch",
                        "description": "end time of the shift"
                    },
                    "department_id":{
                        "type": "string",
                        "description" : "the $roleId or department ID for this shift"
                    },
                    "id":{
                        "type": "string",
                        "description": "unique identifier of the shift"
                    },
                    "is_fixed":{
                      "type":"boolean",
                      "description": "indicate whether the shift can be freely assigned. If this field is true, we expect user_id to be filled"
                    },
                    "user_id":{
                      "type":"boolean",
                      "description": "this field is only filled when the is_fixed flag is set to true. The information is used for rule calculation"
                    },
                    "pay_duration":{
                      "type":"number",
                      "description": "pay duration in minutes. This duration is used for the various rules regarding maximum and minimum hours"
                    },
                    "break_duration":{
                      "type": "number",
                      "description":"Total duration of the breaks for this shift in minutes"
                    },
                    "subshifts":{
                      "type":"array",
                      "description":"list of subshifts / tasks within this shift",
                      "items":{
                        "type":"object",
                        "title":"Subshift / task within the shift",
                        "properties":{
                          "start":{
                            "type": "number",
                            "description":"start of the subshift in epoch time"
                          },
                          "finish":{
                            "type": "number",
                            "description": "finish of the subshift in epoch time"
                          },
                          "department_id":{
                            "type": "string",
                            "description": "Identifier of the department for this subshift"
                          }
                        }
                      }
                    },
                    "breaks":{
                      "type":"array",
                      "description" : "array of breaks within this shift",
                      "items":{
                        "type": "object",
                        "title": "Break within the subshift",
                        "properties":{
                          "start":{
                            "type":"number",
                            "description":"start of the break"
                          },
                          "finish":{
                            "type":"number",
                            "description": "finish of the break"
                          }
                        }
                      }
                    },
                    "licenses":{
                      "type":"array",
                      "description":"list of required licenses for this shift",
                      "items":{
                        "type": "object",
                        "title": "required license for this shift",
                        "properties":{
                          "id":{
                            "type":"string",
                            "description":"required license for this shift"
                          }
                        }
                      }
                    },
                    "skills":{
                      "type": "array",
                      "description":"required skills for this shift",
                      "items":{
                        "type":"object",
                        "title":"required skill for this shift",
                        "properties":{
                          "id":{
                            "type":"string",
                            "description":"required skill identifier"
                          },
                          "min_level":{
                            "type": "number",
                            "description": "required minimum level for this skill (proficiency)"
                          }
                        }
                      }
                    }
                }
            }
        },
        "users":{
            "type": "array",
            "title": "Employees who will be part of the scenario, we use this information to not overallocate shifts for a specific employee type",
            "items":{
                "type":"object",
                "description": "Individual employees",
                "properties":{
                    "id":{
                        "type": "number",
                        "title": "Unique ID of the employee"
                    },
                    "department_ids":{
                        "type": "array",
                        "title": "list of roles / department ids the employees is part of",
                        "items":{
                          "type": "object",
                          "description": "department or role the user is part of",
                          "properties":{
                            "id":{
                              "description": "identifier of the department id",
                              "type": "string"
                            },
                            "from":{
                              "description": "from what time (epoch) the user is part of this department / role",
                              "type": "number"
                            },
                            "proficiency_rating":{
                                "description": "rating this employee has for this department",
                                "type": "number"
                            }
                          }
                        }
                    },
                    "hourly_rate":{
                        "type": "number",
                        "title": "base hourly rate of the employee"
                    },
                    "payperiod_minutes_min":{
                        "type": "number",
                        "title": "minimum contract minutes for the pay period"
                    },
                    "payperiod_minutes_max": {
                        "type": "number",
                        "title": "maximum contract minutes for the pay period"
                    },
					"minimum_time_between_shifts": {
                        "type": "number",
                        "title": "minimum time between two sequential shifts in minutes. Is only used when parameters of corresponding rule (5) is not set"
                    },
                    "maximum_shift_duration": {
                        "type": "number",
                        "title": "Maximum shift length in minutes. Is only used when parameters of corresponding rule (10) is not set"
                    },
                    "payperiod_length_days":{
                      "type":"number",
                      "title":"pay period length in days"
                    },
                    "is_fixed":{
                        "type":"boolean",
                        "title":"indicator to indicate whether the employee can be adjusted / shifts can be assigned"
                    },
                    "start_contract":{
                      "type": "number",
                      "description":"start of the contract in epoch time"
                    },
                    "skills":{
                      "type":"array",
                      "description":"list of skills the user has",
                      "items":{
                        "type":"object",
                        "description": "skill object",
                        "properties":{
                          "id":{
                            "type":"string",
                            "description":"unique identifier of the skill the user has"
                          },
                          "level":{
                            "type":"number",
                            "description":"The proficiency level of the skill of the user"
                          }
                        }
                      }
                    },
                    "licenses":{
                      "type":"array",
                      "description":"list of licenses the user has",
                      "items":{
                        "type":"object",
                        "description": "license object",
                        "properties":{
                          "id":{
                            "type":"string",
                            "description":"unique identifier of the license the user has"
                          },
                          "from":{
                            "type":"number",
                            "description":"Date from which the license started (epoch time)"
                          },
                          "expires":{
                            "type":"number",
                            "description":"expiration date of the license"
                          }
                        }
                      }
                    },
                    "unavailabilities":{
                        "type": "array",
                        "title": "list of unavailabilities the employee has. Only full day unavailabilities for the specified period will be taken into consideration",
                        "items":{
                            "title":"Unavailability",
                            "type": "object",
                            "properties":{
                                "start": {
                                    "type": "time in epoch",
                                    "title": "start time of the unavailability in epoch"
                                },
                                "finish":{
                                   "type": "time in epoch",
                                   "title": "end time of the unavailability in epoch"
                                },
                                "pay_duration":{
                                  "type":"number",
                                  "title":"pay duration in minutes of this unavailability"
                                },
                                "type":{
                                  "type":"number",
                                  "description":"type of unavailability (whether it is paid or not)"
                                }
                            }
                        }
                    }

                }
            }
        },
        "departments":{
            "title": "list of departments which are relevant for the specific run",
            "type": "array",
            "items":{
                "type": "object",
                "title": "department object",
                "properties":{
                    "id":{
                        "type": "string",
                        "title": "unique id of the department"
                    },
                    "name":{
                        "type": "string",
                        "title": "name of the department"
                    },
                    "location_id":{
                        "type": "string",
                        "title": "Unique identifier of the location where the department belongs to"
                    },
                    "to_solve":{
                        "type": "boolean",
                        "title": "Whether this department should be considered for the creation of shifts"
                    },
                    "target_budget":{
                        "type": "number",
                        "title": "The target budget for the specified period for which shifts are created"
                    }
                }
            }
        },
        "shift_type_definitions": {
            "title": "list of shift type definitions which are relevant fo the specific run",
            "type": "array",
            "items":{
                "type": "object",
                "title": "shift type object",
                "properties":{
                    "id":{
                        "type": "number",
                        "title": "Unique id of the shift type"
                    },
                    "name":{
                        "type": "string",
                        "title": "Name of the shift type"
                    },
                    "start_after": {
                        "type": "number",
                        "title": "Minutes from midnight that shifts of this type start after"
                    },
                    "start_before": {
                        "type": "number",
                        "title": "Minutes from midnight that shifts of this type start before"
                    }

                }
            }
        },
        "rules":{
          "type":"array",
          "title":"list of rules which are applied to users or roles or days of the week",
          "items":{
            "type":"object",
            "description":"the rule object",
            "oneOf":[
              { "$ref":"#/definitions/rule/1"},
              { "$ref":"#/definitions/rule/2"},
              { "$ref":"#/definitions/rule/3"},
              { "$ref":"#/definitions/rule/4"},
              { "$ref":"#/definitions/rule/5"},
              { "$ref":"#/definitions/rule/6"},
              { "$ref":"#/definitions/rule/7"},
              { "$ref":"#/definitions/rule/8"},
              { "$ref":"#/definitions/rule/9"},
              { "$ref":"#/definitions/rule/10"},
              { "$ref":"#/definitions/rule/11"},
              { "$ref":"#/definitions/rule/12"},
              { "$ref":"#/definitions/rule/13"},
              { "$ref":"#/definitions/rule/14"},
              { "$ref":"#/definitions/rule/15"},
              { "$ref":"#/definitions/rule/16"},
              { "$ref":"#/definitions/rule/26"}
            ]
          }
        },
        "settings":{
            "type":"object",
            "title": "Settings object with items which will influence the behaviour of the algorithm",
            "properties":{
                "start":{
                    "type": "number",
                    "description": "the start time of the optimiser period"
                },
                "finish":{
                    "type": "number",
                    "description": "the end time of the optimiser period"
                },
                "runtime":{
                    "type": "number",
                    "description": "The runtime provided to the algorithm. If a solution is found before this timelimit the result will be returned early"
                },
                "cost_objective":{
                    "type": "number",
                    "description":"the importance of the cost objective for the algorithm. Each assigned shift will attract a cost of the pay_duration * the hourly_rate of the assigned employee"
                },
                "rule_objective":{
                    "type": "number",
                    "description": "the importance of the rule objective. Each violated shift will attract a penalty based on the penalty factor of the rule"
                },
                "fairness_objective":{
                    "type": "number",
                    "description": "the importance of the fairness objective"
                },
                "proficiency_objective":{
                    "type": "number",
                    "description": "the importance of the proficiency objective. Bonus will be given to employees who have a higher rating multiplied with this setting"
                }
            }
        }
    },
    "definitions": {
      "rules": {
        "1": {
          "type": "object",
          "description": "Rule 1 ensures the assignment of shifts",
          "properties": {
            "rule_id": {
              "type": "string",
              "description": "Identifier for rule 1"
            },
            "department_ids": {
              "type": "array of department_ids",
              "description": "optional list of department ids for which this rule applies to. If left empty, the rule will apply to all department ids"
            },
            "user_ids": {
              "type": "array of user_ids",
              "description": "optional list of user ids for which this rule applies. If left empty it will apply to all users"
            },
            "weekdays": {
              "type": "array of weekdays (numbers, 0 = Monday)",
              "description": "optional list of weekdays for which this rule applies. If left empty it will apply to all weekdays"
            },
            "is_mandatory": {
              "type": "boolean",
              "description": "indicates whether the rule is applied as mandatory. If set to true this could lead to unfeasible situations"
            },
            "penalty": {
              "type": "number",
              "description": "penalty for rule 1, for every unassigned shift this penalty will be applied"
            }
          }
        },
        "2": {
          "type": "object",
          "description": "Rule 2 restricts users to go over their contract hours",
          "properties": {
            "rule_id": {
              "type": "string",
              "description": "Identifier for rule 2"
            },
            "department_ids": {
              "type": "array of department_ids",
              "description": "optional list of department ids for which this rule applies to. If left empty, the rule will apply to all department ids"
            },
            "user_ids": {
              "type": "array of user_ids",
              "description": "optional list of user ids for which this rule applies. If left empty it will apply to all users"
            },
            "is_mandatory": {
              "type": "boolean",
              "description": "indicates whether the rule is applied as mandatory. If set to true this could lead to unfeasible situations"
            },
            "penalty": {
              "type": "number",
              "description": "penalty for rule 2, for every minute additional to the user's max contract hours this penalty will be applied per minute"
            }
          }
        },
        "3": {
          "type": "object",
          "description": "Rule 3: maximum consecutive work days",
          "properties": {
            "rule_id": {
              "type": "string",
              "description": "Identifier for rule 3"
            },
            "department_ids": {
              "type": "array of department_ids",
              "description": "optional list of department ids for which this rule applies to. If left empty, the rule will apply to all department ids"
            },
            "user_ids": {
              "type": "array of user_ids",
              "description": "optional list of user ids for which this rule applies. If left empty it will apply to all users"
            },
            "is_mandatory": {
              "type": "boolean",
              "description": "indicates whether the rule is applied as mandatory. If set to true this could lead to unfeasible situations"
            },
            "penalty": {
              "type": "number",
              "description": "penalty for rule 3, for every additional day of work this penalty will be applied"
            },
            "parameter_1": {
              "type": "number",
              "description": "maximum number of consecutive work days"
            },
            "parameter_2": {
              "type": "number",
              "description": "0 indicates that a shift is counted on a day when the shift starts, 1 indicates that a shift is counted on a day when the shift end"
            }
          }
        },
        "4": {
          "type": "object",
          "description": "Rule 4: minimum consecutive rest days",
          "properties": {
            "rule_id": {
              "type": "string",
              "description": "Identifier for rule 4"
            },
            "department_ids": {
              "type": "array of department_ids",
              "description": "optional list of department ids for which this rule applies to. If left empty, the rule will apply to all department ids"
            },
            "user_ids": {
              "type": "array of user_ids",
              "description": "optional list of user ids for which this rule applies. If left empty it will apply to all users"
            },
            "is_mandatory": {
              "type": "boolean",
              "description": "indicates whether the rule is applied as mandatory. If set to true this could lead to unfeasible situations"
            },
            "penalty": {
              "type": "number",
              "description": "penalty for rule 4, for every rest day block which does not follow the minimum days this penalty will be applied"
            },
            "parameter_1": {
              "type": "number",
              "description": "minimum number of consecutive rest days"
            },
            "parameter_2": {
              "type": "number",
              "description": "0 indicates that a shift is counted on a day when the shift starts, 1 indicates that a shift is counted on a day when the shift end"
            }
          }
        },
        "5": {
          "type": "object",
          "description": "Rule 5 rest time between shifts",
          "properties": {
            "rule_id": {
              "type": "string",
              "description": "Identifier for rule 5"
            },
            "department_ids": {
              "type": "array of department_ids",
              "description": "optional list of department ids for which this rule applies to. If left empty, the rule will apply to all department ids"
            },
            "user_ids": {
              "type": "array of user_ids",
              "description": "optional list of user ids for which this rule applies. If left empty it will apply to all users"
            },
            "is_mandatory": {
              "type": "boolean",
              "description": "indicates whether the rule is applied as mandatory. If set to true this could lead to unfeasible situations"
            },
            "penalty": {
              "type": "number",
              "description": "penalty for rule 5, if two shifts are assigned within the minimum rest time - the duration which is violated will be applied multiplied by this penalty"
            },
            "parameter_1": {
              "type": "number",
              "description": "minimum minutes between any two assigned shifts for 1 employee"
            },
            "parameter_2": {
              "type": "number",
              "description": "if shifts are closer to eachother than this number, they will be ignored"
            }
          }
        },
        "7": {
          "type": "object",
          "description": "Rule 7: max work days per work period",
          "properties": {
            "rule_id": {
              "type": "string",
              "description": "Identifier for rule 7"
            },
            "department_ids": {
              "type": "array of department_ids",
              "description": "optional list of department ids for which this rule applies to. If left empty, the rule will apply to all department ids"
            },
            "user_ids": {
              "type": "array of user_ids",
              "description": "optional list of user ids for which this rule applies. If left empty it will apply to all users"
            },
            "is_mandatory": {
              "type": "boolean",
              "description": "indicates whether the rule is applied as mandatory. If set to true this could lead to unfeasible situations"
            },
            "penalty": {
              "type": "number",
              "description": "penalty for rule 7, for every additional day assigned in a work period this penalty will be applied"
            },
            "parameter_1": {
              "type": "number",
              "description": "maximum days per workperiod of an employee"
            }
          }
        },
        "8": {
          "type": "object",
          "description": "Rule 8: Each shift must start x minutes after midnight",
          "properties": {
            "rule_id": {
              "type": "string",
              "description": "Identifier for rule 8"
            },
            "department_ids": {
              "type": "array of department_ids",
              "description": "optional list of department ids for which this rule applies to. If left empty, the rule will apply to all department ids"
            },
            "user_ids": {
              "type": "array of user_ids",
              "description": "optional list of user ids for which this rule applies. If left empty it will apply to all users"
            },
            "weekdays": {
              "type": "array of weekdays (numbers, 0 = Monday)",
              "description": "optional list of weekdays for which this rule applies. If left empty it will apply to all weekdays"
            },
            "is_mandatory": {
              "type": "boolean",
              "description": "indicates whether the rule is applied as mandatory. If set to true this could lead to unfeasible situations"
            },
            "penalty": {
              "type": "number",
              "description": "penalty for rule 8, for every unassigned shift this penalty will be applied"
            },
            "parameter_1": {
              "type": "number",
              "description": "Minutes from midnight after which the shift must start"
            }
          }
        },
        "9": {
          "type": "object",
          "description": "Rule 9: Shift must end before",
          "properties": {
            "rule_id": {
              "type": "string",
              "description": "Identifier for rule 9"
            },
            "department_ids": {
              "type": "array of department_ids",
              "description": "optional list of department ids for which this rule applies to. If left empty, the rule will apply to all department ids"
            },
            "user_ids": {
              "type": "array of user_ids",
              "description": "optional list of user ids for which this rule applies. If left empty it will apply to all users"
            },
            "weekdays": {
              "type": "array of weekdays (numbers, 0 = Monday)",
              "description": "optional list of weekdays for which this rule applies. If left empty it will apply to all weekdays"
            },
            "is_mandatory": {
              "type": "boolean",
              "description": "indicates whether the rule is applied as mandatory. If set to true this could lead to unfeasible situations"
            },
            "penalty": {
              "type": "number",
              "description": "penalty for rule 9, for every minute that the shift ends after the indicated time a penalty is included"
            },
            "parameter_1": {
              "type": "number",
              "description": "Minuted before midnight the shift has to end before"
            }
          }
        },
        "10": {
          "type": "object",
          "description": "Rule 10: Maximum minutes per shift",
          "properties": {
            "rule_id": {
              "type": "string",
              "description": "Identifier for rule 10"
            },
            "department_ids": {
              "type": "array of department_ids",
              "description": "optional list of department ids for which this rule applies to. If left empty, the rule will apply to all department ids"
            },
            "user_ids": {
              "type": "array of user_ids",
              "description": "optional list of user ids for which this rule applies. If left empty it will apply to all users"
            },
            "weekdays": {
              "type": "array of weekdays (numbers, 0 = Monday)",
              "description": "optional list of weekdays for which this rule applies. If left empty it will apply to all weekdays"
            },
            "is_mandatory": {
              "type": "boolean",
              "description": "indicates whether the rule is applied as mandatory. If set to true this could lead to unfeasible situations"
            },
            "penalty": {
              "type": "number",
              "description": "penalty for rule 10, for every minute the shift is longer than the limit, a penalty is applied"
            },
            "parameter_1": {
              "type": "number",
              "description": "Maximum minutes of a shift"
            }
          }
        },
        "11": {
          "type": "object",
          "description": "Rule 11: Minimum minutes per shift",
          "properties": {
            "rule_id": {
              "type": "string",
              "description": "Identifier for rule 11"
            },
            "department_ids": {
              "type": "array of department_ids",
              "description": "optional list of department ids for which this rule applies to. If left empty, the rule will apply to all department ids"
            },
            "user_ids": {
              "type": "array of user_ids",
              "description": "optional list of user ids for which this rule applies. If left empty it will apply to all users"
            },
            "weekdays": {
              "type": "array of weekdays (numbers, 0 = Monday)",
              "description": "optional list of weekdays for which this rule applies. If left empty it will apply to all weekdays"
            },
            "is_mandatory": {
              "type": "boolean",
              "description": "indicates whether the rule is applied as mandatory. If set to true this could lead to unfeasible situations"
            },
            "penalty": {
              "type": "number",
              "description": "penalty for rule 11, for every minute the shift is shorter than the limit, a penalty is applied"
            },
            "parameter_1": {
              "type": "number",
              "description": "Minimum minutes of a shift"
            }
          }
        },
        "12": {
          "type": "object",
          "description": "Rule 12: Maximum employees per day",
          "properties": {
            "rule_id": {
              "type": "string",
              "description": "Identifier for rule 12"
            },
            "department_ids": {
              "type": "array of department_ids",
              "description": "optional list of department ids for which this rule applies to. If left empty, the rule will apply to all department ids"
            },
            "user_ids": {
              "type": "array of user_ids",
              "description": "optional list of user ids for which this rule applies. If left empty it will apply to all users"
            },
            "weekdays": {
              "type": "array of weekdays (numbers, 0 = Monday)",
              "description": "optional list of weekdays for which this rule applies. If left empty it will apply to all weekdays"
            },
            "is_mandatory": {
              "type": "boolean",
              "description": "indicates whether the rule is applied as mandatory. If set to true this could lead to unfeasible situations"
            },
            "penalty": {
              "type": "number",
              "description": "penalty for rule 12, for every employee per day going over the maximum, this penalty is applied"
            },
            "parameter_1": {
              "type": "number",
              "description": "Maximum employees per day which are included in the filter"
            }
          }
        },
        "13": {
          "type": "object",
          "description": "Rule 13: Maximum minutes per day",
          "properties": {
            "rule_id": {
              "type": "string",
              "description": "Identifier for rule 13"
            },
            "department_ids": {
              "type": "array of department_ids",
              "description": "optional list of department ids for which this rule applies to. If left empty, the rule will apply to all department ids"
            },
            "user_ids": {
              "type": "array of user_ids",
              "description": "optional list of user ids for which this rule applies. If left empty it will apply to all users"
            },
            "weekdays": {
              "type": "array of weekdays (numbers, 0 = Monday)",
              "description": "optional list of weekdays for which this rule applies. If left empty it will apply to all weekdays"
            },
            "is_mandatory": {
              "type": "boolean",
              "description": "indicates whether the rule is applied as mandatory. If set to true this could lead to unfeasible situations"
            },
            "penalty": {
              "type": "number",
              "description": "penalty for rule 13, for every minute assigned over the maximum a penalty will be applied"
            },
            "parameter_13": {
              "type": "number",
              "description": "Maximum number of minutes per day"
            }
          }
        },
        "14": {
          "type": "object",
          "description": "Rule 14: Minimum minutes per payperiod ",
          "properties": {
            "rule_id": {
              "type": "string",
              "description": "Identifier for rule 14"
            },
            "department_ids": {
              "type": "array of department_ids",
              "description": "optional list of department ids for which this rule applies to. If left empty, the rule will apply to all department ids"
            },
            "user_ids": {
              "type": "array of user_ids",
              "description": "optional list of user ids for which this rule applies. If left empty it will apply to all users"
            },
            "is_mandatory": {
              "type": "boolean",
              "description": "indicates whether the rule is applied as mandatory. If set to true this could lead to unfeasible situations"
            },
            "penalty": {
              "type": "number",
              "description": "penalty for rule 14, for every minute, the employee is not assigned minutes under their payperiod_minutes_min this penalty is applied"
            }
          }
        },
        "15": {
          "type": "object",
          "description": "Rule 15: Maximum shifts per day, for an employee",
          "properties": {
            "rule_id": {
              "type": "string",
              "description": "Identifier for rule 15"
            },
            "department_ids": {
              "type": "array of department_ids",
              "description": "optional list of department ids for which this rule applies to. If left empty, the rule will apply to all department ids"
            },
            "user_ids": {
              "type": "array of user_ids",
              "description": "optional list of user ids for which this rule applies. If left empty it will apply to all users"
            },
            "is_mandatory": {
              "type": "boolean",
              "description": "indicates whether the rule is applied as mandatory. If set to true this could lead to unfeasible situations"
            },
            "penalty": {
              "type": "number",
              "description": "penalty for rule 15, for every additional shift over the limit, this penalty is applied"
            },
            "parameter_1": {
              "type": "number",
              "description": "Maximum shifts per day for an employee"
            }
          }
        },
        "16": {
          "type": "object",
          "description": "Rule 16: Shifts assigned to employee need to have Y minutes of break time after X minutes of the start of the shift",
          "properties": {
            "rule_id": {
              "type": "string",
              "description": "Identifier for rule 16"
            },
            "department_ids": {
              "type": "array of department_ids",
              "description": "optional list of department ids for which this rule applies to. If left empty, the rule will apply to all department ids"
            },
            "user_ids": {
              "type": "array of user_ids",
              "description": "optional list of user ids for which this rule applies. If left empty it will apply to all users"
            },
            "is_mandatory": {
              "type": "boolean",
              "description": "indicates whether the rule is applied as mandatory. If set to true this could lead to unfeasible situations"
            },
            "penalty": {
              "type": "number",
              "description": "penalty for rule 16, for every assigned shift in violation, this penalty is applied"
            },
            "parameter_1": {
              "type": "number",
              "description": "Time after which the break should occur"
            },
            "parameter_2": {
              "type": "number",
              "description": "Length of the break"
            }
          }
        },
        "17": {
          "type": "object",
          "description": "Rule 17: Bonus in case a shift of a certain type is assigned an employee who prefers to work that shift-type",
          "properties": {
            "rule_id": {
              "type": "string",
              "description": "Identifier for rule 17"
            },
            "department_ids": {
              "type": "array of department_ids",
              "description": "optional list of department ids for which this rule applies to. If left empty, the rule will apply to all department ids"
            },
            "user_ids": {
              "type": "array of user_ids",
              "description": "optional list of user ids for which this rule applies. If left empty it will apply to all users"
            },
            "is_mandatory": {
              "type": "boolean",
              "description": "indicates whether the rule is applied as mandatory. If set to true this could lead to unfeasible situations"
            },
            "penalty": {
              "type": "number",
              "description": "bonus for rule 17, for every assigned shift to an employee that has a preference, this bonus is applied"
            }
          }
        },
        "18": {
          "type": "object",
          "description": "Rule 18: Ensures that for at most X weekends shifts of type are assigned to an employee.",
          "properties": {
            "rule_id": {
              "type": "string",
              "description": "Identifier for rule 18"
            },
            "department_ids": {
              "type": "array of department_ids",
              "description": "optional list of department ids for which this rule applies to. If left empty, the rule will apply to all department ids"
            },
            "user_ids": {
              "type": "array of user_ids",
              "description": "optional list of user ids for which this rule applies. If left empty it will apply to all users"
            },
            "is_mandatory": {
              "type": "boolean",
              "description": "indicates whether the rule is applied as mandatory. If set to true this could lead to unfeasible situations"
            },
            "penalty": {
              "type": "number",
              "description": "penalty for rule 18, for shift that is assigned too much, the penalty is applied"
            },
            "parameter_1": {
              "type": "number",
              "description": "Maximum number of shifts"
            },
            "parameter_2": {
              "type": "number",
              "description": "Type of the shifts for which this rule is applied"
            }
          }
        },
        "19": {
          "type": "object",
          "description": "Rule 19: Gives a bonus for assigning the shift to the employee with matching employee ID that is set on the shift.",
          "properties": {
            "rule_id": {
              "type": "string",
              "description": "Identifier for rule 19"
            },
            "department_ids": {
              "type": "array of department_ids",
              "description": "optional list of department ids for which this rule applies to. If left empty, the rule will apply to all department ids"
            },
            "user_ids": {
              "type": "array of user_ids",
              "description": "optional list of user ids for which this rule applies. If left empty it will apply to all users"
            },
            "is_mandatory": {
              "type": "boolean",
              "description": "indicates whether the rule is applied as mandatory. If set to true this could lead to unfeasible situations"
            },
            "penalty": {
              "type": "number",
              "description": "bonus for rule 19, for each shift that is assigned to a pre-assigned employee, the bonus is assigned"
            }
          }
        },
        "20": {
          "type": "object",
          "description": "Rule 20: Adds a bonus in case a shift is assigned an employee who prefers to work during that time",
          "properties": {
            "rule_id": {
              "type": "string",
              "description": "Identifier for rule 20"
            },
            "department_ids": {
              "type": "array of department_ids",
              "description": "optional list of department ids for which this rule applies to. If left empty, the rule will apply to all department ids"
            },
            "user_ids": {
              "type": "array of user_ids",
              "description": "optional list of user ids for which this rule applies. If left empty it will apply to all users"
            },
            "is_mandatory": {
              "type": "boolean",
              "description": "indicates whether the rule is applied as mandatory. If set to true this could lead to unfeasible situations"
            },
            "penalty": {
              "type": "number",
              "description": "bonus for rule 20, for each hour that a shifts overlaps with an employee preference to work, the bonus is applied"
            }
          }
        },
        "21": {
          "type": "object",
          "description": "Rule 21: Ensures that employees get a number of working hours close to the number in the previous pay-period",
          "properties": {
            "rule_id": {
              "type": "string",
              "description": "Identifier for rule 21"
            },
            "department_ids": {
              "type": "array of department_ids",
              "description": "optional list of department ids for which this rule applies to. If left empty, the rule will apply to all department ids"
            },
            "user_ids": {
              "type": "array of user_ids",
              "description": "optional list of user ids for which this rule applies. If left empty it will apply to all users"
            },
            "is_mandatory": {
              "type": "boolean",
              "description": "indicates whether the rule is applied as mandatory. If set to true this could lead to unfeasible situations"
            },
            "penalty": {
              "type": "number",
              "description": "penalty for rule 21, for each hour that the number of assigned hours deviates from the number of hours in the previous period, the penalty is applied"
            }
          }
        },
        "22": {
          "type": "object",
          "description": "Rule 22: Ensures that employees get a number of shifts of type X (parameter 1) is close to the number in the previous pay-period",
          "properties": {
            "rule_id": {
              "type": "string",
              "description": "Identifier for rule 22"
            },
            "department_ids": {
              "type": "array of department_ids",
              "description": "optional list of department ids for which this rule applies to. If left empty, the rule will apply to all department ids"
            },
            "user_ids": {
              "type": "array of user_ids",
              "description": "optional list of user ids for which this rule applies. If left empty it will apply to all users"
            },
            "is_mandatory": {
              "type": "boolean",
              "description": "indicates whether the rule is applied as mandatory. If set to true this could lead to unfeasible situations"
            },
            "penalty": {
              "type": "number",
              "description": "penalty for rule 22, for each shift that the number of assigned shifts deviates from the number of shifts in the previous period, the penalty is applied"
            }
          }
        },
        "23": {
          "type": "object",
          "description": "Rule 23: Ensures each period of X days an employee gets a work-free period of at least Y minutes",
          "properties": {
            "rule_id": {
              "type": "string",
              "description": "Identifier for rule 23"
            },
            "department_ids": {
              "type": "array of department_ids",
              "description": "optional list of department ids for which this rule applies to. If left empty, the rule will apply to all department ids"
            },
            "user_ids": {
              "type": "array of user_ids",
              "description": "optional list of user ids for which this rule applies. If left empty it will apply to all users"
            },
            "is_mandatory": {
              "type": "boolean",
              "description": "indicates whether the rule is applied as mandatory. If set to true this could lead to unfeasible situations"
            },
            "penalty": {
              "type": "number",
              "description": "penalty for rule 23, for each shift that the number of assigned shifts deviates from the number of shifts in the previous period, the penalty is applied"
            },
            "parameter_1": {
              "type": "number",
              "description": "Period in which the resting time must be, in days"
            },
            "parameter_2": {
              "type": "number",
              "description": "minimum resting period in minutes"
            }
          }
        },
        "24": {
          "type": "object",
          "description": "Rule 24: Ensures that each period of Y days has at least one period with X consecutive days off",
          "properties": {
            "rule_id": {
              "type": "string",
              "description": "Identifier for rule 24"
            },
            "department_ids": {
              "type": "array of department_ids",
              "description": "optional list of department ids for which this rule applies to. If left empty, the rule will apply to all department ids"
            },
            "user_ids": {
              "type": "array of user_ids",
              "description": "optional list of user ids for which this rule applies. If left empty it will apply to all users"
            },
            "is_mandatory": {
              "type": "boolean",
              "description": "indicates whether the rule is applied as mandatory. If set to true this could lead to unfeasible situations"
            },
            "penalty": {
              "type": "number",
              "description": "penalty for rule 24, for each shift that the number of assigned shifts deviates from the number of shifts in the previous period, the penalty is applied"
            },
            "parameter_1": {
              "type": "number",
              "description": "Period in which the resting time must be, in days"
            },
            "parameter_2": {
              "type": "number",
              "description": "Minimum number of consecutive days off"
            }
          }
        },
        "25": {
          "type": "object",
          "description": "Rule 25: Ensures that the maximum number of working minutes in the period will not be exceeded",
          "properties": {
            "rule_id": {
              "type": "string",
              "description": "Identifier for rule 25"
            },
            "department_ids": {
              "type": "array of department_ids",
              "description": "optional list of department ids for which this rule applies to. If left empty, the rule will apply to all department ids"
            },
            "user_ids": {
              "type": "array of user_ids",
              "description": "optional list of user ids for which this rule applies. If left empty it will apply to all users"
            },
            "is_mandatory": {
              "type": "boolean",
              "description": "indicates whether the rule is applied as mandatory. If set to true this could lead to unfeasible situations"
            },
            "penalty": {
              "type": "number",
              "description": "penalty for rule 25, for each minute that an employee is working more than parameter 1, the penalty is applied"
            },
            "parameter_1": {
              "type": "number",
              "description": "maximum working minutes in period"
            }
          }
        },
        "26": {
          "type": "object",
          "description": "Rule 26: After working shift type 1, an employee must have a minimum of X days rest before working shift type 2",
          "properties": {
            "rule_id": {
              "type": "string",
              "description": "Identifier for rule 26"
            },
            "department_ids": {
              "type": "array of department_ids",
              "description": "optional list of department ids for which this rule applies to. If left empty, the rule will apply to all department ids"
            },
            "user_ids": {
              "type": "array of user_ids",
              "description": "optional list of user ids for which this rule applies. If left empty it will apply to all users"
            },
            "is_mandatory": {
              "type": "boolean",
              "description": "indicates whether the rule is applied as mandatory. If set to true this could lead to unfeasible situations"
            },
            "penalty": {
              "type": "number",
              "description": "penalty for rule 26, for every assigned shift in violation, this penalty is applied"
            },
            "parameter_1": {
              "type": "number",
              "description": "Id of shift type 1"
            },
            "parameter_2": {
              "type": "number",
              "description": "Id of shift type 2"
            },
            "parameter_3": {
              "type": "number",
              "description": "Minimum days between shifts"
            }
          }
        }
      }
    }
}
```
> example JSON

```json
{
  "users":
  [
    {
      "id":"123", //employee id
      "start_contract":"1492995600", //start of the contract of the employee
      "hourly_rate": "19.56",
      "payperiod_minutes_min" : 2100, //contracted minutes for a certain payperiod the employee is on
      "payperiod_minutes_max" : 2400, //if the employee goes over this number, an overtime penalty will be incurred, this can be kept the same as the min depending on the situation
      "payperiod_length_days": 14, //payperiod for this employee
      "is_fixed": false, //if set to true this employee will not be touched by the optimisation but it shifts might count to some of the rules
      "skills": //optional skills
      [
        { "id": "789",  //id for the skill
          "level": "1" //profiency / skill level
        }
      ],
      "licenses":[
        {
          "id":"456",
          "from": "1492995600",
          "expires":"1492995600"
        }
      ],
      "unavailabilities":[
        {
          "start":"1492995600",
          "finish":"1492995600",
          "type":1, //type of unavailability - sick, normal leave, etc
          "pay_duration": 0 //pay duration for the leave which is used for the min and max minutes per payperiod
        }
      ],
      "department_ids":
      [
        { "id": "123",
          "from": "1492995600",
          "proficiency_rating" :5
        }
      ]
    }
  ],
  "shifts":[
    {
      "id" : "321",
      "start": "1492995600",
      "finish": "1492995600",
      "is_fixed": false, //if this is set to true the employee_id should be entered as well and then the shift won't be touched
      "user_id": "123",
      "pay_duration": 120,
      "break_duration": 0,
      "skills":[
        {
          "id": "789",
          "min_level": "3"
        }
      ],
      "licenses":[
        {
          "id":"456"
        }
      ],
      "breaks":[
        {
          "start" : "1492995600",
          "finish" : "1492995600"
        }
      ],
      "subshifts":[
        {
          "start" : "1492995600",
          "finish" : "1492995600",
          "department_id":"123"
        }
      ]
    }
  ],
  "rules":[
    {
      "rule_id":"1", //1 = penalty for keeping unassigned shifts
      "department_ids":["123","456"], // department ids that the rule applies to; leave blank for all
      "user_ids": ["123","456"], // employee ids that the rule applies to; leave blank for all
      "parameter_1": 0, //can be optional for various rule_ids, will provide the rules and their identifiers in an another document
      "parameter_2": 0,
      "penalty":"100", //penalty for violating this rule - in this case per shift
      "is_mandatory": false //if this is set to true the rule will be adhered to no matter what - this is quite dangerous because if the input situation is 'infeasible' this will result in an error - best practice is to never really use this except for extreme cases
    },
    {
      "rule_id":"2", //2 = do not violate contract hours
      "department_ids":["123","456"], // department ids that the rule applies to; leave blank for all
      "user_ids": ["123","456"], // employee ids that the rule applies to; leave blank for all
      "parameter_1": 0,
      "parameter_2": 0,
      "penalty":"1", //penalty for violating this rule - in this case per violated minute
      "is_mandatory": false //if this is set to true the rule will be adhered to no matter what - this is quite dangerous because if the input situation is 'infeasible' this will result in an error - best practice is to never really use this except for extreme cases
    },
    {
      "rule_id":"3", //3 = maximum consecutive work days
      "department_ids":["123","456"], // department ids that the rule applies to; leave blank for all
      "user_ids": ["123","456"], // employee ids that the rule applies to; leave blank for all
      "parameter_1": 3, //number of consecutive work days
      "parameter_2": 0,
      "penalty":"1", //penalty for violating this rule per day
      "is_mandatory": false //if this is set to true the rule will be adhered to no matter what - this is quite dangerous because if the input situation is 'infeasible' this will result in an error - best practice is to never really use this except for extreme cases
    },
    {
      "rule_id":"4", //4 = minimum consecutive rest days
      "department_ids":["123","456"], // department ids that the rule applies to; leave blank for all
      "user_ids": ["123","456"], // employee ids that the rule applies to; leave blank for all
      "parameter_1": 2, //number of consecutive rest days
      "parameter_2": 0,
      "penalty":"1", //penalty for violating this rule per day
      "is_mandatory": false //if this is set to true the rule will be adhered to no matter what - this is quite dangerous because if the input situation is 'infeasible' this will result in an error - best practice is to never really use this except for extreme cases
    },
    {
      "rule_id":"5", //5 = rest time between shifts
      "department_ids":["123","456"], // department ids that the rule applies to; leave blank for all
      "user_ids": ["123","456"], // employee ids that the rule applies to; leave blank for all
      "parameter_1": 480, //minimum minutes there need to be between shift 1 and shift 2
      "parameter_2": 180, //however if the shifts are closer than 180 minutes apart each other - it is ok. This is for split shifts
      "penalty":"1", //penalty for violating this rule per minute
      "is_mandatory": false //if this is set to true the rule will be adhered to no matter what - this is quite dangerous because if the input situation is 'infeasible' this will result in an error - best practice is to never really use this except for extreme cases
    },
    {
      "rule_id":"7", //7 = max work days in payperiod
      "department_ids":["123","456"], // department ids that the rule applies to; leave blank for all
      "user_ids": ["123","456"], // employee ids that the rule applies to; leave blank for all
      "parameter_1": 5, //in days
      "parameter_2": 0,
      "penalty":"1", //penalty for violating this rule per day
      "is_mandatory": false //if this is set to true the rule will be adhered to no matter what - this is quite dangerous because if the input situation is 'infeasible' this will result in an error - best practice is to never really use this except for extreme cases
    },
    {
      "rule_id":"8", //8 = shift must start after for each assigned shift
      "department_ids":["123","456"], // department ids that the rule applies to; leave blank for all
      "user_ids": ["123","456"], // employee ids that the rule applies to; leave blank for all
      "weekdays": [0,3,5,6], // weekdays that the rule applies to (0 = Monday); leave blank for all
      "parameter_1": 420, //minutes from midnight
      "parameter_2": 0,
      "penalty":"1", //penalty for violating this rule per violated minute
      "is_mandatory": false //if this is set to true the rule will be adhered to no matter what - this is quite dangerous because if the input situation is 'infeasible' this will result in an error - best practice is to never really use this except for extreme cases
    },
    {
      "rule_id":"9", //9 = shift must end before
      "department_ids":["123","456"], // department ids that the rule applies to; leave blank for all
      "user_ids": ["123","456"], // employee ids that the rule applies to; leave blank for all
      "weekdays": [0,3,5,6], // weekdays that the rule applies to (0 = Monday); leave blank for all
      "parameter_1": 1200, //minutes from midnight
      "parameter_2": 0,
      "penalty":"1", //penalty for violating this rule per violated minute
      "is_mandatory": false //if this is set to true the rule will be adhered to no matter what - this is quite dangerous because if the input situation is 'infeasible' this will result in an error - best practice is to never really use this except for extreme cases
    },
    {
      "rule_id":"10", //10 = max minutes per shift (so you might have long shifts for a bunch of people but you want to exclude certain groups for long shifts using this rule)
      "department_ids":["123","456"], // department ids that the rule applies to; leave blank for all
      "user_ids": ["123","456"], // employee ids that the rule applies to; leave blank for all
      "weekdays": [0,3,5,6], // weekdays that the rule applies to (0 = Monday); leave blank for all
      "parameter_1": 360, //max payminutes per shift
      "parameter_2": 0,
      "penalty":"1", //penalty for violating this rule per violated minute
      "is_mandatory": false //if this is set to true the rule will be adhered to no matter what - this is quite dangerous because if the input situation is 'infeasible' this will result in an error - best practice is to never really use this except for extreme cases
    },
    {
      "rule_id":"11", //11 = min minutes per shift
      "department_ids":["123","456"], // department ids that the rule applies to; leave blank for all
      "user_ids": ["123","456"], // employee ids that the rule applies to; leave blank for all
      "weekdays": [0,3,5,6], // weekdays that the rule applies to (0 = Monday); leave blank for all
      "parameter_1": 180, //min payminutes per shift
      "parameter_2": 0,
      "penalty":"1", //penalty for violating this rule per violated minute
      "is_mandatory": false //if this is set to true the rule will be adhered to no matter what - this is quite dangerous because if the input situation is 'infeasible' this will result in an error - best practice is to never really use this except for extreme cases
    },
    {
      "rule_id":"12", //12 = max employees per day
      "department_ids":["123","456"], // department ids that the rule applies to; leave blank for all
      "user_ids": ["123","456"], // employee ids that the rule applies to; leave blank for all
      "weekdays": [0,3,5,6], // weekdays that the rule applies to (0 = Monday); leave blank for all
      "parameter_1": 5, //max assigned employees per day for the department ids
      "parameter_2": 0,
      "penalty":"1", //penalty for violating this rule per violated employee
      "is_mandatory": false //if this is set to true the rule will be adhered to no matter what - this is quite dangerous because if the input situation is 'infeasible' this will result in an error - best practice is to never really use this except for extreme cases
    },
    {
      "rule_id":"13", //13 = max minutes per day
      "department_ids":["123","456"], // department ids that the rule applies to; leave blank for all
      "user_ids": ["123","456"], // employee ids that the rule applies to; leave blank for all
      "weekdays": [0,3,5,6], // weekdays that the rule applies to (0 = Monday); leave blank for all
      "parameter_1": 480, //max assigned shift minutes per day
      "parameter_2": 0,
      "penalty":"1", //penalty for violating this rule per violated employee
      "is_mandatory": false //if this is set to true the rule will be adhered to no matter what - this is quite dangerous because if the input situation is 'infeasible' this will result in an error - best practice is to never really use this except for extreme cases
    },
    {
      "rule_id":"14", //14 = min minutes per payperiod (related to payperiod_minutes_min)
      "department_ids":["123","456"], // department ids that the rule applies to; leave blank for all
      "user_ids": ["123","456"], // employee ids that the rule applies to; leave blank for all
      "parameter_1": 0,
      "parameter_2": 0,
      "penalty":"1", //penalty for violating this rule per violated employee
      "is_mandatory": false //if this is set to true the rule will be adhered to no matter what - this is quite dangerous because if the input situation is 'infeasible' this will result in an error - best practice is to never really use this except for extreme cases
    },
    {
      "rule_id":"15", //15 = maximum shifts per day, for an employee
      "department_ids":["123","456"], // department ids that the rule applies to; leave blank for all
      "user_ids": ["123","456"], // employee ids that the rule applies to; leave blank for all
      "parameter_1": 2,
      "penalty":"1", //penalty for violating this rule per violated shift
      "is_mandatory": false //if this is set to true the rule will be adhered to no matter what - this is quite dangerous because if the input situation is 'infeasible' this will result in an error - best practice is to never really use this except for extreme cases
    },
    {
      "rule_id":"16", //16 = minimum break length
      "department_ids":["123","456"], // department ids that the rule applies to; leave blank for all
      "user_ids": ["123","456"], // employee ids that the rule applies to; leave blank for all
      "parameter_1": 600,
      "parameter_2": 60,
      "penalty":"1", //penalty for violating this rule per violated shift
      "is_mandatory": false //if this is set to true the rule will be adhered to no matter what - this is quite dangerous because if the input situation is 'infeasible' this will result in an error - best practice is to never really use this except for extreme cases
    },
    {
      "rule_id":"17", //17 = bonus in case a shift of a certain type is assigned an employee who prefers to work that shift-type
      "department_ids":["123","456"], // department ids that the rule applies to; leave blank for all
      "user_ids": ["123","456"], // employee ids that the rule applies to; leave blank for all
      "penalty":"1", //bonus assigning a shift to an employee that has a preference for that shift-type
      "is_mandatory": false //if this is set to true the rule will be adhered to no matter what - this is quite dangerous because if the input situation is 'infeasible' this will result in an error - best practice is to never really use this except for extreme cases
    },
    {
      "rule_id":"18", //18 = ensures that for at most X weekends shifts of type are assigned to an employee
      "department_ids":["123","456"], // department ids that the rule applies to; leave blank for all
      "user_ids": ["123","456"], // employee ids that the rule applies to; leave blank for all
      "penalty":"1", //bonus assigning a shift to an employee that has a preference for that shift-type
      "parameter_1": 8, //maximum number of shifts
      "parameter_2": 2, //type of the shifts for which this rule is applied
      "is_mandatory": false //if this is set to true the rule will be adhered to no matter what - this is quite dangerous because if the input situation is 'infeasible' this will result in an error - best practice is to never really use this except for extreme cases
    },
    {
      "rule_id":"19", //19 = gives a bonus for assigning the shift to the employee with matching employee ID that is set on the shift
      "department_ids":["123","456"], // department ids that the rule applies to; leave blank for all
      "user_ids": ["123","456"], // employee ids that the rule applies to; leave blank for all
      "penalty":"1", //bonus for each shift that is assigned to a pre-assigned employee
      "is_mandatory": false //if this is set to true the rule will be adhered to no matter what - this is quite dangerous because if the input situation is 'infeasible' this will result in an error - best practice is to never really use this except for extreme cases
    },
    {
      "rule_id":"20", //20 = Adds a bonus in case a shift is assigned an employee who prefers to work during that time
      "department_ids":["123","456"], // department ids that the rule applies to; leave blank for all
      "user_ids": ["123","456"], // employee ids that the rule applies to; leave blank for all
      "penalty":"1", //for each hour that a shifts overlaps with an employee preference to work this is applied
      "is_mandatory": false //if this is set to true the rule will be adhered to no matter what - this is quite dangerous because if the input situation is 'infeasible' this will result in an error - best practice is to never really use this except for extreme cases
    },
    {
      "rule_id":"21", //21 = Ensures that employees get a number of working hours close to the number in the previous pay-period
      "department_ids":["123","456"], // department ids that the rule applies to; leave blank for all
      "user_ids": ["123","456"], // employee ids that the rule applies to; leave blank for all
      "penalty":"1", //bonus for each shift that is assigned to a pre-assigned employee
      "is_mandatory": false //if this is set to true the rule will be adhered to no matter what - this is quite dangerous because if the input situation is 'infeasible' this will result in an error - best practice is to never really use this except for extreme cases
    },
    {
      "rule_id":"22", //22 = Ensures that employees get a number of shifts of type X (parameter 1) is close to the number in the previous pay-period
      "department_ids":["123","456"], // department ids that the rule applies to; leave blank for all
      "user_ids": ["123","456"], // employee ids that the rule applies to; leave blank for all
      "parameter_1": 1, // type of shifts for which the rule applies
      "penalty":"1", //for each shift that the number of assigned shifts deviates from the number of shifts in the previous period, the penalty is applied
      "is_mandatory": false //if this is set to true the rule will be adhered to no matter what - this is quite dangerous because if the input situation is 'infeasible' this will result in an error - best practice is to never really use this except for extreme cases
    },
    {
      "rule_id":"23", //23 = Ensures each period of X days an employee gets a work-free period of at least Y minutes
      "department_ids":["123","456"], // department ids that the rule applies to; leave blank for all
      "user_ids": ["123","456"], // employee ids that the rule applies to; leave blank for all
      "parameter_1": 7, // period in which the resting time must be, in days
      "parameter_2": 1920, // minimum resting period in minutes
      "penalty":"1", //for missing resting period for an employee, the penalty is applied
      "is_mandatory": false //if this is set to true the rule will be adhered to no matter what - this is quite dangerous because if the input situation is 'infeasible' this will result in an error - best practice is to never really use this except for extreme cases
    },
    {
      "rule_id":"24", //24 = Ensures that each period of Y days has at least one period with X consecutive days off
      "department_ids":["123","456"], // department ids that the rule applies to; leave blank for all
      "user_ids": ["123","456"], // employee ids that the rule applies to; leave blank for all
      "parameter_1": 7, // period in which the resting time must be, in days
      "parameter_2": 2, // minimum resting period in minutes
      "penalty":"1", //for missing resting period for an employee, the penalty is applied
      "is_mandatory": false //if this is set to true the rule will be adhered to no matter what - this is quite dangerous because if the input situation is 'infeasible' this will result in an error - best practice is to never really use this except for extreme cases
    },
    {
      "rule_id":"25", //25 = Ensures that the maximum number of working minutes in the period will not be exceeded
      "department_ids":["123","456"], // department ids that the rule applies to; leave blank for all
      "user_ids": ["123","456"], // employee ids that the rule applies to; leave blank for all
      "parameter_1": 960, // maximum working minutes in period
      "penalty":"1", //for each minute that an employee is working more than parameter 1, this penalty is applied
      "is_mandatory": false //if this is set to true the rule will be adhered to no matter what - this is quite dangerous because if the input situation is 'infeasible' this will result in an error - best practice is to never really use this except for extreme cases
    },
    {
      "rule_id":"26", //26 = minimum days between shifts of different types (e.g. min 2 days after N shift before working D shift)
      "department_ids":["123","456"], // department ids that the rule applies to; leave blank for all
      "user_ids": ["123","456"], // employee ids that the rule applies to; leave blank for all
      "parameter_1": 3, // id shift type 1
      "parameter_2": 1, // id of shift type 2
      "prarameter_3": 2, //minimum days between shift types
      "penalty":"1", //penalty for violating this rule per employee per forbidden shift type combination assignment
      "is_mandatory": false //if this is set to true the rule will be adhered to no matter what - this is quite dangerous because if the input situation is 'infeasible' this will result in an error - best practice is to never really use this except for extreme cases
    }
  ],
  "settings":{
    "start":"1492995600", //period to consider for the optimiser
    "finish":"1492995600",
    "runtime":"60", //maximum number of seconds provided to the optimisation algorithm. If it goes over this it will return the best solution it would have found at that stage
    "cost_objective": 1, //setting to indicate how important it is to adhere to costs
    "rule_objective": 100000, //setting to indicate how important the rules are compared to the other objectives
    "fairness_objective": 0, //fairness depends a bit on how it is defined (could be start times spread out over a certain period for example)
    "proficiency_objective": 0 //proficiency objective setting
  }
}

```

The Shift Fill json expects the following inputs:
* <b>shifts</b>: existing shifts, if the is_fixed flag = true, then these shifts will not be changed by the optimizer, but they will be taken into account for rule checking
* <b>users</b>: employees who will be part of the scenario
* <b>departments</b>: list of departments which are relevant for the specific run
* <b>rules</b>: array of rules which are applied to users or roles or a subset of days of the week
* <b>settings</b>: an object with various settings for the algorithm

### Input File FAQ
* <b>How can I manage compliance with algorithms?</b>

The shift fill algorithm will ensure labor laws are applied correctly while considering additional priorities (e.g., employee preferences). Whether a rule applies to all employees or a subset, it will be checked when shifts are assigned. This structure can also be used to run what-if scenarios and analyse the impact changing rules on existing rosters.

Labor laws can be specified within a hierarchy, with different rules applying at a location, department, employee type, and employee level.

* <b>What if I want a rule to always be followed?</b>

Each rule can be set to mandatory or given a specific weight to prioritize relative importance. However, use caution with the mandatory flag, as conflicting or impossible mandatory rules will result in an infeasible solution and the optimizer will not return a result.

To give a simple example: if you have a mandatory rule that all employees must be assigned exactly 40 hours in a week, and your scenario has 1 employee (40 hours) and 4 8-hour shifts, then the result is infeasible. Even if all shifts are assigned to the one employee, they will only have 32 hours in the week.  In this case, the algorithm will not return a result.

The advantage of using weights to guide the results is that it allows you to specified *preferred* outcomes as well as the relative importance of those outcomes.

For instance, there is a choice between assigning all shifts (to ensure coverage) and not assigning overtime to employees (to reduce costs).  In an ideal world, you could assign all shifts to employees without incurring overtime.  However, in most real world circumstances, it's a business decision on which is more important -- coverage or costs, and to what extent one should be priortized over the other.

* <b>What rules are available to be included in the optimization run?</b>

- Total hours of the scheduled period (of all employees) must not exceed X.
- Total unassigned hours in the scheduled period must not exceed X
- All shifts have to be assigned
- Number of employees working in the schedule must not exceed X
- Number of employees working on the same day must not exceed X
- Employee maximum hours in their pay period cannot be exceeded
- Employee minimum hours in their pay period has to be met
- Employee maximum hours in the total schedule cannot be exceeded
- Employee minimum hours in the total schedule has to be met (these rules are for when there are rules for a longer period than the pay period. So employees has to work 24 hours per week, with a minimum of 110 a month - this happens quite a bit in Europe)
- Employee must not work more than X consecutive days
- Employee must have X consecutive days off when there is an off day
- Minimum gap between shifts must be at least X minutes
- Must not work X minutes per shift
- Must not work more than X minutes per shift
- Shift must start after
- Shift must end before
- Shift must contain a break
- Break time must not exceed X minutes
- must not work more than X days in the schedule
- must not work more than X days in the pay period
- Costs per shift must be less than X
- Total schedule costs must be less than X
- Total pay period costs must be less than X
- Maximum shifts starting within a time period (this will help forcing employees on a certain rotation)
- Must have Y minutes break after X minutes from start of shift
- Preference to assign shift to preassigned employee
- Must have X day rest between different shift types

## Shift Fill Output

```json
{
  "result":"1", //0 = unfeasible, 1 = optimal, 2 = not done yet but returned best result
  "goal_score":"200", //this is the sum of all the violations + costs coming out of the optimisation
  "shifts": [
    {
      "shift_id" : "123",
      "employee_id" : "456",
      "shift_costs" : "60",
      "violation_costs": "0"
    }
  ],
  "rule_violations":[
    {
      "rule_id": "1",
      "shift_id" :"321",
      "violation_costs":"1000",
      "employee_id": "123", //not for rule 1 but if a rule is related to an employee this key will have the employee id
      "date" : "1492995600" //date in case the violation is date based
    }
  ]
}
```

The Shift Fill output json returns a set of shifts and a set of rule violations.

Shifts will have an employee_id field to indicate which employee they have been assigned to, a shift_cost field to indicate the cost (wages, premiums) of a given shift, and finally a violation_costs field that indicates the value of any penalties associated with the shift assignment.

Rule Violations will have a rule_id (to indicate which rule was violated), the shift_id and employee_id (if applicable), and the violation_costs due to any penalties incurred for violating rules. For instance, if an employee has a target contract hours of 35 to 40, but was only assigned 32 hours, then they would have a rule violation that indicates the penalty for this violation.

All violations and costs are summed to define the overall goal_score.  The lower the goal_score the better the result in the sense that there are fewer costs and violations.

### FAQ
* <b> How do I link the shifts in this json to shifts / employees in my system?</b>

The shifts object will return a shift_id field, which is a unique identifier for the shift.  A _unique_ shift_id must be specified for each shift in the input json, and the same ID will be returned in the output.

Similarly, the shifts object will return an employee_id for any shift assigned to an employee.  This field will be blank for unassigned shifts. A _unique_ employee_id must be specified for each shift in the input json, and the same ID will be returned to link back to the assigned employee.

* <b> The optimizer run isn't returning any results, what should I check?</b>

In some cases, you won't get an error message back, but you also won't see any shifts assigned, the goal_score is 0, or you'll see something else that indicates a partial / incomplete / empty result. This typically happens because there is some logical flaw with your input json. Any parsing errors (e.g., typos) or hard erros (e.g., duplicate id fields) will result in an error message. If you don't see an error, then your input json is probably _technically_ OK, but you have another issue - so keep digging a little.

Common things to check include:
* Do your department_ids match between your input shifts and your input employees? For instance, if your employees have a department_id "nurse" and the shifts have department_id "nursing" then the algorithm will not realize that these employees are allowed to work these shifts.

* Do your scenario start / end dates fully overlap with the input shifts? For instance, if your shifts are in the range April 1, 2018 - April 15, 2018 but your scenario start / end dates are April 7, 2018 - April 22, 2018 then only the shifts that overlap with the scenario dates will be assigned (April 15 - April 22).

* Is the is_fixed flag set to false for all shifts that you want to be assigned? The agorithm will not touch or update any shifts with is_fixed = true.
