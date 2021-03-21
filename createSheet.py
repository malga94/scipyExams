
from sympyExams import FunctionGenerator, ExpressionGenerator, RandomArticle

x = ExpressionGenerator(['nestedradical'])
expressions, types = x.generate(10)
exam = RandomArticle(expressions, ['NestedSquareRoots'])

# x = FunctionGenerator(['trig', 'poly'], include_special_trig=True)
# functions, _ = x.generate(10)
#exam = RandomArticle(functions, ['Integration'])

exam.cheatsheet()
exam.to_pdf()