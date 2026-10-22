"""Gotchas, C++ (third deck): built as C++17 with clang++/g++/MSVC; notes are in langs.py (the `cpp` entry).

Same rules as content_cpp2.py: defined behaviour in C++17, nothing that depends on an address, a hash container's
order, a moved-from object's contents or an unspecified evaluation order (the chained `<<` cards rely on C++17's
guaranteed left-to-right sequencing of shifts, which is why the deck is C++17). This one is the library side (vector
growth, string_view, optional/variant, the algorithms, the stream manipulators) and the lambda, constructor and
destructor ordering cards that the first two decks did not reach.
"""

from __future__ import annotations

from .items import Item, make

q = make("cpp")

ITEMS: tuple[Item, ...] = (
    # ── Batch 1: containers and the library ────────────────────────────────
    q("vector-fill-makes-separate-rows", r'''
        #include <iostream>
        #include <vector>

        int main() {
            std::vector<std::vector<int>> g(3, std::vector<int>(2, 7));
            g[1][0] = 1;
            g[2].push_back(5);
            std::cout << g[0][0] << " " << g[1][0] << " " << g[2][0] << " "
                      << g[2].size() << "\n";
        }
    ''', "7 1 7 3", ["1 1 1 3", "7 1 7 2", "7 1 1 3"],
      "The fill constructor copies the row, so every row is its own vector",
      """`g(3, row)` stores three independent copies of `row`. Changing `g[1][0]` or growing `g[2]`
      does not touch the others, unlike `[[0] * 2] * 3` in Python, which repeats one list."""),

    q("vector-grows-by-copy-unless-move-is-noexcept", r'''
        #include <iostream>
        #include <vector>
        template <bool NE> struct T {
            static inline int c = 0, m = 0;
            T() = default;
            T(const T&) { ++c; }
            T(T&&) noexcept(NE) { ++m; }
        };

        int main() {
            std::vector<T<false>> a; std::vector<T<true>> b;
            a.emplace_back(); a.emplace_back();
            b.emplace_back(); b.emplace_back();
            std::cout << T<false>::c << T<false>::m << " "
                      << T<true>::c << T<true>::m << "\n";
        }
    ''', "10 01", ["01 01", "00 00", "10 10"],
      "On reallocation a vector only moves its elements if the move constructor is noexcept",
      """The second emplace_back needs more room and relocates the first element. To keep its
      strong guarantee, vector copies when the move might throw, and moves only when it is noexcept."""),

    q("copy-construction-is-not-assignment", r'''
        #include <iostream>
        #include <string>
        std::string trace;

        struct T {
            T() { trace += "D "; }
            T(const T&) { trace += "C "; }
            T& operator=(const T&) { trace += "A "; return *this; }
        };

        int main() {
            T a, c;
            T b = a;
            c = a;
            std::cout << trace << "\n";
        }
    ''', "D D C A", ["D D A A", "D D C C", "D C D A"],
      "`T b = a;` builds a new object with the copy constructor; only `c = a;` assigns",
      """`T a, c;` makes two default objects. The `=` in `T b = a;` is initialisation, not assignment, so it
      calls the copy constructor. `c = a;` works on an object that already exists, so it calls operator=."""),

    q("conversion-operator-in-expressions", r'''
        #include <iostream>

        struct Five {
            operator int() const { return 5; }
        };

        int main() {
            Five f;
            std::cout << f << " " << f + 1 << " " << f / 2 << " " << f / 2.0
                      << "\n";
        }
    ''', "5 6 2 2.5", ["5 6 2.5 2.5", "5 6 2 2", "5 5 2 2.5"],
      "An object with operator int behaves as that int, and the usual arithmetic rules follow",
      """`f` is converted to the int 5 wherever a number is wanted: printing, `+ 1`, `/ 2`. Then
      the normal rules apply, so `5 / 2` is integer division (2) and `5 / 2.0` is a double (2.5)."""),

    q("string-view-is-a-window", r'''
        #include <iostream>
        #include <string>
        #include <string_view>

        int main() {
            std::string s = "hello world";
            std::string_view v = s;
            v.remove_prefix(6);
            s[6] = 'W';
            std::cout << v << " " << s.size() << " " << v.size() << " " << s
                      << "\n";
        }
    ''', "World 11 5 hello World", ["world 11 5 hello World", "World 5 5 hello World",
                                    "world 5 5 hello world"],
      "A string_view does not copy: it sees later changes, and remove_prefix only moves its edge",
      """`remove_prefix(6)` shrinks the view (5 characters left) but leaves the string alone, still 11.
      Because the view points at the string's own characters, the later `s[6] = 'W'` shows through it."""),

    q("optional-holding-zero-is-engaged", r'''
        #include <iostream>
        #include <optional>

        int main() {
            std::optional<int> a = 0;
            std::optional<int> b;
            std::cout << bool(a) << " " << bool(b) << " " << a.value_or(9) << " "
                      << b.value_or(9) << "\n";
        }
    ''', "1 0 0 9", ["0 0 0 9", "1 0 9 9", "0 0 9 9"],
      "An optional is true when it holds a value, even if that value is 0",
      """The test is about presence, not about what is inside. `a` holds 0, so it is true and
      `value_or(9)` gives its 0. `b` is empty, so it is false and `value_or(9)` gives 9."""),

    q("variant-starts-as-its-first-alternative", r'''
        #include <iostream>
        #include <string>
        #include <variant>

        int main() {
            std::variant<std::string, int> v;
            std::cout << v.index() << " [" << std::get<0>(v) << "] ";
            v = 42;
            std::cout << v.index() << " " << std::get<int>(v) << "\n";
        }
    ''', "0 [] 1 42", ["1 [] 2 42", "0 [0] 1 42", "0 [] 0 42"],
      "A default-constructed variant holds a default value of its first type, index 0",
      """There is no 'empty' state: `v` starts as an empty string, index 0. Assigning 42 switches it
      to the `int` alternative, whose index is 1 (indices start at 0)."""),

    q("map-keys-sort-as-text", r'''
        #include <iostream>
        #include <map>
        #include <string>

        int main() {
            std::map<std::string, int> m;
            for (int n : {9, 10, 100, 8}) m[std::to_string(n)] = n;
            for (const auto& kv : m) std::cout << kv.first << " ";
            std::cout << "\n";
        }
    ''', "10 100 8 9", ["8 9 10 100", "100 10 9 8", "9 10 100 8"],
      "Keys that are strings sort character by character, whatever the digits mean",
      """A std::map keeps its keys in order, but the order of the strings "9", "10", "100", "8" is
      alphabetical: '1' comes before '8' and '9', and "10" is a prefix of "100", so it comes first."""),

    q("set-comparator-defines-equality", r'''
        #include <iostream>
        #include <set>
        #include <string>

        struct ByLen {
            bool operator()(const std::string& a, const std::string& b) const {
                return a.size() < b.size();
            }
        };

        int main() {
            std::set<std::string, ByLen> s{"bb", "a", "cc", "ddd"};
            std::cout << s.size();
            for (const auto& w : s) std::cout << " " << w;
            std::cout << "\n";
        }
    ''', "3 a bb ddd", ["4 a bb cc ddd", "3 a cc ddd", "3 bb cc ddd"],
      "A set treats two values as the same if neither is 'less' than the other",
      """With the length comparator, "bb" and "cc" are equivalent: neither is shorter. The set never
      uses `==`, so "cc" is refused as a duplicate of the "bb" that was inserted first."""),

    q("stable-sort-keeps-the-order-of-ties", r'''
        #include <algorithm>
        #include <iostream>
        #include <string>
        #include <vector>

        int main() {
            std::vector<std::string> w{"bb", "a", "cc", "d", "ee"};
            auto shorter = [](const std::string& x, const std::string& y) {
                return x.size() < y.size();
            };
            std::stable_sort(w.begin(), w.end(), shorter);
            for (const auto& s : w) std::cout << s << " ";
            std::cout << "\n";
        }
    ''', "a d bb cc ee", ["d a bb cc ee", "a d ee cc bb", "bb cc ee a d"],
      "stable_sort keeps items that compare equal in their original order",
      """"a" and "d" tie on length, as do "bb", "cc" and "ee". `stable_sort` promises to leave each
      group in the order it was in: a before d, and bb, cc, ee as given. Plain `sort` promises nothing."""),

    # ── Batch 2: algorithms, lambdas, destructors ──────────────────────────
    q("adjacent-difference-keeps-the-first", r'''
        #include <iostream>
        #include <numeric>
        #include <vector>

        int main() {
            std::vector<int> v{5, 6, 7, 8};
            std::vector<int> d(v.size());
            std::adjacent_difference(v.begin(), v.end(), d.begin());
            for (int x : d) std::cout << x << " ";
            std::cout << "\n";
        }
    ''', "5 1 1 1", ["1 1 1", "1 1 1 0", "0 1 1 1"],
      "adjacent_difference copies the first element, and then writes the differences",
      """The output has as many elements as the input. The first one has nothing before it to subtract,
      so it is just copied: 5. The rest are 6 - 5, 7 - 6 and 8 - 7, which are all 1."""),

    q("lower-and-upper-bound-with-duplicates", r'''
        #include <algorithm>
        #include <iostream>
        #include <vector>

        int main() {
            std::vector<int> v{1, 2, 2, 2, 3};
            auto lo = std::lower_bound(v.begin(), v.end(), 2);
            auto hi = std::upper_bound(v.begin(), v.end(), 2);
            auto no = std::lower_bound(v.begin(), v.end(), 4);
            std::cout << lo - v.begin() << " " << hi - v.begin() << " "
                      << hi - lo << " " << no - v.begin() << "\n";
        }
    ''', "1 4 3 5", ["1 3 2 5", "1 4 3 -1", "0 3 3 5"],
      "lower_bound is the first element not less than the key, upper_bound the first greater",
      """The 2s sit at indexes 1 to 3, so lower_bound is 1 and upper_bound is 4: the gap between them
      is the count, 3. A key bigger than everything gives the end iterator (index 5), never -1."""),

    q("max-min-and-minmax-on-a-tie", r'''
        #include <algorithm>
        #include <iostream>

        struct K { int k; char tag; };

        int main() {
            K a{1, 'a'}, b{1, 'b'};
            auto lt = [](const K& x, const K& y) { return x.k < y.k; };
            auto mx = std::max(a, b, lt);
            auto mn = std::min(a, b, lt);
            auto mm = std::minmax(a, b, lt);
            std::cout << mx.tag << mn.tag << mm.first.tag << mm.second.tag << "\n";
        }
    ''', "aaab", ["baab", "abba", "aaaa"],
      "On a tie max and min both return the first argument, but minmax returns them in order",
      """`std::max(a, b)` gives `b` only if `a` is strictly less, so on a tie it returns `a`, and `min`
      returns `a` too. `minmax` returns the pair (a, b), so its second is the later one, `b`."""),

    q("sizeof-a-char-literal", r'''
        #include <iostream>

        int main() {
            std::cout << sizeof('a') << " " << sizeof(true) << " " << sizeof(1.5f)
                      << " " << sizeof(1.5) << "\n";
        }
    ''', "1 1 4 8", ["4 1 4 8", "4 4 4 8", "1 1 8 8"],
      "A character literal is a char in C++ (it is an int in C)",
      """`'a'` has type char here, so its size is 1; in C it would be 4. A bool is also 1 byte, a float
      is 4 and an unsuffixed floating literal is a double: 8."""),

    q("structured-binding-copies-unless-it-is-a-reference", r'''
        #include <iostream>
        #include <utility>

        int main() {
            std::pair<int, int> p{1, 2};
            auto [x, y] = p;
            x = 10;
            auto& [r, s] = p;
            r = 20;
            std::cout << p.first << " " << x << " " << s << " " << y << "\n";
        }
    ''', "20 10 2 2", ["10 10 2 2", "1 10 2 2", "20 20 2 2"],
      "`auto [x, y] = p` works on a copy of p; `auto& [r, s] = p` names p's own members",
      """The first binding copies the pair, so setting x to 10 leaves p alone. The reference binding makes
      r another name for `p.first`, so `r = 20` really changes p. `x` stays at 10 and `p.first` is 20."""),

    q("generic-lambda-deduces-each-call", r'''
        #include <iostream>

        int main() {
            auto half = [](auto x) { return x / 2; };
            std::cout << half(5) << " " << half(5.0) << " " << half(5.0f) << " "
                      << half('d') << "\n";
        }
    ''', "2 2.5 2.5 50", ["2.5 2.5 2.5 50", "2 2 2.5 50", "2 2.5 2.5 d"],
      "An `auto` parameter is deduced afresh at each call, and the result type follows from it",
      """With an int, `x / 2` is integer division (2); with a double or float it is floating point. For
      a char, the division promotes it to an int, so 'd' (100) halves to the int 50, not a character."""),

    q("std-function-keeps-its-own-copy-of-the-state", r'''
        #include <functional>
        #include <iostream>

        int main() {
            int c = 0;
            auto inc = [c]() mutable { return ++c; };
            std::function<int()> f = inc;
            std::function<int()> g = f;
            f(); f();
            std::cout << f() << " " << g() << " " << inc() << "\n";
        }
    ''', "3 1 1", ["3 3 3", "3 1 3", "3 4 1"],
      "Each std::function holds a separate copy of the lambda, and each copy has its own state",
      """`f` copies `inc` and `g` copies `f` before any call, so the three counters are independent.
      `f` is called three times (3), while `g` and `inc` are each called once (1)."""),

    q("capture-this-versus-capture-star-this", r'''
        #include <iostream>

        struct Counter {
            int n = 0;
            auto byRef() { return [this]() { return ++n; }; }
            auto byCopy() { return [*this]() mutable { return ++n; }; }
        };

        int main() {
            Counter c;
            auto r = c.byRef();
            r(); r();
            auto k = c.byCopy();
            std::cout << k() << " " << k() << " " << c.n << " " << r() << "\n";
        }
    ''', "3 4 2 3", ["3 3 2 3", "3 4 4 5", "1 2 2 3"],
      "[this] shares the object, while [*this] takes a private copy of it (C++17)",
      """`r` increments c itself, so c.n is 2 after two calls. `[*this]` copies c at that moment, with
      n = 2: `k()` counts 3, 4 on its own copy and never changes `c.n`, which is still 2 when it is
      printed. A later `r()` makes it 3."""),

    q("destruction-runs-in-reverse-of-construction", r'''
        #include <iostream>
        #include <string>
        std::string t;
        struct M { char id; M(char c) : id(c) { t += c; } ~M() { t += id; } };
        struct B { B() { t += 'B'; } ~B() { t += 'b'; } };
        struct D : B {
            M m1{'1'}, m2{'2'};
            D() { t += 'D'; }
            ~D() { t += 'd'; }
        };

        int main() {
            { D x; }
            std::cout << t << "\n";
        }
    ''', "B12Dd21b", ["B12Dd12b", "B12Db21d", "B21Dd12b"],
      "An object is taken apart in the opposite order to how it was built",
      """Building goes base `B`, then the members in declaration order (1, 2), then the body of `D`.
      Destruction undoes it: the body of `~D`, then the members backwards (2, 1), then the base."""),

    q("a-derived-name-hides-every-base-overload", r'''
        #include <iostream>
        #include <string>

        struct B {
            std::string f(int) { return "Bi"; }
            std::string f(double) { return "Bd"; }
        };
        struct D : B {
            std::string f(int) { return "Di"; }
        };

        int main() {
            D d;
            B& b = d;
            std::cout << d.f(1.5) << " " << b.f(1.5) << " " << d.B::f(1.5) << "\n";
        }
    ''', "Di Bd Bd", ["Bd Bd Bd", "Di Di Bd", "Di Bd Di"],
      "Declaring f in a derived class hides all of the base's f overloads, not just the same signature",
      """Name lookup on a `D` stops at `D::f(int)`, so `d.f(1.5)` silently converts 1.5 to int and
      calls it. Through a `B&` the lookup sees both base overloads and picks `f(double)`. `d.B::f`
      asks for the base version explicitly."""),

    # ── Batch 3: templates, streams, strings, smart pointers ───────────────
    q("if-constexpr-and-is-integral", r'''
        #include <iostream>
        #include <string>
        #include <type_traits>

        template <class T> std::string kind(T) {
            if constexpr (std::is_integral_v<T>) return "int";
            else if constexpr (std::is_floating_point_v<T>) return "fp";
            else return "other";
        }

        int main() {
            std::cout << kind(1) << " " << kind(1.5f) << " " << kind('c') << " "
                      << kind(true) << " " << kind("s") << "\n";
        }
    ''', "int fp int int other", ["int fp other other other", "int fp int int int",
                                  "int fp int other other"],
      "char and bool count as integral types, and a string literal is a pointer",
      """`std::is_integral` is true for char and bool as well as int, so 'c' and `true` are "int". The
      literal "s" is passed as a `const char*`, which is neither integral nor floating point."""),

    q("move-of-an-int-is-a-copy", r'''
        #include <iostream>
        #include <utility>

        int main() {
            int a = 5;
            int b = std::move(a);
            b += 1;
            std::cout << a << " " << b << "\n";
        }
    ''', "5 6", ["0 6", "6 6", "5 5"],
      "std::move only allows moving; for a plain int the 'move' is an ordinary copy",
      """`std::move` is just a cast to an rvalue. Moving an int means copying its bits, and nothing
      resets the original, so `a` stays 5 while `b` becomes 6."""),

    q("boolalpha-only-touches-bool", r'''
        #include <iostream>

        int main() {
            std::cout << std::boolalpha << true << " " << 1 << " " << (2 > 1)
                      << " " << (5 & 1) << " " << std::noboolalpha << true
                      << "\n";
        }
    ''', "true 1 true 1 1", ["true true true true true", "1 1 1 1 1", "true 1 1 1 1"],
      "boolalpha changes how a bool prints, and only a bool: an int 1 is still 1",
      """`true` and the comparison `2 > 1` are bools and print as words. `1` and `5 & 1` are ints and
      stay numbers. After `noboolalpha` a bool prints as 1 again."""),

    q("setw-applies-once-setfill-sticks", r'''
        #include <iomanip>
        #include <iostream>

        int main() {
            std::cout << std::setw(5) << std::setfill('0') << 42 << "|" << 7
                      << "|" << std::setw(4) << "ab" << "\n";
        }
    ''', "00042|7|00ab", ["00042|00007|00ab", "00042|7|  ab", "   42|7|  ab"],
      "setw lasts for one output only; setfill stays until it is changed",
      """The width 5 pads the 42 and is then reset, so the 7 prints plainly. The fill character '0'
      persists, so the later `setw(4)` pads "ab" with zeros, not spaces."""),

    q("to-string-of-a-double-has-six-decimals", r'''
        #include <iostream>
        #include <string>

        int main() {
            std::cout << std::to_string(3.0) << " " << std::to_string(0.1 + 0.2)
                      << " " << std::to_string(12) << " " << std::to_string(1.5f)
                      << "\n";
        }
    ''', "3.000000 0.300000 12 1.500000",
    ["3 0.3 12 1.5", "3.0 0.30000000000000004 12 1.5", "3.000000 0.300000 12.000000 1.500000"],
      "to_string formats floating point like %f: always six decimals",
      """Unlike `std::cout`, `to_string(double)` does not choose the shortest form. It prints six digits
      after the point, so 3.0 is "3.000000" and 0.1 + 0.2 is "0.300000". An int has no decimals."""),

    q("stoi-reports-where-it-stopped", r'''
        #include <iostream>
        #include <string>

        int main() {
            std::size_t p1 = 0, p2 = 0, p3 = 0;
            int a = std::stoi("42abc", &p1);
            int b = std::stoi("  7", &p2);
            int c = std::stoi("0x1F", &p3, 16);
            std::cout << a << "@" << p1 << " " << b << "@" << p2 << " "
                      << c << "@" << p3 << "\n";
        }
    ''', "42@2 7@3 31@4", ["42@5 7@1 31@4", "42@2 7@1 31@4", "42@2 7@3 0@1"],
      "stoi skips leading spaces, stops at the first bad character, and says where",
      """"42abc" gives 42 and a position of 2, where the `a` is. "  7" skips two spaces, so the end is
      at 3. With base 16 an optional `0x` is allowed, so "0x1F" is 31 and ends at 4."""),

    q("auto-with-braces", r'''
        #include <iostream>

        int main() {
            auto a = {7, 8, 9};
            auto b{7};
            auto c = 7;
            std::cout << a.size() << " " << b + 1 << " " << c + 1 << "\n";
        }
    ''', "3 8 8", ["3 3 8", "1 8 8", "3 1 8"],
      "`auto x = {...}` deduces a std::initializer_list, but `auto x{7}` is just an int",
      """With an equals sign and braces, `a` is an `initializer_list<int>` of three elements. Without
      the equals sign and with a single element, C++17 deduces plain `int`, so `b + 1` is 8."""),

    q("std-array-copies-but-a-c-array-decays", r'''
        #include <array>
        #include <iostream>

        int main() {
            std::array<int, 3> a{1, 2, 3};
            auto b = a;
            b[0] = 9;
            int c[3] = {1, 2, 3};
            int* d = c;
            d[0] = 9;
            std::cout << a[0] << " " << b[0] << " " << c[0] << "\n";
        }
    ''', "1 9 9", ["9 9 9", "1 9 1", "1 1 9"],
      "std::array is copied by value like any struct; a pointer to a C array shares it",
      """`auto b = a` makes a separate array, so changing b leaves a at 1. `d` is only a pointer to
      `c`'s elements, so `d[0] = 9` writes into `c` itself."""),

    q("weak-ptr-does-not-keep-things-alive", r'''
        #include <iostream>
        #include <memory>

        int main() {
            std::weak_ptr<int> w;
            {
                auto s = std::make_shared<int>(5);
                w = s;
                std::cout << w.use_count() << w.expired() << " ";
            }
            std::cout << w.use_count() << w.expired() << " "
                      << (w.lock() == nullptr) << "\n";
        }
    ''', "10 01 1", ["20 01 1", "10 10 0", "10 01 0"],
      "A weak_ptr is not counted as an owner, and it goes stale when the last owner dies",
      """Inside the block there is one owner, `s`, so use_count is 1 and the weak pointer is not
      expired. When `s` ends the object is destroyed: the count is 0, `expired()` is true and `lock()`
      gives a null pointer."""),

    q("braced-lists-evaluate-left-to-right", r'''
        #include <iostream>
        #include <vector>

        int main() {
            int i = 0;
            std::vector<int> v{i++, i++, i++};
            int a[] = {i++, i++};
            std::cout << v[0] << v[1] << v[2] << " " << a[0] << a[1] << " "
                      << i << "\n";
        }
    ''', "012 34 5", ["210 43 5", "000 33 5", "012 34 3"],
      "Inside braces the elements are evaluated strictly left to right",
      """Unlike the arguments of a function call, the items of a braced list are sequenced in order, so
      `{i++, i++, i++}` is 0, 1, 2. The next list continues from 3 and ends with i equal to 5."""),

    # ── Batch 4: unwinding, more algorithms, templates, sequencing ─────────
    q("stack-unwinding-destroys-before-the-handler", r'''
        #include <iostream>

        struct G {
            const char* n;
            ~G() { std::cout << n << " "; }
        };

        int main() {
            try {
                G a{"a"}, b{"b"};
                throw 1;
            } catch (int) {
                std::cout << "caught\n";
            }
        }
    ''', "b a caught", ["caught b a", "a b caught", "caught"],
      "Locals of the try block are destroyed, newest first, before the catch body runs",
      """Throwing unwinds the stack up to the handler, destroying every local on the way in reverse
      order of creation: b, then a. Only then does the `catch` block start."""),

    q("pairs-sort-by-first-then-second", r'''
        #include <algorithm>
        #include <iostream>
        #include <utility>
        #include <vector>

        int main() {
            std::vector<std::pair<int, int>> v{{2, 1}, {1, 5}, {2, 0}, {1, 3}};
            std::sort(v.begin(), v.end());
            for (const auto& p : v) std::cout << p.first << "," << p.second << " ";
            std::cout << "\n";
        }
    ''', "1,3 1,5 2,0 2,1", ["1,5 1,3 2,1 2,0", "1,3 1,5 2,1 2,0", "2,0 2,1 1,3 1,5"],
      "A pair is ordered by its first member, and by its second only when the firsts are equal",
      """`operator<` on pairs is lexicographic, like comparing words. Both 1s come before both 2s, and
      within each group the second numbers are in ascending order: 3 then 5, 0 then 1."""),

    q("reserve-is-not-resize", r'''
        #include <iostream>
        #include <vector>

        int main() {
            std::vector<int> v{1, 2};
            v.reserve(10);
            std::cout << v.size() << " ";
            v.resize(4, 7);
            v.resize(3);
            for (int x : v) std::cout << x << " ";
            std::cout << "\n";
        }
    ''', "2 1 2 7", ["10 1 2 7", "2 1 2 7 7", "2 1 2 0 0"],
      "reserve only prepares room; resize changes the number of elements, filling new ones",
      """`reserve(10)` leaves the size at 2. `resize(4, 7)` appends two 7s, and `resize(3)` drops the
      last one, which leaves {1, 2, 7}."""),

    q("priority-queue-pops-the-largest-first", r'''
        #include <functional>
        #include <iostream>
        #include <queue>
        #include <vector>

        int main() {
            std::priority_queue<int> a;
            std::priority_queue<int, std::vector<int>, std::greater<int>> b;
            for (int x : {3, 1, 4, 1, 5}) { a.push(x); b.push(x); }
            std::cout << a.top() << b.top() << " ";
            a.pop(); b.pop();
            std::cout << a.top() << b.top() << "\n";
        }
    ''', "51 41", ["15 14", "33 11", "51 51"],
      "priority_queue is a max-heap unless you give it std::greater",
      """The default queue always offers the largest element: 5, then 4 after a pop. With `greater<int>`
      the order flips and the smallest comes first: 1, and again 1 after the pop (there are two)."""),

    q("rotate-makes-the-middle-the-first", r'''
        #include <algorithm>
        #include <iostream>
        #include <vector>

        int main() {
            std::vector<int> v{1, 2, 3, 4, 5};
            std::rotate(v.begin(), v.begin() + 2, v.end());
            for (int x : v) std::cout << x << " ";
            std::cout << "\n";
        }
    ''', "3 4 5 1 2", ["2 3 4 5 1", "4 5 1 2 3", "2 1 3 4 5"],
      "rotate(first, middle, last) makes `middle` the new first element",
      """The element at `begin() + 2`, which is 3, moves to the front, and the elements before it
      (1, 2) wrap round to the back. That is a left rotation by two places."""),

    q("unique-only-merges-neighbours", r'''
        #include <algorithm>
        #include <iostream>
        #include <vector>

        int main() {
            std::vector<int> v{1, 1, 2, 1, 1, 3, 3};
            v.erase(std::unique(v.begin(), v.end()), v.end());
            for (int x : v) std::cout << x << " ";
            std::cout << "\n";
        }
    ''', "1 2 1 3", ["1 2 3", "1 2 1 1 3", "1 1 2 3"],
      "unique removes repeats that sit next to each other, not duplicates in general",
      """Each run of equal neighbours collapses to one element: 1 1, then 2, then 1 1, then 3 3. The
      second run of 1s is separate from the first, so 1 appears twice. Sort first to remove all."""),

    q("all-of-an-empty-range", r'''
        #include <algorithm>
        #include <iostream>
        #include <vector>

        int main() {
            std::vector<int> v;
            auto pos = [](int x) { return x > 0; };
            std::cout << std::all_of(v.begin(), v.end(), pos) << " "
                      << std::any_of(v.begin(), v.end(), pos) << " "
                      << std::none_of(v.begin(), v.end(), pos) << "\n";
        }
    ''', "1 0 1", ["0 0 1", "1 0 0", "0 0 0"],
      "On an empty range all_of and none_of are true, and any_of is false",
      """`all_of` means no element fails the test, and with no elements none can fail. `none_of` is
      true for the same reason, and `any_of` needs at least one element that passes, so it is false."""),

    q("next-permutation-wraps-to-sorted", r'''
        #include <algorithm>
        #include <iostream>
        #include <vector>

        int main() {
            std::vector<int> v{3, 2, 1};
            bool more = std::next_permutation(v.begin(), v.end());
            std::cout << more << " ";
            for (int x : v) std::cout << x << " ";
            std::cout << "\n";
        }
    ''', "0 1 2 3", ["0 3 2 1", "1 1 2 3", "1 3 1 2"],
      "At the last permutation next_permutation returns false and resets to the first",
      """{3, 2, 1} is the largest ordering, so there is no next one. The function says so by returning
      false, and it leaves the range in its smallest (sorted) order: 1 2 3."""),

    q("each-template-instance-has-its-own-static", r'''
        #include <iostream>

        template <class T> int next() {
            static int n = 0;
            return ++n;
        }

        int main() {
            next<int>(); next<int>();
            std::cout << next<int>() << " " << next<double>() << " "
                      << next<int>() << "\n";
        }
    ''', "3 1 4", ["3 4 5", "3 1 3", "1 1 1"],
      "A static inside a function template is separate for every type it is instantiated with",
      """`next<int>` and `next<double>` are two different functions, each with its own `n`. The int one
      has been called twice, so it gives 3 and later 4; the first call of the double one gives 1."""),

    q("a-stream-chain-is-sequenced-in-cpp17", r'''
        #include <iostream>

        int main() {
            int i = 0;
            std::cout << i << i++ << i << " " << i++ << ++i << "\n";
        }
    ''', "001 13", ["000 12", "011 13", "111 23"],
      "Since C++17 the operands of << are evaluated left to right, so the chain reads in order",
      """Each `<<` runs after everything to its left. So `i` prints 0, `i++` prints 0 and makes i 1, and
      the next `i` prints 1. Then `i++` prints 1 (i becomes 2) and `++i` prints 3."""),
)
