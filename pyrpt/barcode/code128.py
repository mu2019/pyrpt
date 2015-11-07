#!/usr/bin/env python

#author=http://jaghatai.infogami.com/python/barcode
#copyright by author

import re
from PIL import Image, ImageDraw,ImageFont

code_img_data=['11011001100','11001101100','11001100110','10010011000','10010001100',
               '10001001100','10011001000','10011000100','10001100100','11001001000',
               '11001000100','11000100100','10110011100','10011011100','10011001110',
               '10111001100','10011101100','10011100110','11001110010','11001011100',
               '11001001110','11011100100','11001110100','11101101110','11101001100',
               '11100101100','11100100110','11101100100','11100110100','11100110010',
               '11011011000','11011000110','11000110110','10100011000','10001011000',
               '10001000110','10110001000','10001101000','10001100010','11010001000',
               '11000101000','11000100010','10110111000','10110001110','10001101110',
               '10111011000','10111000110','10001110110','11101110110','11010001110',
               '11000101110','11011101000','11011100010','11011101110','11101011000',
               '11101000110','11100010110','11101101000','11101100010','11100011010',
               '11101111010','11001000010','11110001010','10100110000','10100001100',
               '10010110000','10010000110','10000101100','10000100110','10110010000',
               '10110000100','10011010000','10011000010','10000110100','10000110010',
               '11000010010','11001010000','11110111010','11000010100','10001111010',
               '10100111100','10010111100','10010011110','10111100100','10011110100',
               '10011110010','11110100100','11110010100','11110010010','11011011110',
               '11011110110','11110110110','10101111000','10100011110','10001011110',
               '10111101000','10111100010','11110101000','11110100010','10111011110',
               '10111101110','11101011110','11110101110','11010000100','11010010000',
               '11010011100','1100011101011'
               ]

code_b_data={' ': 0, '!': 1, '"': 2, '#': 3, '$': 4, '%': 5, '&': 6, '\'': 7,
             '(': 8, ')': 9, '*': 10, '+': 11, ',': 12, '-': 13, '.': 14, '/': 15,
             '0': 16, '1': 17, '2': 18, '3': 19, '4': 20, '5': 21, '6': 22, '7': 23,
             '8': 24, '9': 25, ':': 26, ';': 27, '<': 28, '=': 29, '>': 30, '?': 31,
             '@': 32, 'A': 33, 'B': 34, 'C': 35, 'D': 36, 'E': 37, 'F': 38, 'G': 39,
             'H': 40, 'I': 41, 'J': 42, 'K': 43, 'L': 44, 'M': 45, 'N': 46, 'O': 47,
             'P': 48, 'Q': 49, 'R': 50, 'S': 51, 'T': 52, 'U': 53, 'V': 54, 'W': 55,
             'X': 56, 'Y': 57, 'Z': 58, '[': 59, '\\': 60, ']': 61, '^': 62, '_': 63,
             '`': 64, 'a': 65, 'b': 66, 'c': 67, 'd': 68, 'e': 69, 'f': 70, 'g': 71,
             'h': 72, 'i': 73, 'j': 74, 'k': 75, 'l': 76, 'm': 77, 'n': 78, 'o': 79,
             'p': 80, 'q': 81, 'r': 82, 's': 83, 't': 84, 'u': 85, 'v': 86, 'w': 87,
             'x': 88, 'y': 89, 'z': 90, '{': 91, '|': 92, '}': 93, '~': 94, 'DEL': 95,
             'FNC3': 96, 'FNC2': 97, 'SHIFT': 98, 'Code C': 99, 'FNC4': 100, 'Code A': 101,
             'FNC1': 102, 'START A': 103, 'START B': 104, 'START C': 105, 'STOP': 106
             }

def codeBFromString (string):
    code=code_img_data[code_b_data['START B']]
    count=1
    checksum=code_b_data['START B']
    for letter in string:
        code += code_img_data[code_b_data[letter]]
        checksum += count*code_b_data[letter]
        count += 1
    code += code_img_data[checksum%103]
    code += code_img_data[code_b_data['STOP']]
    return (code)

def codeBCFromString (string):
    # Look for even numbered groups of digits (at least 4) to use code c
    frags = re.split('(\d\d(?:\d\d)+)', string)
    if frags[0]:
        # the string starts with regular code b data
        code = code_img_data[code_b_data['START B']]
        checksum = code_b_data['START B']
        codeb = True
    else:
        # the string starts with a matching set of numbers - code c
        code = code_img_data[code_b_data['START C']]
        checksum = code_b_data['START C']
        codeb = False
        frags.pop(0)

    # remove the last frag if it's blank
    # i.e. if the string ends with a matching numeric sequence
    if not(frags[-1]):
        frags.pop(-1)

    count = 1
    for frag in frags:
        if codeb:
            if count > 1: #switch to code b
                code += code_img_data[100]
                checksum += count*100
                count += 1
            for letter in frag:
                code += code_img_data[code_b_data[letter]]
                checksum += count*code_b_data[letter]
                count += 1
        else:
            if count > 1: #switch to code c
                code += code_img_data[code_b_data['Code C']]
                checksum += count*code_b_data['Code C']
                count += 1
            for pair in re.findall('..', frag):
                code += code_img_data[int(pair)]
                checksum += count*int(pair)
                count += 1
        codeb = not(codeb)
    code += code_img_data[checksum%103]
    code += code_img_data[code_b_data['STOP']]
    return (code)


def barcodeImg (string, label='',height=70,padding=10,rotate=0,fonttype='arial.ttf',fontsize=16):
    width = len(string) + padding*2#20
    im = Image.new('1', (width,height), 24)
    draw = ImageDraw.Draw(im)
    x = padding#10
    y=height-22
    for char in string:
        draw.rectangle(((x, padding),(x, y)), fill=not(int(char)))
        x += 1
    if label:
        font = ImageFont.truetype(fonttype,fontsize)
        labelsize = draw.textsize(label,font=font)
        draw.text((int((width-labelsize[0])/2.0), y+1), label, fill=0,font=font)
    return im.rotate(rotate)
    


