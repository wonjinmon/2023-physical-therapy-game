# Elderly Recognition-Movement Training in Sensor-based Interactive Environment

from abc import ABC, abstractmethod
from enum import Enum
import sys
import os
import json
import pygame
from pygame.rect import Rect
from pygame.font import Font
from os import environ
from statistics import mean
environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
from serial import Serial
import time
import random
from portfinder import macAddfinder
from typing import Sequence


def set_font(font: Font, message: str, color: Sequence[int], center_coord: Sequence[float], anti_alias: bool = True) -> Rect:
    text = font.render(message, anti_alias, color)
    text_rect = text.get_rect()
    text_rect.center = center_coord
    return text_rect


class Button:
    def __init__(self, button_name, screen, x, y, image_path, scale):
        self.button_name = button_name

        image = pygame.image.load(image_path).convert_alpha()
        width = image.get_width()
        height = image.get_height()
        self.image = pygame.transform.scale(image, (int(width * scale), int(height * scale)))
        self.rect = image.get_rect()
        self.rect.topleft = (x, y)

        self.draw(screen)

    def draw(self, screen):
        screen.blit(self.image, (self.rect.x, self.rect.y))
        
    def click(self):
        action = False

        left_click, _, _ = pygame.mouse.get_pressed()

        pos = pygame.mouse.get_pos()

        if self.rect.collidepoint(pos) and left_click:
            action = True

        return action


class TagCheckWindow:
    pass


class MainWindowConfig(Enum):
    SCREEN_COLOR = (52, 68, 131)
    CAPTION = 'Main Menu'

    TMTA_IMG_PATH = 'test/images/TMTA.png'
    TMTA_BUTTON_X = 10
    TMTA_BUTTON_Y = 10
    TMTA_BUTTON_SCALE = 1

    TMTB_IMG_PATH = 'test/images/TMTB.png'
    TMTB_BUTTON_X = 10
    TMTB_BUTTON_Y = 310
    TMTB_BUTTON_SCALE = 1

    DIGITSPAN_IMG_PATH = 'test/images/DIGITSPAN.png'
    DIGITSPAN_BUTTON_X = 10
    DIGITSPAN_BUTTON_Y = 610
    DIGITSPAN_BUTTON_SCALE = 1

    MEMORYGAME_IMG_PATH = 'test/images/MEMORYGAME.png'
    MEMORYGAME_BUTTON_X = 900
    MEMORYGAME_BUTTON_Y = 10
    MEMORYGAME_BUTTON_SCALE = 1


class MainWindow:
    def __init__(self):
        self.config = MainWindowConfig        
        
    def update_screen(self, screen):
        pygame.display.set_caption(self.config.CAPTION.value)
        screen.fill(self.config.SCREEN_COLOR.value)

        self.tmta_button = Button(
            'tmta',
            screen,
            self.config.TMTA_BUTTON_X.value,
            self.config.TMTA_BUTTON_Y.value,
            self.config.TMTA_IMG_PATH.value,
            self.config.TMTA_BUTTON_SCALE.value,
        )
        self.tmtb_button = Button(
            'tmtb',
            screen,
            self.config.TMTB_BUTTON_X.value,
            self.config.TMTB_BUTTON_Y.value,
            self.config.TMTB_IMG_PATH.value,
            self.config.TMTB_BUTTON_SCALE.value,
        )
        self.digitspan_button = Button(
            'digitspan',
            screen,
            self.config.DIGITSPAN_BUTTON_X.value,
            self.config.DIGITSPAN_BUTTON_Y.value,
            self.config.DIGITSPAN_IMG_PATH.value,
            self.config.DIGITSPAN_BUTTON_SCALE.value,
        )
        self.memorygame_button = Button(
            'memorygame',
            screen,
            self.config.MEMORYGAME_BUTTON_X.value,
            self.config.MEMORYGAME_BUTTON_Y.value,
            self.config.MEMORYGAME_IMG_PATH.value,
            self.config.MEMORYGAME_BUTTON_SCALE.value,
        )

        pygame.display.update()


class Game(ABC):
    # 설정 -> 게임

    @abstractmethod
    def setup(self, screen, arduino):
        raise NotImplementedError

    @abstractmethod
    def game(self, screen, arduino):
        raise NotImplementedError


    def __call__(self, screen, arduino, rfid_map):
        
        self.setup(screen)
        self.game(screen, arduino, rfid_map)


