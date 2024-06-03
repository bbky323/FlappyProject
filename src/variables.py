import pygame
import time # 시간 측정을 위해 사용(승훈)

FPS = 30 # 게임의 프레임 설정
SCREENWIDTH  = 288 # 화면 너비
SCREENHEIGHT = 512 # 화면 높
PIPEGAPSIZE  = 100 # 파이프 사이 간격
BASEY        = SCREENHEIGHT * 0.79 # 바닥의 높이
# image, sound and hitmask  dicts
IMAGES, SOUNDS, HITMASKS = {}, {}, {}

# 난이도에 따라 파이프의 수평 간격 조절 (준영)
EASY_PIPE_SPACING = 50
HARD_PIPE_SPACING = 0
pipeSpacing = EASY_PIPE_SPACING # 초기값을 easy로 설정

#일시정지 상태 저장 변수(승재)
paused = False

# list of all possible players (tuple of 3 positions of flap)
PLAYERS_LIST = (
    # red bird
    (
        'assets/sprites/redbird-upflap.png',
        'assets/sprites/redbird-midflap.png',
        'assets/sprites/redbird-downflap.png',
    ),
    # blue bird
    (
        'assets/sprites/bluebird-upflap.png',
        'assets/sprites/bluebird-midflap.png',
        'assets/sprites/bluebird-downflap.png',
    ),
    # yellow bird
    (
        'assets/sprites/yellowbird-upflap.png',
        'assets/sprites/yellowbird-midflap.png',
        'assets/sprites/yellowbird-downflap.png',
    ),
)

# list of backgrounds
BACKGROUNDS_LIST = (
    'assets/sprites/background-day.png',
    'assets/sprites/background-night.png',
)

# list of pipes
PIPES_LIST = (
    'assets/sprites/pipe-green.png',
    'assets/sprites/pipe-red.png',
)


try:
    xrange
except NameError:
    xrange = range

#기존에 전역변수였던 변수들
FPSCLOCK = pygame.time.Clock() # Pygame 시계 객체, 프레임 속도를 제어
SCREEN = pygame.display.set_mode((SCREENWIDTH, SCREENHEIGHT)) # Pygame 화면 객체, 창의 픽셀 크기 정의
startTime = time.time()     #시작시간 측정을 위한 전역변수 선언 (승훈)
