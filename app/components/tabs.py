import reflex as rx
from app.state import State


def nav_button(text: str, tab_name: str, icon: str | None = None) -> rx.Component:
    """A styled navigation button for the tabs."""
    return rx.el.button(
        rx.icon(icon, size=14, class_name="mr-1.5") if icon else None,
        text,
        on_click=lambda: State.set_active_tab(tab_name),
        class_name=rx.cond(
            State.active_tab == tab_name,
            "flex items-center px-3 py-1.5 text-sm font-semibold text-white bg-emerald-500 rounded-lg shadow-sm transition-colors",
            "flex items-center px-3 py-1.5 text-sm font-semibold text-gray-600 hover:bg-gray-200 rounded-lg transition-colors",
        ),
        disabled=~(State.uploaded_files.length() > 0) & (tab_name != "upload"),
    )


def tab_group(*children) -> rx.Component:
    return rx.el.div(*children, class_name="flex items-center flex-wrap gap-2")


def separator() -> rx.Component:
    return rx.el.div(class_name="h-6 w-px bg-gray-300 mx-2")


def navigation_tabs() -> rx.Component:
    """Component for switching between app sections."""
    return rx.el.div(
        rx.el.div(
            tab_group(
                nav_button("Upload", "upload", icon="upload-cloud"),
                nav_button("Profiling", "profiling", icon="bar-chart-big"),
            ),
            separator(),
            tab_group(
                nav_button("Column Mapping", "mapping", icon="shuffle"),
                nav_button("Column Selection", "column_selection", icon="columns-3"),
                nav_button("Data Types", "datatypes", icon="type"),
            ),
            separator(),
            tab_group(
                nav_button("Text Operations", "text_ops", icon="pilcrow"),
                nav_button("Split/Join", "split_join", icon="split"),
                nav_button("Filter", "filter", icon="blinds"),
                nav_button("Null Handling", "null_handling", icon="search-slash"),
                nav_button("Deduplication", "deduplication", icon="copy-x"),
            ),
            separator(),
            tab_group(
                nav_button("Validation", "validation", icon="shield-check"),
                nav_button("Conditional", "conditional_transform", icon="git-fork"),
                nav_button("Date/Time", "datetime", icon="calendar"),
                nav_button("Sample/Sort", "sample_sort", icon="arrow-up-down"),
                nav_button("Pivot/Reshape", "pivot", icon="table-properties"),
                nav_button("Encoding", "encoding", icon="binary"),
            ),
            separator(),
            tab_group(nav_button("Download", "download", icon="download-cloud")),
            class_name="flex flex-wrap items-center justify-center gap-2 p-2 bg-gray-100/50 border border-gray-200/80 rounded-xl",
        ),
        class_name="my-6 px-4",
    )