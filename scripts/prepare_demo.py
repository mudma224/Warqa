"""Curation du jeu de demo : selectionne des documents a une page, riches en champs cles.

Affiche sur stdout le JSON des documents retenus (rediriger vers
src/demo/demo_docs.json) ; les diagnostics vont sur stderr.
Execution : docker compose exec -T docile uv run python scripts/prepare_demo.py > src/demo/demo_docs.json
"""
from __future__ import annotations

import json
import sys

from docile.dataset import CachingConfig, Dataset

DATA_PATH = "/app/data/docile"
PREDICTIONS_PATH = (
    "/app/models/layoutlmv3-ours/predictions/layoutlmv3_ours/val_predictions_KILE.json"
)
TARGET = 15

KEY_CODES = {
    "vendor_name", "document_id", "date_issue", "amount_total_gross", "amount_due",
    "amount_total_tax", "amount_total_net", "customer_billing_name", "order_id",
    "date_due", "vendor_address", "currency_code_amount_due",
}


def best_text(preds: list[dict], code: str) -> str:
    texts = [
        ((p.get("score") or 0.0), (p.get("text") or "").strip())
        for p in preds
        if p.get("fieldtype") == code
    ]
    return max(texts, default=(0.0, ""))[1].replace("\n", " ")[:34]


def main() -> None:
    dataset = Dataset("val", DATA_PATH, load_ocr=False, cache_images=CachingConfig.OFF)
    with open(PREDICTIONS_PATH, encoding="utf-8") as fh:
        predictions = json.load(fh)

    candidates = []
    for idx, doc in enumerate(dataset):
        ann = doc.annotation
        if ann.page_count != 1:
            continue
        preds = [p for p in predictions.get(doc.docid, []) if p.get("page") == 0]
        strong = [
            p for p in preds
            if p.get("fieldtype") in KEY_CODES and (p.get("score") or 0.0) >= 0.5
        ]
        distinct = {p["fieldtype"] for p in strong}
        if len(distinct) < 5 or len(preds) > 18:
            continue

        vendor = best_text(preds, "vendor_name") or doc.docid[:12]
        total = best_text(preds, "amount_total_gross") or best_text(preds, "amount_due")
        candidates.append({
            "docid": doc.docid,
            "idx": idx,
            "doctype": ann.document_type,
            "language": ann.language,
            "vendor": vendor or doc.docid[:12],
            "total": total or "-",
            "n_key": len(distinct),
            "avg_score": sum((p.get("score") or 0.0) for p in strong) / len(strong),
        })

    candidates.sort(
        key=lambda c: (c["doctype"] == "invoice", c["n_key"], c["avg_score"]),
        reverse=True,
    )
    selected = candidates[:TARGET]

    print(json.dumps(selected, ensure_ascii=False, indent=2))
    print(
        f"[stderr] {len(candidates)} candidats, {len(selected)} retenus",
        file=sys.stderr,
    )


if __name__ == "__main__":
    main()
