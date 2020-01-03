#coding:utf-8

import os
import sys

def DelComment(src, dst): 

    fSrc = open(src, 'rb')
    fDst = open(dst, 'wb')
      
    out = []

    STATE_NORMAL            = 0
    STATE_BEGIN             = 1
    STATE_LINE_COMMENT      = 2
    STATE_BLOCK_COMMENT     = 3
    STATE_END               = 4

    State = STATE_NORMAL
    
    while 1:
        ReadInChar = fSrc.read(1)

        if ReadInChar == '':
            break
        if State == STATE_NORMAL:
            if ReadInChar == '/':
                State = STATE_BEGIN
            else:
                out.append(ReadInChar)
        elif State == STATE_BEGIN:
            if ReadInChar == '/':
                State = STATE_LINE_COMMENT
            elif ReadInChar == '*':
                State = STATE_BLOCK_COMMENT
            else:
                State = STATE_NORMAL
                out.append('/'+ReadInChar)
        elif State == STATE_LINE_COMMENT:
            if ReadInChar == '\n':
                State = STATE_NORMAL
        elif State == STATE_BLOCK_COMMENT:
            if ReadInChar == '*':
                State = STATE_END
        elif State == STATE_END:
            if ReadInChar == '/':
                State = STATE_NORMAL
                ReadInChar = fSrc.read(1)
                while ReadInChar == '\r' or ReadInChar == '\n':
                    ReadInChar = fSrc.read(1)
                fSrc.seek(-1, 1)
            else:
                State = STATE_BLOCK_COMMENT
                fSrc.seek(-1, 1)
    
    fDst.writelines(out)
    fDst.flush()
    fDst.close()
    fSrc.close()