class TMTA(Game):
    def __init__(self):
        super().__init__()
        
        # setup 폰트
        self.color = self.config.SCREEN_COLOR.value
        self.text = ""
        self.cursor = "_"
        self.font = pygame.font.Font("src/font/NanumGothic.ttf", 40)
        self.text_surface = self.font.render(self.text, True, self.color)
        self.text_rect = self.text_surface.get_rect()
        self.text_rect.center = (200, 150)

        self.cursor_surface = self.font.render(self.cursor, True, self.color)
        self.cursor_rect = self.cursor_surface.get_rect()
        self.cursor_rect.left = self.text_rect.right
        self.cursor_rect.centery = self.text_rect.centery

        # game 소리
        self.correctSoundEffect = pygame.mixer.Sound('src/sounds/correct.mp3')
        self.incorrectSoundEffect = pygame.mixer.Sound('src/sounds/incorrect.mp3')
        self.startSound = pygame.mixer.Sound('src/sounds/tmt/start.mp3')
        self.dingSound = pygame.mixer.Sound('src/sounds/tmt/ding.mp3')
        self.congratSound = pygame.mixer.Sound('src/sounds/congratulations.mp3')

        self.correctSoundEffect.set_volume(0.5)
        self.incorrectSoundEffect.set_volume(0.3)
        self.startSound.set_volume(0.3)
        self.dingSound.set_volume(0.2)
        self.congratSound.set_volume(0.5)

        # game 폰트
        self.myFont = pygame.font.Font("src/font/NanumGothic.ttf", 30)
        self.myFont_big = pygame.font.Font("src/font/NanumGothic.ttf", 300)
        self.myFont_medium = pygame.font.Font("src/font/NanumGothic.ttf", 100)

        # game 사진
        self.bgImage = pygame.image.load('src/MemoryGame/images/Background.png')
        self.bgImage = pygame.transform.scale(self.bgImage, (1600, 900))
        self.bgImageRect = self.bgImage.get_rect()
            
        
    def setup(self, screen):
        pygame.display.set_caption('TMT A')
        screen.fill((255,255,255))
        
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.unicode.isalnum() or event.unicode == " ":
                        self.text += event.unicode
                        self.text_surface = self.font.render(self.text, True, self.color)
                        text_rect = self.text_surface.get_rect()
                        text_rect.center = (200, 150)
                        self.cursor_rect.left = self.text_rect.right
                    elif event.key == pygame.K_BACKSPACE:
                        self.text = self.text[:-1]
                        self.text_surface = self.font.render(self.text, True, self.color)
                        text_rect = self.text_surface.get_rect()
                        text_rect.center = (200, 150)
                        self.cursor_rect.left = self.text_rect.right

                    elif event.key == pygame.K_TAB:
                        self.option = self.text
                        print(self.option)
                        running = False
            
            screen.blit(self.text_surface, self.text_rect)
            screen.blit(self.cursor_surface, self.cursor_rect)
            draw_text("Enter option number(2 ~ 30) and press TAB to start", self.font, (0,0,0), 550, 600, screen)
            pygame.display.update()


    def game(self, screen, arduino, rfid_map):
        pygame.display.set_caption('TMT-A')
        gameIcon = pygame.image.load('src/MemoryGame/images/card.png')
        pygame.display.set_icon(gameIcon)

        self.init_game(screen)

        time_show = random.randint(3, 5)
        pygame.time.wait(time_show * 1000)

        rfid_map = dict(list(rfid_map.items())[:int(self.option)])
        rfid_map_keys = list(rfid_map.keys())
        rfid_map_values = list(rfid_map.values())

        clock = pygame.time.Clock()
        buf = ""
        i = 0
        right = 0
        wrong = 0
        start = time.time()
        latency = time.time()
        latencies = []
        
        self.dingSound.play()

        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        running = False
            
            screen.blit(self.bgImage, self.bgImageRect)

            text_elapsed = self.myFont.render(f'진행 시간: {int(time.time()-start)}초', 1, self.color)
            text_elapsed_rect = text_elapsed.get_rect()
            text_elapsed_rect.center = (1600 * 0.2, 900 * 0.97)
            screen.blit(text_elapsed, text_elapsed_rect)

            text_wrong = self.myFont.render(f'오답: {wrong}번', 1, self.color)
            text_wrong_rect = text_wrong.get_rect()
            text_wrong_rect.center = (1600 * 0.8, 900 * 0.97)
            screen.blit(text_wrong, text_wrong_rect)

            text_progress = self.myFont.render(f'{i/len(rfid_map)*100:.2f}%', 1, self.color)
            text_progress_rect = text_progress.get_rect()
            text_progress_rect.center = (1600 * 0.5, 900 * 0.97)
            screen.blit(text_progress, text_progress_rect)

            text_tag = self.myFont_big.render(f'{i}', 1, self.color)
            text_tag_rect = text_tag.get_rect()
            text_tag_rect.center = (1600 * 0.5, 900 * 0.5)
            screen.blit(text_tag, text_tag_rect)

            text_tag_desc = self.myFont.render('태그해야 할 카드', 1, self.color)
            text_tag_desc_rect = text_tag_desc.get_rect()
            text_tag_desc_rect.center = (1600 * 0.5, 900 * 0.7)
            screen.blit(text_tag_desc, text_tag_desc_rect)

            try:
                text_tag_pre = self.myFont_medium.render(f'{rfid_map_values[i-1]}', 1, self.color)
                text_tag_pre_rect = text_tag_pre.get_rect()
                text_tag_pre_rect.center = (1600 * 0.25, 900 * 0.5)
                screen.blit(text_tag_pre, text_tag_pre_rect)
            except:
                pass

            try:
                text_tag_next = self.myFont_medium.render(f'{rfid_map_values[i+1]}', 1, self.color)
                text_tag_next_rect = text_tag_next.get_rect()
                text_tag_next_rect.center = (1600 * 0.75, 900 * 0.5)
                screen.blit(text_tag_next, text_tag_next_rect)
            except:
                pass

            if arduino.readable():
                try:
                    arduino_input = arduino.readline().decode().strip()
                except UnicodeDecodeError as ude:
                    arduino_input = arduino.readline('Windows-1252').decode().strip()

            if arduino_input:
                if arduino_input != buf:
                    buf = arduino_input
                    try:
                        input_index = rfid_map[arduino_input]        
                    except:
                        continue
                    
                    if input_index == i:
                        self.correctSoundEffect.play()
                        i += 1
                        right += 1
                        latency_temp = time.time()
                        latencies.append(latency_temp - latency)
                        latency = latency_temp
                        print('right')
                    else:
                        self.incorrectSoundEffect.play()
                        wrong += 1
                        print('wrong')

                    if right == len(rfid_map):
                        running = False
            
            pygame.display.update()
            clock.tick(60)
        
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        pygame.quit()

            end = time.time()

            self.congratSound.play()

            screen.blit(self.bgImage, self.bgImageRect)

            text_result1 = self.myFont.render(f'결과', 1, self.color)
            text_result1_rect = text_result1.get_rect()
            text_result1_rect.center = (1600 * 0.5, 900 * 0.1)
            screen.blit(text_result1, text_result1_rect)

            text_result2 = self.myFont.render(f'총 소요 시간: {int(end-start)}초', 1, self.color)
            text_result2_rect = text_result2.get_rect()
            text_result2_rect.center = (1600 * 0.5, 900 * 0.3)
            screen.blit(text_result2, text_result2_rect)

            text_result3 = self.myFont.render(f'오답: {wrong}개', 1, self.color)
            text_result3_rect = text_result3.get_rect()
            text_result3_rect.center = (1600 * 0.5, 900 * 0.5)
            screen.blit(text_result3, text_result3_rect)

            text_result4 = self.myFont.render(f'평균 반응 시간: {mean(latencies):.2f}초', 1, self.color)
            text_result4_rect = text_result4.get_rect()
            text_result4_rect.center = (1600 * 0.5, 900 * 0.7)
            screen.blit(text_result4, text_result4_rect)

            text_result5 = self.myFont.render(f'계속하려면 엔터 키를 누르세요...', 1, self.color)
            text_result5_rect = text_result5.get_rect()
            text_result5_rect.center = (1600 * 0.5, 900 * 0.9)
            screen.blit(text_result5, text_result5_rect)

            pygame.display.update()

    def init_game(self, screen):
        self.startSound.play()
        screen.blit(self.bgImage, self.bgImageRect)

        text_wait = self.myFont_medium.render(f'잠시 후 테스트를 시작합니다.', 1, self.color)
        text_wait_rect = text_wait.get_rect()
        text_wait_rect.center = (1600 * 0.5, 900 * 0.5)
        screen.blit(text_wait, text_wait_rect)

        pygame.display.update()


