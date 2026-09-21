import pandas as pd
from datasets import load_dataset


def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:

    df = df.dropna(subset=["text", "label"]).copy()

    df = df.drop_duplicates(subset=["text"])

    df["text"] = (
        df["text"]
        .astype(str)
        .str.replace(r"\s+", " ", regex=True)
        .str.strip()
    )

    df = df[df["text"].str.len() > 0]

    return df


def fetch_ag_news_data(
    split: str = "train",
    limit: int = 100,
    shuffle: bool = True,
    seed: int = 42
):
    
    dataset = load_dataset("fancyzhx/ag_news", split=split)

   
    df = pd.DataFrame(dataset)

    df = clean_dataframe(df)

    label_mapping = {
        0: "World",
        1: "Sports",
        2: "Business",
        3: "Sci/Tech"
    }

    df["label_name"] = df["label"].map(label_mapping)

    if shuffle:
        df = df.sample(
            frac=1,
            random_state=seed
        ).reset_index(drop=True)


    if limit is not None:
        df = df.head(limit)

    df = df.reset_index(drop=True)

    return df


if __name__ == "__main__":
    df_samples = fetch_ag_news_data(limit=5)

    print("Data loaded and cleaned successfully!")
    print("\nDataset shape:", df_samples.shape)

    print("\nCategory distribution:")
    print(df_samples["label_name"].value_counts())

    print("\nSample data:")
    print(df_samples[["label_name", "text"]])