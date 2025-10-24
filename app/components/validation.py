import reflex as rx
from app.state import State, ValidationRule


def validation_rule_editor(rule: ValidationRule) -> rx.Component:
    """A component to edit a single validation rule."""
    rule_types = {
        "required": "Is Required",
        "min_length": "Min Length",
        "max_length": "Max Length",
        "numeric_range": "Numeric Range",
        "regex_pattern": "Regex Pattern",
    }
    return rx.el.div(
        rx.el.select(
            rx.el.option("Select Column...", value="", disabled=True),
            rx.foreach(State.all_columns, lambda col: rx.el.option(col, value=col)),
            value=rule["column"],
            on_change=lambda val: State.update_validation_rule(
                rule["id"], "column", val
            ),
            class_name="w-1/3 px-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-emerald-500 focus:border-emerald-500",
        ),
        rx.el.select(
            rx.foreach(
                list(rule_types.items()), lambda op: rx.el.option(op[1], value=op[0])
            ),
            value=rule["rule_type"],
            on_change=lambda val: State.update_validation_rule(
                rule["id"], "rule_type", val
            ),
            class_name="w-1/4 px-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-emerald-500 focus:border-emerald-500",
        ),
        rx.el.div(
            rx.match(
                rule["rule_type"],
                (
                    "min_length",
                    rx.el.input(
                        placeholder="Min chars",
                        default_value=rule["param1"],
                        on_change=lambda val: State.update_validation_rule(
                            rule["id"], "param1", val
                        ),
                        class_name="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg",
                    ),
                ),
                (
                    "max_length",
                    rx.el.input(
                        placeholder="Max chars",
                        default_value=rule["param1"],
                        on_change=lambda val: State.update_validation_rule(
                            rule["id"], "param1", val
                        ),
                        class_name="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg",
                    ),
                ),
                (
                    "numeric_range",
                    rx.el.div(
                        rx.el.input(
                            placeholder="Min value",
                            default_value=rule["param1"],
                            on_change=lambda val: State.update_validation_rule(
                                rule["id"], "param1", val
                            ),
                            class_name="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg",
                        ),
                        rx.el.input(
                            placeholder="Max value",
                            default_value=rule["param2"],
                            on_change=lambda val: State.update_validation_rule(
                                rule["id"], "param2", val
                            ),
                            class_name="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg",
                        ),
                        class_name="flex gap-2",
                    ),
                ),
                (
                    "regex_pattern",
                    rx.el.input(
                        placeholder="Regex pattern",
                        default_value=rule["param1"],
                        on_change=lambda val: State.update_validation_rule(
                            rule["id"], "param1", val
                        ),
                        class_name="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg font-mono",
                    ),
                ),
                rx.el.div(),
            ),
            class_name="w-1/3",
        ),
        rx.el.button(
            rx.icon("trash-2", size=16),
            on_click=lambda: State.remove_validation_rule(rule["id"]),
            class_name="p-2 text-gray-500 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors",
        ),
        class_name="flex items-center gap-2 w-full p-3 bg-white border border-gray-200 rounded-lg",
    )


