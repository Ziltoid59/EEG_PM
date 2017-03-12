import random, pygame, sys, os, time
import egi.simple as egi
from Tkinter import *
"""

NOTE:

1) While experiment is running (not paused) you can exit by pressing q

2) All NetStation code has been commented out. To connect to NetStation,
uncomment the relevent sections and modify as per your needs

Pro-Tip: NetStation will only accept 4 characters per string; no more, no less

"""

#Set our paramaters (these can be changed at will)

participant_number = 1 #Update for each participant
num_of_block_trials = 4
num_of_trials_per_block = 30
num_of_trials = num_of_block_trials * num_of_trials_per_block
num_of_repeats = 40 #Number of 1-backs classified as 'the same'
num_of_pm_cues = 12
num_of_blocks = 5 #Number of blocks shown on the screen during each trial

"""

NOTE:
      num_of_repeats / num_of_block_trials
                    AND
      num_of_pm_cues / num_of_block_trials

should both be whole numbers under floating point division


"""
 
"""These two vars tell us how big a section we want to dedicate to displaying
blocks"""
screen_width = 800
screen_height = 800

block_height = 100
block_width = 100

monitor_width = Tk().winfo_screenwidth()
monitor_height = Tk().winfo_screenheight()

"""Play with these values if the blocks are not in center area, though I don't
know why they wouldn't be"""
x_offset = (monitor_width/2) - (screen_width/2)
y_offset = (monitor_height/2) - (screen_height/2)

"""These two vars tell us how many block-sized sections we can make given the
space we have dedicated to displaying blocks"""
height_sections = (screen_height - block_height)/block_height
width_sections = (screen_width - block_width)/block_width

black = (0, 0, 0)
blue = (0, 0, 255)
red = (255, 0, 0)
green = (0, 255, 0)
white = (255, 255, 255)
grey = (128, 128, 128)
yellow = (255, 255, 0)

"""Set up our NetStation trigger codes"""
pre_mask_code = 'q'
post_mask_code = 'w'
response_code = 'e'
repeat_code = 'rp'
pm_code = 'pm'
non_repeat_code = 'nr'
block_trial_code = '' #leave empty as it gets assigned later

#Get coordinates for all our block configurations

x_locations = [] #All permissible locations along x-axis
y_locations = [] #All permissible locations along y-axis

counter = 0
top = 0
side = 0

while counter < height_sections:
    counter +=1
    top +=block_height
    y_locations.append(top + y_offset)

counter = 0

while counter < width_sections:
    counter +=1
    side +=block_width
    x_locations.append(side + x_offset)

def get_block_coordinates():
    y_axis_top = random.sample(y_locations, num_of_blocks)
    x_axis_left = random.sample(x_locations, num_of_blocks)

    coordinates = zip(x_axis_left, y_axis_top) #top left corner of block

    return coordinates

block_coordinates = dict()
trial = 0

while trial < num_of_trials: #Get coords for all trials
    trial +=1
    coordinates = get_block_coordinates()
    block_coordinates.update({trial: coordinates})

#Get trial indexes for repeats, non-repeats, and pm cues
    
repeats = []
start = 1
end = num_of_trials_per_block + 1
select = num_of_repeats/num_of_block_trials

def get_repeats(start, end, select):
    sub_list = random.sample(range(start, end), select)

    for i in sub_list:
        repeats.append(i)

    start += num_of_trials_per_block
    end += num_of_trials_per_block
    select = select

    if end <= num_of_trials + 1: get_repeats(start, end, select)
    
get_repeats(start, end, select)

repeats = sorted(repeats)

non_repeats = [i for i in range(1, num_of_trials + 1) if i not in repeats]

pm_cues = []
start = 1
end = num_of_trials_per_block + 1
select = num_of_pm_cues/num_of_block_trials

def get_pm(start, end, select):
    valid_indexes = [i for i in range(start, end) if i in non_repeats]
    sub_list = random.sample(valid_indexes, select)

    for i in sub_list:
        pm_cues.append(i)

    start +=  num_of_trials_per_block
    end += num_of_trials_per_block
    select = select

    if end <= num_of_trials + 1: get_pm(start, end, select)

get_pm(start, end, select)

pm_cues = sorted(pm_cues)

#Run experiment

