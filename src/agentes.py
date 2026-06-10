"""
Módulo de Sistema Multiagente — ORBITAL-IA
===========================================
Implementa três agentes autônomos que cooperam por troca de mensagens para
coordenar o monitoramento e a resposta a riscos de colisão:

  • AgenteMonitor   — ingere o catálogo e os eventos de conjunção (percepção)
  • AgenteAnalista  — aplica a rede neural e classifica o risco (raciocínio)
  • AgenteDecisor   — gera recomendações de manobra/ação (decisão)

A coordenação é orquestrada por um barramento simples (lista de mensagens),
ilustrando o padrão de sistemas multiagentes (percepção -> raciocínio ->
decisão) aplicável a operações de missão.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any
import pandas as pd

from modelo import ModeloRiscoColisao


@dataclass
class Mensagem:
    remetente: str
    tipo: str
    conteudo: Any


@dataclass
class Barramento:
    """Canal de comunicação compartilhado entre os agentes."""
    historico: list[Mensagem] = field(default_factory=list)

    def publicar(self, msg: Mensagem):
        self.historico.append(msg)

    def log(self) -> list[str]:
        return [f"[{m.remetente}] {m.tipo}" for m in self.historico]


class AgenteMonitor:
    nome = "AgenteMonitor"

    def perceber(self, eventos: pd.DataFrame, barramento: Barramento) -> pd.DataFrame:
        barramento.publicar(Mensagem(self.nome, "ingestao",
                                     f"{len(eventos)} eventos ingeridos"))
        return eventos


class AgenteAnalista:
    nome = "AgenteAnalista"

    def __init__(self, modelo: ModeloRiscoColisao):
        self.modelo = modelo

    def analisar(self, eventos: pd.DataFrame, barramento: Barramento) -> pd.DataFrame:
        eventos = eventos.copy()
        eventos["risco_previsto"] = self.modelo.prever_risco(eventos)
        criticos = int((eventos["risco_previsto"] > 0.7).sum())
        barramento.publicar(Mensagem(self.nome, "analise",
                                     f"{criticos} conjunções críticas (risco > 0.70)"))
        return eventos


class AgenteDecisor:
    nome = "AgenteDecisor"

    def decidir(self, eventos: pd.DataFrame, barramento: Barramento,
                top_n: int = 5) -> list[dict]:
        prioritarios = eventos.sort_values("risco_previsto", ascending=False).head(top_n)
        recomendacoes = []
        for _, ev in prioritarios.iterrows():
            risco = ev["risco_previsto"]
            if risco > 0.85:
                acao = "MANOBRA EVASIVA IMEDIATA"
            elif risco > 0.70:
                acao = "Planejar manobra evasiva nas próximas horas"
            elif risco > 0.50:
                acao = "Monitoramento intensivo e novo cálculo de órbita"
            else:
                acao = "Acompanhamento de rotina"
            recomendacoes.append({
                "primario": ev["id_primario"],
                "secundario": ev["id_secundario"],
                "risco": round(float(risco), 3),
                "distancia_minima_km": float(ev["distancia_minima_km"]),
                "tempo_ate_aprox_h": float(ev["tempo_ate_aprox_h"]),
                "acao_recomendada": acao,
            })
        barramento.publicar(Mensagem(self.nome, "decisao",
                                     f"{len(recomendacoes)} recomendações emitidas"))
        return recomendacoes


def orquestrar(eventos: pd.DataFrame, modelo: ModeloRiscoColisao):
    """Executa o ciclo cooperativo dos três agentes."""
    barramento = Barramento()
    monitor = AgenteMonitor()
    analista = AgenteAnalista(modelo)
    decisor = AgenteDecisor()

    eventos = monitor.perceber(eventos, barramento)
    eventos = analista.analisar(eventos, barramento)
    recomendacoes = decisor.decidir(eventos, barramento)
    return recomendacoes, barramento, eventos
