from pygame import *
from random import randint
from time import time as timer 
font.init()
font1 = font.Font(None, 80)
win = font1.render('YOU WIN!', True, (255, 255, 255))
lose = font1.render('YOU LOSE!', True, (180, 0, 0))


font2 = font.SysFont('Arial', 36)


mixer.init()
mixer.music.load('space.ogg')
mixer.music.play()
fire_sound = mixer.Sound('fire.ogg')

img_back = "galaxy.jpg" 
img_bullet = "bullet.png" 
img_hero = "rocket.png" 
img_enemy = "ufo.png" 
img_ast = "asteroid.png" 


score = 0 
goal = 20 
lost = 0
max_lost = 10 
life = 3  


#? класс родитель для классов: Player,Enemy,Bullet.

class GameSprite(sprite.Sprite):

    def __init__(self, player_image, player_x, player_y, size_x, size_y, player_speed):
        
        sprite.Sprite.__init__(self)
        
        self.image = transform.scale(image.load(player_image), (size_x, size_y))
        self.speed = player_speed
        
        self.rect = self.image.get_rect()
        self.rect.x = player_x
        self.rect.y = player_y

    def reset(self):
        window.blit(self.image, (self.rect.x, self.rect.y))

#! класс Игрок
class Player(GameSprite):
    def update(self):
        keys = key.get_pressed()
        if keys[K_LEFT] and self.rect.x > 5:
            self.rect.x -= self.speed
        if keys[K_RIGHT] and self.rect.x < win_width - 80:
            self.rect.x += self.speed
        #? В этой части класса прописанно движение игрока по игровой карте

    def fire(self):
        bullet = Bullet(img_bullet, self.rect.centerx, self.rect.top, 15, 20, -15)
        bullets.add(bullet)
        #? В этой части класса прописаны пули, которыми игрок стреляет по агрессивным NPC

#! Класс Враг
class Enemy(GameSprite):
    def update(self):
        self.rect.y += self.speed
        global lost
        
        if self.rect.y > win_height:
            self.rect.x = randint(80, win_width - 80)
            self.rect.y = 0
            lost = lost + 1
#TODO Движение Агрессивного НПС по локации


#класс спрайта-пули 
#* ИГРОВОЙ КЛАСС ПУЛИ
class Bullet(GameSprite):
    #движение врага
    #** Движение пули и ее уничтожение при прикосновении с АНПС
    def update(self):
        self.rect.y += self.speed
        #исчезает, если дойдёт до края экрана
        if self.rect.y < 0:
            self.kill()
    
#создаём окошко
win_width = 700
win_height = 500
display.set_caption("Shooter")
window = display.set_mode((win_width, win_height))
background = transform.scale(image.load(img_back), (win_width, win_height))
#создаём спрайты
ship = Player(img_hero, 5, win_height - 100, 80, 100, 10)


#создание группы спрайтов-врагов
monsters = sprite.Group()
for i in range(1, 6):
  monster = Enemy(img_enemy, randint(80, win_width - 80), -40, 80, 50, randint(1, 5))
  monsters.add(monster)


#создание группы спрайтов-астероидов ()
asteroids = sprite.Group()
for i in range(1, 3):
   asteroid = Enemy(img_ast, randint(30, win_width - 30), -40, 80, 50, randint(1, 7))
   asteroids.add(asteroid)


bullets = sprite.Group()


finish = False
run = True


rel_time = False 


num_fire = 0         


while run:
    #событие нажатия на кнопку “Закрыть”
    for e in event.get():
        if e.type == QUIT:
            run = False
        #событие нажатия на пробел - спрайт стреляет
        elif e.type == KEYDOWN:
            if e.key == K_SPACE:
                    #проверяем, сколько выстрелов сделано и не происходит ли перезарядка
                    if num_fire < 5 and rel_time == False:
                        num_fire = num_fire + 1
                        fire_sound.play()
                        ship.fire()
                        
                    if num_fire  >= 5 and rel_time == False : #если игрок сделал 5 выстрелов
                        last_time = timer() #засекаем время, когда это произошло
                        rel_time = True #ставим флаг перезарядки
              
   #сама игра: действия спрайтов, проверка правил игры, перерисовка
    if not finish:
        #обновляем фон
        window.blit(background,(0,0))


        #производим движения спрайтов
        ship.update()
        monsters.update()
        asteroids.update()
        bullets.update()


        #обновляем их в новом местоположении при каждой итерации цикла
        ship.reset()
        monsters.draw(window)
        asteroids.draw(window)
        bullets.draw(window)


        #перезарядка
        if rel_time == True:
            now_time = timer() #считываем время
        
            if now_time - last_time < 3: #пока не прошло 3 секунды выводим информацию о перезарядке
                reload = font2.render('Wait, reload...', 1, (150, 0, 0))
                window.blit(reload, (260, 460))
            else:
                num_fire = 0   #обнуляем счётчик пуль
                rel_time = False #сбрасываем флаг перезарядки


       #проверка столкновения пули и монстров (и монстр, и пуля при касании исчезают)
        collides = sprite.groupcollide(monsters, bullets, True, True)
        for c in collides:
            #этот цикл повторится столько раз, сколько монстров подбито
            score = score + 1
            monster = Enemy(img_enemy, randint(80, win_width - 80), -40, 80, 50, randint(1, 5))
            monsters.add(monster)


        #если спрайт коснулся врага, уменьшает жизнь
        if sprite.spritecollide(ship, monsters, False) or sprite.spritecollide(ship, asteroids, False):
            sprite.spritecollide(ship, monsters, True)
            sprite.spritecollide(ship, asteroids, True)
            life = life -1


        #проигрыш
        if life == 0 or lost >= max_lost:
            finish = True #проиграли, ставим фон и больше не управляем спрайтами.
            window.blit(lose, (200, 200))




       #проверка выигрыша: сколько очков набрали?
        if score >= goal:
            finish = True
            window.blit(win, (200, 200))


        #пишем текст на экране
        text = font2.render("Счет: " + str(score), 1, (255, 255, 255))
        window.blit(text, (10, 20))


        text_lose = font2.render("Пропущено: " + str(lost), 1, (255, 255, 255))
        window.blit(text_lose, (10, 50))


       #задаём разный цвет в зависимости от количества жизней
        if life == 3:
            life_color = (0, 150, 0)
        if life == 2:
            life_color = (150, 150, 0)
        if life == 1:
            life_color = (150, 0, 0)


        text_life = font1.render(str(life), 1, life_color)
        window.blit(text_life, (650, 10))


        display.update()


   #бонус: автоматический перезапуск игры
    else:
        finish = False
        score = 0
        lost = 0
        num_fire = 0
        life = 3
        for b in bullets:
            b.kill()
        for m in monsters:
            m.kill()
        for a in asteroids:
            a.kill()   
        
        time.delay(3000)
        for i in range(1, 6):
            monster = Enemy(img_enemy, randint(80, win_width - 80), -40, 80, 50, randint(1, 5))
            monsters.add(monster)
        for i in range(1, 3):
            asteroid = Enemy(img_ast, randint(30, win_width - 30), -40, 80, 50, randint(1, 7))
            asteroids.add(asteroid)   


    time.delay(50)