from fastapi import FastAPI

app = FastAPI()

@app.get("/filtration")
def filtration(m0: float = 1000, x0: float = 0.10, residus: float = 20):
    m1 = m0 - residus
    x1 = (m0 * x0) / m1
    return {
        "m1_kg_h": m1,
        "x1": round(x1, 4),
        "concentration_pct": round(100 * x1, 2),
        "erreur_bilan_global": m0 - (m1 + residus),
        "erreur_bilan_solubles": m0 * x0 - m1 * x1,
    }