# Rishi Nachnani
# Tuesday, January 9th, 2024

import pygame
import random
import sys

# changing working directory to the directory where the files are located, as to let the images be loaded properly.
import os

abspath = os.path.realpath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)
# -- -- -- - - -

# fixing pygame scaling issue with windows on some laptops. - https://stackoverflow.com/questions/44334594/how-to-avoid-scaling-pygame-window-when-make-ui-larger-is-used-in-windows 
if sys.platform == "win32":
    import ctypes
    ctypes.windll.user32.SetProcessDPIAware()
# ----

pygame.init()
SIZE = (800,700)
screen = pygame.display.set_mode(SIZE)

pygame.display.set_caption(f"CO\N{SUBSCRIPT TWO} Destroyer")
pygame.display.set_icon(pygame.image.load("images/icon.png"))

myClock = pygame.time.Clock()

# sounds
button_sound = pygame.mixer.Sound('./sounds/button.mp3')
oof_sound = pygame.mixer.Sound('./sounds/oof.mp3')
slice_sound = pygame.mixer.Sound('./sounds/slice.mp3')
bomb_sound = pygame.mixer.Sound('./sounds/bomb.mp3')

# colors
BLACK = (0, 0, 0)
GREY = (80,80,80)
RED = (255, 0, 0)
SKY = (135, 206, 235)
BLUE = (0, 0, 255)
WHITE = (255, 255, 255)
GOLD = (255, 215, 0)

# constants
CIRCLE_COLORS = [(172, 146, 235), (79, 193, 232), (160, 213, 104), (235, 206, 84), (237, 85, 100)]
FPS = 120

# variables needed
falling_rate_per_second = 2
falling_speed = 2
state = 'menu'
lives = 3
points = 0
previous_left = False
mouse_trace = []
fallingObjects = []
ctr = 0

#grass = pygame.image.load(r'C:\Users\rishi\Documents\coding\summative\images\bg.png')
bg = pygame.image.load('./images/background.jpg')
full_heart = pygame.image.load('./images/fullh.png')
empty_heart = pygame.image.load('./images/emptyh.png')
def drawGameBG():
    #screen.fill(SKY) old background
    #screen.blit(grass, (0,600))
    #screen.blit(grass, (284,600))
    #screen.blit(grass, (568,600))
    screen.fill(BLACK)
    screen.blit(bg, (0, 0)) 

def draw_hearts(): # draw the minecraft hearts in top left, displaying how many lives are left
    global lives

    for i in range(1,4):
        if i > lives:
            screen.blit(empty_heart, (575+(i*55), 10))
        else:
            screen.blit(full_heart, (575+(i*55), 10))

def draw_points():
    global points
    font = pygame.font.Font('./font.otf', 30)
    point_text = font.render('%i g' % points, True, WHITE)
    point_rect = point_text.get_rect()
    point_rect.x = 5
    point_rect.y = 5
    screen.blit(point_text, point_rect)

def drawFallingObjects():
    global ctr

    if ctr >= FPS/falling_rate_per_second:
        x = random.randint(80, 720)
        if random.randint(0,100) <= 15: # 15% chance for a bomb to be generated
            fallingObjects.append([x, 50, 60, BLACK, True, False]) # x, y, radius, color, bomb?, sliced? (obj var)
        else:
            radius = random.randint(30, 60)
            color = random.choice(CIRCLE_COLORS)
            fallingObjects.append([x, 50, radius, color, False, False]) # x, y, radius, color, bomb?, sliced? (obj var)
        ctr = 0

    for obj in fallingObjects:
        x, y, radius, color, bomb, sliced = obj
        if sliced: 
            pygame.draw.circle(screen, BLUE, (x, y), radius)
            if bomb:
                pygame.draw.circle(screen, RED, (x, y), radius, width=5)
        elif bomb: 
            pygame.draw.circle(screen, color, (x, y), radius)
            pygame.draw.circle(screen, WHITE, (x, y), radius, width=5)
            pygame.draw.circle(screen, GOLD, (x-20, y-20), 12)
        else:
            pygame.draw.circle(screen, color, (x, y), radius)
            pygame.draw.circle(screen, GREY, (x, y), radius, width=5)

        obj[1] += falling_speed # moving objects down (changing y value)

    ctr += 1

