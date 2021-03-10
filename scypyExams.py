#TODO:
# Write README and manual
# Solve issue with saving date on the log file of pdflatex
# Solve issue with polyrational not having a constant term (only terms from x^1 upwards)
# Test functionality for solving equations, and add proper latex formatting

import sympy as sp
import numpy as np

supported_ftype = {'Rational': ['rational'],
						'Polynomial': ['poly', 'polynomial'],
						'Rational Polynomial': ['polyrational'],
						'Trigonometric': ['trig, trigonometric'] #TODO
	}
	
x = sp.symbols('x')

#A class to generate random mathematical functions
class FunctionGenerator:

	functions = ['sin(&)', 'cos(&)', 'exp(&)']
	poly_functions = ['&']
	symbols_for_rational = ['+', '-', '*']

	def __init__(self, func_type, max_nesting=1, max_power=4, max_terms=3, max_coeff=9):
		self.ftype = func_type
		if not self.check_ftype():
			s = []
			for i in supported_ftype.keys():
				for x in supported_ftype[i]:
					s.append(x)
					s.append(', ')

			options = ''.join(s)
			raise ValueError(f"FunctionGenerator(str): str must be one of the following: {options}")

		self.max_nesting = max_nesting

		self.max_power = max_power
		for i in range(2, self.max_power + 1):
			self.functions.append(f'&**{str(i)}')
			self.poly_functions.append(f'&**{str(i)}')

		self.max_terms = max_terms
		if self.ftype.lower() in supported_ftype['Rational Polynomial']:
			if self.max_terms > self.max_power:
				raise ValueError('Keyword argument max_power must be greater or equal to max_terms for the func_type "polyrational"')

		self.max_coeff = max_coeff

	def check_ftype(self):

		valid = False
		for i in supported_ftype.keys():
			if self.ftype.lower() in supported_ftype[i]:
				valid = True

		return valid

	def rand_function(self, l):
		
		selection = np.random.randint(0, len(l))
		function = l[selection]
		if '&' in function:
			coefficient = np.random.randint(1, self.max_coeff + 1)
			function = str(coefficient) + '*' + function

		return function

	def generate_single_expression(self):

		#Method to generate a random mathematical function f(x)
		nest = self.max_nesting - 1

		if self.ftype.lower() in ['rational', 'polyrational']:
			#In this block I wrote the code to generate a random RATIONAL function f(x)/g(x). For polyrational, both f and g are polynomials of degree <= self.max_power. Otherwise they are 
			#combinations of elementary functions cos(x), sin(x), e^(x), log(x)
			if self.ftype.lower() in supported_ftype['Rational']:
				poly = False
				functions = self.functions.copy()
				symbols = self.symbols_for_rational.copy()
			else:
				poly = True
				functions = self.poly_functions.copy()
				symbols = self.symbols_for_rational.copy()
				symbols.remove('*')
				#No need for composite functions when we deal only with polynomials
				nest = 0

			numerator_terms = np.random.randint(1,self.max_terms + 1)
			denominator_terms = np.random.randint(1,self.max_terms + 1)
			numerator = ''
			denominator = ''

			while numerator_terms > 0:
				f = self.rand_function(functions)
				numerator += f
				#For the polynomial case, we don't want same powers to appear twice, as they would simply be summed together. We want all different powers
				if poly:
					functions.remove(f[2:])
				if numerator_terms > 1:
					numerator += self.rand_function(symbols)
				numerator_terms -= 1

			if not poly:
				functions = self.functions.copy()
			else:
				functions = self.poly_functions.copy()

			while denominator_terms > 0:
				f = self.rand_function(functions)
				denominator += f
				if poly:
					functions.remove(f[2:])
				if denominator_terms > 1:
					denominator += self.rand_function(symbols)
				denominator_terms -= 1
			#print(f"Numerator: {numerator}, Denominator: {denominator}")
			
			str_expression = '(' + numerator + ')/(' + denominator + ')'

			while nest > 0:
				variable_num = str_expression.count('&')
				for i in range(0, variable_num):
					r = self.rand_function(functions)
					str_expression = str_expression.replace('&', r, i)
				nest -= 1

			str_expression = str_expression.replace('&', 'x')
			expression = sp.sympify(str_expression)

		if self.ftype.lower() in supported_ftype['Polynomial']:
			polynomial = Polynomial(self.max_power, self.max_coeff)
			expression = polynomial.generate_polynomial()

		return (expression, self.ftype.lower())

	def generate(self, n=1):

		#Generating n random functions, as requested by the user. This is the method that should most often be called on a FunctionGenerator object
		questions = []
		if n <= 0:
			raise ValueError("generate(int): argument 1 must be > 0 ")
		for i in range(n):
			expression = self.generate_single_expression()
			questions.append(expression[0])

		function_type = expression[1]

		return questions, function_type

