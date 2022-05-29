from .errors import ArityMismatchError, EquationConditionError
from .equations import EquationalIdentity

class Operation:  # Operation of a given arity
    def __init__(self, name, arity):
        self.name = name
        self.arity = arity

    def __call__(self, *input_vars):
        if len(input_vars) != self.arity:
            raise ArityMismatchError(self.arity, len(input_vars))
        else:
            return H1Term(self, *input_vars)
    def __str__(self):
        return f"Operation symbol named '{self.name}' of arity {self.arity}."
    def __repr__(self):
        return self.name


class H1Term:  # Height 1 term, i.e., t(x,x,y)
    def __init__(self, operation: str, *input_vars):
        self.input_vars = input_vars
        self.operation = operation

    def __eq__(self, other):
        if type(other) != H1Term:
            raise EquationConditionError(type(other))
        else:
            return EquationalIdentity(self, other)
