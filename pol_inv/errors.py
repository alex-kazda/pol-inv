
class ArityMismatchError(Exception):
    def __init__(self, arity_expected, arity_got):
        super().__init__(f"Expected arity {arity_expected}, but got arity {arity_got}.")

class RelationArityMismatchError(Exception):
    def __init__(self, relation):
        super().__init__(f"Arity mismatch when creating a relation. The relation was {relation}.")

class RelationOutOfUniverseError(Exception):
    def __init__(self, element, universe):
        super().__init__(f"Element {element} does not belong in universe {universe}.")

class SignatureMismatchError(Exception):
    def __init__(self, a, b):
        super().__init__(f"Signatures of {a} and {b} do not match (note: names of relations/operations matter here).")

class MissingArityError(Exception):
    def __init__(self, arity_expected, arity_got):
        super().__init__(f"Arity is missing for an empty relation.")

class EquationConditionError(Exception):
    def __init__(self, wrong_type):
        super().__init__(
            f"Cannot form equational identity with height 1 term on one side and \
                         type {wrong_type} on the other side of ==."
        )