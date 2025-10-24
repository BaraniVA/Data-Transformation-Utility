import reflex as rx
from app.state import State


def split_column_section() -> rx.Component:
    return rx.el.div(
        rx.el.h3("Split Column", class_name="text-xl font-bold text-gray-800 mb-4"),
        rx.el.div(
            rx.el.div(
                rx.el.label(
                    "Column to Split", class_name="text-sm font-medium text-gray-600"
                ),
                rx.el.select(
                    rx.el.option("Select Column...", value="", disabled=True),
                    rx.foreach(
                        State.all_columns, lambda col: rx.el.option(col, value=col)
                    ),
                    value=State.split_column,
                    on_change=State.set_split_column,
                    class_name="w-full mt-1 px-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-emerald-500 focus:border-emerald-500",
                ),
                class_name="flex-1",
            ),
            rx.el.div(
                rx.el.label(
                    "Delimiter", class_name="text-sm font-medium text-gray-600"
                ),
                rx.el.input(
                    on_change=State.set_split_delimiter,
                    default_value=State.split_delimiter,
                    class_name="w-full mt-1 px-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-emerald-500 focus:border-emerald-500",
                ),
                class_name="w-32",
            ),
            rx.el.div(
                rx.el.label(
                    "New Column Prefix", class_name="text-sm font-medium text-gray-600"
                ),
                rx.el.input(
                    on_change=State.set_split_new_col_prefix,
                    default_value=State.split_new_col_prefix,
                    class_name="w-full mt-1 px-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-emerald-500 focus:border-emerald-500",
                ),
                class_name="flex-1",
            ),
            class_name="flex flex-col md:flex-row gap-4 mb-4",
        ),
        rx.el.button(
            "Apply Split",
            rx.icon("split", size=16),
            on_click=State.apply_split_column,
            disabled=State.split_column == "",
            class_name="w-full flex items-center justify-center gap-2 px-4 py-2 bg-blue-500 text-white font-semibold rounded-lg hover:bg-blue-600 transition-colors shadow-sm disabled:bg-gray-300",
        ),
        class_name="p-6 bg-white border border-gray-200 rounded-xl",
    )


def join_columns_section() -> rx.Component:
    return rx.el.div(
        rx.el.h3("Join Columns", class_name="text-xl font-bold text-gray-800 mb-4"),
        rx.el.div(
            rx.el.label(
                "Columns to Join", class_name="text-sm font-medium text-gray-600 mb-1"
            ),
            rx.el.div(
                rx.foreach(
                    State.all_columns,
                    lambda col: rx.el.label(
                        rx.el.input(
                            type="checkbox",
                            is_checked=State.join_columns.contains(col),
                            on_change=lambda _: State.toggle_join_column(col),
                            class_name="size-4 rounded border-gray-300 text-emerald-600 focus:ring-emerald-500",
                        ),
                        rx.el.span(col, class_name="font-mono text-sm text-gray-700"),
                        class_name="flex items-center gap-2 p-2 rounded-md hover:bg-gray-50 cursor-pointer",
                    ),
                ),
                class_name="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-2 p-4 border rounded-lg bg-gray-50",
            ),
        ),
        rx.el.div(
            rx.el.div(
                rx.el.label(
                    "Separator", class_name="text-sm font-medium text-gray-600"
                ),
                rx.el.input(
                    on_change=State.set_join_separator,
                    default_value=State.join_separator,
                    class_name="w-full mt-1 px-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-emerald-500 focus:border-emerald-500",
                ),
                class_name="w-32",
            ),
            rx.el.div(
                rx.el.label(
                    "New Joined Column Name",
                    class_name="text-sm font-medium text-gray-600",
                ),
                rx.el.input(
                    on_change=State.set_join_new_col_name,
                    default_value=State.join_new_col_name,
                    class_name="w-full mt-1 px-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-emerald-500 focus:border-emerald-500",
                ),
                class_name="flex-1",
            ),
            class_name="flex flex-col md:flex-row gap-4 mt-4",
        ),
        rx.el.button(
            "Apply Join",
            rx.icon("link-2", size=16),
            on_click=State.apply_join_columns,
            disabled=State.join_columns.length() < 2,
            class_name="mt-4 w-full flex items-center justify-center gap-2 px-4 py-2 bg-blue-500 text-white font-semibold rounded-lg hover:bg-blue-600 transition-colors shadow-sm disabled:bg-gray-300",
        ),
        class_name="p-6 bg-white border border-gray-200 rounded-xl mt-6",
    )