"""ns = egi.Netstation()
ns.connect('10.0.0.1', 55513)
ns.BeginSession()
ns.sync()
ns.StartRecording()"""

pygame.init()
screen = pygame.display.set_mode((0,0), pygame.FULLSCREEN)
   
def start_warning():
    screen.fill((white))
    pygame.display.update()
    
    font = pygame.font.SysFont('monospace', 30)
    numbers = []
    
    for i in range(1,11):
        numbers.append(str(i))

    numbers = numbers[::-1]

    for i in numbers:
        num_to_show = font.render(i, 1, black)
        screen.blit(num_to_show, (monitor_width/2, monitor_height/2))
        pygame.display.update()
        time.sleep(1)
        screen.fill((white))

def pause():
    screen.fill((white))
    pygame.display.update()
    
    font = pygame.font.SysFont('monospace', 30)
    pause = font.render('Experiment Paused.', 1, black)
    pause_cords = pause.get_rect(center = (monitor_width/2, monitor_height/2))
    screen.blit(pause, pause_cords)
    pygame.display.update()

    time.sleep(50)

    start_warning() #Give 10s start warning

def present_blocks(trial, pm_colour, reg_colour):
    code = 0

    """Ensure our block_trial_code for NetStation reflects what block trial we
    are currently in"""
    if trial <= num_of_trials/num_of_block_trials:
        code +=1
        block_trial_code = str(code) #'z'
    elif (trial > num_of_trials/num_of_block_trials) \
                     and (trial <= 2*(num_of_trials/num_of_block_trials)):
        code +=2
        block_trial_code = str(code) #'x'
    elif (trial > 2*(num_of_trials/num_of_block_trials)) \
                     and (trial <= 3*(num_of_trials/num_of_block_trials)):
        code +=3
        block_trial_code = str(code) #'c'
    elif (trial > 3*(num_of_trials/num_of_block_trials)) \
                     and (trial <= 4*(num_of_trials/num_of_block_trials)):
        code +=4
        block_trial_code = str(code) #'v'

    #If there are more than 4 block trials, add an elif statement
    #for each additional block trial... I have simply run out of time
    #to automate it, so you get a bit of spaghetti
    
    screen.fill((black))

    """Draw fixation cross"""
    pygame.draw.line(screen, white, \
                     (monitor_width/2 - 25, monitor_height/2), \
                     (monitor_width/2 + 25, monitor_height/2), 1)

    pygame.draw.line(screen, white, \
                     (monitor_width/2, monitor_height/2 - 25), \
                     (monitor_width/2, monitor_height/2 + 25), 1)

    pygame.display.update()
    
    time.sleep(1)
    
    screen.fill((white))

    coordinates = block_coordinates[trial]
    
    different_inputs = [pygame.K_k]
    same_inputs = [pygame.K_j]
    pm_inputs = [pygame.K_a]
                
    def pre_mask(coordinates):
        colour = reg_colour
        block = 0

        """Draw all our blocks"""
        while block < num_of_blocks:
            pygame.draw.rect(screen, colour,
                    (coordinates[block][0], coordinates[block][1], 100, 100))

            block +=1

        pygame.display.update()

        """if trial in repeats:
              netstation_code = pre_mask_code + block_trial_code + repeat_code
              ns.send_event(netstation_code, table = {'stat': 'prem',\
                                   'cond': 'yrep', \
                                    'blck': 4*block_trial_code})
              time.sleep(0.1)
        elif trial in pm_cues:
              netstation_code = pre_mask_code + block_trial_code + pm_code
              ns.send_event(netstation_code, table = {'stat': 'prem',\
                                   'cond': 'pmpm', \
                                    'blck': 4*block_trial_code})
              time.sleep(0.1)
        else:
              netstation_code = pre_mask_code + block_trial_code + \
                                non_repeat_code
              ns.send_event(netstation_code, table = {'stat': 'prem',\
                                   'cond': 'nrep', \
                                    'blck': 4*block_trial_code})
              time.sleep(0.1)"""
              
    def post_mask(coordinates):
        if trial in pm_cues:
            colour = pm_colour
        else:
            colour = reg_colour
            
        if trial in repeats:
            pre_mask(coordinates) #show same config if indexed as a repeat
        else:
            x_shuffled = []
            y_shuffled = []

            for i in coordinates: #generate new coordinates for our blocks
                x_shuffled.append(i[0])
                y_shuffled.append(i[1])

                random.shuffle(x_shuffled)
                random.shuffle(y_shuffled)
                
                shuffled_coordinates = zip(x_shuffled, y_shuffled)

            block = 0

            """Draw all our blocks"""
            while block < num_of_blocks:
                pygame.draw.rect(screen, colour,
                                (shuffled_coordinates[block][0],
                                 shuffled_coordinates[block][1], 100, 100))

                block +=1

            pygame.display.update()

            """if trial in repeats:
                netstation_code = post_mask_code + block_trial_code + \
                                  repeat_code
                ns.send_event(netstation_code, table = {'stat': 'posm',\
                                   'cond': 'yrep', \
                                    'blck': 4*block_trial_code})
                time.sleep(0.1)
            elif trial in pm_cues:
                netstation_code = post_mask_code + block_trial_code + pm_code
                ns.send_event(netstation_code, table = {'stat': 'posm',\
                                   'cond': 'pmpm', \
                                    'blck': 4*block_trial_code})
                time.sleep(0.1)
            else:
                netstation_code = post_mask_code + block_trial_code + \
                                  non_repeat_code
                ns.send_event(netstation_code, table = {'stat': 'posm',\
                                   'cond': 'nrep', \
                                    'blck': 4*block_trial_code})
                time.sleep(0.1)"""

    pre_mask(coordinates) #Show our blocks

    time.sleep(2)

    screen.fill((grey)) #Show our mask
    pygame.display.update()

    time.sleep(1)
    
    screen.fill((white)) #Remove our mask
    pygame.display.update()
    
    post_mask(coordinates) #Show blocks again (either same or different)

    clear = False

    """Get participant responses"""
    while clear == False:
        for i in pygame.event.get():
            if i.type == pygame.KEYDOWN:
                if i.key in same_inputs:
                    """netstation_code = response_code + \
                                      block_trial_code +\
                                      repeat_code
                    ns.send_event(netstation_code, \
                                  table = {'stat': 'resp', \
                                           'ansr': 'same',\
                                           'blck': 4*block_trial_code})
                    time.sleep(0.1)"""
                    clear = True
                elif i.key in different_inputs:
                    """netstation_code = response_code + \
                                      block_trial_code +\
                                      non_repeat_code
                    ns.send_event(netstation_code, \
                                  table = {'stat': 'resp', \
                                           'ansr': 'diff',\
                                           'blck': 4*block_trial_code})
                    time.sleep(0.1)"""
                    clear = True
                elif i.key in pm_inputs:
                    """netstation_code = response_code + \
                                      block_trial_code +\
                                      pm_code
                    ns.send_event(netstation_code, \
                                  table = {'stat': 'resp', \
                                           'ansr': 'pmqu',\
                                           'blck': 4*block_trial_code})
                    time.sleep(0.1)"""
                    clear = True
                elif i.key == pygame.K_q:
                    pygame.quit()
                    exit()

