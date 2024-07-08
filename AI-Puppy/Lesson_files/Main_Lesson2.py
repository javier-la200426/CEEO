import hub, utime, motor, color, CEEO_AI
from hub import port, button, light, sound
ai = CEEO_AI.CEEO_AI()

### SENSOR, MOTORS, AND PORTS HERE ###
d_sensor = port.A
legL = port.D
legR = port.C
motors = [legL,legR]

### PUPPY TRAINING MODE ###
train_color1 = color.AZURE
ai.button_color(train_color1)
print('PRINT_KEY:Now in training mode')
train_num = 5
print('PRINT_KEY:**IMPORTANT: Connect motors to ports C and D. Distance Sensor goes in Port A!!!)
print('PRINT_KEY:Move the legs of your puppy so that it is sitting!')
print('PRINT_KEY:When done press the right button!')
ai.wait_for_right_button()
sit_position = ai.get_motor_position(motors)
print('PRINT_KEY:Choose whether or not you want your puppy to sit when your hand is far or close.')
print('PRINT_KEY:Add %s data samples for sitting by putting your hand in front of the sensor and pressing the right button!' % (train_num))
print('PRINT_KEY:You should hear a beep when a data point is recorded.')
for i in range(train_num):
    ai.wait_for_right_button()
    ai.add_data('sit',ai.get_distance(d_sensor))
    sound.beep(220)
    utime.sleep(0.75)

train_color2 = color.BLUE
ai.button_color(train_color2)
sound.beep(440)

print('PRINT_KEY:Move the legs of your puppy so that it is standing!')
print('PRINT_KEY:When done press the right button!')
ai.wait_for_right_button()
stand_position = ai.get_motor_position(motors)
print('PRINT_KEY:Now add %s data samples for standing!' % (train_num))
for i in range(train_num):
    ai.wait_for_right_button()
    ai.add_data('stand',ai.get_distance(d_sensor))
    sound.beep(220)
    utime.sleep(0.75)
    
# PUPPY IS TRAINED

### PUPPY PLAY MODE ###
print('PRINT_KEY:Press right button to exit training mode and play with your puppy!')
ai.wait_for_right_button() # Now in play mode!
play_color = color.MAGENTA
ai.button_color(play_color)
sound.beep(880)
print('PRINT_KEY:Puppy is trained!')
K = 3
while not button.pressed(button.LEFT):
    guess_dist = ai.get_distance(d_sensor)
    guess = ai.KNN_1D(guess_dist, K)
    print('PRINT_KEY:%d mm distance is classified as %s' % (guess_dist, guess))
    if guess == 'sit': # Puppy sits or stands
        ai.go_to_position(motors,sit_position)
    elif guess == 'stand':
        ai.go_to_position(motors,stand_position)
    utime.sleep(0.1)
