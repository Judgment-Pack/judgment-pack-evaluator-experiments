# Rego v1 language reference (arms B and C)

This is a language reference. It describes only how to write Rego; it says nothing about the
policy you are asked to implement. All examples below are toy examples from unrelated
domains (fruit baskets, library shelves) and are not hints about the policy.

## Provenance (derivation record)

Derived by the registered rule from the official Open Policy Agent documentation at the
pinned tag **v1.19.0** (the same tag as the pinned `opa` binary, which reports
`Rego Version: v1`). Every description below is a quotation of, or a close paraphrase of,
the official text on the pages listed here; every example is newly written for this study
and was compiled and evaluated against the pinned binary.

**Deviation from the registered fetch path, recorded:** the registered rule names
`https://raw.githubusercontent.com/open-policy-agent/opa/v1.19.0/docs/content/`. That
directory does not exist at this tag — all four `docs/content/...` fetches returned HTTP
404. At v1.19.0 the documentation lives under `docs/docs/`. The pages below are the
policy-language and policy-reference pages named by the rule, resolved at that path. No
other change to the rule.

Fetched 2026-08-15 with `curl`; `sha256` of each fetched file recorded so the derivation can
be re-checked:

| File (repo path at v1.19.0) | Raw URL | sha256 |
|---|---|---|
| `docs/docs/policy-language.md` | https://raw.githubusercontent.com/open-policy-agent/opa/v1.19.0/docs/docs/policy-language.md | `dd7b17a2df1e537975d8bddb5a40ee043bf7fbe97f41cbb9e7dd5bdcadcb2293` |
| `docs/docs/policy-reference/index.md` | https://raw.githubusercontent.com/open-policy-agent/opa/v1.19.0/docs/docs/policy-reference/index.md | `6812416361c42f77705c8a29d9bb0bed1a513d8c72a8b519f5723bdf6be9f3d5` |
| `docs/docs/policy-reference/keywords/default.md` | https://raw.githubusercontent.com/open-policy-agent/opa/v1.19.0/docs/docs/policy-reference/keywords/default.md | `2164e5dc11393f0b9452352e9b4880b8b310382e331c988552d0a145703e5034` |
| `docs/docs/policy-reference/keywords/if.md` | https://raw.githubusercontent.com/open-policy-agent/opa/v1.19.0/docs/docs/policy-reference/keywords/if.md | `efebe2b2a6dd153678774deeb3782a418701574109a72d15086acd47fec38a00` |
| `docs/docs/policy-reference/keywords/some.md` | https://raw.githubusercontent.com/open-policy-agent/opa/v1.19.0/docs/docs/policy-reference/keywords/some.md | `7d45bcfdcebcda0301e2b83a9de6429fdb583c7ff1c2416763ae183aa6314808` |
| `docs/docs/policy-reference/keywords/import.md` | https://raw.githubusercontent.com/open-policy-agent/opa/v1.19.0/docs/docs/policy-reference/keywords/import.md | `711654ee0bb4b7d8eec1ca9c31dfbcaee97ef49321d6ccbfd95e9f3a1d4c96dd` |
| `docs/docs/policy-reference/keywords/not.md` | https://raw.githubusercontent.com/open-policy-agent/opa/v1.19.0/docs/docs/policy-reference/keywords/not.md | `496423176db03353770438184ee4d7c1ef06b1559117e7433c50a60090cbfdde` |
| `docs/docs/policy-reference/keywords/contains.md` | https://raw.githubusercontent.com/open-policy-agent/opa/v1.19.0/docs/docs/policy-reference/keywords/contains.md | `49636a4e0f7a9c82b9ddaa3df0fb1fc5e5a4cf6d27a2dd3757db71439a7174c9` |
| `docs/docs/policy-reference/builtins/aggregates.mdx` | https://raw.githubusercontent.com/open-policy-agent/opa/v1.19.0/docs/docs/policy-reference/builtins/aggregates.mdx | `ae49b5c5b9dd46201f2f74ebc51828a7cd274575e637ca920480f6ba64f6c273` |
| `docs/docs/policy-reference/builtins/object.mdx` | https://raw.githubusercontent.com/open-policy-agent/opa/v1.19.0/docs/docs/policy-reference/builtins/object.mdx | `4ab190d8fdcd1a7fdb71d40227c7ac8e0bc1187cfaf80be25ccb255c4bfdd883` |
| `docs/docs/policy-reference/builtins/comparison.mdx` | https://raw.githubusercontent.com/open-policy-agent/opa/v1.19.0/docs/docs/policy-reference/builtins/comparison.mdx | `6d65462be8a89b56454f48bd46dbe2da31dd1aeded10767ca94abeae6c076048` |
| `docs/docs/policy-testing.md` | https://raw.githubusercontent.com/open-policy-agent/opa/v1.19.0/docs/docs/policy-testing.md | `ad04f1452f86173a55cf797bbd6a6117ab0d58edf2bc898d9786f3693ede6412` |

