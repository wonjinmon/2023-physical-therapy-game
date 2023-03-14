from os import environ
from statistics import mean
environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
import pygame
from serial import Serial
import time
import random

pygame.init()



def tmt_b(arduino, cnt, rfid_map):
    pygame.init()

    correctSoundEffect = pygame.mixer.Sound('./sounds/correct.mp3')
    incorrectSoundEffect = pygame.mixer.Sound('./sounds/incorrect.mp3')
    startSound = pygame.mixer.Sound('./sounds/tmt/start.mp3')
    dingSound = pygame.mixer.Sound('./sounds/tmt/ding.mp3')
    congratSound = pygame.mixer.Sound('./sounds/congratulations.mp3')
    correctSoundEffect.set_volume(0.5)
    incorrectSoundEffect.set_volume(0.3)
    startSound.set_volume(0.3)
    dingSound.set_volume(0.2)
    congratSound.set_volume(0.5)
    myFont = pygame.font.Font("./font/NanumGothic.ttf", 30)
    myFont_big = pygame.font.Font("./font/NanumGothic.ttf", 300)
    myFont_medium = pygame.font.Font("./font/NanumGothic.ttf", 100)

    # rfid_map = {
    # '5a749d28':'0',
    # '4abca828':'ㄱ',
    # '5ada3528':'1',
    # '5aa21628':'ㄴ',
    # '5a603528':'2',
    # '4aeb8f28':'ㄷ',
    # '4ad38c28':'3',
    # '5a121228':'ㄹ',
    # '5a911328':'4',
    # '5a27928':'ㅁ',
    # '5a996128':'5',
    # '5a76ed28':'ㅂ',
    # '5a36e628':'6',
    # '4aa0d628':'ㅅ',
    # '4acf4e28':'7',
    # '5ab79228':'ㅇ',
    # '4ae13428':'8',
    # '4aca3328':'ㅈ',
    # '4ad0e228':'9',
    # '4aff2f28':'ㅊ',
    # '5a45ea28':'10',
    # '4aa53428':'ㅋ',
    # '5a30d928':'11',
    # '5a1a5128':'ㅌ',
    # '5a20bb28':'12',
    # '4abb6c28':'ㅍ',
    # '4a9a6828':'13',
    # '4abe7028':'ㅎ',
    # '5a33e428':'14',
    # }

    rfid_map = dict(list(rfid_map.items())[:cnt])

    gameWidth = 1600
    gameHeight = 900
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    right = 0
    wrong = 0

    screen = pygame.display.set_mode((gameWidth, gameHeight))
    pygame.display.set_caption('TMT')
    gameIcon = pygame.image.load(f'./MemoryGame/images/card.png')
    pygame.display.set_icon(gameIcon)

    bgImage = pygame.image.load('./MemoryGame/images/Background.png')
    bgImage = pygame.transform.scale(bgImage, (gameWidth, gameHeight))
    bgImageRect = bgImage.get_rect()

    clock = pygame.time.Clock()

    buf = ""
    gameLoop = True
    i = 0
    rfid_map_keys = list(rfid_map.keys())
    rfid_map_values = list(rfid_map.values())

    startSound.play()
    screen.blit(bgImage, bgImageRect)
    text_wait = myFont_medium.render(f'잠시 후 테스트를 시작합니다.', 1, BLACK)
    text_wait_rect = text_wait.get_rect()
    text_wait_rect.center = (gameWidth * 0.5, gameHeight * 0.5)
    screen.blit(text_wait, text_wait_rect)
    pygame.display.update()
    time_show = random.randint(3, 5)
    pygame.time.wait(time_show * 1000)

    start = time.time()
    latency = time.time()
    latencies = []
    dingSound.play()
    while gameLoop:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                gameLoop = False
        
        screen.blit(bgImage, bgImageRect)
        text_elapsed = myFont.render(f'진행 시간: {int(time.time()-start)}초', 1, BLACK)
        text_elapsed_rect = text_elapsed.get_rect()
        text_elapsed_rect.center = (gameWidth * 0.2, gameHeight * 0.97)
        text_wrong = myFont.render(f'오답: {wrong}번', 1, BLACK)
        text_wrong_rect = text_wrong.get_rect()
        text_wrong_rect.center = (gameWidth * 0.8, gameHeight * 0.97)
        text_progress = myFont.render(f'{i/len(rfid_map)*100:.2f}%', 1, BLACK)
        text_progress_rect = text_progress.get_rect()
        text_progress_rect.center = (gameWidth * 0.5, gameHeight * 0.97)
        screen.blit(text_elapsed, text_elapsed_rect)
        screen.blit(text_wrong, text_wrong_rect)
        screen.blit(text_progress, text_progress_rect)

        text_tag = myFont_big.render(f'{rfid_map_values[i]}', 1, BLACK)
        text_tag_rect = text_tag.get_rect()
        text_tag_rect.center = (gameWidth * 0.5, gameHeight * 0.5)
        screen.blit(text_tag, text_tag_rect)
        text_tag_desc = myFont.render('태그해야 할 카드', 1, BLACK)
        text_tag_desc_rect = text_tag_desc.get_rect()
        text_tag_desc_rect.center = (gameWidth * 0.5, gameHeight * 0.7)
        screen.blit(text_tag_desc, text_tag_desc_rect)

        try:
            text_tag_pre = myFont_medium.render(f'{rfid_map_values[i-1]}', 1, BLACK)
            text_tag_pre_rect = text_tag_pre.get_rect()
            text_tag_pre_rect.center = (gameWidth * 0.25, gameHeight * 0.5)
            screen.blit(text_tag_pre, text_tag_pre_rect)
        except:
            pass

        try:
            text_tag_next = myFont_medium.render(f'{rfid_map_values[i+1]}', 1, BLACK)
            text_tag_next_rect = text_tag_next.get_rect()
            text_tag_next_rect.center = (gameWidth * 0.75, gameHeight * 0.5)
            screen.blit(text_tag_next, text_tag_next_rect)
        except:
            pass

        if arduino.readable():
            arduino_input = arduino.readline().decode().strip()

        if arduino_input:
            if arduino_input != buf:
                print(arduino_input)
                buf = arduino_input
                try:
                    input_index = rfid_map_keys.index(arduino_input)
                except:
                    continue
                
                if input_index == i:
                    correctSoundEffect.play()
                    i += 1
                    right += 1
                    latency_temp = time.time()
                    latencies.append(latency_temp - latency)
                    latency = latency_temp
                    print('right')
                else:
                    incorrectSoundEffect.play()
                    wrong += 1
                    print('wrong')

                if right == len(rfid_map):
                    gameLoop = False
        
        pygame.display.update()
        clock.tick(60)

    if gameLoop == False:
        end = time.time()
        congratSound.play()
        text_result1 = myFont.render(f'결과', 1, BLACK)
        text_result1_rect = text_result1.get_rect()
        text_result1_rect.center = (gameWidth * 0.5, gameHeight * 0.1)

        text_result2 = myFont.render(f'총 소요 시간: {int(end-start)}초', 1, BLACK)
        text_result2_rect = text_result2.get_rect()
        text_result2_rect.center = (gameWidth * 0.5, gameHeight * 0.3)

        text_result3 = myFont.render(f'오답: {wrong}개', 1, BLACK)
        text_result3_rect = text_result3.get_rect()
        text_result3_rect.center = (gameWidth * 0.5, gameHeight * 0.5)

        text_result4 = myFont.render(f'평균 반응 시간: {mean(latencies):.2f}초', 1, BLACK)
        text_result4_rect = text_result4.get_rect()
        text_result4_rect.center = (gameWidth * 0.5, gameHeight * 0.7)

        text_result5 = myFont.render(f'계속하려면 엔터 키를 누르세요...', 1, BLACK)
        text_result5_rect = text_result5.get_rect()
        text_result5_rect.center = (gameWidth * 0.5, gameHeight * 0.9)
            
        screen.blit(bgImage, bgImageRect)
        screen.blit(text_result1, text_result1_rect)
        screen.blit(text_result2, text_result2_rect)
        screen.blit(text_result3, text_result3_rect)
        screen.blit(text_result4, text_result4_rect)
        screen.blit(text_result5, text_result5_rect)
        pygame.display.update()

        while True:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        pygame.quit()
                        return None

    return None
