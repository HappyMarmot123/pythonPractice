def add(a, b):
    return a + b

def subtract(a, b):
    return a - b

def multiply(a, b):
    return a * b

def divide(a, b):
    if b == 0:
        return "0으로 나눌 수 없습니다."
    return a / b

def calculator():
    print("--- 간단한 미니 계산기 ---")
    print("사용 가능한 연산: +, -, *, /")
    print("종료하려면 'q'를 입력하세요.")
    print("--------------------------")

    while True:
        try:
            num1_input = input("첫 번째 숫자를 입력하세요: ")
            if num1_input.lower() == 'q':
                break
            num1 = float(num1_input)

            operator = input("연산자를 입력하세요 (+, -, *, /):")
            if operator.lower() == 'q':
                break
            if operator not in ['+', '-', '*', '/']:
                print("잘못된 연산자입니다. 다시 입력하세요.")
                continue

            num2_input = input("두 번째 숫자를 입력하세요: ")
            if num2_input.lower() == 'q':
                break
            num2 = float(num2_input)

        except ValueError:
            print("❌ 유효한 숫자를 입력하세요.")
            continue

        result = None
        if operator == '+':
            result = add(num1, num2)
        elif operator == '-':
            result = subtract(num1, num2)
        elif operator == '*':
            result = multiply(num1, num2)
        elif operator == '/':
            result = divide(num1, num2)

        print(f"\n결과: {num1} {operator} {num2} = {result}\n")
        print("--------------------------")
        
if __name__ == "__main__":
    calculator()