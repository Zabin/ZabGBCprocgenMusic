"""
gbc_lib.py — Core ROM class: SM83 assembler opcodes, color math, header.
Nothing game-specific lives here.
"""

def rgb15(r, g, b):
    return (r & 0x1F) | ((g & 0x1F) << 5) | ((b & 0x1F) << 10)


class ROM:
    def __init__(self, size=32768):
        self.data    = bytearray(size)
        self.pos     = 0
        self.labels  = {}
        self.fixups  = []

    def seek(self, addr): self.pos = addr

    def emit(self, *bs):
        for b in bs:
            self.data[self.pos] = b & 0xFF
            self.pos += 1

    def label(self, n):
        if n in self.labels: raise Exception(f"Dup label '{n}'")
        self.labels[n] = self.pos

    def addr(self, n): return self.labels[n]

    def _abs(self, t):
        if isinstance(t, int): self.emit(t & 0xFF, (t >> 8) & 0xFF)
        else:
            self.fixups.append((self.pos, t, 'abs16')); self.emit(0, 0)

    def _rel(self, t):
        if isinstance(t, int):
            off = t - (self.pos + 1)
            if not (-128 <= off <= 127): raise Exception(f"JR oor {off}")
            self.emit(off & 0xFF)
        else:
            self.fixups.append((self.pos, t, 'rel8')); self.emit(0)

    def NOP(self):   self.emit(0x00)
    def DI(self):    self.emit(0xF3)
    def EI(self):    self.emit(0xFB)
    def HALT(self):  self.emit(0x76)
    def RET(self):   self.emit(0xC9)
    def RET_Z(self): self.emit(0xC8)
    def RET_NZ(self):self.emit(0xC0)
    def RET_C(self): self.emit(0xD8)
    def RET_NC(self):self.emit(0xD0)
    def RETI(self):  self.emit(0xD9)
    def XOR_A(self): self.emit(0xAF)
    def OR_A(self):  self.emit(0xB7)
    def CPL(self):   self.emit(0x2F)
    def RLA(self):   self.emit(0x17)
    def RRA(self):   self.emit(0x1F)
    def RLCA(self):  self.emit(0x07)
    def RRCA(self):  self.emit(0x0F)
    def DAA(self):   self.emit(0x27)
    def LD_A_n(self,n): self.emit(0x3E, n&0xFF)
    def LD_B_n(self,n): self.emit(0x06, n&0xFF)
    def LD_C_n(self,n): self.emit(0x0E, n&0xFF)
    def LD_D_n(self,n): self.emit(0x16, n&0xFF)
    def LD_E_n(self,n): self.emit(0x1E, n&0xFF)
    def LD_H_n(self,n): self.emit(0x26, n&0xFF)
    def LD_L_n(self,n): self.emit(0x2E, n&0xFF)
    def LD_BC_nn(self,nn): self.emit(0x01, nn&0xFF, (nn>>8)&0xFF)
    def LD_DE_nn(self,nn): self.emit(0x11, nn&0xFF, (nn>>8)&0xFF)
    def LD_HL_nn(self,nn): self.emit(0x21, nn&0xFF, (nn>>8)&0xFF)
    def LD_SP_nn(self,nn): self.emit(0x31, nn&0xFF, (nn>>8)&0xFF)
    def _rr(self,d,s): self.emit(0x40|(d<<3)|s)
    def LD_A_A(self): self._rr(7,7)
    def LD_A_B(self): self._rr(7,0)
    def LD_A_C(self): self._rr(7,1)
    def LD_A_D(self): self._rr(7,2)
    def LD_A_E(self): self._rr(7,3)
    def LD_A_H(self): self._rr(7,4)
    def LD_A_L(self): self._rr(7,5)
    def LD_A_HL(self):self._rr(7,6)
    def LD_B_A(self): self._rr(0,7)
    def LD_C_A(self): self._rr(1,7)
    def LD_D_A(self): self._rr(2,7)
    def LD_E_A(self): self._rr(3,7)
    def LD_H_A(self): self._rr(4,7)
    def LD_L_A(self): self._rr(5,7)
    def LD_HL_A(self):self._rr(6,7)
    def LD_B_HL(self):self._rr(0,6)
    def LD_C_HL(self):self._rr(1,6)
    def LD_D_HL(self):self._rr(2,6)
    def LD_E_HL(self):self._rr(3,6)
    def LD_H_HL(self):self._rr(4,6)
    def LD_L_HL(self):self._rr(5,6)
    def LD_H_D(self): self._rr(4,2)
    def LD_L_E(self): self._rr(5,3)
    def LD_HL_n(self,n): self.emit(0x36, n&0xFF)
    def LD_A_BC(self):  self.emit(0x0A)
    def LD_A_DE(self):  self.emit(0x1A)
    def LD_BC_A(self):  self.emit(0x02)
    def LD_DE_A(self):  self.emit(0x12)
    def LD_A_HLI(self): self.emit(0x2A)
    def LD_A_HLD(self): self.emit(0x3A)
    def LD_HLI_A(self): self.emit(0x22)
    def LD_HLD_A(self): self.emit(0x32)
    def LD_A_nn(self,nn): self.emit(0xFA, nn&0xFF, (nn>>8)&0xFF)
    def LD_nn_A(self,nn): self.emit(0xEA, nn&0xFF, (nn>>8)&0xFF)
    def LDH_n_A(self,n): self.emit(0xE0, n&0xFF)
    def LDH_A_n(self,n): self.emit(0xF0, n&0xFF)
    def LDH_C_A(self):   self.emit(0xE2)
    def LDH_A_C(self):   self.emit(0xF2)
    def INC_A(self): self.emit(0x3C)
    def INC_B(self): self.emit(0x04)
    def INC_C(self): self.emit(0x0C)
    def INC_D(self): self.emit(0x14)
    def INC_E(self): self.emit(0x1C)
    def INC_H(self): self.emit(0x24)
    def INC_L(self): self.emit(0x2C)
    def DEC_A(self): self.emit(0x3D)
    def DEC_B(self): self.emit(0x05)
    def DEC_C(self): self.emit(0x0D)
    def DEC_D(self): self.emit(0x15)
    def DEC_E(self): self.emit(0x1D)
    def DEC_H(self): self.emit(0x25)
    def DEC_L(self): self.emit(0x2D)
    def INC_BC(self): self.emit(0x03)
    def INC_DE(self): self.emit(0x13)
    def INC_HL(self): self.emit(0x23)
    def DEC_BC(self): self.emit(0x0B)
    def DEC_DE(self): self.emit(0x1B)
    def DEC_HL(self): self.emit(0x2B)
    def ADD_A_n(self,n): self.emit(0xC6, n&0xFF)
    def ADD_A_A(self): self.emit(0x87)
    def ADD_A_B(self): self.emit(0x80)
    def ADD_A_C(self): self.emit(0x81)
    def ADD_A_D(self): self.emit(0x82)
    def ADD_A_E(self): self.emit(0x83)
    def SUB_n(self,n): self.emit(0xD6, n&0xFF)
    def SUB_B(self): self.emit(0x90)
    def SUB_C(self): self.emit(0x91)
    def SUB_D(self): self.emit(0x92)
    def SUB_E(self): self.emit(0x93)
    def AND_n(self,n): self.emit(0xE6, n&0xFF)
    def AND_B(self): self.emit(0xA0)
    def AND_C(self): self.emit(0xA1)
    def AND_A(self): self.emit(0xA7)
    def OR_n(self,n): self.emit(0xF6, n&0xFF)
    def OR_B(self):  self.emit(0xB0)
    def OR_C(self):  self.emit(0xB1)
    def OR_D(self):  self.emit(0xB2)
    def OR_E(self):  self.emit(0xB3)
    def XOR_n(self,n): self.emit(0xEE, n&0xFF)
    def XOR_B(self): self.emit(0xA8)
    def CP_n(self,n): self.emit(0xFE, n&0xFF)
    def CP_B(self): self.emit(0xB8)
    def CP_C(self): self.emit(0xB9)
    def CP_D(self): self.emit(0xBA)
    def ADD_HL_BC(self): self.emit(0x09)
    def ADD_HL_DE(self): self.emit(0x19)
    def ADD_HL_HL(self): self.emit(0x29)
    def PUSH_AF(self): self.emit(0xF5)
    def PUSH_BC(self): self.emit(0xC5)
    def PUSH_DE(self): self.emit(0xD5)
    def PUSH_HL(self): self.emit(0xE5)
    def POP_AF(self):  self.emit(0xF1)
    def POP_BC(self):  self.emit(0xC1)
    def POP_DE(self):  self.emit(0xD1)
    def POP_HL(self):  self.emit(0xE1)
    def JP(self,t):    self.emit(0xC3); self._abs(t)
    def JP_Z(self,t):  self.emit(0xCA); self._abs(t)
    def JP_NZ(self,t): self.emit(0xC2); self._abs(t)
    def JP_C(self,t):  self.emit(0xDA); self._abs(t)
    def JP_NC(self,t): self.emit(0xD2); self._abs(t)
    def JP_HL(self):   self.emit(0xE9)
    def JR(self,t):    self.emit(0x18); self._rel(t)
    def JR_Z(self,t):  self.emit(0x28); self._rel(t)
    def JR_NZ(self,t): self.emit(0x20); self._rel(t)
    def JR_C(self,t):  self.emit(0x38); self._rel(t)
    def JR_NC(self,t): self.emit(0x30); self._rel(t)
    def CALL(self,t):    self.emit(0xCD); self._abs(t)
    def CALL_Z(self,t):  self.emit(0xCC); self._abs(t)
    def CALL_NZ(self,t): self.emit(0xC4); self._abs(t)
    def BIT_b_r(self,b,r): self.emit(0xCB, 0x40|(b<<3)|r)
    def BIT_b_A(self,b): self.BIT_b_r(b,7)
    def BIT_b_B(self,b): self.BIT_b_r(b,0)
    def SET_b_A(self,b): self.emit(0xCB, 0xC0|(b<<3)|7)
    def RES_b_A(self,b): self.emit(0xCB, 0x80|(b<<3)|7)
    def SWAP_A(self):    self.emit(0xCB, 0x37)
    def SWAP_B(self):    self.emit(0xCB, 0x30)
    def SRL_A(self):     self.emit(0xCB, 0x3F)
    def SRL_B(self):     self.emit(0xCB, 0x38)
    def SLA_A(self):     self.emit(0xCB, 0x27)
    def SLA_B(self):     self.emit(0xCB, 0x20)

    def resolve(self):
        for (pos, lbl, typ) in self.fixups:
            t = lbl if isinstance(lbl, int) else self.labels.get(lbl)
            if t is None: raise Exception(f"Undef '{lbl}'")
            if typ == 'abs16':
                self.data[pos] = t & 0xFF; self.data[pos+1] = (t>>8) & 0xFF
            else:
                off = t - (pos + 1)
                if not (-128 <= off <= 127):
                    raise Exception(f"JR oor '{lbl}': {off}")
                self.data[pos] = off & 0xFF

    def set_header(self, title, cart=0x03, rsize=0x00, ramsize=0x02):
        LOGO = bytes([
            0xCE,0xED,0x66,0x66,0xCC,0x0D,0x00,0x0B,0x03,0x73,0x00,0x83,
            0x00,0x0C,0x00,0x0D,0x00,0x08,0x11,0x1F,0x88,0x89,0x00,0x0E,
            0xDC,0xCC,0x6E,0xE6,0xDD,0xDD,0xD9,0x99,0xBB,0xBB,0x67,0x63,
            0x6E,0x0E,0xEC,0xCC,0xDD,0xDC,0x99,0x9F,0xBB,0xB9,0x33,0x3E,
        ])
        for i, b in enumerate(LOGO): self.data[0x104+i] = b
        for i, b in enumerate(title[:15].encode('ascii')): self.data[0x134+i] = b
        self.data[0x143]=0x80; self.data[0x144]=0x30; self.data[0x145]=0x30
        self.data[0x146]=0x00; self.data[0x147]=cart
        self.data[0x148]=rsize; self.data[0x149]=ramsize
        self.data[0x14A]=0x01; self.data[0x14B]=0x33; self.data[0x14C]=0x00
        chk = 0
        for a in range(0x134,0x14D): chk=(chk-self.data[a]-1)&0xFF
        self.data[0x14D]=chk
        gchk=0
        for i,b in enumerate(self.data):
            if i not in (0x14E,0x14F): gchk=(gchk+b)&0xFFFF
        self.data[0x14E]=(gchk>>8)&0xFF; self.data[0x14F]=gchk&0xFF
