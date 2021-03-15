
from sympyExams import FunctionGenerator, Polynomial, RationalPolynomial, RandomArticle, TrigFunction

# function = FunctionGenerator('poly')
# questions, ftype = function.generate(10)

# article = RandomArticle(questions, ["Integration"], ftype)
# article.cheatsheet()
# article.to_pdf()

x = FunctionGenerator(['trig', 'poly'], include_special_trig=True)
functions, _ = x.generate(10)

exam = RandomArticle(functions, ['Integration'])
exam.cheatsheet()
exam.to_pdf()