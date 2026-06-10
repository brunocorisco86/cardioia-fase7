"""
ORBITAL-IA — Orquestrador Principal
====================================
Executa a POC de ponta a ponta:

  1. Pipeline de dados (catálogo orbital + eventos de conjunção)
  2. Treino da rede neural de risco de colisão
  3. Visão computacional (detecção em imagem orbital)
  4. Sistema multiagente (monitor -> analista -> decisor)
  5. IA Generativa (briefing em linguagem natural)
  6. Geração de gráficos, métricas (JSON) e dashboard HTML

Uso:  python main.py
"""

from __future__ import annotations
import os
import sys
import json

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from dados import gerar_catalogo, gerar_eventos_conjuncao   # noqa: E402
from modelo import ModeloRiscoColisao                        # noqa: E402
from visao import executar_visao                             # noqa: E402
from agentes import orquestrar                                # noqa: E402
from genai import gerar_briefing                              # noqa: E402

OUT = "outputs"
os.makedirs(OUT, exist_ok=True)


def gerar_graficos(catalogo, eventos, metricas):
    # 1. Distribuição de objetos por regime orbital
    fig, ax = plt.subplots(figsize=(6, 4))
    catalogo["regime"].value_counts().plot(kind="bar", ax=ax, color="#3b82f6")
    ax.set_title("Objetos catalogados por regime orbital")
    ax.set_ylabel("Quantidade"); ax.set_xlabel("Regime")
    fig.tight_layout(); fig.savefig(f"{OUT}/objetos_por_regime.png", dpi=110); plt.close(fig)

    # 2. Matriz de confusão
    cm = np.array(metricas["matriz_confusao"])
    fig, ax = plt.subplots(figsize=(4.5, 4))
    im = ax.imshow(cm, cmap="Blues")
    ax.set_xticks([0, 1]); ax.set_yticks([0, 1])
    ax.set_xticklabels(["Sem risco", "Risco"]); ax.set_yticklabels(["Sem risco", "Risco"])
    ax.set_xlabel("Previsto"); ax.set_ylabel("Real")
    ax.set_title("Matriz de confusão — rede neural")
    for i in range(2):
        for j in range(2):
            ax.text(j, i, cm[i, j], ha="center", va="center",
                    color="white" if cm[i, j] > cm.max() / 2 else "black")
    fig.colorbar(im); fig.tight_layout()
    fig.savefig(f"{OUT}/matriz_confusao.png", dpi=110); plt.close(fig)

    # 3. Distribuição do risco previsto
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.hist(eventos["risco_previsto"], bins=40, color="#ef4444", alpha=0.8)
    ax.set_title("Distribuição do risco de colisão previsto")
    ax.set_xlabel("Probabilidade de risco"); ax.set_ylabel("Nº de conjunções")
    fig.tight_layout(); fig.savefig(f"{OUT}/distribuicao_risco.png", dpi=110); plt.close(fig)