def checkSlice():
    # kinda obv, checking if something was sliced or not
    global previous_left, mouse_trace, fallingObjects, points, lives

    leftxy = False
    rightxy = False

    leftyx = False
    rightyx = False

    for obj in fallingObjects:
        x, y, radius, color, bomb, sliced = obj

        for trace in mouse_trace: # logic is kinda weird/complicated, basically checking if you sliced it
            # checking x and y coords and checking if the mouse actually went through

            if trace[1][0] < x-radius+10 and trace[1][1] > y-radius-10 and trace[1][1] < y+radius+10 and not leftxy:
                leftxy = True
            elif trace[1][0] > x+radius-10 and trace[1][1] > y-radius-10 and trace[1][1] < y+radius+10 and not rightxy:
                rightxy = True

            if trace[1][1] < y-radius+10 and trace[1][0] > x-radius-10 and trace[1][0] < x+radius+10 and not leftyx:
                leftyx = True
            elif trace[1][1] > y+radius-10 and trace[1][0] > x-radius-10 and trace[1][0] < x+radius+10 and not rightyx:
                rightyx = True
        
        if (leftxy and rightxy) or (leftyx and rightyx): #basically means if sliced
            if bomb: # bomb logic, removes life
                lives -= 1
                bomb_sound.play()
                bomb_sound.set_volume(0.75)
            else:
                points += 90-radius
                slice_sound.play()
                slice_sound.set_volume(0.75)
            obj[5] = True # setting ibject sliced to true
            mouse_trace = []
            previous_left = False
            return

        leftxy = False
        rightxy = False
        leftyx = False
        rightyx = False

    mouse_trace = []
    previous_left = False

def drawSliceTrace():
    # draws the line of your mouse slicing, so you can actually see the slice
    global previous_left, mouse_trace

    mouse_pos = pygame.mouse.get_pos()
    left, middle, right = pygame.mouse.get_pressed()

    if left:
        if previous_left:
            pygame.draw.line(screen, WHITE, previous_left, mouse_pos, width=5)
            mouse_trace.append([previous_left, mouse_pos])
        previous_left = mouse_pos
    elif not left and previous_left:
        checkSlice()
    
    for trace in mouse_trace:
        pygame.draw.line(screen, WHITE, trace[0], trace[1], width=5)

def checkMissedObjects():
    # checking if a object hits the ground and removes a live, or if obj was sliced and deletes it
    # bomb logic handled in checkSlice() function
    global lives, fallingObjects, state

    for index, [x, y, radius, color, bomb, sliced] in enumerate(fallingObjects):
        if y >= 580 and not sliced and not bomb:
            del fallingObjects[index]
            lives -= 1
            oof_sound.play()
        elif (sliced or bomb) and y >= 580:
            del fallingObjects[index]
    
    if lives <= 0:
        state = 'end'
        draw_hearts()
        draw_points()
        pygame.display.flip()
        pygame.time.wait(1000)
        #reset()

def checkFocused():
    # function to pause game if you accidentally close the window by going outside of it
    global state
    if not pygame.mouse.get_focused() and not pygame.key.get_focused(): # https://www.pygame.org/docs/ref/key.html#pygame.key.get_focused and https://www.pygame.org/docs/ref/mouse.html 
        state = 'paused'
        return True

def reset(retry=False):
    # resets all game variables, allowing the game to restart
    global falling_rate_per_second, falling_speed, lives, points, previous_left, mouse_trace, fallingObjects, ctr
    if not retry:
        falling_rate_per_second = 2.15
        falling_speed = 2.25
    lives = 3
    points = 0
    previous_left = False
    mouse_trace = []
    fallingObjects = []
    ctr = 0

def game():
    # pygame game run function
    if checkFocused():
        return # stops everything from moving
    drawGameBG()
    draw_hearts()
    draw_points()
    drawFallingObjects()
    drawSliceTrace()
    checkMissedObjects()
    pygame.display.flip()

