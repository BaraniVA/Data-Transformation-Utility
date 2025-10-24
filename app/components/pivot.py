import reflex as rx
from app.state import State


def column_selector_grid(
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


def pivot_section() -> rx.Component:
    agg_funcs = ["sum", "mean", "count", "min", "max"]
    return rx.el.div(
        rx.el.h3("Pivot Table", class_name="text-xl font-bold text-gray-800 mb-2"),
        rx.el.div(
            rx.el.div(
                rx.el.label(
                    "Index (Rows)", class_name="text-sm font-medium text-gray-600"
                ),
                rx.el.select(
                    rx.el.option("Select Column...", value=""),
                    rx.foreach(
                        State.all_columns, lambda col: rx.el.option(col, value=col)
                    ),
                    value=State.pivot_index,
                    on_change=State.set_pivot_index,
                    class_name="w-full mt-1 px-3 py-2 text-sm border border-gray-300 rounded-lg",
                ),
            ),
            rx.el.div(
                rx.el.label("Columns", class_name="text-sm font-medium text-gray-600"),
                rx.el.select(
                    rx.el.option("Select Column...", value=""),
                    rx.foreach(
                        State.all_columns, lambda col: rx.el.option(col, value=col)
                    ),
                    value=State.pivot_columns,
                    on_change=State.set_pivot_columns,
                    class_name="w-full mt-1 px-3 py-2 text-sm border border-gray-300 rounded-lg",
                ),
            ),
            rx.el.div(
                rx.el.label("Values", class_name="text-sm font-medium text-gray-600"),
                rx.el.select(
                    rx.el.option("Select Column...", value=""),
                    rx.foreach(
                        State.all_columns, lambda col: rx.el.option(col, value=col)
                    ),
                    value=State.pivot_values,
                    on_change=State.set_pivot_values,
                    class_name="w-full mt-1 px-3 py-2 text-sm border border-gray-300 rounded-lg",
                ),
            ),
            rx.el.div(
                rx.el.label(
                    "Aggregation", class_name="text-sm font-medium text-gray-600"
                ),
                rx.el.select(
                    rx.foreach(
                        agg_funcs, lambda f: rx.el.option(f.capitalize(), value=f)
                    ),
                    value=State.pivot_aggfunc,
                    on_change=State.set_pivot_aggfunc,
                    class_name="w-full mt-1 px-3 py-2 text-sm border border-gray-300 rounded-lg",
                ),
            ),
            class_name="grid md:grid-cols-4 gap-4",
        ),
        rx.el.button(
            "Create Pivot Table",
            rx.icon("table-properties", size=16),
            on_click=State.apply_pivot,
            disabled=(State.pivot_index == "")
            | (State.pivot_columns == "")
            | (State.pivot_values == ""),
            class_name="mt-4 w-full flex items-center justify-center gap-2 px-4 py-2 bg-blue-500 text-white font-semibold rounded-lg hover:bg-blue-600 transition-colors shadow-sm disabled:bg-gray-300",
        ),
        class_name="p-6 bg-white border border-gray-200 rounded-xl",
    )


def melt_section() -> rx.Component:
    return rx.el.div(
        rx.el.h3("Melt (Unpivot)", class_name="text-xl font-bold text-gray-800 mb-2"),
        rx.el.div(
            rx.el.div(
                rx.el.label(
                    "ID Variables (columns to keep)",
                    class_name="text-sm font-medium text-gray-600",
                ),
                column_selector_grid(State.melt_id_vars, State.toggle_melt_id_var),
            ),
            rx.el.div(
                rx.el.label(
                    "Value Variables (columns to unpivot)",
                    class_name="text-sm font-medium text-gray-600 mt-4",
                ),
                column_selector_grid(
                    State.melt_value_vars, State.toggle_melt_value_var
                ),
            ),
            class_name="grid md:grid-cols-2 gap-4",
        ),
        rx.el.button(
            "Apply Melt",
            rx.icon("unfold-vertical", size=16),
            on_click=State.apply_melt,
            disabled=(State.melt_id_vars.length() == 0)
            | (State.melt_value_vars.length() == 0),
            class_name="mt-4 w-full flex items-center justify-center gap-2 px-4 py-2 bg-blue-500 text-white font-semibold rounded-lg hover:bg-blue-600 transition-colors shadow-sm disabled:bg-gray-300",
        ),
        class_name="p-6 bg-white border border-gray-200 rounded-xl mt-6",
    )


def groupby_section() -> rx.Component:
    agg_funcs = ["sum", "mean", "count", "min", "max", "first", "last"]
    return rx.el.div(
        rx.el.h3(
            "Group By & Aggregate", class_name="text-xl font-bold text-gray-800 mb-2"
        ),
        rx.el.div(
            rx.el.div(
                rx.el.label(
                    "Group By Columns", class_name="text-sm font-medium text-gray-600"
                ),
                column_selector_grid(
                    State.groupby_columns, State.toggle_groupby_column
                ),
            ),
            rx.el.div(
                rx.el.label(
                    "Aggregation Columns",
                    class_name="text-sm font-medium text-gray-600",
                ),
                column_selector_grid(
                    State.groupby_agg_columns, State.toggle_groupby_agg_column
                ),
            ),
        ),
        rx.el.div(
            rx.el.label(
                "Aggregation Function",
                class_name="text-sm font-medium text-gray-600 mt-4",
            ),
            rx.el.select(
                rx.foreach(agg_funcs, lambda f: rx.el.option(f.capitalize(), value=f)),
                value=State.groupby_aggfunc,
                on_change=State.set_groupby_aggfunc,
                class_name="w-full mt-1 px-3 py-2 text-sm border border-gray-300 rounded-lg",
            ),
        ),
        rx.el.button(
            "Apply GroupBy",
            rx.icon("group", size=16),
            on_click=State.apply_groupby,
            disabled=(State.groupby_columns.length() == 0)
            | (State.groupby_agg_columns.length() == 0),
            class_name="mt-4 w-full flex items-center justify-center gap-2 px-4 py-2 bg-blue-500 text-white font-semibold rounded-lg hover:bg-blue-600 transition-colors shadow-sm disabled:bg-gray-300",
        ),
        class_name="p-6 bg-white border border-gray-200 rounded-xl mt-6",
    )


def pivot_view() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.h2("Pivot & Reshape", class_name="text-2xl font-bold text-gray-800"),
            rx.el.p(
                "Restructure your data with pivot, melt, or groupby operations.",
                class_name="text-gray-500 mt-1",
            ),
            class_name="mb-6 text-center",
        ),
        rx.cond(
            State.all_columns.length() > 0,
            rx.el.div(pivot_section(), melt_section(), groupby_section()),
            rx.el.div(
                rx.icon("table-properties", size=48, class_name="text-gray-400"),
                rx.el.h3(
                    "No Data to Reshape",
                    class_name="mt-4 text-lg font-semibold text-gray-700",
                ),
                rx.el.p(
                    "Upload files to begin reshaping data.",
                    class_name="mt-1 text-sm text-gray-500",
                ),
                class_name="text-center p-10 border-2 border-dashed border-gray-300 rounded-xl bg-gray-50",
            ),
        ),
        class_name="w-full max-w-5xl mx-auto flex flex-col",
    )