import reflex as rx
from app.state import State


def dedup_column_selector(column: str) -> rx.Component:
    """Checkbox for selecting a column for deduplication."""
    return rx.el.label(
        rx.el.input(
            type="checkbox",
            is_checked=State.dedup_columns.contains(column),
            on_change=lambda _: State.toggle_dedup_column(column),
            class_name="size-4 rounded border-gray-300 text-emerald-600 focus:ring-emerald-500",
        ),
        rx.el.span(column, class_name="font-mono text-sm text-gray-700"),
        class_name="flex items-center gap-2 p-2 rounded-md hover:bg-gray-50",
    )


def keep_strategy_radio(value: str, label: str) -> rx.Component:
    """Radio button for selecting the keep strategy."""
    return rx.el.label(
        rx.el.input(
            type="radio",
            name="dedup_keep",
            value=value,
            is_checked=State.dedup_keep == value,
            on_change=lambda: State.set_dedup_keep(value),
            class_name="size-4 border-gray-300 text-emerald-600 focus:ring-emerald-500",
        ),
        rx.el.span(label, class_name="text-sm font-medium text-gray-700"),
        class_name="flex items-center gap-2",
    )


def deduplication_view() -> rx.Component:
    """The view for removing duplicate rows."""
    return rx.el.div(
        rx.el.div(
            rx.el.h2(
                "Data Deduplication", class_name="text-2xl font-bold text-gray-800"
            ),
            rx.el.p(
                "Find and remove duplicate rows based on a set of columns.",
                class_name="text-gray-500 mt-1",
            ),
            class_name="mb-6 text-center",
        ),
        rx.cond(
            State.all_columns.length() > 0,
            rx.el.div(
                rx.el.div(
                    rx.el.h3(
                        "1. Select Columns for Deduplication",
                        class_name="font-semibold text-gray-800 mb-2",
                    ),
                    rx.el.div(
                        rx.foreach(State.all_columns, dedup_column_selector),
                        class_name="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-2 p-4 border border-gray-200 rounded-lg bg-white",
                    ),
                ),
                rx.el.div(
                    rx.el.h3(
                        "2. Choose Strategy",
                        class_name="font-semibold text-gray-800 mb-2",
                    ),
                    rx.el.div(
                        keep_strategy_radio("first", "Keep First Entry"),
                        keep_strategy_radio("last", "Keep Last Entry"),
                        keep_strategy_radio("none", "Remove All Duplicates"),
                        class_name="flex items-center gap-6 p-4 border border-gray-200 rounded-lg bg-white",
                    ),
                    class_name="mt-6",
                ),
                rx.el.div(
                    rx.el.button(
                        "Find Duplicates",
                        rx.icon("search", size=16),
                        on_click=State.find_duplicates,
                        disabled=State.dedup_columns.length() == 0,
                        class_name="w-full flex items-center justify-center gap-2 px-4 py-2 bg-blue-500 text-white font-semibold rounded-lg hover:bg-blue-600 transition-colors shadow-sm disabled:bg-gray-300",
                    ),
                    class_name="mt-6",
                ),
                rx.cond(
                    State.duplicates_found > 0,
                    rx.el.div(
                        rx.icon("square_check", class_name="text-emerald-500"),
                        rx.el.span(f"{State.duplicates_found} duplicate rows found."),
                        rx.el.button(
                            "Remove Duplicates",
                            rx.icon("trash-2", size=16),
                            on_click=State.remove_duplicates,
                            class_name="ml-auto flex items-center justify-center gap-2 px-4 py-2 bg-red-500 text-white font-semibold rounded-lg hover:bg-red-600 transition-colors shadow-sm",
                        ),
                        class_name="flex items-center gap-2 mt-4 text-sm font-medium text-emerald-600 bg-emerald-50 p-3 rounded-lg border border-emerald-200",
                    ),
                    rx.cond(
                        State.duplicates_found == 0,
                        rx.el.div(
                            rx.icon("info", class_name="text-blue-500"),
                            rx.el.span(
                                "No duplicates found based on selected criteria."
                            ),
                            class_name="flex items-center gap-2 mt-4 text-sm font-medium text-blue-600 bg-blue-50 p-3 rounded-lg border border-blue-200",
                        ),
                        None,
                    ),
                ),
            ),
            rx.el.div(
                rx.icon("copy-x", size=48, class_name="text-gray-400"),
                rx.el.h3(
                    "No Data to Process",
                    class_name="mt-4 text-lg font-semibold text-gray-700",
                ),
                rx.el.p(
                    "Upload one or more files to begin deduplication.",
                    class_name="mt-1 text-sm text-gray-500",
                ),
                class_name="text-center p-10 border-2 border-dashed border-gray-300 rounded-xl bg-gray-50",
            ),
        ),
        class_name="w-full max-w-4xl mx-auto flex flex-col",
    )