ucolor = WHITE
rcolor = WHITE
mcolor = WHITE
qcolor = WHITE
def paused():
    global state, rcolor, mcolor, qcolor, ucolor

    mouse_pos = pygame.mouse.get_pos()
    leftpress, middlepress, rightpress = pygame.mouse.get_pressed()

    screen.fill(BLACK)

    button_unpause = pygame.Rect(200, 110, 400, 100)
    button_restart = pygame.Rect(200, 230, 400, 100)
    button_menu = pygame.Rect(200, 350, 400, 100)
    button_quit = pygame.Rect(200, 470, 400, 100)
 
    pygame.draw.rect(screen, ucolor, button_unpause, border_radius=30) # drawing rounded rects - https://www.geeksforgeeks.org/how-to-draw-a-rectangle-with-rounded-corner-in-pygame/ 
    pygame.draw.rect(screen, RED, button_unpause, width=5, border_radius=30) # ------------

    pygame.draw.rect(screen, rcolor, button_restart, border_radius=30) # drawing rounded rects - https://www.geeksforgeeks.org/how-to-draw-a-rectangle-with-rounded-corner-in-pygame/ 
    pygame.draw.rect(screen, RED, button_restart, width=5, border_radius=30) # ------------

    pygame.draw.rect(screen, mcolor, button_menu, border_radius=30) # drawing rounded rects - https://www.geeksforgeeks.org/how-to-draw-a-rectangle-with-rounded-corner-in-pygame/ 
    pygame.draw.rect(screen, RED, button_menu, width=5, border_radius=30) # ------------  

    pygame.draw.rect(screen, qcolor, button_quit, border_radius=30) # drawing rounded rects - https://www.geeksforgeeks.org/how-to-draw-a-rectangle-with-rounded-corner-in-pygame/ 
    pygame.draw.rect(screen, RED, button_quit, width=5, border_radius=30) # ------------

    boxfont = pygame.font.Font('./font.otf', 30)

    unpause = boxfont.render('UNPAUSE', False, BLACK)
    urect = unpause.get_rect()
    urect.center = (400, 160)

    restart = boxfont.render('RESTART', False, BLACK)
    rrect = restart.get_rect()
    rrect.center = (400, 280)

    menu = boxfont.render('MENU', False, BLACK)
    mrect = menu.get_rect()
    mrect.center = (400, 400)

    qui = boxfont.render('QUIT', False, BLACK)
    qrect = qui.get_rect()
    qrect.center = (400, 520)

    # changing button color when hovering (animation)

    if button_unpause.collidepoint(mouse_pos):
        ucolor = RED
    else:
        ucolor = WHITE

    if button_restart.collidepoint(mouse_pos):
        rcolor = RED
    else:
        rcolor = WHITE

    if button_menu.collidepoint(mouse_pos):
        mcolor = RED
    else:
        mcolor = WHITE

    if button_quit.collidepoint(mouse_pos):
        qcolor = RED
    else:
        qcolor = WHITE

    if button_unpause.collidepoint(mouse_pos) and leftpress:
        state = 'game'
        button_sound.play()
        button_sound.set_volume(0.75)
    elif button_restart.collidepoint(mouse_pos) and leftpress:
        reset(retry=True)
        state = 'game'
        button_sound.play()
        button_sound.set_volume(0.75)
    elif button_menu.collidepoint(mouse_pos) and leftpress:
        reset()
        state = 'menu'
        button_sound.play()
        button_sound.set_volume(0.75)
    elif button_quit.collidepoint(mouse_pos) and leftpress:
        button_sound.play()
        button_sound.set_volume(0.75)
        quit()

    screen.blit(unpause, urect)
    screen.blit(restart, rrect)
    screen.blit(menu, mrect)
    screen.blit(qui, qrect)

    pygame.display.flip()

