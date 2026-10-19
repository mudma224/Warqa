"""Test de fumée : vérifie que le dataset DocILE se charge dans le conteneur."""
from pathlib import Path

from docile.dataset import Dataset

DATA_PATH = Path("/app/data/docile")


def main() -> None:
    val = Dataset("val", DATA_PATH)
    print(f"[OK] Split 'val' charge : {len(val)} documents")

    doc = val[0]
    print(f"[OK] Premier document : {doc.docid} ({len(doc.pages)} page(s))")

    try:
        fields = doc.annotation.fields.get_all()
        print(f"[OK] Champs annotes : {len(fields)}")
        for f in fields[:5]:
            bbox = [round(v, 3) for v in f.bbox]
            print(f"     - {f.fieldtype} | page {f.page} | bbox {bbox} | texte: {str(f.text)[:40]}")
    except AttributeError:
        attrs = [a for a in dir(doc.annotation.fields) if not a.startswith("_")]
        print(f"[!] API champs inattendue. Attributs disponibles : {attrs[:15]}")

    print("SMOKE TEST REUSSI")


if __name__ == "__main__":
    main()
