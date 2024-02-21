from phidias.Lib import *
from actions import *

# Reasoning
process_clause_final() / (DEF_CLAUSE(X) & REASON("ON") & IS_RULE(Y)) >> [show_line("\nReasoning...............\n"), -DEF_CLAUSE(X), -LISTEN('ON'), -IS_RULE(Y), reason(X), process_clause_final()]
process_clause_final() / (DEF_CLAUSE(X) & REASON("ON")) >> [show_line("\nReasoning...............\n"), -DEF_CLAUSE(X), -LISTEN('ON'), reason(X), process_clause_final()]

# Retracting definite clause
process_clause_final() / (DEF_CLAUSE(X) & LISTEN("ON") & RETRACT("ON")) >> [show_line("\nRetracting clause."), -DEF_CLAUSE(X), -RETRACT("ON"), retract_clause(X), process_clause_final()]

# Asserting definite clause
process_clause_final() / (DEF_CLAUSE(X) & LISTEN("ON")) >> [show_line("\nAsserting definite clause into Fol Kb."), -DEF_CLAUSE(X), new_clause(X), process_clause_final()]