class TMTB(Game):
    def __init__(self):
        super().__init__()
        # setup 폰트
        self.color = (0,0,0)
        self.text = ""
        self.cursor = "_"
        self.font = pygame.font.Font("src/font/NanumGothic.ttf", 40)
        self.text_surface = self.font.render(self.text, True, self.color)
        self.text_rect = self.text_surface.get_rect()
        self.text_rect.center = (200, 150)

        self.cursor_surface = self.font.render(self.cursor, True, self.color)
        self.cursor_rect = self.cursor_surface.get_rect()
        self.cursor_rect.left = self.text_rect.right
        self.cursor_rect.centery = self.text_rect.centery
        
        # game 소리
        self.correctSoundEffect = pygame.mixer.Sound('src/sounds/correct.mp3')
        self.incorrectSoundEffect = pygame.mixer.Sound('src/sounds/incorrect.mp3')
        self.startSound = pygame.mixer.Sound('src/sounds/tmt/start.mp3')
        self.dingSound = pygame.mixer.Sound('src/sounds/tmt/ding.mp3')
        self.congratSound = pygame.mixer.Sound('src/sounds/congratulations.mp3')

        self.correctSoundEffect.set_volume(0.5)
        self.incorrectSoundEffect.set_volume(0.3)
        self.startSound.set_volume(0.3)
        self.dingSound.set_volume(0.2)
        self.congratSound.set_volume(0.5)

        # game 폰트
        self.myFont = pygame.font.Font("src/font/NanumGothic.ttf", 30)
        self.myFont_big = pygame.font.Font("src/font/NanumGothic.ttf", 300)
        self.myFont_medium = pygame.font.Font("src/font/NanumGothic.ttf", 100)

        # game 사진
        self.bgImage = pygame.image.load('src/MemoryGame/images/Background.png')
        self.bgImage = pygame.transform.scale(self.bgImage, (1600, 900))
        self.bgImageRect = self.bgImage.get_rect()


    def setup(self, screen):
        pygame.display.set_caption('TMT B')
        screen.fill((255,255,255))
        
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.unicode.isalnum() or event.unicode == " ":
                        self.text += event.unicode
                        self.text_surface = self.font.render(self.text, True, self.color)
                        text_rect = self.text_surface.get_rect()
                        text_rect.center = (200, 150)
                        self.cursor_rect.left = self.text_rect.right
                    elif event.key == pygame.K_BACKSPACE:
                        self.text = self.text[:-1]
                        self.text_surface = self.font.render(self.text, True, self.color)
                        text_rect = self.text_surface.get_rect()
                        text_rect.center = (200, 150)
                        self.cursor_rect.left = self.text_rect.right
                    elif event.key == pygame.K_TAB:
                        self.option = self.text
                        print(self.option)
                        running = False
            
            screen.blit(self.text_surface, self.text_rect)
            screen.blit(self.cursor_surface, self.cursor_rect)
            draw_text("Enter option number(2 ~ 30) and press TAB to start", self.font, (0,0,0), 550, 600, screen)
            pygame.display.update()


    def game(self, screen, arduino, rfid_map):
        pygame.display.set_caption('TMT')
        gameIcon = pygame.image.load(f'src/MemoryGame/images/card.png')
        pygame.display.set_icon(gameIcon)

        self.startSound.play()
        screen.blit(self.bgImage, self.bgImageRect)
        text_wait = self.myFont_medium.render(f'잠시 후 테스트를 시작합니다.', 1, self.color)
        text_wait_rect = text_wait.get_rect()
        text_wait_rect.center = (1600 * 0.5, 900 * 0.5)
        screen.blit(text_wait, text_wait_rect)
        pygame.display.update()
        time_show = random.randint(3, 5)
        pygame.time.wait(time_show * 1000)
        
        rfid_map = dict(list(rfid_map.items())[:int(self.option)])
        rfid_map_keys = list(rfid_map.keys())
        rfid_map_values = list(rfid_map.values())
        
        clock = pygame.time.Clock()
        buf = ""
        i = 0
        right = 0
        wrong = 0
        start = time.time()
        latency = time.time()
        latencies = []

        self.dingSound.play()
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
            
            screen.blit(self.bgImage, self.bgImageRect)
            text_elapsed = self.myFont.render(f'진행 시간: {int(time.time()-start)}초', 1, self.color)
            text_elapsed_rect = text_elapsed.get_rect()
            text_elapsed_rect.center = (1600 * 0.2, 900 * 0.97)
            text_wrong = self.myFont.render(f'오답: {wrong}번', 1, self.color)
            text_wrong_rect = text_wrong.get_rect()
            text_wrong_rect.center = (1600 * 0.8, 900 * 0.97)
            text_progress = self.myFont.render(f'{i/len(rfid_map)*100:.2f}%', 1, self.color)
            text_progress_rect = text_progress.get_rect()
            text_progress_rect.center = (1600 * 0.5, 900 * 0.97)
            screen.blit(text_elapsed, text_elapsed_rect)
            screen.blit(text_wrong, text_wrong_rect)
            screen.blit(text_progress, text_progress_rect)

            text_tag = self.myFont_big.render(f'{rfid_map_values[i]}', 1, self.color)
            text_tag_rect = text_tag.get_rect()
            text_tag_rect.center = (1600 * 0.5, 900 * 0.5)
            screen.blit(text_tag, text_tag_rect)
            text_tag_desc = self.myFont.render('태그해야 할 카드', 1, self.color)
            text_tag_desc_rect = text_tag_desc.get_rect()
            text_tag_desc_rect.center = (1600 * 0.5, 900 * 0.7)
            screen.blit(text_tag_desc, text_tag_desc_rect)

            try:
                text_tag_pre = self.myFont_medium.render(f'{rfid_map_values[i-1]}', 1, self.color)
                text_tag_pre_rect = text_tag_pre.get_rect()
                text_tag_pre_rect.center = (1600 * 0.25, 900 * 0.5)
                screen.blit(text_tag_pre, text_tag_pre_rect)
            except:
                pass

            try:
                text_tag_next = self.myFont_medium.render(f'{rfid_map_values[i+1]}', 1, self.color)
                text_tag_next_rect = text_tag_next.get_rect()
                text_tag_next_rect.center = (1600 * 0.75, 900 * 0.5)
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
                        self.correctSoundEffect.play()
                        i += 1
                        right += 1
                        latency_temp = time.time()
                        latencies.append(latency_temp - latency)
                        latency = latency_temp
                        print('right')
                    else:
                        self.incorrectSoundEffect.play()
                        wrong += 1
                        print('wrong')

                    if right == len(rfid_map):
                        running = False
            
            pygame.display.update()
            clock.tick(60)

        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        pygame.quit()

        end = time.time()

        self.congratSound.play()

        screen.blit(self.bgImage, self.bgImageRect)

        text_result1 = self.myFont.render(f'결과', 1, self.color)
        text_result1_rect = text_result1.get_rect()
        text_result1_rect.center = (1600 * 0.5, 900 * 0.1)
        screen.blit(text_result1, text_result1_rect)

        text_result2 = self.myFont.render(f'총 소요 시간: {int(end-start)}초', 1, self.color)
        text_result2_rect = text_result2.get_rect()
        text_result2_rect.center = (1600 * 0.5, 900 * 0.3)
        screen.blit(text_result2, text_result2_rect)

        text_result3 = self.myFont.render(f'오답: {wrong}개', 1, self.color)
        text_result3_rect = text_result3.get_rect()
        text_result3_rect.center = (1600 * 0.5, 900 * 0.5)
        screen.blit(text_result3, text_result3_rect)
        
        text_result4 = self.myFont.render(f'평균 반응 시간: {mean(latencies):.2f}초', 1, self.color)
        text_result4_rect = text_result4.get_rect()
        text_result4_rect.center = (1600 * 0.5, 900 * 0.7)
        screen.blit(text_result4, text_result4_rect)

        text_result5 = self.myFont.render(f'계속하려면 엔터 키를 누르세요...', 1, self.color)
        text_result5_rect = text_result5.get_rect()
        text_result5_rect.center = (1600 * 0.5, 900 * 0.9)
        screen.blit(text_result5, text_result5_rect)

        pygame.display.update()
        # time.sleep(5)


