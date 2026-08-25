import pandas as pd


class DataAgent:

    def __init__(self, data):
        self.data = data

    def ask(self, question):

        if self.data is None or self.data.empty:
            return "I don't have any data to analyze yet. Please upload your utility data first."

        question = question.lower().strip()

        df = self.data.copy()

        # -------------------------------------------------
        # BASIC DATASET INFORMATION
        # -------------------------------------------------

        if "how many rows" in question:
            return f"The dataset contains {len(df):,} rows."

        if "how many columns" in question:
            return f"The dataset contains {len(df.columns)} columns."

        if "columns" in question:
            return (
                "The available columns are:\n\n"
                + "\n".join(f"- {col}" for col in df.columns)
            )

        # -------------------------------------------------
        # MISSING VALUES
        # -------------------------------------------------

        if "missing" in question:
            missing = df.isna().sum()
            missing = missing[missing > 0]

            if missing.empty:
                return "There are no missing values in the dataset."

            result = "\n".join(
                f"- {column}: {count}"
                for column, count in missing.items()
            )

            return f"Missing values found:\n\n{result}"

        # -------------------------------------------------
        # DUPLICATES
        # -------------------------------------------------

        if "duplicate" in question:
            count = int(df.duplicated().sum())

            if count == 0:
                return "There are no duplicate rows."

            return f"There are {count} duplicate rows."

        # -------------------------------------------------
        # NUMERIC ANALYSIS
        # -------------------------------------------------

        numeric_columns = df.select_dtypes(
            include="number"
        ).columns.tolist()

        if "average" in question or "mean" in question:

            if not numeric_columns:
                return "I could not find numeric columns to calculate an average."

            results = []

            for column in numeric_columns:
                value = df[column].mean()

                if pd.notna(value):
                    results.append(
                        f"- {column}: {value:,.2f}"
                    )

            return (
                "Average values in the dataset:\n\n"
                + "\n".join(results)
            )

        # -------------------------------------------------
        # MAXIMUM
        # -------------------------------------------------

        if (
            "highest" in question
            or "maximum" in question
            or "max" in question
        ):

            if not numeric_columns:
                return "I could not find numeric columns."

            results = []

            for column in numeric_columns:
                value = df[column].max()

                if pd.notna(value):
                    results.append(
                        f"- {column}: {value:,.2f}"
                    )

            return (
                "Highest values:\n\n"
                + "\n".join(results)
            )

        # -------------------------------------------------
        # MINIMUM
        # -------------------------------------------------

        if (
            "lowest" in question
            or "minimum" in question
            or "min" in question
        ):

            if not numeric_columns:
                return "I could not find numeric columns."

            results = []

            for column in numeric_columns:
                value = df[column].min()

                if pd.notna(value):
                    results.append(
                        f"- {column}: {value:,.2f}"
                    )

            return (
                "Lowest values:\n\n"
                + "\n".join(results)
            )

        # -------------------------------------------------
        # SUMMARY
        # -------------------------------------------------

        if (
            "summary" in question
            or "summarize" in question
            or "overview" in question
        ):

            summary = []

            summary.append(
                f"Dataset contains {len(df):,} rows "
                f"and {len(df.columns)} columns."
            )

            if numeric_columns:

                summary.append("\nNumeric data:")

                for column in numeric_columns:

                    avg = df[column].mean()
                    maximum = df[column].max()
                    minimum = df[column].min()

                    summary.append(
                        f"- {column}: "
                        f"average {avg:,.2f}, "
                        f"minimum {minimum:,.2f}, "
                        f"maximum {maximum:,.2f}"
                    )

            return "\n".join(summary)

        # -------------------------------------------------
        # DEFAULT RESPONSE
        # -------------------------------------------------

        return (
            "I couldn't determine the answer from that question yet.\n\n"
            "Try asking about:\n"
            "- average consumption\n"
            "- highest values\n"
            "- lowest values\n"
            "- missing values\n"
            "- duplicate rows\n"
            "- columns\n"
            "- dataset summary"
        )