import sys
import random
from copy import deepcopy

def LeiaMatrizLocal(NomeArquivo):
    """
    Lê um arquivo texto com 9 linhas e 9 inteiros separados por espaços.
    Retorna a matriz 9x9 (lista de listas de int) ou [] em caso de erro.
    """
    try:
        arq = open(NomeArquivo, "r")
    except Exception as e:
        print(f"Erro abrindo arquivo '{NomeArquivo}': {e}")
        return []

    mat = []
    try:
        for linha in arq:
            linha = linha.strip()
            if linha == "":
                continue
            v = linha.split()
            if len(v) != 9:
                print(f"Formato incorreto: linha com {len(v)} elementos (esperado 9).")
                arq.close()
                return []
            # converter para int e verificar 0..9
            try:
                row = [int(x) for x in v]
            except:
                print("Erro: elementos não são inteiros.")
                arq.close()
                return []
            for x in row:
                if x < 0 or x > 9:
                    print("Erro: elemento fora do intervalo 0..9.")
                    arq.close()
                    return []
            mat.append(row)
        if len(mat) != 9:
            print(f"Formato incorreto: arquivo tem {len(mat)} linhas (esperado 9).")
            arq.close()
            return []
    finally:
        arq.close()

    # matriz lida
    return mat

def imprime_matriz(mat, titulo=None):
    if titulo:
        print(titulo)
        print()
    for i in range(9):
        linha = ""
        for j in range(9):
            linha += f"{mat[i][j]:>2}  "
        print(linha)
    print()

def TestaMatrizSudoku(matriz):
    """
    Recebe matriz 9x9 totalmente preenchida (valores 1 a 9).
    Retorna True se linhas, colunas e quadrados 3x3 contiverem todos os dígitos 1 a 9 sem repetição.
    """
    # checar linhas
    for i in range(9):
        row = matriz[i]
        if sorted(row) != list(range(1,10)):
            return False

    # checar colunas
    for j in range(9):
        col = [matriz[i][j] for i in range(9)]
        if sorted(col) != list(range(1,10)):
            return False

    # checar quadrantes
    for bi in range(3):
        for bj in range(3):
            block = []
            for i in range(bi*3, bi*3+3):
                for j in range(bj*3, bj*3+3):
                    block.append(matriz[i][j])
            if sorted(block) != list(range(1,10)):
                return False

    return True

