# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT license.


from textworld.generator import data
from textworld.generator.chaining import maybe_instantiate_variables
from textworld.logic import Action, Placeholder, Proposition, Rule, State, Variable


P = Variable("P", "P")
I = Variable("I", "I")
bedroom = Variable("bedroom", "r")
kitchen = Variable("kitchen", "r")
old_key = Variable("old key", "k")
rusty_key = Variable("rusty key", "k")
small_key = Variable("small key", "k")
wooden_door = Variable("wooden door", "d")
glass_door = Variable("glass door", "d")
chest = Variable("chest", "c")
cabinet = Variable("cabinet", "c")
counter = Variable("counter", "s")
robe = Variable("robe", "o")


def build_state(door_state="open"):
    # Set up a world with two rooms and a few objecs.
    state = State([
        Proposition("at", [P, bedroom]),
        Proposition("south_of", [kitchen, bedroom]),
        Proposition("north_of", [bedroom, kitchen]),
        Proposition("link", [bedroom, wooden_door, kitchen]),
        Proposition("link", [kitchen, wooden_door, bedroom]),
        Proposition(door_state, [wooden_door]),
        #
        Proposition("in", [rusty_key, I]),
        Proposition("match", [rusty_key, chest]),
        Proposition("locked", [chest]),
        Proposition("at", [chest, kitchen]),
        Proposition("in", [small_key, chest]),
        #
        Proposition("match", [small_key, cabinet]),
        Proposition("locked", [cabinet]),
        Proposition("at", [cabinet, bedroom]),
        Proposition("in", [robe, cabinet]),
    ])
    return state


def test_variables():
    for var in [P, bedroom, robe, counter, chest]:
        data = var.serialize()
        loaded_var = Variable.deserialize(data)
        assert loaded_var == var


def test_propositions():
    state = build_state()
    for prop in state.facts:
        data = prop.serialize()
        loaded_prop = Proposition.deserialize(data)
        assert loaded_prop == prop


def test_rules():
    # Make sure the number of basic rules matches the number
    # of rules in rules.txt
    basic_rules = [k for k in data.get_rules().keys() if "-" not in k]
    assert len(basic_rules) == 19

    for rule in data.get_rules().values():
        infos = rule.serialize()
        loaded_rule = Rule.deserialize(infos)
        assert loaded_rule == rule


def test_get_reverse_rules(verbose=False):
    for rule in data.get_rules().values():
        r_rule = data.get_reverse_rules(rule)

        if verbose:
            print(rule, r_rule)

        if rule.name.startswith("eat"):
            assert r_rule is None
        else:
            # Check if that when applying the reverse rule we can reobtain
            # the previous state.
            action = maybe_instantiate_variables(rule, data.get_types().constants_mapping.copy(), State([]))
            state = State(action.preconditions)

            new_state = state.copy()
            assert new_state.apply(action)

            assert r_rule is not None
            actions = list(new_state.all_applicable_actions([r_rule], data.get_types().constants_mapping))
            if len(actions) != 1:
                print(actions)
                print(r_rule)
                print(new_state)
                print(list(new_state.all_instantiations(r_rule, data.get_types().constants_mapping)))
                assert len(actions) == 1
            r_state = new_state.copy()
            r_state.apply(actions[0])
            assert state == r_state


def test_serialization_deserialization():
    rule = data.get_rules()["go/east"]
    mapping = {
        Placeholder("r'"): Variable("room1", "r"),
        Placeholder("r"): Variable("room2"),
    }
    mapping.update(data.get_types().constants_mapping)
    action = rule.instantiate(mapping)
    infos = action.serialize()
    action2 = Action.deserialize(infos)
    assert action == action2


if __name__ == "__main__":
    test_get_reverse_rules()
