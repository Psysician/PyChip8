import sys, random, os, msvcrt
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "hide"
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

def get_key():
    c = msvcrt.getch().decode('ASCII')
    k = pg.key.get_pressed()
    if k[pg.K_0]:
        return 0x0
    elif k[pg.K_1]:
        return 0x1
    elif k[pg.K_2]:
        return 0x2
    elif k[pg.K_3]:
        return 0x3
    elif k[pg.K_4]:
        return 0x4
    elif k[pg.K_5]:
        return 0x5
    elif k[pg.K_6]:
        return 0x6
    elif k[pg.K_7]:
        return 0x7
    elif k[pg.K_8]:
        return 0x8
    elif k[pg.K_9]:
        return 0x9
    elif k[pg.K_a]:
        return 0xa
    elif k[pg.K_b]:
        return 0xb
    elif k[pg.K_c]:
        return 0xc
    elif k[pg.K_d]:
        return 0xd
    elif k[pg.K_e]:
        return 0xe
    elif k[pg.K_f]:
        return 0xf
    elif c == "0":
        return 0x0  
    
    elif c == "0":
        return 0x0  
    elif c == "1":
        return 0x1
    elif c == "2":
        return 0x2
    elif c == "3":
        return 0x3
    elif c == "4":
        return 0x4
    elif c == "5":
        return 0x5
    elif c == "6":
        return 0x6
    elif c == "7":
        return 0x7
    elif c == "8":
        return 0x8
    elif c == "9":
        return 0x9
    elif c == "a":
        return 0xa
    elif c == "b":
        return 0xb
    elif c == "c":
        return 0xc
    elif c == "d":
        return 0xd
    elif c == "e":
        return 0xe
    elif c == "f":
        return 0xf


    return None