scolor = WHITE
mcolor = WHITE
icolor = WHITE
def menu():
    global state
    global scolor, mcolor, icolor

    mouse_pos = pygame.mouse.get_pos()
    leftpress, middlepress, rightpress = pygame.mouse.get_pressed()

    screen.fill(BLACK)

    button_singleplayer = pygame.Rect(200, 230, 400, 100)
    button_multiplayer = pygame.Rect(200, 350, 400, 100)
    button_instructions = pygame.Rect(200, 470, 400, 100)
    
    pygame.draw.rect(screen, scolor, button_singleplayer, border_radius=30) # drawing rounded rects - https://www.geeksforgeeks.org/how-to-draw-a-rectangle-with-rounded-corner-in-pygame/ 
    pygame.draw.rect(screen, RED, button_singleplayer, width=5, border_radius=30)
    
    pygame.draw.rect(screen, mcolor, button_multiplayer, border_radius=30) # drawing rounded rects - https://www.geeksforgeeks.org/how-to-draw-a-rectangle-with-rounded-corner-in-pygame/ 
    pygame.draw.rect(screen, RED, button_multiplayer, width=5, border_radius=30)

    pygame.draw.rect(screen, icolor, button_instructions, border_radius=30) # drawing rounded rects - https://www.geeksforgeeks.org/how-to-draw-a-rectangle-with-rounded-corner-in-pygame/ 
    pygame.draw.rect(screen, RED, button_instructions, width=5, border_radius=30)

    # changing button color when hovering (animation)

    if button_singleplayer.collidepoint(mouse_pos):
        scolor = RED
    else:
        scolor = WHITE

    if button_multiplayer.collidepoint(mouse_pos):
        mcolor = RED
    else:
        mcolor = WHITE

    if button_instructions.collidepoint(mouse_pos):
        icolor = RED
    else:
        icolor = WHITE

    if button_singleplayer.collidepoint(mouse_pos) and leftpress:
        state = 'diff'
        button_sound.play()
        pygame.time.wait(500)
    elif button_instructions.collidepoint(mouse_pos) and leftpress:
        state = 'instructions'
        button_sound.play()

    font = pygame.font.Font('./font.otf', 60)
    title = font.render(f'CO2 Destroyer', True, WHITE) # font doesn't have subscript and ion wanan find anohter one
    titleRect = title.get_rect()
    titleRect.center = (400, 175)

    boxfont = pygame.font.Font('./font.otf', 30)

    singleplayer = boxfont.render('SINGLEPLAYER', False, BLACK)
    srect = singleplayer.get_rect()
    srect.center = (400, 280)

    multiplayer = boxfont.render('COMING SOON!', True, BLACK)
    mrect = multiplayer.get_rect()
    mrect.center = (400, 400)

    instructions = boxfont.render('INSTRUCTIONS', False, BLACK)
    irect = instructions.get_rect()
    irect.center = (400, 520)

    screen.blit(singleplayer, srect)
    screen.blit(multiplayer, mrect)
    screen.blit(instructions, irect)
    screen.blit(title, titleRect)
    
    pygame.display.flip()

