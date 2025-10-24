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


def label_encoding_section() -> rx.Component:
    return rx.el.div(
        rx.el.h3("Label Encoding", class_name="text-xl font-bold text-gray-800 mb-2"),
        rx.el.p(
            "Convert categorical text data into integer labels.",
            class_name="text-sm text-gray-500 mb-2",
        ),
        rx.el.label(
            "Select columns to encode:", class_name="text-sm font-medium text-gray-600"
        ),
        column_selector_grid(
            State.label_encode_columns, State.toggle_label_encode_column
        ),
        rx.el.button(
            "Apply Label Encoding",
            rx.icon("tags", size=16),
            on_click=State.apply_label_encoding,
            disabled=State.label_encode_columns.length() == 0,
            class_name="mt-4 w-full flex items-center justify-center gap-2 px-4 py-2 bg-blue-500 text-white font-semibold rounded-lg hover:bg-blue-600 transition-colors shadow-sm disabled:bg-gray-300",
        ),
        rx.cond(
            State.label_mappings.keys().length() > 0,
            rx.el.div(
                rx.el.h4("Generated Mappings", class_name="text-lg font-semibold mt-4"),
                rx.foreach(
                    State.label_mappings.keys(),
                    lambda col: rx.el.div(
                        rx.el.h5(col, class_name="font-mono font-bold mt-2"),
                        rx.el.div(
                            rx.foreach(
                                State.label_mappings[col].to_string().split(","),
                                lambda item: rx.el.div(
                                    rx.el.span(
                                        item.split(":")[0]
                                        .replace('"', "")
                                        .replace("{", "")
                                    ),
                                    rx.el.span(item.split(":")[1].replace("}", "")),
                                    class_name="flex justify-between text-sm p-1",
                                ),
                            ),
                            class_name="border p-2 rounded-md bg-gray-50",
                        ),
                    ),
                ),
                class_name="mt-4",
            ),
        ),
        class_name="p-6 bg-white border border-gray-200 rounded-xl",
    )


def one_hot_encoding_section() -> rx.Component:
    return rx.el.div(
        rx.el.h3("One-Hot Encoding", class_name="text-xl font-bold text-gray-800 mb-2"),
        rx.el.p(
            "Create new binary (0/1) columns for each category in a column.",
            class_name="text-sm text-gray-500 mb-2",
        ),
        rx.el.label(
            "Select columns to encode:", class_name="text-sm font-medium text-gray-600"
        ),
        column_selector_grid(State.onehot_columns, State.toggle_onehot_column),
        rx.el.button(
            "Apply One-Hot Encoding",
            rx.icon("binary", size=16),
            on_click=State.apply_onehot_encoding,
            disabled=State.onehot_columns.length() == 0,
            class_name="mt-4 w-full flex items-center justify-center gap-2 px-4 py-2 bg-blue-500 text-white font-semibold rounded-lg hover:bg-blue-600 transition-colors shadow-sm disabled:bg-gray-300",
        ),
        class_name="p-6 bg-white border border-gray-200 rounded-xl mt-6",
    )


def special_chars_section() -> rx.Component:
    return rx.el.div(
        rx.el.h3(
            "Remove Special Characters",
            class_name="text-xl font-bold text-gray-800 mb-2",
        ),
        rx.el.label(
            "Select columns to clean:", class_name="text-sm font-medium text-gray-600"
        ),
        column_selector_grid(
            State.remove_special_columns, State.toggle_remove_special_column
        ),
        rx.el.div(
            rx.el.label(
                "Regex pattern for characters to remove",
                class_name="text-sm font-medium text-gray-600 mt-4",
            ),
            rx.el.input(
                default_value=State.special_char_pattern,
                on_change=State.set_special_char_pattern,
                class_name="w-full font-mono mt-1 px-3 py-2 text-sm border border-gray-300 rounded-lg",
            ),
        ),
        rx.el.button(
            "Remove Special Characters",
            rx.icon("eraser", size=16),
            on_click=State.apply_remove_special_chars,
            disabled=State.remove_special_columns.length() == 0,
            class_name="mt-4 w-full flex items-center justify-center gap-2 px-4 py-2 bg-blue-500 text-white font-semibold rounded-lg hover:bg-blue-600 transition-colors shadow-sm disabled:bg-gray-300",
        ),
        class_name="p-6 bg-white border border-gray-200 rounded-xl mt-6",
    )


def encoding_view() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.h2(
                "Encoding & Advanced Text",
                class_name="text-2xl font-bold text-gray-800",
            ),
            rx.el.p(
                "Prepare data for machine learning or advanced analysis.",
                class_name="text-gray-500 mt-1",
            ),
            class_name="mb-6 text-center",
        ),
        rx.cond(
            State.all_columns.length() > 0,
            rx.el.div(
                label_encoding_section(),
                one_hot_encoding_section(),
                special_chars_section(),
            ),
            rx.el.div(
                rx.icon("binary", size=48, class_name="text-gray-400"),
                rx.el.h3(
                    "No Data to Encode",
                    class_name="mt-4 text-lg font-semibold text-gray-700",
                ),
                rx.el.p(
                    "Upload files to begin encoding data.",
                    class_name="mt-1 text-sm text-gray-500",
                ),
                class_name="text-center p-10 border-2 border-dashed border-gray-300 rounded-xl bg-gray-50",
            ),
        ),
        class_name="w-full max-w-5xl mx-auto flex flex-col",
    )