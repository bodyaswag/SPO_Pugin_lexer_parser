import re
import sys
from lexer_def import token_exprs

def lex(characters, token_exprs):
    tokens = []
    pos = 0
    while pos < len(characters):
        match = None
        for token_expr in token_exprs:
            #извлекаем данные из кортежа лексемы
            pattern, tag, priority = token_expr
            regex = re.compile(pattern)
            match = regex.match(characters, pos)
            if match:
                lexem = match.group(0)
                if tag:
                    token = (lexem.replace('"',''), tag, priority)
                    tokens.append(token)
                break
        if not match:
            print("Wrong character '" + str(characters[pos]) + "'")
            return(tokens)
            sys.exit(0)
        else:
            pos = match.end(0)
    return tokens

def do_lex(chars):
    return lex(chars, token_exprs)
