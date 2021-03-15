#TODO:
# Write README and manual
# Solve issue with saving date on the log file of pdflatex
# Solve issue with polyrational not having a constant term (only terms from x^1 upwards)
# Test functionality for solving equations, and add proper latex formatting

import sympy as sp
import re
import random

supported_ftype = {'Rational': ['rational'],
						'Polynomial': ['poly', 'polynomial'],
						'Rational Polynomial': ['polyrational'],
						'Trigonometric': ['trig', 'trigonometric']
	}

x = sp.symbols('x')

#A class to generate random mathematical functions
class FunctionGenerator:

	def __init__(self, func_type, max_power=4, max_coeff=9, include_special_trig=False):
		
		if isinstance(func_type, str):
			self.ftype = [func_type]
		else:
			self.ftype = func_type

		self.check_ftype()

		self.max_power = max_power
		self.max_coeff = max_coeff

		self.include_special_trig = include_special_trig

	def check_ftype(self):
		#TODO: Test this function
		for single_type in self.ftype:

			valid = False
			for i in supported_ftype.keys():
				
				if single_type.lower() in supported_ftype[i]:
					valid = True

			if not valid:
				s = []
				for i in supported_ftype.keys():
					for x in supported_ftype[i]:
						s.append(x)
						s.append(', ')

				options = ''.join(s)
				raise ValueError(f"FunctionGenerator(list): str must be one of the following: {options}")

	def select_function_type(self):

		x = random.randint(0, len(self.ftype)-1)
		f = self.ftype[x]
		return f

	def generate_single_expression(self):

		if len(self.ftype) == 1:
			function_type = self.ftype[0]
		else:
			function_type = self.select_function_type()

		if function_type.lower() in supported_ftype['Polynomial']:
			polynomial = Polynomial(self.max_power, self.max_coeff)
			expression = polynomial.generate_polynomial()

		if function_type.lower() in supported_ftype['Rational Polynomial']:
			num_power = random.randint(0, self.max_power)
			denom_power = random.randint(1, self.max_power)

			rational_polynomial = RationalPolynomial(power_numerator=num_power, power_denominator=denom_power)
			expression = rational_polynomial.generate_rational_poly()

		if function_type.lower() in supported_ftype['Trigonometric']:
			trig = TrigFunction(power=self.max_power, max_coeff=self.max_coeff, include_others=self.include_special_trig)
			expression = trig.generate_trig_function()

		return (expression, function_type.lower())

	def generate(self, n=1):

		#Generating n random functions, as requested by the user. This is the method that should most often be called on a FunctionGenerator object
		questions = []
		function_types = []
		if n <= 0:
			raise ValueError("generate(int): argument 1 must be > 0 ")
		for i in range(n):
			expression = self.generate_single_expression()
			questions.append(expression[0])
			function_types.append(expression[1])

		return questions, function_types

#Class to generate a polynomial in sympy
class Polynomial:

	symbols = ['+', '-']

	def __init__(self, power=2, max_coeff=10):
		self.power = power
		self.max_coeff = max_coeff

	def generate_str_polynomial(self):
		#Here the code to generate a random polynomial of degree = self.power
		powers_of_x = []
		for i in range(self.power, 1, -1):
			powers_of_x.append(f'x**{i}')
		powers_of_x.append('x')
		symbols_poly = self.symbols
		coeff, symbols = [], []
		for i in range(0, self.power+1):
			coeff.append(random.randint(0, self.max_coeff))			
			symbols.append(random.randint(0, len(symbols_poly)-1))
		str_expression = ''
		for cont, c in enumerate(coeff[:-1]):
			
			str_expression = str_expression + symbols_poly[symbols[cont]] + str(c) + '*' + powers_of_x[cont]

		str_expression = str_expression + symbols_poly[symbols[-1]] + str(coeff[-1])
		#We don't need the + before the first term - but we do need a -  if the coefficient is negative
		if str_expression[0] == '+':
			str_expression = str_expression[1:]

		return str_expression, symbols

	def generate_polynomial(self):

		s, _ = self.generate_str_polynomial()
		expression = sp.sympify(s)
		return expression

class RationalPolynomial(Polynomial):

	def __init__(self, power_numerator = 2, max_coeff_numerator=10, power_denominator = 4, max_coeff_denominator=10):
		super().__init__()
		self.power_d = power_denominator
		self.max_coeff_d = max_coeff_denominator

	def generate_rational_poly(self):
		num, _ = super().generate_str_polynomial()
		den_polynomial = Polynomial(self.power_d, self.max_coeff_d)
		den, _ = den_polynomial.generate_str_polynomial()

		str_expression = '(' + num + ')/(' + den + ')'
		expression = sp.sympify(str_expression)
		return expression

