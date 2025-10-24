import reflex as rx
from app.state import State, FilterRule


def filter_rule_editor(rule: FilterRule) -> rx.Component:
    """A component to edit a single filter rule."""
    operations = {
        "equals": "Equals",
        "not_equals": "Not Equals",
        "contains": "Contains",
        "not_contains": "Not Contains",
        "is_empty": "Is Empty",
        "is_not_empty": "Is Not Empty",
        "greater_than": "Greater Than (>)",
        "less_than": "Less Than (<)",
        "ge": "Greater or Equal (>=)",
        "le": "Less or Equal (<=)",
    }
    return rx.el.div(
        rx.el.div(
            rx.el.select(
                rx.el.option("Select Column...", value="", disabled=True),
                rx.foreach(State.all_columns, lambda col: rx.el.option(col, value=col)),
                value=rule["column"],
                on_change=lambda val: State.update_filter_rule(
                    rule["id"], "column", val
                ),
                class_name="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-emerald-500 focus:border-emerald-500",
            ),
            class_name="w-2/5",
        ),
        rx.el.div(
            rx.el.select(
                rx.foreach(
                    list(operations.items()),
                    lambda op: rx.el.option(op[1], value=op[0]),
                ),
                value=rule["operation"],
                on_change=lambda val: State.update_filter_rule(
                    rule["id"], "operation", val
                ),
                class_name="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-emerald-500 focus:border-emerald-500",
            ),
            class_name="w-1/4",
        ),
        rx.el.div(
            rx.cond(
                (rule["operation"] != "is_empty")
                & (rule["operation"] != "is_not_empty"),
                rx.el.input(
                    placeholder="Enter value...",
                    on_change=lambda val: State.update_filter_rule(
                        rule["id"], "value", val
                    ),
                    class_name="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-emerald-500 focus:border-emerald-500",
                    default_value=rule["value"],
                ),
                rx.el.div(class_name="h-10"),
            ),
            class_name="w-1/4",
        ),
        rx.el.button(
            rx.icon("trash-2", size=16),
            on_click=lambda: State.remove_filter_rule(rule["id"]),
            class_name="p-2 text-gray-500 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors",
        ),
        class_name="flex items-center gap-2 w-full p-3 bg-white border border-gray-200 rounded-lg",
    )


def filter_view() -> rx.Component:
    """The view for filtering and cleaning data."""
    return rx.el.div(
        rx.el.div(
            rx.el.h2("Filter & Cleanup", class_name="text-2xl font-bold text-gray-800"),
            rx.el.p(
                "Define rules to include or exclude rows from your datasets.",
                class_name="text-gray-500 mt-1",
            ),
            class_name="mb-6 text-center",
        ),
        rx.cond(
            State.all_columns.length() > 0,
            rx.el.div(
                rx.el.div(
                    rx.foreach(State.filter_rules, filter_rule_editor),
                    class_name="space-y-2",
                ),
                rx.el.button(
                    "Add Filter Rule",
                    rx.icon("circle_plus", size=16),
                    on_click=State.add_filter_rule,
                    class_name="mt-4 w-full flex items-center justify-center gap-2 px-4 py-2 bg-gray-100 text-gray-700 font-semibold rounded-lg hover:bg-gray-200 transition-colors border border-gray-300",
                ),
                rx.cond(
                    State.rows_removed > 0,
                    rx.el.div(
                        rx.icon("square_check", class_name="text-emerald-500"),
                        rx.el.span(f"{State.rows_removed} rows were removed."),
                        class_name="flex items-center gap-2 mt-4 text-sm font-medium text-emerald-600 bg-emerald-50 p-3 rounded-lg border border-emerald-200",
                    ),
                    None,
                ),
                rx.el.button(
                    "Apply Filters",
                    rx.icon("blinds", size=16),
                    on_click=State.apply_filters,
                    class_name="mt-6 w-full flex items-center justify-center gap-2 px-4 py-2 bg-emerald-500 text-white font-semibold rounded-lg hover:bg-emerald-600 transition-colors shadow-sm disabled:bg-gray-300",
                    disabled=State.filter_rules.length() == 0,
                ),
            ),
            rx.el.div(
                rx.icon("folder-search", size=48, class_name="text-gray-400"),
                rx.el.h3(
                    "No Data to Filter",
                    class_name="mt-4 text-lg font-semibold text-gray-700",
                ),
                rx.el.p(
                    "Upload one or more files to begin filtering data.",
                    class_name="mt-1 text-sm text-gray-500",
                ),
                class_name="text-center p-10 border-2 border-dashed border-gray-300 rounded-xl bg-gray-50",
            ),
        ),
        class_name="w-full max-w-4xl mx-auto flex flex-col",
    )