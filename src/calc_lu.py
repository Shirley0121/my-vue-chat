import sys
import time
import math
import re

def read_matrix_from_file(filename):
    matrix = []
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read().strip()
        
        if '[' in content:
            start = content.find('[') + 1
            end = content.rfind(']')
            matrix_content = content[start:end]
        else:
            matrix_content = content
        
        lines = matrix_content.split(';')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            line = line.replace('[', '').replace(']', '').strip()
            
            numbers = line.split()
            if numbers:
                row = []
                for num in numbers:
                    try:
                        row.append(float(num))
                    except ValueError:
                        if 'j' in num or '+' in num or '(' in num:
                            num_clean = num.replace('j', '').replace('(', '').replace(')', '')
                            if '+' in num_clean:
                                real_part, imag_part = num_clean.split('+')
                                row.append(complex(float(real_part), float(imag_part)))
                            elif '-' in num_clean and num_clean.count('-') > 1:
                                parts = num_clean.split('-')
                                if len(parts) == 3: 
                                    row.append(complex(-float(parts[1]), -float(parts[2])))
                                else:
                                    row.append(complex(float(parts[0]), -float(parts[1])))
                            else:
                                row.append(complex(float(num_clean), 0))
                        else:
                            raise ValueError(f"Не могу '{num}' в число")
                
                matrix.append(row)
        
        return matrix
    
    except Exception as e:
        print(f"Ошибка{filename}: {e}")
        sys.exit(1)

def is_square(matrix):
    """Проверка, является ли матрица квадратной"""
    n = len(matrix)
    if n == 0:
        return False
    for row in matrix:
        if len(row) != n:
            return False
    return True

def doolittle_lu(A):
    """
    LU-разложение методом Дулиттла (теорема 8.1)
    A = L * U, где L - нижняя треугольная с единицами на диагонали
    """
    n = len(A)
    L = [[0.0 for _ in range(n)] for _ in range(n)]
    U = [[0.0 for _ in range(n)] for _ in range(n)]
    
    for k in range(n):
        for j in range(k, n):
            s = 0.0
            for m in range(k):
                s += L[k][m] * U[m][j]
            U[k][j] = A[k][j] - s
        
        if abs(U[k][k]) < 1e-12:
            raise ValueError(f"не является строго регулярной. U[{k+1}][{k+1}] = {U[k][k]}")
        
        for i in range(k + 1, n):
            s = 0.0
            for m in range(k):
                s += L[i][m] * U[m][k]
            L[i][k] = (A[i][k] - s) / U[k][k]
        
        L[k][k] = 1.0
    
    return L, U

def matrix_multiply(L, U):
    """Умножение матриц L и U"""
    n = len(L)
    result = [[0.0 for _ in range(n)] for _ in range(n)]
    
    for i in range(n):
        for j in range(n):
            s = 0.0
            for k in range(n):
                s += L[i][k] * U[k][j]
            result[i][j] = s
    
    return result

def matrix_subtract(A, B):
    """Вычитание матриц: A - B"""
    n = len(A)
    result = [[0.0 for _ in range(n)] for _ in range(n)]
    
    for i in range(n):
        for j in range(n):
            result[i][j] = A[i][j] - B[i][j]
    
    return result

def frobenius_norm(matrix):
    """Вычисление нормы Фробениуса ||matrix||_E"""
    n = len(matrix)
    total = 0.0
    
    for i in range(n):
        for j in range(n):
            val = matrix[i][j]
            if isinstance(val, complex):
                total += val.real ** 2 + val.imag ** 2
            else:
                total += val ** 2
    
    return math.sqrt(total)

def write_matrix_to_file(matrix, filename):
    """Запись матрицы в файл"""
    n = len(matrix)
    
    with open(filename, 'w', encoding='utf-8') as f:
        for i in range(n):
            row_str = []
            for j in range(n):
                val = matrix[i][j]
                
                if isinstance(val, complex):
                    if abs(val.real) < 1e-15:
                        val = complex(0, val.imag)
                    if abs(val.imag) < 1e-15:
                        val = complex(val.real, 0)
                    
                    if val.imag == 0:
                        row_str.append(f"{val.real:.12f}")
                    elif val.real == 0:
                        row_str.append(f"{val.imag:.12f}j")
                    else:
                        sign = '+' if val.imag >= 0 else ''
                        row_str.append(f"{val.real:.12f}{sign}{val.imag:.12f}j")
                else:
                    if abs(val) < 1e-15:
                        val = 0.0
                    row_str.append(f"{val:.12f}")
            
            f.write(' '.join(row_str) + '\n')

def write_result_file(filename, computation_time, error):
    """Запись результатов в файл Res*.num"""
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(f"{computation_time:.6f} секунд.\n")
        f.write(f"{error:.12e}.\n")

def main():
    """Главная функция программы"""
    if len(sys.argv) != 2:
        print("Использование: python calc_lu.py <имя_файла>")
        print("Пример: python calc_lu.py Amat1.num")
        print("Пример: python calc_lu.py Amat3.num")
        sys.exit(1)
    
    input_file = sys.argv[1]
    
    print(f"Чтение матрицы из файла: {input_file}")
    
    A = read_matrix_from_file(input_file)
    
    if not is_square(A):
        print("Ошибка: матрица не является квадратной!")
        sys.exit(1)
    
    n = len(A)
    print(f"Матрица размером {n}x{n} успешно прочитана.")
    
    print("Выполнение LU-разложения...")
    try:
        start_time = time.time()
        L, U = doolittle_lu(A)
        end_time = time.time()
        computation_time = end_time - start_time
    except ValueError as e:
        print(f"Ошибка: {e}")
        sys.exit(1)
    
    print("LU-разложение успешно завершено.")
    
    print("Проверка точности разложения...")
    LU = matrix_multiply(L, U)
    diff = matrix_subtract(A, LU)
    error = frobenius_norm(diff)
    
    match = re.search(r'Amat(\d+)\.num', input_file)
    if match:
        num = match.group(1)
    else:
        num = "out"
    
    L_file = f"Lmat{num}.num"
    U_file = f"Umat{num}.num"
    Res_file = f"Res{num}.num"
    
    print(f"Запись матрицы L в файл: {L_file}")
    write_matrix_to_file(L, L_file)
    
    print(f"Запись матрицы U в файл: {U_file}")
    write_matrix_to_file(U, U_file)
    
    print(f"Запись результатов в файл: {Res_file}")
    write_result_file(Res_file, computation_time, error)
    
    print("\n" + "="*50)
    print("РЕЗУЛЬТАТЫ:")
    print("="*50)
    print(f"Время вычислений: {computation_time:.6f} секунд")
    print(f"Погрешность ||A - L*U||_E: {error:.6e}")
    
    if n <= 10:
        print("\nМатрица L (первые 5x5):")
        for i in range(min(5, n)):
            print("  ", " ".join(f"{L[i][j]:8.4f}" for j in range(min(5, n))))
        
        print("\nМатрица U (первые 5x5):")
        for i in range(min(5, n)):
            print("  ", " ".join(f"{U[i][j]:8.4f}" for j in range(min(5, n))))
    
    print(f"\nФайлы успешно созданы:")
    print(f"  • {L_file}")
    print(f"  • {U_file}")
    print(f"  • {Res_file}")
    print("="*50)

if __name__ == "__main__":
    main()