The two built-in function pages render their signature tables from OPA's built-in metadata
rather than from prose, so the wording quoted below for `count` and `object.get` is taken
from that metadata as reported by the pinned binary itself
(`opa capabilities --current`), which is the source those tables are generated from.

---

<!-- construct: package-declaration -->
## Modules and packages

A module consists of exactly one package declaration, zero or more import statements, and
zero or more rule definitions. Packages group the rules defined in one or more modules into
a particular namespace; because rules are namespaced they can be safely shared across
projects. The rules defined in a module are automatically exported, so they can be queried
under the path formed by the package name and the rule name.

```rego
package basket

pi := 3.14159
```

Given that module, the `pi` document is `data.basket.pi`.

Valid package names are variables or references that only contain string operands, e.g.
`package foo`, `package foo.bar`, `package foo.bar.baz`.

<!-- construct: comments -->
Comments begin with the `#` character and continue until the end of the line.

<!-- construct: import-statement -->
## Imports

Import statements declare dependencies that modules have on documents defined outside the
package. By importing a document, the identifiers exported by that document can be
referenced within the current module. All modules contain implicit statements which import
the `data` and `input` documents — so `input.x` and `data.foo.bar` are always available with
no import at all. Modules can also declare dependencies on query arguments by specifying an
import path that starts with `input`.

```rego
package shelf

import data.basket.pi

import input.item

circumference := pi * 2

named if item == "atlas"
```

A policy that only reads `input` and defines its own rules needs no import statements at
all.

<!-- construct: scalar-values -->
<!-- construct: composite-object -->
<!-- construct: composite-array -->
<!-- construct: composite-set -->
## Values

Scalar values are the simplest type of term in Rego: strings, numbers, booleans, or `null`.

```rego
package values

greeting := "hello"

max_height := 42

allowed := true

location := null
```

Composite values define collections.

- **Arrays** are ordered collections of values, zero-indexed, and may contain any value.
  Use arrays when order matters or when duplicate values are required: `[1, "two", 3.0]`.
- **Objects** are unordered key-value collections. In Rego, any value type can be used as
  an object key: `{"name": "atlas", "shelves": [1, 2]}`.
- **Sets** are unordered collections of unique values: `{1, 2, 3}`. Set documents are
  collections of values without keys or order. OPA represents sets as arrays when
  serializing to JSON or other formats that do not support a set data type. Sets are
  unkeyed, i.e. you cannot refer to the index of an element within a set.

Sets share their curly-brace syntax with objects. An empty object is written `{}`; an empty
set has to be constructed with the different syntax `set()`.

<!-- construct: assignment-local -->
## Assignment `:=`

The assignment operator `:=` is used to assign values to variables. Variables assigned
inside a rule are locally scoped to that rule and shadow global variables. Assigned
variables are not allowed to appear before the assignment in the query, and a variable may
not be assigned twice in the same body.

```rego
package assignment

ripe if {
	n := 3
	n > 1
}
```

<!-- construct: comparison-operators -->
## Comparison operators

The following comparison operators are supported (quoting the official list):

```text
a  ==  b  #  `a` is equal to `b`.
a  !=  b  #  `a` is not equal to `b`.
a  <   b  #  `a` is less than `b`.
a  <=  b  #  `a` is less than or equal to `b`.
a  >   b  #  `a` is greater than `b`.
a  >=  b  #  `a` is greater than or equal to `b`.
```

None of these operators bind variables contained in the expression. As a result, if either
operand is a variable, the variable must appear in another expression in the same rule that
would cause the variable to be bound, i.e. an equality expression or the target position of
a built-in function.

