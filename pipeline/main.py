from pipeline.extract import extract_data
from pipeline.transform import transform_data
from pipeline.validate import validate_data
from pipeline.load import load_data


def run_pipeline():
    print("\n" + "=" * 55)
    print("CLOUDMIND AI - ETL PIPELINE")
    print("=" * 55)

    # 1. Extract
    raw_df = extract_data()
    total_rows = len(raw_df)

    # 2. Transform
    transformed_df = transform_data(raw_df)

    # 3. Validate
    valid_df, rejected_df, rules = validate_data(
        transformed_df
    )

    # 4. Load
    report = load_data(
        valid_df,
        rejected_df,
        rules,
        total_rows
    )

    print("\n" + "=" * 55)
    print("ETL PIPELINE COMPLETED")
    print("=" * 55)

    print(f"Total rows: {report['total_rows']}")
    print(f"Valid rows: {report['valid_rows']}")
    print(f"Rejected rows: {report['rejected_rows']}")
    print(f"Quality: {report['quality_percentage']}%")

    return report


if __name__ == "__main__":
    run_pipeline()