import reflex as rx
from app.state import State


def stat_card(icon: str, title: str, value: rx.Var) -> rx.Component:
    """A card to display a single statistic."""
    return rx.el.div(
        rx.icon(icon, size=24, class_name="text-gray-500"),
        rx.el.div(
            rx.el.p(title, class_name="text-sm font-medium text-gray-500"),
            rx.el.p(value, class_name="text-2xl font-semibold text-gray-800"),
            class_name="flex-1",
        ),
        class_name="flex items-center gap-4 p-4 bg-white border border-gray-200 rounded-xl shadow-sm",
    )


def data_preview_table() -> rx.Component:
    """The data table for previewing processed data."""
    return rx.el.div(
        rx.el.div(
            rx.el.table(
                rx.el.thead(
                    rx.el.tr(
                        rx.foreach(
                            State.preview_columns,
                            lambda col: rx.el.th(
                                col,
                                class_name="px-4 py-2 text-left text-sm font-semibold text-gray-600 bg-gray-50 first:rounded-tl-lg last:rounded-tr-lg",
                            ),
                        ),
                        class_name="border-b border-gray-200",
                    )
                ),
                rx.el.tbody(
                    rx.foreach(
                        State.paginated_preview_data,
                        lambda row, index: rx.el.tr(
                            rx.foreach(
                                State.preview_columns,
                                lambda col: rx.el.td(
                                    row.get(col, "").to_string(),
                                    class_name="px-4 py-2 text-sm text-gray-700 font-mono whitespace-nowrap",
                                ),
                            ),
                            class_name=rx.cond(
                                index % 2 == 0, "bg-white", "bg-gray-50/50"
                            ),
                        ),
                    )
                ),
                class_name="w-full text-sm",
            ),
            class_name="w-full overflow-x-auto border border-gray-200 rounded-lg shadow-sm",
        ),
        rx.el.div(
            rx.el.div(
                rx.el.p(
                    f"Page {State.preview_page} of {State.total_preview_pages}",
                    class_name="text-sm text-gray-600",
                )
            ),
            rx.el.div(
                rx.el.button(
                    rx.icon("chevron-left", size=16),
                    on_click=lambda: State.set_preview_page(State.preview_page - 1),
                    disabled=State.preview_page <= 1,
                    class_name="p-2 rounded-md hover:bg-gray-100 disabled:opacity-50",
                ),
                rx.el.button(
                    rx.icon("chevron-right", size=16),
                    on_click=lambda: State.set_preview_page(State.preview_page + 1),
                    disabled=State.preview_page >= State.total_preview_pages,
                    class_name="p-2 rounded-md hover:bg-gray-100 disabled:opacity-50",
                ),
            ),
            rx.el.div(
                rx.el.span("Rows per page:", class_name="text-sm text-gray-600"),
                rx.el.select(
                    ["10", "25", "50", "100"],
                    default_value=State.preview_rows_per_page.to_string(),
                    on_change=State.set_preview_rows_per_page,
                    class_name="ml-2 px-2 py-1 text-sm border border-gray-300 rounded-md focus:ring-emerald-500 focus:border-emerald-500",
                ),
            ),
            class_name="flex items-center justify-between mt-4 text-sm",
        ),
        class_name="w-full",
    )


def download_buttons() -> rx.Component:
    return rx.el.div(
        rx.el.h3(
            "Download Options", class_name="text-lg font-semibold text-gray-800 mb-4"
        ),
        rx.el.div(
            rx.el.p("Format", class_name="text-sm font-semibold text-gray-600 mb-2"),
            rx.el.div(
                rx.el.button(
                    "CSV",
                    on_click=lambda: State.set_download_format("csv"),
                    class_name=rx.cond(
                        State.download_format == "csv",
                        "flex-1 py-2 text-sm font-semibold text-white bg-emerald-500 rounded-l-lg",
                        "flex-1 py-2 text-sm font-semibold text-gray-700 bg-gray-200 hover:bg-gray-300 rounded-l-lg",
                    ),
                ),
                rx.el.button(
                    "Excel",
                    on_click=lambda: State.set_download_format("excel"),
                    class_name=rx.cond(
                        State.download_format == "excel",
                        "flex-1 py-2 text-sm font-semibold text-white bg-emerald-500 rounded-r-lg",
                        "flex-1 py-2 text-sm font-semibold text-gray-700 bg-gray-200 hover:bg-gray-300 rounded-r-lg",
                    ),
                ),
                class_name="flex w-full mb-4",
            ),
        ),
        rx.el.button(
            f"Download All as .{State.download_format}",
            rx.icon("file-archive", size=16),
            on_click=State.download_all_zip,
            class_name="w-full flex items-center justify-center gap-2 px-4 py-2 bg-emerald-500 text-white font-semibold rounded-lg hover:bg-emerald-600 transition-colors shadow-sm mb-4",
        ),
        rx.el.h4(
            "Individual Files", class_name="text-md font-semibold text-gray-700 mb-2"
        ),
        rx.el.div(
            rx.foreach(
                State.uploaded_files,
                lambda file, index: rx.el.button(
                    rx.icon("download", size=14),
                    file["file_name"],
                    on_click=lambda: State.download_file(index),
                    class_name="w-full flex items-center justify-start gap-3 p-2 text-sm text-gray-700 font-medium hover:bg-gray-100 rounded-md transition-colors",
                ),
            ),
            class_name="space-y-1",
        ),
    )


def download_view() -> rx.Component:
    """The view for previewing and downloading data."""
    return rx.el.div(
        rx.el.div(
            rx.el.h2(
                "Preview & Download", class_name="text-2xl font-bold text-gray-800"
            ),
            rx.el.p(
                "Review your transformed data and download the results.",
                class_name="text-gray-500 mt-1",
            ),
            class_name="mb-6 text-center",
        ),
        rx.cond(
            State.uploaded_files.length() > 0,
            rx.el.div(
                rx.el.div(
                    stat_card("files", "Total Files", State.uploaded_files.length()),
                    stat_card(
                        "table_rows_split", "Total Rows", State.total_preview_rows
                    ),
                    stat_card(
                        "columns_3", "Total Columns", State.preview_columns.length()
                    ),
                    class_name="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8",
                ),
                rx.el.div(
                    rx.el.div(data_preview_table(), class_name="flex-grow pr-6"),
                    rx.el.div(
                        download_buttons(), class_name="w-full md:w-64 flex-shrink-0"
                    ),
                    class_name="flex flex-col md:flex-row gap-6",
                ),
            ),
            rx.el.div(
                rx.icon("file_x_2", size=48, class_name="text-gray-400"),
                rx.el.h3(
                    "No Data to Preview",
                    class_name="mt-4 text-lg font-semibold text-gray-700",
                ),
                rx.el.p(
                    "Upload and process files to see the results here.",
                    class_name="mt-1 text-sm text-gray-500",
                ),
                class_name="text-center p-10 border-2 border-dashed border-gray-300 rounded-xl bg-gray-50",
            ),
        ),
        class_name="w-full mx-auto flex flex-col",
    )