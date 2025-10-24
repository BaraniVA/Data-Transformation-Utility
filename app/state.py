import reflex as rx
import pandas as pd
from typing import TypedDict, Any
import io
import logging


class FilterRule(TypedDict):
    id: int
    column: str
    operation: str
    value: str


class ValidationRule(TypedDict):
    id: int
    column: str
    rule_type: str
    param1: str
    param2: str


class FileData(TypedDict):
    file_name: str
    row_count: int
    columns: list[str]
    df_json: str


class State(rx.State):
    """The main application state."""

    active_tab: str = "upload"
    is_uploading: bool = False
    is_dragging: bool = False
    uploaded_files: list[FileData] = []
    column_mappings: dict[str, str] = {}
    data_type_mappings: dict[str, str] = {}
    filter_rules: list[FilterRule] = []
    next_rule_id: int = 0
    rows_removed: int = 0
    validation_rules: list[ValidationRule] = []
    next_validation_id: int = 0
    validation_results: dict[str, int | dict[str, int]] = {}
    show_validation_results: bool = False
    preview_data: list[dict] = []
    preview_columns: list[str] = []
    preview_page: int = 1
    preview_rows_per_page: int = 10
    download_format: str = "csv"

    @rx.var
    def total_preview_rows(self) -> int:
        """Total number of rows in the preview data."""
        return len(self.preview_data)

    @rx.var
    def total_preview_pages(self) -> int:
        """Total number of pages for the preview table."""
        if not self.preview_data:
            return 1
        return -(-self.total_preview_rows // self.preview_rows_per_page)

    @rx.var
    def paginated_preview_data(self) -> list[dict]:
        """The data for the current page of the preview table."""
        start = (self.preview_page - 1) * self.preview_rows_per_page
        end = start + self.preview_rows_per_page
        return self.preview_data[start:end]

    @rx.var
    def all_columns(self) -> list[str]:
        """Get a unique, sorted list of all column names from all uploaded files."""
        all_cols = set()
        for file_data in self.uploaded_files:
            for col in file_data["columns"]:
                all_cols.add(col)
        return sorted(list(all_cols))

    @rx.event
    def set_column_mapping(self, original_col: str, new_col: str):
        """Update the mapping for a single column."""
        if new_col:
            self.column_mappings[original_col] = new_col
        elif original_col in self.column_mappings:
            del self.column_mappings[original_col]

    @rx.event
    def apply_column_mapping(self):
        """Apply the defined column mappings to all uploaded dataframes."""
        if not self.column_mappings:
            return rx.toast.warning("No column mappings have been defined.")
        for i in range(len(self.uploaded_files)):
            df = pd.read_json(
                io.StringIO(self.uploaded_files[i]["df_json"]), orient="split"
            )
            rename_dict = {
                k: v for k, v in self.column_mappings.items() if k in df.columns
            }
            df.rename(columns=rename_dict, inplace=True)
            self.uploaded_files[i]["columns"] = df.columns.tolist()
            self.uploaded_files[i]["df_json"] = df.to_json(orient="split")
        self.column_mappings = {}
        return rx.toast.success("Column mappings applied successfully!")

    @rx.event
    def add_filter_rule(self):
        """Add a new, empty filter rule."""
        new_rule: FilterRule = {
            "id": self.next_rule_id,
            "column": "",
            "operation": "equals",
            "value": "",
        }
        self.filter_rules.append(new_rule)
        self.next_rule_id += 1

    @rx.event
    def remove_filter_rule(self, rule_id: int):
        """Remove a filter rule by its ID."""
        self.filter_rules = [
            rule for rule in self.filter_rules if rule["id"] != rule_id
        ]

    @rx.event
    def update_filter_rule(self, rule_id: int, field: str, value: str):
        """Update a specific field of a filter rule."""
        for i, rule in enumerate(self.filter_rules):
            if rule["id"] == rule_id:
                updated_rule = self.filter_rules[i].copy()
                updated_rule[field] = value
                if field == "operation" and value in ["is_empty", "is_not_empty"]:
                    updated_rule["value"] = ""
                self.filter_rules[i] = updated_rule
                break

    @rx.event
    def apply_filters(self):
        """Apply all defined filter rules to the dataframes."""
        if not self.filter_rules:
            return rx.toast.warning("No filter rules to apply.")
        total_rows_before = sum((f["row_count"] for f in self.uploaded_files))
        total_rows_after = 0
        for i in range(len(self.uploaded_files)):
            try:
                df = pd.read_json(
                    io.StringIO(self.uploaded_files[i]["df_json"]), orient="split"
                )
                initial_mask = pd.Series([True] * len(df), index=df.index)
                for rule in self.filter_rules:
                    if not rule["column"]:
                        continue
                    col = rule["column"]
                    op = rule["operation"]
                    val = rule["value"]
                    if col not in df.columns:
                        continue
                    if op == "equals":
                        initial_mask &= df[col].astype(str) == val
                    elif op == "not_equals":
                        initial_mask &= df[col].astype(str) != val
                    elif op == "contains":
                        initial_mask &= (
                            df[col].astype(str).str.contains(val, case=False, na=False)
                        )
                    elif op == "not_contains":
                        initial_mask &= ~df[col].astype(str).str.contains(
                            val, case=False, na=False
                        )
                    elif op == "is_empty":
                        initial_mask &= df[col].isnull() | (df[col].astype(str) == "")
                    elif op == "is_not_empty":
                        initial_mask &= df[col].notnull() & (df[col].astype(str) != "")
                    else:
                        numeric_col = pd.to_numeric(df[col], errors="coerce")
                        numeric_val = pd.to_numeric(val, errors="coerce")
                        op_mask = pd.Series([False] * len(df), index=df.index)
                        valid_comparison = numeric_col.notna() & (
                            numeric_val is not None
                        )
                        if op == "greater_than":
                            op_mask[valid_comparison] = (
                                numeric_col[valid_comparison] > numeric_val
                            )
                        elif op == "less_than":
                            op_mask[valid_comparison] = (
                                numeric_col[valid_comparison] < numeric_val
                            )
                        elif op == "ge":
                            op_mask[valid_comparison] = (
                                numeric_col[valid_comparison] >= numeric_val
                            )
                        elif op == "le":
                            op_mask[valid_comparison] = (
                                numeric_col[valid_comparison] <= numeric_val
                            )
                        initial_mask &= op_mask
                df = df[initial_mask]
                total_rows_after += len(df)
                self.uploaded_files[i]["row_count"] = len(df)
                self.uploaded_files[i]["df_json"] = df.to_json(orient="split")
            except Exception as e:
                logging.exception(
                    f"Error applying filters to {self.uploaded_files[i]['file_name']}: {e}"
                )
                return rx.toast.error(
                    f"Error on file {self.uploaded_files[i]['file_name']}: {e}"
                )
        self.rows_removed = total_rows_before - total_rows_after
        return rx.toast.success(f"Filters applied. {self.rows_removed} rows removed.")

    @rx.event
    async def handle_upload(self, files: list[rx.UploadFile]):
        """Handle file uploads, parse them, and store the data."""
        if not files:
            yield rx.toast.error("No files selected for upload.")
            return
        self.is_uploading = True
        yield
        for file in files:
            try:
                upload_data = await file.read()
                file_name = file.name
                if file_name.endswith(".csv"):
                    df = pd.read_csv(io.BytesIO(upload_data))
                elif file_name.endswith((".xlsx", ".xls")):
                    df = pd.read_excel(io.BytesIO(upload_data))
                else:
                    yield rx.toast.warning(f"Unsupported file type: {file_name}")
                    continue
                file_info: FileData = {
                    "file_name": file_name,
                    "row_count": len(df),
                    "columns": df.columns.tolist(),
                    "df_json": df.to_json(orient="split"),
                }
                self.uploaded_files.append(file_info)
            except Exception as e:
                logging.exception(f"Error processing {file.name}: {e}")
                yield rx.toast.error(f"Error processing {file.name}: {e}")
        self.is_uploading = False
        yield rx.toast.success(f"Successfully uploaded {len(files)} file(s).")

    @rx.event
    def set_data_type_mapping(self, column_name: str, new_type: str):
        """Update the data type for a single column."""
        if new_type:
            self.data_type_mappings[column_name] = new_type
        elif column_name in self.data_type_mappings:
            del self.data_type_mappings[column_name]

    @rx.event
    def apply_data_type_conversions(self):
        """Apply the defined data type conversions to all uploaded dataframes."""
        if not self.data_type_mappings:
            return rx.toast.warning("No data type conversions have been defined.")
        for i in range(len(self.uploaded_files)):
            df = pd.read_json(
                io.StringIO(self.uploaded_files[i]["df_json"]), orient="split"
            )
            for col, new_type in self.data_type_mappings.items():
                if col not in df.columns:
                    continue
                try:
                    if new_type == "string":
                        df[col] = df[col].astype(str)
                    elif new_type == "integer":
                        df[col] = pd.to_numeric(df[col], errors="coerce").astype(
                            "Int64"
                        )
                    elif new_type == "float":
                        df[col] = pd.to_numeric(df[col], errors="coerce").astype(float)
                    elif new_type == "boolean":
                        df[col] = df[col].astype(bool)
                    elif new_type == "date":
                        df[col] = pd.to_datetime(df[col], errors="coerce")
                except Exception as e:
                    logging.exception(
                        f"Error converting column {col} to {new_type}: {e}"
                    )
                    return rx.toast.error(f"Failed to convert '{col}' to {new_type}.")
            self.uploaded_files[i]["df_json"] = df.to_json(orient="split")
        self.data_type_mappings = {}
        return rx.toast.success("Data type conversions applied successfully!")

    @rx.event
    def clear_all_files(self):
        """Clear all uploaded files from the state."""
        self.uploaded_files = []
        self.column_mappings = {}
        self.data_type_mappings = {}
        self.filter_rules = []
        self.rows_removed = 0
        self.active_tab = "upload"
        self.validation_rules = []
        self.validation_results = {}
        self.show_validation_results = False
        yield rx.toast.info("All files have been cleared.")

    @rx.event
    def set_active_tab(self, tab_name: str):
        """Set the active tab for navigation."""
        if tab_name == "validation":
            self.show_validation_results = False
            self.validation_results = {}
        self.active_tab = tab_name
        if self.active_tab == "download":
            self._prepare_preview_data()

    def _prepare_preview_data(self):
        """Helper to combine all dataframes for preview."""
        if not self.uploaded_files:
            self.preview_data = []
            self.preview_columns = []
            return
        all_dfs = [
            pd.read_json(io.StringIO(f["df_json"]), orient="split")
            for f in self.uploaded_files
        ]
        if all_dfs:
            combined_df = pd.concat(all_dfs, ignore_index=True)
            self.preview_columns = combined_df.columns.tolist()
            self.preview_data = combined_df.to_dict(orient="records")
        else:
            self.preview_data = []
            self.preview_columns = []
        self.preview_page = 1

    @rx.event
    def download_file(self, file_index: int):
        """Download a single processed file in the selected format."""
        file_to_download = self.uploaded_files[file_index]
        df = pd.read_json(io.StringIO(file_to_download["df_json"]), orient="split")
        original_name = file_to_download["file_name"].split(".")[0]
        if self.download_format == "csv":
            content = df.to_csv(index=False)
            filename = f"processed_{original_name}.csv"
            return rx.download(data=content, filename=filename)
        elif self.download_format == "excel":
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine="openpyxl") as writer:
                df.to_excel(writer, index=False, sheet_name="Sheet1")
            content = output.getvalue()
            filename = f"processed_{original_name}.xlsx"
            return rx.download(data=content, filename=filename)

    @rx.event
    def download_all_zip(self):
        """Download all processed files as a single ZIP archive."""
        import zipfile

        if not self.uploaded_files:
            return rx.toast.warning("No files to download.")
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
            for file_data in self.uploaded_files:
                df = pd.read_json(io.StringIO(file_data["df_json"]), orient="split")
                original_name = file_data["file_name"].split(".")[0]
                if self.download_format == "csv":
                    content = df.to_csv(index=False)
                    filename = f"processed_{original_name}.csv"
                elif self.download_format == "excel":
                    output = io.BytesIO()
                    with pd.ExcelWriter(output, engine="openpyxl") as writer:
                        df.to_excel(writer, index=False, sheet_name="Sheet1")
                    content = output.getvalue()
                    filename = f"processed_{original_name}.xlsx"
                else:
                    continue
                zip_file.writestr(filename, content)
        zip_buffer.seek(0)
        return rx.download(
            data=zip_buffer.getvalue(), filename="dataforge_processed_files.zip"
        )

    @rx.event
    def set_preview_page(self, page: int):
        """Set the current page for the preview table."""
        if 1 <= page <= self.total_preview_pages:
            self.preview_page = page

    @rx.event
    def set_preview_rows_per_page(self, rows: str):
        """Set the number of rows per page and reset to page 1."""
        self.preview_rows_per_page = int(rows)
        self.preview_page = 1

    @rx.event
    def set_is_dragging(self, is_dragging: bool):
        """Set the dragging state for UI feedback."""
        self.is_dragging = is_dragging

    @rx.event
    def add_validation_rule(self):
        """Add a new, empty validation rule."""
        new_rule: ValidationRule = {
            "id": self.next_validation_id,
            "column": "",
            "rule_type": "required",
            "param1": "",
            "param2": "",
        }
        self.validation_rules.append(new_rule)
        self.next_validation_id += 1

    @rx.event
    def remove_validation_rule(self, rule_id: int):
        """Remove a validation rule by its ID."""
        self.validation_rules = [
            rule for rule in self.validation_rules if rule["id"] != rule_id
        ]

    @rx.event
    def update_validation_rule(self, rule_id: int, field: str, value: str):
        """Update a specific field of a validation rule."""
        for i, rule in enumerate(self.validation_rules):
            if rule["id"] == rule_id:
                updated_rule = self.validation_rules[i].copy()
                updated_rule[field] = value
                self.validation_rules[i] = updated_rule
                break

    @rx.event
    def clear_validation_results(self):
        """Clear the validation results."""
        self.show_validation_results = False
        self.validation_results = {}

    @rx.event
    def run_validation(self):
        """Execute all validation rules against the data."""
        if not self.validation_rules:
            return rx.toast.warning("No validation rules to run.")
        total_rows = 0
        all_failing_indices = set()
        error_details = {}
        for file_data in self.uploaded_files:
            df = pd.read_json(io.StringIO(file_data["df_json"]), orient="split")
            total_rows += len(df)
            file_failing_indices = pd.Series([False] * len(df), index=df.index)
            for rule in self.validation_rules:
                if not rule["column"] or rule["column"] not in df.columns:
                    continue
                col = rule["column"]
                rule_type = rule["rule_type"]
                param1 = rule["param1"]
                param2 = rule["param2"]
                try:
                    if rule_type == "required":
                        failures = df[col].isnull() | (df[col].astype(str) == "")
                    elif rule_type == "min_length":
                        failures = df[col].astype(str).str.len() < int(param1)
                    elif rule_type == "max_length":
                        failures = df[col].astype(str).str.len() > int(param1)
                    elif rule_type == "numeric_range":
                        numeric_col = pd.to_numeric(df[col], errors="coerce")
                        min_val = float(param1)
                        max_val = float(param2)
                        failures = ~numeric_col.between(min_val, max_val)
                    elif rule_type == "regex_pattern":
                        failures = ~df[col].astype(str).str.match(param1, na=False)
                    else:
                        continue
                    if failures.any():
                        rule_key = f'''"{rule["column"]}" - {rule["rule_type"]}'''
                        if rule_key not in error_details:
                            error_details[rule_key] = 0
                        error_details[rule_key] += failures.sum()
                        file_failing_indices |= failures
                except Exception as e:
                    logging.exception(f"Error validating rule {rule}: {e}")
                    return rx.toast.error(f"Invalid parameter for rule on '{col}'.")
            global_indices = set(
                df.index[file_failing_indices]
                + sum(
                    (
                        len(pd.read_json(io.StringIO(f["df_json"])))
                        for f in self.uploaded_files[
                            : self.uploaded_files.index(file_data)
                        ]
                    )
                )
            )
            all_failing_indices.update(global_indices)
        self.validation_results = {
            "total_rows": total_rows,
            "passing_rows": total_rows - len(all_failing_indices),
            "failing_rows": len(all_failing_indices),
            "error_details": error_details,
        }
        self.show_validation_results = True
        return rx.toast.success("Validation complete!")

    @rx.event
    def remove_invalid_rows(self):
        """Filters out rows that failed validation from the dataframes."""
        if (
            not self.validation_results
            or self.validation_results.get("failing_rows", 0) == 0
        ):
            return rx.toast.info("No invalid rows to remove.")
        all_dfs = [
            pd.read_json(io.StringIO(f["df_json"]), orient="split")
            for f in self.uploaded_files
        ]
        if not all_dfs:
            return
        combined_df = pd.concat(all_dfs, ignore_index=True)
        failing_indices_list = []
        start_index = 0
        for df in all_dfs:
            file_failing_indices = pd.Series([False] * len(df), index=df.index)
            for rule in self.validation_rules:
                if not rule["column"] or rule["column"] not in df.columns:
                    continue
                col, rule_type, param1, param2 = (
                    rule["column"],
                    rule["rule_type"],
                    rule["param1"],
                    rule["param2"],
                )
                try:
                    if rule_type == "required":
                        failures = df[col].isnull() | (df[col].astype(str) == "")
                    elif rule_type == "min_length":
                        failures = df[col].astype(str).str.len() < int(param1)
                    elif rule_type == "max_length":
                        failures = df[col].astype(str).str.len() > int(param1)
                    elif rule_type == "numeric_range":
                        numeric_col = pd.to_numeric(df[col], errors="coerce")
                        failures = ~numeric_col.between(float(param1), float(param2))
                    elif rule_type == "regex_pattern":
                        failures = ~df[col].astype(str).str.match(param1, na=False)
                    else:
                        continue
                    file_failing_indices |= failures
                except Exception as e:
                    logging.exception(
                        f"Error during removal check for rule {rule}: {e}"
                    )
            failing_indices_for_file = df.index[file_failing_indices]
            for index_val in failing_indices_for_file:
                failing_indices_list.append(start_index + index_val)
            start_index += len(df)
        valid_rows_df = combined_df.drop(index=list(set(failing_indices_list)))
        if not valid_rows_df.empty:
            self.uploaded_files[0]["df_json"] = valid_rows_df.to_json(orient="split")
            self.uploaded_files[0]["row_count"] = len(valid_rows_df)
            self.uploaded_files[0]["file_name"] = "combined_and_validated.csv"
            self.uploaded_files = [self.uploaded_files[0]]
        else:
            self.uploaded_files = []
        rows_removed_count = len(combined_df) - len(valid_rows_df)
        self.clear_validation_results()
        return rx.toast.success(f"Removed {rows_removed_count} invalid rows.")