import os
import sys
import pytest
import pandas as pd

# Adiciona a pasta src ao sys.path para permitir a importação direta dos módulos
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from dados import gerar_catalogo, gerar_eventos_conjuncao
from modelo import ModeloRiscoColisao

@pytest.fixture(scope="session")
def catalogo_simulado():
    """Fixture que gera um catálogo de objetos orbitais simulado para testes rápidos."""
    return gerar_catalogo(n_objetos=100, seed=42)

@pytest.fixture(scope="session")
def eventos_simulados(catalogo_simulado):
    """Fixture que gera eventos de conjunção a partir do catálogo simulado."""
    return gerar_eventos_conjuncao(catalogo_simulado, n_eventos=200, seed=7)

@pytest.fixture(scope="session")
def modelo_treinado(eventos_simulados):
    """Fixture que retorna um ModeloRiscoColisao já treinado."""
    modelo = ModeloRiscoColisao(seed=42)
    modelo.treinar(eventos_simulados)
    return modelo