ecolor = WHITE
ncolor = WHITE
hcolor = WHITE
acolor = WHITE
def difficulty_selection():
    global ecolor, ncolor, hcolor, acolor, state
    global falling_rate_per_second, falling_speed

    mouse_pos = pygame.mouse.get_pos()
    leftpress, middlepress, rightpress = pygame.mouse.get_pressed()

    screen.fill(BLACK)

    back = pygame.image.load('./images/backbutton.png')
    back_rect = pygame.Rect(19, 9, 70, 70)

    if back_rect.collidepoint(mouse_pos):
        pygame.draw.circle(screen, RED, (60, 50), 35)
    else:
        pygame.draw.circle(screen, WHITE, (60, 50), 35)
    
    screen.blit(back, back_rect)

    if back_rect.collidepoint(mouse_pos) and leftpress:
        state = 'menu'
        button_sound.play()
        button_sound.set_volume(0.75)

    font = pygame.font.Font('./font.otf', 45)
    title = font.render('DIFFICULTY SELECTION', True, WHITE)
    titleRect = title.get_rect()
    titleRect.center = (400, 175)
    screen.blit(title, titleRect)

    button_easy = pygame.Rect(200, 230, 400, 100)
    button_normal = pygame.Rect(200, 350, 400, 100)
    button_hard = pygame.Rect(200, 470, 400, 100)
    # button_advanced = pygame.Rect(200, 510, 400, 100)

    pygame.draw.rect(screen, ecolor, button_easy, border_radius=30) # drawing rounded rects - https://www.geeksforgeeks.org/how-to-draw-a-rectangle-with-rounded-corner-in-pygame/ 
    pygame.draw.rect(screen, RED, button_easy, width=5, border_radius=30)
    
    pygame.draw.rect(screen, ncolor, button_normal, border_radius=30) # drawing rounded rects - https://www.geeksforgeeks.org/how-to-draw-a-rectangle-with-rounded-corner-in-pygame/ 
    pygame.draw.rect(screen, RED, button_normal, width=5, border_radius=30)

    pygame.draw.rect(screen, hcolor, button_hard, border_radius=30) # drawing rounded rects - https://www.geeksforgeeks.org/how-to-draw-a-rectangle-with-rounded-corner-in-pygame/ 
    pygame.draw.rect(screen, RED, button_hard, width=5, border_radius=30)

    # pygame.draw.rect(screen, acolor, button_advanced, border_radius=30) # drawing rounded rects - https://www.geeksforgeeks.org/how-to-draw-a-rectangle-with-rounded-corner-in-pygame/ 
    # pygame.draw.rect(screen, RED, button_advanced, width=5, border_radius=30)

    boxfont = pygame.font.Font('./font.otf', 30)

    easy = boxfont.render('EASY', False, BLACK)
    erect = easy.get_rect()
    erect.center = (400, 280)

    normal = boxfont.render('NORMAL', False, BLACK)
    nrect = normal.get_rect()
    nrect.center = (400, 400)

    hard = boxfont.render('HARD', False, BLACK)
    hrect = hard.get_rect()
    hrect.center = (400, 520)

    # advanced = boxfont.render('ADVANCED', False, BLACK)
    # arect = advanced.get_rect()
    # arect.center = (400, 560)

    screen.blit(easy, erect)
    screen.blit(normal, nrect)
    screen.blit(hard, hrect)
    # screen.blit(advanced, arect)


    if button_easy.collidepoint(mouse_pos):
        ecolor = RED
    else:
        ecolor = WHITE

    if button_normal.collidepoint(mouse_pos):
        ncolor = RED
    else:
        ncolor = WHITE

    if button_hard.collidepoint(mouse_pos):
        hcolor = RED
    else:
        hcolor = WHITE

    # if button_advanced.collidepoint(mouse_pos):
    #     acolor = RED
    # else:
    #     acolor = WHITE
    
    if button_easy.collidepoint(mouse_pos) and leftpress:
        falling_rate_per_second = 1.5
        falling_speed = 1.5
        state = 'game'
        button_sound.play()
        button_sound.set_volume(0.75)
    elif button_normal.collidepoint(mouse_pos) and leftpress:
        falling_rate_per_second = 2.25
        falling_speed = 2.15
        state = 'game'
        button_sound.play()
        button_sound.set_volume(0.75)
    elif button_hard.collidepoint(mouse_pos) and leftpress:
        falling_rate_per_second = 3.5
        falling_speed = 3
        state = 'game'
        button_sound.play()
        button_sound.set_volume(0.75)

    pygame.display.flip()