def validation_results_view() -> rx.Component:
    """Component to display the results of the validation."""
    return rx.el.div(
        rx.el.div(
            rx.el.h3(
                "Validation Results", class_name="text-xl font-semibold text-gray-800"
            ),
            rx.el.button(
                "Run Again",
                rx.icon("refresh-cw", size=14),
                on_click=State.run_validation,
                class_name="flex items-center gap-2 px-3 py-1 bg-gray-100 text-gray-700 font-semibold rounded-lg hover:bg-gray-200 text-sm",
            ),
            class_name="flex items-center justify-between mb-4",
        ),
        rx.el.div(
            rx.el.div(
                rx.el.p("Total Rows Validated", class_name="text-sm text-gray-500"),
                rx.el.p(
                    State.validation_results.get("total_rows", 0).to_string(),
                    class_name="text-2xl font-bold text-gray-800",
                ),
                class_name="p-4 bg-white border border-gray-200 rounded-lg text-center",
            ),
            rx.el.div(
                rx.el.p("Passing Rows", class_name="text-sm text-green-600"),
                rx.el.p(
                    State.validation_results.get("passing_rows", 0).to_string(),
                    class_name="text-2xl font-bold text-green-700",
                ),
                class_name="p-4 bg-green-50 border border-green-200 rounded-lg text-center",
            ),
            rx.el.div(
                rx.el.p("Failing Rows", class_name="text-sm text-red-600"),
                rx.el.p(
                    State.validation_results.get("failing_rows", 0).to_string(),
                    class_name="text-2xl font-bold text-red-700",
                ),
                class_name="p-4 bg-red-50 border border-red-200 rounded-lg text-center",
            ),
            class_name="flex items-center justify-between mb-4",
        ),
        rx.cond(
            State.validation_results.get("failing_rows", 0).to(int) > 0,
            rx.el.div(
                rx.el.h4(
                    "Error Details",
                    class_name="text-lg font-semibold text-gray-800 mb-2",
                ),
                rx.el.div(
                    rx.foreach(
                        State.validation_results.get("error_details", {})
                        .to_string()
                        .split(","),
                        lambda item: rx.el.div(
                            rx.el.span(
                                item.split(":")[0].replace('"', "").replace("{", ""),
                                class_name="font-mono text-sm text-gray-600",
                            ),
                            rx.el.span(
                                item.split(":")[1].replace("}", ""),
                                class_name="font-semibold text-red-600 bg-red-100 px-2 py-0.5 rounded-md",
                            ),
                            class_name="flex justify-between items-center p-2 border-b",
                        ),
                    ),
                    class_name="bg-white border rounded-lg p-2",
                ),
                rx.el.button(
                    "Remove All Invalid Rows",
                    rx.icon("trash", size=16),
                    on_click=State.remove_invalid_rows,
                    class_name="mt-6 w-full flex items-center justify-center gap-2 px-4 py-2 bg-red-500 text-white font-semibold rounded-lg hover:bg-red-600 transition-colors shadow-sm",
                ),
            ),
        ),
        class_name="mt-8",
    )


def validation_view() -> rx.Component:
    """The view for creating and running data validation rules."""
    return rx.el.div(
        rx.el.div(
            rx.el.h2("Data Validation", class_name="text-2xl font-bold text-gray-800"),
            rx.el.p(
                "Define rules to ensure your data meets quality standards.",
                class_name="text-gray-500 mt-1",
            ),
            class_name="mb-6 text-center",
        ),
        rx.cond(
            State.show_validation_results,
            validation_results_view(),
            rx.cond(
                State.all_columns.length() > 0,
                rx.el.div(
                    rx.el.div(
                        rx.foreach(State.validation_rules, validation_rule_editor),
                        class_name="space-y-2",
                    ),
                    rx.el.button(
                        "Add Validation Rule",
                        rx.icon("circle_plus", size=16),
                        on_click=State.add_validation_rule,
                        class_name="mt-4 w-full flex items-center justify-center gap-2 px-4 py-2 bg-gray-100 text-gray-700 font-semibold rounded-lg hover:bg-gray-200 transition-colors border border-gray-300",
                    ),
                    rx.el.button(
                        "Run Validation",
                        rx.icon("play", size=16),
                        on_click=State.run_validation,
                        class_name="mt-6 w-full flex items-center justify-center gap-2 px-4 py-2 bg-emerald-500 text-white font-semibold rounded-lg hover:bg-emerald-600 transition-colors shadow-sm disabled:bg-gray-300",
                        disabled=State.validation_rules.length() == 0,
                    ),
                ),
                rx.el.div(
                    rx.icon("shield_check", size=48, class_name="text-gray-400"),
                    rx.el.h3(
                        "No Data to Validate",
                        class_name="mt-4 text-lg font-semibold text-gray-700",
                    ),
                    rx.el.p(
                        "Upload one or more files to begin validating data.",
                        class_name="mt-1 text-sm text-gray-500",
                    ),
                    class_name="text-center p-10 border-2 border-dashed border-gray-300 rounded-xl bg-gray-50",
                ),
            ),
        ),
        class_name="w-full max-w-4xl mx-auto flex flex-col",
    )