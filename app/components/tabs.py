import reflex as rx
from app.state import State


def nav_button(text: str, tab_name: str, icon: str, accent_color: str) -> rx.Component:
    """A styled navigation button for the tabs."""
    is_active = State.active_tab == tab_name
    is_disabled = ~(State.uploaded_files.length() > 0) & (tab_name != "upload")
    return rx.el.button(
        rx.icon(icon, size=16),
        rx.el.span(text, class_name="ml-2"),
        on_click=lambda: State.set_active_tab(tab_name),
        class_name=rx.cond(
            is_active,
            f"nav-button active {accent_color}-active",
            f"nav-button {accent_color}",
        ),
        disabled=is_disabled,
    )


def category_label(text: str) -> rx.Component:
    return rx.el.p(
        text,
        class_name="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2",
    )


def tab_group(label: str, *children) -> rx.Component:
    return rx.el.div(
        category_label(label),
        rx.el.div(*children, class_name="flex items-center flex-wrap gap-2"),
        class_name="flex flex-col items-start",
    )


def separator() -> rx.Component:
    return rx.el.div(class_name="w-px h-12 bg-white/10 mx-4")


def navigation_tabs() -> rx.Component:
    """Component for switching between app sections."""
    return rx.el.div(
        rx.el.div(
            tab_group(
                "Start",
                nav_button("Upload", "upload", "cloud_upload", "blue"),
                nav_button("Profiling", "profiling", "bar-chart-big", "blue"),
            ),
            separator(),
            tab_group(
                "Transform",
                nav_button("Column Mapping", "mapping", "shuffle", "purple"),
                nav_button(
                    "Column Selection", "column_selection", "columns-3", "purple"
                ),
                nav_button("Data Types", "datatypes", "type", "purple"),
                nav_button("Text Operations", "text_ops", "pilcrow", "purple"),
                nav_button("Split/Join", "split_join", "split", "purple"),
            ),
            separator(),
            tab_group(
                "Clean & Validate",
                nav_button("Filter", "filter", "blinds", "orange"),
                nav_button("Null Handling", "null_handling", "search-slash", "orange"),
                nav_button("Deduplication", "deduplication", "copy-x", "orange"),
                nav_button("Validation", "validation", "shield-check", "orange"),
            ),
            separator(),
            tab_group(
                "Advanced",
                nav_button("Conditional", "conditional_transform", "git-fork", "teal"),
                nav_button("Date/Time", "datetime", "calendar", "teal"),
                nav_button("Sample/Sort", "sample_sort", "arrow-up-down", "teal"),
                nav_button("Pivot/Reshape", "pivot", "table-properties", "teal"),
                nav_button("Encoding", "encoding", "binary", "teal"),
            ),
            separator(),
            tab_group(
                "Finish", nav_button("Download", "download", "cloud_download", "green")
            ),
            class_name="flex flex-wrap items-start justify-center gap-4 p-4 bg-gray-800/80 backdrop-blur-sm border border-white/10 rounded-2xl shadow-2xl shadow-black/20",
            style={"background_image": "linear-gradient(145deg, #2D3748, #1A202C)"},
        ),
        class_name="my-8 px-4",
    )