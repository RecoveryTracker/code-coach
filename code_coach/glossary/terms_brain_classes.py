"""Words the Brain Drills class pack teaches: attributes and properties, class vs instance attributes, static and
class methods, inheritance, override, super, the method resolution order / prototype chain, isinstance / instanceof,
string representation and state."""

from __future__ import annotations

from .entry import Entry, both, js, py

TERMS: list[Entry] = [
    *py(
        "attribute",
        "Attribute",
        "A named value stored on an object, such as the name of a dog. You read it with a dot: dog.name.",
        see=("class", "instance", "self", "class-attribute"),
        priority=50,
        aka=("attributes", "property", "properties", "field", "fields", "member", "instance variable"),
        detect=(r"\bself\.\w+\s*=(?!=)", r"\b(?:getattr|setattr|hasattr)\("),
        rules=(
            "self.name = name inside __init__ makes the attribute; obj.name reads it and obj.name = 'x' changes it.",
            "Reading an attribute that is not there is an AttributeError; hasattr(obj, 'name') asks first.",
            "Python lets you add a new attribute to an object at any time: d.age = 3.",
            "A method marked @property is read like an attribute, without brackets.",
        ),
        example="""
            class Dog:
                def __init__(self, name):
                    self.name = name
            d = Dog("Rex")
            d.age = 3
            print(d.name, d.age, hasattr(d, "color"))
        """,
        out="Rex 3 False",
    ),
    *js(
        "property",
        "Property",
        "A named value stored on an object, such as the name of a dog. You read it with a dot: dog.name.",
        see=("object", "class", "this", "class-attribute"),
        priority=50,
        aka=("properties", "attribute", "attributes", "field", "fields", "member", "instance variable"),
        detect=(r"\bthis\.[\w$]+\s*=(?!=)", r"\bhasOwn(?:Property)?\("),
        rules=(
            "this.name = name inside the constructor makes the property; obj.name reads it and obj.name = 'x' changes it.",
            "Reading a property that is not there is NOT an error: it gives undefined ('color' in obj asks first).",
            "JavaScript lets you add a new property to an object at any time: d.age = 3.",
            "get area() { ... } in a class makes a property that is worked out when read, without brackets.",
        ),
        example="""
            const dog = { name: "Rex" };
            dog.age = 3;
            console.log(dog.name, dog.age, dog.color, "color" in dog);
        """,
        out="Rex 3 undefined false",
    ),
    *both(
        "class-attribute",
        "Class attribute",
        "A value that belongs to the class itself, not to any one object, so every object of the class sees the same one.",
        see=("class", "instance-attribute", "shadowing"),
        priority=55,
        aka=("class attributes", "class variable", "class variables", "static attribute", "static property", "shared state", "shared"),
        python=dict(
            see=("class", "instance-attribute", "shadowing", "self"),
            rules=(
                "It is written in the class body, outside any method: class A: count = 0.",
                "Change it through the class (A.count = 5) and every object that has not made its own copy sees the change.",
                "Assigning through an object (a.count = 9) does NOT change the class attribute: it makes a new instance attribute that hides it for a only.",
            ),
            example="""
                class A:
                    count = 0
                a = A()
                b = A()
                A.count = 5
                print(a.count, b.count)
                a.count = 9
                print(a.count, b.count, A.count)
            """,
            out="5 5\n9 5 5",
        ),
        javascript=dict(
            see=("class", "instance-attribute", "static-method", "prototype-chain"),
            rules=(
                "static count = 0 inside a class belongs to the class: read it as A.count.",
                "Objects made with new A() do not have it: new A().count is undefined.",
                "Something put on A.prototype IS shared by every object, because lookups walk up to it.",
            ),
            example="""
                class A {
                  static count = 0;
                }
                const a = new A();
                A.count = 5;
                console.log(A.count, a.count);
            """,
            out="5 undefined",
        ),
    ),
    *both(
        "instance-attribute",
        "Instance attribute",
        "A value that belongs to one particular object. Each object made from the class has its own copy.",
        priority=50,
        aka=("instance attributes", "instance variable", "instance variables", "per-object", "instance property", "own property"),
        python=dict(
            see=("class-attribute", "class", "self", "attribute"),
            rules=(
                "It is made on self, usually in __init__: self.n = n.",
                "Changing it on one object leaves every other object alone.",
                "It hides a class attribute of the same name, for that object only.",
            ),
            example="""
                class A:
                    def __init__(self, n):
                        self.n = n
                a, b = A(1), A(2)
                a.n = 10
                print(a.n, b.n)
            """,
            out="10 2",
        ),
        javascript=dict(
            see=("class-attribute", "class", "this", "property"),
            rules=(
                "It is made on this, in the constructor (this.n = n) or as a class field (n = 0;).",
                "Changing it on one object leaves every other object alone.",
                "A class field such as items = [] makes a fresh array for each object.",
            ),
            example="""
                class A {
                  constructor(n) {
                    this.n = n;
                  }
                }
                const a = new A(1), b = new A(2);
                a.n = 10;
                console.log(a.n, b.n);
            """,
            out="10 2",
        ),
    ),
    *py(
        "static-method",
        "Static method",
        "A function that lives in a class's namespace but uses neither the object nor the class. It gets no self.",
        see=("class-method", "method", "class"),
        priority=50,
        aka=("staticmethod", "@staticmethod", "static methods"),
        detect=(r"@staticmethod\b",),
        rules=(
            "Mark it with @staticmethod and leave out self.",
            "Call it on the class or on an object: M.double(4) and M().double(4) both work.",
            "It cannot read or change the object's attributes, because it is never given the object.",
        ),
        example="""
            class M:
                @staticmethod
                def double(x):
                    return x * 2
            print(M.double(4), M().double(5))
        """,
        out="8 10",
    ),
    *py(
        "class-method",
        "Class method",
        "A method that receives the class itself (conventionally called cls) instead of one object. It is used for things that concern the whole class.",
        see=("static-method", "class-attribute", "method"),
        priority=50,
        aka=("classmethod", "@classmethod", "class methods", "cls"),
        detect=(r"@classmethod\b",),
        rules=(
            "Mark it with @classmethod; its first parameter is the class, usually named cls.",
            "It can change class attributes, which every object shares: cls.total += 1.",
            "It can be called on the class or on an object, and cls is the class either way.",
        ),
        example="""
            class Counter:
                total = 0
                @classmethod
                def bump(cls):
                    cls.total += 1
            Counter.bump()
            Counter.bump()
            print(Counter.total)
        """,
        out="2",
    ),
    *js(
        "static-method",
        "Static method",
        "A method marked static: it belongs to the class itself, not to the objects, so you call it on the class.",
        see=("class-attribute", "method", "class", "this"),
        priority=50,
        aka=("class method", "class methods", "static methods", "static member", "static members", "static"),
        detect=(r"\bstatic\b",),
        rules=(
            "Write static before the method: static double(x) { ... }; call it as M.double(4).",
            "An object made with new M() does not have it: new M().double is undefined.",
            "Inside it, this is the class itself, not an object.",
        ),
        example="""
            class M {
              static double(x) {
                return x * 2;
              }
            }
            console.log(M.double(4), typeof new M().double);
        """,
        out="8 undefined",
    ),
    *both(
        "inheritance",
        "Inheritance",
        "Making a new class that starts with everything another class has (its attributes and methods), and then adds or changes some.",
        see=("class", "subclass", "override", "super"),
        priority=60,
        aka=("inherit", "inherits", "inherited", "extends", "parent class", "base class", "child class"),
        python=dict(
            rules=(
                "class Dog(Animal): makes Dog inherit from Animal.",
                "A Dog object can use every Animal method that Dog does not replace.",
                "Python looks for a name on the object, then the class, then the parent classes in order (the method resolution order).",
            ),
            detect=(r"^[ \t]*class\s+\w+\s*\(\s*\w[^)]*\)\s*:",),
            example="""
                class Animal:
                    def speak(self):
                        return "..."
                class Dog(Animal):
                    pass
                print(Dog().speak())
            """,
            out="...",
        ),
        javascript=dict(
            rules=(
                "class Dog extends Animal makes Dog inherit from Animal.",
                "A Dog object can use every Animal method that Dog does not replace.",
                "JavaScript looks for a name on the object, then up its prototype chain: Dog.prototype, then Animal.prototype.",
            ),
            detect=(r"\bextends\b",),
            example="""
                class Animal {
                  speak() {
                    return "...";
                  }
                }
                class Dog extends Animal {}
                console.log(new Dog().speak());
            """,
            out="...",
        ),
    ),
    *both(
        "subclass",
        "Subclass",
        "A class that inherits from another. The class it inherits from is its parent (superclass).",
        priority=50,
        aka=("subclasses", "superclass", "parent", "child", "derived class", "base class", "sub-class"),
        python=dict(
            see=("inheritance", "override", "isinstance"),
            rules=(
                "In class Dog(Animal), Dog is the subclass and Animal the superclass.",
                "issubclass(Dog, Animal) is True; issubclass(Animal, Dog) is False. A class counts as a subclass of itself.",
                "An object of the subclass is also an object of the superclass: isinstance(Dog(), Animal) is True.",
            ),
            detect=(r"\bissubclass\(",),
            example="""
                class Animal: pass
                class Dog(Animal): pass
                print(issubclass(Dog, Animal), isinstance(Dog(), Animal), issubclass(Animal, Dog))
            """,
            out="True True False",
        ),
        javascript=dict(
            see=("inheritance", "override", "instanceof"),
            rules=(
                "In class Dog extends Animal, Dog is the subclass and Animal the superclass.",
                "An object of the subclass is also an instanceof the superclass: new Dog() instanceof Animal is true.",
                "The superclass is not an instance of the subclass: new Animal() instanceof Dog is false.",
            ),
            example="""
                class Animal {}
                class Dog extends Animal {}
                console.log(new Dog() instanceof Animal, new Animal() instanceof Dog, Object.getPrototypeOf(Dog) === Animal);
            """,
            out="true false true",
        ),
    ),
    *both(
        "override",
        "Override",
        "Writing a method in a subclass with the same name as one in its parent, so objects of the subclass use the new one.",
        see=("inheritance", "super", "method"),
        priority=55,
        aka=("overriding", "overrides", "overridden", "replace a method"),
        python=dict(
            rules=(
                "The subclass's version wins for the subclass's objects; the parent's objects still use the parent's version.",
                "Python overrides by NAME only: the parameters do not have to match.",
                "To also run the parent's version, call super().name(...) inside the new one.",
            ),
            example="""
                class A:
                    def hi(self):
                        return "A"
                class B(A):
                    def hi(self):
                        return "B"
                print(A().hi(), B().hi())
            """,
            out="A B",
        ),
        javascript=dict(
            rules=(
                "The subclass's version wins for the subclass's objects; the parent's objects still use the parent's version.",
                "JavaScript overrides by NAME only: the parameters do not have to match.",
                "To also run the parent's version, call super.name(...) inside the new one.",
            ),
            example="""
                class A {
                  hi() { return "A"; }
                }
                class B extends A {
                  hi() { return "B"; }
                }
                console.log(new A().hi(), new B().hi());
            """,
            out="A B",
        ),
    ),
    *both(
        "super",
        "super",
        "The way a subclass reaches its parent class: to run the parent's version of a method, or the parent's constructor.",
        see=("inheritance", "override", "method"),
        priority=55,
        aka=("super()", "super.", "parent method", "call the parent"),
        python=dict(
            rules=(
                "super().hi() runs the parent's hi on the same object.",
                "In __init__, super().__init__(...) lets the parent set up its attributes first.",
                "It follows the method resolution order, so with several parents it finds the next class in line.",
            ),
            detect=(r"\bsuper\(",),
            example="""
                class A:
                    def hi(self):
                        return "A"
                class B(A):
                    def hi(self):
                        return super().hi() + "B"
                print(B().hi())
            """,
            out="AB",
        ),
        javascript=dict(
            rules=(
                "super.hi() runs the parent's hi on the same object; super(...) calls the parent's constructor.",
                "In a subclass constructor, super(...) must run BEFORE you touch this, or it is a ReferenceError.",
                "If a subclass has no constructor of its own, JavaScript calls the parent's one for you.",
            ),
            detect=(r"\bsuper\b",),
            example="""
                class A {
                  hi() { return "A"; }
                }
                class B extends A {
                  hi() { return super.hi() + "B"; }
                }
                console.log(new B().hi());
            """,
            out="AB",
        ),
    ),
    *py(
        "method-resolution-order",
        "Method resolution order (MRO)",
        "The order in which Python searches a class and its parents for a name. The first class that has it wins.",
        see=("inheritance", "super", "override"),
        priority=50,
        aka=("mro", "__mro__", "resolution order", "lookup order"),
        detect=(r"\.__mro__|\.mro\(\)",),
        rules=(
            "It starts with the object's own class, then its parents; ClassName.__mro__ lists them.",
            "Every class ends with object, the parent of all classes.",
            "With several parents, class C(A, B) tries A before B.",
        ),
        example="""
            class A: pass
            class B(A): pass
            print([c.__name__ for c in B.__mro__])
        """,
        out="['B', 'A', 'object']",
    ),
    *js(
        "prototype-chain",
        "Prototype chain",
        "The line of objects JavaScript searches, in order, when you ask an object for a name it does not have itself.",
        see=("inheritance", "class", "override"),
        priority=50,
        aka=("prototype", "prototypes", "prototypal inheritance", "method resolution order", "mro", "__proto__", "lookup order"),
        detect=(r"\.prototype\b|\bgetPrototypeOf\(|__proto__",),
        rules=(
            "An object, then its class's prototype, then the parent class's prototype, up to Object.prototype.",
            "The first object that has the name wins; if none has it the answer is undefined.",
            "class Dog extends Animal sets Object.getPrototypeOf(Dog.prototype) to Animal.prototype.",
        ),
        example="""
            class A {
              hi() { return "A"; }
            }
            class B extends A {}
            const b = new B();
            console.log(Object.getPrototypeOf(b) === B.prototype, Object.getPrototypeOf(B.prototype) === A.prototype, b.hi());
        """,
        out="true true A",
    ),
    *py(
        "isinstance",
        "isinstance()",
        "A function that asks whether an object belongs to a class, or to any class that inherits from it.",
        see=("type", "inheritance", "subclass", "identity"),
        priority=55,
        aka=("isinstance()", "instanceof", "is instance", "type check", "type checking"),
        detect=(r"\bisinstance\(",),
        rules=(
            "isinstance(b, A) is True when b is an A or an object of a subclass of A.",
            "type(b) is A is stricter: it is False for a subclass object.",
            "A tuple of classes means 'any of these': isinstance(3, (int, str)) is True.",
            "bool is a subclass of int, so isinstance(True, int) is True.",
        ),
        example="""
            class A: pass
            class B(A): pass
            b = B()
            print(isinstance(b, A), type(b) is A, isinstance(3, (int, str)), isinstance(True, int))
        """,
        out="True False True True",
    ),
    *js(
        "instanceof",
        "instanceof",
        "An operator that asks whether an object was made by a class, or by a class that inherits from it.",
        see=("type", "inheritance", "subclass", "prototype-chain"),
        priority=55,
        aka=("isinstance", "is instance", "type check", "type checking"),
        detect=(r"\binstanceof\b",),
        rules=(
            "x instanceof A is true when A.prototype is somewhere on x's prototype chain, so subclass objects count.",
            "It is only for objects: 'a' instanceof String is false, because a plain string is not an object.",
            "For plain values use typeof; for arrays use Array.isArray.",
        ),
        example="""
            class A {}
            class B extends A {}
            console.log(new B() instanceof A, [] instanceof Array, "a" instanceof String, typeof "a");
        """,
        out="true true false string",
    ),
    *both(
        "string-representation",
        "String representation",
        "The text an object turns into when it is printed or joined to a string. By default it is not helpful, so a class can define its own.",
        priority=50,
        aka=("string representation", "printing", "printed form", "display text"),
        python=dict(
            see=("string", "method", "print", "f-string"),
            aka=("__str__", "__repr__", "repr", "str()", "repr()", "string representation", "printing", "printed form"),
            rules=(
                "__str__ is what print(obj), str(obj) and f'{obj}' use; __repr__ is the unambiguous version for debugging, and what a list shows for its items.",
                "With neither, you get something like <__main__.P object at 0x...>, which is rarely what you want.",
                "If only __repr__ is defined, print uses it too.",
            ),
            detect=(r"\bdef\s+__(?:str|repr)__\b",),
            example="""
                class P:
                    def __init__(self, n):
                        self.n = n
                    def __str__(self):
                        return f"P{self.n}"
                    def __repr__(self):
                        return f"P({self.n})"
                p = P(1)
                print(p, repr(p), [p], f"{p}")
            """,
            out="P1 P(1) [P(1)] P1",
        ),
        javascript=dict(
            see=("string", "method", "console-log", "template-literal"),
            aka=("tostring", "toString", "toString()", "string representation", "printing", "printed form", "display text"),
            rules=(
                "toString() is what String(obj), template literals and + with a string use.",
                "The default toString() gives '[object Object]', which is rarely what you want.",
                "console.log(obj) does not call toString: it shows the object's contents.",
            ),
            detect=(r"\btoString\s*\(",),
            example="""
                class P {
                  constructor(n) { this.n = n; }
                  toString() { return `P${this.n}`; }
                }
                const p = new P(1);
                console.log(String(p), `${p}`, "" + p, String({}));
            """,
            out="P1 P1 P1 [object Object]",
        ),
    ),
    *both(
        "state",
        "State",
        "What an object (or a program) remembers between one moment and the next, held in its attributes or variables.",
        see=("class", "reassign", "mutable"),
        priority=40,
        aka=("object state", "stateful", "remembers", "internal state"),
        python=dict(
            see=("class", "attribute", "reassign", "mutable"),
            rules=(
                "A method that changes self.n changes the object's state; later calls see the new value.",
                "Two objects of the same class have separate state unless they share a class attribute or a mutable value.",
                "A function with no state gives the same answer for the same arguments; an object with state may not.",
            ),
            example="""
                class Counter:
                    def __init__(self):
                        self.n = 0
                    def up(self):
                        self.n += 1
                c = Counter()
                c.up()
                c.up()
                print(c.n)
            """,
            out="2",
        ),
        javascript=dict(
            see=("class", "property", "reassign", "mutable"),
            rules=(
                "A method that changes this.n changes the object's state; later calls see the new value.",
                "Two objects of the same class have separate state unless they share a static field or a mutable value.",
                "A function with no state gives the same answer for the same arguments; an object with state may not.",
            ),
            example="""
                class Counter {
                  n = 0;
                  up() { this.n++; }
                }
                const c = new Counter();
                c.up();
                c.up();
                console.log(c.n);
            """,
            out="2",
        ),
    ),
    *js(
        "instance",
        "Instance",
        "One object made from a class with new. Each instance has its own properties.",
        see=("class", "instanceof", "property", "this"),
        priority=40,
        aka=("instances", "instantiate", "instantiation", "new object"),
        detect=(r"\bnew\s+[A-Z]\w*\s*\(",),
        rules=(
            "new Dog() runs the class's constructor and gives back a new instance.",
            "Two instances are different objects even with the same contents: new A() === new A() is false.",
            "x instanceof Dog asks whether x is an instance of Dog.",
        ),
        example="""
            class Dog {}
            const a = new Dog(), b = new Dog();
            console.log(a instanceof Dog, a === b);
        """,
        out="true false",
    ),
]
