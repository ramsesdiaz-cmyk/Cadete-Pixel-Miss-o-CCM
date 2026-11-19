import pygame
import sys
import math
import array
import asyncio

pygame.mixer.pre_init(44100, -16, 1, 512)
pygame.init()

# Tela única (800x600)
LARGURA, ALTURA = 800, 600
TELA = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Cadete Pixel - 20 Moedas")
RELOGIO = pygame.time.Clock()
FPS = 60

# Cores
AZUL_CEU = (92, 148, 252)
VERDE_GRAMA = (0, 168, 0)
MARROM_TERRA = (172, 80, 0)
AMARELO_MOEDA = (252, 216, 0)
AZUL_UNIFORME = (15, 35, 95)
DOURADO = (255, 215, 0)
CASTANHO = (110, 55, 20)
PELE = (252, 204, 156)
BRANCO = (255, 255, 255)
PRETO = (0, 0, 0)

FONTE = pygame.font.Font(None, 36)
FONTE_GRANDE = pygame.font.Font(None, 64)

def gerar_som(freq, ms):
    n = int(round(ms * 44100 / 1000.0))
    buf = array.array('h', [0] * n)
    for s in range(n):
        buf[s] = 4000 if math.sin(2.0 * math.pi * freq * (s / 44100)) >= 0 else -4000
    return pygame.mixer.Sound(buffer=buf)

SOM_PULO = gerar_som(440, 100)
SOM_MOEDA = gerar_som(880, 80)
SOM_VITORIA = gerar_som(660, 400)

class Jogador:
    def __init__(self):
        self.rect = pygame.Rect(40, 490, 32, 48)
        self.vel_x = 0
        self.vel_y = 0
        self.no_chao = False
        self.moedas_coletadas = 0
        self.direcao = 1
        self.passo = 0

    def atualizar(self, plataformas):
        teclas = pygame.key.get_pressed()
        self.vel_x = 0
        if teclas[pygame.K_LEFT] or teclas[pygame.K_a]:
            self.vel_x = -5
            self.direcao = -1
        if teclas[pygame.K_RIGHT] or teclas[pygame.K_d]:
            self.vel_x = 5
            self.direcao = 1
        if (teclas[pygame.K_SPACE] or teclas[pygame.K_UP] or teclas[pygame.K_w]) and self.no_chao:
            self.vel_y = -14
            self.no_chao = False
            SOM_PULO.play()

        self.passo = self.passo + 0.25 if (self.vel_x != 0 and self.no_chao) else 0

        self.rect.x += self.vel_x
        if self.rect.left < 0: self.rect.left = 0
        if self.rect.right > LARGURA: self.rect.right = LARGURA
        for p in plataformas:
            if self.rect.colliderect(p):
                if self.vel_x > 0: self.rect.right = p.left
                elif self.vel_x < 0: self.rect.left = p.right

        self.vel_y = min(self.vel_y + 0.7, 15)
        self.rect.y += self.vel_y
        self.no_chao = False
        for p in plataformas:
            if self.rect.colliderect(p):
                if self.vel_y > 0:
                    self.rect.bottom = p.top
                    self.vel_y = 0
                    self.no_chao = True
                elif self.vel_y < 0:
                    self.rect.top = p.bottom
                    self.vel_y = 0

    def desenhar(self, tela):
        x, y = self.rect.x, self.rect.y
        pygame.draw.rect(tela, CASTANHO, (x + 4, y, 24, 10))
        pygame.draw.rect(tela, PELE, (x + 6, y + 8, 20, 14))
        olho_x = x + 18 if self.direcao == 1 else x + 10
        pygame.draw.rect(tela, PRETO, (olho_x, y + 12, 4, 5))
        pygame.draw.rect(tela, AZUL_UNIFORME, (x + 6, y + 22, 20, 16))
        pygame.draw.rect(tela, DOURADO, (x + 14, y + 26, 4, 4))
        mov = int(math.sin(self.passo) * 3)
        pygame.draw.rect(tela, AZUL_UNIFORME, (x + 8, y + 38, 6, 10 + mov))
        pygame.draw.rect(tela, AZUL_UNIFORME, (x + 18, y + 38, 6, 10 - mov))

def criar_fase():
    plataformas = [
        pygame.Rect(0, 550, 800, 50),     # Chão
        pygame.Rect(80, 440, 220, 20),    # Plataforma Esquerda Baixa
        pygame.Rect(500, 440, 220, 20),   # Plataforma Direita Baixa
        pygame.Rect(280, 330, 240, 20),   # Plataforma Central
        pygame.Rect(80, 220, 200, 20),    # Plataforma Esquerda Alta
        pygame.Rect(520, 220, 200, 20),   # Plataforma Direita Alta
    ]

    # 20 moedas espalhadas pela tela
    moedas = [
        pygame.Rect(200, 515, 18, 18), pygame.Rect(320, 515, 18, 18),
        pygame.Rect(460, 515, 18, 18), pygame.Rect(580, 515, 18, 18),
        pygame.Rect(100, 405, 18, 18), pygame.Rect(150, 405, 18, 18),
        pygame.Rect(200, 405, 18, 18), pygame.Rect(250, 405, 18, 18),
        pygame.Rect(520, 405, 18, 18), pygame.Rect(570, 405, 18, 18),
        pygame.Rect(620, 405, 18, 18), pygame.Rect(670, 405, 18, 18),
        pygame.Rect(310, 295, 18, 18), pygame.Rect(360, 295, 18, 18),
        pygame.Rect(410, 295, 18, 18), pygame.Rect(460, 295, 18, 18),
        pygame.Rect(130, 185, 18, 18), pygame.Rect(210, 185, 18, 18),
        pygame.Rect(570, 185, 18, 18), pygame.Rect(650, 185, 18, 18),
    ]
    return plataformas, moedas

async def main():
    jogador = Jogador()
    plataformas, moedas = criar_fase()
    venceu = False

    while True:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if evento.type == pygame.KEYDOWN and venceu and evento.key == pygame.K_r:
                jogador = Jogador()
                plataformas, moedas = criar_fase()
                venceu = False

        if not venceu:
            jogador.atualizar(plataformas)

            for m in moedas[:]:
                if jogador.rect.colliderect(m):
                    moedas.remove(m)
                    jogador.moedas_coletadas += 1
                    SOM_MOEDA.play()

            if jogador.moedas_coletadas == 20:
                venceu = True
                SOM_VITORIA.play()

        TELA.fill(AZUL_CEU)

        for p in plataformas:
            pygame.draw.rect(TELA, MARROM_TERRA, p)
            pygame.draw.rect(TELA, VERDE_GRAMA, (p.x, p.y, p.width, 6))
            pygame.draw.rect(TELA, PRETO, p, 2)

        for m in moedas:
            pygame.draw.ellipse(TELA, AMARELO_MOEDA, m)
            pygame.draw.ellipse(TELA, PRETO, m, 2)

        jogador.desenhar(TELA)

        placar = FONTE.render(f"MOEDAS: {jogador.moedas_coletadas} / 20", True, BRANCO)
        TELA.blit(placar, (20, 20))

        if venceu:
            msg = FONTE_GRANDE.render("VOCÊ VENCEU!", True, DOURADO)
            sub = FONTE.render("Pressione R para jogar novamente", True, BRANCO)
            TELA.blit(msg, (LARGURA//2 - msg.get_width()//2, 240))
            TELA.blit(sub, (LARGURA//2 - sub.get_width()//2, 310))

        pygame.display.flip()
        RELOGIO.tick(FPS)
        await asyncio.sleep(0)

if __name__ == "__main__":
    asyncio.run(main())