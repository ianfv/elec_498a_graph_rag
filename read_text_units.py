import pandas as pd

GRAPHRAG_FOLDER = "test_data/output"


def main():
    text_df = pd.read_parquet(
        f"{GRAPHRAG_FOLDER}/text_units.parquet",
        columns=["id", "text", "n_tokens", "document_ids"],
        engine="fastparquet",
    )
    print("text unit table")
    print(text_df)
    print("-" * 160)

    entity_df = pd.read_parquet(
        f"{GRAPHRAG_FOLDER}/entities.parquet",
        columns=["title", "type", "description", "text_unit_ids", "degree"],
        engine="fastparquet",
    )

    print("entitiy table")
    print(entity_df)


if __name__ == "__main__":
    main()
