# pol-inv

The goal of this project is to allow one to use a Jupyter notebook (or a Python program) to investigate various properties of relational structures and algebras.

The package is very basic and probably full of bugs at the moment. There some similar packages are already available:
- Jakub Opršal's [PCSP Tools](https://github.com/jakub-oprsal/pcsptools) from which I took a lot of inspiration
- Peter Jipsen's [Sage package](https://math.chapman.edu/~jipsen/sagepkg/) that uses Prover9 to reason about algebras
- Miklos Maroti's [Critical Relations](https://www.math.u-szeged.hu/~mmaroti/applets/CriticalRels.html) and [Graph Polymorphism](https://www.math.u-szeged.hu/~mmaroti/applets/GraphPoly.html) Java applets
- The [Universal Algebra Calculator](http://uacalc.org) has a GUI and a Python API (but only handles algebras, not relational structures)

Currently pol-inv can compute:
- Whether there exists a polymorphism from a relational structure A to a relational structure B that satisfies a given height 1 identity (see https://doi.org/10.1145/3457606)