def gerar_dashboard(resultados):
    """Gera um dashboard HTML autocontido (imagens embutidas) a partir da execução."""
    import base64

    def b64(caminho):
        try:
            with open(f"{OUT}/{caminho}", "rb") as f:
                return "data:image/png;base64," + base64.b64encode(f.read()).decode()
        except FileNotFoundError:
            return ""

    img_visao = b64("visao_deteccao.png")
    img_risco = b64("distribuicao_risco.png")
    img_regime = b64("objetos_por_regime.png")
    img_cm = b64("matriz_confusao.png")
    m = resultados["metricas"]; v = resultados["visao"]
    recs = resultados["recomendacoes"]
    linhas_rec = "".join(
        f"<tr><td>{r['primario']}</td><td>{r['secundario']}</td>"
        f"<td><span class='risco' style='--p:{r['risco']}'>{r['risco']:.0%}</span></td>"
        f"<td>{r['distancia_minima_km']:.2f} km</td>"
        f"<td>T-{r['tempo_ate_aprox_h']:.0f}h</td>"
        f"<td>{r['acao_recomendada']}</td></tr>"
        for r in recs
    )
    log_html = "".join(f"<li>{l}</li>" for l in resultados["log_agentes"])
    html = f"""<!doctype html><html lang="pt-br"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>ORBITAL-IA · Painel de Controle</title>
<style>
:root{{--bg:#0b1020;--card:#141b30;--line:#243049;--txt:#e6ecff;--mut:#8b97b8;--ac:#5b8cff;--ok:#22c55e;--warn:#f59e0b;--bad:#ef4444}}
*{{box-sizing:border-box}}body{{margin:0;font-family:system-ui,-apple-system,Segoe UI,Roboto,sans-serif;background:var(--bg);color:var(--txt)}}
header{{padding:28px 32px;border-bottom:1px solid var(--line);display:flex;align-items:center;gap:14px}}
header h1{{font-size:20px;margin:0;letter-spacing:.5px}}
header .tag{{color:var(--mut);font-size:13px}}
.dot{{width:10px;height:10px;border-radius:50%;background:var(--ok);box-shadow:0 0 12px var(--ok)}}
main{{padding:24px 32px;max-width:1100px;margin:0 auto}}
.grid{{display:grid;grid-template-columns:repeat(4,1fr);gap:16px;margin-bottom:24px}}
.kpi{{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:18px}}
.kpi .v{{font-size:28px;font-weight:700}}.kpi .l{{color:var(--mut);font-size:13px;margin-top:4px}}
.card{{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:20px;margin-bottom:20px}}
.card h2{{font-size:15px;margin:0 0 14px;color:var(--ac);text-transform:uppercase;letter-spacing:1px}}
table{{width:100%;border-collapse:collapse;font-size:14px}}
th,td{{text-align:left;padding:9px 8px;border-bottom:1px solid var(--line)}}
th{{color:var(--mut);font-weight:600;font-size:12px;text-transform:uppercase}}
.risco{{font-weight:700;color:color-mix(in srgb,var(--bad) calc(var(--p)*100%),var(--ok))}}
.cols{{display:grid;grid-template-columns:1fr 1fr;gap:20px}}
img{{width:100%;border-radius:10px;border:1px solid var(--line)}}
ul.log{{list-style:none;padding:0;margin:0;font-family:ui-monospace,monospace;font-size:13px;color:var(--mut)}}
ul.log li{{padding:6px 0;border-bottom:1px solid var(--line)}}
@media(max-width:760px){{.grid{{grid-template-columns:repeat(2,1fr)}}.cols{{grid-template-columns:1fr}}}}
</style></head><body>
<header><span class="dot"></span><h1>ORBITAL-IA</h1>
<span class="tag">Sistema Multiagente de Monitoramento de Detritos Espaciais · POC</span></header>
<main>
<div class="grid">
<div class="kpi"><div class="v">{m['acuracia']:.0%}</div><div class="l">Acurácia do modelo</div></div>
<div class="kpi"><div class="v">{m['auc_roc']:.2f}</div><div class="l">AUC-ROC</div></div>
<div class="kpi"><div class="v">{v['objetos_detectados']}</div><div class="l">Objetos detectados (visão)</div></div>
<div class="kpi"><div class="v">{len(recs)}</div><div class="l">Conjunções prioritárias</div></div>
</div>
<div class="card"><h2>Conjunções prioritárias e ações recomendadas</h2>
<table><thead><tr><th>Primário</th><th>Secundário</th><th>Risco</th>
<th>Dist. mínima</th><th>Janela</th><th>Ação recomendada</th></tr></thead>
<tbody>{linhas_rec}</tbody></table></div>
<div class="cols">
<div class="card"><h2>Visão computacional</h2><img src="{img_visao}" alt="Detecção orbital"></div>
<div class="card"><h2>Distribuição do risco</h2><img src="{img_risco}" alt="Risco"></div>
</div>
<div class="cols">
<div class="card"><h2>Objetos por regime</h2><img src="{img_regime}" alt="Regimes"></div>
<div class="card"><h2>Matriz de confusão</h2><img src="{img_cm}" alt="Confusão"></div>
</div>
<div class="card"><h2>Log do sistema multiagente</h2><ul class="log">{log_html}</ul></div>
</main></body></html>"""
    with open(f"{OUT}/dashboard.html", "w", encoding="utf-8") as f:
        f.write(html)


def main():
    print("=" * 60)
    print("ORBITAL-IA — executando pipeline da POC")
    print("=" * 60)

    print("\n[1/6] Pipeline de dados...")
    catalogo = gerar_catalogo()
    eventos = gerar_eventos_conjuncao(catalogo)
    print(f"      {len(catalogo)} objetos, {len(eventos)} eventos de conjunção")

    print("[2/6] Treinando rede neural de risco...")
    modelo = ModeloRiscoColisao()
    metricas = modelo.treinar(eventos)
    print(f"      Acurácia={metricas['acuracia']:.1%}  AUC-ROC={metricas['auc_roc']:.2f}")

    print("[3/6] Visão computacional...")
    visao = executar_visao(f"{OUT}/visao_deteccao.png")
    print(f"      {visao['objetos_detectados']} objetos detectados")

    print("[4/6] Sistema multiagente...")
    recomendacoes, barramento, eventos = orquestrar(eventos, modelo)
    print(f"      {len(recomendacoes)} recomendações emitidas")

    print("[5/6] IA Generativa (briefing)...")
    briefing = gerar_briefing(metricas, recomendacoes, visao)
    with open(f"{OUT}/briefing.txt", "w", encoding="utf-8") as f:
        f.write(briefing)

    print("[6/6] Gráficos, métricas e dashboard...")
    gerar_graficos(catalogo, eventos, metricas)
    resultados = {
        "metricas": metricas,
        "visao": visao,
        "recomendacoes": recomendacoes,
        "log_agentes": barramento.log(),
    }
    with open(f"{OUT}/resultados.json", "w", encoding="utf-8") as f:
        json.dump(resultados, f, ensure_ascii=False, indent=2)
    gerar_dashboard(resultados)

    print("\n" + "=" * 60)
    print("Concluído! Saídas geradas em ./outputs/")
    print("  - dashboard.html        (painel visual)")
    print("  - briefing.txt          (briefing por IA generativa)")
    print("  - resultados.json       (métricas e recomendações)")
    print("  - *.png                 (gráficos)")
    print("=" * 60)
    print("\n----- BRIEFING -----\n")
    print(briefing)


if __name__ == "__main__":
    main()
