import reflex as rx
from app.state import State


def nav_button(text: str, tab_name: str) -> rx.Component:
    """A styled navigation button for the tabs."""
    return rx.el.button(
        text,
        on_click=lambda: State.set_active_tab(tab_name),
        class_name=rx.cond(
            State.active_tab == tab_name,
            "px-4 py-2 text-sm font-semibold text-white bg-emerald-500 rounded-lg shadow-sm",
            "px-4 py-2 text-sm font-semibold text-gray-600 hover:bg-gray-100 rounded-lg",
        ),
        disabled=~State.uploaded_files.length() > 0,
    )


def navigation_tabs() -> rx.Component:
    """Component for switching between app sections."""
    return rx.el.div(
        rx.el.div(
            nav_button("Upload", "upload"),
            nav_button("Profiling", "profiling"),
            nav_button("Column Mapping", "mapping"),
            nav_button("Column Selection", "column_selection"),
            nav_button("Filter & Cleanup", "filter"),
            nav_button("Validation", "validation"),
            nav_button("Data Types", "datatypes"),
            nav_button("Deduplication", "deduplication"),
            nav_button("Preview & Download", "download"),
            class_name="flex items-center gap-2 p-1 bg-gray-50 border border-gray-200 rounded-xl overflow-x-auto",
        ),
        class_name="flex justify-center my-6",
    )