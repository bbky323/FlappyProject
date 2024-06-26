import sys 
from itertools import cycle 
import random
import pygame
from pygame.locals import * 
from variables import *

def load_assets():
    IMAGES['numbers'] = [pygame.image.load(f'assets/sprites/{i}.png').convert_alpha() for i in range(10)]
    IMAGES.update({
        'gameover': pygame.image.load('assets/sprites/gameover.png').convert_alpha(),
        'message': pygame.image.load('assets/sprites/message.png').convert_alpha(),
        'base': pygame.image.load('assets/sprites/base.png').convert_alpha(),
    })

    item_image = pygame.image.load('assets/sprites/star.png').convert_alpha()
    item_size = (item_image.get_width() // 8, item_image.get_height() // 8)  
    IMAGES['item'] = pygame.transform.scale(item_image, item_size)

    IMAGES['life'] = pygame.image.load('assets/sprites/life.png').convert_alpha()
    IMAGES['modilife'] = pygame.transform.scale(IMAGES['life'], (20, 20)) 

    colon_image = pygame.image.load('assets/sprites/colon.png').convert_alpha()
    colon_size = (colon_image.get_width() // 2, colon_image.get_height() // 3.5)
    IMAGES['colon'] = pygame.transform.scale(colon_image, colon_size)

    if 'win' in sys.platform:
        soundExt = '.wav'
    else:
        soundExt = '.ogg'

    SOUNDS['die']    = pygame.mixer.Sound('assets/audio/die' + soundExt)
    SOUNDS['hit']    = pygame.mixer.Sound('assets/audio/hit' + soundExt)
    SOUNDS['point']  = pygame.mixer.Sound('assets/audio/point' + soundExt)
    SOUNDS['swoosh'] = pygame.mixer.Sound('assets/audio/swoosh' + soundExt)
    SOUNDS['wing']   = pygame.mixer.Sound('assets/audio/wing' + soundExt)

def showWelcomeAnimation(): # 게임 시작 전 환영 화면
    """Shows welcome screen animation of flappy bird"""
    global pipeSpacing
    playerIndex = 0
    playerIndexGen = cycle([0, 1, 2, 1]) 
    loopIter = 0

    playerx = int(SCREENWIDTH * 0.2)
    playery = int((SCREENHEIGHT - IMAGES['player'][0].get_height()) / 2)

    messagex = int((SCREENWIDTH - IMAGES['message'].get_width()) / 2)
    messagey = int(SCREENHEIGHT * 0.12) 

    basex = 0
    baseShift = IMAGES['base'].get_width() - IMAGES['background'].get_width()

    playerShmVals = {'val': 0, 'dir': 1}

    # 난이도 설정하는 문구 표시
    pygame.font.init()
    font = pygame.font.Font(None, 18)
    text = "Press 'E' for Easy mode, 'H' for Hard mode" 
    shadow_color = (0, 0, 0)
    text_color = (255, 255, 255)
    shadow_offset = 2 

    shadow_surface = font.render(text, True, shadow_color)
    shadow_rect = shadow_surface.get_rect(center=(SCREENWIDTH / 2, SCREENHEIGHT * 0.77 + shadow_offset)) # 기존 0.81

    text_surface = font.render(text, True, text_color)
    text_rect = text_surface.get_rect(center=(SCREENWIDTH / 2, SCREENHEIGHT * 0.77))

    while True:
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
            
            if event.type == KEYDOWN and event.key == K_e: # e key를 누르면 easy mode 로 게임 시작
                SOUNDS['wing'].play()
                pipeSpacing = EASY_PIPE_SPACING
                return {
                    'playery': playery + playerShmVals['val'],
                    'basex': basex,
                    'playerIndexGen': playerIndexGen,
                }
            if event.type == KEYDOWN and event.key == K_h: # h key를 누르면 hard mode로 게임 시작
                SOUNDS['wing'].play()
                pipeSpacing = HARD_PIPE_SPACING
                return {
                    'playery': playery + playerShmVals['val'],
                    'basex': basex,
                    'playerIndexGen': playerIndexGen,
                }

        if (loopIter + 1) % 5 == 0:
            playerIndex = next(playerIndexGen)
        loopIter = (loopIter + 1) % 30
        basex = -((-basex + 4) % baseShift)
        playerShm(playerShmVals)

        SCREEN.blit(IMAGES['background'], (0,0))
        SCREEN.blit(IMAGES['player'][playerIndex],
                    (playerx, playery + playerShmVals['val']))
        SCREEN.blit(IMAGES['message'], (messagex, messagey))
        SCREEN.blit(IMAGES['base'], (basex, BASEY))
        SCREEN.blit(shadow_surface, shadow_rect)
        SCREEN.blit(text_surface, text_rect)

        pygame.display.update()
        FPSCLOCK.tick(FPS)


def mainGame(movementInfo): #mainGame 화면
    global paused, pauseTime, startTime #일시정지 상태, 일시정지 시간 측정, 시작시간 전역변수 선언
    
    startTime = time.time() # 시간 초기화
    score = playerIndex = loopIter = 0 
    playerIndexGen = movementInfo['playerIndexGen']
    playerx, playery = int(SCREENWIDTH * 0.2), movementInfo['playery']

    basex = movementInfo['basex']
    baseShift = IMAGES['base'].get_width() - IMAGES['background'].get_width()

    newPipe1 = getRandomPipe()
    newPipe2 = getRandomPipe()

    # list of upper pipes, 위 아래 파이프의 생성 간격을 난이도 설정에 따라 더함.
    upperPipes = [
        {'x': SCREENWIDTH + 200, 'y': newPipe1[0]['y']},
        {'x': SCREENWIDTH + 200 + (SCREENWIDTH / 2) + pipeSpacing, 'y': newPipe2[0]['y']}, 
    ]


    lowerPipes = [
        {'x': SCREENWIDTH + 200, 'y': newPipe1[1]['y']},
        {'x': SCREENWIDTH + 200 + (SCREENWIDTH / 2) + pipeSpacing, 'y': newPipe2[1]['y']},
    ]

    # 아이템 생성하는 코드, 아이템 생성 확률은 20%(기영)
    item = None
    item_spawn_chance = 0.2


    dt = FPSCLOCK.tick(FPS)/1000
    pipeVelX = -128 * dt

    # player velocity, max velocity, downward acceleration, acceleration on flap
    playerVelY    =  -9   # player's velocity along Y, default same as playerFlapped
    playerMaxVelY =  10   # max vel along Y, max descend speed
    playerMinVelY =  -8   # min vel along Y, max ascend speed
    playerAccY    =   1   # players downward acceleration
    playerRot     =  45   # player's rotation
    playerVelRot  =   3   # angular speed
    playerRotThr  =  20   # rotation threshold
    playerFlapAcc =  -9   # players speed on flapping
    playerFlapped = False # True when player flaps

    #목숨 추가, 무적 상태와 시간, 깜빡거림 상태와 빈도 프레임 단위(영섭)
    playerLives         =   3   
    invincible          = False 
    blink_visible       = True                                                                    
    invincible_duration =   30                                                                
    blink_frequency     =   3                                                                    
    
    #일시정지 상태 변수 초기화
    paused = False
    pauseTime = 0 #일시정지 시간 값은 int형 자료로 저장함

    while True:
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
            
            #일시정지 이벤트 처리
            if (event.type == KEYDOWN and event.key == K_p):
                if paused == False:  #일시정지가 된 시점으로부터 시간 측정
                    pauseTimecheck = time.time()
                elif paused == True:
                    pauseTime += round(time.time() - pauseTimecheck)

                paused = not paused
                if paused:  # 일시정지 상태가 되면 pauseGame 함수를 호출
                    pauseGame()
            
            if event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP): 
                if playery > -2 * IMAGES['player'][0].get_height():
                    playerVelY = playerFlapAcc
                    playerFlapped = True
                    SOUNDS['wing'].play()
        
        #일시정지가 되면 뒤의 게임 로직은 무시됨
        if paused:
            continue
        
        # 충돌 검사
        if not invincible:    #무적이 아닌경우 충돌 무시
            crashTest = checkCrash({'x': playerx, 'y': playery, 'index': playerIndex},        
                               upperPipes, lowerPipes)
            if crashTest[0]:            #충돌 시  
                SOUNDS['hit'].play()    #충돌 소리 발생
                playerLives -= 1        #목숨 감소
                invincible = True       #무적 상태 활성화                              

        else :
            if invincible_duration % blink_frequency == 0:         #무적기간 / 무적빈도 의 값이 0일때만
                blink_visible = not blink_visible                  #not blink_visible으로 정의함으로써 true일땐 flase , false일땐 true로 변하여 밑의 조건문의 조건에 걸려서 깜빡거리도록함

            invincible_duration -= 1                               #프레임마다 while문이 한번 씩 돌고 이때마다 1씩 감소
            
            if invincible_duration <= 0:                           #만약 남은 무적시간이 0보다 작다면 
                invincible = False                                 #설정 값들 초기화(무적 해제, 무적시간 초기화, 깜빡거림 초기화)
                invincible_duration = 30
                blink_visible = True

        if playerLives == 0:    #목숨이 0개라면 종료
            return {
                'y': playery,
                'groundCrash': crashTest[1],
                'basex': basex,
                'upperPipes': upperPipes,
                'lowerPipes': lowerPipes,
                'score': score,
                'playerVelY': playerVelY,
                'playerRot': playerRot
            }

        # 아이템 충돌 확인 함수 추가
        if item and checkItemCollision({'x': playerx, 'y': playery, 'index': playerIndex}, item):
            score += 1
            SOUNDS['point'].play()
            item = None

        # check for score
        playerMidPos = playerx + IMAGES['player'][0].get_width() / 2
        playerMidY = playery + IMAGES['player'][0].get_height() / 2 
        for pipe in upperPipes:
            pipeMidPosleft = pipe['x'] 
            pipeMidPosright = pipe['x'] + IMAGES['pipe'][0].get_width()
            if pipeMidPosleft < playerMidPos <pipeMidPosright and not pipe.get('scored', False): # 캐릭터가 파이프를 지났는지 체크, 해당 파이프를 통과했을때 점수를 계산했는지 체크.(파이프에 scored 속성 추가, 준영)
                if upperPipes[0]['y'] + IMAGES['pipe'][0].get_height() < playerMidY < lowerPipes[0]['y']: 
                    score += 1 
                    pipe['scored'] = True  # 점수가 계산되면 True로 설정, 해당 파이프에 대해 점수가 계산되는 것 방지
                    SOUNDS['point'].play()
                    if random.random() < item_spawn_chance: #확률 로직 추가
                        item = getRandomItem(lowerPipes, upperPipes, playerx)
 

        if (loopIter + 1) % 3 == 0:
            playerIndex = next(playerIndexGen)
        loopIter = (loopIter + 1) % 30
        basex = -((-basex + 100) % baseShift)


        if playerRot > -90:
            playerRot -= playerVelRot


        if playerVelY < playerMaxVelY and not playerFlapped:
            playerVelY += playerAccY
        if playerFlapped:
            playerFlapped = False
            playerRot = 45

        playerHeight = IMAGES['player'][playerIndex].get_height()
        playery += min(playerVelY, BASEY - playery - playerHeight)


        for uPipe, lPipe in zip(upperPipes, lowerPipes):
            uPipe['x'] += pipeVelX
            lPipe['x'] += pipeVelX

        # 파이프 생성 조건 수정
        if 0 < len(upperPipes) and upperPipes[-1]['x'] < SCREENWIDTH - (SCREENWIDTH / 2 + pipeSpacing): # 파이프 개수에 상관 없이 마지막 파이프가 화면 중간을 넘어설때 새 파이프 추가
            newPipe = getRandomPipe()
            newPipeX = upperPipes[-1]['x'] + SCREENWIDTH / 2 + pipeSpacing
            upperPipes.append({'x': newPipeX, 'y': newPipe[0]['y'], 'scored': False})  # 새 파이프에 scored : False 속성 추가. 캐릭터가 해당 파이프를 지나게 될때 점수를 체크 하고 True로 변환
            lowerPipes.append({'x': newPipeX, 'y': newPipe[1]['y']})

        if len(upperPipes) > 0 and upperPipes[0]['x'] < -IMAGES['pipe'][0].get_width():
            upperPipes.pop(0)
            lowerPipes.pop(0)

        SCREEN.blit(IMAGES['background'], (0,0))

        for uPipe, lPipe in zip(upperPipes, lowerPipes):
            SCREEN.blit(IMAGES['pipe'][0], (uPipe['x'], uPipe['y']))
            SCREEN.blit(IMAGES['pipe'][1], (lPipe['x'], lPipe['y']))

        SCREEN.blit(IMAGES['base'], (basex, BASEY))
        showScore(score)

        visibleRot = playerRotThr
        if playerRot <= playerRotThr:
            visibleRot = playerRot

        #blink_visible 상태라면 이미지가 나타나지않도록 하는 조건문
        if blink_visible : 
            playerSurface = pygame.transform.rotate(IMAGES['player'][playerIndex], visibleRot)
            SCREEN.blit(playerSurface, (playerx, playery))

        # 아이템 그리기 추가
        if item:
            item['x'] += pipeVelX
            if item['x'] < -IMAGES['item'].get_width():
                item = None
            else:
                SCREEN.blit(IMAGES['item'], (item['x'], item['y']))

        #목숨 개수 표시
        ShowplayerLives(playerLives)

        pygame.display.update()
        FPSCLOCK.tick(FPS)


def showGameOverScreen(crashInfo): # 게임 오버 화면
    """crashes the player down and shows gameover image"""
    score = crashInfo['score']
    playerx = SCREENWIDTH * 0.2
    playery = crashInfo['y']
    playerHeight = IMAGES['player'][0].get_height()
    playerVelY = crashInfo['playerVelY']
    playerAccY = 2
    playerRot = crashInfo['playerRot']
    playerVelRot = 7
    soundToggle = False             # whlie True에서 die sound를 한 번만 출력하기 위한 토글 변수 생성

    basex = crashInfo['basex']

    upperPipes, lowerPipes = crashInfo['upperPipes'], crashInfo['lowerPipes']

    SOUNDS['hit'].play()

    # 게임 시간 출력
    playTime = int((time.time() - startTime) - pauseTime)  #시작부터 게임 오버까지 플레이한 시간을 저장함

    while True:
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP):
                if playery + playerHeight >= BASEY - 1:
                    return

        if playery + playerHeight < BASEY - 1:
            playery += min(playerVelY, BASEY - playery - playerHeight)

        if playerVelY < 15:
            playerVelY += playerAccY

        if not crashInfo['groundCrash']:

            # this play die sound / 'die' 출력 부분 수정 if문
            if playerRot <= -30 and soundToggle == False:   #사운드 수정사항, 새의 각도가 -30이하이고 soundToggle이 False일 때
                    SOUNDS['die'].play()
                    soundToggle = True                      #soundToggle은 True상태가 되며 다시 실행되기 전까지는 이 상태를 유지함
            
            if playerRot > -90:
                playerRot -= playerVelRot

        SCREEN.blit(IMAGES['background'], (0,0))

        for uPipe, lPipe in zip(upperPipes, lowerPipes):
            SCREEN.blit(IMAGES['pipe'][0], (uPipe['x'], uPipe['y']))
            SCREEN.blit(IMAGES['pipe'][1], (lPipe['x'], lPipe['y']))

        SCREEN.blit(IMAGES['base'], (basex, BASEY))
        showScore(score)

        playTimecheck(playTime)          #게임 오버시 시간 출력해주는 함수
        playerSurface = pygame.transform.rotate(IMAGES['player'][1], playerRot)
        SCREEN.blit(playerSurface, (playerx,playery))
        SCREEN.blit(IMAGES['gameover'], (50, 180))

        FPSCLOCK.tick(FPS)
        pygame.display.update()