class DigitSpan(Game):
    def __init__(self):
        super().__init__()

        
        self.sounds = [
            "src/sounds/digit_span/zero.wav",
            "src/sounds/digit_span/one.wav",
            "src/sounds/digit_span/two.wav",
            "src/sounds/digit_span/three.wav",
            "src/sounds/digit_span/four.wav",
            "src/sounds/digit_span/five.wav",
            "src/sounds/digit_span/six.wav",
            "src/sounds/digit_span/seven.wav",
            "src/sounds/digit_span/eight.wav",
            "src/sounds/digit_span/nine.wav"]
        # setup 폰트
        self.color = (0,0,0)
        self.text = ""
        self.cursor = "_"
        self.font = pygame.font.Font("src/font/NanumGothic.ttf", 40)
        self.text_surface = self.font.render(self.text, True, self.color)
        self.text_rect = self.text_surface.get_rect()
        self.text_rect.center = (200, 150)

        self.cursor_surface = self.font.render(self.cursor, True, self.color)
        self.cursor_rect = self.cursor_surface.get_rect()
        self.cursor_rect.left = self.text_rect.right
        self.cursor_rect.centery = self.text_rect.centery
        
        # game 소리
        self.correctSoundEffect = pygame.mixer.Sound('src/sounds/correct.mp3')
        self.incorrectSoundEffect = pygame.mixer.Sound('src/sounds/incorrect.mp3')
        self.forwardSound = pygame.mixer.Sound('src/sounds/digit_span/forward.mp3')
        self.backwardSound = pygame.mixer.Sound('src/sounds/digit_span/backward.mp3')
        self.startSound = pygame.mixer.Sound('src/sounds/digit_span/start.mp3')

        self.correctSoundEffect.set_volume(0.5)
        self.incorrectSoundEffect.set_volume(0.3)
        self.forwardSound.set_volume(0.5)
        self.backwardSound.set_volume(0.5)
        self.startSound.set_volume(0.2)

        # game 폰트
        self.myFont = pygame.font.Font("src/font/NanumGothic.ttf", 30)
        self.myFont_big = pygame.font.Font("src/font/NanumGothic.ttf", 300)
        self.myFont_medium = pygame.font.Font("src/font/NanumGothic.ttf", 100)

        # game 사진
        self.bgImage = pygame.image.load('src/MemoryGame/images/Background.png')
        self.bgImage = pygame.transform.scale(self.bgImage, (1600, 900))
        self.bgImageRect = self.bgImage.get_rect()
        


    def setup(self, screen):
        pygame.display.set_caption('Digit Span')
        screen.fill((255, 255, 255))

        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.unicode.isalnum() or event.unicode == " ":
                        self.text += event.unicode
                        self.text_surface = self.font.render(self.text, True, self.color)
                        text_rect = self.text_surface.get_rect()
                        text_rect.center = (200, 150)
                        self.cursor_rect.left = self.text_rect.right
                    elif event.key == pygame.K_BACKSPACE:
                        self.text = self.text[:-1]
                        self.text_surface = self.font.render(self.text, True, self.color)
                        text_rect = self.text_surface.get_rect()
                        text_rect.center = (200, 150)
                        self.cursor_rect.left = self.text_rect.right
                    elif event.key == pygame.K_TAB:
                        self.option = self.text
                        print(self.option)
                        running = False
            
            screen.blit(self.text_surface, self.text_rect)
            screen.blit(self.cursor_surface, self.cursor_rect)
            draw_text("Enter option number(2 ~ 10) and press TAB to start", self.font, (0,0,0), 550, 600, screen)
            pygame.display.update()

    def game(self, screen, arduino, rfid_map):
            pygame.display.set_caption('Digit Span')
            idxList = list(rfid_map.values())
            assert int(self.option) <= len(idxList)
            randomChoices = random.sample(idxList, int(self.option))

            rfid_map_keys = list(rfid_map.keys())
            rfid_map_values = list(rfid_map.values())
            clock = pygame.time.Clock()

            arduino_input = None
            buf = ""
            i = 0
            right = 0
            wrong = 0

            self.forwardSound.play()

            screen.blit(self.bgImage, self.bgImageRect)
            text_wait = self.myFont_medium.render(f'정방향 태그를 시작합니다.', 1, self.color)
            text_wait_rect = text_wait.get_rect()
            text_wait_rect.center = (1600 * 0.5, 900 * 0.5)
            screen.blit(text_wait, text_wait_rect)
            pygame.display.update()

            time_show = random.randint(3, 5)
            pygame.time.wait(time_show * 1000)

            tmp = ""
            for digitStr in randomChoices:
                tmp += str(digitStr)
                screen.blit(self.bgImage, self.bgImageRect)
                text_wait = self.myFont_big.render(tmp, 1, self.color)
                text_wait_rect = text_wait.get_rect()
                text_wait_rect.center = (1600 * 0.5, 900 * 0.5)
                screen.blit(text_wait, text_wait_rect)
                pygame.display.update()
                soundDir = self.sounds[digitStr]
                digitSound = pygame.mixer.Sound(soundDir)
                digitSound.play()
                time.sleep(1)
                digitSound.stop()
            
            forward_inputs = []
            self.startSound.play()
            start = time.time()  
            cnt = 0

            running = True
            while running:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                
                screen.blit(self.bgImage, self.bgImageRect)
                text_elapsed = self.myFont.render(f'진행 시간: {int(time.time()-start)}초', 1, self.color)
                text_elapsed_rect = text_elapsed.get_rect()
                text_elapsed_rect.center = (1600 * 0.2, 900 * 0.97)
                screen.blit(text_elapsed, text_elapsed_rect)

                text_wrong = self.myFont.render(f'오답: {wrong}번', 1, self.color)
                text_wrong_rect = text_wrong.get_rect()
                text_wrong_rect.center = (1600 * 0.8, 900 * 0.97)
                screen.blit(text_wrong, text_wrong_rect)

                text_progress = self.myFont.render(f'{i/len(randomChoices)*100:.2f}%', 1, self.color)
                text_progress_rect = text_progress.get_rect()
                text_progress_rect.center = (1600 * 0.5, 900 * 0.97)
                screen.blit(text_progress, text_progress_rect)

                text_tag = self.myFont_big.render(f'{randomChoices[i]}', 1, self.color)
                text_tag_rect = text_tag.get_rect()
                text_tag_rect.center = (1600 * 0.5, 900 * 0.5)
                screen.blit(text_tag, text_tag_rect)

                text_tag_desc = self.myFont.render('태그해야 할 카드', 1, self.color)
                text_tag_desc_rect = text_tag_desc.get_rect()
                text_tag_desc_rect.center = (1600 * 0.5, 900 * 0.7)
                screen.blit(text_tag_desc, text_tag_desc_rect)

                try:
                    text_tag_pre = self.myFont_medium.render(f'{randomChoices[i-1]}', 1, self.color)
                    text_tag_pre_rect = text_tag_pre.get_rect()
                    text_tag_pre_rect.center = (1600 * 0.25, 900 * 0.5)
                    screen.blit(text_tag_pre, text_tag_pre_rect)
                except:
                    pass

                try:
                    text_tag_next = self.myFont_medium.render(f'{randomChoices[i+1]}', 1, self.color)
                    text_tag_next_rect = text_tag_next.get_rect()
                    text_tag_next_rect.center = (1600 * 0.75, 900 * 0.5)
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
                            self.correctSoundEffect.play()
                            right += 1
                            print('right')
                        else:
                            self.incorrectSoundEffect.play()
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
                                self.correctSoundEffect.play()
                                right += 1
                                print('right')
                            else:
                                self.incorrectSoundEffect.play()
                                wrong += 1
                                print('wrong')
                            cnt = 0
                            i += 1
                        else:
                            cnt += 1

                    if len(forward_inputs) == len(randomChoices):
                        running = False

                pygame.display.update()
                clock.tick(60)

            forward_time = time.time()-start
            forward_right = right
