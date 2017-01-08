#!/usr/bin/env python

from scipy.io import wavfile
import argparse
import numpy as np
import pygame
import sys
import warnings
#import RPi.GPIO as GPIO

# need 10 digitals to be used as keys:
# L0 is left pinky, R4 is right thumb etc
#
#   Finger |  Pin  | GPIOnum
#     L0   |   11  |   17
#     L1   |   13  |   27
#     L2   |   15  |   22
#     L3   |   12  |   18 
#     L4   |   16  |   23
#     R0   |   29  |    5
#     R1   |   31  |    6
#     R2   |   33  |   13 
#     R3   |   32  |   12 
#     R4   |   37  |   26 
#
# 1 digital to be used as strum:
#
#	Strum  |   7   |    4  
#

class Button:
	"""Button variable class for keyboard buttons"""
	pressed = 0
	def __init__(self,finger,pin,GPIOnum):
		self.finger = finger
		self.pin = pin
		self.GPIOnum = GPIOnum

pins = [11, 13 ,15, 12, 16, 29, 31, 33, 32, 37]
GPIOnums = [17, 27, 22, 18, 23, 5, 6, 13, 12, 26]
finger_names = ["L0", "L1", "L2", "L3", "L4", "R0", "R1", "R2", "R3", "R4"]
fingers = [Button(finger_names[x],pins[x],GPIOnums[x]) for x in range(10)]
strum = Button("STRUM",7,4)

################################################################
#   
#   Initialise and parse arguments
#

def parse_arguments():
    description = ('Open source instument, osordica.')

    parser = argparse.ArgumentParser(description=description)
    parser.add_argument(
        '--wav', '-w',
        metavar='FILE',
        type=argparse.FileType('r'),
        default='bowl.wav',
        help='WAV file (default: bowl.wav)')
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='verbose mode')
    parser.add_argument(
        '--base', '-b',
        metavar='N',
        type=int,
        default=12,
        help='basemode')

    return (parser.parse_args(), parser)

################################################################
#
#   Pitch shifting stuff:
#

def speedx(snd_array, factor):
    """ Speeds up / slows down a sound, by some factor. """
    indices = np.round(np.arange(0, len(snd_array), factor))
    indices = indices[indices < len(snd_array)].astype(int)
    return snd_array[indices]


def stretch(snd_array, factor, window_size, h):
    """ Stretches/shortens a sound, by some factor. """
    phase = np.zeros(window_size)
    hanning_window = np.hanning(window_size)
    result = np.zeros(round(len(snd_array) / factor) + window_size)

    for i in np.arange(0, len(snd_array) - (window_size + h), round(h*factor)):
        # Two potentially overlapping subarrays
        a1 = snd_array[i: i + window_size]
        a2 = snd_array[i + h: i + window_size + h]

        # The spectra of these arrays
        s1 = np.fft.fft(hanning_window * a1)
        s2 = np.fft.fft(hanning_window * a2)

        # Rephase all frequencies
        phase = (phase + np.angle(s2/s1)) % 2*np.pi

        a2_rephased = np.fft.ifft(np.abs(s2)*np.exp(1j*phase))
        i2 = int(i/factor)
        result[i2: i2 + window_size] += hanning_window*a2_rephased.real

    # normalize (16bit)
    result = ((2**(16-4)) * result/result.max())

    return result.astype('int16')


def pitchshift(snd_array, n, base, window_size=2**13, h=2**11):
    """ Changes the pitch of a sound by ``n`` semitones. """
    factor = 2**(1.0 * n / base)
    stretched = stretch(snd_array, 1.0/factor, window_size, h)
    return speedx(stretched[window_size:], factor)
    
################################################################
#
#    Main
#


def main():
    # Parse command line arguments
    (args, parser) = parse_arguments()
    
    # Enable warnings from scipy if requested
    if not args.verbose:
        warnings.simplefilter('ignore')

    fps, sound = wavfile.read(args.wav.name)

    tones = range(-25, 25)
    sys.stdout.write('Transponding sound file... ')
    sys.stdout.flush()
    transposed_sounds = [pitchshift(sound, n, args.base) for n in tones]
    print('DONE')

    # So flexible ;)
    pygame.mixer.init(fps, -16, 1, 2048)
    # For the focus
    screen = pygame.display.set_mode((150, 150))
    # this is not to be used as keyboard but as digital io's
    # probably no need to keep pygame but until it is completely unused i wont remove it
    keys = args.keyboard.read().split('\n')
    sounds = map(pygame.sndarray.make_sound, transposed_sounds)
    key_sound = dict(zip(keys, sounds))
    is_playing = {k: False for k in keys}

    while True:
        # if strum event (strum == 1)
        # then do the things:
        # read remaining digital IO's
        # 
        # lookup table of what that string of IO's represents
        #
        # play that sound
        #
        
        
        
        
        
        event = pygame.event.wait()

        if event.type in (pygame.KEYDOWN, pygame.KEYUP):
            key = pygame.key.name(event.key)

        if event.type == pygame.KEYDOWN:
            if (key in key_sound.keys()) and (not is_playing[key]):
                key_sound[key].play(fade_ms=50)
                is_playing[key] = True

            elif event.key == pygame.K_ESCAPE:
                pygame.quit()
                raise KeyboardInterrupt

        elif event.type == pygame.KEYUP and key in key_sound.keys():
            # Stops with 50ms fadeout
            key_sound[key].fadeout(50)
            is_playing[key] = False


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Goodbye')
        
#need to map raspberrypi io's

#need to load audio sample file

#need to generate clean sine waves of required frequencies to see if it sounds better

#need to stretch and attenuate/amplify scaled sound

#need to do lots of other stuff, if you think of anything just add it
