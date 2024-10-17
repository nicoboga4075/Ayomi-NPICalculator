
class CalculatorView:
    def get_expression(self):
        return input("Enter an expression : ")

    def show_result(self, expression, result):
        print(f"{expression} = {result}")

