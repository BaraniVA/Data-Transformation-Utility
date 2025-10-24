import reflex as rx
from app.state import State


def column_selection_item(column: str, index: int) -> rx.Component:
    """A single row in the column selection/reordering UI."""
    return rx.el.div(
        rx.el.div(
            rx.el.input(
                type="checkbox",
                is_checked=State.selected_columns.contains(column),
                on_change=lambda _: State.toggle_column_selection(column),
                class_name="size-4 rounded border-gray-300 text-emerald-600 focus:ring-emerald-500",
            ),
            rx.el.span(column, class_name="font-mono text-sm text-gray-700"),
            class_name="flex items-center gap-3",
        ),
        rx.el.div(
            rx.el.button(
                rx.icon("arrow-up", size=16),
                on_click=lambda: State.move_column_up(column),
                disabled=index == 0,
                class_name="p-1.5 rounded-md hover:bg-gray-100 disabled:opacity-50 disabled:cursor-not-allowed",
            ),
            rx.el.button(
                rx.icon("arrow-down", size=16),
                on_click=lambda: State.move_column_down(column),
                disabled=index == State.column_order.length() - 1,
                class_name="p-1.5 rounded-md hover:bg-gray-100 disabled:opacity-50 disabled:cursor-not-allowed",
            ),
            class_name="flex items-center gap-1 text-gray-500",
        ),
        class_name="flex items-center justify-between w-full p-3 bg-white border border-gray-200 rounded-lg",
    )


def column_selection_view() -> rx.Component:
    """The view for selecting and reordering columns."""
    return rx.el.div(
        rx.el.div(
            rx.el.h2(
                "Column Selection & Reordering",
                class_name="text-2xl font-bold text-gray-800",
            ),
            rx.el.p(
                "Choose which columns to include and their order for the final output.",
                class_name="text-gray-500 mt-1",
            ),
            class_name="mb-6 text-center",
        ),
        rx.cond(
            State.all_columns.length() > 0,
            rx.el.div(
                rx.el.div(
                    rx.el.button(
                        "Select All",
                        on_click=State.select_all_columns,
                        class_name="px-3 py-1 text-sm font-semibold text-gray-600 bg-gray-100 border border-gray-300 rounded-md hover:bg-gray-200",
                    ),
                    rx.el.button(
                        "Deselect All",
                        on_click=State.deselect_all_columns,
                        class_name="px-3 py-1 text-sm font-semibold text-gray-600 bg-gray-100 border border-gray-300 rounded-md hover:bg-gray-200",
                    ),
                    class_name="flex items-center gap-2 mb-4",
                ),
                rx.el.div(
                    rx.foreach(
                        State.column_order,
                        lambda col, index: column_selection_item(col, index),
                    ),
                    class_name="space-y-2",
                ),
                rx.el.button(
                    "Apply Selection & Order",
                    rx.icon("check_check", size=16),
                    on_click=State.apply_column_selection,
                    class_name="mt-6 w-full flex items-center justify-center gap-2 px-4 py-2 bg-emerald-500 text-white font-semibold rounded-lg hover:bg-emerald-600 transition-colors shadow-sm",
                ),
            ),
            rx.el.div(
                rx.icon("columns-3", size=48, class_name="text-gray-400"),
                rx.el.h3(
                    "No Columns to Select",
                    class_name="mt-4 text-lg font-semibold text-gray-700",
                ),
                rx.el.p(
                    "Upload one or more files to begin managing columns.",
                    class_name="mt-1 text-sm text-gray-500",
                ),
                class_name="text-center p-10 border-2 border-dashed border-gray-300 rounded-xl bg-gray-50",
            ),
        ),
        class_name="w-full max-w-3xl mx-auto flex flex-col",
    )