class TrigFunction(Polynomial):

	trig_functions = ['sin(x)', 'cos(x)', 'tan(x)']
	other_trig_functions = ['sec(x)', 'csc(x)', 'cot(x)', 'asin(x)', 'acos(x)', 'atan(x)']

	def __init__(self, power=2, max_coeff=10, terms=0, include_others=False):
		super().__init__()
		self.terms = terms
		self.special_func = include_others
		if self.special_func:
			self.trig_functions.extend(self.other_trig_functions)

	def generate_trig_function(self):
		p, symbols = self.generate_str_polynomial()
		p_terms = re.split('\+|\-', p)
		if p_terms[0] == '':
			p_terms.pop(0)
		str_expression = ''
		
		for term in range(len(p_terms)):
			x = random.randint(0,len(self.trig_functions)-1)
			rand_trig_function = self.trig_functions[x]
			p_terms[term] = p_terms[term].replace('x', '(' + rand_trig_function + ')')
			
			str_expression = str_expression + self.symbols[symbols[term]] + p_terms[term]

		if str_expression[0] == '+':
			str_expression = str_expression[1:]

		expression = sp.sympify(str_expression)
		return expression

#An object that takes the random f(x)'s created with FunctionGenerator, and creates a question sheet on a topic chosen by the user (e.g integration) with answers, computed using sympy
class RandomArticle:

	#Maximum length (as in len(str)) of the answer to a question, to avoid crazy integrals and derivatives which no human would ever find useful to compute by hand
	ans_length = 40
	implemented_topics = ['Integration', 'Differentiation', 'SolveAlgebraic']

	def __init__(self, questions, topics, ftypes=None, number_of_questions=0, filename="questions"):
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

		#If the user didn't pass the list ftypes, which describes which kind of functions were passed in "questions" (i.e polynomials, trig...), then some nice features will not work. 
		#For consistency, self.ftypes will still be a list of the same length
		if ftypes == None:
			self.ftypes = ['']*len(self.q)
		else:
			self.ftypes = ftypes

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

			ftype = self.ftypes[cont]
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
				if len(str(integral)) > self.ans_length and ftype.lower() not in supported_ftype['Polynomial']:
					integral = 'R'
				answers.append(integral)

			if self.topics[cont] == 'Differentiation':
				derivative = sp.diff(question, x)
				answers.append(derivative)

			if self.topics[cont] == 'SolveAlgebraic':
				try:
					print(question)
					solutions = sp.solveset(question, x)
					answers.append(solutions)
				except NotImplementedError:
					answers.append('Sympy cannot solve this equation!')
				except Exception as e:
					print(f"Error: {str(e)}")
					exit()

		while 'R' in answers:
			to_remove = answers.index('R')
			print(f"Question {self.q[to_remove]} will be discarded")
			answers.pop(to_remove)
			self.q.pop(to_remove)

		return answers

	@staticmethod
	def choose_random_topic(topics):
		
		x = random.randint(0, len(topics)-1)
		random_topic = topics[x]
		return random_topic

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

		elif topic.lower() == 'solvealgebraic':

			#print(answer)
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

		data = ['\\documentclass[12pt]{article}\n', '\\usepackage{fancyhdr}\n', '\\pagestyle{fancy}\n', '\\rhead{' + f'Generated with Sympy on {self.today_date}' + '}\n', '\\begin{document}\n', '\\section{Questions}']	
		answers = ["\\newpage\n \\section{Answer Sheet}\n\n"]

		for cont, q in enumerate(questions):
			s_ans, s_q = self.prepare_latex_line(q, cont)
			answers.append(s_ans)
			data.append(s_q)

		data.extend(answers)
		data.append('\\end{document}')
		filename += '.tex'
		s = ''.join(data)
		#Replace the sympy names with the Latex names of some trigonometric functions
		sympy_to_latex = {
			'atan': 'arctan',
			'acos': 'arccos',
			'asin': 'arcsin',
		}
		for key, value in sympy_to_latex.items():
			s = s.replace('operatorname{' + f'{key}' + '}', f'{value}')

		with open(filename, 'w') as f:
			f.write(s)

		#print(s)

	def to_pdf(self):

		filename = self.filename

		import os
		
		os.system(f"echo 'GENERATENEWPDF {self.today_date}\n\n' >> pdflatexlog.txt")
		os.system(f"pdflatex {filename}.tex {filename}.pdf >> pdflatexlog.txt")
		


