import reflex as rx
from app.state import State


def mapping_row(column_name: str) -> rx.Component:
    """A single row in the column mapping UI."""
    return rx.el.div(
        rx.el.div(
            rx.el.span(column_name, class_name="font-mono text-sm text-gray-600"),
            class_name="flex items-center w-1/3",
        ),
        rx.el.div(
            rx.icon("arrow-right", class_name="text-gray-400"),
            class_name="flex justify-center items-center w-1/6",
        ),
        rx.el.div(
            rx.el.input(
                placeholder="Enter new column name...",
                default_value=State.column_mappings.get(column_name, ""),
                on_change=lambda val: State.set_column_mapping(column_name, val),
                class_name="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-emerald-500 focus:border-emerald-500 transition-shadow",
            ),
            class_name="w-1/2",
        ),
        class_name="flex items-center justify-between w-full p-3 bg-white border border-gray-200 rounded-lg",
    )


def mapping_view() -> rx.Component:
    """The view for mapping columns."""
    return rx.el.div(
        rx.el.div(
            rx.el.h2("Column Mapping", class_name="text-2xl font-bold text-gray-800"),
            rx.el.p(
                "Rename columns to a standardized format. Leave fields blank to keep original names.",
                class_name="text-gray-500 mt-1",
            ),
            class_name="mb-6 text-center",
        ),
        rx.cond(
            State.all_columns.length() > 0,
            rx.el.div(
                rx.el.div(
                    rx.el.div(
                        "Original Column",
                        class_name="font-semibold text-gray-700 w-1/3",
                    ),
                    rx.el.div(
                        "New Column",
                        class_name="font-semibold text-gray-700 w-1/2 text-left pl-2",
                    ),
                    class_name="flex items-center justify-between w-full px-3 mb-2",
                ),
                rx.el.div(
                    rx.foreach(State.all_columns, mapping_row), class_name="space-y-2"
                ),
                rx.el.button(
                    "Apply Mapping",
                    rx.icon("check_check", size=16),
                    on_click=State.apply_column_mapping,
                    class_name="mt-6 w-full flex items-center justify-center gap-2 px-4 py-2 bg-emerald-500 text-white font-semibold rounded-lg hover:bg-emerald-600 transition-colors shadow-sm disabled:bg-gray-300",
                    disabled=State.column_mappings.keys().length() == 0,
                ),
            ),
            rx.el.div(
                rx.icon("folder-search", size=48, class_name="text-gray-400"),
                rx.el.h3(
                    "No Columns to Map",
                    class_name="mt-4 text-lg font-semibold text-gray-700",
                ),
                rx.el.p(
                    "Upload one or more files to begin mapping columns.",
                    class_name="mt-1 text-sm text-gray-500",
                ),
                class_name="text-center p-10 border-2 border-dashed border-gray-300 rounded-xl bg-gray-50",
            ),
        ),
        class_name="w-full max-w-3xl mx-auto flex flex-col",
    )