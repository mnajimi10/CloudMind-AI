import json

from pipeline.config import (
    CLEAN_FILE,
    REJECTED_FILE,
    REPORT_FILE,
    PROCESSED_DIR,
    QUARANTINE_DIR,
    REPORT_DIR,
)


def load_data(valid_df, rejected_df, rules, total_rows):
    for directory in [
        PROCESSED_DIR,
        QUARANTINE_DIR,
        REPORT_DIR,
    ]:
        directory.mkdir(parents=True, exist_ok=True)

    valid_output = valid_df.drop(
        columns=["_source_row", "ParsedTags"],
        errors="ignore"
    ).copy()

    rejected_output = rejected_df.drop(
        columns=["_source_row", "ParsedTags"],
        errors="ignore"
    ).copy()

    # Standardize date output
    for frame in [valid_output, rejected_output]:
        if "Date" in frame.columns:
            frame["Date"] = frame["Date"].dt.strftime("%Y-%m-%d")

    valid_output.to_csv(
        CLEAN_FILE,
        index=False,
        encoding="utf-8-sig"
    )

    rejected_output.to_csv(
        REJECTED_FILE,
        index=False,
        encoding="utf-8-sig"
    )

    report = {
        "total_rows": int(total_rows),
        "valid_rows": int(len(valid_df)),
        "rejected_rows": int(len(rejected_df)),
        "quality_percentage": round(
            len(valid_df) / total_rows * 100, 2
        ) if total_rows else 0,
        "rules": rules,
    }

    REPORT_FILE.write_text(
        json.dumps(report, indent=4, ensure_ascii=False),
        encoding="utf-8"
    )

    print("[LOAD] Output files generated")
    return report