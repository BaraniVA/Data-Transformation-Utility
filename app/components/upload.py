import reflex as rx
from app.state import State
import reflex_enterprise as rxe


def uploaded_file_card(file: dict, index: int) -> rx.Component:
    """A card to display information about an uploaded file."""
    return rx.el.div(
        rx.el.div(
            rx.icon("file-text", class_name="text-emerald-500"),
            rx.el.span(
                file["file_name"], class_name="font-medium text-gray-800 truncate"
            ),
            class_name="flex items-center gap-3",
        ),
        rx.el.div(
            rx.el.span(
                f"{file['row_count']} rows",
                class_name="text-sm font-medium text-gray-500 bg-gray-100 px-2 py-1 rounded-md",
            )
        ),
        class_name="flex items-center justify-between p-3 border border-gray-200 rounded-lg bg-white hover:shadow-sm transition-shadow",
    )


def upload_view() -> rx.Component:
    """The view for uploading and displaying files."""
    return rx.el.div(
        rx.upload.root(
            rx.el.div(
                rx.icon("cloud_upload", size=48, class_name="text-gray-400"),
                rx.el.h3(
                    "Drag & drop files here",
                    class_name="mt-4 text-lg font-semibold text-gray-700",
                ),
                rx.el.p(
                    "or click to select files", class_name="mt-1 text-sm text-gray-500"
                ),
                rx.el.p(".csv, .xlsx, .xls", class_name="mt-2 text-xs text-gray-400"),
                class_name="flex flex-col items-center justify-center p-10 text-center",
            ),
            id="upload_area",
            class_name="w-full cursor-pointer rounded-xl border-2 border-dashed border-gray-300 bg-gray-50 hover:bg-gray-100 transition-colors",
            accept={
                "text/csv": [".csv"],
                "application/vnd.ms-excel": [".xls"],
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": [
                    ".xlsx"
                ],
            },
        ),
        rx.cond(
            rx.selected_files("upload_area").length() > 0,
            rx.el.div(
                rx.el.button(
                    "Upload Files",
                    rx.icon("arrow-up-from-line", size=16),
                    on_click=State.handle_upload(
                        rx.upload_files(upload_id="upload_area")
                    ),
                    class_name="mt-4 w-full flex items-center justify-center gap-2 px-4 py-2 bg-emerald-500 text-white font-semibold rounded-lg hover:bg-emerald-600 transition-colors shadow-sm",
                ),
                rx.el.button(
                    "Clear Selection",
                    rx.icon("x", size=16),
                    on_click=rx.clear_selected_files("upload_area"),
                    class_name="mt-2 w-full flex items-center justify-center gap-2 px-4 py-2 bg-gray-200 text-gray-700 font-semibold rounded-lg hover:bg-gray-300 transition-colors",
                ),
                class_name="mt-4",
            ),
            None,
        ),
        rx.cond(
            State.is_uploading,
            rx.el.div(
                rx.spinner(class_name="text-emerald-500"),
                rx.el.p("Processing files...", class_name="text-gray-600"),
                class_name="flex flex-col items-center gap-4 mt-8",
            ),
            None,
        ),
        rx.cond(
            State.uploaded_files.length() > 0,
            rx.el.div(
                rx.el.div(
                    rx.el.h3(
                        "Uploaded Files",
                        class_name="text-xl font-semibold text-gray-800",
                    ),
                    rx.el.button(
                        "Clear All",
                        on_click=State.clear_all_files,
                        class_name="flex items-center gap-2 text-sm font-semibold text-red-500 hover:text-red-700",
                    ),
                    class_name="flex items-center justify-between mb-4",
                ),
                rx.el.div(
                    rx.foreach(State.uploaded_files, uploaded_file_card),
                    class_name="space-y-2",
                ),
                class_name="mt-8 w-full",
            ),
            None,
        ),
        class_name="w-full max-w-2xl mx-auto flex flex-col items-center",
    )