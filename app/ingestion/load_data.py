import pandas as pd
from datasets import load_dataset


def fetch_ag_news_data(split: str = "train", limit: int = 100):
    """Downloads AG News dataset from Hugging Face and returns it as a DataFrame."""
    dataset = load_dataset("fancyzhx/ag_news", split=split)
    df = pd.DataFrame(dataset)

    label_mapping = {
        0: "World",
        1: "Sports",
        2: "Business",
        3: "Sci/Tech",
    }
    df["label_name"] = df["label"].map(label_mapping)

    if limit:
        df = df.head(limit)

    return df


if __name__ == "__main__":
    df_samples = fetch_ag_news_data(limit=5)
    print("Data loaded successfully!")
    print(df_samples[["label_name", "text"]])