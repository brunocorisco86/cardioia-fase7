import pandas as pd
from dados import gerar_catalogo, gerar_eventos_conjuncao

def test_gerar_catalogo():
    n_objetos = 50
    df = gerar_catalogo(n_objetos=n_objetos, seed=42)
    
    assert isinstance(df, pd.DataFrame)
    assert len(df) == n_objetos
    
    # Verifica colunas obrigatórias
    colunas_esperadas = {
        "id_objeto", "tipo", "regime", "altitude_km", 
        "inclinacao_deg", "velocidade_kms", "tamanho_m"
    }
    assert colunas_esperadas.issubset(df.columns)
    
    # Verifica tipos de dados e limites físicos plausíveis
    assert df["altitude_km"].min() >= 300
    assert df["inclinacao_deg"].min() >= 0
    assert df["inclinacao_deg"].max() <= 180
    assert df["velocidade_kms"].min() > 0

def test_gerar_eventos_conjuncao(catalogo_simulado):
    n_eventos = 100
    df_eventos = gerar_eventos_conjuncao(catalogo_simulado, n_eventos=n_eventos, seed=7)
    
    assert isinstance(df_eventos, pd.DataFrame)
    assert len(df_eventos) == n_eventos
    
    colunas_esperadas = {
        "id_primario", "id_secundario", "distancia_minima_km",
        "velocidade_relativa_kms", "tamanho_combinado_m",
        "diferenca_altitude_km", "tempo_ate_aprox_h", "risco_real"
    }
    assert colunas_esperadas.issubset(df_eventos.columns)
    
    # Risco real deve ser binário (0 ou 1)
    assert df_eventos["risco_real"].isin([0, 1]).all()

def test_reprodutibilidade_dados():
    df1 = gerar_catalogo(n_objetos=30, seed=99)
    df2 = gerar_catalogo(n_objetos=30, seed=99)
    assert df1.equals(df2)
    
    ev1 = gerar_eventos_conjuncao(df1, n_eventos=50, seed=8)
    ev2 = gerar_eventos_conjuncao(df2, n_eventos=50, seed=8)
    assert ev1.equals(ev2)