start_warning() #10s countdown

trial = 0
while trial < 1*(num_of_trials/num_of_block_trials): #Show 1st block trial
    trial +=1
    pm_colour = blue #make sure to counterbalance colours each block trial 
    reg_colour = green
    present_blocks(trial, pm_colour, reg_colour)

pause() #Give participants a 50s break + a 10s warning

while trial < 2*(num_of_trials/num_of_block_trials): #show 2nd block trial
    trial +=1
    pm_colour = green #did you counterbalance us?
    reg_colour = blue
    present_blocks(trial, pm_colour, reg_colour)

pause()

while trial < 3*(num_of_trials/num_of_block_trials): #show 3rd block trial
    trial +=1
    pm_colour = blue #what about now?
    reg_colour = green
    present_blocks(trial, pm_colour, reg_colour)

pause()

while trial < 4*(num_of_trials/num_of_block_trials): #show 4th block trial
    trial +=1
    pm_colour = green #counterbalance, motherfuckers! -- Jackson, S.L.
    reg_colour = blue
    present_blocks(trial, pm_colour, reg_colour)

#If more than 4 block trials, add a while statement for each additional
#block trial as I have run out of time to automate it

screen.fill((white))
pygame.display.update()

"""ns.send_event('stop') #Let NetStation know we're done

time.sleep(2)

ns.StopRecording()
ns.EndSession()
ns.disconnect()"""
pygame.quit()
exit()