Comparison (`==`) checks if two values are equal within a rule; values used in comparison
must be assigned before the comparison is made. Best practice is to use assignment `:=` and
comparison `==` unless you know you need unification (`=`).

```rego
package compare

package_size := 12

bulk if package_size >= 12

single if package_size < 12
```

<!-- construct: complete-rule-no-body -->
<!-- construct: complete-rule-if-body -->
## Rules

A rule can be understood intuitively as:

```text
rule-name IS value IF body
```

If the **value** is not specified, it defaults to the boolean value `true`. Rego also allows
authors to omit the body of rules; if the body is omitted, it defaults to true. So a rule
with a value and no body is simply a definition:

```rego
package rules

shelf_names := ["fiction", "atlas", "maps"]

shelf_count := count(shelf_names)
```

When evaluating rule bodies, OPA searches for variable bindings that make all of the
expressions true. The rule body can be understood intuitively as
`expression-1 AND expression-2 AND ... AND expression-N`.

<!-- construct: if-keyword -->
The `if` keyword separates the rule head from the rule body, making it clear which part of
the rule is the condition (the part following the `if`). The body may be a single expression
or a braced block:

```rego
package rules

bulk if input.qty >= 12

crate if {
	input.qty >= 12
	input.fruit == "apple"
}
```

**Complete definitions.** Rules provide a complete definition by omitting the key in the
head. Documents produced by rules with complete definitions can only have one value at a
time; if evaluation produces multiple values for the same document, an error will be
returned. (On the pinned binary such a case fails at evaluation with
`complete rules must not produce multiple outputs`, exit status 2.)

```rego
package rules

label := "crate" if input.qty >= 12
```

<!-- construct: undefined-and-default -->
## Undefined results, and how `default` interacts with them

Rego rules are *partial*: a rule whose body is not satisfied produces no value at all. The
official text puts it this way — evaluating such a rule "returns `undefined` because the
body of the rule never evaluates to `true`. As a result, the document generated by the rule
is not defined." Undefined is not `false` and not `null`; it is the absence of a value.

Undefinedness propagates: "Expressions that refer to undefined values are also undefined.
This includes comparisons such as `!=`."

```rego
package undefined_demo

# undefined whenever input.fruit is not "apple"
apple if input.fruit == "apple"

# also undefined in that case, even though `!=` looks like it should be true
not_pear if apple != true
```

Querying an undefined document yields no result (the pinned binary prints `{}` and exits 0
without `--fail`, and exits 1 with `--fail`).

<!-- construct: default-rule -->
**The `default` keyword** allows policies to define a default value for documents produced
by rules with complete definitions. *The default value is used when all the rules sharing
the same name are undefined.* It is often helpful to know that a value will always be
defined so that the policy or its callers do not also need to handle undefined values.

```rego
package default_demo

default label := {"name": "none", "tags": []}

label := {"name": "apple-crate", "tags": ["bulk"]} if {
	input.fruit == "apple"
	input.qty >= 12
}
```

With no matching input, `data.default_demo.label` is `{"name": "none", "tags": []}`; without
the default definition it would be undefined.

When the `default` keyword is used, the rule syntax is restricted to:

```text
default <name> := <term>
```

The term may be any scalar, composite, or comprehension value but it may not be a variable
or reference. If the value is a composite then it may not contain variables or references.
Comprehensions however may, as the result of a comprehension is never undefined.

The `default` keyword can be applied to functions as well, with the same conditions on the
value, plus: same arity as other functions with the same name; arguments should only be
plain variables (no composite values); argument names should not be repeated. Note that a
`default` function will still fail (as in, not evaluate even to the default value) if any of
the arguments provided in the call are **undefined**, because the arguments are evaluated
before the function is called.

A `default` does **not** make a rule "last in a list of alternatives" — it supplies the
value for the case where *every* rule of that name is undefined. It never overrides a rule
that did produce a value, and it never resolves a conflict between two rules that produced
different values.

<!-- construct: evaluation-order -->
## Rule evaluation order is not priority; `else` is

