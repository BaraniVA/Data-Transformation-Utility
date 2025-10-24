import reflex as rx
from app.state import State


def null_overview_section() -> rx.Component:
    """Section to display null value statistics for each column."""
    return rx.el.div(
        rx.el.h3(
            "Null Value Overview", class_name="text-xl font-bold text-gray-800 mb-4"
        ),
        rx.el.button(
            "Refresh Overview",
            rx.icon("refresh-cw", size=14),
            on_click=State.calculate_null_stats,
            class_name="mb-4 flex items-center justify-center gap-2 px-4 py-2 bg-gray-100 text-gray-700 font-semibold rounded-lg hover:bg-gray-200 transition-colors border border-gray-300 text-sm",
        ),
        rx.cond(
            State.null_stats.keys().length() > 0,
            rx.el.div(
                rx.el.div(
                    rx.el.div("Column", class_name="font-semibold w-1/3"),
                    rx.el.div("Null Count", class_name="font-semibold w-1/4"),
                    rx.el.div("Null Percentage", class_name="font-semibold w-2/5"),
                    class_name="flex items-center text-sm text-gray-600 p-2 border-b",
                ),
                rx.foreach(
                    State.null_stats.keys(),
                    lambda col: rx.el.div(
                        rx.el.span(col, class_name="font-mono text-sm w-1/3"),
                        rx.el.span(
                            State.null_stats[col].get("null_count", 0).to_string(),
                            class_name="w-1/4",
                        ),
                        rx.el.div(
                            rx.el.div(
                                class_name="bg-red-200 h-2 rounded-full",
                                style={
                                    "width": f"{(State.null_stats[col].get('null_percentage', 0).to(float) * 100).to_string()}%"
                                },
                            ),
                            class_name="w-full bg-gray-200 rounded-full h-2",
                        ),
                        rx.el.span(
                            f"{(State.null_stats[col].get('null_percentage', 0).to(float) * 100).to_string()}%",
                            class_name="text-xs w-20 text-right",
                        ),
                        class_name="flex items-center p-2 border-b gap-2",
                    ),
                ),
                class_name="bg-white border rounded-lg",
            ),
        ),
        class_name="p-6 bg-white border border-gray-200 rounded-xl",
    )


def fill_null_section() -> rx.Component:
    """Section for filling null values."""
    return rx.el.div(
        rx.el.h3("Fill Null Values", class_name="text-xl font-bold text-gray-800 mb-4"),
        rx.el.div(
            rx.el.div(
                rx.el.label(
                    "Columns to Fill", class_name="text-sm font-medium text-gray-600"
                ),
                rx.el.div(
                    rx.foreach(
                        State.all_columns,
                        lambda col: rx.el.label(
                            rx.el.input(
                                type="checkbox",
                                is_checked=State.fill_columns.contains(col),
                                on_change=lambda _: State.toggle_fill_column(col),
                                class_name="size-4 rounded border-gray-300 text-emerald-600 focus:ring-emerald-500",
                            ),
                            rx.el.span(
                                col, class_name="font-mono text-sm text-gray-700"
                            ),
                            class_name="flex items-center gap-2 p-2 rounded-md hover:bg-gray-50 cursor-pointer",
                        ),
                    ),
                    class_name="grid grid-cols-2 md:grid-cols-4 gap-2 p-4 border rounded-lg bg-gray-50 mt-1",
                ),
            ),
            rx.el.div(
                rx.el.label(
                    "Fill Strategy", class_name="text-sm font-medium text-gray-600"
                ),
                rx.el.select(
                    rx.el.option("Custom Value", value="custom"),
                    rx.el.option("Forward Fill (ffill)", value="ffill"),
                    rx.el.option("Backward Fill (bfill)", value="bfill"),
                    rx.el.option("Mean (numeric only)", value="mean"),
                    rx.el.option("Median (numeric only)", value="median"),
                    rx.el.option("Mode (most frequent)", value="mode"),
                    value=State.fill_strategy,
                    on_change=State.set_fill_strategy,
                    class_name="w-full mt-1 px-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-emerald-500 focus:border-emerald-500",
                ),
            ),
            rx.cond(
                State.fill_strategy == "custom",
                rx.el.div(
                    rx.el.label(
                        "Custom Value", class_name="text-sm font-medium text-gray-600"
                    ),
                    rx.el.input(
                        placeholder="Enter value to fill nulls with...",
                        default_value=State.fill_custom_value,
                        on_change=State.set_fill_custom_value,
                        class_name="w-full mt-1 px-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-emerald-500 focus:border-emerald-500",
                    ),
                ),
                None,
            ),
            rx.el.button(
                "Apply Fill",
                rx.icon("droplets", size=16),
                on_click=State.apply_fill_nulls,
                disabled=State.fill_columns.length() == 0,
                class_name="w-full flex items-center justify-center gap-2 px-4 py-2 bg-blue-500 text-white font-semibold rounded-lg hover:bg-blue-600 transition-colors shadow-sm disabled:bg-gray-300",
            ),
            class_name="space-y-4",
        ),
        class_name="p-6 bg-white border border-gray-200 rounded-xl mt-6",
    )


def remove_nulls_section() -> rx.Component:
    """Section for removing rows or columns with null values."""
    return rx.el.div(
        rx.el.h3("Remove Nulls", class_name="text-xl font-bold text-gray-800 mb-4"),
        rx.el.div(
            rx.el.h4(
                "Remove Rows with Nulls",
                class_name="text-lg font-semibold text-gray-700 mb-2",
            ),
            rx.el.button(
                "Remove Rows with ANY Null Value",
                rx.icon("trash-2", size=16),
                on_click=State.remove_null_rows_any,
                class_name="w-full flex items-center justify-center gap-2 px-4 py-2 bg-red-500 text-white font-semibold rounded-lg hover:bg-red-600 transition-colors shadow-sm mb-4",
            ),
            class_name="space-y-4",
        ),
        class_name="p-6 bg-white border border-gray-200 rounded-xl mt-6",
    )


def null_handling_view() -> rx.Component:
    """The view for handling null values."""
    return rx.el.div(
        rx.el.div(
            rx.el.h2(
                "Null Value Handling", class_name="text-2xl font-bold text-gray-800"
            ),
            rx.el.p(
                "Analyze, fill, or remove missing data from your datasets.",
                class_name="text-gray-500 mt-1",
            ),
            class_name="mb-6 text-center",
        ),
        rx.cond(
            State.all_columns.length() > 0,
            rx.el.div(
                null_overview_section(), fill_null_section(), remove_nulls_section()
            ),
            rx.el.div(
                rx.icon("search-slash", size=48, class_name="text-gray-400"),
                rx.el.h3(
                    "No Data to Process",
                    class_name="mt-4 text-lg font-semibold text-gray-700",
                ),
                rx.el.p(
                    "Upload one or more files to manage null values.",
                    class_name="mt-1 text-sm text-gray-500",
                ),
                class_name="text-center p-10 border-2 border-dashed border-gray-300 rounded-xl bg-gray-50",
            ),
        ),
        class_name="w-full max-w-5xl mx-auto flex flex-col",
    )