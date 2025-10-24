import reflex as rx
import reflex_enterprise as rxe
from app.state import State
from app.components.header import header
from app.components.tabs import navigation_tabs
from app.components.upload import upload_view
from app.components.mapping import mapping_view
from app.components.filter import filter_view
from app.components.validation import validation_view
from app.components.datatypes import data_types_view
from app.components.download import download_view


def index() -> rx.Component:
    """The main page of the DataForge app."""
    return rx.el.div(
        header(),
        rx.el.main(
            navigation_tabs(),
            rx.el.div(
                rx.match(
                    State.active_tab,
                    ("upload", upload_view()),
                    ("mapping", mapping_view()),
                    ("filter", filter_view()),
                    ("validation", validation_view()),
                    ("datatypes", data_types_view()),
                    ("download", download_view()),
                    rx.el.div("Select a tab", class_name="text-center text-gray-500"),
                ),
                class_name="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8",
            ),
            class_name="w-full",
        ),
        class_name="min-h-screen bg-gray-50 font-['Montserrat']",
    )


app = rxe.App(
    theme=rx.theme(appearance="light"),
    head_components=[
        rx.el.link(rel="preconnect", href="https://fonts.googleapis.com"),
        rx.el.link(rel="preconnect", href="https://fonts.gstatic.com", cross_origin=""),
        rx.el.link(
            href="https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600;700&display=swap",
            rel="stylesheet",
        ),
    ],
)
app.add_page(index, title="DataForge - Data Transformation")