from os import environ
import random
environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
import pygame
from serial import Serial
import time

pygame.init()


def digit_span(arduino, num_cards, rfid_map):
    pygame.init()

    correctSoundEffect = pygame.mixer.Sound('./sounds/correct.mp3')
    incorrectSoundEffect = pygame.mixer.Sound('./sounds/incorrect.mp3')
    forwardSound = pygame.mixer.Sound('./sounds/digit_span/forward.mp3')
    backwardSound = pygame.mixer.Sound('./sounds/digit_span/backward.mp3')
    startSound = pygame.mixer.Sound('./sounds/digit_span/start.mp3')

    correctSoundEffect.set_volume(0.5)
    incorrectSoundEffect.set_volume(0.3)
    forwardSound.set_volume(0.5)
    backwardSound.set_volume(0.5)
    startSound.set_volume(0.2)

    myFont = pygame.font.Font("./font/NanumGothic.ttf", 30)
    myFont_big = pygame.font.Font("./font/NanumGothic.ttf", 300)
    myFont_medium = pygame.font.Font("./font/NanumGothic.ttf", 100)

    # rfid_map = {
    # '5a392f28':0,
    # '5adb6f28':1,
    # '4ad82d28':2,
    # '5a6f5d28':3,
    # '4ae9a628':4,
    # '5a9a8628':5,
    # '4ae1b128':6,
    # '5a2ee328':7,
    # '5a3ddf28':8,
    # '4ac6d828':9,
    # }

    sounds = [
        "./sounds/digit_span/zero.wav",
        "./sounds/digit_span/one.wav",
        "./sounds/digit_span/two.wav",
        "./sounds/digit_span/three.wav",
        "./sounds/digit_span/four.wav",
        "./sounds/digit_span/five.wav",
        "./sounds/digit_span/six.wav",
        "./sounds/digit_span/seven.wav",
        "./sounds/digit_span/eight.wav",
        "./sounds/digit_span/nine.wav"
        ]




    idxList = list(rfid_map.values())
    assert num_cards <= len(idxList)
    randomChoices = random.sample(idxList, num_cards)


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

    arduino_input = None
    buf = ""
    gameLoop = True
    i = 0
    rfid_map_keys = list(rfid_map.keys())
    rfid_map_values = list(rfid_map.values())

    forwardSound.play()
    screen.blit(bgImage, bgImageRect)
    text_wait = myFont_medium.render(f'정방향 태그를 시작합니다.', 1, BLACK)
    text_wait_rect = text_wait.get_rect()
    text_wait_rect.center = (gameWidth * 0.5, gameHeight * 0.5)
    screen.blit(text_wait, text_wait_rect)
    pygame.display.update()
    time_show = random.randint(3, 5)
    pygame.time.wait(time_show * 1000)

    tmp = ""
    for digitStr in randomChoices:
        tmp += str(digitStr)
        screen.blit(bgImage, bgImageRect)
        text_wait = myFont_big.render(tmp, 1, BLACK)
        text_wait_rect = text_wait.get_rect()
        text_wait_rect.center = (gameWidth * 0.5, gameHeight * 0.5)
        screen.blit(text_wait, text_wait_rect)
        pygame.display.update()
        soundDir = sounds[digitStr]
        digitSound = pygame.mixer.Sound(soundDir)
        digitSound.play()
        time.sleep(1)
        digitSound.stop()
    
    forward_inputs = []
    startSound.play()
    start = time.time()  
    cnt = 0
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

        text_progress = myFont.render(f'{i/len(randomChoices)*100:.2f}%', 1, BLACK)
        text_progress_rect = text_progress.get_rect()
        text_progress_rect.center = (gameWidth * 0.5, gameHeight * 0.97)
        
        screen.blit(text_elapsed, text_elapsed_rect)
        screen.blit(text_wrong, text_wrong_rect)
        screen.blit(text_progress, text_progress_rect)

        text_tag = myFont_big.render(f'{randomChoices[i]}', 1, BLACK)
        text_tag_rect = text_tag.get_rect()
        text_tag_rect.center = (gameWidth * 0.5, gameHeight * 0.5)
        screen.blit(text_tag, text_tag_rect)
        text_tag_desc = myFont.render('태그해야 할 카드', 1, BLACK)
        text_tag_desc_rect = text_tag_desc.get_rect()
        text_tag_desc_rect.center = (gameWidth * 0.5, gameHeight * 0.7)
        screen.blit(text_tag_desc, text_tag_desc_rect)

        try:
            text_tag_pre = myFont_medium.render(f'{randomChoices[i-1]}', 1, BLACK)
            text_tag_pre_rect = text_tag_pre.get_rect()
            text_tag_pre_rect.center = (gameWidth * 0.25, gameHeight * 0.5)
            screen.blit(text_tag_pre, text_tag_pre_rect)
        except:
            pass

        try:
            text_tag_next = myFont_medium.render(f'{randomChoices[i+1]}', 1, BLACK)
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
                    forward_inputs.append(input_index)
                except:
                    continue
                
                if input_index == randomChoices[i]:
                    correctSoundEffect.play()
                    right += 1
                    print('right')
                else:
                    incorrectSoundEffect.play()
                    wrong += 1
                    print('wrong')
                i += 1

            elif arduino_input == buf:
                if cnt > 10:
                    buf = arduino_input
                    try:
                        input_index = rfid_map_keys.index(arduino_input)
                        forward_inputs.append(input_index)
                    except:
                        continue
                    
                    if input_index == randomChoices[i]:
                        correctSoundEffect.play()
                        right += 1
                        print('right')
                    else:
                        incorrectSoundEffect.play()
                        wrong += 1
                        print('wrong')
                    cnt = 0
                    i += 1
                else:
                    cnt += 1

            if len(forward_inputs) == len(randomChoices):
                gameLoop = False

        pygame.display.update()
        clock.tick(60)

    forward_time = time.time()-start
    forward_right = right


