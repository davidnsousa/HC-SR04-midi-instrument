from gpiozero import DistanceSensor, Button
from time import sleep
import rtmidi
from sf2utils.sf2parse import Sf2File
from ssd1306_module import Display
from rotary_module import RotaryEncoder
import subprocess
import warnings

warnings.filterwarnings("ignore")

# Pins

echo_pin = 17
triger_pin = 27
menu_button_pin = 22
mode_button_pin = 18

# Devices

menu_button = Button(menu_button_pin)
mode_button = Button(mode_button_pin)
display = Display()
sensor = DistanceSensor(echo_pin, triger_pin)
encoder = RotaryEncoder(9, 10)

# Sound variables and constants

global soundfont_path, fluidsynth_process, midi_out

soundfont_path = "/usr/share/sounds/sf2/FluidR3_GM.sf2"

with open(soundfont_path, 'rb') as sf2_file:
    sf2 = Sf2File(sf2_file)
sf2.presets.pop() # remove EOP
instrument = [preset.name for preset in sorted(sf2.presets, key=lambda x: (x.bank, x.preset))]

scale = {'Chromatic': set(range(12)),
         'Minor': {0, 2, 3, 5, 7, 8, 10},
         'Major': {0, 2, 4, 5, 7, 9, 11},
         'Dorian': {0, 2, 3, 5, 7, 9, 10}}

P = [['Octave: ', 3, list(range(10))],
     ['Scale: ', 0, list(scale.keys())],
     ['Instrument: ', 0, instrument],
     ['Volume: ', 50, list(range(127))]] 

S = -1

# MIDI to chromatic scale mapping for printing MIDI note's names in the display

note_names = [
    "C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"
]
max_midi_note = 127
midi_to_note = {}

for midi_note in range(max_midi_note):
    octave = midi_note // 12
    note_name = note_names[midi_note % 12]
    note_with_octave = f"{note_name}{octave}"
    midi_to_note[midi_note] = note_with_octave

# Functions

def execute_fluidsynth():
    
    global fluidsynth_process, midi_out

    # Execute Fluidsynth

    fluidsynth_process = subprocess.Popen("fluidsynth -a alsa -g 3 " + soundfont_path, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # Wait for FluidSynth to be ready and the midi port to become available

    fluidsynth_port = None
    while fluidsynth_port is None:
        output_names = rtmidi.MidiOut().get_ports()
        for name in output_names:
            if 'FLUID' in name:
                fluidsynth_port = name
                break
        sleep(1)

    # Connect to fluidsynth midi port

    fluidsynth_port = next((i for i, port_name in enumerate(rtmidi.MidiOut().get_ports()) if 'FLUID' in port_name), None)
    midi_out = rtmidi.MidiOut().open_port(fluidsynth_port)

def set_instrument(n):
    midi_out.send_message([0xC0, n])

def is_note_in_scale(note,s):
    scale_notes = list(scale.values())[s]
    offset = note % 12
    return offset in scale_notes

def play_note(ln):
    NOTE = round(sensor.distance*100+P[0][1]*12)
    if ln != NOTE and NOTE <= max_midi_note and is_note_in_scale(NOTE,P[1][1]):
        midi_out.send_message([0x80, ln, 0])
        midi_out.send_message([0x90, NOTE, P[3][1]])
        ln = NOTE
        display.clear()
        display.new_text_1st_half(midi_to_note[NOTE],14)
    return ln

def menu():
    global S
    S = (S + 1) % len(P)
    mode = P[S][1]
    display.clear()
    display.new_text_1st_half(P[S][0],14)
    display.new_text_2nd_half(str(P[S][2][mode]),14)

def change_mode():
    global P
    mode = P[S][1]
    mode = (mode + encoder.counter) % len(P[S][2])
    P[S][1] = mode
    display.clear()
    display.new_text_1st_half(P[S][0],14)
    display.new_text_2nd_half(str(P[S][2][mode]),14)
    if S == 2:
        set_instrument(P[2][1])


# MAIN

def main():
    try:
        
        execute_fluidsynth()      
        set_instrument(P[2][1])
        last_note = 0
        
        display.new_text_1st_half('Start playing!')
        
        while True:
            
            last_note = play_note(last_note)
            menu_button.when_pressed = menu
            encoder.when_rotated = change_mode
            sleep(0.1)
            
    except KeyboardInterrupt:
        fluidsynth_process.terminate()
        fluidsynth_process.wait()
        print("Fluidsynth terminated.")
    except:
        display.new_text_1st_half("ERROR!")
        display.new_text_2nd_half("Restarting...")
        display.clear()
        fluidsynth_process.terminate()
        fluidsynth_process.wait()
        main()

if __name__ == "__main__":
    main()