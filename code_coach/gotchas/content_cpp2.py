"""Gotchas, C++ (second deck): built as C++17 with clang++/g++/MSVC; notes are in langs.py (the `cpp` entry).

Every card is defined behaviour in C++17: no signed overflow, no out-of-range access, no dangling reference, no
unsequenced writes, nothing that depends on the address of an object or on a hash container's order. About a third
are easy-looking on purpose (integer maths, precedence, copies, formatting), the rest are medium and hard.
"""

from __future__ import annotations

from .items import Item, make

q = make("cpp")

ITEMS: tuple[Item, ...] = (
    # ── Easy-looking: basics with a real trap ──────────────────────────────
    q("signed-unsigned-compare", r'''
        #include <iostream>

        int main() {
            int a = -1;
            unsigned b = 1;
            std::cout << (a < b) << (a < 1) << (-1 < 1u) << "\n";
        }
    ''', "010", ["111", "000", "011"],
      "Mixing signed and unsigned turns the signed one into a huge unsigned number",
      """When an int and an unsigned int meet in a comparison, the int is converted to unsigned, so -1 becomes
      4294967295 and is no longer less than 1. Compared with a plain `1` (an int) nothing is converted and -1 < 1
      holds."""),

    q("division-and-modulo", r'''
        #include <iostream>

        int main() {
            std::cout << 7 / 2 << " " << 7 % 3 << " " << -7 / 2 << " "
                      << -7 % 3 << "\n";
        }
    ''', "3 1 -3 -1", ["3 1 -4 2", "3.5 1 -3.5 -1", "3 1 -3 2"],
      "Integer division truncates toward zero, and % takes the sign of the left side",
      """Since C++11 the quotient is cut toward zero, so -7 / 2 is -3, and the remainder is whatever makes
      `(a / b) * b + a % b == a` true, which gives -7 % 3 == -1. There is no flooring as in Python."""),

    q("shift-and-bitand-precedence", r'''
        #include <iostream>

        int main() {
            std::cout << (1 << 2 + 1) << " " << (6 & 3 == 3) << "\n";
        }
    ''', "8 0", ["5 0", "8 1", "5 1"],
      "+ binds tighter than <<, and == binds tighter than &",
      """`1 << 2 + 1` is `1 << 3`, which is 8, not `(1 << 2) + 1`. In `6 & 3 == 3` the comparison happens first and
      gives 1, so it is `6 & 1`, which is 0."""),

    q("plus-equals-char-arithmetic", r'''
        #include <iostream>
        #include <string>

        int main() {
            std::string s = "ab";
            s += 'c' + 1;
            std::cout << s << "\n";
        }
    ''', "abd", ["ab100", "abc1", "abc"],
      "'c' + 1 is the int 100, and += narrows it back to a char",
      """The sum is an int, but `std::string::operator+=` takes a char, so 100 becomes the character 'd' and is
      appended; it is never turned into the text "100". Appending a number as text needs `std::to_string`."""),

    q("vector-parens-vs-braces", r'''
        #include <iostream>
        #include <vector>

        int main() {
            std::vector<int> a(3, 1);
            std::vector<int> b{3, 1};
            std::cout << a.size() << " " << b.size() << "\n";
        }
    ''', "3 2", ["2 3", "3 3", "2 2"],
      "Parentheses mean (count, value); braces mean a list of two elements",
      """`a(3, 1)` calls the size-and-fill constructor, giving three ones. `b{3, 1}` prefers the
      `initializer_list<int>` constructor, so it holds the two elements 3 and 1."""),

    q("array-equals-is-address", r'''
        #include <iostream>
        #include <string>

        int main() {
            char a[] = "hi";
            char b[] = "hi";
            std::cout << (a == b) << (std::string(a) == b) << "\n";
        }
    ''', "01", ["11", "00", "10"],
      "== on two char arrays compares where they live, not what they hold",
      """Both arrays decay to pointers to their first element, and two separate arrays are at different
      addresses, so the first test is false. Once one side is a `std::string`, `==` compares the characters."""),

    q("range-for-copies", r'''
        #include <iostream>
        #include <vector>

        int main() {
            std::vector<int> v{1, 2, 3};
            for (auto x : v) x *= 2;
            std::cout << v[0];
            for (auto &x : v) x *= 2;
            std::cout << v[0] << "\n";
        }
    ''', "12", ["22", "24", "11"],
      "`auto x` copies each element; only `auto &x` changes the vector",
      """The first loop doubles private copies and throws them away, so `v[0]` is still 1. The second loop binds
      references to the real elements, so `v[0]` becomes 2."""),

    q("capture-by-value-snapshot", r'''
        #include <iostream>

        int main() {
            int x = 1;
            auto byValue = [x] { return x; };
            auto byRef = [&x] { return x; };
            x = 2;
            std::cout << byValue() << byRef() << "\n";
        }
    ''', "12", ["22", "11", "21"],
      "A by-value capture is a copy taken when the lambda is created",
      """`[x]` stores 1 inside the lambda at the moment it is made, and later changes to the outer `x` do not
      reach it. `[&x]` refers to the live variable, so it sees the 2."""),

    q("short-circuit-increments", r'''
        #include <iostream>

        int main() {
            int i = 0;
            bool a = (i++ > 0) && (i++ > 0);
            bool b = (i++ == 1) || (i++ > 0);
            std::cout << i << " " << a << " " << b << "\n";
        }
    ''', "2 0 1", ["4 0 1", "3 0 1", "2 0 0"],
      "&& and || skip the right side as soon as the answer is known",
      """The first `i++ > 0` is false, so `&&` never evaluates its right side; `i` is 1. The next `i++ == 1` is
      true, so `||` skips its right side as well; `i` ends at 2."""),

    q("switch-falls-through", r'''
        #include <iostream>
        #include <string>

        int main() {
            std::string s;
            switch (2) {
                case 1: s += 'a';
                case 2: s += 'b';
                case 3: s += 'c'; break;
                case 4: s += 'd';
            }
            std::cout << s << "\n";
        }
    ''', "bc", ["b", "bcd", "c"],
      "Without `break`, execution runs on into the next case",
      """The switch jumps to `case 2`, appends 'b', and carries on into `case 3` because there is no `break`
      after it; the `break` after 'c' stops it before `case 4`."""),

    q("enum-counts-on", r'''
        #include <iostream>

        enum E { A = 1, B, C = 10, D };

        int main() {
            std::cout << A << " " << B << " " << C << " " << D << "\n";
        }
    ''', "1 2 10 11", ["1 2 10 10", "0 1 10 11", "1 2 3 4"],
      "An enumerator without a value is the previous one plus one",
      """B has no value, so it is A + 1, which is 2. D follows C, which was set to 10, so D is 11. An unscoped
      enum prints as its integer value."""),

    q("reference-cannot-rebind", r'''
        #include <iostream>

        int main() {
            int a = 1, b = 2;
            int &r = a;
            r = b;
            r++;
            std::cout << a << " " << b << "\n";
        }
    ''', "3 2", ["1 3", "2 2", "3 3"],
      "Assigning to a reference assigns to what it refers to; it never re-points",
      """`r = b` copies b's value into `a`, so `a` is 2. `r` still names `a`, so `r++` makes it 3, and `b` is
      untouched."""),

    q("assignment-in-condition", r'''
        #include <iostream>

        int main() {
            int x = 0;
            if (x = 5) std::cout << "yes ";
            if (x == 5) std::cout << "five ";
            std::cout << x << "\n";
        }
    ''', "yes five 5", ["five 0", "yes 0", "5"],
      "A single = in a condition assigns, and the assigned value is the test",
      """`x = 5` stores 5 in `x` and evaluates to 5, which is true, so "yes " prints and `x` is now 5. That is
      why the second test, `x == 5`, also succeeds."""),

    q("loop-counter-after-loop", r'''
        #include <iostream>

        int main() {
            int i;
            for (i = 10; i > 0; i -= 3) {}
            std::cout << i << "\n";
        }
    ''', "-2", ["1", "0", "-3"],
      "The counter keeps the value that made the condition fail",
      """The loop sees 10, 7, 4 and 1, all greater than 0, and subtracts 3 once more to reach -2. Only then does
      `i > 0` fail, so the variable is left at -2, not at the last value the body saw."""),

    q("array-partial-init", r'''
        #include <iostream>

        int main() {
            int a[4] = {1, 2};
            std::cout << a[0] << a[1] << a[2] << a[3] << "\n";
        }
    ''', "1200", ["1212", "1222", "1111"],
      "Elements with no initialiser in a braced list are zero",
      """Once an array has an initialiser list, every element beyond it is value-initialised, which is 0 for an
      int. The list is not repeated or extended with the last value."""),

    q("bool-conversions", r'''
        #include <iostream>

        int main() {
            bool a = 5, b = 0.1, c = -1;
            int n = true + true;
            std::cout << a << " " << b << " " << c << " " << n << "\n";
        }
    ''', "1 1 1 2", ["5 0 -1 2", "1 0 1 2", "1 1 1 1"],
      "Any non-zero value becomes true, and true is the number 1 in arithmetic",
      """Converting to bool asks only "is it non-zero?", so 5, 0.1 and -1 are all true and print as 1. In
      arithmetic `true` is promoted to the int 1, so `true + true` is 2."""),

    q("literal-plus-one", r'''
        #include <iostream>
        #include <string>

        int main() {
            std::cout << "hello" + 1 << " ";
            std::cout << "hello" + std::string("1") << "\n";
        }
    ''', "ello hello1", ["hello1 hello1", "ello ello1", "hello1 ello"],
      "A string literal plus an int moves the pointer; it does not append text",
      """`"hello"` decays to a `const char*`, and adding 1 points at the second character, so the stream prints
      "ello". Only when one side is a `std::string` does `+` concatenate."""),

    q("missing-comma-concatenates", r'''
        #include <iostream>
        #include <string>
        #include <vector>

        int main() {
            std::vector<std::string> v = {"a", "b" "c", "d"};
            std::cout << v.size() << " " << v[1] << "\n";
        }
    ''', "3 bc", ["4 b", "3 b", "2 bc"],
      "Adjacent string literals are joined into one at compile time",
      """`"b" "c"` has no comma between the literals, so the compiler glues them into the single string "bc".
      The vector therefore has three elements, not four."""),

    q("substr-takes-a-length", r'''
        #include <iostream>
        #include <string>

        int main() {
            std::string s = "hello world";
            std::cout << s.substr(6, 3) << "|" << s.substr(6) << "|"
                      << s.substr(2, 0) << "|\n";
        }
    ''', "wor|world||", ["wor|wor||", "worl|world||", "wor|world|ll|"],
      "substr(pos, len): the second argument is a count, not an end index",
      """`substr(6, 3)` takes three characters starting at index 6, which is "wor". With one argument it runs to
      the end of the string, and a length of 0 gives the empty string."""),

    q("octal-literal", r'''
        #include <iostream>

        int main() {
            std::cout << 010 + 1 << " " << 0x1F << " " << 0b101 << "\n";
        }
    ''', "9 31 5", ["11 31 5", "9 31 101", "10 31 5"],
      "A leading zero makes an integer literal octal",
      """`010` is octal, so it is 8 and `010 + 1` is 9. `0x1F` is hexadecimal 31, and `0b101` is a binary literal
      (C++14) worth 5; the stream prints all of them in decimal."""),

    # ── Medium: classes, copies, overloads, the standard library ───────────
    q("default-argument-static-type", r'''
        #include <iostream>

        struct B {
            virtual void f(int x = 1) { std::cout << "B" << x; }
        };
        struct D : B {
            void f(int x = 2) override { std::cout << "D" << x; }
        };

        int main() {
            D d;
            B &r = d;
            r.f();
            d.f();
            std::cout << "\n";
        }
    ''', "D1D2", ["D2D2", "B1D2", "D1D1"],
      "The function called is chosen at run time, its default argument at compile time",
      """`r` is a `B&`, so the compiler fills in B's default of 1, but the virtual call still lands in D::f. The
      result is D's body with B's default. Calling through the `D` object uses D's default of 2."""),

    q("slicing-in-a-vector", r'''
        #include <iostream>
        #include <vector>

        struct A { virtual int f() const { return 1; } };
        struct B : A { int f() const override { return 2; } };

        int main() {
            std::vector<A> v;
            B b;
            v.push_back(b);
            A *p = &b;
            std::cout << v[0].f() << p->f() << "\n";
        }
    ''', "12", ["22", "11", "21"],
      "A vector<A> stores A objects, so a pushed B is cut down to its A part",
      """`push_back` copies the argument into an element of type `A`, which keeps only the base sub-object, so
      virtual dispatch on it finds A::f. The pointer to the original `B` still dispatches to B::f."""),

    q("virtual-call-in-constructor", r'''
        #include <iostream>

        struct A {
            A() { who(); }
            virtual void who() { std::cout << "A"; }
        };
        struct B : A {
            B() { who(); }
            void who() override { std::cout << "B"; }
        };

        int main() {
            B b;
            b.who();
            std::cout << "\n";
        }
    ''', "ABB", ["BBB", "ABA", "AAA"],
      "While a base constructor runs, the object is only a base",
      """Inside `A()` the derived part does not exist yet, so the virtual call resolves to A::who and prints A.
      Inside `B()` the object is a B, and the later call from `main` is fully virtual: B and B."""),

    q("temporary-lifetimes", r'''
        #include <iostream>
        struct T {
            char n;
            T(char c) : n(c) { std::cout << '+' << n; }
            ~T() { std::cout << '-' << n; }
        };
        int main() {
            {
                T('t');
                T a('a');
                const T &r = T('r');
                std::cout << "|";
            }
            std::cout << "\n";
        }
    ''', "+t-t+a+r|-r-a", ["+t+a+r|-r-a-t", "+t-t+a+r|-a-r", "+t+a+r-t|-r-a"],
      "A plain temporary dies at the semicolon, but one bound to a const reference lives on",
      """`T('t')` is destroyed at the end of its statement, before `a` exists. The temporary bound to `r` has
      its lifetime extended to the end of the block, and locals are destroyed in reverse order, so `r` goes
      before `a`."""),

    q("member-init-order", r'''
        #include <iostream>
        struct M {
            char c;
            M(char k) : c(k) { std::cout << '+' << c; }
            ~M() { std::cout << '-' << c; }
        };
        struct P {
            M x, y;
            P() : y('y'), x('x') {}
        };
        int main() {
            { P p; }
            std::cout << "\n";
        }
    ''', "+x+y-y-x", ["+y+x-x-y", "+y+x-y-x", "+x+y-x-y"],
      "Members are built in the order they are declared, not the order of the init list",
      """The constructor lists `y` first, but `x` is declared first, so `x` is constructed first. Destruction
      always runs in the exact reverse of construction."""),

    q("static-initialisation-order", r'''
        #include <iostream>

        int tick(char c) { std::cout << c; return 1; }

        int g = tick('g');

        void f() { static int s = tick('s'); }

        int main() {
            std::cout << 'm';
            f();
            f();
            std::cout << "\n";
        }
    ''', "gms", ["gmss", "msg", "sgm"],
      "Globals start before main; a function-local static starts on its first call",
      """`g` is initialised before `main` begins, so its 'g' comes first. The static inside `f` is constructed
      the first time control passes its declaration and never again, so 's' appears once, after 'm'."""),

    q("initializer-list-wins-braces", r'''
        #include <initializer_list>
        #include <iostream>

        struct S {
            S(int, int) { std::cout << "pair "; }
            S(std::initializer_list<int>) { std::cout << "list "; }
        };

        int main() {
            S a(1, 2);
            S b{1, 2};
            S c = {1, 2};
            std::cout << "\n";
        }
    ''', "pair list list", ["pair pair pair", "list list list", "pair pair list"],
      "Braces prefer an initializer_list constructor whenever one fits",
      """Parentheses never consider the list constructor, so `a` uses (int, int). With braces, overload
      resolution tries the `initializer_list<int>` constructor first, and it matches, so `b` and `c` both use
      it."""),

    q("auto-drops-const-and-reference", r'''
        #include <iostream>
        #include <type_traits>

        int main() {
            const int c = 1;
            auto a = c;
            auto &b = c;
            using B = std::remove_reference_t<decltype(b)>;
            std::cout << std::is_const_v<decltype(a)> << std::is_const_v<B>
                      << "\n";
        }
    ''', "01", ["11", "00", "10"],
      "auto by value drops const; auto& keeps it",
      """`auto a = c` copies the value into a new, non-const int, so `a` is plain `int`. `auto &b = c` has to
      bind to the original, so it deduces `const int` and `b` is `const int&`."""),

    q("uint8-promotes-to-int", r'''
        #include <cstdint>
        #include <iostream>

        int main() {
            std::uint8_t a = 200, b = 100;
            std::cout << (a + b) << " " << int(std::uint8_t(a + b)) << " "
                      << int(std::uint8_t(~a)) << "\n";
        }
    ''', "300 44 55", ["44 44 55", "300 300 55", "300 44 -201"],
      "Small integers are promoted to int before any arithmetic happens",
      """`a + b` is computed as ints, so it is 300; only converting back to `uint8_t` wraps it to 44. Likewise
      `~a` is the int -201, and squeezing that into a byte gives 55."""),

    q("unsigned-wraps-around", r'''
        #include <cstdint>
        #include <iostream>

        int main() {
            std::uint32_t a = 4000000000u;
            std::uint32_t b = a + a;
            std::uint32_t z = 0;
            --z;
            std::cout << b << " " << z << "\n";
        }
    ''', "3705032704 4294967295", ["8000000000 -1", "3705032704 -1", "8000000000 4294967295"],
      "Unsigned arithmetic wraps modulo 2^32 and is fully defined",
      """The true sum 8,000,000,000 does not fit in 32 bits, so it wraps to 8,000,000,000 - 2^32 = 3,705,032,704.
      Decrementing an unsigned 0 gives the largest value, 4,294,967,295, never -1."""),

    q("narrow-product", r'''
        #include <cstdint>
        #include <iostream>

        int main() {
            std::uint16_t a = 300;
            std::cout << a * a << " " << std::uint16_t(a * a) << "\n";
        }
    ''', "90000 24464", ["24464 24464", "90000 90000", "90000 -41072"],
      "uint16_t times uint16_t is an int, so it only wraps when you convert back",
      """Both operands are promoted to int, so the product is the full 90000. Converting it to `uint16_t` keeps
      it modulo 65536, which is 24464."""),

    q("shifts-on-unsigned", r'''
        #include <cstdint>
        #include <iostream>

        int main() {
            std::uint32_t x = 1;
            std::cout << (x << 31) << " " << (x << 31 >> 31) << " "
                      << (0xFFu >> 4) << "\n";
        }
    ''', "2147483648 1 15", ["-2147483648 -1 15", "2147483648 0 15", "2147483648 1 255"],
      "Unsigned shifts are plain bit moves; the top bit is just a big number",
      """With an unsigned type, 1 << 31 is 2147483648 and shifting it back down fills with zeros, so the result
      is 1. `0xFFu >> 4` drops the low four bits and leaves 15."""),

    q("mutable-lambda-copy", r'''
        #include <iostream>

        int main() {
            int n = 0;
            auto f = [n]() mutable { return ++n; };
            auto g = f;
            f();
            f();
            std::cout << f() << " " << g() << " " << n << "\n";
        }
    ''', "3 1 0", ["3 4 3", "3 1 3", "3 3 0"],
      "A mutable lambda changes its own copy, and copying the lambda copies that state",
      """The captured `n` lives inside `f`, so the outer `n` stays 0. `g` was copied before any call, so it has
      its own counter starting at 0 and its first call returns 1."""),

    q("overload-ranking", r'''
        #include <iostream>

        void f(int) { std::cout << 'i'; }
        void f(long) { std::cout << 'l'; }
        void f(double) { std::cout << 'd'; }
        void f(const char *) { std::cout << 'p'; }

        int main() {
            f('a'); f(1.5f); f(0L); f(true); f(nullptr);
            std::cout << "\n";
        }
    ''', "idlip", ["iilip", "ildip", "idlid"],
      "Promotions beat conversions: char and bool go to int, float goes to double",
      """`char` and `bool` are promoted to `int`, and `float` is promoted to `double`, which are better than any
      other conversion. `0L` is exactly a long, and `nullptr` converts only to the pointer overload."""),

    q("pointer-beats-string", r'''
        #include <iostream>
        #include <string>

        void g(bool) { std::cout << "bool"; }
        void g(const std::string &) { std::cout << "string"; }

        int main() {
            g("hello");
            std::cout << "\n";
        }
    ''', "bool", ["string", "bool string", "hello"],
      "A literal becomes a bool through the pointer before it becomes a std::string",
      """"hello" decays to a `const char*`, and a pointer-to-bool conversion is a standard conversion. Building
      a `std::string` needs a user-defined conversion, which always ranks lower, so `g(bool)` wins."""),

    q("const-overload-chosen-by-object", r'''
        #include <iostream>
        #include <utility>
        struct W {
            int v = 0;
            int &at() { std::cout << "nc "; return v; }
            const int &at() const { std::cout << "c "; return v; }
        };

        int main() {
            W w;
            const W &cw = w;
            w.at();
            cw.at();
            std::as_const(w).at();
            std::cout << "\n";
        }
    ''', "nc c c", ["nc nc c", "c c c", "nc c nc"],
      "Which overload runs depends on the constness of the object, not of the call",
      """A non-const `w` picks the non-const `at`. Through a reference to const, or through `std::as_const`, the
      object is const, so the const overload is the only one allowed."""),

    q("copy-move-and-elision", r'''
        #include <iostream>
        #include <utility>

        struct T {
            T() { std::cout << "D"; }
            T(const T &) { std::cout << "C"; }
            T(T &&) noexcept { std::cout << "M"; }
        };

        int main() {
            T a = T();
            T b = a;
            T c = std::move(b);
            std::cout << "\n";
        }
    ''', "DCM", ["DMCM", "DCC", "DDCM"],
      "`T a = T()` builds the object in place; copy for an lvalue, move for std::move",
      """Since C++17 initialising from a prvalue like `T()` does not create a temporary at all, so only the
      default constructor runs. `b = a` copies an lvalue, and `std::move(b)` casts to an rvalue so `c` is move
      constructed."""),

    q("move-from-const-copies", r'''
        #include <iostream>
        #include <string>
        #include <utility>

        int main() {
            const std::string a = "hello";
            std::string b = std::move(a);
            std::cout << a.size() << " " << b.size() << "\n";
        }
    ''', "5 5", ["0 5", "5 0", "0 0"],
      "std::move only casts; a const object cannot be stolen from, so it is copied",
      """The move constructor takes a non-const rvalue reference, which a `const std::string` cannot supply. The
      copy constructor accepts a const rvalue, so `b` gets a copy and `a` is left intact."""),

    q("unique-ptr-after-move", r'''
        #include <iostream>
        #include <memory>

        int main() {
            auto p = std::make_unique<int>(5);
            auto q = std::move(p);
            std::cout << (p == nullptr) << " " << *q << "\n";
        }
    ''', "1 5", ["0 5", "1 0", "0 0"],
      "Moving a unique_ptr leaves the source empty, by guarantee",
      """Only one `unique_ptr` can own the int, so the move transfers ownership and sets the source to null.
      The new owner `q` still reads the value 5."""),

    q("shared-use-count", r'''
        #include <iostream>
        #include <memory>

        int main() {
            auto a = std::make_shared<int>(1);
            auto b = a;
            std::weak_ptr<int> w = a;
            std::cout << a.use_count();
            {
                auto c = a;
                std::cout << " " << a.use_count();
            }
            std::cout << " " << a.use_count() << "\n";
        }
    ''', "2 3 2", ["3 4 3", "2 3 3", "2 2 2"],
      "weak_ptr does not count as an owner; each shared_ptr copy does",
      """`a` and `b` are two owners, and `w` is only an observer, so the count starts at 2. The copy `c` makes
      it 3, and it drops back to 2 when `c` goes out of scope."""),

    # ── Hard but legal ─────────────────────────────────────────────────────
    q("vector-bool-proxy", r'''
        #include <iostream>
        #include <vector>

        int main() {
            std::vector<bool> v{true, true};
            auto b = v[0];
            bool c = v[0];
            v[0] = false;
            std::cout << b << c << "\n";
        }
    ''', "01", ["11", "00", "10"],
      "vector<bool> packs bits, so v[0] is a proxy that stays connected to the vector",
      """`auto b = v[0]` does not give a `bool`; it gives a reference-like proxy object for that bit, so it
      reads whatever the bit holds later, which is false. `bool c = v[0]` really copies the value true."""),

    q("specialisation-vs-overload", r'''
        #include <iostream>

        template <class T> void p(T) { std::cout << "T"; }
        template <> void p<int *>(int *) { std::cout << "S"; }
        template <class T> void p(T *) { std::cout << "P"; }

        int main() {
            int x = 0;
            p(&x);
            p<int *>(&x);
            std::cout << "\n";
        }
    ''', "PS", ["SS", "PP", "SP"],
      "Specialisations belong to a template; overload resolution never sees them",
      """The explicit specialisation `p<int*>` specialises the first template, but plain `p(&x)` picks between
      the templates, and the pointer overload is more specialised, so it wins and prints P. Asking for
      `p<int*>` by name selects the first template and therefore its specialisation S."""),

    q("forwarding-reference-deduction", r'''
        #include <iostream>
        #include <type_traits>
        #include <utility>

        template <class T>
        bool lv(T &&) { return std::is_lvalue_reference<T>::value; }

        int main() {
            int x = 0;
            const int c = 1;
            std::cout << lv(x) << lv(0) << lv(std::move(x)) << lv(c) << "\n";
        }
    ''', "1001", ["1111", "1011", "0001"],
      "T&& on a template parameter is a forwarding reference, not an rvalue reference",
      """For an lvalue such as `x` or `c`, T is deduced as a reference type (`int&`, `const int&`), so the test is
      true. For an rvalue like `0` or `std::move(x)`, T is deduced as a plain `int` and the test is false."""),

    q("throw-copy-slices", r'''
        #include <iostream>

        struct E { virtual const char *what() const { return "E"; } };
        struct F : E { const char *what() const override { return "F"; } };

        int main() {
            try {
                try { throw F(); }
                catch (E &e) { throw e; }
            } catch (E &e) { std::cout << e.what(); }
            try {
                try { throw F(); }
                catch (E &) { throw; }
            } catch (E &e) { std::cout << e.what() << "\n"; }
        }
    ''', "EF", ["FF", "EE", "FE"],
      "`throw e;` throws a copy of the static type; a bare `throw;` rethrows the original",
      """The first handler's `e` is declared as `E&`, so `throw e;` copies only the E part and throws a brand
      new, sliced E. A bare `throw;` rethrows the exception object that is in flight, which is still the F."""),

    q("virtual-base-built-once", r'''
        #include <iostream>

        struct A { A() { std::cout << "A"; } };
        struct B : virtual A { B() { std::cout << "B"; } };
        struct C : virtual A { C() { std::cout << "C"; } };
        struct D : B, C { D() { std::cout << "D"; } };

        int main() {
            D d;
            std::cout << "\n";
        }
    ''', "ABCD", ["ABACD", "ACBD", "ABDC"],
      "A virtual base is built once, first, by the most derived class",
      """With `virtual` inheritance there is only one A inside a D, and it is constructed before everything
      else. Then the direct bases follow in the order they are declared, B and then C, and finally D itself.
      Without `virtual`, A would be built twice."""),

    q("setprecision-then-fixed", r'''
        #include <iomanip>
        #include <iostream>

        int main() {
            std::cout << std::setprecision(3) << 3.14159 << " " << 1234.5
                      << " " << std::fixed << 2.0 << " " << 1234.5 << "\n";
        }
    ''', "3.14 1.23e+03 2.000 1234.500",
      ["3.14 1235 2.00 1234.50", "3.142 1234.500 2.000 1234.500", "3.14 1.23e+03 2 1234.5"],
      "By default precision counts significant digits; after `fixed` it counts decimals",
      """Both manipulators are sticky. Without `fixed`, three digits cannot show 1234.5, so it switches to
      scientific form 1.23e+03. After `std::fixed` the same 3 means digits after the point."""),

    q("stream-operator-left-to-right", r'''
        #include <iostream>

        int main() {
            int i = 0;
            std::cout << i++ << i++ << i++ << "\n";
        }
    ''', "012", ["210", "000", "123"],
      "Since C++17, the operands of << are evaluated left to right",
      """C++17 sequences the left operand of `<<` before the right one, including for the overloaded stream
      operator, so the three increments run in the order written and print 0, 1 and 2. Before C++17 the order
      was unspecified."""),

    q("accumulate-takes-its-type-from-init", r'''
        #include <iostream>
        #include <numeric>
        #include <vector>

        int main() {
            std::vector<double> v{0.5, 1.5, 2.5};
            auto s = std::accumulate(v.begin(), v.end(), 0);
            auto t = std::accumulate(v.begin(), v.end(), 0.0);
            std::cout << s << " " << t << "\n";
        }
    ''', "3 4.5", ["4 4.5", "4.5 4.5", "3 4"],
      "accumulate keeps its running total in the type of the initial value",
      """With `0` the total is an int, so after each step 0.5, 1.5 and 3.5 are truncated to 0, 1 and 3. Passing
      `0.0` makes the total a double, and the sum is the expected 4.5."""),

    q("map-insert-keeps-the-old-value", r'''
        #include <iostream>
        #include <map>
        #include <string>

        int main() {
            std::map<std::string, int> m;
            m["a"] = 1;
            m.insert({"a", 2});
            m["b"] = 3;
            m["b"] = 4;
            m.emplace("b", 5);
            std::cout << m["a"] << " " << m["b"] << " " << m.size() << "\n";
        }
    ''', "1 4 2", ["2 5 2", "2 4 2", "1 4 4"],
      "insert and emplace never overwrite an existing key; operator[] assignment does",
      """`insert({"a", 2})` and `emplace("b", 5)` do nothing when the key already exists, so `a` stays 1. Only
      `m["b"] = 4` replaces the value. The map holds just the two keys."""),

    q("find-returns-unsigned-npos", r'''
        #include <iostream>
        #include <string>

        int main() {
            std::string s = "abc";
            std::cout << (s.find('z') == -1) << (s.find('z') < 0)
                      << (s.find('b') == 1) << "\n";
        }
    ''', "101", ["111", "001", "010"],
      "find returns an unsigned npos, so `< 0` can never be true",
      """`npos` is the largest size_t. Comparing it with `-1` converts the -1 to the same value, so `== -1` is
      true, but nothing unsigned is ever less than 0. That is why the idiom is `!= std::string::npos`."""),
)
