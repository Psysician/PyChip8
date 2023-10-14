import sys
import numpy as np
import pygame as pg


def main():
    rom = None

    with open(sys.argv[1], "rb") as f:
        rom = np.array([int(x) for x in f.read()], np.ubyte)

    print(rom)



if __name__ == "__main__":
    main()



class Chip8:
    def __init__(self):
        self.ram = np.array([0 for _ in range(0x1000)], np.ubyte)
        # the 15 V registers
        self.regV = np.array([0 for _ in range(16)], np.ubyte)
        # the 16 bit I register (instruction pointer)
        self.regI = np.ushort(0)
