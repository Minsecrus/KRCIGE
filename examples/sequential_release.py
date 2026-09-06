"""Exact finite-horizon demonstration for KRCIGE v0.2; synthetic inputs, stdlib only."""
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


def expansion(alpha, beta):
    q = alpha / (alpha+beta)
    p = INPUTS
    return (1-q)*p["delivery_value"] - p["release_cost"] - q*(
        p["direct_loss"] + p["recovery_cost"])


@lru_cache(None)
def solve(alpha, beta, remaining, budget, active, observation_enabled=True):
    p = INPUTS
    actions = {}
    if active and budget >= p["rollback_cost"]:
        actions["rollback"] = -p["rollback_cost"]
    if not active:
        actions["stop"] = 0.0
    if budget >= p["release_cost"] and p["recovery_budget"] >= p["recovery_cost"]:
        actions["expand"] = expansion(alpha, beta)
    if (observation_enabled and remaining > 0 and
            budget >= p["sample_cost"] + p["rollback_cost"]):
        probs = predictive(alpha, beta, p["batch_size"])
        actions["observe"] = -p["sample_cost"]-p["sample_delay"] + sum(
            prob * (-p["loss_per_sample_failure"]*x +
                    solve(alpha+x, beta+p["batch_size"]-x, remaining-1,
                          budget-p["sample_cost"], True)[1])
            for x, prob in enumerate(probs))
    assert actions
    chosen = max(actions, key=actions.get)
    return chosen, actions[chosen], actions


def calculation():
    p = INPUTS
    a, b, size = p["alpha"], p["beta"], p["batch_size"]
    root = solve(a, b, p["rounds"], p["initial_budget"], False)
    one_round = solve(a, b, 1, p["initial_budget"], False)
    first = []
    # Independent explicit expansion over the 11 first-round outcomes.
    independent = -p["sample_cost"] - p["sample_delay"]
    for x, prob in enumerate(predictive(a, b)):
        aa, bb = a+x, b+size-x
        end = max(expansion(aa, bb), -p["rollback_cost"])
        future = -p["sample_cost"] - p["sample_delay"] + sum(
            pp * (-p["loss_per_sample_failure"]*xx +
                  max(expansion(aa+xx, bb+size-xx), -p["rollback_cost"]))
            for xx, pp in enumerate(predictive(aa, bb)))
        best = max(end, future)
        independent += prob * (-p["loss_per_sample_failure"]*x + best)
        decision = solve(aa, bb, 1, p["initial_budget"]-p["sample_cost"], True)
        assert isclose(decision[1], best, abs_tol=1e-10)
        first.append(dict(failures=x, probability=prob, posterior_mean=aa/(aa+bb),
                          action=decision[0], continuation_value=decision[1]))
    assert isclose(root[2]["observe"], independent, abs_tol=1e-10)
    assert root[1] >= one_round[1] >= max(root[2]["expand"], root[2]["stop"])
    return dict(evidence="synthetic exact calculation", inputs=p,
                root_action=root[0], root_value=root[1], root_action_values=root[2],
                one_round_value=one_round[1], first_round_policy=first,
                terminal_expand_threshold=(p["delivery_value"]-p["release_cost"]+
                    p["rollback_cost"])/(p["delivery_value"]+p["direct_loss"]+
                    p["recovery_cost"]),
                checks="normalization, posterior martingale, independent tree enumeration, horizon option value")


if __name__ == "__main__":
    print(json.dumps(calculation(), ensure_ascii=False, indent=2))

