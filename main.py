import sys
import numpy as np
import pygame as pg


class Chip8:
    def __init__(self, rom):
        self.ram = np.array([0 for _ in range(0x1000)], np.ubyte)

        # load the rom
        for i, b in enumerate(rom):
            self.ram[0x200 + i] = b

        # the 15 "V" registers
        self.regV = np.array([0 for _ in range(16)], np.ubyte)

        # the 16 bit "I" register
        self.regI = np.ushort(0)

        # program counter
        self.regPC = np.ushort(0x200)

        # call stack
        self.stack = np.array([0 for _ in range(16)], np.ushort)

        # stack pointer
        self.regSP = np.ubyte(0)

        self.delayT = 0
        self.soundT = 0

    def fetch(self) -> np.ushort:
        return (np.ushort(self.ram[self.regPC]) << 8) | self.ram[self.regPC + 1]

    def run(self):
        while True:
            instr = self.fetch()

            print(hex(instr)[2:])

            match instr:
                # 00E0 clear display
                case 0x00E0:
                    self.clear_display()
                    self.regPC += 2

                # 00EE return from subroutine
                case 0x00EE:
                    self.regPC = self.stack[self.regSP]
                    self.regSP -= 2

                # 0nnn jump to address (ignored by modern)
                case x if x & 0xF000 == 0:
                    self.regPC += 2

                # 1nnn jump to address
                case x if (x & 0xF000) >> 12 == 1:
                    self.regPC = np.ushort(x & 0xFFF)

                # 2nnn call adress
                case x if (x & 0xF000) >> 12 == 2:
                    self.regSP += 2
                    self.stack[self.regSP] = self.regPC

                # 3xkk skip instruction if Vx == kk
                case x if (x & 0xF000) >> 12 == 3:
                    vX = x << 4 >> 12
                    kk = x << 8 >> 8
                    if self.regV[vX] == kk:
                        self.regPC += 4
                    else:
                        self.regPC += 2

                # 4xkk skip instruction if Vx != kk
                case x if (x & 0xF000) >> 12 == 4:
                    vX = x << 4 >> 12
                    kk = x << 8 >> 8
                    if self.regV[vX] != kk:
                        self.regPC += 4
                    else:
                        self.regPC += 2

                # 5xy0 skip instruction if Vx == Vy
                case x if (x & 0xF000) >> 12 == 5:
                    vX = x << 4 >> 12
                    vY = x << 8 >> 12
                    if self.regV[vX] == self.regV[vY]:
                        self.regPC += 4
                    else:
                        self.regPC += 2

                # 6xkk set Vx = kk
                case x if (x & 0xF000) >> 12 == 6:
                    vX = x << 4 >> 12
                    kk = x << 8 >> 8
                    self.regV[vX] = kk

                # 7xkk add kk to Vx
                case x if (x & 0xF000) >> 12 == 7:
                    vX = x << 4 >> 12
                    kk = x << 8 >> 8
                    self.regV[vX] += kk

                # 8xy? operators
                case x if (x & 0xF000) >> 12 == 5:
                    vX = x << 4 >> 12
                    vY = x << 8 >> 12

                    op = x & 0xFFF0

                    match op:
                        case 0:
                            pass
                            
                # 9xy0 skip instrction if Vx != Vy
                case x if (x & 0xF000) >> 12 == 9:
                    vX = x << 4 >> 12
                    vY = x << 8 >> 12
                    if self.regV[vX] != self.regV[vY]:
                        self.regPC += 4
                    else:
                        self.regPC += 2

                # Annn set reg I to nnn
                case x if (x & 0xF000) >> 12 == 0xA:
                    self.regI = x << 4 >> 4

                case x:
                    raise Exception("unimplemented: ", hex(x)[2:])




    def clear_display(self):
        pass # TODO


def main():
    rom = None

    with open(sys.argv[1], "rb") as f:
        rom = np.array([int(x) for x in f.read()], np.ubyte)

    cpu = Chip8(rom)
    cpu.run()



if __name__ == "__main__":
    main()