#Class to generate a polynomial in sympy
class Polynomial:

	symbols = ['+', '-']

	def __init__(self, max_power=2, max_coeff=10):
		self.max_power = max_power
		self.max_coeff = max_coeff

	def generate_str_polynomial(self):
		#Here the code to generate a random polynomial of degree <= self.max_power
		powers_of_x = []
		for i in range(self.max_power, 1, -1):
			powers_of_x.append(f'x**{i}')
		powers_of_x.append('x')
		symbols_poly = self.symbols

		coeff = np.random.randint(1, self.max_coeff + 1, self.max_power + 1)
		symbols = np.random.randint(0, len(symbols_poly), self.max_power)
		str_expression = ''
		for cont, c in enumerate(coeff[:-1]):
			
			str_expression = str_expression + str(c) + '*' + powers_of_x[cont] + symbols_poly[symbols[cont]]

		str_expression += str(coeff[-1])

		return str_expression

	def generate_polynomial(self):

		s = self.generate_str_polynomial()
		expression = sp.sympify(s)
		return expression

#An object that takes the random f(x)'s created with FunctionGenerator, and creates a question sheet on a topic chosen by the user (e.g integration) with answers, computed using sympy
class RandomArticle:

	#Maximum length (as in len(str)) of the answer to a question, to avoid crazy integrals and derivatives which no human would ever find useful to compute by hand
	ans_length = 40
	implemented_topics = ['Integration', 'Differentiation', 'SolveAlgebraic']

	def __init__(self, questions, topics, func_type, number_of_questions=0, filename="questions"):
		self.q = questions
		self.topics = []
		for t in topics:
			if t not in self.implemented_topics:
				raise ValueError(f"Topic {t} does not exist. See the documentation for the list of topics")
		x = topics[0]
		for i in range(len(self.q)):
			if len(topics) > 1:
				self.topics.append(choose_random_topic(topics))
			else:
				self.topics.append(x)

		self.ftype = func_type

		self.answers = self.answer()
		if number_of_questions > len(self.q):
			print(f"WARNING: Not enough questions provided to generate {number_of_questions} questions. Only {len(self.q)} can be generated")
		elif number_of_questions == 0:
			pass
		else:
			self.q = self.q[:number_of_questions]

		self.filename = filename
		if len(filename.split('.')) > 1:
			raise ValueError("to_pdf(str): str must not contain the '.'character. The extension of the file is not needed (do not add .tex at the end)")

	def answer(self):
		#The actual calculation of the answers to the questions is in here
		answers = []
		for cont, question in enumerate(self.q):
			if self.topics[cont] == 'Integration':
				try:
					integral = sp.integrate(question, x)
				except sp.polys.polyerrors.PolynomialDivisionFailed:
					print("Solito errore di sympy")
					integral = "Solution could not be found"
				except Exception as e:
					print(f'Error: {str(e)}')
					exit()

				#Answers longer than ans_length are removed only if the function is not polynomial. Integrals of polynomials are always easy so there is no need to remove them for being too hard
				if len(str(integral)) > self.ans_length and self.ftype.lower() not in supported_ftype['Polynomial']:
					integral = 'R'
				answers.append(integral)

			if self.topics[cont] == 'Differentiation':
				derivative = sp.diff(question, x)
				answers.append(derivative)

			if self.topics[cont] == 'SolveAlgebraic':
				solutions = sp.solve(question, x)
				answers.append(solutions)

		while 'R' in answers:
			to_remove = answers.index('R')
			print(f"Question {self.q[to_remove]} will be discarded")
			answers.pop(to_remove)
			self.q.pop(to_remove)

		return answers

	@staticmethod
	def choose_random_topic(topics):
		pass

	def prepare_latex_line(self, q, cont):

		topic = self.topics[cont]
		answer = self.answers[cont]
		
		if topic.lower() in ['integration', 'integrals', 'indefinite integrals']:

			s_ans = f"Answer to question {cont+1}\n" + sp.latex(answer, mode='equation') + '\n'
			s_q = f"Question {cont+1}: Solve\n" + sp.latex(q, mode='equation') + '\n'
			s_q = s_q.replace('begin{equation}', 'begin{equation}\\int ')
			s_q = s_q.replace('\\end{equation}', 'dx\\end{equation}')

		elif topic.lower() in ['defintegration', 'definite integrals', 'def integrals']:
			#TODO: Implement definite integration with sympy
			s_ans = f"Answer to question {cont+1}\n" + sp.latex(sp.integrate(q, x), mode='equation') + '\n'
			s_q = f"Question {cont+1}: Solve\n" + sp.latex(q, mode='equation') + '\n'
			s_q = s_q.replace('begin{equation}', 'begin{equation}\\int_{infbound}^{supbound} ')
			s_q = s_q.replace('\\end{equation}', 'dx\\end{equation}')

		elif topic.lower() in ['differentiation', 'diff', 'derivatives']:

			s_ans = f"Answer to question {cont+1}\n" + sp.latex(answer, mode='equation') + '\n'
			s_q = f"Question {cont+1}: Solve\n" + sp.latex(q, mode='equation') + '\n'
			s_q = s_q.replace('begin{equation}', 'begin{equation}\\frac{\\partial f}{\\partial x}')

		elif topic.lower() == 'SolveAlgebraic':

			if len(answer) == 1:
				s_ans = f"Answer to question {cont+1}\n" + f'The solution is {answer[0]}' + '\n'
			else:
				s_ans = f"Answer to question {cont+1}\n" + 'The solutions are '
				for i in range(len(answer) - 1):
					s_ans += f' {answer[i]},'

				s_ans += f' {answer[i]}\n'
			s_q = f"Question {cont+1}: Solve\n" + sp.latex(q, mode='equation') + '\n'

		return s_ans, s_q

	@staticmethod
	def construct_date():
		from datetime import datetime
		now = datetime.now()
		date = now.strftime("%d/%m/%Y, %H:%M:%S")
		return date

	def cheatsheet(self, exam=False):
		#Function to prepare the LATEX document with the random questions
		self.today_date = self.construct_date()
		questions = self.q
		topics = self.topics
		filename = self.filename

		data = ['\\documentclass[12pt]{article}\n', '\\usepackage{fancyhdr}\n', '\\pagestyle{fancy}\n', '\\rhead{' + f'Generated with Sympy on {self.today_date}' + '}\n' '\\begin{document}\n', '\\section{Questions}']	
		answers = ["\\newpage\n \\section{Answer Sheet}\n\n"]

		for cont, q in enumerate(questions):
			s_ans, s_q = self.prepare_latex_line(q, cont)
			answers.append(s_ans)
			data.append(s_q)

		data.extend(answers)
		data.append('\\end{document}')
		filename += '.tex'
		s = ''.join(data)
		s = s.replace('operatorname{atan}', 'arctan')
		with open(filename, 'w') as f:
			f.write(s)

		#print(s)

	def to_pdf(self):

		filename = self.filename

		import os
		
		os.system(f"echo 'GENERATENEWPDF {self.today_date}\n\n' >> pdflatexlog.txt")
		os.system(f"pdflatex {filename}.tex {filename}.pdf >> pdflatexlog.txt")