# 아이템을 생성하는 함수 추가
def getRandomItem(lowerPipes, upperPipes, playerx):
    pipe_idx = random.randint(0, len(lowerPipes) - 1)
    lowerPipe = lowerPipes[pipe_idx]
    upperPipe = upperPipes[pipe_idx]
    
    itemX = max(lowerPipe['x'], playerx + 50) + 50 # 항상 아이템을 캐릭터보다 앞에, 파이프 사이에 위치
    itemY = random.randint(int(upperPipe['y'] + IMAGES['pipe'][0].get_height() + PIPEGAPSIZE / 2),
                           int(lowerPipe['y'] - PIPEGAPSIZE / 2))  # y좌표는 항상 위 파이프와 아래 파이프 사이에 나오도록 설정
    
    return {'x': itemX, 'y': itemY}

#플레이 시간 출력해주는 함수
def playTimecheck(playTime):                            # 'MM' 'SS'로 출력하기 위해 리스트에 시간값을 다 분해함
    timeArr = [
        ((playTime // 60) // 10), 
        ((playTime // 60) % 10), 
        ((playTime % 60) // 10), 
        ((playTime % 60) % 10)
    ]

    x_offset = SCREENWIDTH // 2 - 75                                    #x위치 최적 75
    y_offset = SCREENHEIGHT // 2 - 20                                   #y위치 최적 20
    
    for coln, seg in enumerate(timeArr):                                #인덱스랑 값을 같이 가져옴
        if coln == 2:
            SCREEN.blit(IMAGES['colon'], (x_offset, y_offset + 3))      #콜론 출력
            x_offset += int(IMAGES['colon'].get_width()) + 10
        
        SCREEN.blit(IMAGES['numbers'][seg], (x_offset, y_offset))
        x_offset += int(IMAGES['numbers'][seg].get_width()) + 10


def playerShm(playerShm):
    if abs(playerShm['val']) == 8:
        playerShm['dir'] *= -1

    if playerShm['dir'] == 1:
         playerShm['val'] += 1
    else:
        playerShm['val'] -= 1


def getRandomPipe():
    gapY = random.randrange(0, int(BASEY * 0.6 - PIPEGAPSIZE))
    gapY += int(BASEY * 0.2)
    pipeHeight = IMAGES['pipe'][0].get_height()
    pipeX = SCREENWIDTH + 10

    return [
        {'x': pipeX, 'y': gapY - pipeHeight},  # upper pipe
        {'x': pipeX, 'y': gapY + PIPEGAPSIZE}, # lower pipe
    ]


def showScore(score):
    """displays score in center of screen"""
    scoreDigits = [int(x) for x in list(str(score))]
    totalWidth = 0

    for digit in scoreDigits:
        totalWidth += IMAGES['numbers'][digit].get_width()

    Xoffset = (SCREENWIDTH - totalWidth) / 2

    for digit in scoreDigits:
        SCREEN.blit(IMAGES['numbers'][digit], (Xoffset, SCREENHEIGHT * 0.1))
        Xoffset += IMAGES['numbers'][digit].get_width()


def checkCrash(player, upperPipes, lowerPipes): # 새와 파이프가 충돌했을 때

    """returns True if player collides with base or pipes."""
    pi = player['index']
    player['w'] = IMAGES['player'][0].get_width()
    player['h'] = IMAGES['player'][0].get_height()

    if player['y'] + player['h'] >= BASEY - 1:
        return [True, True]
    else:

        playerRect = pygame.Rect(player['x'], player['y'],
                      player['w'], player['h'])
        pipeW = IMAGES['pipe'][0].get_width()
        pipeH = IMAGES['pipe'][0].get_height()

        for uPipe, lPipe in zip(upperPipes, lowerPipes):
            uPipeRect = pygame.Rect(uPipe['x'], uPipe['y'], pipeW, pipeH)
            lPipeRect = pygame.Rect(lPipe['x'], lPipe['y'], pipeW, pipeH)

            pHitMask = HITMASKS['player'][pi]
            uHitmask = HITMASKS['pipe'][0]
            lHitmask = HITMASKS['pipe'][1]

            uCollide = pixelCollision(playerRect, uPipeRect, pHitMask, uHitmask)
            lCollide = pixelCollision(playerRect, lPipeRect, pHitMask, lHitmask)

            if uCollide or lCollide:
                return [True, False]

    return [False, False]

def pixelCollision(rect1, rect2, hitmask1, hitmask2): # 픽셀로 봤을 때 두 객체가 겹치는지 확인
    """Checks if two objects collide and not just their rects"""
    rect = rect1.clip(rect2)

    if rect.width == 0 or rect.height == 0:
        return False

    x1, y1 = rect.x - rect1.x, rect.y - rect1.y
    x2, y2 = rect.x - rect2.x, rect.y - rect2.y

    for x in xrange(rect.width):
        for y in xrange(rect.height):
            if hitmask1[x1+x][y1+y] and hitmask2[x2+x][y2+y]:
                return True
    return False

def getHitmask(image): #이미지와 겹쳤을 때 충돌
    """returns a hitmask using an image's alpha."""
    mask = []
    for x in xrange(image.get_width()):
        mask.append([])
        for y in xrange(image.get_height()):
            mask[x].append(bool(image.get_at((x,y))[3]))
    return mask

#아이템과 캐릭터가 충돌하는지 확인하는 함수 추가
def checkItemCollision(player, item):
    playerRect = pygame.Rect(player['x'], player['y'], IMAGES['player'][0].get_width(), IMAGES['player'][0].get_height())
    itemRect = pygame.Rect(item['x'], item['y'], IMAGES['item'].get_width(), IMAGES['item'].get_height())
    return playerRect.colliderect(itemRect)

#목숨의 개수를 보여주는 함수 추가
def ShowplayerLives(playerLives):      
    for i in range(playerLives):                                                        
        SCREEN.blit(IMAGES['modilife'],(10+i*25,10))   

#배경 선택 함수 추가
def selectBackground():
    select = 0
    selected = False
    
    while not selected:
        #배경 선택 텍스트 표시 
        font = pygame.font.Font(None, 36)
        title_text = font.render('Select Background', True, (255, 255, 255)) 
        title_rect = title_text.get_rect(center=(SCREENWIDTH // 2, SCREENHEIGHT // 6)) #텍스트 위치 설정
        SCREEN.blit(title_text, title_rect) #화면에 텍스트 표시

        #이미지 위치 설정
        for i in range(len(BACKGROUNDS_LIST)):
            background_image = pygame.image.load(BACKGROUNDS_LIST[i]) 
            image_rect = background_image.get_rect(center=(SCREENWIDTH // 2 * (i + 1), SCREENHEIGHT // 2))
            SCREEN.blit(background_image, image_rect)

            #이미지 아래에 나타낼 텍스트 설정
            font = pygame.font.Font(None, 22)
            prompt_text = font.render(f'Press {i + 1}', True, (255, 255, 255))
            prompt_rect = prompt_text.get_rect(center=(SCREENWIDTH // 4 * (i + 1) + 40, SCREENHEIGHT // 2 + 50))
            SCREEN.blit(prompt_text, prompt_rect)

        #화면 업데이트
        pygame.display.update()
        FPSCLOCK.tick(FPS)

        #사용자에게 숫자로 배경 입력받음
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
            elif event.type == KEYDOWN:
                if event.key == K_1: select = 1
                elif event.key == K_2: select = 2
                
                if select: 
                    selected = True
    return select - 1 


#캐릭터 선택 함수 추가
def selectPlayer():
    select = 0
    selected = False
    
    while not selected:
        #캐릭터 선택 텍스트 표시 
        font = pygame.font.Font(None, 36)
        title_text = font.render('Select Player', True, (255, 255, 255)) 
        title_rect = title_text.get_rect(center=(SCREENWIDTH // 2, SCREENHEIGHT // 6)) 
        SCREEN.blit(title_text, title_rect) 

        #화면에 표시할 player 이미지들
        player_images = [pygame.image.load(PLAYERS_LIST[0][1]).convert_alpha(),
                            pygame.image.load(PLAYERS_LIST[1][1]).convert_alpha(),
                            pygame.image.load(PLAYERS_LIST[2][1]).convert_alpha()]

        #이미지 위치 설정
        for i in range(len(player_images)):
            player_image = player_images[i]
            image_rect = player_image.get_rect(center=(SCREENWIDTH // 4 * (i + 1), SCREENHEIGHT // 2))
            SCREEN.blit(player_image, image_rect)

            #이미지 아래에 나타낼 텍스트 설정
            font = pygame.font.Font(None, 22)
            prompt_text = font.render(f'Press {i + 1}', True, (255, 255, 255))
            prompt_rect = prompt_text.get_rect(center=(SCREENWIDTH // 4 * (i + 1), SCREENHEIGHT // 2 + 50))
            SCREEN.blit(prompt_text, prompt_rect)

        #화면 업데이트
        pygame.display.update()
        FPSCLOCK.tick(FPS)


        #사용자에게 숫자로 캐릭터 입력받음
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
            elif event.type == KEYDOWN:
                if event.key == K_1: select = 1
                elif event.key == K_2: select = 2
                elif event.key == K_3: select = 3
                
                if select: 
                    selected = True

    return select - 1 

#일시정지 함수 추가
def pauseGame():
    global paused
    paused = True
    font = pygame.font.Font(None, 36)
    paused_text = font.render('PAUSE', True, (255, 255, 255)) 
    paused_rect = paused_text.get_rect(center=(SCREENWIDTH // 2, SCREENHEIGHT // 2)) 
    
    while paused:
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
            elif event.type == KEYDOWN:
                if event.key == K_p:  # 'p' 키를 누르면 일시정지 해제
                    paused = False
        SCREEN.blit(paused_text, paused_rect) 
        pygame.display.update()
        FPSCLOCK.tick(FPS)
