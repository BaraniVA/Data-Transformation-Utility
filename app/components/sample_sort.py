import reflex as rx
from app.state import State, SortConfig


def sampling_section() -> rx.Component:
    return rx.el.div(
        rx.el.h3("Data Sampling", class_name="text-xl font-bold text-gray-800 mb-2"),
        rx.el.div(
            rx.el.label(
                rx.el.input(
                    type="radio",
                    name="sample_type",
                    value="random",
                    is_checked=State.sample_type == "random",
                    on_change=lambda: State.set_sample_type("random"),
                ),
                " Random N Rows",
                class_name="flex items-center text-sm",
            ),
            rx.el.label(
                rx.el.input(
                    type="radio",
                    name="sample_type",
                    value="percentage",
                    is_checked=State.sample_type == "percentage",
                    on_change=lambda: State.set_sample_type("percentage"),
                ),
                " Percentage (%) of Rows",
                class_name="flex items-center text-sm",
            ),
            rx.el.label(
                rx.el.input(
                    type="radio",
                    name="sample_type",
                    value="top",
                    is_checked=State.sample_type == "top",
                    on_change=lambda: State.set_sample_type("top"),
                ),
                " Top N Rows",
                class_name="flex items-center text-sm",
            ),
            rx.el.label(
                rx.el.input(
                    type="radio",
                    name="sample_type",
                    value="bottom",
                    is_checked=State.sample_type == "bottom",
                    on_change=lambda: State.set_sample_type("bottom"),
                ),
                " Bottom N Rows",
                class_name="flex items-center text-sm",
            ),
            class_name="grid md:grid-cols-4 gap-4 mb-4",
        ),
        rx.cond(
            State.sample_type == "percentage",
            rx.el.input(
                type="number",
                default_value=State.sample_percentage.to_string(),
                on_change=State.set_sample_percentage,
                class_name="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg",
            ),
            rx.el.input(
                type="number",
                default_value=State.sample_n.to_string(),
                on_change=State.set_sample_n,
                class_name="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg",
            ),
        ),
        rx.el.button(
            "Apply Sample",
            rx.icon("test_tube", size=16),
            on_click=State.apply_sampling,
            class_name="mt-4 w-full flex items-center justify-center gap-2 px-4 py-2 bg-blue-500 text-white font-semibold rounded-lg hover:bg-blue-600 transition-colors shadow-sm",
        ),
        class_name="p-6 bg-white border border-gray-200 rounded-xl",
    )


def sort_rule_editor(config: SortConfig) -> rx.Component:
    return rx.el.div(
        rx.el.select(
            rx.el.option("Select Column...", value=""),
            rx.foreach(State.all_columns, lambda col: rx.el.option(col, value=col)),
            value=config["column"],
            on_change=lambda val: State.update_sort_config(config["id"], "column", val),
            class_name="flex-1 px-3 py-2 text-sm border border-gray-300 rounded-lg",
        ),
        rx.el.button(
            rx.icon("arrow-up-down", size=16),
            rx.cond(config["ascending"], "Ascending", "Descending"),
            on_click=lambda: State.update_sort_config(
                config["id"], "ascending", ~config["ascending"]
            ),
            class_name="flex items-center gap-2 px-3 py-2 text-sm border border-gray-300 rounded-lg",
        ),
        rx.el.button(
            rx.icon("trash-2", size=16),
            on_click=lambda: State.remove_sort_config(config["id"]),
            class_name="p-2 text-gray-500 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors",
        ),
        class_name="flex items-center gap-2 w-full",
    )


def sorting_section() -> rx.Component:
    return rx.el.div(
        rx.el.h3(
            "Multi-column Sorting", class_name="text-xl font-bold text-gray-800 mb-2"
        ),
        rx.el.div(
            rx.foreach(State.sort_configs, sort_rule_editor), class_name="space-y-2"
        ),
        rx.el.button(
            "Add Sort Level",
            rx.icon("plus", size=16),
            on_click=State.add_sort_config,
            class_name="mt-4 w-full flex items-center justify-center gap-2 px-4 py-2 bg-gray-100 text-gray-700 font-semibold rounded-lg hover:bg-gray-200 border border-gray-300",
        ),
        rx.el.button(
            "Apply Sort",
            rx.icon("arrow-up-down", size=16),
            on_click=State.apply_sorting,
            disabled=State.sort_configs.length() == 0,
            class_name="mt-6 w-full flex items-center justify-center gap-2 px-4 py-2 bg-blue-500 text-white font-semibold rounded-lg hover:bg-blue-600 transition-colors shadow-sm disabled:bg-gray-300",
        ),
        class_name="p-6 bg-white border border-gray-200 rounded-xl mt-6",
    )


def sample_sort_view() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.h2("Sample & Sort", class_name="text-2xl font-bold text-gray-800"),
            rx.el.p(
                "Extract a subset of your data or sort it by multiple columns.",
                class_name="text-gray-500 mt-1",
            ),
            class_name="mb-6 text-center",
        ),
        rx.cond(
            State.all_columns.length() > 0,
            rx.el.div(sampling_section(), sorting_section()),
            rx.el.div(
                rx.icon("arrow-up-down", size=48, class_name="text-gray-400"),
                rx.el.h3(
                    "No Data to Process",
                    class_name="mt-4 text-lg font-semibold text-gray-700",
                ),
                rx.el.p(
                    "Upload files to begin sampling or sorting.",
                    class_name="mt-1 text-sm text-gray-500",
                ),
                class_name="text-center p-10 border-2 border-dashed border-gray-300 rounded-xl bg-gray-50",
            ),
        ),
        class_name="w-full max-w-4xl mx-auto flex flex-col",
    )