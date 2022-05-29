from itertools import product, count, combinations, chain
from tempfile import NamedTemporaryFile
from subprocess import run
from .relational_structure import RelationalStructure
from .terms_and_operations import Operation
import os
from .solver_callers import run_solver
from .errors import SignatureMismatchError


def transpose(matrix: list[tuple]):
    """
    Given a matrix realized by a list of lists, return the transposed matrix.
    I.e. given
    [[a, b],
    [d,e],
    [f,g]],
    the output will be
    [(a, d, f),
    (b, e, g)].
    For technical reasons returns tuples instead of lists.
    """
    return [tuple([m[i] for m in matrix]) for i in range(len(matrix[0]))]


def generate_operation_inputs_outputs(inputs, outputs, arity):
    return product(product(inputs, repeat=arity), outputs)


def find_polymorphisms(
    a: RelationalStructure,
    b: RelationalStructure,
    equations: list,
    solver_name: str = "g3",
):
    def mk_hash_table():
        """
        This nested function will fill the hash_table with two types of keys:
        a) `(operation, input_values, output_value)` to describe function values of `operation`
        b) `(operation, input_tuples, output_tuple)` to describe values that `operation`
        takes on tuples in the relation
        :return: hash_table dictionary
        """
        hash_table = {}
        variable_counter = 1
        for operation in operations_to_find:
            hash_table.update(
                {
                    (operation, input_values, output_value): i
                    for i, (input_values, output_value) in enumerate(
                        generate_operation_inputs_outputs(
                            a.universe,
                            b.universe,
                            operation.arity,
                        ),
                        start=variable_counter,
                    )
                }
            )
            variable_counter += len(a.universe) ** operation.arity * len(b.universe)
            for relation_no in range(signature_len):
                hash_table.update(
                    {
                        (operation, input_tuples, output_tuple): i
                        for i, (input_tuples, output_tuple) in enumerate(
                            generate_operation_inputs_outputs(
                                a.relations[relation_no],
                                b.relations[relation_no],
                                operation.arity,
                            ),
                            start=variable_counter,
                        )
                    }
                )
                variable_counter += len(
                    a.relations[relation_no]
                ) ** operation.arity * len(b.relations[relation_no])
        return hash_table

    def model_to_functions():
        # TODO make this more efficient
        results = {}
        for op in operations_to_find:
            value_table = {}
            for tuple, b_val in product(
                product(a.universe, repeat=op.arity), b.universe
            ):
                if solution[hash_table[(op, tuple, b_val)] - 1] > 0:
                    value_table.update({tuple: b_val})
            results.update({op.name: value_table})
        return results

    if a.signature != b.signature:
        raise SignatureMismatchError()
    else:
        signature_len = len(a.signature)

    operations_to_find = set(
        chain.from_iterable([eqn.operation_set for eqn in equations])
    )
    hash_table = mk_hash_table()
    sat_instance = sat_instance_from_eq_condition(
        a, b, equations, operations_to_find, hash_table
    )
    solution = run_solver(sat_instance, solver_name, equations)
    if solution is None:
        return None
    else:
        return model_to_functions()



def sat_instance_from_eq_condition(
    a: RelationalStructure,
    b: RelationalStructure,
    equations: list,
    operations_to_find: set[Operation],
    hash_table: dict,
) -> list:
    """
    Creates a CNF SAT instance (in the form of list of clauses with clause = list of variables, see DIMACS instances for more).
    Input are relational structures and a list of equations that are to be satisfied. For technical reasons, we
    also need to pass a hash table (see mk_hash_table above) and a set of operations to find.
    :param a:
    :param b:
    :param equations:
    :param hash_table:
    :return:
    """

    def exactly_one(variables: list[tuple]) -> iter:
        """
        Outputs CNF clauses that ensure that exactly one of `variables` is true.
        Used to ensure that each operation has exactly one value for any given input.
        """
        yield [hash_table[v] for v in variables]
        for v, w in combinations(variables, 2):
            yield [-hash_table[v], -hash_table[w]]

    def at_least_one(variables: iter) -> iter:
        """
        Outputs CNF clause that ensure that at least one of `variables` is true.
        """
        yield [hash_table[v] for v in variables]

    def operation_commutes_with_projections_on_tuples(input_data):
        """
        Outputs CNF clauses that enforce that operation applied to tuples
        works coordinate-wise (="commutes with projections to i-th place").
        That is, if f((0,1),(1,2))==(a,b), we enforce f(0, 1)== a and f(1, 2)==b.
        Here we would have `tuples=[(0,1),(1,2),(a,b)]`
        :param input_data: a triple (operation, input_tuples, output_tuple)
        :return: Returns a generator for CNF clauses such as (in the example above),
         "[not f((0,1),(1,2))==(a,b) OR f(0,1)==a, not f((0,1),(1,2))==(a,b) OR f(1,2)==b]"
        """
        operation, input_tuples, output_tuple = input_data
        rows = transpose(input_tuples)
        for i, row in enumerate(rows):
            yield [
                -hash_table[input_data],
                hash_table[(operation, row, output_tuple[i])],
            ]

    def unique_function_values_cnf_generator():
        return chain.from_iterable(
            [unique_function_values_for_operation(op) for op in operations_to_find]
        )

    def unique_function_values_for_operation(op: Operation):
        return chain.from_iterable(
            map(exactly_one, enumerate_all_inputs(op, a.universe, b.universe))
        )

    def enumerate_all_inputs(op, input_set, output_set):
        """
        Ouputs an iterable of lists of the form
        "[(f, a0, b0),(f, a0, b1), ..., (f, a0, bn)]" where b0,...,bn = b.universe
        and a0 is a tuple of inputs (the same for each list).
        Each of these lists is then fed to `exactly_one`.
        """
        for inputs in product(input_set, repeat=op.arity):
            yield [(op, inputs, b_val) for b_val in output_set]

    def relations_preserved_cnf_generator():
        return chain(
            *[
                operation_commutes_with_projections_clause_generator(op, relation_no)
                for op, relation_no in product(operations_to_find, range(signature_len))
            ],
            *[
                operation_preserves_tuples_clause_generator(op, relation_no)
                for op, relation_no in product(operations_to_find, range(signature_len))
            ],
        )

    def operation_commutes_with_projections_clause_generator(op, relation_no):
        return chain.from_iterable(
            map(
                operation_commutes_with_projections_on_tuples,
                product(
                    [op],
                    product(a.relations[relation_no], repeat=op.arity),
                    b.relations[relation_no],
                ),
            )
        )

    def operation_preserves_tuples_clause_generator(op, relation_no):
        return chain.from_iterable(
            map(at_least_one, enumerate_all_inputs(op, a.relations[relation_no], b.relations[relation_no]))
        )

    def equalities_clauses():
        return chain.from_iterable([equality_clauses_equation(eq) for eq in equations])

    def equality_clauses_equation(eq):
        for equality, b_val in product(eq.plug_in_all_values(a.universe), b.universe):
            yield [
                hash_table[equality[0] + (b_val,)],
                -hash_table[equality[1] + (b_val,)],
            ]
            yield [
                -hash_table[equality[0] + (b_val,)],
                hash_table[equality[1] + (b_val,)],
            ]

    signature_len = len(a.signature)

    unique_function_values_cnf = unique_function_values_cnf_generator()
    relations_preserved_cnf = relations_preserved_cnf_generator()
    equalities = equalities_clauses()
    return chain(unique_function_values_cnf, relations_preserved_cnf, equalities)

    # os.remove(cnf_file.name)
