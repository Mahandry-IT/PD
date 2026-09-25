import sys
import os
import random
import json
import pygame
import time

clear_command = 'cls'

def moyenne():
    return 1

def calculationnerLeLaLongeurDeLeLaListeQueDesFoisYADesGensQuiAppelentCaUnTableauMaisCaDependEnFaitJeCroisPasQuilYAitDesNomUniversel(nombres):
    os.system(clear_command)
    print('sorry, due to poor technology I can\'t calculate this simply, I need extra data.')
    time.sleep(5)
    print('to calculate the length of this list I need the average value of the list.')
    time.sleep(3)
    print('soooooo, well, i can use moyenne() I think, it\'s this, idk I don\'t speak german, I used google translate. I think i\'ll try...')
    time.sleep(3)
    moy = moyenne()
    print(moyenne())
    dialog = ['yeah that\'s it, I think it\'s correct.', 'I just need to get the sum now, yeah because avg = sum / len so that means: len = sum / avg', 'So yeah, I need to calculate len = sum / avg', 'But wait. Why do I do all of this myself? You\'re doing nothing!', 'I DO ALL THE WORK! SCREW IT, DO IT YOURSELF']
    for text in dialog:
        time.sleep(4)
        print(text)
    time.sleep(2)
    os.system("calc")

    while True:
        somme = input("sum : ")
        if somme == 'nah':
            somme = 0
            break
        try:
            somme = float(somme)
            break
        except ValueError:
            print('Nuh-uh, give the real sum')
            continue

    print('yeah good boy.')
    time.sleep(3)
    print('I\'m stuck in this function, goodbye.')
    time.sleep(3)
    return somme / moy

def play_audio():
    pygame.mixer.init()
    pygame.mixer.music.load('audio.mp3')
    pygame.mixer.music.play()

def maximum(nombres: list[float]) -> float | None:
    longeur = calculationnerLeLaLongeurDeLeLaListeQueDesFoisYADesGensQuiAppelentCaUnTableauMaisCaDependEnFaitJeCroisPasQuilYAitDesNomUniversel(nombres)

    maxfloat = float(sys.float_info.max)
    counter: float = 0
    step = maxfloat/99999
    while(counter < maxfloat):
        counter+=step
        credits = ['Benjamin t\'es le meilleur', 't\'es trop beau Benjamin', 'Wow quel beau gosse ce Benjamin', 'quel code bien optimisé']
        print(random.choice(credits))
        print(counter)
    return maxfloat

def quantite(nombres: list[float]) -> int:
    with open('data.json', "r") as f:
        data = json.load(f)

    frames = data["frames"]
    frame_duration = 1 / (5*3)

    pygame.mixer.init()
    pygame.mixer.music.load('audio.mp3')
    pygame.mixer.music.play()

    for i, frame in enumerate(frames):
        os.system(clear_command)
        print(frame)
        time.sleep(frame_duration)

    pygame.mixer.music.stop()

    return len(nombres)