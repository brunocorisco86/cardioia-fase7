import numpy as np
import cv2
from visao import gerar_imagem_orbital, detectar_objetos, anotar, executar_visao

def test_gerar_imagem_orbital():
    largura, altura = 320, 240
    n_objetos = 5
    img, verdade = gerar_imagem_orbital(largura=largura, altura=altura, n_objetos=n_objetos, seed=42)
    
    assert isinstance(img, np.ndarray)
    assert img.shape == (altura, largura)
    assert img.dtype == np.uint8
    assert len(verdade) == n_objetos
    for x, y, raio in verdade:
        assert 0 <= x < largura
        assert 0 <= y < altura
        assert raio > 0

def test_detectar_objetos():
    largura, altura = 320, 240
    img, verdade = gerar_imagem_orbital(largura=largura, altura=altura, n_objetos=4, seed=42)
    
    deteccoes = detectar_objetos(img)
    
    assert isinstance(deteccoes, list)
    # Pelo menos algumas das detecções devem ser encontradas com o threshold/morfologia
    assert len(deteccoes) > 0
    for det in deteccoes:
        assert len(det) == 3
        x, y, raio = det
        assert 0 <= x < largura
        assert 0 <= y < altura
        assert raio > 0

def test_anotar():
    largura, altura = 160, 120
    img, _ = gerar_imagem_orbital(largura=largura, altura=altura, n_objetos=2, seed=1)
    deteccoes = [(30, 40, 5), (80, 90, 7)]
    
    img_anotada = anotar(img, deteccoes)
    
    assert isinstance(img_anotada, np.ndarray)
    # Imagem de entrada é escala de cinza (2D), anotada deve ser BGR (3D - 3 canais de cor)
    assert len(img_anotada.shape) == 3
    assert img_anotada.shape[2] == 3
    assert img_anotada.shape[0] == altura
    assert img_anotada.shape[1] == largura

def test_executar_visao_completo(tmp_path):
    caminho_teste = tmp_path / "visao_saida_teste.png"
    
    res = executar_visao(str(caminho_teste))
    
    assert isinstance(res, dict)
    assert "objetos_reais" in res
    assert "objetos_detectados" in res
    assert "imagem" in res
    assert res["imagem"] == str(caminho_teste)
    assert caminho_teste.exists()
