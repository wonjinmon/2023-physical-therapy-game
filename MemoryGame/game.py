from statistics import mean
import pygame, os, random, time

from serial import Serial
from serial.tools import list_ports
# 6 X 6


os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'


def memory_game(arduino, rfid_map, imageset='animals', gameColumns=6, gameRows=6):

    # rfid_map = {
    # 'ba85d11b': 0,
    # 'ba72961b': 1,
    # 'ba93791b': 2,
    # 'ba8aa21b': 3,
    # 'ba861a1b': 4,
    # 'ba8f131b': 5,
    # 'ba93521b': 6,
    # 'ba93591b': 7,
    # 'ba8eeb1b': 8,
    # 'ba7371b': 9,
    # 'ba816b1b': 10,
    # 'ba7c511b': 11,
    # 'ba777b1b': 12,
    # 'ba7c4a1b': 13,
    # 'ba7331b': 14,
    # 'ba6e241b': 15,
    # 'ba69331b': 16,
    # 'ba69321b': 17,
    # 'ba6e231b': 18,
    # 'ba7361b': 19,
    # 'ba7c4f1b': 20,
    # 'ba7c4b1b': 21,
    # 'ba7381b': 22,
    # 'ba7cb11b': 23,
    # 'ba81141b': 24,
    # 'ba63be1b': 25,
    # 'ba5f371b': 26,
    # 'ba93801b': 27,
    # 'ba8f1d1b': 28,
    # 'ba86161b': 29,
    # 'ba85ca1b': 30,
    # 'ba81131b': 31,
    # 'ba8a641b': 32,
    # 'ba8f1c1b': 33,
    # 'ba8a681b': 34,
    # 'ba85cb1b': 35
    # }

    pygame.init()

    correctSoundEffect = pygame.mixer.Sound('./sounds/correct.mp3')
    incorrectSoundEffect = pygame.mixer.Sound('./sounds/incorrect.mp3')
    congratSound = pygame.mixer.Sound('./sounds/congratulations.mp3')
    correctSoundEffect.set_volume(0.5)
    incorrectSoundEffect.set_volume(0.3)
    congratSound.set_volume(0.5)


    myFont = pygame.font.Font("./font/NanumGothic.ttf", 30)

    #  Variables for Game
    gameWidth = 1600
    gameHeight = 900
    picSize = 128
    # gameColumns = 6
    # gameRows = 6
    padding = 10
    leftMargin = (gameWidth - ((picSize + padding) * gameColumns)) // 2
    rightMargin = leftMargin
    topMargin = (gameHeight - ((picSize + padding) * gameRows)) // 2
    bottomMargin = topMargin
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    selection1 = None
    selection2 = None
    right = 0
    wrong = 0

    # Loading the pygame screen.
    screen = pygame.display.set_mode((gameWidth, gameHeight))
    pygame.display.set_caption('Memory Game')
    gameIcon = pygame.image.load(f'./MemoryGame/images/card.png')
    pygame.display.set_icon(gameIcon)

    # Load the BackGround image into Python
    bgImage = pygame.image.load('./MemoryGame/images/Background.png')
    bgImage = pygame.transform.scale(bgImage, (gameWidth, gameHeight))
    bgImageRect = bgImage.get_rect()

    cardImage = pygame.image.load('./MemoryGame/images/card.png')
    cardImage = pygame.transform.scale(cardImage, (picSize, picSize))

    # Create list of Memory Pictures
    memoryPictures = []
    for item in os.listdir(f'./MemoryGame/images/{imageset}/'):
        memoryPictures.append(item.split('.')[0])
    memoryPictures = random.sample(memoryPictures, int(gameColumns*gameRows/2))
    memoryPicturesCopy = memoryPictures.copy()
    memoryPictures.extend(memoryPicturesCopy)
    memoryPicturesCopy.clear()
    random.shuffle(memoryPictures)

    # Load each of the images into the python memory
    memPics = []
    memPicsRect = []
    hiddenImages = []
    sounds = []
    for item in memoryPictures:
        picture = pygame.image.load(f'./MemoryGame/images/{imageset}/{item}.png')
        picture = pygame.transform.scale(picture, (picSize, picSize))
        memPics.append(picture)
        pictureRect = picture.get_rect()
        memPicsRect.append(pictureRect)

        selectedSound = pygame.mixer.Sound(f'./sounds/{imageset}/{item}.mp3')
        selectedSound.set_volume(0.5)
        sounds.append(selectedSound)

    for j in range(gameRows):
        for k in range(gameColumns):
            i = j * gameColumns + k
            memPicsRect[i][0] = leftMargin + ((picSize + padding) * k)
            memPicsRect[i][1] = topMargin + ((picSize + padding) * j)
            hiddenImages.append(False)

    screen.blit(bgImage, bgImageRect)
    for i in range(gameColumns*gameRows):
        screen.blit(memPics[i], memPicsRect[i])
    pygame.display.update()

    time_show = random.randint(3, 10)
    pygame.time.wait(time_show * 1000)

    screen.blit(bgImage, bgImageRect)
    for i in range(gameColumns*gameRows):
        screen.blit(cardImage, memPicsRect[i])

    pygame.display.update()

    buf = ''
    gameLoop = True
    latency = time.time()
    latencies = []
    start = time.time()
    while gameLoop:
        # Load background image
        screen.blit(bgImage, bgImageRect)

        text_elapsed = myFont.render(f'진행 시간: {int(time.time()-start)}초', 1, BLACK)
        text_wrong = myFont.render(f'오답: {wrong}번', 1, BLACK)
        text_elapsed_rect = text_elapsed.get_rect()
        text_wrong_rect = text_wrong.get_rect()
        text_elapsed_rect.center = (gameWidth * 0.2, gameHeight * 0.97)
        text_wrong_rect.center = (gameWidth * 0.8, gameHeight * 0.97)
        screen.blit(text_elapsed, text_elapsed_rect)
        screen.blit(text_wrong, text_wrong_rect)

        if arduino.readable():
            arduino_input = arduino.readline().decode().strip()

        if arduino_input:
            if arduino_input != buf:
                buf = arduino_input
                try:
                    input_index = rfid_map[arduino_input]
                except KeyError:
                    continue

                if hiddenImages[input_index] != True:
                    if selection1 != None:
                        selection2 = input_index
                        hiddenImages[selection2] = True
                    else:
                        selection1 = input_index
                        hiddenImages[selection1] = True
                    sounds[input_index].play()
                
                print(f'input: {input_index}')

        # Input events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                gameLoop = False
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for item in memPicsRect:
                    if item.collidepoint(event.pos):
                        if hiddenImages[memPicsRect.index(item)] != True:
                            if selection1 != None:
                                selection2 = memPicsRect.index(item)
                                hiddenImages[selection2] = True
                            else:
                                selection1 = memPicsRect.index(item)
                                hiddenImages[selection1] = True
                            sounds[memPicsRect.index(item)].play()
        
        for i in range(gameColumns*gameRows):
            if hiddenImages[i] == True:
                screen.blit(memPics[i], memPicsRect[i])
            else:
                screen.blit(cardImage, memPicsRect[i])


        pygame.display.update()

        if selection1 != None and selection2 != None:
            if memoryPictures[selection1] == memoryPictures[selection2]:
                selection1, selection2 = None, None
                right += 1
                correctSoundEffect.play()
                latency_temp = time.time()
                latencies.append(latency_temp - latency)
                latency = latency_temp
                
            else:
                incorrectSoundEffect.play()
                pygame.time.wait(500)
                hiddenImages[selection1] = False
                hiddenImages[selection2] = False
                selection1, selection2 = None, None
                wrong += 1

        win = 1
        for number in range(len(hiddenImages)):
            win *= hiddenImages[number]

        if win == 1:
            gameLoop = False

        pygame.display.update()

    end = time.time()
    congratSound.play()
    text_result1 = myFont.render(f'결과', 1, BLACK)
    text_result1_rect = text_result1.get_rect()
    text_result1_rect.center = (gameWidth * 0.5, gameHeight * 0.1)

    text_result2 = myFont.render(f'총 소요 시간: {(end-start):.2f}초', 1, BLACK)
    text_result2_rect = text_result2.get_rect()
    text_result2_rect.center = (gameWidth * 0.5, gameHeight * 0.3)

    text_result3 = myFont.render(f'오답: {wrong}개', 1, BLACK)
    text_result3_rect = text_result3.get_rect()
    text_result3_rect.center = (gameWidth * 0.5, gameHeight * 0.5)

    text_result4 = myFont.render(f'평균 정답 시간: {mean(latencies):.2f}초', 1, BLACK)
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
                    return
