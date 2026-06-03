"""Financial text signal package."""

from quant_mas.text.data_schema import FinancialTextRecord, TextSignalRecord
from quant_mas.text.dataset import (
    build_synthetic_text_records,
    load_text_records,
    split_text_records_by_time,
)
from quant_mas.text.finbert_baseline import (
    FinBERTSentimentClassifier,
    SentimentClassifier,
    predict_sentiment,
)
from quant_mas.text.lora_finetune import train_lora_text_classifier
from quant_mas.text.mock_classifier import MockSentimentClassifier

__all__ = [
    "FinancialTextRecord",
    "FinBERTSentimentClassifier",
    "MockSentimentClassifier",
    "SentimentClassifier",
    "TextSignalRecord",
    "build_synthetic_text_records",
    "load_text_records",
    "predict_sentiment",
    "split_text_records_by_time",
    "train_lora_text_classifier",
]
