import reflex as rx
from app.state import State


def component_selector_grid(
    columns_var: rx.Var, on_toggle: rx.event.EventHandler
) -> rx.Component:
    return rx.el.div(
        rx.foreach(
            State.all_columns,
            lambda col: rx.el.label(
                rx.el.input(
                    type="checkbox",
                    is_checked=columns_var.contains(col),
                    on_change=lambda _: on_toggle(col),
                    class_name="size-4 rounded border-gray-300 text-emerald-600 focus:ring-emerald-500",
                ),
                rx.el.span(col, class_name="font-mono text-sm text-gray-700"),
                class_name="flex items-center gap-2 p-2 rounded-md hover:bg-gray-50 cursor-pointer",
            ),
        ),
        class_name="grid grid-cols-2 md:grid-cols-4 gap-2 p-4 border border-gray-200 rounded-lg bg-white mt-2",
    )


def extract_date_components_section() -> rx.Component:
    components = ["year", "month", "day", "weekday", "hour", "minute"]
    return rx.el.div(
        rx.el.h3(
            "Extract Date Components", class_name="text-xl font-bold text-gray-800 mb-2"
        ),
        rx.el.label(
            "Select date columns:", class_name="text-sm font-medium text-gray-600"
        ),
        component_selector_grid(State.datetime_columns, State.toggle_datetime_column),
        rx.el.label(
            "Components to extract:",
            class_name="text-sm font-medium text-gray-600 mt-4",
        ),
        rx.el.div(
            rx.foreach(
                components,
                lambda comp: rx.el.label(
                    rx.el.input(
                        type="checkbox",
                        is_checked=State.extract_components.contains(comp),
                        on_change=lambda _: State.toggle_extract_component(comp),
                        class_name="mr-2",
                    ),
                    comp.capitalize(),
                    class_name="flex items-center text-sm",
                ),
            ),
            class_name="flex flex-wrap gap-4 mt-2",
        ),
        rx.el.button(
            "Extract Components",
            rx.icon("calendar-plus", size=16),
            on_click=State.extract_date_components,
            disabled=State.datetime_columns.length() == 0,
            class_name="mt-4 w-full flex items-center justify-center gap-2 px-4 py-2 bg-blue-500 text-white font-semibold rounded-lg hover:bg-blue-600 transition-colors shadow-sm disabled:bg-gray-300",
        ),
        class_name="p-6 bg-white border border-gray-200 rounded-xl",
    )


def date_difference_section() -> rx.Component:
    return rx.el.div(
        rx.el.h3(
            "Calculate Date Difference",
            class_name="text-xl font-bold text-gray-800 mb-2",
        ),
        rx.el.div(
            rx.el.div(
                rx.el.label(
                    "Start Date Column", class_name="text-sm font-medium text-gray-600"
                ),
                rx.el.select(
                    rx.el.option("Select Column...", value=""),
                    rx.foreach(
                        State.all_columns, lambda col: rx.el.option(col, value=col)
                    ),
                    value=State.date_diff_col1,
                    on_change=State.set_date_diff_col1,
                    class_name="w-full mt-1 px-3 py-2 text-sm border border-gray-300 rounded-lg",
                ),
            ),
            rx.el.div(
                rx.el.label(
                    "End Date Column", class_name="text-sm font-medium text-gray-600"
                ),
                rx.el.select(
                    rx.el.option("Select Column...", value=""),
                    rx.foreach(
                        State.all_columns, lambda col: rx.el.option(col, value=col)
                    ),
                    value=State.date_diff_col2,
                    on_change=State.set_date_diff_col2,
                    class_name="w-full mt-1 px-3 py-2 text-sm border border-gray-300 rounded-lg",
                ),
            ),
            rx.el.div(
                rx.el.label(
                    "New Column Name", class_name="text-sm font-medium text-gray-600"
                ),
                rx.el.input(
                    default_value=State.date_diff_new_col,
                    on_change=State.set_date_diff_new_col,
                    class_name="w-full mt-1 px-3 py-2 text-sm border border-gray-300 rounded-lg",
                ),
            ),
            class_name="grid md:grid-cols-3 gap-4",
        ),
        rx.el.button(
            "Calculate Difference (in days)",
            rx.icon("calendar-clock", size=16),
            on_click=State.calculate_date_difference,
            disabled=(State.date_diff_col1 == "") | (State.date_diff_col2 == ""),
            class_name="mt-4 w-full flex items-center justify-center gap-2 px-4 py-2 bg-blue-500 text-white font-semibold rounded-lg hover:bg-blue-600 transition-colors shadow-sm disabled:bg-gray-300",
        ),
        class_name="p-6 bg-white border border-gray-200 rounded-xl mt-6",
    )


def date_arithmetic_section() -> rx.Component:
    units = ["days", "weeks", "months", "years"]
    return rx.el.div(
        rx.el.h3("Date Arithmetic", class_name="text-xl font-bold text-gray-800 mb-2"),
        rx.el.div(
            rx.el.select(
                rx.el.option("Select Date Column...", value=""),
                rx.foreach(State.all_columns, lambda col: rx.el.option(col, value=col)),
                value=State.date_arith_column,
                on_change=State.set_date_arith_column,
                class_name="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg",
            ),
            rx.el.select(
                rx.el.option("Add", value="add"),
                rx.el.option("Subtract", value="subtract"),
                value=State.date_arith_op,
                on_change=State.set_date_arith_op,
                class_name="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg",
            ),
            rx.el.input(
                type="number",
                default_value=State.date_arith_value.to_string(),
                on_change=State.set_date_arith_value,
                class_name="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg",
            ),
            rx.el.select(
                rx.foreach(
                    units, lambda unit: rx.el.option(unit.capitalize(), value=unit)
                ),
                value=State.date_arith_unit,
                on_change=State.set_date_arith_unit,
                class_name="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg",
            ),
            class_name="grid md:grid-cols-4 gap-4",
        ),
        rx.el.button(
            "Apply Arithmetic",
            rx.icon("calendar-plus-2", size=16),
            on_click=State.apply_date_arithmetic,
            disabled=State.date_arith_column == "",
            class_name="mt-4 w-full flex items-center justify-center gap-2 px-4 py-2 bg-blue-500 text-white font-semibold rounded-lg hover:bg-blue-600 transition-colors shadow-sm disabled:bg-gray-300",
        ),
        class_name="p-6 bg-white border border-gray-200 rounded-xl mt-6",
    )


def datetime_view() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.h2(
                "Date/Time Operations", class_name="text-2xl font-bold text-gray-800"
            ),
            rx.el.p(
                "Perform calculations and transformations on date and time columns.",
                class_name="text-gray-500 mt-1",
            ),
            class_name="mb-6 text-center",
        ),
        rx.cond(
            State.all_columns.length() > 0,
            rx.el.div(
                extract_date_components_section(),
                date_difference_section(),
                date_arithmetic_section(),
            ),
            rx.el.div(
                rx.icon("calendar", size=48, class_name="text-gray-400"),
                rx.el.h3(
                    "No Data to Process",
                    class_name="mt-4 text-lg font-semibold text-gray-700",
                ),
                rx.el.p(
                    "Upload files to begin date/time operations.",
                    class_name="mt-1 text-sm text-gray-500",
                ),
                class_name="text-center p-10 border-2 border-dashed border-gray-300 rounded-xl bg-gray-50",
            ),
        ),
        class_name="w-full max-w-5xl mx-auto flex flex-col",
    )