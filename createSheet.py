
from scypyExams import FunctionGenerator, Polynomial, RandomArticle

function = FunctionGenerator('poly')
questions, ftype = function.generate(10)

article = RandomArticle(questions, ["Integration"], ftype)
article.cheatsheet()
article.to_pdf()