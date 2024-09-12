def onboarding_view():
    onboarding_view = {
        "type": "modal",
        "callback_id": "view-id",
        "submit": {
            "type": "plain_text",
            "text": "Submit",
        },
        "close": {
            "type": "plain_text",
            "text": "Cancel",
        },
        "title": {
            "type": "plain_text",
            "text": "Enter your Details",
        },
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "Welcome to Slack!\n\n*Get started by filling the below details:*"
                }
            },
            {
                "type": "divider"
            },
            {
                "type": "input",
                "element": {
                    "type": "plain_text_input",
                    "action_id": "plain_text_input-action_1",
                    "placeholder": {
                        "type": "plain_text",
                        "text": "First Name"
                    }
                },
                "label": {
                    "type": "plain_text",
                    "text": "Enter your first name"
                }
            },
            {
                "type": "input",
                "element": {
                    "type": "plain_text_input",
                    "action_id": "plain_text_input-action_2",
                    "placeholder": {
                        "type": "plain_text",
                        "text": "Last Name"
                    }
                },
                "label": {
                    "type": "plain_text",
                    "text": "Enter your last name"
                }
            },
            {
                "type": "input",
                "optional": True,
                "element": {
                    "type": "plain_text_input",
                    "multiline": True,
                    "action_id": "plain_text_input-action_3",
                    "placeholder": {
                        "type": "plain_text",
                        "text": "Address"
                    }
                },
                "label": {
                    "type": "plain_text",
                    "text": "Enter you address"
                }
            },
            {
                "type": "input",
                "optional": True,
                "element": {
                    "type": "number_input",
                    "is_decimal_allowed": False,
                    "action_id": "number_input-action_1",
                    "placeholder": {
                        "type": "plain_text",
                        "text": "Contact Number"
                    }
                },
                "label": {
                    "type": "plain_text",
                    "text": "Enter your contact number",
                }
            },
            {
                "type": "input",
                "element": {
                    "type": "email_text_input",
                    "action_id": "email_text_input-action_1",
                    "placeholder": {
                        "type": "plain_text",
                        "text": "Email Addresss"
                    }
                },
                "label": {
                    "type": "plain_text",
                    "text": "Enter your email address",
                }
            },
            {
                "type": "input",
                "optional": True,
                "element": {
                    "type": "datepicker",
                    "action_id": "datepicker-action",
                    "placeholder": {
                        "type": "plain_text",
                        "text": "Select a date"
                    }
                },
                "label": {
                    "type": "plain_text",
                    "text": "Enter your joining date"
                }
            },
            {
                "type": "input",
                "optional": True,
                "element": {
                    "type": "plain_text_input",
                    "action_id": "plain_text_input-action_4",
                    "placeholder": {
                        "type": "plain_text",
                        "text": "Job Level"
                    }
                },
                "label": {
                    "type": "plain_text",
                    "text": "Enter your job level"
                }
            },
            {
                "type": "input",
                "element": {
                    "type": "static_select",
                    "placeholder": {
                        "type": "plain_text",
                        "text": "Select an option (Y/N)"
                    },
                    "options": [
                        {
                            "text": {
                                "type": "plain_text",
                                "text": "No"
                            },
                            "value": "False"
                        },
                        {
                            "text": {
                                "type": "plain_text",
                                "text": "Yes"
                            },
                            "value": "True"
                        }
                    ],
                    "action_id": "static_select-action_1"
                },
                "label": {
                    "type": "plain_text",
                    "text": "Are you a remote employee"
                }
            },
            {
                "type": "input",
                "optional": True,
                "element": {
                    "type": "plain_text_input",
                    "action_id": "plain_text_input-action_5",
                    "placeholder": {
                        "type": "plain_text",
                        "text": "Designation"
                    }
                },
                "label": {
                    "type": "plain_text",
                    "text": "Enter your designation"
                }
            },
            {
                "type": "input",
                "optional": True,
                "element": {
                    "type": "plain_text_input",
                    "action_id": "plain_text_input-action_6",
                    "placeholder": {
                        "type": "plain_text",
                        "text": "Your Skills"
                    }
                },
                "label": {
                    "type": "plain_text",
                    "text": "Enter your skills (comma-separated)"
                }
            }
        ],
    }
    return onboarding_view

def add_skill_view(user_skills):
    add_skill_view={
        "type": "modal",
        "callback_id": "view-id_1",
        "submit": {
            "type": "plain_text",
            "text": "Submit",
        },
        "close": {
            "type": "plain_text",
            "text": "Cancel",
        },
        "title": {
            "type": "plain_text",
            "text": "Add your skills",
        },
        "blocks": [
            {
                "type": "rich_text",
                "elements": [
                    {
                        "type": "rich_text_section",
                        "elements": [
                            {
                                "type": "text",
                                "text": "Your saved skills: ",
                                "style": {
                                    "bold": True
                                }
                            },
                            {
                                "type": "text",
                                "text": f"{user_skills}"
                            }
                        ]
                    }
                ]
            },
            {
                "type": "input",
                "element": {
                    "type": "plain_text_input",
                    "action_id": "plain_text_input-action_6",
                    "placeholder": {
                        "type": "plain_text",
                        "text": "e.g., Python, Java, JavaScript"
                    }
                },
                "label": {
                    "type": "plain_text",
                    "text": "Enter the skills you want to add, separated by commas."
                }
            }
        ],
    }
    return add_skill_view

def delete_skill_view(user_skills):
    delete_skill_view={
        "type": "modal",
        "callback_id": "view-id_2",
        "submit": {
            "type": "plain_text",
            "text": "Submit",
        },
        "close": {
            "type": "plain_text",
            "text": "Cancel",
        },
        "title": {
            "type": "plain_text",
            "text": "Delete your skills",
        },
        "blocks": [
            {
                "type": "rich_text",
                "elements": [
                    {
                        "type": "rich_text_section",
                        "elements": [
                            {
                                "type": "text",
                                "text": "Your saved skills: ",
                                "style": {
                                    "bold": True
                                }
                            },
                            {
                                "type": "text",
                                "text": f"{user_skills}"
                            }
                        ]
                    }
                ]
            },
            {
                "type": "input",
                "element": {
                    "type": "plain_text_input",
                    "action_id": "plain_text_input-action_6",
                    "placeholder": {
                        "type": "plain_text",
                        "text": "e.g., Python, Java, JavaScript"
                    }
                },
                "label": {
                    "type": "plain_text",
                    "text": "Enter the skills you want to delete, separated by commas."
                }
            }
        ],
    }
    return delete_skill_view