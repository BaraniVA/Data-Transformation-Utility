import reflex as rx
from app.state import State


def stat_item(label: str, value: rx.Var) -> rx.Component:
    return rx.el.div(
        rx.el.span(label, class_name="text-xs text-gray-500"),
        rx.el.span(value, class_name="text-sm font-semibold text-gray-800"),
        class_name="flex flex-col",
    )


def profiling_card(column_name: str, profile_data: rx.Var) -> rx.Component:
    """Card to display profiling statistics for a single column."""
    completeness = (1 - profile_data.get("null_percentage", 0).to(float)) * 100
    return rx.el.div(
        rx.el.div(
            rx.el.h4(
                column_name, class_name="font-mono text-md font-bold text-gray-800"
            ),
            rx.el.span(
                profile_data.get("dtype", "N/A"),
                class_name="text-xs font-medium bg-gray-100 text-gray-600 px-2 py-0.5 rounded-full",
            ),
            class_name="flex items-center justify-between pb-2 border-b border-gray-200",
        ),
        rx.el.div(
            rx.el.div(
                rx.el.div(class_name="w-full bg-gray-200 rounded-full h-1.5"),
                rx.el.div(
                    class_name="bg-emerald-500 h-1.5 rounded-full",
                    style={"width": f"{completeness.to_string()}%"},
                ),
                class_name="relative w-full",
            ),
            rx.el.span(
                f"{completeness.to_string()}% complete",
                class_name="text-xs text-gray-500",
            ),
            class_name="flex items-center gap-2 mt-3",
        ),
        rx.el.div(
            stat_item("Total Rows", profile_data.get("count", 0).to_string()),
            stat_item("Unique Values", profile_data.get("unique", 0).to_string()),
            stat_item("Null Values", profile_data.get("null_count", 0).to_string()),
            class_name="grid grid-cols-3 gap-2 mt-3 pt-3 border-t border-gray-200",
        ),
        rx.cond(
            profile_data.get("dtype", "").to(str).contains("int")
            | profile_data.get("dtype", "").to(str).contains("float"),
            rx.el.div(
                stat_item("Min", profile_data.get("min", "N/A").to_string()),
                stat_item("Mean", profile_data.get("mean", "N/A").to_string()),
                stat_item("Max", profile_data.get("max", "N/A").to_string()),
                class_name="grid grid-cols-3 gap-2 mt-2 pt-2 border-t border-gray-200/60",
            ),
            None,
        ),
        rx.cond(
            profile_data.get("dtype", "").to(str) == "object",
            rx.el.div(
                stat_item("Min Length", profile_data.get("min_len", "N/A").to_string()),
                stat_item("Max Length", profile_data.get("max_len", "N/A").to_string()),
                class_name="grid grid-cols-2 gap-2 mt-2 pt-2 border-t border-gray-200/60",
            ),
            None,
        ),
        class_name="p-4 bg-white border border-gray-200 rounded-xl shadow-sm",
    )


def profiling_view() -> rx.Component:
    """The view for displaying data profiling statistics."""
    return rx.el.div(
        rx.el.div(
            rx.el.h2("Data Profiling", class_name="text-2xl font-bold text-gray-800"),
            rx.el.p(
                "Get a quick overview of your data's quality and characteristics.",
                class_name="text-gray-500 mt-1",
            ),
            rx.el.button(
                "Refresh Profile",
                rx.icon("refresh-cw", size=14),
                on_click=State.generate_data_profile,
                class_name="mt-4 flex items-center justify-center gap-2 px-4 py-2 bg-gray-100 text-gray-700 font-semibold rounded-lg hover:bg-gray-200 transition-colors border border-gray-300 text-sm",
            ),
            class_name="mb-6 text-center",
        ),
        rx.cond(
            State.profiling_data.keys().length() > 0,
            rx.el.div(
                rx.foreach(
                    State.profiling_data.keys(),
                    lambda col: profiling_card(col, State.profiling_data[col]),
                ),
                class_name="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4",
            ),
            rx.el.div(
                rx.icon("bar-chart-big", size=48, class_name="text-gray-400"),
                rx.el.h3(
                    "No Data to Profile",
                    class_name="mt-4 text-lg font-semibold text-gray-700",
                ),
                rx.el.p(
                    "Upload one or more files to generate a data profile.",
                    class_name="mt-1 text-sm text-gray-500",
                ),
                class_name="text-center p-10 border-2 border-dashed border-gray-300 rounded-xl bg-gray-50",
            ),
        ),
        class_name="w-full mx-auto flex flex-col",
    )