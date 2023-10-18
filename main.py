import sys, random
import pygame as pg

from byte import Byte, Short


pg.init()

FONT = [
    # 0
    0xF0,
    0x90,
    0x90,
    0x90,
    0xF0,

    # 1
    0x20,
    0x60,
    0x20,
    0x20,
    0x70,

    # 2
    0xF0,
    0x10,
    0xF0,
    0x80,
    0xF0,

    # 3
    0xF0,
    0x10,
    0xF0,
    0x10,
    0xF0,

    # 4
    0x90,
    0x90,
    0xF0,
    0x10,
    0x10,

    # 5
    0xF0,
    0x80,
    0xF0,
    0x10,
    0xF0,

    # 6
    0xF0,
    0x80,
    0xF0,
    0x90,
    0xF0,

    # 7
    0xF0,
    0x10,
    0x20,
    0x40,
    0x40,

    # 8
    0xF0,
    0x90,
    0xF0,
    0x90,
    0xF0,

    # 9
    0xF0,
    0x90,
    0xF0,
    0x10,
    0xF0,

    # A
    0xF0,
    0x90,
    0xF0,
    0x90,
    0x90,

    # B
    0xE0,
    0x90,
    0xE0,
    0x90,
    0xE0,

    # C
    0xF0,
    0x80,
    0x80,
    0x80,
    0xF0,

    # D
    0xE0,
    0x90,
    0x90,
    0x90,
    0xE0,

    # E
    0xF0,
    0x80,
    0xF0,
    0x80,
    0xF0,

    # F
    0xF0,
    0x80,
    0xF0,
    0x80,
    0x80,
]


class Chip8:
    def __init__(self, rom, scale=10):
        self.ram = [Byte(0) for _ in range(0x1000)]

        for i, b in enumerate(FONT):
            self.ram[i] = b

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

        # create display
        self.scale = scale
        self.display = pg.display.set_mode((64 * scale, 32 * scale))

        self.screen = None
        self.clear_display()


    def fetch(self) -> Short:
        return Short.from_bytes(self.ram[self.regPC], self.ram[self.regPC + 1])

    def execute(self, instr: Short):
        match instr:
            # 00E0 clear display
            case 0x00E0:
                self.clear_display()
                self.regPC += 2

            # 00EE return from subroutine
            case 0x00EE:
                self.regPC = self.stack[self.regSP]
                self.regSP -= 2

            # 0nnn jump to address (ignored)
            case x if x & 0xF000 == 0:
                self.regPC += 2

            # 1nnn jump to address
            case x if (x & 0xF000) >> 12 == 1:
                self.regPC = Short(x & 0x0FFF)

            # 2nnn call adress
            case x if (x & 0xF000) >> 12 == 2:
                self.regSP += 2
                self.stack[self.regSP] = self.regPC
                self.regPC = Short(x & 0x0FFF)

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
                        self.regV[vX] = self.regV[vX] + self.regV[vY]
                        self.regV[0xF] = Byte(1) if self.regV[vX].wrapped else Byte(0)

                    case 5: # SUB
                        self.regV[vX] = self.regV[vX] - self.regV[vY]
                        self.regV[0xF] = Byte(1) if not self.regV[vX].wrapped else Byte(0)

                    case 6: # SHR
                        self.regV[0xF] = Byte(1) if self.regV[vX] & 1 == 1 else Byte(0)
                        self.regV[vX] //= 2

                    case 7: # SUBN
                        self.regV[vX] = self.regV[vY] - self.regV[vX]
                        self.regV[0xF] = Byte(1) if not self.regV[vX].wrapped else Byte(0)

                    case 0xE: # SHL
                        self.regV[0xF] = Byte(1) if self.regV[vX] & (1 << 7) == 1 else Byte(0)
                        self.regV[vX] *= 2

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
                self.regPC += 2

            # Bnnn jmp to nnn + reg V0
            case x if (x & 0xF000) >> 12 == 0xB:
                self.regPC = Short(x & 0x0FFF) + self.regV[0]

            # Cxkk Vx = random byte & kk
            case x if (x & 0xF000) >> 12 == 0xC:
                rnd = Byte(random.randint(0, 255))
                vX = x << 4 >> 12
                self.regV[vX] = rnd & x << 8 >> 8
                self.regPC += 2

            # Dxyn draw sprite
            case x if (x & 0xF000) >> 12 == 0xD:
                sX = x & 0x0F00 >> 8
                sY = x & 0x00F0 >> 4
                sN = x & 0x000F

                self.draw_sprite(self.ram[self.regI:self.regI+sN], sX, sY)

                self.regPC += 2

            # Ex9E skip if key is pressed
            case x if (x & 0xF0FF) == 0xE09E:
                raise NotImplemented

            # ExA1 skip if key is not pressed
            case x if (x & 0xF0FF) == 0xE0A1:
                raise NotImplemented

            # Fx07 Vx = DT
            case x if (x & 0xF0FF) == 0xF007: 
                vX = x << 4 >> 12
                self.regV[vX] = self.delayT
                self.regPC += 2

            # Fx0A Vx = next keypress
            case x if (x & 0xF0FF) == 0xF00A:
                raise NotImplemented

            # Fx15 Vx = Delay timer     Ich hab keine ahnung ob das hier sinn macht
            #                           mein ausbilder zwingt mich übrigens dazu meine docs, kommentare und generell alles auf deutsch zu schreiben
            case x if (x & 0xF0FF) == 0xF015:
                vX = x << 4 >> 12
                self.delayT = self.regV[vX]
                self.regPC += 2

            # Fx18 ST = Vx
            case x if (x & 0xF0FF) == 0xF018:
                vX = x << 4 >> 12
                self.soundT = self.regV[vX]
                self.regPC += 2

            # Fx1E I += Vx
            case x if (x & 0xF0FF) == 0xF01E:
                vX = x << 4 >> 12
                self.regI = self.regI + self.regV[vX]
                self.regPC += 2


            case x:
                raise Exception("unimplemented: ", hex(x)[2:])


    def run(self):
        running = True

        while running:
            instr = self.fetch()

            print(hex(instr))

            for event in pg.event.get():
                    if event.type == pg.QUIT:
                        running = False

            self.execute(instr)

            pg.display.flip()


    def draw_sprite(self, sprite, x, y):
        for sy, byte in enumerate(sprite):
            for sx, bit in enumerate(reversed(range(8))):
                pix = (byte >> bit) & 1 == 1
                if pix:
                    self.toggle_pixel(x + sx, y + sy)


    def toggle_pixel(self, x, y):
        rect = pg.Rect(x * self.scale, y * self.scale, self.scale, self.scale)

        if self.screen[x][y]:
            pg.draw.rect(self.display, "black", rect)
        else:
            pg.draw.rect(self.display, "white", rect)

        self.screen[x][y] = not self.screen[x][y]



    def clear_display(self):
        self.screen = [[False]*32]*64
        self.display.fill("black")


def main():
    rom = None

    with open(sys.argv[1], "rb") as f:
        rom = [Byte(x) for x in f.read()]

    cpu = Chip8(rom)
    cpu.run()



if __name__ == "__main__":
    main()
