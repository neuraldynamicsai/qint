# Quantized Integer Operations (QInt) Library
The Quantized Integer Operations (QInt) library is a Python package for performing arithmetic operations on quantized integers. It allows for exact arithmetic calculations while working with numbers that have been quantized for precision. This library is particularly useful when dealing with numerical computations that require high precision.

## About
Quantized Integers (QInt) are a specialized numeric data type that represents integers with a defined level of precision. In simple terms, a quantized integer consists of two components:
1. Value: This is the integer value you want to represent.
2. Precision: This is the number of decimal places to which the integer value is quantized.
For example, if you have a value of 123 and a precision of 2, it means that you are representing the number 123 as 1.23 with two decimal places of precision. Quantized integers allow you to work with exact fractional values while maintaining control over precision.

### Why are Quantized Integers Important?
#### 1. Precision Control
Quantized integers provide precise control over the level of precision in numeric calculations. In contrast to floating-point numbers, which have limited precision and may introduce rounding errors, quantized integers enable exact arithmetic operations. This makes them essential for applications where precision is critical, such as financial calculations, scientific simulations, and engineering designs.
#### 2. Avoiding Floating-Point Errors
Floating-point arithmetic in traditional programming languages (e.g., Python's float) can result in unexpected errors due to the inherent limitations of floating-point representations. Quantized integers eliminate these errors by representing values as scaled integers, ensuring that calculations are performed exactly as intended.
#### 3. Deterministic Results
Quantized integers offer deterministic results in computations. This means that the same operations performed on quantized integers will always yield the same results, regardless of the platform or environment. This determinism is crucial in applications like cryptography, where consistent results are essential.
#### 4. Compatibility with Integer Operations
Despite their fractional representation, quantized integers can seamlessly interact with regular integer operations, making them versatile for various use cases. You can add, subtract, multiply, divide, and perform other standard mathematical operations on quantized integers just like regular integers.

### When Should I Use Quantized Integers?
Quantized integers are particularly valuable in scenarios where precision matters and floating-point inaccuracies can lead to significant problems. Consider using quantized integers in the following situations:
- Financial Calculations: Precise monetary calculations require exact representation of decimal values to avoid rounding errors.
- Scientific Research: In scientific simulations and experiments, maintaining precision is crucial for accurate results.
- Control Systems: Systems that rely on precise numeric values, such as robotics and automation, benefit from deterministic calculations.
- Cryptography: Cryptographic algorithms demand exact results to ensure the security and reliability of the system.

## Installation
You can install the library using pip like so:
```bash
pip install qint
```

## Usage
To use the QInt library, you first need to import the necessary modules:
```python
from qint import qint
```

### Creating a Quantized Integer
You can create a quantized integer using the QInt class. Quantized integers are represented by two attributes: value and precision, where value is the quantized integer value and precision is the precision of the quantized value.
```python
# Create a QInt with a value of 123 and precision of 2
qint = QInt(123, 2)
```
If you instead want to create a QInt based on an actual float or integer value at a given precision, instead call the static create method:
```python
# Create a QInt with a value of 147 and a precision of 2
qint = QInt.create(1.47, 2)
```

### Arithmetic Operations
QInt supports various arithmetic operations, including addition, subtraction, multiplication, division, and more.
It is worth noting that addition and subtraction can be performed either with another QInt, or with an integer. If done with an integer, it is treated with the implied precision. For example:
```python
q1 = QInt.create(4.00, 2)
q2 = QInt.create(4.00, 2)
q3 = q1 + q2 # QInt(800, 2)
q4 = q1 + 4 # QInt(800, 2)
```
In addition to integers and QInts, multiplication and division can also be performed with python `Fraction` objects (from the standard `fractions` library):
```python
from fractions import Fraction

q1 = QInt.create(4.00, 2)
q2 = QInt.create(4.00, 2)
q3 = q1 + q2 # QInt(1600, 2)
q4 = q1 * 4 # QInt(1600, 2)
q5 = q1 * Fraction(1, 2) # QInt(200, 2)
```

### Comparison Operations
You can also compare QInt instances using standard comparison operators like ==, !=, <, <=, >, and >=.
```python
qint1 = QInt(100, 2)
qint2 = QInt(200, 2)

if qint1 < qint2:
    print("qint1 is less than qint2")
```

### Safe Arithmetic - QInts with Different Precisions
QInts are designed to throw an error when attempting to perform operations at different precisions. This is by design to ensure careful usage and ensure uniformity. However, if you wish to perform arithmetic, there are also "safe" methods which allow you to operate on QInts with different precisions. These must be explicitly called as follows, and always return a QInt with the greater precision of the two being operated on:
```python
q1 = QInt(400, 2)
q2 = QInt(4000, 3)
q3 = q1 + q2 # Precision error
q4 = q1.add(q2) # QInt(8000, 3)
```

## Speed
Making efficient calculations with quanitzed integers is a top priority! Speed tests and improvements are coming soon!

## Contributing
We welcome contributions to the QInt library. If you find a bug or have an idea for an enhancement, please open an issue or submit a pull request on the GitHub repository.

## License
This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments
We would like to thank the open-source community for their contributions and support in making the QInt library possible.
