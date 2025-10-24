import reflex as rx
from app.state import State


def data_type_row(column_name: str) -> rx.Component:
    """A single row in the data type conversion UI."""
    data_types = {
        "string": "Text (String)",
        "integer": "Integer",
        "float": "Decimal (Float)",
        "boolean": "True/False (Boolean)",
        "date": "Date/Time",
    }
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
            rx.el.select(
                rx.el.option("Select Type...", value=""),
                rx.foreach(
                    list(data_types.items()),
                    lambda op: rx.el.option(op[1], value=op[0]),
                ),
                default_value=State.data_type_mappings.get(column_name, ""),
                on_change=lambda val: State.set_data_type_mapping(column_name, val),
                class_name="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-emerald-500 focus:border-emerald-500 transition-shadow",
            ),
            class_name="w-1/2",
        ),
        class_name="flex items-center justify-between w-full p-3 bg-white border border-gray-200 rounded-lg",
    )


def data_types_view() -> rx.Component:
    """The view for converting column data types."""
    return rx.el.div(
        rx.el.div(
            rx.el.h2(
                "Data Type Conversion", class_name="text-2xl font-bold text-gray-800"
            ),
            rx.el.p(
                "Convert columns to a specific data type. Incompatible values will become null.",
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
                        "New Data Type",
                        class_name="font-semibold text-gray-700 w-1/2 text-left pl-2",
                    ),
                    class_name="flex items-center justify-between w-full px-3 mb-2",
                ),
                rx.el.div(
                    rx.foreach(State.all_columns, data_type_row), class_name="space-y-2"
                ),
                rx.el.button(
                    "Apply Conversions",
                    rx.icon("check_check", size=16),
                    on_click=State.apply_data_type_conversions,
                    class_name="mt-6 w-full flex items-center justify-center gap-2 px-4 py-2 bg-emerald-500 text-white font-semibold rounded-lg hover:bg-emerald-600 transition-colors shadow-sm disabled:bg-gray-300",
                    disabled=State.data_type_mappings.keys().length() == 0,
                ),
            ),
            rx.el.div(
                rx.icon("type", size=48, class_name="text-gray-400"),
                rx.el.h3(
                    "No Columns to Convert",
                    class_name="mt-4 text-lg font-semibold text-gray-700",
                ),
                rx.el.p(
                    "Upload one or more files to begin converting data types.",
                    class_name="mt-1 text-sm text-gray-500",
                ),
                class_name="text-center p-10 border-2 border-dashed border-gray-300 rounded-xl bg-gray-50",
            ),
        ),
        class_name="w-full max-w-3xl mx-auto flex flex-col",
    )