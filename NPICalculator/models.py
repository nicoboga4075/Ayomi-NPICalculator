""" Models for the app using SQLite (SQLAlchemy).

This module defines classes for basic arithmetic operations (Addition, Subtraction, etc.) 
and integrates a calculator using Reverse Polish Notation.

>>> import sqlalchemy
>>> sqlalchemy_version = sqlalchemy.__version__
>>> isinstance(sqlalchemy_version, str)
True

"""
import os
import re
from typing import Union
from sqlalchemy import Column, Integer, String, Float, create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from NPICalculator.logger import logger

# SQLAlchemy Setup
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///app.db")
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False}) # Multithreading
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Operation(Base):
    """ Represents a mathematical operation with an expression and its result.
    
    This class handles the evaluation of a RPN expression converting it into basic infix operations.
    If the computing succeeded, it is stored in the 'operation' table of the database.

    """
    __tablename__ = "operation"
    __table_args__ = {"extend_existing": True} # Enables further modifications of the structure

    id = Column(Integer, primary_key=True, index=True)
    expression = Column(String, nullable = False)
    result = Column(Float, nullable = False)

    def __init__(self, expression = None, result = None):
        """ Initializes the Operation instance with an expression
        If the result is given, it will be stored in the database (RPN expression).
        The expression is None by default to be used by subclasses.
        If the expression is given alone, it is an infix one.

        >>> op = Operation("0 + 0")
        >>> op.expression
        '0 + 0'

        """
        self.expression = expression
        self.result = result

    def infix_pattern(self):
        """ Checks if the expression matches a basic arithmetic operation: {a} {operator} {b}
        - `s*` : Matches any leading and trailing whitespace characters.
        - `([-+]?\\d+(\\.\\d+)?)` : Matches a number that can be:
            - An optional plus or minus sign `[-+]?` (to allow for positive and negative numbers).
            - One or more digits `\\d+` (to match integers).
            - An optional fractional part `(\\.\\d+)?` (to match decimals).
        - `([+\\-*/])` : Matches any of the operators: +, -, *, or /.  

        >>> op = Operation("3 + 4")
        >>> op.infix_pattern() is not None
        True

        >>> op = Operation("10.5 - 2.5")
        >>> op.infix_pattern() is not None
        True

        >>> op = Operation("-5 * -2")
        >>> op.infix_pattern() is not None
        True

        >>> op = Operation("  1.5 / 3.0  ")
        >>> op.infix_pattern() is not None
        True

        >>> op = Operation("invalid_expression")
        >>> op.infix_pattern() is None
        True

        >>> op = Operation("5 +")
        >>> op.infix_pattern() is None
        True

        >>> op = Operation("+ 5 5")
        >>> op.infix_pattern() is None
        True

        >>> op = Operation("3 ^ 4")
        >>> op.infix_pattern() is None
        True

        """
        pattern = r'^\s*([-+]?\d+(\.\d+)?)\s*([\+\-\*/])\s*([-+]?\d+(\.\d+)?)\s*$'
        return re.match(pattern, self.expression)

    @property
    def operator(self):
        """ Extracts the first operator found in the expression.

        >>> op = Operation("3 + 4")
        >>> op.operator
        '+'
        
        >>> op2 = Operation("5 - 2")
        >>> op2.operator
        '-'
        
        >>> op3 = Operation("6 * 3")
        >>> op3.operator
        '*'
        
        >>> op4 = Operation("8 / 2")
        >>> op4.operator
        '/'
        
        >>> op5 = Operation("42")
        >>> op5.operator
        ''
        """
        match = self.infix_pattern()
        return match.group(3) if match else '' # 1 & 2 for first operand, 4 & 5 for second operand

    @property
    def operation_class(self):
        """ Returns the operation class associated with the operator.

        >>> op = Operation("3 + 4")
        >>> op.operation_class
        <class 'models.Addition'>

        >>> op2 = Operation("5 - 2")
        >>> op2.operation_class
        <class 'models.Subtraction'>
        
        >>> op3 = Operation("6 * 3")
        >>> op3.operation_class
        <class 'models.Multiplication'>
        
        >>> op4 = Operation("8 / 2")
        >>> op4.operation_class
        <class 'models.Division'>
        
        >>> op5 = Operation("42")
        >>> op5.operation_class
        <class 'models.ExtraNotImplemented'>

        """
        operators = {
            '+': Addition,
            '-': Subtraction,
            '*': Multiplication,
            '/': Division
        }
        return operators.get(self.operator, ExtraNotImplemented)

    @staticmethod
    def check_number(input_calc):
        """ Checks if the input is a valid number (int, float, or string as number).

        >>> Operation.check_number(0)
        True

        >>> Operation.check_number("42")
        True

        >>> Operation.check_number("3.14")
        True

        >>> Operation.check_number("")
        False

        >>> Operation.check_number('+')
        False

        >>> Operation.check_number(3.14)
        True

        >>> Operation.check_number("abc")
        False

        >>> Operation.check_number("-42")  # Negative number as string
        True

        >>> Operation.check_number("-3.14")  # Negative decimal as string
        True

        """
        try:
            float(input_calc)
            return True
        except ValueError as _:
            return False

    def calculate(self):
        """ Calculates the result using the appropriate operation class.

        >>> op = Operation("3 + 4")
        >>> op.calculate()
        7.0

        >>> op2 = Operation("5 - 2")
        >>> op2.calculate()
        3.0

        >>> op3 = Operation("6 * 3")
        >>> op3.calculate()
        18.0

        >>> op4 = Operation("8 / 2")
        >>> op4.calculate()
        4.0

        >>> op5 = Operation("8 / 0")
        >>> op5.calculate()
        Traceback (most recent call last):
            ...
        ValueError: Division by zero

        """
        match = self.infix_pattern()
        result = None
        if match:
            a, b = match.group(1), match.group(4)
            if Operation.check_number(a) and Operation.check_number(b):
                operation_class = self.operation_class()
                # An operation of two floats return a float
                result = operation_class.calculate(float(a), float(b))
        return result