# 역방향
            buf = ""
            arduino_input = None
            running = True
            i = 0
            right = 0
            wrong = 0
            backward_inputs = []
            randomChoices = list(reversed(randomChoices))
            self.backwardSound.play()
            screen.blit(self.bgImage, self.bgImageRect)

            text_wait = self.myFont_medium.render(f'잠시 후 역방향 태그를 시작합니다.', 1, self.color)
            text_wait_rect = text_wait.get_rect()
            text_wait_rect.center = (1600 * 0.5, 900 * 0.5)
            screen.blit(text_wait, text_wait_rect)

            pygame.display.update()
            time_show = random.randint(5, 7)
            pygame.time.wait(time_show * 1000)

            self.startSound.play()
            start = time.time()
            while running:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                
                screen.blit(self.bgImage, self.bgImageRect)
                text_elapsed = self.myFont.render(f'진행 시간: {int(time.time()-start)}초', 1, self.color)
                text_elapsed_rect = text_elapsed.get_rect()
                text_elapsed_rect.center = (1600 * 0.2, 900 * 0.97)
                screen.blit(text_elapsed, text_elapsed_rect)

                text_wrong = self.myFont.render(f'오답: {wrong}번', 1, self.color)
                text_wrong_rect = text_wrong.get_rect()
                text_wrong_rect.center = (1600 * 0.8, 900 * 0.97)
                screen.blit(text_wrong, text_wrong_rect)

                text_progress = self.myFont.render(f'{i/len(randomChoices)*100:.2f}%', 1, self.color)
                text_progress_rect = text_progress.get_rect()
                text_progress_rect.center = (1600 * 0.5, 900 * 0.97)
                screen.blit(text_progress, text_progress_rect)

                text_tag = self.myFont_big.render(f'{randomChoices[i]}', 1, self.color)
                text_tag_rect = text_tag.get_rect()
                text_tag_rect.center = (1600 * 0.5, 900 * 0.5)
                screen.blit(text_tag, text_tag_rect)

                text_tag_desc = self.myFont.render('태그해야 할 카드', 1, self.color)
                text_tag_desc_rect = text_tag_desc.get_rect()
                text_tag_desc_rect.center = (1600 * 0.5, 900 * 0.7)
                screen.blit(text_tag_desc, text_tag_desc_rect)

                try:
                    text_tag_pre = self.myFont_medium.render(f'{randomChoices[i-1]}', 1, self.color)
                    text_tag_pre_rect = text_tag_pre.get_rect()
                    text_tag_pre_rect.center = (1600 * 0.25, 900 * 0.5)
                    screen.blit(text_tag_pre, text_tag_pre_rect)
                except:
                    pass

                try:
                    text_tag_next = self.myFont_medium.render(f'{randomChoices[i+1]}', 1, self.color)
                    text_tag_next_rect = text_tag_next.get_rect()
                    text_tag_next_rect.center = (1600 * 0.75, 900 * 0.5)
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
                            self.correctSoundEffect.play()
                            right += 1
                            print('right')
                        else:
                            self.incorrectSoundEffect.play()
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
                                self.correctSoundEffect.play()
                                right += 1
                                print('right')
                            else:
                                self.incorrectSoundEffect.play()
                                wrong += 1
                                print('wrong')
                            cnt = 0
                            i += 1
                        else:
                            cnt += 1
                    if len(backward_inputs) == len(randomChoices):
                        running = False
                pygame.display.update()
                clock.tick(60)
            
            running = True
            while running:
                for event in pygame.event.get():
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_RETURN:
                            pygame.quit()

            backward_time = time.time()-start
            backward_right = right

            screen.blit(self.bgImage, self.bgImageRect)

            text_result1 = self.myFont.render(f'결과', 1, self.color)
            text_result1_rect = text_result1.get_rect()
            text_result1_rect.center = (1600 * 0.5, 900 * 0.1)
            screen.blit(text_result1, text_result1_rect)

            text_result2 = self.myFont.render(f'총 소요 시간: 정방향: {forward_time:.2f}초,\t역방향: {backward_time:.2f}초', 1, self.color)
            text_result2_rect = text_result2.get_rect()
            text_result2_rect.center = (1600 * 0.5, 900 * 0.3)
            screen.blit(text_result2, text_result2_rect)

            text_result3 = self.myFont.render(f'정방향 정답: {forward_right}개,\t역방향 정답: {backward_right}개', 1, self.color)
            text_result3_rect = text_result3.get_rect()
            text_result3_rect.center = (1600 * 0.5, 900 * 0.5)
            screen.blit(text_result3, text_result3_rect)

            text_result5 = self.myFont.render(f'계속하려면 엔터 키를 누르세요...', 1, self.color)
            text_result5_rect = text_result5.get_rect()
            text_result5_rect.center = (1600 * 0.5, 900 * 0.9)
            screen.blit(text_result5, text_result5_rect)          

            pygame.display.update()
            # time.sleep(5)