class Chip8:
    def __init__(self, rom, scale=10, debug=False):
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

        self.debug_on = debug


    def fetch(self, addr) -> Short:
        return Short.from_bytes(self.ram[addr], self.ram[addr + 1])

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
                self.regPC += 2

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
                Vx = Byte(x << 4 >> 12)
                kk = Byte(x << 8 >> 8)
                if self.regV[Vx] == kk:
                    self.regPC += 4
                else:
                    self.regPC += 2

            # 4xkk skip instruction if Vx != kk
            case x if (x & 0xF000) >> 12 == 4:
                Vx = Byte(x << 4 >> 12)
                kk = Byte(x << 8 >> 8)
                if self.regV[Vx] != kk:
                    self.regPC += 4
                else:
                    self.regPC += 2

            # 5xy0 skip instruction if Vx == Vy
            case x if (x & 0xF000) >> 12 == 5:
                Vx = Byte(x << 4 >> 12)
                Vy = Byte(x << 8 >> 12)
                if self.regV[Vx] == self.regV[Vy]:
                    self.regPC += 4
                else:
                    self.regPC += 2

            # 6xkk set Vx = kk
            case x if (x & 0xF000) >> 12 == 6:
                Vx = Byte(x << 4 >> 12)
                kk = Byte(x << 8 >> 8)
                self.regV[Vx] = kk

                self.regPC += 2

            # 7xkk add kk to Vx
            case x if (x & 0xF000) >> 12 == 7:
                Vx = Byte(x << 4 >> 12)
                kk = Byte(x << 8 >> 8)
                self.regV[Vx] += kk

                self.regPC += 2

            # 8xy? operators
            case x if (x & 0xF000) >> 12 == 8:
                Vx = Byte(x << 4 >> 12)
                Vy = Byte(x << 8 >> 12)

                op = Byte(x & 0x000F)

                match op:
                    case 0: # assign
                        self.regV[Vx] = self.regV[Vy]
                    case 1: # OR
                        self.regV[Vx] = self.regV[Vx] | self.regV[Vy]
                    case 2: # AND
                        self.regV[Vx] = self.regV[Vx] & self.regV[Vy]
                    case 3: # XOR
                        self.regV[Vx] = self.regV[Vx] ^ self.regV[Vy]
                    case 4: # ADD
                        self.regV[Vx] = self.regV[Vx] + self.regV[Vy]
                        self.regV[0xF] = Byte(1) if self.regV[Vx].wrapped else Byte(0)

                    case 5: # SUB
                        self.regV[Vx] = self.regV[Vx] - self.regV[Vy]
                        self.regV[0xF] = Byte(1) if not self.regV[Vx].wrapped else Byte(0)

                    case 6: # SHR
                        self.regV[0xF] = Byte(1) if self.regV[Vx] & 1 == 1 else Byte(0)
                        self.regV[Vx] //= 2

                    case 7: # SUBN
                        self.regV[Vx] = self.regV[Vy] - self.regV[Vx]
                        self.regV[0xF] = Byte(1) if not self.regV[Vx].wrapped else Byte(0)

                    case 0xE: # SHL
                        self.regV[0xF] = Byte(1) if self.regV[Vx] & (1 << 7) == 1 else Byte(0)
                        self.regV[Vx] *= 2

                self.regPC += 2

            # 9xy0 skip instrction if Vx != Vy
            case x if (x & 0xF000) >> 12 == 9:
                Vx = Byte(x << 4 >> 12)
                Vy = Byte(x << 8 >> 12)
                if self.regV[Vx] != self.regV[Vy]:
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
                Vx = Byte(x << 4 >> 12)
                rnd = Byte(random.randint(0, 255))
                self.regV[Vx] = rnd & x << 8 >> 8
                self.regPC += 2

            # Dxyn draw sprite
            case x if (x & 0xF000) >> 12 == 0xD:
                Sx = Byte((x & 0x0F00) >> 8)
                Sy = Byte((x & 0x00F0) >> 4)
                Sn = Byte(x & 0x000F)

                self.draw_sprite(self.ram[self.regI:self.regI+Sn], int(self.regV[Sx]), int(self.regV[Sy]))

                self.regPC += 2

            # Ex9E skip if key is pressed
            case x if (x & 0xF0FF) == 0xE09E:
                Vx = Byte(x << 4 >> 12)
                if get_key() == self.regV[Vx]:
                    self.regPC += 4
                else:
                    self.regPC += 2

            # ExA1 skip if key is not pressed
            case x if (x & 0xF0FF) == 0xE0A1:
                Vx = Byte(x << 4 >> 12)
                k = get_key()
                if k != self.regV[Vx]:
                    self.regPC += 4
                else:
                    self.regPC += 2

            # Fx07 Vx = DT
            case x if (x & 0xF0FF) == 0xF007: 
                Vx = Byte(x << 4 >> 12)
                self.regV[Vx] = self.delayT
                self.regPC += 2

            # Fx0A wait for key, store it in Vx
            case x if (x & 0xF0FF) == 0xF00A:
                Vx = Byte(x << 4 >> 12)
                k = get_key()
                while (k==None):
                    k = get_key()
                    print("stuck")
                    pass

                if k != None:
                    self.regV[Vx] = k
                    self.regPC += 2

            # Fx15 Vx = Delay timer     Ich hab keine ahnung ob das hier sinn macht
            #                           mein ausbilder zwingt mich übrigens dazu meine docs, kommentare und generell alles auf deutsch zu schreiben
            case x if (x & 0xF0FF) == 0xF015:
                Vx = Byte(x << 4 >> 12)
                self.delayT = self.regV[Vx]
                self.regPC += 2

            # Fx18 soundT = Vx
            case x if (x & 0xF0FF) == 0xF018:
                Vx = Byte(x << 4 >> 12)
                self.soundT = self.regV[Vx]
                self.regPC += 2

            # Fx1E I += Vx
            case x if (x & 0xF0FF) == 0xF01E:
                Vx = Byte(x << 4 >> 12)
                self.regI = self.regI + self.regV[Vx]
                self.regPC += 2

            # Fx29 load glyph from font data corresponding to Vx
            case x if (x & 0xF0FF) == 0xF029:
                Vx = Byte(x << 4 >> 12)
                # each glyph is 5 bytes,
                # the font data is stored at address 0
                # Vx = wievieltes sprite
                self.regI = Short(self.regV[Vx] * 5)
                self.regPC += 2

            # Fx33 store decimal representation of Vx at I, I+1 and I+2
            case x if (x & 0xF0FF) == 0xF033:
                Vx = Byte(x << 4 >> 12)
                s = "{:03}".format(Vx.num)

                self.ram[self.regI] = int(s[0])
                self.ram[self.regI+1] = int(s[1])
                self.ram[self.regI+2] = int(s[2])

                self.regPC += 2


            # Fx55 store V0 - Vx in memory
            case x if (x & 0xF0FF) == 0xF055:
                Vx = Byte(x << 4 >> 12)
                for i in range(Vx):
                    self.ram[self.regI+i] = self.regV[i]

                self.regPC += 2

            # Fx65 
            case x if (x & 0xF0FF) == 0xF065:
                Vx = Byte(x << 4 >> 12)
                for i in range(Vx):
                    self.regV[i] = self.ram[self.regI+i]

                self.regPC += 2


            
            case x:
                raise Exception("unimplemented: ", hex(x)[2:])


    def run(self):
        running = True

        if self.debug_on:
            self.debug()

        while running:
            instr = self.fetch(self.regPC)

            for event in pg.event.get():
                if event.type == pg.QUIT:
                    running = False

            self.execute(instr)

            pg.display.flip()

            if self.debug_on:
                self.debug(instr)


    def draw_sprite(self, sprite, x, y):
        sy = 0
        for byte in sprite:
            sx = 0
            for bit in reversed(range(8)):
                if (byte >> bit) & 1 == 1:
                    self.toggle_pixel(x + sx, y + sy)
                sx += 1
            sy += 1


    def toggle_pixel(self, x, y):
        rect = pg.Rect(x * self.scale, y * self.scale, self.scale, self.scale)

        self.regV[0xF] = Byte(0)

        if self.screen[x][y]:
            self.regV[0xF] = Byte(1)
            pg.draw.rect(self.display, "black", rect)
        else:
            pg.draw.rect(self.display, "white", rect)

        self.screen[x][y] = not self.screen[x][y]


    def clear_display(self):
        self.screen = []
        for _ in range(64):
            self.screen.append([False]*32)
        self.display.fill("black")


    last_instr = None

    def debug(self, instr: Short | None = None):
        lines = 6
        if not self.last_instr:
            sys.stdout.write("\n"*(lines+1))
        sys.stdout.write("\033[F"*lines)

        def black(s: str):
            return "\x1b[30m" + s + "\x1b[0m"

        # instructions
        sys.stdout.write(black(str(self.last_instr if self.last_instr else "    ")) + " ")
        sys.stdout.write("\x1b[30;42m" + str(instr if instr else "....") + "\x1b[0m ")
        sys.stdout.write(black(str(self.fetch(self.regPC))))
        sys.stdout.write("\n")

        # registers
        sys.stdout.write(black("PC: ") + repr(self.regPC) + black(" I: ") + repr(self.regI) + black(" SP: ") + str(self.regSP))
        sys.stdout.write("\n\n")

        for i, vreg in enumerate(self.regV):
            sys.stdout.write(black("V" + "{:01X}".format(i) + ":") + " " + str(vreg) + " ")
            if i == 7:
                sys.stdout.write("\n")
        sys.stdout.write("\n\n")

        sys.stdout.write(black("stack: "))
        if self.regSP == 0:
            sys.stdout.write("empty                                     ")
        for i in range(self.regSP):
            sys.stdout.write(str(self.stack[i]) + " ")


        sys.stdout.flush()

        self.last_instr = instr if instr else "...."
        breakpoint()



def main():
    rom = None

    if len(sys.argv) < 2:
        print("ERROR: Expected input ROM")
        exit(1)

    with open(sys.argv[1], "rb") as f:
        rom = [Byte(x) for x in f.read()]

    cpu = Chip8(rom, debug=False)
    cpu.run()



if __name__ == "__main__":
    main()