# Polymorphism

class Addition(Operation):
    """ Class for performing addition of numbers (integer or float) """
    def calculate(self, a: Union[int, float], b: Union[int, float]) -> Union[int, float]:
        """ Adds two numbers.

        >>> Addition().calculate(3, 4)
        7

        >>> Addition().calculate(3.0, 4.0)
        7.0

        """
        return a + b

class Subtraction(Operation):
    """ Class for performing subtraction of numbers (integer or float) """
    def calculate(self, a: Union[int, float], b: Union[int, float]) -> Union[int, float]:
        """ Subtracts the first number by the second.

        >>> Subtraction().calculate(5, 2)
        3

        >>> Subtraction().calculate(5.0, 2.0)
        3.0

        """
        return a - b

class Multiplication(Operation):
    """ Class for performing multiplication of numbers (integer or float) """
    def calculate(self, a: Union[int, float], b: Union[int, float]) -> Union[int, float]:
        """ Multiplies two numbers.

        >>> Multiplication().calculate(6, 3)
        18

        >>> Multiplication().calculate(6.0, 3.0)
        18.0

        """
        return a * b

class Division(Operation):
    """ Class for performing divisions of numbers (integer or float) """
    def calculate(self, a: Union[int, float], b: Union[int, float]) -> Union[int, float]:
        """ Divides the first number by the second, only if it is not zero.

        >>> Division().calculate(8, 2)
        4.0

        >>> Division().calculate(8.0, 2.0)
        4.0

        >>> Division().calculate(8, 0)
        Traceback (most recent call last):
            ...
        ValueError: Division by zero

        >>> Division().calculate(8.0, 0.0)
        Traceback (most recent call last):
            ...
        ValueError: Division by zero

        """
        if b == 0:
            raise ValueError("Division by zero")
        return a / b

class ExtraNotImplemented(Operation):
    """ Class for performing extra operations (not implemented) """
    def calculate(self, a: Union[int, float], b: Union[int, float]) -> Union[int, float]:
        """ Manages extra operations (other than basic ones).
        
        >>> ExtraNotImplemented().calculate(0, 0)
        Traceback (most recent call last):
            ...
        ValueError: Invalid operation : operator not found

        """
        raise ValueError("Invalid operation : operator not found")

class Calculator:
    """ A simple calculator for evaluating expressions in Reverse Polish Notation (RPN) """

    def __init__(self):
        """ Initializes a calculator with a stack : LIFO (Last In, First Out) implementation
            
        >>> calc = Calculator()
        >>> calc.stack
        []

        """
        self.stack = []

    def compute(self, expression):
        """ Evaluates a RPN expression and returns the result.

        >>> calc = Calculator()
        >>> calc.compute("3 4 + 2 *")  # (3 + 4) * 2
        14.0

        >>> calc.compute("10 2 / 3 +")  # (10 / 2) + 3
        8.0

        >>> calc.compute("5 6 - 2 *")  # (5 - 6) * 2
        -2.0

        >>> calc.compute("-5.5 -2.5 +") # -5.5 + (-2.5)
        -8.0

        >>> calc.compute("-10 -2 *") # (-10) * (-2)
        20.0

        >>> calc.compute("+0 +0 -") # 0 - 0
        0.0

        >>> calc.compute("0 0 +") # 0 + 0
        0.0

        >>> calc.compute("8 0 /") # Division by zero
        Traceback (most recent call last):
            ...
        ValueError: Division by zero
        
        """
        logger.info("Expression to compute : '%s'", expression)
        self.stack.clear()  # Resets stack for each new expression
        logger.info("Initial stack : %s", self.stack)

        for o in expression.split():
            logger.info("Expression token : %s", o)
            if Operation.check_number(o):
                # Adds the operand to the stack
                self.stack.append(float(o))
                logger.info("Added number : %s, stack : %s", float(o), self.stack)
            else:
                # Operator encountered, pops two operands from the stack
                if len(self.stack) < 2:
                    raise ValueError("Invalid expression : insufficient operands for the operation")
                b = self.stack.pop()
                a = self.stack.pop()
                logger.info("Popped operands : %s, %s, stack : %s", a, b, self.stack)
                # Creates the operation instance and calculate
                operation = Operation(expression=f"{a} {o} {b}")
                result = operation.calculate()
                self.stack.append(result)
                logger.info("TEMP : %s %s %s = %s, stack : %s", a, o, b, result, self.stack)

        # Final result should be the only item left in the stack
        logger.info("Final stack : %s", self.stack)
        if len(self.stack) == 1:
            return self.stack.pop()
         # If there are multiple items left, the expression was incomplete
        raise ValueError("Invalid expression : too many operands")
    def save(self, op, db):
        """ Attempts to save an operation in the database"""
        db_error = None
        try:
            db.add(op)
            db.commit()  # Commits to save the operation (expression and result)
        except SQLAlchemyError as sqlae:
            db_error = sqlae
            db.rollback()  # Rollbacks in case of failure
        finally:
            if db_error is None:
                logger.info("Operation saved in database.")

# Creation of tables that match classes inherited from Base, above this line ('operation')
Base.metadata.create_all(bind=engine)