# 역방향




    buf = ""
    arduino_input = None
    gameLoop = True
    i = 0
    right = 0
    wrong = 0
    backward_inputs = []
    randomChoices = list(reversed(randomChoices))
    backwardSound.play()
    screen.blit(bgImage, bgImageRect)
    text_wait = myFont_medium.render(f'잠시 후 역방향 태그를 시작합니다.', 1, BLACK)
    text_wait_rect = text_wait.get_rect()
    text_wait_rect.center = (gameWidth * 0.5, gameHeight * 0.5)
    screen.blit(text_wait, text_wait_rect)
    pygame.display.update()
    time_show = random.randint(5, 7)
    pygame.time.wait(time_show * 1000)

    startSound.play()
    start = time.time()
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
        text_progress = myFont.render(f'{i/len(randomChoices)*100:.2f}%', 1, BLACK)
        text_progress_rect = text_progress.get_rect()
        text_progress_rect.center = (gameWidth * 0.5, gameHeight * 0.97)
        screen.blit(text_elapsed, text_elapsed_rect)
        screen.blit(text_wrong, text_wrong_rect)
        screen.blit(text_progress, text_progress_rect)
        text_tag = myFont_big.render(f'{randomChoices[i]}', 1, BLACK)
        text_tag_rect = text_tag.get_rect()
        text_tag_rect.center = (gameWidth * 0.5, gameHeight * 0.5)
        screen.blit(text_tag, text_tag_rect)
        text_tag_desc = myFont.render('태그해야 할 카드', 1, BLACK)
        text_tag_desc_rect = text_tag_desc.get_rect()
        text_tag_desc_rect.center = (gameWidth * 0.5, gameHeight * 0.7)
        screen.blit(text_tag_desc, text_tag_desc_rect)

        try:
            text_tag_pre = myFont_medium.render(f'{randomChoices[i-1]}', 1, BLACK)
            text_tag_pre_rect = text_tag_pre.get_rect()
            text_tag_pre_rect.center = (gameWidth * 0.25, gameHeight * 0.5)
            screen.blit(text_tag_pre, text_tag_pre_rect)
        except:
            pass

        try:
            text_tag_next = myFont_medium.render(f'{randomChoices[i+1]}', 1, BLACK)
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
                    backward_inputs.append(input_index)
                except:
                    continue
                
                if input_index == randomChoices[i]:
                    correctSoundEffect.play()
                    right += 1
                    print('right')
                else:
                    incorrectSoundEffect.play()
                    wrong += 1
                    print('wrong')
                i += 1
                
            elif arduino_input == buf:
                if cnt > 10:
                    buf = arduino_input
                    try:
                        input_index = rfid_map_keys.index(arduino_input)
                        backward_inputs.append(input_index)
                    except:
                        continue
                    
                    if input_index == randomChoices[i]:
                        correctSoundEffect.play()
                        right += 1
                        print('right')
                    else:
                        incorrectSoundEffect.play()
                        wrong += 1
                        print('wrong')
                    cnt = 0
                    i += 1
                else:
                    cnt += 1
            if len(backward_inputs) == len(randomChoices):
                gameLoop = False
        pygame.display.update()
        clock.tick(60)
    
    backward_time = time.time()-start
    backward_right = right

    if gameLoop == False:
        text_result1 = myFont.render(f'결과', 1, BLACK)
        text_result1_rect = text_result1.get_rect()
        text_result1_rect.center = (gameWidth * 0.5, gameHeight * 0.1)

        text_result2 = myFont.render(f'총 소요 시간: 정방향: {forward_time:.2f}초,\t역방향: {backward_time:.2f}초', 1, BLACK)
        text_result2_rect = text_result2.get_rect()
        text_result2_rect.center = (gameWidth * 0.5, gameHeight * 0.3)

        text_result3 = myFont.render(f'정방향 정답: {forward_right}개,\t역방향 정답: {backward_right}개', 1, BLACK)
        text_result3_rect = text_result3.get_rect()
        text_result3_rect.center = (gameWidth * 0.5, gameHeight * 0.5)

        text_result5 = myFont.render(f'계속하려면 엔터 키를 누르세요...', 1, BLACK)
        text_result5_rect = text_result5.get_rect()
        text_result5_rect.center = (gameWidth * 0.5, gameHeight * 0.9)
            
        screen.blit(bgImage, bgImageRect)
        screen.blit(text_result1, text_result1_rect)
        screen.blit(text_result2, text_result2_rect)
        screen.blit(text_result3, text_result3_rect)

        screen.blit(text_result5, text_result5_rect)
        pygame.display.update()

        while True:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        pygame.quit()
                        return None

    return None
