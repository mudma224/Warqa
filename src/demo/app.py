"""Demo Warqa — interface Streamlit (presentation aux cabinets pilotes).

Lancement : docker compose up -d demo  ->  http://localhost:8501
"""
from __future__ import annotations

import streamlit as st

import demo_core as core

st.set_page_config(page_title="Warqa — lecture automatique de factures", page_icon="🧾", layout="wide")

st.markdown(
    """
    <div style="display:flex;align-items:baseline;gap:14px;border-bottom:2px solid #d4875a;padding-bottom:8px;">
      <span style="font-size:26px;font-weight:700;">Warqa</span>
      <span style="font-size:16px;color:#555;">lecture automatique des factures — prototype de démonstration</span>
    </div>
    """,
    unsafe_allow_html=True,
)
st.caption("Entraîné sur le benchmark international DocILE · fonctionne hors ligne · "
           "aucune donnée ne quitte cet ordinateur")

if "reading_done" not in st.session_state:
    st.session_state.reading_done = False


@st.cache_resource(show_spinner="Chargement du corpus de démonstration…")
def get_dataset():
    return core.load_dataset()


@st.cache_resource(show_spinner=False)
def get_predictions():
    return core.load_predictions()


@st.cache_data(show_spinner=False)
def get_demo_docs():
    return core.load_demo_docs()


@st.cache_data(show_spinner="Rendu de la page…")
def render_page(docid: str, page: int):
    dataset = get_dataset()
    doc = next(d for d in dataset if d.docid == docid)
    image = doc.page_image(page)
    preds = core.predictions_for_page(get_predictions(), docid, page)
    return core.render_page_with_boxes(image, preds)


dataset = get_dataset()
predictions = get_predictions()
demo_docs = get_demo_docs()

with st.sidebar:
    st.subheader("1 — Choisissez une facture")
    options = {
        f"{d['vendor']} · {d['total']} ({d['doctype']})": d for d in demo_docs
    }
    choice = st.selectbox("Corpus de démonstration", list(options.keys()), label_visibility="collapsed")
    selected = options[choice]
    st.subheader("2 — Lancez la lecture")
    run = st.button("▶ Lire la facture automatiquement", type="primary", use_container_width=True)
    if run:
        st.session_state.reading_done = True
    st.markdown("---")
    st.markdown(
        "**Légende des cadres**\n"
        "- 🟩 confiance élevée\n"
        "- 🟧 confiance moyenne\n"
        "- 🟥 confiance faible\n\n"
        "*La fiche reste toujours vérifiable par un humain avant export — "
        "c'est le principe de Warqa.*"
    )

doc = next(d for d in dataset if d.docid == selected["docid"])

if not st.session_state.reading_done:
    st.info("Choisissez une facture dans le menu de gauche, puis cliquez sur "
            "« Lire la facture automatiquement ».")
    st.stop()

preds_page = core.predictions_for_page(predictions, selected["docid"], page=0)
rows = core.build_form_rows(preds_page)
image = render_page(selected["docid"], 0)

col_img, col_form = st.columns([1.25, 1])
with col_img:
    st.markdown("**Facture originale** (zones reconnues encadrées)")
    st.image(image, width="stretch")
with col_form:
    st.markdown("**Fiche extraite automatiquement**")
    if rows:
        st.dataframe(
            [
                {
                    "Champ": r["champ"],
                    "Valeur": r["texte"] or "—",
                    "Confiance": f"{r['confiance']*100:.0f} %" if r["confiance"] is not None else "—",
                }
                for r in rows
            ],
            width="stretch",
            hide_index=True,
        )
    else:
        st.warning("Aucun champ reconnu sur ce document.")

st.divider()
left, right = st.columns([1, 1])
with left:
    st.markdown("##### Données exportables (JSON)")
    st.caption("Même structure que l'export de la version finale (fiche + boîtes + confiance).")
with right:
    payload = core.export_json(selected["docid"], rows)
    st.download_button(
        "Télécharger la fiche (JSON)",
        data=payload,
        file_name=f"warqa_{selected['docid'][:12]}.json",
        mime="application/json",
        width="stretch",
    )
with st.expander("Aperçu du JSON"):
    st.code(payload, language="json")