class MemoryGame(Game):
    def __init__(self):
        super().__init__()
        # setup 폰트
        self.color = (0,0,0)
        self.text = ""
        self.cursor = "_"
        self.font = pygame.font.Font("src/font/NanumGothic.ttf", 40)
        self.text_surface = self.font.render(self.text, True, self.color)
        self.text_rect = self.text_surface.get_rect()
        self.text_rect.center = (200, 150)

        self.cursor_surface = self.font.render(self.cursor, True, self.color)
        self.cursor_rect = self.cursor_surface.get_rect()
        self.cursor_rect.left = self.text_rect.right
        self.cursor_rect.centery = self.text_rect.centery

        # 소리
        self.correctSoundEffect = pygame.mixer.Sound('src/sounds/correct.mp3')
        self.incorrectSoundEffect = pygame.mixer.Sound('src/sounds/incorrect.mp3')
        self.congratSound = pygame.mixer.Sound('src/sounds/congratulations.mp3')
        self.correctSoundEffect.set_volume(0.5)
        self.incorrectSoundEffect.set_volume(0.3)
        self.congratSound.set_volume(0.5)

        # 카드
        self.picSize = 128
        self.padding = 10
        self.bgImage = pygame.image.load('src/MemoryGame/images/Background.png')
        self.bgImage = pygame.transform.scale(self.bgImage, (1600, 900))
        self.bgImageRect = self.bgImage.get_rect()

        self.cardImage = pygame.image.load('src/MemoryGame/images/card.png')
        self.cardImage = pygame.transform.scale(self.cardImage, (self.picSize, self.picSize))
        

        self.myFont = pygame.font.Font("src/font/NanumGothic.ttf", 30)

        self.imageset = None


    def setup(self, screen):
        self.setup1(screen)
        self.setup2(screen)

    #카드의 종류 설정
    def setup1(self, screen):
        pygame.display.set_caption('Memory Game setting 1')
        screen.fill((52, 68, 131))
        
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        running = False

            self.animal_button = Button('animal', screen, 200, 250, 'src/MemoryGame/images/animals/pig.png', 0.8)
            self.fruits_button = Button('fruit', screen, 900, 250, 'src/MemoryGame/images/fruits/apple.png', 0.8)
            pygame.display.update()

            if self.animal_button.click():
                self.imageset = 'animals'
                print('animalll')
                running = False
                
            if self.fruits_button.click():
                self.imageset = 'fruits'
                print('fruitss')
                running = False
                

        return running
            

    # 카드의 행렬 설정
    def setup2(self, screen):
            pygame.display.set_caption('Memory Game setting 2')
            screen.fill((255, 255, 255))
            running = True
            while running:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                    elif event.type == pygame.KEYDOWN:
                        if event.unicode.isalnum() or event.unicode == " ":
                            self.text += event.unicode
                            self.text_surface = self.font.render(self.text, True, self.color)
                            text_rect = self.text_surface.get_rect()
                            text_rect.center = (200, 150)
                            self.cursor_rect.left = self.text_rect.right
                        elif event.key == pygame.K_BACKSPACE:
                            self.text = self.text[:-1]
                            self.text_surface = self.font.render(self.text, True, self.color)
                            text_rect = self.text_surface.get_rect()
                            text_rect.center = (200, 150)
                            self.cursor_rect.left = self.text_rect.right
                        elif event.key == pygame.K_TAB:
                            self.option = self.text
                            print(self.option)
                            running = False
                
                screen.blit(self.text_surface, self.text_rect)
                screen.blit(self.cursor_surface, self.cursor_rect)
                draw_text("Enter option number 행:(2 ~ 6), 열:(2 ~ 6) and press TAB to start", self.font, (0,0,0), 550, 600, screen)
                
                pygame.display.update()

            self.gameColumns = int(self.option[0])
            self.gameRows = int(self.option[1]) 


    def game(self, screen, arduino, rfid_map):
                imageset = self.imageset
                gameColumns = self.gameColumns
                gameRows = self.gameRows
                pygame.display.set_caption('Memory Game')
                gameIcon = pygame.image.load(f'src/MemoryGame/images/card.png')
                pygame.display.set_icon(gameIcon)

                leftMargin = (1600 - ((self.picSize + self.padding) * gameColumns)) // 2
                rightMargin = leftMargin
                topMargin = (900 - ((self.picSize + self.padding) * gameRows)) // 2
                bottomMargin = topMargin
                selection1 = None
                selection2 = None
                right = 0
                wrong = 0

                memoryPictures = []
                for item in os.listdir(f'src/MemoryGame/images/{imageset}/'):
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
                    picture = pygame.image.load(f'src/MemoryGame/images/{imageset}/{item}.png')
                    picture = pygame.transform.scale(picture, (self.picSize, self.picSize))
                    memPics.append(picture)
                    pictureRect = picture.get_rect()
                    memPicsRect.append(pictureRect)

                    selectedSound = pygame.mixer.Sound(f'src/sounds/{imageset}/{item}.mp3')
                    selectedSound.set_volume(0.5)
                    sounds.append(selectedSound)

                for j in range(gameRows):
                    for k in range(gameColumns):
                        i = j * gameColumns + k
                        memPicsRect[i][0] = leftMargin + ((self.picSize + self.padding) * k)
                        memPicsRect[i][1] = topMargin + ((self.picSize + self.padding) * j)
                        hiddenImages.append(False)

                screen.blit(self.bgImage, self.bgImageRect)
                for i in range(gameColumns*gameRows):
                    screen.blit(memPics[i], memPicsRect[i])
                pygame.display.update()

                time_show = random.randint(3, 10)
                pygame.time.wait(time_show * 1000)

                screen.blit(self.bgImage, self.bgImageRect)
                for i in range(gameColumns*gameRows):
                    screen.blit(self.cardImage, memPicsRect[i])

                pygame.display.update()

                buf = ''
                latency = time.time()
                latencies = []
                start = time.time()
                running = True
                while running:
                    for event in pygame.event.get():
                        if event.type == pygame.KEYDOWN:
                            if event.key == pygame.K_q:
                                running = False
                    # Load background image
                    screen.blit(self.bgImage, self.bgImageRect)

                    text_elapsed = self.myFont.render(f'진행 시간: {int(time.time()-start)}초', 1, self.color)
                    text_elapsed_rect = text_elapsed.get_rect()
                    text_elapsed_rect.center = (1600 * 0.2, 900 * 0.97)
                    screen.blit(text_elapsed, text_elapsed_rect)

                    text_wrong = self.myFont.render(f'오답: {wrong}번', 1, self.color)
                    text_wrong_rect = text_wrong.get_rect()
                    text_wrong_rect.center = (1600 * 0.8, 900 * 0.97)
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
                            running = False
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
                            screen.blit(self.cardImage, memPicsRect[i])


                    pygame.display.update()

                    if selection1 != None and selection2 != None:
                        if memoryPictures[selection1] == memoryPictures[selection2]:
                            selection1, selection2 = None, None
                            right += 1
                            self.correctSoundEffect.play()
                            latency_temp = time.time()
                            latencies.append(latency_temp - latency)
                            latency = latency_temp
                            
                        else:
                            self.incorrectSoundEffect.play()
                            pygame.time.wait(500)
                            hiddenImages[selection1] = False
                            hiddenImages[selection2] = False
                            selection1, selection2 = None, None
                            wrong += 1

                    win = 1
                    for number in range(len(hiddenImages)):
                        win *= hiddenImages[number]

                    if win == 1:
                        running = False
                    
                    pygame.display.update()

                running = True
                while running:
                    for event in pygame.event.get():
                        if event.type == pygame.KEYDOWN:
                            if event.key == pygame.K_RETURN:
                                pygame.quit()
    
                    
                end = time.time()

                self.congratSound.play()

                screen.blit(self.bgImage, self.bgImageRect)

                text_result1 = self.myFont.render(f'결과', 1, self.color)
                text_result1_rect = text_result1.get_rect()
                text_result1_rect.center = (1600 * 0.5, 900 * 0.1)
                screen.blit(text_result1, text_result1_rect)

                text_result2 = self.myFont.render(f'총 소요 시간: {(end-start):.2f}초', 1, self.color)
                text_result2_rect = text_result2.get_rect()
                text_result2_rect.center = (1600 * 0.5, 900 * 0.3)
                screen.blit(text_result2, text_result2_rect)

                text_result3 = self.myFont.render(f'오답: {wrong}개', 1, self.color)
                text_result3_rect = text_result3.get_rect()
                text_result3_rect.center = (1600 * 0.5, 900 * 0.5)
                screen.blit(text_result3, text_result3_rect)

                text_result4 = self.myFont.render(f'평균 정답 시간: {mean(latencies):.2f}초', 1, self.color)
                text_result4_rect = text_result4.get_rect()
                text_result4_rect.center = (1600 * 0.5, 900 * 0.7)
                screen.blit(text_result4, text_result4_rect)

                text_result5 = self.myFont.render(f'계속하려면 엔터 키를 누르세요...', 1, self.color)
                text_result5_rect = text_result5.get_rect()
                text_result5_rect.center = (1600 * 0.5, 900 * 0.9)
                screen.blit(text_result5, text_result5_rect)

                pygame.display.update()
                # time.sleep(5)
                
                
                    




