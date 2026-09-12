"""KRCIGE v0.3: exact synthetic release decisions and sensitivity, stdlib only."""
import argparse
from functools import lru_cache
from math import comb, isclose, lgamma, exp
import json

INPUTS = dict(alpha=4, beta=46, batch_size=10, rounds=2,
              delivery_value=240, release_cost=20, direct_loss=2400,
              recovery_cost=80, rollback_cost=6, sample_cost=2,
              sample_delay=1, loss_per_sample_failure=3,
              initial_budget=30, recovery_budget=100)


def predictive(alpha, beta, size=10):
    log_beta = lambda a, b: lgamma(a) + lgamma(b) - lgamma(a + b)
    probs = [comb(size, x) * exp(log_beta(alpha+x, beta+size-x)
             - log_beta(alpha, beta)) for x in range(size+1)]
    assert isclose(sum(probs), 1.0, abs_tol=1e-11)
    assert isclose(sum(p*(alpha+x)/(alpha+beta+size)
                       for x, p in enumerate(probs)),
                   alpha/(alpha+beta), abs_tol=1e-11)
    return probs


def expansion(alpha, beta, inputs=None):
    q = alpha / (alpha+beta)
    p = INPUTS if inputs is None else inputs
    return (1-q)*p["delivery_value"] - p["release_cost"] - q*(
        p["direct_loss"] + p["recovery_cost"])


def make_solver(inputs):
    # Each experiment owns its parameters and cache; changing a later scenario
    # cannot silently reuse values calculated under a different cost model.
    p = dict(inputs)

    @lru_cache(None)
    def solve(alpha, beta, remaining, budget, active, observation_enabled=True):
        actions = {}
        if active and budget >= p["rollback_cost"]:
            actions["rollback"] = -p["rollback_cost"]
        if not active:
            actions["stop"] = 0.0
        if budget >= p["release_cost"] and p["recovery_budget"] >= p["recovery_cost"]:
            actions["expand"] = expansion(alpha, beta, p)
        if (observation_enabled and remaining > 0 and
                budget >= p["sample_cost"] + p["rollback_cost"]):
            probs = predictive(alpha, beta, p["batch_size"])
            actions["observe"] = -p["sample_cost"]-p["sample_delay"] + sum(
                prob * (-p["loss_per_sample_failure"]*x +
                        solve(alpha+x, beta+p["batch_size"]-x, remaining-1,
                              budget-p["sample_cost"], True)[1])
                for x, prob in enumerate(probs))
        assert actions, "No feasible action: an active trial needs a rollback reserve"
        chosen = max(actions, key=actions.get)
        return chosen, actions[chosen], actions

    return solve


solve = make_solver(INPUTS)


def explicit_two_round_value(p):
    """Unrolled two-stage tree, including tight budgets and blocked expansion."""
    a, b, size = p["alpha"], p["beta"], p["batch_size"]
    budget = p["initial_budget"]

    def terminal(aa, bb, cash, active):
        values = [0.0] if not active else []
        if active and cash >= p["rollback_cost"]:
            values.append(-p["rollback_cost"])
        if cash >= p["release_cost"] and p["recovery_budget"] >= p["recovery_cost"]:
            values.append(expansion(aa, bb, p))
        assert values
        return max(values)

    root = terminal(a, b, budget, False)
    if budget < p["sample_cost"] + p["rollback_cost"]:
        return root
    first_value = -p["sample_cost"] - p["sample_delay"]
    after_first = budget - p["sample_cost"]
    for x, prob in enumerate(predictive(a, b, size)):
        aa, bb = a+x, b+size-x
        best = terminal(aa, bb, after_first, True)
        if after_first >= p["sample_cost"] + p["rollback_cost"]:
            after_second = after_first - p["sample_cost"]
            second_value = -p["sample_cost"] - p["sample_delay"] + sum(
                pp * (-p["loss_per_sample_failure"]*xx +
                      terminal(aa+xx, bb+size-xx, after_second, True))
                for xx, pp in enumerate(predictive(aa, bb, size)))
            best = max(best, second_value)
        first_value += prob * (-p["loss_per_sample_failure"]*x + best)
    return max(root, first_value)


