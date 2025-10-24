import reflex as rx
from app.state import State


def find_and_replace_section() -> rx.Component:
    return rx.el.div(
        rx.el.h3("Find & Replace", class_name="text-xl font-bold text-gray-800 mb-4"),
        rx.el.div(
            rx.el.div(
                rx.el.label(
                    "Column to search", class_name="text-sm font-medium text-gray-600"
                ),
                rx.el.select(
                    rx.el.option("All Columns", value="_all_"),
                    rx.foreach(
                        State.all_columns, lambda col: rx.el.option(col, value=col)
                    ),
                    value=State.find_replace_column,
                    on_change=State.set_find_replace_column,
                    class_name="w-full mt-1 px-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-emerald-500 focus:border-emerald-500",
                ),
                class_name="w-full md:w-1/3",
            ),
            rx.el.div(
                rx.el.label("Find", class_name="text-sm font-medium text-gray-600"),
                rx.el.input(
                    placeholder="Text to find...",
                    on_change=State.set_find_text,
                    default_value=State.find_text,
                    class_name="w-full mt-1 px-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-emerald-500 focus:border-emerald-500",
                ),
                class_name="w-full md:w-1/3",
            ),
            rx.el.div(
                rx.el.label(
                    "Replace with", class_name="text-sm font-medium text-gray-600"
                ),
                rx.el.input(
                    placeholder="Replacement text...",
                    on_change=State.set_replace_text,
                    default_value=State.replace_text,
                    class_name="w-full mt-1 px-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-emerald-500 focus:border-emerald-500",
                ),
                class_name="w-full md:w-1/3",
            ),
            class_name="flex flex-col md:flex-row gap-4 mb-4",
        ),
        rx.el.div(
            rx.el.div(
                rx.el.label(
                    rx.el.input(
                        type="checkbox",
                        on_change=State.set_case_sensitive,
                        is_checked=State.case_sensitive,
                        class_name="mr-2",
                    ),
                    "Case Sensitive",
                    class_name="flex items-center text-sm",
                ),
                rx.el.label(
                    rx.el.input(
                        type="checkbox",
                        on_change=State.set_use_regex,
                        is_checked=State.use_regex,
                        class_name="mr-2",
                    ),
                    "Use Regex",
                    class_name="flex items-center text-sm",
                ),
                class_name="flex gap-4",
            ),
            rx.el.div(
                rx.el.button(
                    "Count Matches",
                    on_click=State.find_matches,
                    class_name="px-3 py-1.5 text-sm font-semibold text-gray-600 bg-gray-100 border border-gray-300 rounded-md hover:bg-gray-200",
                ),
                rx.el.button(
                    "Apply Replacement",
                    rx.icon("replace", size=16),
                    on_click=State.apply_find_replace,
                    class_name="flex items-center gap-2 px-4 py-2 bg-blue-500 text-white font-semibold rounded-lg hover:bg-blue-600 transition-colors shadow-sm",
                ),
                class_name="flex items-center gap-2",
            ),
            class_name="flex items-center justify-between mt-4",
        ),
        rx.cond(
            State.match_count >= 0,
            rx.el.div(
                rx.icon("search", class_name="text-blue-500"),
                rx.el.span(f"Found {State.match_count} matches."),
                class_name="flex items-center gap-2 mt-4 text-sm font-medium text-blue-600 bg-blue-50 p-3 rounded-lg border border-blue-200",
            ),
        ),
        class_name="p-6 bg-white border border-gray-200 rounded-xl",
    )


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
        class_name="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-2 p-4 border border-gray-200 rounded-lg bg-white mt-2",
    )


def case_conversion_section() -> rx.Component:
    return rx.el.div(
        rx.el.h3("Case Conversion", class_name="text-xl font-bold text-gray-800 mb-2"),
        rx.el.label(
            "Select columns to convert:", class_name="text-sm font-medium text-gray-600"
        ),
        column_selector_grid(
            State.case_conversion_columns, State.toggle_case_conversion_column
        ),
        rx.el.div(
            rx.el.select(
                rx.el.option("UPPERCASE", value="upper"),
                rx.el.option("lowercase", value="lower"),
                rx.el.option("Title Case", value="title"),
                rx.el.option("Capitalize", value="capitalize"),
                value=State.case_conversion_type,
                on_change=State.set_case_conversion_type,
                class_name="w-full md:w-1/3 px-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-emerald-500 focus:border-emerald-500",
            ),
            rx.el.button(
                "Apply Case Conversion",
                rx.icon("case-sensitive", size=16),
                on_click=State.apply_case_conversion,
                disabled=State.case_conversion_columns.length() == 0,
                class_name="flex items-center gap-2 px-4 py-2 bg-blue-500 text-white font-semibold rounded-lg hover:bg-blue-600 transition-colors shadow-sm disabled:bg-gray-300",
            ),
            class_name="flex items-center gap-4 mt-4",
        ),
        class_name="p-6 bg-white border border-gray-200 rounded-xl mt-6",
    )


def whitespace_trimming_section() -> rx.Component:
    return rx.el.div(
        rx.el.h3(
            "Whitespace Trimming", class_name="text-xl font-bold text-gray-800 mb-2"
        ),
        rx.el.label(
            "Select columns to trim:", class_name="text-sm font-medium text-gray-600"
        ),
        column_selector_grid(State.whitespace_columns, State.toggle_whitespace_column),
        rx.el.div(
            rx.el.select(
                rx.el.option("Leading & Trailing", value="all"),
                rx.el.option("Leading Only", value="leading"),
                rx.el.option("Trailing Only", value="trailing"),
                rx.el.option("Collapse Multiple Spaces", value="collapse"),
                value=State.whitespace_operation,
                on_change=State.set_whitespace_operation,
                class_name="w-full md:w-1/3 px-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-emerald-500 focus:border-emerald-500",
            ),
            rx.el.button(
                "Apply Whitespace Operation",
                rx.icon("pilcrow", size=16),
                on_click=State.apply_whitespace_operation,
                disabled=State.whitespace_columns.length() == 0,
                class_name="flex items-center gap-2 px-4 py-2 bg-blue-500 text-white font-semibold rounded-lg hover:bg-blue-600 transition-colors shadow-sm disabled:bg-gray-300",
            ),
            class_name="flex items-center gap-4 mt-4",
        ),
        class_name="p-6 bg-white border border-gray-200 rounded-xl mt-6",
    )


def text_ops_view() -> rx.Component:
    """The view for all text operations."""
    return rx.el.div(
        rx.el.div(
            rx.el.h2("Text Operations", class_name="text-2xl font-bold text-gray-800"),
            rx.el.p(
                "Perform powerful find/replace, case conversion, and trimming on your text data.",
                class_name="text-gray-500 mt-1",
            ),
            class_name="mb-6 text-center",
        ),
        rx.cond(
            State.all_columns.length() > 0,
            rx.el.div(
                find_and_replace_section(),
                case_conversion_section(),
                whitespace_trimming_section(),
            ),
            rx.el.div(
                rx.icon("pilcrow", size=48, class_name="text-gray-400"),
                rx.el.h3(
                    "No Text to Process",
                    class_name="mt-4 text-lg font-semibold text-gray-700",
                ),
                rx.el.p(
                    "Upload one or more files to begin text operations.",
                    class_name="mt-1 text-sm text-gray-500",
                ),
                class_name="text-center p-10 border-2 border-dashed border-gray-300 rounded-xl bg-gray-50",
            ),
        ),
        class_name="w-full max-w-5xl mx-auto flex flex-col",
    )