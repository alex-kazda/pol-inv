from .errors import MissingArityError, RelationArityMismatchError, RelationOutOfUniverseError
from itertools import chain


#class Relation:
#    def __init__(self, name, tuples: list, arity=None):
#        arities = [len(r) for r in tuples]
#         if arity is not None:
#             arities.append(arity)
#         if arities == []:
#             raise MissingArityError
#         if len(set(arities))>1:
#             raise RelationArityMismatchError
#         self.arity = arities[0]
#         self.tuples = tuples
#         self.name = name

def calculate_signature(relation, empty_rel_signature):
    if relation == []:
        return empty_rel_signature
    else:
        arities = [len(tuple) for tuple in relation]
        if len(set(arities)) > 1:
           raise RelationArityMismatchError(relation)
        else:
            return arities[0]

def check_membership_in_universe(relation, universe):
    universe_relation = set(chain.from_iterable(relation))
    if not universe_relation.issubset(universe):
        for element in universe_relation:
            if element not in universe:
                raise RelationOutOfUniverseError(element, universe)


class RelationalStructure:
    def __init__(self, universe: list, relations: list[list], empty_rel_signature=1):
        """
        Creates a new relational structure.
        :type universe: list
        """
        self.signature = [calculate_signature(relation, empty_rel_signature) for relation in relations]
        for relation in relations:
            check_membership_in_universe(relation, universe)
        self.relations = relations
        self.universe = universe
