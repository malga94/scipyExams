sympyExams is a Python module that uses sympy to generate math questions on topics such as solving trig equations, derivatives and integrals. 
The user chooses the kinds of functions to be included in the question sheet, such as polynomials, trig, rational etc. Then one or more topics need to be chosen (integration, derivatives...). 
Finally, the code generates a pdf file with random questions about the chosen topics.

The generation of the functions/expressions that will be included in the question sheet, and the creation of the question sheet + answers are handled by two different classes: the first by FunctionGenerator and the second by RandomArticle. Here is some example code, to generate questions about integration of polynomial functions

```
from sympyExams import FunctionGenerator, RandomArticle

#Takes one positional argument of type list
x = FunctionGenerator(['polynomial'])

#Here we generate 10 random polynomials by calling the generate method. 

#This method returns a list of sympy objects (the functions), and a list containing the type 
#of functions (in this case, only polynomials)

functions, _ = x.generate(10)

#Now we create an instance of the RandomArticle class, passing the functions and the type of exercises we want (for example integration) as a list
#The cheatsheet method generates the .tex file containing the questions and answers. The to_pdf method converts this file to PDF, provided that pdfTeX is installed on the machine

exam_sheet = RandomArticle(functions, ['Integration'])
exam.cheatsheet()
exam.to_pdf()
```
For now, the following math functions are implemented:
1. "trig" : trigonometric functions (sin(x), cos(x), tan(x)). Will generate a linear combination of some of these, including squares of any of the trig functions. 
2. "polynomial" : generates a polynomial of degree <= 4
3. "polyrational" : generates a rational function f(x)/g(x), where f and g are polynomials of degree <= 4

And the following topics:
1. "Integration" 
2. "Differentiation"
3. "SolveAlgebraic" : questions where you have to solve f(x) = 0 for one of the function types explained above

**The FunctionGenerator class takes the following keyword arguments:**

max_power=int -> Determines the maximum power appearing in the function. Default is 4

max_coeff=int -> Determines the largest coefficient of the powers of x in the polynomial and rational polynomial functions. Default is 9

include_special_trig = Bool -> Whether to include inverse trig functions arcsin(x), arccos(x), arctan(x) and reciprocal trig functions sec(x), csc(x), cot(x). Default is False

**The RandomArticle class takes the following keyword arguments:**

ftypes = list -> Optionally, one can pass the second return value of the FunctionGenerator.generate() method. It allows the code to discard integrals which are not solvable analytically

number_of_questions = int -> Some of the random functions generated might be too complicated and the code will discard them. This leads to sometimes having a different number of questions in the question sheet than specified in the FunctionGenerator.generate() method. Use this argument to force the number of questions to int, provided that you have generated enough questions

filename = str -> The filename of the question sheet, which will be generated in the current directory as str.tex. Default is questions

