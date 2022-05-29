from .errors import EquationConditionError
from itertools import product

class EquationalIdentity:
    def __init__(self, LHSterm, RHSterm):
        self.LHSterm = LHSterm
        self.RHSterm = RHSterm
        self.variable_set = set(LHSterm.input_vars).union(set(RHSterm.input_vars))
        self.operation_set = {LHSterm.operation, RHSterm.operation}
        self._enum_table = {v: i for i, v in enumerate(self.variable_set)}

    def __and__(self, other):
        if type(other) == EquationalIdentity:
            return ChainOfEquationalIdentities(self, other)
        elif type(other) == ChainOfEquationalIdentities:
            return other.append(self)
        else:
            raise EquationConditionError(type(other))

    def plug_in_values(self, valuation):
        return [(t.operation, tuple([valuation[self._enum_table[v]] for v in t.input_vars])) for t in [self.LHSterm, self.RHSterm]]

    def plug_in_all_values(self, universe):
        return map(self.plug_in_values, product(universe, repeat=len(self.variable_set)))



class ChainOfEquationalIdentities:
    def __init__(self, *equations):
        raise NotImplemented
        # for eqn in equations:
        #    if type(eqn)!=EquationalIdentity:
        #        raise TypeError
        # self.identities= equations

    def append(self, eq_identity):
        raise NotImplemented