def calculation():
    p = INPUTS
    solve = make_solver(p)
    a, b, size = p["alpha"], p["beta"], p["batch_size"]
    root = solve(a, b, p["rounds"], p["initial_budget"], False)
    one_round = solve(a, b, 1, p["initial_budget"], False)
    first = []
    # Independent explicit expansion over the 11 first-round outcomes.
    independent = -p["sample_cost"] - p["sample_delay"]
    for x, prob in enumerate(predictive(a, b, size)):
        aa, bb = a+x, b+size-x
        end = max(expansion(aa, bb), -p["rollback_cost"])
        future = -p["sample_cost"] - p["sample_delay"] + sum(
            pp * (-p["loss_per_sample_failure"]*xx +
                  max(expansion(aa+xx, bb+size-xx), -p["rollback_cost"]))
            for xx, pp in enumerate(predictive(aa, bb, size)))
        best = max(end, future)
        independent += prob * (-p["loss_per_sample_failure"]*x + best)
        decision = solve(aa, bb, 1, p["initial_budget"]-p["sample_cost"], True)
        assert isclose(decision[1], best, abs_tol=1e-10)
        first.append(dict(failures=x, probability=prob, posterior_mean=aa/(aa+bb),
                          action=decision[0], continuation_value=decision[1]))
    assert isclose(root[2]["observe"], independent, abs_tol=1e-10)
    assert isclose(root[1], explicit_two_round_value(p), abs_tol=1e-10)
    assert root[1] >= one_round[1] >= max(root[2]["expand"], root[2]["stop"])
    return dict(evidence="synthetic exact calculation", inputs=p,
                root_action=root[0], root_value=root[1], root_action_values=root[2],
                one_round_value=one_round[1], first_round_policy=first,
                terminal_expand_threshold=(p["delivery_value"]-p["release_cost"]+
                    p["rollback_cost"])/(p["delivery_value"]+p["direct_loss"]+
                    p["recovery_cost"]),
                checks="normalization, posterior martingale, independent tree enumeration, horizon option value")


def sensitivity():
    scenarios = [
        ("base", {}),
        ("cheap_failure", {"direct_loss": 600}),
        ("expensive_observation", {"sample_cost": 10}),
        ("higher_prior_risk", {"alpha": 8, "beta": 42}),
        ("recovery_budget_shortfall", {"recovery_budget": 79}),
        ("release_budget_shortfall", {"initial_budget": 19}),
        ("small_batch", {"batch_size": 3}),
    ]
    # Hold the recovery reserve high for the entire I sweep; otherwise an
    # affordability threshold would be confused with a pure cost effect.
    scenarios += [(f"recovery_cost_{cost}", {"recovery_cost": cost,
                   "recovery_budget": 1000}) for cost in (0, 80, 400, 800)]
    rows = []
    for name, changes in scenarios:
        p = {**INPUTS, **changes}
        solve = make_solver(p)
        roots = [solve(p["alpha"], p["beta"], horizon,
                       p["initial_budget"], False) for horizon in range(3)]
        assert roots[2][1] + 1e-10 >= roots[1][1] >= roots[0][1] - 1e-10
        assert isclose(roots[2][1], explicit_two_round_value(p), abs_tol=1e-10)
        rows.append(dict(scenario=name, changed_inputs=changes,
                         no_observation_value=roots[0][1],
                         one_round_value=roots[1][1], two_round_value=roots[2][1],
                         root_action=roots[2][0], root_action_values=roots[2][2],
                         gain_over_no_observation=roots[2][1]-roots[0][1]))
    assert rows[0]["root_action"] == "observe"
    assert rows[1]["root_action"] == rows[2]["root_action"] == "expand"
    assert rows[3]["root_action"] == rows[4]["root_action"] == rows[5]["root_action"] == "stop"
    assert [row["two_round_value"] for row in rows[-4:]] == sorted(
        (row["two_round_value"] for row in rows[-4:]), reverse=True)
    return dict(evidence="synthetic sensitivity; no empirical performance claim",
                base_inputs=INPUTS, scenarios=rows,
                checks="unrolled budget-aware tree, nested horizons, action reversals, fixed-reserve cost sweep")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sensitivity", action="store_true",
                        help="compare fixed-model horizons and parameter scenarios")
    args = parser.parse_args()
    print(json.dumps(sensitivity() if args.sensitivity else calculation(),
                     ensure_ascii=False, indent=2))
