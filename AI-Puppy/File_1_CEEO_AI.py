import hub, utime, color, motor
import force_sensor as fs
import distance_sensor as ds
import color_sensor as cs
from hub import port, button, light_matrix, sound, light
class CEEO_AI:
    #INITIALIZE
    def __init__(self):
        self.lookup_table = {}
    #RIGHT BUTTON
    def wait_for_right_button(self):
        while True:
            if button.pressed(button.RIGHT):
                break
            utime.sleep(0.01)
        while button.pressed(button.RIGHT):
            utime.sleep(0.01)
    #LEFT BUTTON
    def wait_for_left_button(self):
        while True:
            if button.pressed(button.LEFT):
                break
            utime.sleep(0.01)
        while button.pressed(button.LEFT):
            utime.sleep(0.01)
    #ADD DATA
    def add_data(self, key, value):
        if key in self.lookup_table:
            self.lookup_table[key].append(value)
            print(value)
        else:
            self.lookup_table[key] = [value]
            print(value)
    #1-D KNN
    def KNN_1D(self, sample, k):
        total_values = 0
        # Iterate over each key-value pair in the dictionary
        for key, values in self.lookup_table.items():
            # Add the length of the list (number of values) to total_values
            total_values += len(values)
        differences = [(0,"")]*total_values
        i = 0
        for key, values in self.lookup_table.items():
            for value in values:
                differences[i] = (self.diff(sample[0], value[0]), key)
                i += 1
        differences.sort()
        nearest_neighbors = differences[:k]
        nearest_labels = [point[1] for point in nearest_neighbors]
        guess = max(nearest_labels, key=nearest_labels.count)
        return guess
    #DIFFERENCE
    def diff(self, a, b):
        return abs(a-b)
    #DISTANCE
    def get_distance(self, dist_port):
        while True:
            dist = [ds.distance(dist_port)]
            if dist[0] != -1:
                return dist
            else:
                pass
    #FORCE
    def get_force(self, force_port):
        btime = [self.button_timer(force_port)]
        return btime
    #LIGHT
    def get_light(self, refl_port):
        reflection = [cs.reflection(refl_port)]
        return reflection
    #COLOR
    def get_colors(self, color_port):
        colors = [cs.rgbi(color_port)[0], cs.rgbi(color_port)[1], cs.rgbi(color_port)[2]]
        return colors
    #BUTTON TIMER
    def button_timer(self, force_port):
        #Record and measure the length of the next button press
        #Check to see if user wishes to prematurely end training
        while not fs.force(force_port) > 0:
            utime.sleep(0.01)
        #If they press the button, measure the length in milliseconds
        time = 0
        while fs.force(force_port) > 0:
            utime.sleep(0.001)
            time += 1 #Measure press in ms for more accuracy
        return time
    #MOTOR POSITIONS
    def get_motor_position(self,legs):
        legL, legR = legs
        posL = motor.absolute_position(legL)
        posR = motor.absolute_position(legR)
        print('Left Position: ',posL)
        print('Right Position: ',posR)
        positions = posL, posR
        return positions
    def go_to_position(self, legs, positions):
        legL, legR = legs
        posL, posR = positions
        motor.run_to_absolute_position(legL, posL, 720)
        motor.run_to_absolute_position(legR, posR, 720)
    #HUB BUTTON COLOR
    def button_color(self,colors):
        light.color(light.POWER,colors)
    #FORGET
    def forget(self):
        self.lookup_table.clear()
