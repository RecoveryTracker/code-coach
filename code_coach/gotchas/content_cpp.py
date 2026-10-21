"""Gotchas, C++: built as C++17 with clang++/g++/MSVC; portability notes are in langs.py (the `cpp` entry)."""

from __future__ import annotations

from .items import Item, make

q = make("cpp")

ITEMS: tuple[Item, ...] = (
    q("char-promotes-to-int", r'''
        #include <iostream>

        int main() {
            char c = 'a';
            std::cout << c + 1 << ' ' << char(c + 1) << "\n";
        }
    ''', "98 b", ["b b", "98 98", "a1 b"],
      "Arithmetic on a char makes an int, and an int prints as a number",
      """`c + 1` is promoted to int before the addition, so the stream sees the int 98 and prints the number, not
      a letter. Casting back with `char(...)` gives 'b', which prints as a letter."""),

    q("remove-does-not-shrink", r'''
        #include <algorithm>
        #include <iostream>
        #include <vector>

        int main() {
            std::vector<int> v{1, 2, 3, 2, 4};
            std::remove(v.begin(), v.end(), 2);
            std::cout << v.size() << "\n";
        }
    ''', "5", ["3", "4", "0"],
      "std::remove only moves elements; it never erases anything",
      """`std::remove` shifts the elements you keep to the front and returns the new logical end, but it cannot
      change the size of a container because it only sees iterators. You need `v.erase(std::remove(...), v.end())`
      to actually shrink the vector."""),

    q("map-subscript-inserts", r'''
        #include <iostream>
        #include <map>
        #include <string>

        int main() {
            std::map<std::string, int> m{{"a", 1}};
            int n = m["b"];
            std::cout << m.size() << " " << n << "\n";
        }
    ''', "2 0", ["1 0", "0 0", "2 1"],
      "operator[] on a map inserts the key when it is missing",
      """Reading `m["b"]` does not fail: it creates the entry with a value-initialised int, which is 0, and then
      returns it. So the map grows to two entries. Use `find`, `count` or `at` to look something up without
      changing the map."""),
)
