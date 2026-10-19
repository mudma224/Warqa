"""Coeur logique de la demo Warqa : chargement des donnees, curation, rendu.

Separe de l'interface Streamlit pour pouvoir etre teste sans navigateur.
Chemin executes dans le conteneur warqa (montages du docker-compose).
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from docile.dataset import CachingConfig, Dataset

DATA_PATH = Path("/app/data/docile")
PREDICTIONS_PATH = Path(
    "/app/models/layoutlmv3-ours/predictions/layoutlmv3_ours/val_predictions_KILE.json"
)
DEMO_DOCS_PATH = Path(__file__).parent / "demo_docs.json"

# Codes DocILE -> libelles francais, dans l'ordre d'affichage de la fiche
FIELD_LABELS_FR: list[tuple[str, str]] = [
    ("vendor_name", "Fournisseur"),
    ("vendor_address", "Adresse fournisseur"),
    ("customer_billing_name", "Client"),
    ("document_id", "Numéro de facture"),
    ("date_issue", "Date d'émission"),
    ("date_due", "Date d'échéance"),
    ("order_id", "Numéro de commande"),
    ("amount_total_net", "Total HT"),
    ("amount_total_tax", "Total TVA"),
    ("amount_total_gross", "Total TTC"),
    ("amount_due", "Net à payer"),
    ("currency_code_amount_due", "Devise"),
    ("payment_reference", "Référence de paiement"),
    ("vendor_tax_id", "Identifiant fiscal fournisseur"),
]
LABELS = dict(FIELD_LABELS_FR)
KEY_CODES = [code for code, _ in FIELD_LABELS_FR]


def load_dataset() -> Dataset:
    """Split val, annotations seules (rapide : pas d'OCR, pas d'images au chargement)."""
    return Dataset("val", DATA_PATH, load_ocr=False, cache_images=CachingConfig.OFF)


def load_predictions() -> dict[str, list[dict[str, Any]]]:
    with open(PREDICTIONS_PATH, encoding="utf-8") as fh:
        return json.load(fh)


def load_demo_docs() -> list[dict[str, Any]]:
    with open(DEMO_DOCS_PATH, encoding="utf-8") as fh:
        return json.load(fh)


def predictions_for_page(
    all_predictions: dict[str, list[dict[str, Any]]], docid: str, page: int = 0
) -> list[dict[str, Any]]:
    return [p for p in all_predictions.get(docid, []) if p.get("page") == page]


def build_form_rows(preds_page: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Construit les lignes de la fiche (champs connus, meilleure prediction par code)."""
    best: dict[str, dict[str, Any]] = {}
    for pred in preds_page:
        code = pred.get("fieldtype")
        if code not in LABELS:
            continue
        score = pred.get("score") or 0.0
        if code not in best or score > (best[code].get("score") or 0.0):
            best[code] = pred
    rows = []
    for code, label in FIELD_LABELS_FR:
        if code in best:
            pred = best[code]
            rows.append(
                {
                    "code": code,
                    "champ": label,
                    "texte": (pred.get("text") or "").strip().replace("\n", " · "),
                    "confiance": pred.get("score"),
                    "bbox": pred.get("bbox"),
                    "page": pred.get("page", 0),
                }
            )
    return rows


def confidence_color(score: float | None) -> tuple[str, str]:
    """(couleur hex du cadre, etiquette) selon le score de confiance."""
    if score is None:
        return "#6b7280", "—"
    if score >= 0.9:
        return "#16a34a", "élevée"
    if score >= 0.6:
        return "#f59e0b", "moyenne"
    return "#dc2626", "faible"


def render_page_with_boxes(image: Any, preds_page: list[dict[str, Any]]) -> Any:
    """Dessine les boites predites sur l'image de la page (copie, original intact)."""
    from PIL import Image, ImageDraw

    img = image.convert("RGB") if image.mode != "RGB" else image.copy()
    draw = ImageDraw.Draw(img)
    width, height = img.size
    for pred in preds_page:
        left, top, right, bottom = pred["bbox"]
        color, _ = confidence_color(pred.get("score"))
        draw.rectangle(
            [left * width, top * height, right * width, bottom * height],
            outline=color,
            width=max(2, width // 400),
        )
    return img


def export_json(docid: str, rows: list[dict[str, Any]]) -> str:
    """Export au format Warqa (champs francais, boites normalisees, confiance)."""
    from datetime import datetime, timezone

    payload = {
        "docid": docid,
        "source": "DocILE val — démonstration hors ligne",
        "date_export": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "champs": [
            {
                "champ": r["champ"],
                "code": r["code"],
                "page": r["page"],
                "boite": [round(v, 4) for v in (r["bbox"] or [])],
                "texte": r["texte"],
                "confiance": round(r["confiance"], 4) if r["confiance"] is not None else None,
            }
            for r in rows
        ],
    }
    return json.dumps(payload, ensure_ascii=False, indent=2)
