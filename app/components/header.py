import reflex as rx


def header() -> rx.Component:
    """The header component for the DataForge app."""
    return rx.el.header(
        rx.el.div(
            rx.el.a(
                rx.el.div(
                    rx.icon("blinds", size=28, class_name="text-emerald-500"),
                    rx.el.h1(
                        "DataForge",
                        class_name="text-2xl font-bold text-gray-800 tracking-tight",
                    ),
                    class_name="flex items-center gap-3",
                ),
                href="/",
            ),
            class_name="flex items-center justify-between max-w-7xl mx-auto w-full",
        ),
        class_name="w-full p-4 border-b border-gray-200 bg-white/80 backdrop-blur-sm sticky top-0 z-10",
    )