#!/usr/bin/env python

from scipy.io import wavfile
import argparse
import numpy as np
import pygame
import sys
import warnings
import lookup
#import RPi.GPIO as GPIO

# need 10 digitals to be used as keys:
# L0 is left pinky, R4 is right pinky etc
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
# Or keyboard implementation for testing/debugging
#   
#   Finger |       Key 
#     L0   |   K_a
#     L1   |   K_s
#     L2   |   K_d
#     L3   |   K_f 
#     L4   |   K_v
#     R0   |   K_n
#     R1   |   K_j
#     R2   |   K_k 
#     R3   |   K_l 
#     R4   |   K_SEMICOLON
#
#   Strum  |   K_SPACE
#




class Button:
    """Button variable class for keyboard buttons"""
    pressed = 0
    def __init__(self,finger,pin,GPIOnum,key):
        self.finger = finger
        self.pin = pin
        self.GPIOnum = GPIOnum
        self.key = key

pins = [11, 13 ,15, 12, 16, 29, 31, 33, 32, 37]
GPIOnums = [17, 27, 22, 18, 23, 5, 6, 13, 12, 26]
finger_names = ["L0", "L1", "L2", "L3", "L4", "R0", "R1", "R2", "R3", "R4"]
kb_keys = [pygame.K_a,pygame.K_s,pygame.K_d,pygame.K_f,pygame.K_v,pygame.K_n,pygame.K_j,pygame.K_k,pygame.K_l,pygame.K_SEMICOLON]
fingers = [Button(finger_names[x],pins[x],GPIOnums[x],kb_keys[x]) for x in range(10)]
strum = Button("STRUM",7,4,pygame.K_SPACE)

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
        '--keyboard', '-k',
        metavar='FILE',
        type=argparse.FileType('r'),
        default='typewriter.kb',
        help='keyboard file (default: typewriter.kb)')
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


def pitchshift(snd_array, factor, base, window_size=2**14, h=2**11):
    """ Changes the pitch of a sound by ``n`` semitones. """
    stretched = stretch(snd_array, 1.0/factor, window_size, h)
    return speedx(stretched[window_size:], factor)
    
################################################################
#
#    Main
#

def bin2dec(bin):
    mult = [2**(n) for n in range(len(bin))]
    return sum(np.multiply(bin,mult))

def main():
    # Parse command line arguments
    (args, parser) = parse_arguments()
    
    # Enable warnings from scipy if requested
    if not args.verbose:
        warnings.simplefilter('ignore')

    fps, sound = wavfile.read(args.wav.name)
    factor = lookup.factors
    sys.stdout.write('Transponding sound file... ')
    sys.stdout.flush()
    transposed_sounds = [pitchshift(sound, lookup.factors[x], args.base) for x in lookup.factors.keys()]
    print('DONE')

    # So flexible ;)
    pygame.mixer.init(fps, -16, 1, 4096)
    # For the focus
    screen = pygame.display.set_mode((150, 150))
    # this is not to be used as keyboard but as digital io's
    # probably no need to keep pygame but until it is completely unused i wont remove it
    # keys = args.keyboard.read().split('\n')
    #pygame.key.set_repeat(500,500)
    
    sounds = map(pygame.sndarray.make_sound, transposed_sounds)
    
    key_sound = dict(zip(lookup.factors.keys(), sounds))
    is_playing = {k: False for k in key_sound}

    while True:
        event = pygame.event.wait()
        if pygame.key.get_pressed()[pygame.K_SPACE]==1:
            if event.type in (pygame.KEYDOWN, pygame.KEYUP):
                if event.type == pygame.KEYDOWN:
                    #if event.key == pygame.K_SPACE:
                        print("Space pressed (y)")
                        pressed = pygame.key.get_pressed()
                        comb = [pressed[fingers[x].key] for x in range(10)]
                        print(comb)
                        dec = bin2dec(comb)
                        print(dec)
                        sounds_to_play = lookup.lookup_sounds(dec)
                        for x in sounds_to_play:
                            if (x in key_sound.keys()):# and (not is_playing[x]):
                                key_sound[x].play(fade_ms=50)
                                #is_playing[x] = True
        if hasattr(event, "key"):
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                
                    #read all keys pressed
                    #determine sound from luptable
        
        
        #if event.type in (pygame.KEYDOWN, pygame.KEYUP)
        #    key = pygame.key.name(event.key)
        
        # if strum event (strum == 1)
        # then do the things:
        # read remaining digital IO's
        # 
        # lookup table of what that string of IO's represents
        #
        # play that sound
        #
        
        
        
        
        
#        event = pygame.event.wait()
#
#        if event.type in (pygame.KEYDOWN, pygame.KEYUP):
#            key = pygame.key.name(event.key)
#
#        if event.type == pygame.KEYDOWN:
 #           if (key in key_sound.keys()) and (not is_playing[key]):
  #              key_sound[key].play(fade_ms=50)
   #             is_playing[key] = True
#
 #           elif event.key == pygame.K_ESCAPE:
  #              pygame.quit()
   #             raise KeyboardInterrupt
#
 #       elif event.type == pygame.KEYUP and key in key_sound.keys():
  #          # Stops with 50ms fadeout
   #         key_sound[key].fadeout(50)
    #        is_playing[key] = False
    

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
