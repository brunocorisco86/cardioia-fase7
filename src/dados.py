"""
Módulo de Dados — ORBITAL-IA
=============================
Pipeline de dados que simula um catálogo de objetos em órbita (satélites
ativos e detritos espaciais) e gera eventos de conjunção (aproximações)
entre pares de objetos.

Em produção, esta camada seria alimentada por fontes reais como o catálogo
público da Space-Track / CelesTrak (dados TLE) e por telemetria via APIs.
Aqui geramos dados sintéticos fisicamente plausíveis para tornar a POC
totalmente executável e reprodutível, sem dependência de rede.
"""

from __future__ import annotations
import numpy as np
import pandas as pd

# Regimes orbitais (altitude em km) — base para gerar objetos realistas
REGIMES = {
    "LEO": (300, 2000),     # Órbita Baixa — maioria dos detritos
    "MEO": (2000, 35000),   # Órbita Média — constelações de navegação (GPS)
    "GEO": (35000, 36500),  # Órbita Geoestacionária — satélites de telecom/clima
}

TIPOS = ["satelite_ativo", "estagio_foguete", "detrito", "fragmento"]


def gerar_catalogo(n_objetos: int = 1200, seed: int = 42) -> pd.DataFrame:
    """Gera um catálogo sintético de objetos orbitais."""
    rng = np.random.default_rng(seed)

    # Distribuição realista: maior concentração em LEO
    regime = rng.choice(list(REGIMES.keys()), size=n_objetos, p=[0.78, 0.15, 0.07])
    altitude = np.array([rng.uniform(*REGIMES[r]) for r in regime])

    # Inclinação orbital (graus)
    inclinacao = rng.uniform(0, 100, n_objetos)
    # Velocidade orbital aproximada (km/s) ~ função da altitude (Terra: mu/(R+h))
    mu = 398600.0  # km^3/s^2
    raio_terra = 6371.0
    velocidade = np.sqrt(mu / (raio_terra + altitude))

    # Tamanho do objeto (m) — detritos pequenos são maioria mas perigosos
    tamanho = rng.lognormal(mean=-0.5, sigma=1.0, size=n_objetos).clip(0.05, 30)

    tipo = rng.choice(TIPOS, size=n_objetos, p=[0.35, 0.10, 0.35, 0.20])

    df = pd.DataFrame({
        "id_objeto": [f"OBJ-{i:05d}" for i in range(n_objetos)],
        "tipo": tipo,
        "regime": regime,
        "altitude_km": altitude.round(1),
        "inclinacao_deg": inclinacao.round(2),
        "velocidade_kms": velocidade.round(3),
        "tamanho_m": tamanho.round(3),
    })
    return df


def gerar_eventos_conjuncao(catalogo: pd.DataFrame, n_eventos: int = 4000,
                            seed: int = 7) -> pd.DataFrame:
    """
    Gera eventos de conjunção (aproximação entre dois objetos).
    Cada evento tem features usadas para estimar o risco de colisão.
    O rótulo de risco é derivado de uma regra física + ruído, simulando
    a verdade-base que o modelo de IA aprenderá a generalizar.
    """
    rng = np.random.default_rng(seed)
    a = catalogo.sample(n_eventos, replace=True, random_state=seed).reset_index(drop=True)
    b = catalogo.sample(n_eventos, replace=True, random_state=seed + 1).reset_index(drop=True)

    distancia_minima_km = rng.exponential(scale=3.0, size=n_eventos).clip(0.01, 50)
    velocidade_relativa = np.abs(a["velocidade_kms"].values - b["velocidade_kms"].values) \
        + rng.uniform(0, 14, n_eventos)
    tamanho_combinado = a["tamanho_m"].values + b["tamanho_m"].values
    diferenca_altitude = np.abs(a["altitude_km"].values - b["altitude_km"].values)
    tempo_ate_aprox_h = rng.uniform(0.5, 72, n_eventos)

    eventos = pd.DataFrame({
        "id_primario": a["id_objeto"].values,
        "id_secundario": b["id_objeto"].values,
        "distancia_minima_km": distancia_minima_km.round(3),
        "velocidade_relativa_kms": velocidade_relativa.round(3),
        "tamanho_combinado_m": tamanho_combinado.round(3),
        "diferenca_altitude_km": diferenca_altitude.round(1),
        "tempo_ate_aprox_h": tempo_ate_aprox_h.round(2),
    })

    # ---- Verdade-base (probabilidade de colisão) por modelo físico simplificado ----
    # Quanto menor a distância, maior a velocidade relativa e o tamanho -> maior risco.
    score = (
        4.5 * np.exp(-eventos["distancia_minima_km"] / 4.0)
        + 0.06 * eventos["velocidade_relativa_kms"]
        + 0.10 * eventos["tamanho_combinado_m"]
        - 0.008 * eventos["diferenca_altitude_km"]
    )
    prob = 1 / (1 + np.exp(-(score - 1.0)))
    prob = (prob + rng.normal(0, 0.05, n_eventos)).clip(0, 1)
    eventos["risco_real"] = (prob > 0.5).astype(int)
    return eventos


if __name__ == "__main__":
    cat = gerar_catalogo()
    ev = gerar_eventos_conjuncao(cat)
    print(cat.head())
    print(ev.head())
    print(f"\nObjetos: {len(cat)} | Eventos: {len(ev)} | "
          f"Eventos de alto risco: {ev['risco_real'].mean():.1%}")
