"""
Módulo de IA Generativa / NLP — ORBITAL-IA
===========================================
Gera um briefing de missão em linguagem natural a partir das recomendações
dos agentes. Demonstra o uso de IA Generativa para transformar dados técnicos
em comunicação clara para operadores humanos.

Funciona OFFLINE por padrão (geração baseada em template determinístico, sem
custo nem chave de API). Caso a equipe defina a variável de ambiente
ANTHROPIC_API_KEY, o módulo pode chamar a API da Anthropic para produzir um
briefing redigido por LLM (padrão usado em pipelines de RAG/sumarização).
"""

from __future__ import annotations
import os
import json
from datetime import datetime, timezone


def _briefing_template(metricas: dict, recomendacoes: list[dict],
                       visao: dict) -> str:
    agora = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    criticas = [r for r in recomendacoes if r["risco"] > 0.70]
    linhas = [
        f"BRIEFING OPERACIONAL — ORBITAL-IA  ({agora})",
        "=" * 60,
        "",
        "1. DESEMPENHO DO MODELO DE RISCO",
        f"   Acurácia: {metricas['acuracia']:.1%} | F1: {metricas['f1']:.2f} | "
        f"AUC-ROC: {metricas['auc_roc']:.2f}",
        "",
        "2. VISÃO COMPUTACIONAL",
        f"   Objetos detectados em imagem orbital: {visao['objetos_detectados']} "
        f"(referência: {visao['objetos_reais']})",
        "",
        "3. SITUAÇÃO DE RISCO",
        f"   Conjunções prioritárias analisadas: {len(recomendacoes)}",
        f"   Conjunções de alto risco (>0.70): {len(criticas)}",
        "",
        "4. RECOMENDAÇÕES PRIORITÁRIAS",
    ]
    for i, r in enumerate(recomendacoes, 1):
        linhas.append(
            f"   {i}. {r['primario']} x {r['secundario']} — risco {r['risco']:.0%}, "
            f"dist. mín. {r['distancia_minima_km']:.2f} km, "
            f"T-{r['tempo_ate_aprox_h']:.0f} h -> {r['acao_recomendada']}"
        )
    linhas += [
        "",
        "5. IMPACTO NA TERRA",
        "   A proteção destes ativos preserva serviços essenciais de "
        "monitoramento climático,",
        "   telecomunicações, navegação (GPS) e prevenção de desastres.",
    ]
    return "\n".join(linhas)


def gerar_briefing(metricas: dict, recomendacoes: list[dict], visao: dict) -> str:
    """Gera o briefing. Usa a API da Anthropic se houver chave; senão, template."""
    chave = os.environ.get("ANTHROPIC_API_KEY")
    if not chave:
        return _briefing_template(metricas, recomendacoes, visao)

    try:
        import urllib.request
        contexto = {
            "metricas": metricas,
            "recomendacoes": recomendacoes,
            "visao": visao,
        }
        prompt = (
            "Você é um analista de operações espaciais. Com base nos dados JSON "
            "a seguir, escreva um briefing operacional claro e objetivo em "
            "português, com seções de situação, riscos prioritários e ações "
            "recomendadas:\n\n" + json.dumps(contexto, ensure_ascii=False)
        )
        body = json.dumps({
            "model": "claude-sonnet-4-20250514",
            "max_tokens": 1024,
            "messages": [{"role": "user", "content": prompt}],
        }).encode("utf-8")
        req = urllib.request.Request(
            "https://api.anthropic.com/v1/messages",
            data=body,
            headers={
                "content-type": "application/json",
                "x-api-key": chave,
                "anthropic-version": "2023-06-01",
            },
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read())
        return "".join(b.get("text", "") for b in data.get("content", []))
    except Exception as e:  # fallback robusto
        return _briefing_template(metricas, recomendacoes, visao) + \
            f"\n\n[Aviso: chamada à API falhou ({e}); usado briefing por template.]"
