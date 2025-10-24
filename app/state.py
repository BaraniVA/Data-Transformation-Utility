import reflex as rx
import pandas as pd
from typing import TypedDict, Any
import io
import logging
import re


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


class ConditionalRule(TypedDict):
    id: int
    condition_column: str
    condition_op: str
    condition_value: str
    action: str
    target_column: str
    action_value: str
    logic_combiner: str


class SortConfig(TypedDict):
    id: int
    column: str
    ascending: bool


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
    dedup_columns: list[str] = []
    dedup_keep: str = "first"
    duplicates_found: int = -1
    selected_columns: list[str] = []
    column_order: list[str] = []
    profiling_data: dict[str, dict] = {}
    find_text: str = ""
    replace_text: str = ""
    find_replace_column: str = "_all_"
    case_sensitive: bool = False
    use_regex: bool = False
    match_count: int = -1
    case_conversion_columns: list[str] = []
    case_conversion_type: str = "upper"
    whitespace_columns: list[str] = []
    whitespace_operation: str = "all"
    null_stats: dict[str, dict] = {}
    fill_columns: list[str] = []
    fill_strategy: str = "custom"
    fill_custom_value: str = ""
    split_column: str = ""
    split_delimiter: str = ","
    split_new_col_prefix: str = "split_"
    split_num_splits: int = -1
    join_columns: list[str] = []
    join_separator: str = " "
    join_new_col_name: str = "joined_column"
    extract_column: str = ""
    extract_start_pos: int = 0
    extract_end_pos: int | None = None
    extract_new_col_name: str = "extracted_column"
    sample_type: str = "random"
    sample_n: int = 10
    sample_percentage: float = 50.0
    sort_configs: list[SortConfig] = []
    next_sort_id: int = 0
    conditional_rules: list[ConditionalRule] = []
    next_conditional_id: int = 0
    pivot_index: str = ""
    pivot_columns: str = ""
    pivot_values: str = ""
    pivot_aggfunc: str = "mean"
    melt_id_vars: list[str] = []
    melt_value_vars: list[str] = []
    melt_var_name: str = "variable"
    melt_value_name: str = "value"
    groupby_columns: list[str] = []
    groupby_agg_columns: list[str] = []
    groupby_aggfunc: str = "sum"
    datetime_columns: list[str] = []
    extract_components: list[str] = ["year", "month", "day"]
    date_diff_col1: str = ""
    date_diff_col2: str = ""
    date_diff_new_col: str = "date_diff_days"
    date_arith_column: str = ""
    date_arith_op: str = "add"
    date_arith_unit: str = "days"
    date_arith_value: int = 1
    label_encode_columns: list[str] = []
    label_mappings: dict[str, dict[str, int]] = {}
    onehot_columns: list[str] = []
    onehot_prefix: str = ""
    remove_special_columns: list[str] = []
    special_char_pattern: str = "[^a-zA-Z0-9\\s]"

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
        if self.uploaded_files:
            self.column_order = self.all_columns
            self.selected_columns = self.all_columns
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
        self.profiling_data = {}
        self.selected_columns = []
        self.column_order = []
        self.dedup_columns = []
        self.duplicates_found = -1
        self.find_text = ""
        self.replace_text = ""
        self.find_replace_column = "_all_"
        self.case_sensitive = False
        self.use_regex = False
        self.match_count = -1
        self.case_conversion_columns = []
        self.whitespace_columns = []
        self.null_stats = {}
        self.fill_columns = []
        self.fill_strategy = "custom"
        self.fill_custom_value = ""
        self.split_column = ""
        self.split_delimiter = ","
        self.split_new_col_prefix = "split_"
        self.split_num_splits = -1
        self.join_columns = []
        self.join_separator = " "
        self.join_new_col_name = "joined_column"
        self.extract_column = ""
        self.extract_start_pos = 0
        self.extract_end_pos = None
        self.extract_new_col_name = "extracted_column"
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
        if self.active_tab == "profiling":
            self.generate_data_profile()
        if self.active_tab == "null_handling":
            self.calculate_null_stats()

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

    @rx.event
    def toggle_dedup_column(self, column: str):
        """Add or remove a column from the deduplication key."""
        if column in self.dedup_columns:
            self.dedup_columns.remove(column)
        else:
            self.dedup_columns.append(column)
        self.duplicates_found = -1

    @rx.event
    def set_dedup_keep(self, strategy: str):
        """Set the keep strategy for deduplication."""
        self.dedup_keep = strategy
        self.duplicates_found = -1

    @rx.event
    def find_duplicates(self):
        """Scan data to find the count of duplicate rows."""
        if not self.dedup_columns:
            return rx.toast.warning(
                "Please select at least one column for deduplication."
            )
        total_rows = 0
        total_unique_rows = 0
        for file_data in self.uploaded_files:
            df = pd.read_json(io.StringIO(file_data["df_json"]), orient="split")
            total_rows += len(df)
            dedup_df = df.drop_duplicates(subset=self.dedup_columns, keep="first")
            total_unique_rows += len(dedup_df)
        self.duplicates_found = total_rows - total_unique_rows
        return rx.toast.info(f"Found {self.duplicates_found} duplicate rows.")

    @rx.event
    def remove_duplicates(self):
        """Remove duplicate rows from all dataframes."""
        if self.duplicates_found < 0:
            return rx.toast.warning("Please run 'Find Duplicates' first.")
        total_rows_before = sum((f["row_count"] for f in self.uploaded_files))
        total_rows_after = 0
        for i in range(len(self.uploaded_files)):
            df = pd.read_json(
                io.StringIO(self.uploaded_files[i]["df_json"]), orient="split"
            )
            keep = self.dedup_keep if self.dedup_keep != "none" else False
            df.drop_duplicates(subset=self.dedup_columns, keep=keep, inplace=True)
            self.uploaded_files[i]["df_json"] = df.to_json(orient="split")
            self.uploaded_files[i]["row_count"] = len(df)
            total_rows_after += len(df)
        rows_removed_count = total_rows_before - total_rows_after
        self.duplicates_found = -1
        self.dedup_columns = []
        return rx.toast.success(f"Removed {rows_removed_count} duplicate rows.")

    @rx.event
    def toggle_column_selection(self, column: str):
        """Toggle the selection of a column for the final output."""
        if column in self.selected_columns:
            self.selected_columns.remove(column)
        else:
            self.selected_columns.append(column)

    @rx.event
    def select_all_columns(self):
        """Select all available columns."""
        self.selected_columns = self.all_columns.copy()

    @rx.event
    def deselect_all_columns(self):
        """Deselect all columns."""
        self.selected_columns = []

    @rx.event
    def move_column_up(self, column: str):
        """Move a column up in the order."""
        idx = self.column_order.index(column)
        if idx > 0:
            self.column_order.insert(idx - 1, self.column_order.pop(idx))

    @rx.event
    def move_column_down(self, column: str):
        """Move a column down in the order."""
        idx = self.column_order.index(column)
        if idx < len(self.column_order) - 1:
            self.column_order.insert(idx + 1, self.column_order.pop(idx))

    @rx.event
    def apply_column_selection(self):
        """Apply the selected columns and their order to all dataframes."""
        for i in range(len(self.uploaded_files)):
            df = pd.read_json(
                io.StringIO(self.uploaded_files[i]["df_json"]), orient="split"
            )
            final_cols = [
                col
                for col in self.column_order
                if col in self.selected_columns and col in df.columns
            ]
            df = df[final_cols]
            self.uploaded_files[i]["df_json"] = df.to_json(orient="split")
            self.uploaded_files[i]["columns"] = df.columns.tolist()
        return rx.toast.success("Column selection and order applied.")

    @rx.event
    def generate_data_profile(self):
        """Generate profiling statistics for the combined data."""
        if not self.uploaded_files:
            self.profiling_data = {}
            return rx.toast.warning("No data to profile.")
        all_dfs = [
            pd.read_json(io.StringIO(f["df_json"]), orient="split")
            for f in self.uploaded_files
        ]
        combined_df = pd.concat(all_dfs, ignore_index=True)
        profile = {}
        for col in combined_df.columns:
            s = combined_df[col]
            stats = {
                "dtype": str(s.dtype),
                "count": int(s.count()),
                "unique": int(s.nunique()),
                "null_count": int(s.isnull().sum()),
            }
            stats["null_percentage"] = stats["null_count"] / len(s) if len(s) > 0 else 0
            if pd.api.types.is_numeric_dtype(s):
                desc = s.describe()
                stats["min"] = float(desc.get("min", 0))
                stats["max"] = float(desc.get("max", 0))
                stats["mean"] = float(desc.get("mean", 0))
                stats["median"] = float(s.median())
            if pd.api.types.is_string_dtype(s) or s.dtype == "object":
                str_series = s.astype(str)
                stats["min_len"] = (
                    int(str_series.str.len().min()) if stats["count"] > 0 else 0
                )
                stats["max_len"] = (
                    int(str_series.str.len().max()) if stats["count"] > 0 else 0
                )
            profile[col] = stats
        self.profiling_data = profile
        return rx.toast.success("Data profile generated.")

    @rx.event
    def calculate_null_stats(self):
        """Calculate null counts and percentages for all columns."""
        if not self.uploaded_files:
            self.null_stats = {}
            return rx.toast.warning("No data to analyze.")
        all_dfs = [
            pd.read_json(io.StringIO(f["df_json"]), orient="split")
            for f in self.uploaded_files
        ]
        combined_df = pd.concat(all_dfs, ignore_index=True)
        stats = {}
        for col in combined_df.columns:
            null_count = int(combined_df[col].isnull().sum())
            total_count = len(combined_df[col])
            null_percentage = null_count / total_count if total_count > 0 else 0
            stats[col] = {"null_count": null_count, "null_percentage": null_percentage}
        self.null_stats = stats
        return rx.toast.success("Null value statistics updated.")

    @rx.event
    def toggle_fill_column(self, column: str):
        """Toggle a column for the fill operation."""
        if column in self.fill_columns:
            self.fill_columns.remove(column)
        else:
            self.fill_columns.append(column)

    @rx.event
    def apply_fill_nulls(self):
        """Apply the selected fill strategy to the selected columns."""
        if not self.fill_columns:
            return rx.toast.warning("Please select at least one column to fill.")
        for i in range(len(self.uploaded_files)):
            df = pd.read_json(
                io.StringIO(self.uploaded_files[i]["df_json"]), orient="split"
            )
            for col in self.fill_columns:
                if col not in df.columns:
                    continue
                try:
                    if self.fill_strategy == "custom":
                        df[col].fillna(self.fill_custom_value, inplace=True)
                    elif self.fill_strategy == "ffill":
                        df[col].fillna(method="ffill", inplace=True)
                    elif self.fill_strategy == "bfill":
                        df[col].fillna(method="bfill", inplace=True)
                    elif self.fill_strategy == "mean":
                        if pd.api.types.is_numeric_dtype(df[col]):
                            df[col].fillna(df[col].mean(), inplace=True)
                        else:
                            return rx.toast.error(
                                f"'Mean' can only be applied to numeric columns. '{col}' is not numeric."
                            )
                    elif self.fill_strategy == "median":
                        if pd.api.types.is_numeric_dtype(df[col]):
                            df[col].fillna(df[col].median(), inplace=True)
                        else:
                            return rx.toast.error(
                                f"'Median' can only be applied to numeric columns. '{col}' is not numeric."
                            )
                    elif self.fill_strategy == "mode":
                        mode_val = df[col].mode()
                        if not mode_val.empty:
                            df[col].fillna(mode_val[0], inplace=True)
                except Exception as e:
                    logging.exception(f"Error filling nulls in column {col}: {e}")
                    return rx.toast.error(f"Failed to fill nulls in '{col}'.")
            self.uploaded_files[i]["df_json"] = df.to_json(orient="split")
        self.fill_columns = []
        self.calculate_null_stats()
        return rx.toast.success("Null values filled successfully.")

    @rx.event
    def remove_null_rows_any(self):
        """Remove rows that contain any null values."""
        total_rows_before = sum((f["row_count"] for f in self.uploaded_files))
        total_rows_after = 0
        for i in range(len(self.uploaded_files)):
            df = pd.read_json(
                io.StringIO(self.uploaded_files[i]["df_json"]), orient="split"
            )
            df.dropna(inplace=True)
            self.uploaded_files[i]["row_count"] = len(df)
            self.uploaded_files[i]["df_json"] = df.to_json(orient="split")
            total_rows_after += len(df)
        rows_removed_count = total_rows_before - total_rows_after
        self.calculate_null_stats()
        return rx.toast.success(f"Removed {rows_removed_count} rows with null values.")

    @rx.event
    def find_matches(self):
        if not self.find_text:
            return rx.toast.warning("Search text cannot be empty.")
        count = 0
        for file_data in self.uploaded_files:
            df = pd.read_json(io.StringIO(file_data["df_json"]), orient="split")
            columns_to_search = (
                [self.find_replace_column]
                if self.find_replace_column != "_all_"
                else df.columns
            )
            for col in columns_to_search:
                if col in df.columns and (
                    pd.api.types.is_string_dtype(df[col]) or df[col].dtype == "object"
                ):
                    matches = df[col].str.count(
                        self.find_text,
                        flags=0 if self.case_sensitive else re.IGNORECASE,
                    )
                    count += matches.sum()
        self.match_count = count
        return rx.toast.info(f"Found {count} matches.")

    @rx.event
    def apply_find_replace(self):
        if not self.find_text:
            return rx.toast.warning("Search text cannot be empty.")
        for i in range(len(self.uploaded_files)):
            df = pd.read_json(
                io.StringIO(self.uploaded_files[i]["df_json"]), orient="split"
            )
            columns_to_search = (
                [self.find_replace_column]
                if self.find_replace_column != "_all_"
                else df.columns
            )
            for col in columns_to_search:
                if col in df.columns and (
                    pd.api.types.is_string_dtype(df[col]) or df[col].dtype == "object"
                ):
                    df[col] = df[col].str.replace(
                        self.find_text,
                        self.replace_text,
                        case=self.case_sensitive,
                        regex=self.use_regex,
                    )
            self.uploaded_files[i]["df_json"] = df.to_json(orient="split")
        self.match_count = -1
        return rx.toast.success("Find and replace operation completed.")

    @rx.event
    def toggle_case_conversion_column(self, column: str):
        if column in self.case_conversion_columns:
            self.case_conversion_columns.remove(column)
        else:
            self.case_conversion_columns.append(column)

    @rx.event
    def apply_case_conversion(self):
        if not self.case_conversion_columns:
            return rx.toast.warning("Please select at least one column.")
        for i in range(len(self.uploaded_files)):
            df = pd.read_json(
                io.StringIO(self.uploaded_files[i]["df_json"]), orient="split"
            )
            for col in self.case_conversion_columns:
                if col in df.columns and (
                    pd.api.types.is_string_dtype(df[col]) or df[col].dtype == "object"
                ):
                    if self.case_conversion_type == "upper":
                        df[col] = df[col].str.upper()
                    elif self.case_conversion_type == "lower":
                        df[col] = df[col].str.lower()
                    elif self.case_conversion_type == "title":
                        df[col] = df[col].str.title()
                    elif self.case_conversion_type == "capitalize":
                        df[col] = df[col].str.capitalize()
            self.uploaded_files[i]["df_json"] = df.to_json(orient="split")
        return rx.toast.success(f"Applied {self.case_conversion_type} case.")

    @rx.event
    def toggle_whitespace_column(self, column: str):
        if column in self.whitespace_columns:
            self.whitespace_columns.remove(column)
        else:
            self.whitespace_columns.append(column)

    @rx.event
    def apply_whitespace_operation(self):
        if not self.whitespace_columns:
            return rx.toast.warning("Please select at least one column.")
        for i in range(len(self.uploaded_files)):
            df = pd.read_json(
                io.StringIO(self.uploaded_files[i]["df_json"]), orient="split"
            )
            for col in self.whitespace_columns:
                if col in df.columns and (
                    pd.api.types.is_string_dtype(df[col]) or df[col].dtype == "object"
                ):
                    if self.whitespace_operation == "leading":
                        df[col] = df[col].str.lstrip()
                    elif self.whitespace_operation == "trailing":
                        df[col] = df[col].str.rstrip()
                    elif self.whitespace_operation == "all":
                        df[col] = df[col].str.strip()
                    elif self.whitespace_operation == "collapse":
                        df[col] = (
                            df[col].str.replace("\\s+", " ", regex=True).str.strip()
                        )
            self.uploaded_files[i]["df_json"] = df.to_json(orient="split")
        return rx.toast.success("Whitespace operation applied successfully.")

    @rx.event
    def toggle_join_column(self, column: str):
        """Toggle a column for the join operation."""
        if column in self.join_columns:
            self.join_columns.remove(column)
        else:
            self.join_columns.append(column)

    @rx.event
    def apply_split_column(self):
        """Split a column into multiple columns."""
        if not self.split_column:
            return rx.toast.warning("Please select a column to split.")
        for i in range(len(self.uploaded_files)):
            df = pd.read_json(
                io.StringIO(self.uploaded_files[i]["df_json"]), orient="split"
            )
            if self.split_column not in df.columns:
                continue
            try:
                split_data = df[self.split_column].str.split(
                    self.split_delimiter, n=self.split_num_splits, expand=True
                )
                num_new_cols = len(split_data.columns)
                new_col_names = [
                    f"{self.split_new_col_prefix}{j + 1}" for j in range(num_new_cols)
                ]
                split_data.columns = new_col_names
                for name in new_col_names:
                    if name in df.columns:
                        return rx.toast.error(
                            f"New column name '{name}' already exists. Choose a different prefix."
                        )
                df = pd.concat([df, split_data], axis=1)
                self.uploaded_files[i]["df_json"] = df.to_json(orient="split")
                self.uploaded_files[i]["columns"] = df.columns.tolist()
            except Exception as e:
                logging.exception(f"Error splitting column: {e}")
                return rx.toast.error("Failed to split column.")
        self.column_order = self.all_columns
        self.selected_columns = self.all_columns
        return rx.toast.success(f"Column '{self.split_column}' split successfully.")

    @rx.event
    def apply_join_columns(self):
        """Join multiple columns into a single column."""
        if len(self.join_columns) < 2:
            return rx.toast.warning("Please select at least two columns to join.")
        for i in range(len(self.uploaded_files)):
            df = pd.read_json(
                io.StringIO(self.uploaded_files[i]["df_json"]), orient="split"
            )
            if self.join_new_col_name in df.columns:
                return rx.toast.error(
                    f"New column name '{self.join_new_col_name}' already exists."
                )
            try:
                df[self.join_new_col_name] = (
                    df[self.join_columns]
                    .astype(str)
                    .agg(self.join_separator.join, axis=1)
                )
                self.uploaded_files[i]["df_json"] = df.to_json(orient="split")
                self.uploaded_files[i]["columns"] = df.columns.tolist()
            except Exception as e:
                logging.exception(f"Error joining columns: {e}")
                return rx.toast.error("Failed to join columns.")
        self.join_columns = []
        self.column_order = self.all_columns
        self.selected_columns = self.all_columns
        return rx.toast.success("Columns joined successfully.")

    @rx.event
    def apply_extract_substring(self):
        """Extract a substring from a column."""
        if not self.extract_column:
            return rx.toast.warning("Please select a column for extraction.")
        if self.extract_new_col_name in self.all_columns:
            return rx.toast.error(
                f"New column name '{self.extract_new_col_name}' already exists."
            )
        for i in range(len(self.uploaded_files)):
            df = pd.read_json(
                io.StringIO(self.uploaded_files[i]["df_json"]), orient="split"
            )
            if self.extract_column not in df.columns:
                continue
            try:
                df[self.extract_new_col_name] = df[self.extract_column].str[
                    self.extract_start_pos : self.extract_end_pos
                ]
                self.uploaded_files[i]["df_json"] = df.to_json(orient="split")
                self.uploaded_files[i]["columns"] = df.columns.tolist()
            except Exception as e:
                logging.exception(f"Error extracting substring: {e}")
                return rx.toast.error("Failed to extract substring.")
        self.column_order = self.all_columns
        self.selected_columns = self.all_columns
        return rx.toast.success("Substring extracted successfully.")

    @rx.event
    def add_sort_config(self):
        """Add a new sort configuration row."""
        new_config: SortConfig = {
            "id": self.next_sort_id,
            "column": "",
            "ascending": True,
        }
        self.sort_configs.append(new_config)
        self.next_sort_id += 1

    @rx.event
    def remove_sort_config(self, config_id: int):
        """Remove a sort configuration by its ID."""
        self.sort_configs = [
            config for config in self.sort_configs if config["id"] != config_id
        ]

    @rx.event
    def update_sort_config(self, config_id: int, field: str, value: Any):
        """Update a field in a sort configuration."""
        for i, config in enumerate(self.sort_configs):
            if config["id"] == config_id:
                updated_config = self.sort_configs[i].copy()
                updated_config[field] = value
                self.sort_configs[i] = updated_config
                break

    @rx.event
    def apply_sorting(self):
        """Apply the defined sorting configurations to all dataframes."""
        if not self.sort_configs:
            return rx.toast.warning("No sort rules defined.")
        sort_columns = [
            config["column"] for config in self.sort_configs if config["column"]
        ]
        sort_ascending = [
            config["ascending"] for config in self.sort_configs if config["column"]
        ]
        if not sort_columns:
            return rx.toast.warning("Please select columns for sorting.")
        for i in range(len(self.uploaded_files)):
            df = pd.read_json(
                io.StringIO(self.uploaded_files[i]["df_json"]), orient="split"
            )
            df.sort_values(by=sort_columns, ascending=sort_ascending, inplace=True)
            self.uploaded_files[i]["df_json"] = df.to_json(orient="split")
        return rx.toast.success("Data sorted successfully.")

    @rx.event
    def apply_sampling(self):
        """Apply the selected sampling method to the data and add it as a new file."""
        all_dfs = [
            pd.read_json(io.StringIO(f["df_json"]), orient="split")
            for f in self.uploaded_files
        ]
        if not all_dfs:
            return rx.toast.warning("No data to sample.")
        combined_df = pd.concat(all_dfs, ignore_index=True)
        filename_part = ""
        if self.sample_type == "random":
            sampled_df = combined_df.sample(n=self.sample_n)
            filename_part = f"random_{self.sample_n}_rows"
        elif self.sample_type == "percentage":
            sampled_df = combined_df.sample(frac=self.sample_percentage / 100)
            filename_part = f"percentage_{self.sample_percentage}_percent"
        elif self.sample_type == "top":
            sampled_df = combined_df.head(self.sample_n)
            filename_part = f"top_{self.sample_n}_rows"
        elif self.sample_type == "bottom":
            sampled_df = combined_df.tail(self.sample_n)
            filename_part = f"bottom_{self.sample_n}_rows"
        else:
            return rx.toast.error("Invalid sample type.")
        new_file_data: FileData = {
            "file_name": f"sampled_data_{filename_part}.csv",
            "row_count": len(sampled_df),
            "columns": sampled_df.columns.tolist(),
            "df_json": sampled_df.to_json(orient="split"),
        }
        self.uploaded_files.append(new_file_data)
        self.column_order = self.all_columns
        self.selected_columns = self.all_columns
        return rx.toast.success(
            f"Sampled data added as a new file with {len(sampled_df)} rows."
        )

    @rx.event
    def add_conditional_rule(self):
        """Add a new conditional transformation rule."""
        new_rule: ConditionalRule = {
            "id": self.next_conditional_id,
            "condition_column": "",
            "condition_op": "equals",
            "condition_value": "",
            "action": "set_value",
            "target_column": "",
            "action_value": "",
            "logic_combiner": "AND",
        }
        self.conditional_rules.append(new_rule)
        self.next_conditional_id += 1

    @rx.event
    def remove_conditional_rule(self, rule_id: int):
        """Remove a conditional rule by its ID."""
        self.conditional_rules = [
            rule for rule in self.conditional_rules if rule["id"] != rule_id
        ]

    @rx.event
    def update_conditional_rule(self, rule_id: int, field: str, value: str):
        """Update a field in a conditional rule."""
        for i, rule in enumerate(self.conditional_rules):
            if rule["id"] == rule_id:
                updated_rule = self.conditional_rules[i].copy()
                updated_rule[field] = value
                self.conditional_rules[i] = updated_rule
                break

    @rx.event
    def apply_conditional_transforms(self):
        """Apply all conditional transformation rules."""
        if not self.conditional_rules:
            return rx.toast.warning("No conditional rules to apply.")
        for i in range(len(self.uploaded_files)):
            df = pd.read_json(
                io.StringIO(self.uploaded_files[i]["df_json"]), orient="split"
            )
            for rule in self.conditional_rules:
                try:
                    mask = self._build_mask(df, rule)
                    action = rule["action"]
                    target_col = rule["target_column"]
                    action_val = rule["action_value"]
                    if action == "set_value":
                        df.loc[mask, target_col] = action_val
                    elif action == "copy_from_column":
                        df.loc[mask, target_col] = df.loc[mask, action_val]
                except Exception as e:
                    logging.exception(f"Error applying conditional rule: {e}")
                    return rx.toast.error(
                        f"Error with rule for column '{rule['condition_column']}'. Check parameters."
                    )
            self.uploaded_files[i]["df_json"] = df.to_json(orient="split")
        return rx.toast.success("Conditional transformations applied.")

    def _build_mask(self, df: pd.DataFrame, rule: ConditionalRule) -> pd.Series:
        col = rule["condition_column"]
        op = rule["condition_op"]
        val = rule["condition_value"]
        if op == "equals":
            return df[col].astype(str) == val
        if op == "not_equals":
            return df[col].astype(str) != val
        if op == "contains":
            return df[col].astype(str).str.contains(val, case=False, na=False)
        numeric_col = pd.to_numeric(df[col], errors="coerce")
        numeric_val = pd.to_numeric(val, errors="coerce")
        mask = pd.Series([False] * len(df), index=df.index)
        valid_comp = numeric_col.notna() & (numeric_val is not None)
        if op == "greater_than":
            mask[valid_comp] = numeric_col[valid_comp] > numeric_val
        elif op == "less_than":
            mask[valid_comp] = numeric_col[valid_comp] < numeric_val
        return mask

    @rx.event
    def toggle_melt_id_var(self, col: str):
        if col in self.melt_id_vars:
            self.melt_id_vars.remove(col)
        else:
            self.melt_id_vars.append(col)

    @rx.event
    def toggle_melt_value_var(self, col: str):
        if col in self.melt_value_vars:
            self.melt_value_vars.remove(col)
        else:
            self.melt_value_vars.append(col)

    @rx.event
    def toggle_groupby_column(self, col: str):
        if col in self.groupby_columns:
            self.groupby_columns.remove(col)
        else:
            self.groupby_columns.append(col)

    @rx.event
    def toggle_groupby_agg_column(self, col: str):
        if col in self.groupby_agg_columns:
            self.groupby_agg_columns.remove(col)
        else:
            self.groupby_agg_columns.append(col)

    @rx.event
    def apply_pivot(self):
        """Apply pivot table operation."""
        if not all([self.pivot_index, self.pivot_columns, self.pivot_values]):
            return rx.toast.warning(
                "Index, Columns, and Values must be selected for pivot."
            )
        all_dfs = [
            pd.read_json(io.StringIO(f["df_json"]), orient="split")
            for f in self.uploaded_files
        ]
        combined_df = pd.concat(all_dfs, ignore_index=True)
        try:
            pivot_df = combined_df.pivot_table(
                index=self.pivot_index,
                columns=self.pivot_columns,
                values=self.pivot_values,
                aggfunc=self.pivot_aggfunc,
            ).reset_index()
            self.uploaded_files = [
                {
                    "file_name": "pivoted_data.csv",
                    "row_count": len(pivot_df),
                    "columns": pivot_df.columns.tolist(),
                    "df_json": pivot_df.to_json(orient="split"),
                }
            ]
            self.column_order = self.all_columns
            self.selected_columns = self.all_columns
            return rx.toast.success("Pivot table created successfully.")
        except Exception as e:
            logging.exception(f"Error creating pivot table: {e}")
            return rx.toast.error("Failed to create pivot table. Check selections.")

    @rx.event
    def apply_melt(self):
        """Apply melt/unpivot operation."""
        if not self.melt_id_vars or not self.melt_value_vars:
            return rx.toast.warning(
                "ID variables and Value variables must be selected."
            )
        all_dfs = [
            pd.read_json(io.StringIO(f["df_json"]), orient="split")
            for f in self.uploaded_files
        ]
        combined_df = pd.concat(all_dfs, ignore_index=True)
        try:
            melted_df = combined_df.melt(
                id_vars=self.melt_id_vars,
                value_vars=self.melt_value_vars,
                var_name=self.melt_var_name,
                value_name=self.melt_value_name,
            )
            self.uploaded_files = [
                {
                    "file_name": "melted_data.csv",
                    "row_count": len(melted_df),
                    "columns": melted_df.columns.tolist(),
                    "df_json": melted_df.to_json(orient="split"),
                }
            ]
            self.column_order = self.all_columns
            self.selected_columns = self.all_columns
            return rx.toast.success("Data melted successfully.")
        except Exception as e:
            logging.exception(f"Error melting data: {e}")
            return rx.toast.error("Failed to melt data. Check selections.")

    @rx.event
    def apply_groupby(self):
        """Apply groupby and aggregation operation."""
        if not self.groupby_columns or not self.groupby_agg_columns:
            return rx.toast.warning(
                "Group-by columns and aggregation columns must be selected."
            )
        all_dfs = [
            pd.read_json(io.StringIO(f["df_json"]), orient="split")
            for f in self.uploaded_files
        ]
        combined_df = pd.concat(all_dfs, ignore_index=True)
        try:
            agg_dict = {col: self.groupby_aggfunc for col in self.groupby_agg_columns}
            grouped_df = (
                combined_df.groupby(self.groupby_columns).agg(agg_dict).reset_index()
            )
            self.uploaded_files = [
                {
                    "file_name": "grouped_data.csv",
                    "row_count": len(grouped_df),
                    "columns": grouped_df.columns.tolist(),
                    "df_json": grouped_df.to_json(orient="split"),
                }
            ]
            self.column_order = self.all_columns
            self.selected_columns = self.all_columns
            return rx.toast.success("Data grouped and aggregated successfully.")
        except Exception as e:
            logging.exception(f"Error grouping data: {e}")
            return rx.toast.error(
                "Failed to group data. Ensure agg function is valid for column types."
            )

    @rx.event
    def toggle_datetime_column(self, col: str):
        if col in self.datetime_columns:
            self.datetime_columns.remove(col)
        else:
            self.datetime_columns.append(col)

    @rx.event
    def toggle_extract_component(self, component: str):
        if component in self.extract_components:
            self.extract_components.remove(component)
        else:
            self.extract_components.append(component)

    @rx.event
    def extract_date_components(self):
        """Extract components from date columns."""
        if not self.datetime_columns:
            return rx.toast.warning("Please select at least one date column.")
        for i in range(len(self.uploaded_files)):
            df = pd.read_json(
                io.StringIO(self.uploaded_files[i]["df_json"]), orient="split"
            )
            for col in self.datetime_columns:
                if col not in df.columns:
                    continue
                try:
                    date_series = pd.to_datetime(df[col], errors="coerce")
                    for comp in self.extract_components:
                        new_col_name = f"{col}_{comp}"
                        if new_col_name in df.columns:
                            continue
                        if comp == "year":
                            df[new_col_name] = date_series.dt.year
                        elif comp == "month":
                            df[new_col_name] = date_series.dt.month
                        elif comp == "day":
                            df[new_col_name] = date_series.dt.day
                        elif comp == "weekday":
                            df[new_col_name] = date_series.dt.weekday
                        elif comp == "hour":
                            df[new_col_name] = date_series.dt.hour
                        elif comp == "minute":
                            df[new_col_name] = date_series.dt.minute
                except Exception as e:
                    logging.exception(
                        f"Error extracting date component from {col}: {e}"
                    )
                    return rx.toast.error(f"Failed to process date column '{col}'.")
            self.uploaded_files[i]["df_json"] = df.to_json(orient="split")
            self.uploaded_files[i]["columns"] = df.columns.tolist()
        self.column_order = self.all_columns
        self.selected_columns = self.all_columns
        return rx.toast.success("Date components extracted.")

    @rx.event
    def calculate_date_difference(self):
        """Calculate difference between two date columns."""
        if not self.date_diff_col1 or not self.date_diff_col2:
            return rx.toast.warning(
                "Please select two columns to calculate the difference."
            )
        for i in range(len(self.uploaded_files)):
            df = pd.read_json(
                io.StringIO(self.uploaded_files[i]["df_json"]), orient="split"
            )
            if (
                self.date_diff_col1 not in df.columns
                or self.date_diff_col2 not in df.columns
            ):
                continue
            try:
                col1 = pd.to_datetime(df[self.date_diff_col1], errors="coerce")
                col2 = pd.to_datetime(df[self.date_diff_col2], errors="coerce")
                df[self.date_diff_new_col] = (col1 - col2).dt.days
                self.uploaded_files[i]["df_json"] = df.to_json(orient="split")
                self.uploaded_files[i]["columns"] = df.columns.tolist()
            except Exception as e:
                logging.exception(f"Error calculating date difference: {e}")
                return rx.toast.error("Failed to calculate date difference.")
        self.column_order = self.all_columns
        self.selected_columns = self.all_columns
        return rx.toast.success("Date difference calculated.")

    @rx.event
    def apply_date_arithmetic(self):
        """Add or subtract a time delta from a date column."""
        if not self.date_arith_column:
            return rx.toast.warning("Please select a date column for arithmetic.")
        for i in range(len(self.uploaded_files)):
            df = pd.read_json(
                io.StringIO(self.uploaded_files[i]["df_json"]), orient="split"
            )
            if self.date_arith_column not in df.columns:
                continue
            try:
                date_series = pd.to_datetime(
                    df[self.date_arith_column], errors="coerce"
                )
                delta = pd.to_timedelta(
                    self.date_arith_value, unit=self.date_arith_unit.rstrip("s")
                )
                if self.date_arith_op == "add":
                    df[self.date_arith_column] = date_series + delta
                else:
                    df[self.date_arith_column] = date_series - delta
                self.uploaded_files[i]["df_json"] = df.to_json(orient="split")
            except Exception as e:
                logging.exception(f"Error applying date arithmetic: {e}")
                return rx.toast.error("Failed to apply date arithmetic.")
        return rx.toast.success("Date arithmetic applied.")

    @rx.event
    def toggle_label_encode_column(self, col: str):
        if col in self.label_encode_columns:
            self.label_encode_columns.remove(col)
        else:
            self.label_encode_columns.append(col)

    @rx.event
    def apply_label_encoding(self):
        """Apply label encoding to selected columns."""
        if not self.label_encode_columns:
            return rx.toast.warning("Please select columns for label encoding.")
        mappings = {}
        for i in range(len(self.uploaded_files)):
            df = pd.read_json(
                io.StringIO(self.uploaded_files[i]["df_json"]), orient="split"
            )
            for col in self.label_encode_columns:
                if col not in df.columns:
                    continue
                new_col_name = f"{col}_encoded"
                codes, uniques = pd.factorize(df[col])
                df[new_col_name] = codes
                mappings[col] = {str(k): v for v, k in enumerate(uniques)}
            self.uploaded_files[i]["df_json"] = df.to_json(orient="split")
            self.uploaded_files[i]["columns"] = df.columns.tolist()
        self.label_mappings = mappings
        self.column_order = self.all_columns
        self.selected_columns = self.all_columns
        return rx.toast.success("Label encoding applied.")

    @rx.event
    def toggle_onehot_column(self, col: str):
        if col in self.onehot_columns:
            self.onehot_columns.remove(col)
        else:
            self.onehot_columns.append(col)

    @rx.event
    def apply_onehot_encoding(self):
        """Apply one-hot encoding to selected columns."""
        if not self.onehot_columns:
            return rx.toast.warning("Please select columns for one-hot encoding.")
        for i in range(len(self.uploaded_files)):
            df = pd.read_json(
                io.StringIO(self.uploaded_files[i]["df_json"]), orient="split"
            )
            try:
                dummies = pd.get_dummies(
                    df[self.onehot_columns], prefix=self.onehot_columns, prefix_sep="_"
                )
                df = pd.concat([df.drop(columns=self.onehot_columns), dummies], axis=1)
                self.uploaded_files[i]["df_json"] = df.to_json(orient="split")
                self.uploaded_files[i]["columns"] = df.columns.tolist()
            except Exception as e:
                logging.exception(f"Error during one-hot encoding: {e}")
                return rx.toast.error("One-hot encoding failed. Check columns.")
        self.column_order = self.all_columns
        self.selected_columns = self.all_columns
        self.onehot_columns = []
        return rx.toast.success("One-hot encoding applied.")

    @rx.event
    def toggle_remove_special_column(self, col: str):
        if col in self.remove_special_columns:
            self.remove_special_columns.remove(col)
        else:
            self.remove_special_columns.append(col)

    @rx.event
    def apply_remove_special_chars(self):
        """Remove special characters from selected columns."""
        if not self.remove_special_columns:
            return rx.toast.warning("Please select columns to clean.")
        try:
            re.compile(self.special_char_pattern)
        except re.error as e:
            logging.exception(f"Invalid regex pattern: {e}")
            return rx.toast.error("Invalid Regex pattern for special characters.")
        for i in range(len(self.uploaded_files)):
            df = pd.read_json(
                io.StringIO(self.uploaded_files[i]["df_json"]), orient="split"
            )
            for col in self.remove_special_columns:
                if col in df.columns:
                    df[col] = (
                        df[col]
                        .astype(str)
                        .str.replace(self.special_char_pattern, "", regex=True)
                    )
            self.uploaded_files[i]["df_json"] = df.to_json(orient="split")
        return rx.toast.success("Special characters removed.")