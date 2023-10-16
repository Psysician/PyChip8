import sys, random
import pygame as pg

from byte import Byte, Short



class Chip8:
    def __init__(self, rom):
        self.ram = [Byte(0) for _ in range(0x1000)]

        # load the rom
        for i, b in enumerate(rom):
            self.ram[0x200 + i] = b

        # the 15 "V" registers
        self.regV = [Byte(0) for _ in range(16)]

        # the 16 bit "I" register
        self.regI = Short(0)

        # program counter
        self.regPC = Short(0x200)

        # call stack
        self.stack = [Short(0) for _ in range(16)]

        # stack pointer
        self.regSP = Byte(0)

        self.delayT = Byte(0)
        self.soundT = Byte(0)

    def fetch(self) -> Short:
        return Short.from_bytes(self.ram[self.regPC], self.ram[self.regPC + 1])

    def run(self):
        while True:
            instr = self.fetch()

            print(hex(instr))

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
                    self.regPC = Short(x & 0x0FFF)

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

                    self.regPC += 2

                # 7xkk add kk to Vx
                case x if (x & 0xF000) >> 12 == 7:
                    vX = x << 4 >> 12
                    kk = x << 8 >> 8
                    self.regV[vX] += kk

                    self.regPC += 2

                # 8xy? operators
                case x if (x & 0xF000) >> 12 == 5:
                    vX = x << 4 >> 12
                    vY = x << 8 >> 12
                    valX = self.regV[vX]
                    valY = self.regV[vY]

                    op = x & 0x000F

                    match op:
                        case 0: # assign
                            self.regV[vX] = self.regV[vY]
                        case 1: # OR
                            self.regV[vX] = self.regV[vX] | self.regV[vY]
                        case 2: # AND
                            self.regV[vX] = self.regV[vX] & self.regV[vY]
                        case 3: # XOR
                            self.regV[vX] = self.regV[vX] ^ self.regV[vY]
                        case 4: # ADD
                            res = int(valX) + int(valY)
                            self.regV[0xF] = Byte(1) if res > 0xFF else Byte(0)
                            self.regV[vX] = Byte(res)

                        case 5: # SUB
                            self.regV[0xF] = Byte(1) if valX > valY else Byte(0)
                            self.regV[vX] = valX - valY

                        case 1: # SHR
                            self.regV[0xF] = Byte(1) if valX & 1 == 1 else Byte(0)
                            self.regV[vX] = Byte()

                    self.regPC += 2

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

                # Bnnn jmp to nnn + reg V
                case x if (x & 0xF000) >> 12 == 0xB:
                    self.regPC = Short(x & 0x0FFF) + self.regV

                # Cxkk Vx = random byte & kk
                case x if (x & 0xF000) >> 12 == 0xC:
                    rnd = Byte(random.randint(0, 255))
                    vX = x << 4 >> 12
                    self.regV[vX] = rnd & x << 8 >> 8

                # Dxyn 
                case x if (x & 0xF000) >> 12 == 0xD:
                    pass
                     
                # Ex9E
                case x if (x & 0xF0FF) == 0xE09E:
                    pass

                # ExA1
                case x if (x & 0xF0FF) == 0xE0A1:
                      pass
                
                # Fx07
                case x if (x & 0xF0FF) == 0xF007: 
                    vX = x << 4 >> 12
                    self.regV[vX] = self.delayT
                
                # Fx0A
                case x if (x & 0xF0FF) == 0xF00A:
                    pass

                # Fx15 Vx = Delay timer     Ich hab keine ahnung ob das hier sinn macht
                #                           mein ausbilder zwingt mich übrigens dazu meine docs, kommentare und generell alles auf deutsch zu schreiben
                case x if (x & 0xF0FF) == 0xF015:
                    Vx = x << 4 >> 12
                    self.delayT = Vx

                # Fx18
                case x if (x & 0xF0FF) == 0xF018:
                    vX = x << 4 >> 12
                    self.soundT = Vx

                # Fx1E regI 0 I + Vx    noch weniger plan 
                case x if (x & 0xF0FF) == 0xF01E:
                    vX = x << 4 >> 12
                    self.regI = self.regI + vX
                
                

                case x:
                    raise Exception("unimplemented: ", hex(x)[2:])




    def clear_display(self):
        pass # TODO


def main():
    rom = None

    with open(sys.argv[1], "rb") as f:
        rom = [Byte(x) for x in f.read()]

    cpu = Chip8(rom)
    cpu.run()



if __name__ == "__main__":
    main()
