from pysat.solvers import Solver

#def run_pycosat(constraints, no_vars, no_constraints, solver_path, solver_params):
#    sol = pycosat.solve(constraints)
#    if sol == "UNSAT":
#        return None
#    return sol

def run_solver(
    sat_instance, solver_name, equations, use_timer=False
):
    #TODO: add ability to run non-pysat solvers.
    with Solver(
        name=solver_name, bootstrap_with=sat_instance, use_timer=use_timer
    ) as sat_solver:
        if sat_solver.solve() == True:
            return sat_solver.get_model()
        else:
            return None



def create_dimacs_instance(constraints, no_vars, no_constraints):
    cnf_file = f"p cnf {no_vars} {no_constraints}\n" + "\n".join(
        [" ".join(map(str, constraint)) + " 0\n" for constraint in constraints]
    )
    #    with NamedTemporaryFile(mode="w", delete=False) as cnf_file:
    #        cnf_file.write(f"p cnf {no_vars} {no_constraints}\n")
    #        for constraint in constraints:
    #            cnf_file.write(' '.join(map(str, constraint)) +' 0\n')
    return cnf_file.encode("ascii")


def glucose_decode_model(output_bytes):
    return list(map(int, output_bytes[output_bytes.find("\nv") + 3 : -3].split(" ")))


def run_maple_glucose(constraints, no_vars, no_constraints, solver_path, solver_params):
    instance = create_dimacs_instance(constraints, no_vars, no_constraints)
    completed_process = run(
        [solver_path, *solver_params],
        input=instance,
        capture_output=True,
    )
    if completed_process.returncode == 20:
        return None  # Unsatifiable instance
    if completed_process.returncode == 10:
        return glucose_decode_model(completed_process.stdout.decode("ascii"))
