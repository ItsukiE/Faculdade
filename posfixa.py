import re

def prioridade(x):
    if x == '+' or x == '-':
        return 1
    if x == '*' or x == '/':
        return 2
    if x == '#' or x == '_':
        return 3
    if x == '**':
        return 4
    if x == '(':
        return 5
    if x == ')':
        return 6
    return 0


class Complexo:
    def __init__ (self,comp=(0.0,0.0)):
        if type(comp) is not tuple:
            raise TypeError ('Complexo deve ser tupla')
        if (type(comp[0]),type(comp[1])) != (float,float):
            raise TypeError ('Complexo com elemento diferente de float')
        self.comp=(comp[0],comp[1])

    def __getitem__(self, key):
        return self.comp[key]

    def __add__ (comp1,comp2):
        return Complexo((comp1[0]+comp2[0],comp1[1]+comp2[1]))

    def __sub__ (comp1,comp2):
        return Complexo((comp1[0]-comp2[0],comp1[1]-comp2[1]))

    def __mul__ (comp1,comp2):
        return Complexo((comp1[0]*comp2[0]-comp1[1]*comp2[1],comp1[0]*comp2[1]+comp1[1]*comp2[0]))

    def __truediv__(comp1, comp2):
        denom = comp2[0]**2 + comp2[1]**2
        if denom == 0:
            raise ZeroDivisionError("Divisão por zero")
        real = (comp1[0] * comp2[0] + comp1[1] * comp2[1]) / denom
        imag = (comp1[1] * comp2[0] - comp1[0] * comp2[1]) / denom
        return Complexo((real, imag))

    def __pos__(comp):
        return Complexo((+comp[0], +comp[1]))

    def __neg__(comp):
        return Complexo((-comp[0], -comp[1]))

    def __str__ (comp):
        sinal='+' if comp[1]>=0 else ''
        return '('+str(comp[0])+' '+sinal+str(comp[1])+'i)'

    def __repr__(comp):
        return comp.__str__()


class Pilha:
    def __init__(self):
        self._pilha = []
    def __len__ (self):
        return len(self._pilha)
    def is_empty(self):
        return len(self) == 0
    def push(self, e):
        self._pilha.append(e)
    def top(self):
        if self.is_empty( ):
            raise IndexError("Pilha vazia")
        return self._pilha[-1]
    def pop(self):
        if self.is_empty( ):
            raise IndexError("Pilha vazia")
        return self._pilha.pop( )
    def __str__(self):
        txt = ''
        for i, x in enumerate(self._pilha):
            txt += str(i) + ' ' + str(x) + '\n'
        return txt


def TraduzPosFixa(exp):
    exp = exp.replace('–', '-')
    r = re.findall(r"(\b\d*[\.]?\d+[i]?\b|[\(\)\+\*\-\/\%])", exp)
    for k in range(len(r)):
        if r[k][-1]=='i':
            r[k]=r[k][:-1]
        try: int(r[k][-1])
        except: continue
        else: r[k]=float(r[k])
    for k in range(1,len(r)):
        if r[k]=='-' and type(r[k+1]) == float:
            r[k+1]*=-1
    n=1
    while n < len(r):
        if r[n] in ('+','-') and (type(r[n-1]),type(r[n+1])) == (float,float):
            del r[n]
        n+=1
    n=1
    while n < len(r):
        if r[n] in ('+','-') and (type(r[n+1]),type(r[n+2])) == (float,float):
            del r[n]
        n+=1
    n=1
    while n <= len(r)-2:
        if (type(r[n]),type(r[n+1])) == (float,float):
            r[n-1]=(r[n],r[n+1])
            del r[n:n+3]
        else: n+=1
    if r[0] in ('+','-'):
        if r[0]=='+': r[0]='#'
        else: r[0]='_'
    for k in range (len(r)):
        if r[k] in ('+','-') and (type(r[k-1]),type(r[k+1])) != (tuple,tuple):
            if r[k]=='+': r[k]='#'
            else: r[k]='_'
    for k in range(len(r)):
        if type(r[k])==tuple:
            r[k]=Complexo(r[k])
    def Traduzir(r_interno):
        operadores = Pilha()
        saida = []
        for k in r_interno:
            if type(k) is Complexo:
                saida.append(k)
            elif k == '(':
                operadores.push(k)
            elif k == ')':
                while not operadores.is_empty() and operadores.top() != '(':
                    saida.append(operadores.pop())
                operadores.pop()
            else:
                while (not operadores.is_empty() and prioridade(operadores.top()) >= prioridade(k) and operadores.top() != '('):
                    saida.append(operadores.pop())
                operadores.push(k)
        while not operadores.is_empty():
            saida.append(operadores.pop())
        return saida
    lista_final = Traduzir(r)
    return lista_final


def CalcPosFixa(listaexp):
    operandos = Pilha()
    if listaexp is None:
        return None

    for token in listaexp:
        if type(token) is tuple:
            token = Complexo(token)

        if type(token) is Complexo:
            operandos.push(token)

        if token in ('+', '-', '*', '/'):
            if len(operandos) < 2: return None
            op2 = operandos.pop()
            op1 = operandos.pop()
            if token == '+': resultado = op1 + op2
            if token == '-': resultado = op1 - op2
            if token == '*': resultado = op1 * op2
            if token == '/':
                if op2[0] == 0.0 and op2[1] == 0.0: return None
                resultado = op1 / op2
            operandos.push(resultado)

        if token in ('#', '_'):
            if len(operandos) < 1: return None
            op = operandos.pop()
            if token == '#': resultado = +op
            if token == '_': resultado = -op
            operandos.push(resultado)

    if len(operandos) == 1:
        resultado_final = operandos.pop()
        return resultado_final
    else:
        return None
    
if __name__ == "__main__":
    import ast

    print("Interpretador de Expressões com Números Complexos")
    print("Digite 'fim' para sair.")
    
    while True:
        try:
            entrada_completa = input(">>> ")
            if entrada_completa.strip().lower() == "fim":
                break
            
            if not entrada_completa:
                continue

            
            valor_str = entrada_completa 
            
            if '=' in entrada_completa:
                valor_str = entrada_completa.split('=', 1)[1].strip()

            resultado = None
            
            try:
                objeto_real = ast.literal_eval(valor_str)
            except (ValueError, SyntaxError):
                objeto_real = valor_str

            if isinstance(objeto_real, list):
                resultado = CalcPosFixa(objeto_real)
            
            elif isinstance(objeto_real, str):
                lista_posfixa = TraduzPosFixa(objeto_real)
                print("Pós-fixa:", lista_posfixa)
                resultado = CalcPosFixa(lista_posfixa)

            if resultado is None:
                print("Erro na expressão.")
            else:
                print("Resultado:", resultado)

        except Exception as e:
            print(f"Ocorreu um erro inesperado: {e}")