Rules that share a name but are written separately are *not* tried in source order with the
first match winning. For complete definitions, "documents produced by rules with complete
definitions can only have one value at a time. If evaluation produces multiple values for
the same document, an error will be returned" — the rule definitions are *in conflict*, and
the fact that one was written above the other does not make it win. (Rules that define sets
or objects incrementally are additive: an incrementally defined rule "can be intuitively
understood as `<rule-1> OR <rule-2> OR ... OR <rule-N>`", i.e. their results are unioned,
again not prioritised.)

This module is a conflict, not a priority list — evaluating `data.order_demo.shelf` with
`input.item == "book"` is an error, not `"left"`:

```rego
package order_demo

shelf := "left" if input.item == "book"

shelf := "right" if input.item == "book"
```

<!-- construct: else-rule-ladder -->
<!-- construct: else-without-body -->
**The `else` keyword** is the construct that *does* give priority. Quoting the official
text: "The `else` keyword is a basic control flow construct that gives you control over rule
evaluation order. Rules grouped together with the `else` keyword are evaluated until a match
is found. Once a match is found, rule evaluation does not proceed to rules further in the
chain." It "is useful if you are porting policies into Rego from an order-sensitive system
like iptables." The `else` keyword may be used repeatedly on the same rule and there is no
limit imposed on the number of `else` clauses on a rule; the official docs recommend using
it sparingly to avoid tightly coupled rules.

```rego
package else_demo

label := "crate" if {
	input.fruit == "apple"
	input.qty >= 12
} else := "bag" if {
	input.fruit == "apple"
} else := "loose" if {
	input.qty != null
} else := "unlabelled"
```

Two things to note in that example:

- Each rung is `else := <value> if { <body> }`. A rung fires only if every earlier rung's
  body failed (or was undefined) and its own body holds.
- The **final rung may omit the `if` body entirely** (`else := "unlabelled"`), because a
  rule body that is omitted defaults to true. That rung therefore always fires if the ladder
  reaches it, which makes the whole ladder total — it always produces a value.

An `else` ladder and a `default` can coexist; the reference grammar lists the ordered form
as:

```text
default a := 1
a := 5 if { ... }
else := 10 if { ... }
```

<!-- construct: function-definition -->
<!-- construct: function-else-ladder -->
## Functions with parameters

Rego supports user-defined functions that can be called with the same semantics as built-in
functions. They have access to both the data document and the input document. Functions may
have an arbitrary number of inputs, but exactly one output. If the output term is omitted,
it is equivalent to having the output term be the literal `true`, and `if` can be used to
write shorter definitions.

```rego
package functions_demo

# two parameters, one output
volume(width, height) := width * height

boxed(width, height) if volume(width, height) > 10
```

The outputs of user functions must resolve to a single value; a function with multiple
possible bindings for its output raises a conflict error. Functions may be defined more than
once, to achieve a conditional selection of which function to execute; a given function call
will execute all functions that match the signature given, and if a call matches multiple
functions they must produce the same output or a conflict error occurs. If a call matches no
functions, then the result is undefined.

`else` works on functions exactly as it does on rules, and is the way to get ordered
alternatives inside a function without conflicts:

```rego
package functions_demo

classify(fruit, qty) := "crate" if {
	fruit == "apple"
	qty >= 12
} else := "bag" if {
	fruit == "apple"
} else := "loose" if {
	qty != null
} else := "empty"
```

Parameters are ordinary local variables: a parameter that a given rung does not constrain is
simply unconstrained in that rung.

<!-- construct: object-get -->
## `object.get`

Reading a key that may be missing is the main reason to use `object.get`. Its official
description:

> Returns value of an object's key if present, otherwise a default. If the supplied `key` is
> an `array`, then `object.get` will search through a nested object or array using each key
> in turn. For example: `object.get({"a": [{ "b": true }]}, ["a", 0, "b"], false)` results in
> `true`.

Signature: `object.get(object, key, default)` — the object to get `key` from, the key to
look up, and the default to use if the lookup fails. The array form walks a path.

```rego
package get_demo

fruit := object.get(input, ["basket", "fruit"], null)

qty := object.get(input, ["basket", "qty"], null)
```

