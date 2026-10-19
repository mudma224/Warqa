"""Test de fumée : vérifie que le dataset DocILE se charge dans le conteneur."""
from pathlib import Path

from docile.dataset import Dataset

DATA_PATH = Path("/app/data/docile")


def main() -> None:
    val = Dataset("val", DATA_PATH)
    print(f"[OK] Split 'val' charge : {len(val)} documents")

    doc = val[0]
    ann = doc.annotation
    print(f"[OK] Premier document : {doc.docid}")
    print(f"     Pages : {ann.page_count} | Type : {ann.document_type} | "
          f"Langue : {ann.language} | Devise : {ann.currency}")

    fields = ann.fields
    print(f"[OK] Champs KILE annotes : {len(fields)}")
    for f in fields[:5]:
        print(f"     - {f.fieldtype} | page {f.page} | bbox {f.bbox} | texte : {str(f.text)[:40]}")

    ocr_words = doc.ocr.get_all_words(page=0)
    print(f"[OK] Mots OCR pre-calcules (page 0) : {len(ocr_words)}")

    print("SMOKE TEST REUSSI")


if __name__ == "__main__":
    main()
