import reflex as rx
from app.state import State, ConditionalRule


def conditional_rule_editor(rule: ConditionalRule) -> rx.Component:
    condition_ops = {
        "equals": "Equals",
        "not_equals": "Not Equals",
        "contains": "Contains",
        "greater_than": "Greater Than (>)",
        "less_than": "Less Than (<)",
    }
    action_types = {"set_value": "Set Value", "copy_from_column": "Copy from Column"}
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                rx.el.p("IF", class_name="font-bold text-gray-600"),
                rx.el.select(
                    rx.el.option("Select Column...", value=""),
                    rx.foreach(
                        State.all_columns, lambda col: rx.el.option(col, value=col)
                    ),
                    value=rule["condition_column"],
                    on_change=lambda val: State.update_conditional_rule(
                        rule["id"], "condition_column", val
                    ),
                    class_name="w-full px-2 py-1 text-sm border-gray-300 rounded-md",
                ),
                rx.el.select(
                    rx.foreach(
                        list(condition_ops.items()),
                        lambda op: rx.el.option(op[1], value=op[0]),
                    ),
                    value=rule["condition_op"],
                    on_change=lambda val: State.update_conditional_rule(
                        rule["id"], "condition_op", val
                    ),
                    class_name="w-full px-2 py-1 text-sm border-gray-300 rounded-md",
                ),
                rx.el.input(
                    placeholder="Value",
                    default_value=rule["condition_value"],
                    on_change=lambda val: State.update_conditional_rule(
                        rule["id"], "condition_value", val
                    ),
                    class_name="w-full px-2 py-1 text-sm border-gray-300 rounded-md",
                ),
                class_name="flex items-center gap-2",
            ),
            rx.el.div(
                rx.el.p("THEN", class_name="font-bold text-gray-600"),
                rx.el.select(
                    rx.foreach(
                        list(action_types.items()),
                        lambda op: rx.el.option(op[1], value=op[0]),
                    ),
                    value=rule["action"],
                    on_change=lambda val: State.update_conditional_rule(
                        rule["id"], "action", val
                    ),
                    class_name="w-full px-2 py-1 text-sm border-gray-300 rounded-md",
                ),
                rx.el.select(
                    rx.el.option("Target Column...", value=""),
                    rx.foreach(
                        State.all_columns, lambda col: rx.el.option(col, value=col)
                    ),
                    value=rule["target_column"],
                    on_change=lambda val: State.update_conditional_rule(
                        rule["id"], "target_column", val
                    ),
                    class_name="w-full px-2 py-1 text-sm border-gray-300 rounded-md",
                ),
                rx.cond(
                    rule["action"] == "set_value",
                    rx.el.input(
                        placeholder="Action Value",
                        default_value=rule["action_value"],
                        on_change=lambda val: State.update_conditional_rule(
                            rule["id"], "action_value", val
                        ),
                        class_name="w-full px-2 py-1 text-sm border-gray-300 rounded-md",
                    ),
                    rx.el.select(
                        rx.el.option("Source Column...", value=""),
                        rx.foreach(
                            State.all_columns, lambda col: rx.el.option(col, value=col)
                        ),
                        value=rule["action_value"],
                        on_change=lambda val: State.update_conditional_rule(
                            rule["id"], "action_value", val
                        ),
                        class_name="w-full px-2 py-1 text-sm border-gray-300 rounded-md",
                    ),
                ),
                class_name="flex items-center gap-2 mt-2",
            ),
            class_name="flex-1",
        ),
        rx.el.button(
            rx.icon("trash-2", size=16),
            on_click=lambda: State.remove_conditional_rule(rule["id"]),
            class_name="p-2 text-gray-500 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors",
        ),
        class_name="flex items-start gap-4 w-full p-4 bg-white border border-gray-200 rounded-lg",
    )


def conditional_transform_view() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.h2(
                "Conditional Transformation",
                class_name="text-2xl font-bold text-gray-800",
            ),
            rx.el.p(
                "Apply transformations to rows based on IF-THEN logic.",
                class_name="text-gray-500 mt-1",
            ),
            class_name="mb-6 text-center",
        ),
        rx.cond(
            State.all_columns.length() > 0,
            rx.el.div(
                rx.el.div(
                    rx.foreach(State.conditional_rules, conditional_rule_editor),
                    class_name="space-y-3",
                ),
                rx.el.button(
                    "Add Rule",
                    rx.icon("circle_plus", size=16),
                    on_click=State.add_conditional_rule,
                    class_name="mt-4 w-full flex items-center justify-center gap-2 px-4 py-2 bg-gray-100 text-gray-700 font-semibold rounded-lg hover:bg-gray-200 transition-colors border border-gray-300",
                ),
                rx.el.button(
                    "Apply Conditional Transforms",
                    rx.icon("git-fork", size=16),
                    on_click=State.apply_conditional_transforms,
                    class_name="mt-6 w-full flex items-center justify-center gap-2 px-4 py-2 bg-emerald-500 text-white font-semibold rounded-lg hover:bg-emerald-600 transition-colors shadow-sm disabled:bg-gray-300",
                    disabled=State.conditional_rules.length() == 0,
                ),
            ),
            rx.el.div(
                rx.icon("git-fork", size=48, class_name="text-gray-400"),
                rx.el.h3(
                    "No Data to Transform",
                    class_name="mt-4 text-lg font-semibold text-gray-700",
                ),
                rx.el.p(
                    "Upload files to begin creating conditional rules.",
                    class_name="mt-1 text-sm text-gray-500",
                ),
                class_name="text-center p-10 border-2 border-dashed border-gray-300 rounded-xl bg-gray-50",
            ),
        ),
        class_name="w-full max-w-4xl mx-auto flex flex-col",
    )