With input `{"basket": {"fruit": "apple"}}` these are `"apple"` and `null`. This is the
difference between `object.get(input, ["basket", "qty"], null)` and `input.basket.qty`: the
plain reference is **undefined** when the key is missing, and an expression that refers to
an undefined value is itself undefined, whereas `object.get` gives you a definite value you
chose. Picking a sentinel default (such as `null`) that the input can never itself contain
lets you test for "the key was missing" with an ordinary comparison.

<!-- construct: count -->
## `count`

Official description:

> Count takes a collection or string and returns the number of elements (or characters) in
> it.

It takes the set/array/object/string to be counted, and returns "the count of elements,
key/val pairs, or characters, respectively".

```rego
package count_demo

shelf_names := ["fiction", "atlas", "maps"]

how_many := count(shelf_names)

only_one if count(shelf_names) == 1
```

<!-- construct: some-in -->
<!-- construct: membership-in -->
## `in`, and `some ... in`

The membership operator `in` lets you check if an element is part of a collection (array,
set, or object). It always evaluates to `true` or `false`:

```rego
package in_demo

result := {
	"array": 3 in [1, 2, 3],
	"set": 3 in {1, 2, 3},
	"object": 3 in {"foo": 1, "bar": 3},
	"object_key": "foo" in {"foo": 1, "bar": 3}, # false: values, not keys
}
```

Combined with `not`, the operator is handy when asserting that an element is *not* a member
of an array: `deny if not "atlas" in input.shelf`.

The `some` keyword is used to define a local variable for use later in a rule. The keyword
can also be used in conjunction with the `in` keyword to enumerate a series of items in a
list or key value pairs in an object. Using the `some` variant introduces new variables
based on a collection's items:

```rego
package some_demo

sizes := [1, 6, 12]

has_big if {
	some s in sizes
	s >= 12
}
```

A body containing `some x in collection` is satisfied if *some* binding of `x` satisfies the
rest of the body — it is existential, and it enumerates rather than picks. Two idioms follow
from that and are worth naming explicitly:

- `some x in c; <body>` inside a rule body means "there exists an element of `c` such that
  `<body>`".
- `some x in c` where `c` is known to hold exactly one element is how you *extract* that one
  element into `x`.

<!-- construct: set-comprehension -->
## Comprehensions

Comprehensions provide a concise way of building composite values from sub-queries. Like
rules, comprehensions consist of a head and a body; the body is one or more expressions that
must all be true, and when the body evaluates to true, the head is evaluated to produce an
element in the result. The body of a comprehension is able to refer to variables defined in
the outer body. The result of a comprehension is never undefined — an empty result is an
empty collection.

The three forms:

```text
[ <term> | <body> ]        # array comprehension
{ <key>: <term> | <body> } # object comprehension
{ <term> | <body> }        # set comprehension
```

A set comprehension collects distinct values, which makes it the natural way to ask "how
many *different* outcomes does this range of possibilities produce?" — build the set, then
`count` it:

```rego
package comprehension_demo

sizes := [1, 6, 12]

labels := {l |
	some s in sizes
	l := classify(s)
}

classify(qty) := "bulk" if {
	qty >= 12
} else := "small"

agreed if count(labels) == 1

the_label := l if {
	count(labels) == 1
	some l in labels
}
```

Note the last rule: `count(...) == 1` establishes that the set is a singleton, and
`some l in labels` then binds `l` to its only member. It also shows that a rule's **value
may be a variable bound in its own body** (`the_label := l if { ... }`) rather than a
literal — which works in an `else` rung exactly as it does in a first rung.

## Writing tests with `opa test`

To test a policy, create a separate Rego file that contains test cases. Test rules are
named with a `test_` prefix, and the `with` keyword is used to supply the input: "The `with`
keyword allows queries to programmatically specify values nested under the input document or
the data document, or built-in functions."

```rego
package classify_test

import data.classify

test_bulk_when_large if {
	classify.label == "crate" with input as {"fruit": "apple", "qty": 20}
}

test_result_object if {
	classify.summary == {"name": "none", "tags": []} with input as {}
}

test_not_bulk_when_small if {
	not classify.bulk with input as {"fruit": "apple", "qty": 1}
}
```

Both files are saved in the same directory and exercised with `opa test .` (add `-v` for
per-test output). A test rule passes when it evaluates to true; `not <rule>` is how you
assert that a rule is undefined or false. Comparing a whole object with `==` is the way to
assert an exact result value rather than just its presence.
