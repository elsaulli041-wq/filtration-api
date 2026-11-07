from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse

app = FastAPI(title="Calcul de filtration")

PAGE = r"""<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Calcul de filtration</title>
<style>
:root{--bg:#f4f6fb;--card:#fff;--txt:#1f2937;--mut:#6b7280;--acc:#2563eb;--ok:#16a34a;--err:#dc2626}
*{box-sizing:border-box}
body{margin:0;font-family:system-ui,sans-serif;background:var(--bg);color:var(--txt)}
.wrap{max-width:720px;margin:0 auto;padding:24px 16px}
h1{font-size:1.6rem;margin:0 0 4px}
.sub{color:var(--mut);margin:0 0 20px}
.card{background:var(--card);border-radius:14px;padding:20px;box-shadow:0 2px 10px rgba(0,0,0,.06);margin-bottom:16px}
label{display:block;font-weight:600;margin-top:12px}
small{color:var(--mut);font-weight:400}
input{width:100%;padding:10px 12px;margin-top:6px;border:1px solid #d1d5db;border-radius:8px;font-size:1rem}
button{margin-top:18px;width:100%;padding:12px;border:0;border-radius:8px;background:var(--acc);color:#fff;font-size:1rem;font-weight:600;cursor:pointer}
button:hover{opacity:.9}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:12px}
.res{background:var(--bg);border-radius:10px;padding:14px}
.res span{display:block;color:var(--mut);font-size:.85rem;margin-bottom:4px}
.res b{font-size:1.4rem}
.check{margin:14px 0 0;font-weight:600}
.ok{color:var(--ok)}.err{color:var(--err)}
footer{text-align:center;color:var(--mut);font-size:.85rem}
footer a{color:var(--acc)}
</style>
</head>
<body>
<div class="wrap">
  <h1>Opération 1 : Filtration</h1>
  <p class="sub">Bilan matière sur le filtre. Entrez vos données puis cliquez sur Calculer.</p>

  <div class="card">
    <label>Débit de jus brut m0 <small>(kg/h)</small>
      <input id="m0" type="number" value="1000" step="any"></label>
    <label>Fraction de solubles x0 <small>(entre 0 et 1)</small>
      <input id="x0" type="number" value="0.10" step="any"></label>
    <label>Résidus retenus par le filtre <small>(kg/h)</small>
      <input id="residus" type="number" value="20" step="any"></label>
    <button onclick="calculer()">Calculer</button>
  </div>

  <div class="card" id="out" hidden>
    <div class="grid" id="grid">
      <div class="res"><span>Débit après filtration m1</span><b id="m1"></b> kg/h</div>
      <div class="res"><span>Fraction de solubles x1</span><b id="x1"></b></div>
      <div class="res"><span>Concentration en solubles</span><b id="c"></b> %</div>
    </div>
    <p class="check" id="check"></p>
  </div>

  <footer>Documentation de l'API : <a href="/docs">/docs</a></footer>
</div>

<script>
const $ = id => document.getElementById(id);
async function calculer() {
  const q = new URLSearchParams({ m0: $('m0').value, x0: $('x0').value, residus: $('residus').value });
  $('out').hidden = false;
  try {
    const r = await fetch('/filtration?' + q);
    const d = await r.json();
    if (!r.ok) throw new Error(typeof d.detail === 'string' ? d.detail : 'Valeurs invalides');
    $('grid').hidden = false;
    $('m1').textContent = d.m1_kg_h;
    $('x1').textContent = d.x1;
    $('c').textContent = d.concentration_pct;
    const ok = Math.abs(d.erreur_bilan_global) < 1e-6 && Math.abs(d.erreur_bilan_solubles) < 1e-6;
    $('check').className = 'check ' + (ok ? 'ok' : 'err');
    $('check').textContent = ok
      ? '✔ Bilans vérifiés : erreur globale = 0, erreur solubles = 0'
      : '⚠ Erreur de bilan : global ' + d.erreur_bilan_global + ' / solubles ' + d.erreur_bilan_solubles;
  } catch (e) {
    $('grid').hidden = true;
    $('check').className = 'check err';
    $('check').textContent = 'Erreur : ' + e.message;
  }
}
</script>
</body>
</html>"""


@app.get("/", response_class=HTMLResponse)
def interface():
    return PAGE


@app.get("/filtration")
def filtration(m0: float = 1000, x0: float = 0.10, residus: float = 20):
    if m0 <= 0 or residus < 0 or residus >= m0 or not 0 <= x0 <= 1:
        raise HTTPException(
            status_code=400,
            detail="Vérifiez les valeurs : m0 > 0, 0 ≤ x0 ≤ 1, 0 ≤ résidus < m0",
        )
    m1 = m0 - residus
    x1 = (m0 * x0) / m1
    return {
        "m1_kg_h": m1,
        "x1": round(x1, 4),
        "concentration_pct": round(100 * x1, 2),
        "erreur_bilan_global": m0 - (m1 + residus),
        "erreur_bilan_solubles": round(m0 * x0 - m1 * x1, 6),
    }
