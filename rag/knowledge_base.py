"""
ORCA Retrieval-Augmented Generation (RAG) Scientific Knowledge Base
Retrieves domain scientific reference material for ecological stress factors.
"""

KNOWLEDGE_BASE = {
    "thermal": {
        "title": "NOAA Coral Reef Watch & SST Stress Thresholds",
        "reference": "Glynn et al., Marine Ecology Progress Series",
        "excerpt": "Sea surface temperature anomalies exceeding 1.0 °C above regional summer maximums induce thermal bleaching stress in shallow tropical coral ecosystems and accelerate marine fauna metabolic respiration."
    },
    "hypoxia": {
        "title": "UNEP Marine Hypoxia & Anoxia Assessment Manual",
        "reference": "Diaz & Rosenberg, Science Journal",
        "excerpt": "Dissolved oxygen concentrations falling below 4.0 mg/L indicate hypoxic stress, while levels under 2.0 mg/L induce rapid benthic invertebrate mortality and pelagic fish displacement."
    },
    "eutrophication": {
        "title": "INCOIS Harmful Algal Bloom (HAB) Technical Guide",
        "reference": "ISRO / INCOIS Coastal Ecosystem Bulletin",
        "excerpt": "Nutrient loading coupled with solar irradiance fuels phytoplankton blooms. High Chlorophyll-a (>6 µg/L) and algae indices (>50) precede severe oxygen depletion during bloom senescence."
    },
    "acidification": {
        "title": "IPCC Oceans & Cryosphere Special Report",
        "reference": "IPCC SROCC Ch. 5",
        "excerpt": "Ocean pH depression below 7.8 indicates ocean acidification, decreasing aragonite saturation states critical for calcifying marine organisms and reef architecture."
    }
}

def retrieve_scientific_context(topic_query):
    """
    Retrieves supporting domain literature citations based on query topic.
    """
    query_lower = topic_query.lower()
    results = []

    for key, doc in KNOWLEDGE_BASE.items():
        if key in query_lower or any(w in query_lower for w in [doc["title"].lower(), doc["excerpt"].lower()]):
            results.append(doc)

    if not results:
        results = [KNOWLEDGE_BASE["thermal"], KNOWLEDGE_BASE["hypoxia"]]

    return results