rcolor = WHITE
mcolor = WHITE
qcolor = WHITE
def end_screen():
    global point
    global state
    global rcolor, mcolor, qcolor

    mouse_pos = pygame.mouse.get_pos()
    leftpress, middlepress, rightpress = pygame.mouse.get_pressed()

    screen.fill(BLACK)

    button_retry = pygame.Rect(200, 230, 400, 100)
    button_menu = pygame.Rect(200, 350, 400, 100)
    button_quit = pygame.Rect(200, 470, 400, 100)
    
    pygame.draw.rect(screen, rcolor, button_retry, border_radius=30) # drawing rounded rects - https://www.geeksforgeeks.org/how-to-draw-a-rectangle-with-rounded-corner-in-pygame/ 
    pygame.draw.rect(screen, RED, button_retry, width=5, border_radius=30)
    
    pygame.draw.rect(screen, mcolor, button_menu, border_radius=30) # drawing rounded rects - https://www.geeksforgeeks.org/how-to-draw-a-rectangle-with-rounded-corner-in-pygame/ 
    pygame.draw.rect(screen, RED, button_menu, width=5, border_radius=30)

    pygame.draw.rect(screen, qcolor, button_quit, border_radius=30) # drawing rounded rects - https://www.geeksforgeeks.org/how-to-draw-a-rectangle-with-rounded-corner-in-pygame/ 
    pygame.draw.rect(screen, RED, button_quit, width=5, border_radius=30)

    if button_retry.collidepoint(mouse_pos):
        rcolor = RED
    else:
        rcolor = WHITE

    if button_menu.collidepoint(mouse_pos):
        mcolor = RED
    else:
        mcolor = WHITE

    if button_quit.collidepoint(mouse_pos):
        qcolor = RED
    else:
        qcolor = WHITE

    if button_retry.collidepoint(mouse_pos) and leftpress:
        reset(retry=True)
        state = 'game'
        button_sound.play()
        button_sound.set_volume(0.75)
    elif button_menu.collidepoint(mouse_pos) and leftpress:
        reset()
        state = 'menu'
        button_sound.play()
        button_sound.set_volume(0.75)
    elif button_quit.collidepoint(mouse_pos) and leftpress:
        quit()
        button_sound.play()
        button_sound.set_volume(0.75)

    font = pygame.font.Font('./font.otf', 35)
    title = font.render('Carbon Destroyed: %i g' % points, True, WHITE)
    titleRect = title.get_rect()
    titleRect.center = (400, 175)

    boxfont = pygame.font.Font('./font.otf', 30)

    retry = boxfont.render('RETRY', False, BLACK)
    rrect = retry.get_rect()
    rrect.center = (400, 280)

    menu = boxfont.render('MENU', False, BLACK)
    mrect = menu.get_rect()
    mrect.center = (400, 400)

    qui = boxfont.render('QUIT', False, BLACK)
    qrect = qui.get_rect()
    qrect.center = (400, 520)

    screen.blit(retry, rrect)
    screen.blit(menu, mrect)
    screen.blit(qui, qrect)
    screen.blit(title, titleRect)
    
    pygame.display.flip()

def instructions():
    global state

    mouse_pos = pygame.mouse.get_pos()
    leftpress, middlepress, rightpress = pygame.mouse.get_pressed()

    screen.fill(BLACK)

    instructions = pygame.image.load('./images/instructions.jpg')
    screen.blit(instructions, (0,0))

    back = pygame.image.load('./images/backbutton.png')
    back_rect = pygame.Rect(19, 9, 70, 70)

    if back_rect.collidepoint(mouse_pos):
        pygame.draw.circle(screen, RED, (60, 50), 35)
    else:
        pygame.draw.circle(screen, WHITE, (60, 50), 35)
    
    screen.blit(back, back_rect)

    if back_rect.collidepoint(mouse_pos) and leftpress:
        state = 'menu'
        button_sound.play()
        button_sound.set_volume(0.75)

    pygame.display.flip()


# pygame game loop
while True:  
    # checking events, quit event allows for game to be closed by clicking the x icon provided by windows in the top right
    for evnt in pygame.event.get():
        if evnt.type == pygame.QUIT:
            quit()

    keys = pygame.key.get_pressed()
    if keys[pygame.K_ESCAPE] and state == 'game':
        state = 'paused'

    if state == 'game':
        game()
    elif state == 'paused':
        paused()
    elif state == 'menu':
        menu()
    elif state == 'diff':
        difficulty_selection()
    elif state == 'end':
        end_screen()
    elif state == 'instructions':
        instructions()

    # accomplishes 60 fps
    myClock.tick(FPS)