def draw_text(text, font, text_col, x, y, screen):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))



def main():
    pygame.init()
    
    screen_width = 1600
    screen_height = 900
    screen = pygame.display.set_mode((screen_width, screen_height))

    with open("./CFG_show.json", "r", encoding='UTF-8') as cfg:
        cfg = json.load(cfg)

    RFID_TMTA = cfg['TMTA']
    RFID_TMTB = cfg['TMTB']
    RFID_DIGITSPAN = cfg['DIGITSPAN']
    RFID_MEMORYGAME = cfg['MemoryGame']
    RFID_BTMACID = cfg['BTMACID']

    hc06_port = macAddfinder(macAddress=RFID_BTMACID)

    arduino = Serial(port=hc06_port, baudrate=9600, timeout=0.5)

    main_window = MainWindow()
    tmta = TMTA()
    tmtb = TMTB()
    digitspan = DigitSpan()
    memorygame = MemoryGame()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        main_window.update_screen(screen)

        if main_window.tmta_button.click():
            tmta(screen, arduino, rfid_map = RFID_TMTA)
            
        if main_window.tmtb_button.click():
            tmtb(screen, arduino, rfid_map = RFID_TMTB)
        if main_window.digitspan_button.click():
            digitspan(screen, arduino, rfid_map = RFID_DIGITSPAN)
        if main_window.memorygame_button.click():
            memorygame(screen, arduino, rfid_map = RFID_MEMORYGAME)
            
        
    pygame.quit()


if __name__ == '__main__':
    main()