def possiveis(matriz, linha, coluna):
    """Retorna uma lista de candidatos válidos (1..9) para posição vazia (linha,coluna)."""
    if matriz[linha][coluna] != 0:
        return []

    usados = set()

    # linha
    usados.update(matriz[linha])

    # coluna
    usados.update(matriz[r][coluna] for r in range(9))

    # bloco 3x3
    bi = (linha // 3) * 3
    bj = (coluna // 3) * 3
    for i in range(bi, bi+3):
        for j in range(bj, bj+3):
            usados.add(matriz[i][j])

    candidatos = [d for d in range(1,10) if d not in usados]
    return candidatos

def encontra_vazio(matriz, start_i=0, start_j=0):
    """
    Encontra a próxima posição vazia (valor 0) percorrendo linhas e colunas
    a partir do início da matriz. Retorna (i,j) ou None se não houver vazio.
    """
    for i in range(9):
        for j in range(9):
            if matriz[i][j] == 0:
                return (i, j)
    return None

def Sudoku(matriz, limite_sol=0):
    """
    Encontra todas as soluções para 'matriz' parcial (com zeros como vazios).
    - limite_sol: 0 = sem limite (encontra todas), n>0 = para após encontrar n soluções.
    Retorna lista de matrizes-solução (cada uma 9x9).
    """
    soluções = []

    def backtrack(m):
        # encontrar vazio
        v = encontra_vazio(m)
        if v is None:
            # matriz completa -> testar consistência
            if TestaMatrizSudoku(m):
                soluções.append(deepcopy(m))
            return

        i, j = v
        cand = possiveis(m, i, j)
        # tentativa dos candidatos
        for val in cand:
            m[i][j] = val
            backtrack(m)
            if limite_sol > 0 and len(soluções) >= limite_sol:
                m[i][j] = 0
                return
            m[i][j] = 0  # desfaz
        # se não houver candidatos, somente retorna (backtrack automático)

    mat_copy = deepcopy(matriz)
    backtrack(mat_copy)
    return soluções

def GeraMatrizSudoku(npp, tentativas_max=10000):
    """
    Gera uma matriz 9x9 com exatamente npp posições preenchidas de forma consistente.
    Retorna matriz (pode demorar se npp for grande); tenta até tentativas_max reinícios.
    """
    if npp < 0 or npp > 81:
        raise ValueError("npp deve estar entre 0 e 81")

    for tentativa in range(tentativas_max):
        mat = [[0]*9 for _ in range(9)]
        # escolha npp posições distintas
        posicoes = random.sample([(i,j) for i in range(9) for j in range(9)], npp)
        ok = True
        for (i,j) in posicoes:
            # tentamos colocar um número aleatório 1..9 que mantenha consistência local
            candidatos = list(range(1,10))
            random.shuffle(candidatos)
            colocado = False
            for val in candidatos:
                # checa se colocar val em (i,j) mantém linha/col/bloco sem repetição
                conflict = False
                # linha
                if val in mat[i]:
                    conflict = True
                # coluna
                if any(mat[r][j] == val for r in range(9)):
                    conflict = True
                # bloco
                bi = (i // 3) * 3
                bj = (j // 3) * 3
                for ii in range(bi, bi+3):
                    for jj in range(bj, bj+3):
                        if mat[ii][jj] == val:
                            conflict = True
                            break
                    if conflict:
                        break
                if not conflict:
                    mat[i][j] = val
                    colocado = True
                    break
            if not colocado:
                ok = False
                break
        if ok:
            # verificação extra: as células preenchidas não violam regras locais, já garantido
            return mat
        # senão, tentar de novo
    raise RuntimeError(f"Não foi possível gerar matriz consistente com {npp} posições após {tentativas_max} tentativas.")

def main():
    print("Sudoku - Gera e resolve (digite 'fim' para sair).")
    while True:
        ent = input("Entre com o número de posições a preencher inicialmente (0..81) ou 'fim': ").strip()
        if ent.lower() == "fim":
            print("Encerrando.")
            break
        try:
            npp = int(ent)
        except:
            print("Entrada inválida. Digite um inteiro entre 0 e 81 ou 'fim'.")
            continue
        if npp < 0 or npp > 81:
            print("Número fora do intervalo 0..81.")
            continue

        # gerar matriz
        try:
            matriz = GeraMatrizSudoku(npp)
        except Exception as e:
            print("Erro ao gerar matriz:", e)
            continue

        print("\n* * * Matriz inicial\n")
        imprime_matriz(matriz)

        # limite de soluções (ex.: parar após 20 soluções para não inundar)
        limite = 20
        print(f"Procurando soluções (limite de exibição = {limite}) ...")
        solucoes = Sudoku(matriz, limite_sol=limite)
        if len(solucoes) == 0:
            print("\nNenhuma solução encontrada.\n")
        else:
            for idx, sol in enumerate(solucoes, start=1):
                imprime_matriz(sol, titulo=f"* * * Matriz Completa – Solução {idx}\n")
                # checagens e prints similares ao enunciado
                linhas_ok = all(sorted(sol[i]) == list(range(1,10)) for i in range(9))
                colunas_ok = all(sorted([sol[r][c] for r in range(9)]) == list(range(1,10)) for c in range(9))
                quadrados_ok = True
                for bi in range(3):
                    for bj in range(3):
                        block = []
                        for i in range(bi*3, bi*3+3):
                            for j in range(bj*3, bj*3+3):
                                block.append(sol[i][j])
                        if sorted(block) != list(range(1,10)):
                            quadrados_ok = False
                print("linhas OK " + ("* * * * * *" if linhas_ok else "ERRO"))
                print("colunas OK " + ("* * * * * *" if colunas_ok else "ERRO"))
                print("quadrados OK " + ("* * * * * *" if quadrados_ok else "ERRO"))
                print("* * * Matriz Completa e Consistente\n")

            if len(solucoes) >= limite:
                print("* * * Há mais soluções (parado no limite)\n")

        # volta ao início do loop

if __name__ == "__main__":
    main()