def extract_substring_section() -> rx.Component:
    return rx.el.div(
        rx.el.h3(
            "Extract Substring", class_name="text-xl font-bold text-gray-800 mb-4"
        ),
        rx.el.div(
            rx.el.div(
                rx.el.label(
                    "Source Column", class_name="text-sm font-medium text-gray-600"
                ),
                rx.el.select(
                    rx.el.option("Select Column...", value="", disabled=True),
                    rx.foreach(
                        State.all_columns, lambda col: rx.el.option(col, value=col)
                    ),
                    value=State.extract_column,
                    on_change=State.set_extract_column,
                    class_name="w-full mt-1 px-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-emerald-500 focus:border-emerald-500",
                ),
                class_name="flex-1",
            ),
            rx.el.div(
                rx.el.label(
                    "Start Position", class_name="text-sm font-medium text-gray-600"
                ),
                rx.el.input(
                    type="number",
                    on_change=State.set_extract_start_pos,
                    default_value=State.extract_start_pos.to_string(),
                    class_name="w-full mt-1 px-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-emerald-500 focus:border-emerald-500",
                ),
                class_name="w-32",
            ),
            rx.el.div(
                rx.el.label(
                    "End Position (optional)",
                    class_name="text-sm font-medium text-gray-600",
                ),
                rx.el.input(
                    type="number",
                    placeholder="End of string",
                    on_change=State.set_extract_end_pos,
                    default_value=State.extract_end_pos.to_string(),
                    class_name="w-full mt-1 px-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-emerald-500 focus:border-emerald-500",
                ),
                class_name="w-32",
            ),
            rx.el.div(
                rx.el.label(
                    "New Column Name", class_name="text-sm font-medium text-gray-600"
                ),
                rx.el.input(
                    on_change=State.set_extract_new_col_name,
                    default_value=State.extract_new_col_name,
                    class_name="w-full mt-1 px-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-emerald-500 focus:border-emerald-500",
                ),
                class_name="flex-1",
            ),
            class_name="flex flex-col md:flex-row gap-4 mb-4",
        ),
        rx.el.button(
            "Apply Extract",
            rx.icon("scissors", size=16),
            on_click=State.apply_extract_substring,
            disabled=State.extract_column == "",
            class_name="w-full flex items-center justify-center gap-2 px-4 py-2 bg-blue-500 text-white font-semibold rounded-lg hover:bg-blue-600 transition-colors shadow-sm disabled:bg-gray-300",
        ),
        class_name="p-6 bg-white border border-gray-200 rounded-xl mt-6",
    )


def split_join_view() -> rx.Component:
    """The view for splitting and joining columns."""
    return rx.el.div(
        rx.el.div(
            rx.el.h2(
                "Split, Join & Extract", class_name="text-2xl font-bold text-gray-800"
            ),
            rx.el.p(
                "Split a column into multiple columns, join multiple columns into one, or extract substrings.",
                class_name="text-gray-500 mt-1",
            ),
            class_name="mb-6 text-center",
        ),
        rx.cond(
            State.all_columns.length() > 0,
            rx.el.div(
                split_column_section(),
                join_columns_section(),
                extract_substring_section(),
            ),
            rx.el.div(
                rx.icon("split", size=48, class_name="text-gray-400"),
                rx.el.h3(
                    "No Columns to Process",
                    class_name="mt-4 text-lg font-semibold text-gray-700",
                ),
                rx.el.p(
                    "Upload one or more files to begin splitting, joining, or extracting.",
                    class_name="mt-1 text-sm text-gray-500",
                ),
                class_name="text-center p-10 border-2 border-dashed border-gray-300 rounded-xl bg-gray-50",
            ),
        ),
        class_name="w-full max-w-5xl mx-auto flex flex-col",
    )