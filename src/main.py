import random
import pygame
from pygame.locals import * # pygame 사용 시 입력 및 이벤트 관리
from functions import *
from variables import *

def main():
    pygame.init() # Pygame 라이브러리 초기화
    pygame.display.set_caption('Flappy Bird') # 게임 창의 상단에 표시될 제목
    
    load_assets()

    while True:
        # select background sprites
        inputBackground = selectBackground()
        IMAGES['background'] = pygame.image.load(BACKGROUNDS_LIST[inputBackground]).convert()
        SCREEN.blit(IMAGES['background'], (0,0))

        # select player sprites
        inputPlayer = selectPlayer()
        IMAGES['player'] = (
            pygame.image.load(PLAYERS_LIST[inputPlayer][0]).convert_alpha(),
            pygame.image.load(PLAYERS_LIST[inputPlayer][1]).convert_alpha(),
            pygame.image.load(PLAYERS_LIST[inputPlayer][2]).convert_alpha(),
        )

        # select random pipe sprites
        pipeindex = random.randint(0, len(PIPES_LIST) - 1)
        IMAGES['pipe'] = (
            pygame.transform.flip(
                pygame.image.load(PIPES_LIST[pipeindex]).convert_alpha(), False, True),
            pygame.image.load(PIPES_LIST[pipeindex]).convert_alpha(),
        )

        # hitmask for pipes
        HITMASKS['pipe'] = (
            getHitmask(IMAGES['pipe'][0]),
            getHitmask(IMAGES['pipe'][1]),
        )

        # hitmask for player
        HITMASKS['player'] = (
            getHitmask(IMAGES['player'][0]),
            getHitmask(IMAGES['player'][1]),
            getHitmask(IMAGES['player'][2]),
        )

        movementInfo = showWelcomeAnimation()
        crashInfo = mainGame(movementInfo)
        showGameOverScreen(crashInfo)

if __name__ == '__main__':
    main()
