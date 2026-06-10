"""
Módulo de Visão Computacional — ORBITAL-IA
===========================================
Demonstra um pipeline de visão computacional para detecção de objetos em
imagens orbitais. Gera uma imagem sintética de um campo estelar com objetos
(satélites/detritos) e os detecta via processamento de imagem (OpenCV).

Esta etapa valida o fluxo de CV de ponta a ponta (captura -> pré-processamento
-> detecção -> contagem -> anotação). Em produção, o detector clássico seria
substituído por uma rede YOLO treinada em imagens orbitais reais — a interface
`detectar_objetos` permanece a mesma, facilitando a troca do backend.
"""

from __future__ import annotations
import numpy as np
import cv2


def gerar_imagem_orbital(largura: int = 640, altura: int = 480,
                         n_objetos: int = 12, seed: int = 1):
    """Cria uma imagem sintética: fundo estrelado + objetos orbitais."""
    rng = np.random.default_rng(seed)
    img = rng.integers(0, 18, size=(altura, largura), dtype=np.uint8)  # fundo escuro

    # Estrelas (ruído pontual fraco — não devem ser detectadas como objetos)
    for _ in range(400):
        x, y = rng.integers(0, largura), rng.integers(0, altura)
        img[y, x] = rng.integers(60, 120)

    verdade = []
    for _ in range(n_objetos):
        x, y = rng.integers(20, largura - 20), rng.integers(20, altura - 20)
        raio = int(rng.integers(3, 9))
        cv2.circle(img, (x, y), raio, int(rng.integers(180, 255)), -1)
        verdade.append((x, y, raio))
    return img, verdade


def detectar_objetos(img: np.ndarray):
    """Detecta objetos brilhantes na imagem. Retorna lista de (x, y, raio)."""
    _, binaria = cv2.threshold(img, 140, 255, cv2.THRESH_BINARY)
    binaria = cv2.morphologyEx(binaria, cv2.MORPH_OPEN,
                               np.ones((2, 2), np.uint8))
    contornos, _ = cv2.findContours(binaria, cv2.RETR_EXTERNAL,
                                    cv2.CHAIN_APPROX_SIMPLE)
    deteccoes = []
    for c in contornos:
        area = cv2.contourArea(c)
        if area < 8:  # filtra estrelas/ruído
            continue
        (x, y), raio = cv2.minEnclosingCircle(c)
        deteccoes.append((int(x), int(y), int(raio)))
    return deteccoes


def anotar(img: np.ndarray, deteccoes) -> np.ndarray:
    """Desenha caixas/etiquetas nas detecções (saída para o dashboard)."""
    colorida = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
    for i, (x, y, r) in enumerate(deteccoes):
        cv2.rectangle(colorida, (x - r - 4, y - r - 4), (x + r + 4, y + r + 4),
                      (0, 220, 120), 1)
        cv2.putText(colorida, f"obj{i}", (x - r - 4, y - r - 8),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 220, 120), 1)
    return colorida


def executar_visao(caminho_saida: str = "outputs/visao_deteccao.png") -> dict:
    img, verdade = gerar_imagem_orbital()
    deteccoes = detectar_objetos(img)
    anotada = anotar(img, deteccoes)
    cv2.imwrite(caminho_saida, anotada)
    return {
        "objetos_reais": len(verdade),
        "objetos_detectados": len(deteccoes),
        "imagem": caminho_saida,
    }


if __name__ == "__main__":
    print(executar_visao())
