import hub, utime, motor, color, CEEO_AI
from hub import port, button, light, sound, light_matrix
ai = CEEO_AI.CEEO_AI()
f_sensor = port.F
train_num = 3
train_color1 = color.AZURE
ai.button_color(train_color1)
print('** TRAIN happy **')
print('Press right button to record a data point before using the touch sensor.')

for i in range(train_num):
    ai.wait_for_right_button()
    ai.add_data(light_matrix.IMAGE_HAPPY, ai.get_force(f_sensor))
    sound.beep(220)
    utime.sleep(0.75)

print('** TRAIN sad **')
print('Press right button to record a data point before using the touch sensor.')
train_color2 = color.BLUE
ai.button_color(train_color2)
sound.beep(440)

for i in range(train_num):
    ai.wait_for_right_button()
    ai.add_data(light_matrix.IMAGE_SAD, ai.get_force(f_sensor))
    sound.beep(220)
    utime.sleep(0.75)


print('Press right button to exit training mode!')
ai.wait_for_right_button()
print('How does your puppy feel?')
play_color = color.MAGENTA
ai.button_color(play_color)

sound.beep(880)
K = 3
while not button.pressed(button.LEFT):
    guess_time = ai.get_force(f_sensor)
    guess = ai.KNN_1D(guess_time, K)
    light_matrix.show_image(guess)
    utime.sleep(0.1)
    utime.sleep(0.1)




    
