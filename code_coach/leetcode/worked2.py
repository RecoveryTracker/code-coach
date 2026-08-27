"""More lessons, in the shape the first module set.

`worked.py` holds the lesson each pattern opens with, and the first three
patterns in full. This is the rest of them. The split follows the one the
problem banks already use — a second module rather than one file that has to
be scrolled past to reach anything else.

Everything here is merged into `WORKED` on import, so the two files are one
registry as far as the rest of the package is concerned. The style is the same
and deliberately so: the first thought anyone has, what it costs, the one
observation that fixes it, then the code a stage at a time.
"""

from __future__ import annotations

from code_coach.leetcode.worked import Worked, _s

_STACK: dict[int, Worked] = {
    # ── stacks ──────────────────────────────────────────────────────────
    155: Worked(
        problem=155,
        naive=(
            "Keep the values in a list. When getMin is asked for, scan the "
            "list and return the smallest."
        ),
        why_not=(
            "Push and pop are instant but getMin walks the whole stack every "
            "time it is called. A caller that asks for the minimum after "
            "every push has quietly bought themselves n squared work."
        ),
        insight=(
            "The minimum only ever changes at a push or a pop, so it does not "
            "need recomputing — it needs remembering. Keep a second stack "
            "whose top is the smallest value in the main stack right now."
        ),
        stages=(
            _s(
                "Two stacks: the values, and the minimum as of each push.",
                "self.stack = []\nself.mins = []",
            ),
            _s(
                "A value only joins the minimum stack if it ties or beats the "
                "current minimum. Ties matter — drop them and popping one "
                "copy would forget the other.",
                "def push(self, val):\n    self.stack.append(val)\n"
                "    if not self.mins or val <= self.mins[-1]:\n"
                "        self.mins.append(val)",
            ),
            _s(
                "Popping the current minimum retires it, and the one beneath "
                "it becomes the minimum again.",
                "def pop(self):\n    val = self.stack.pop()\n"
                "    if self.mins and val == self.mins[-1]:\n"
                "        self.mins.pop()",
            ),
            _s(
                "Both questions are now a single read of a top.",
                "def top(self):\n    return self.stack[-1]\n\n"
                "def get_min(self):\n    return self.mins[-1]",
            ),
        ),
    ),
    150: Worked(
        problem=150,
        naive=(
            "Scan for an operator, look at the two tokens before it, work it "
            "out, and splice the answer back into the list."
        ),
        why_not=(
            "Splicing a list shifts everything after it, so each operator "
            "costs a pass over the rest of the expression. It also gets "
            "fiddly to write, which is its own kind of expensive."
        ),
        insight=(
            "In postfix an operator always applies to the two most recent "
            "unused values. 'Most recent' means a stack, and the answer it "
            "produces is itself a value that goes straight back on."
        ),
        stages=(
            _s(
                "Anything that is not an operator is a number, and numbers "
                "wait on the stack.",
                'stack = []\nfor token in tokens:\n'
                '    if token not in "+-*/":\n        stack.append(int(token))',
            ),
            _s(
                "Plus and times do not care which operand came first, so they "
                "can pop straight into the expression.",
                'if token == "+":\n'
                "    stack.append(stack.pop() + stack.pop())\n"
                'elif token == "*":\n'
                "    stack.append(stack.pop() * stack.pop())",
            ),
            _s(
                "Minus and divide do care. The first pop is the SECOND "
                "operand, so name them before using them.",
                'elif token == "-":\n'
                "    b, a = stack.pop(), stack.pop()\n"
                "    stack.append(a - b)",
            ),
            _s(
                "Division truncates toward zero, which is not what floor "
                "division does to a negative result. int() of the float is.",
                'elif token == "/":\n'
                "    b, a = stack.pop(), stack.pop()\n"
                "    stack.append(int(a / b))",
            ),
            _s(
                "One value is left, and it is the answer.",
                "return stack[0]",
            ),
        ),
    ),
    739: Worked(
        problem=739,
        naive=(
            "For each day, walk forward until you meet a warmer one, and "
            "record how many days that took."
        ),
        why_not=(
            "A long cold spell makes every day in it scan the whole spell. On "
            "a descending run that is n squared, and weather data is exactly "
            "the kind of input that has long runs in it."
        ),
        insight=(
            "Turn the question around. Instead of each day hunting for its "
            "warmer day, let a warm day announce itself and settle every "
            "colder day still waiting behind it."
        ),
        stages=(
            _s(
                "Zero is already the right answer for a day whose warm day "
                "never comes, so start there and only overwrite what resolves.",
                "answer = [0] * len(temperatures)\nstack = []",
            ),
            _s(
                "The stack holds the indexes of days still waiting. Walk the "
                "days once.",
                "for i, temp in enumerate(temperatures):",
            ),
            _s(
                "Today settles every waiting day it beats. Each one gets the "
                "distance from its own index to today's.",
                "    while stack and temperatures[stack[-1]] < temp:\n"
                "        prev = stack.pop()\n        answer[prev] = i - prev",
            ),
            _s(
                "Then today joins the queue of the unresolved. Every index is "
                "pushed once and popped at most once, which is what makes the "
                "whole thing linear despite the inner loop.",
                "    stack.append(i)\nreturn answer",
            ),
        ),
    ),
    682: Worked(
        problem=682,
        naive=(
            "Read the operations into a list, then make a second pass "
            "resolving every C, D and + against the original positions."
        ),
        why_not=(
            "The positions move. A C removes a score, so every reference "
            "after it means something different from what it meant in the "
            "raw list, and a second pass has to reconstruct that anyway."
        ),
        insight=(
            "Every operation here reads or writes only the end of the record: "
            "cancel the last, double the last, add the last two. That is the "
            "definition of a stack, so use one and each rule becomes a line."
        ),
        stages=(
            _s(
                "The record of scores that actually count.",
                "stack = []\nfor op in operations:",
            ),
            _s(
                "Cancel simply removes the most recent score.",
                '    if op == "C":\n        stack.pop()',
            ),
            _s(
                "Double and sum read the top without disturbing it, then push "
                "a new score of their own.",
                '    elif op == "D":\n        stack.append(stack[-1] * 2)\n'
                '    elif op == "+":\n'
                "        stack.append(stack[-1] + stack[-2])",
            ),
            _s(
                "Anything else is a plain score. At the end the stack IS the "
                "record, so the total is just its sum.",
                "    else:\n        stack.append(int(op))\nreturn sum(stack)",
            ),
        ),
    ),
    71: Worked(
        problem=71,
        naive=(
            "Replace '//' with '/' repeatedly, strip out '/./', then find "
            "each '..' and delete it along with the name before it."
        ),
        why_not=(
            "String surgery on a path fights itself. Deleting a name changes "
            "what the next '..' is next to, so the passes have to be repeated "
            "until nothing changes, and the edge cases multiply."
        ),
        insight=(
            "A path is a list of directories you have entered, and '..' means "
            "leave the last one. Entering and leaving in that order is a "
            "stack, so build the answer instead of editing the input."
        ),
        stages=(
            _s(
                "Splitting on the slash turns every doubled slash into an "
                "empty piece, so the messy cases arrive already separated.",
                'stack = []\nfor part in path.split("/"):',
            ),
            _s(
                "An empty piece and a '.' both mean 'stay where you are'.",
                '    if part == "" or part == ".":\n        continue',
            ),
            _s(
                "Up from the root is still the root — no error, nothing to "
                "pop. This is where the naive version usually crashes.",
                '    if part == "..":\n'
                "        if stack:\n            stack.pop()",
            ),
            _s(
                "Anything else is a real directory name. Joining with slashes "
                "and one leading slash gives the canonical form for free, "
                "including the root, which comes out as a lone slash.",
                "    else:\n        stack.append(part)\n"
                'return "/" + "/".join(stack)',
            ),
        ),
    ),
    84: Worked(
        problem=84,
        naive=(
            "Take every pair of bars as the left and right edge, find the "
            "shortest bar between them, and multiply by the width."
        ),
        why_not=(
            "That is n squared pairs, and finding the shortest bar in each "
            "makes it n cubed. Even carrying a running minimum only brings it "
            "to n squared, which a histogram of any size will feel."
        ),
        insight=(
            "Every rectangle is as tall as its shortest bar, so ask instead: "
            "for each bar, how far can a rectangle of THAT height stretch? It "
            "stops where a shorter bar appears on either side."
        ),
        stages=(
            _s(
                "A sentinel zero at the end is shorter than everything, so it "
                "forces every bar still on the stack to settle. Without it a "
                "tall run at the end is never measured.",
                "stack = []\nbest = 0\n"
                "for i, height in enumerate(heights + [0]):",
            ),
            _s(
                "The stack holds bars in increasing height, each paired with "
                "the leftmost index its height could reach back to.",
                "    start = i",
            ),
            _s(
                "A shorter bar closes off every taller bar behind it. Each one "
                "gets measured from where it began to here.",
                "    while stack and stack[-1][1] > height:\n"
                "        left, tall = stack.pop()\n"
                "        if tall * (i - left) > best:\n"
                "            best = tall * (i - left)",
            ),
            _s(
                "Whatever was popped was taller than this bar, so this bar "
                "could have started back where that one did. Carrying the "
                "index is what stops the widths being undercounted.",
                "        start = left\n    stack.append((start, height))\n"
                "return best",
            ),
        ),
    ),
    394: Worked(
        problem=394,
        naive=(
            "Find a bracketed section, expand it, splice the result back in, "
            "and start again until no brackets are left."
        ),
        why_not=(
            "Nesting means the outer brackets cannot be expanded until the "
            "inner ones are, so every pass rescans a string that keeps "
            "growing. Finding the matching close bracket is its own chore."
        ),
        insight=(
            "An opening bracket does not end the work in progress, it "
            "suspends it. Put what you had so far aside, start fresh, and "
            "resume when the bracket closes."
        ),
        stages=(
            _s(
                "Three things in flight: the text being built, the repeat "
                "count being read, and the suspended work.",
                'stack = []\ncurrent = ""\ncount = 0',
            ),
            _s(
                "Digits accumulate, because a count can be more than one "
                "digit. This is the line people forget, and it only shows up "
                "on an input with ten or more repeats.",
                "for ch in encoded:\n    if ch.isdigit():\n"
                "        count = count * 10 + int(ch)",
            ),
            _s(
                "An open bracket banks the outer work and its count, then "
                "clears the slate for what is inside.",
                '    elif ch == "[":\n'
                "        stack.append((current, count))\n"
                '        current = ""\n        count = 0',
            ),
            _s(
                "A close bracket repeats what was built and reattaches it to "
                "the work that was waiting.",
                '    elif ch == "]":\n'
                "        before, times = stack.pop()\n"
                "        current = before + current * times",
            ),
            _s(
                "Plain letters just extend whatever is being built now, "
                "whichever depth that is.",
                "    else:\n        current += ch\nreturn current",
            ),
        ),
    ),
}


_LINKED_LIST: dict[int, Worked] = {
    21: Worked(
        problem=21,
        naive=(
            "Read both lists into an array, sort it, and build a new list "
            "from the sorted values."
        ),
        why_not=(
            "It throws away the one thing the question gave you. Both inputs "
            "are already sorted, so sorting again pays n log n for an order "
            "you were handed, and it allocates a whole second list to do it."
        ),
        insight=(
            "The smaller head of the two lists is the next node of the answer, "
            "always. So keep taking whichever head is smaller and the merge "
            "falls out in one pass with no new nodes at all."
        ),
        stages=(
            _s(
                "A dummy node in front means there is always a node to attach "
                "to, so the first node needs no special case. It is the whole "
                "trick to writing list code without a thicket of ifs.",
                "dummy = ListNode()\ntail = dummy",
            ),
            _s(
                "While both lists still have nodes, take the smaller head. "
                "Using <= rather than < keeps equal values in their original "
                "order, which is what makes the merge stable.",
                "while list1 and list2:\n    if list1.val <= list2.val:\n"
                "        tail.next = list1\n        list1 = list1.next",
            ),
            _s(
                "Otherwise the other list supplies the node. Either way the "
                "tail moves up to what was just attached.",
                "    else:\n        tail.next = list2\n"
                "        list2 = list2.next\n    tail = tail.next",
            ),
            _s(
                "One list runs out first. Whatever is left of the other is "
                "already sorted and already linked, so attach it whole rather "
                "than walking it node by node.",
                "tail.next = list1 or list2\nreturn dummy.next",
            ),
        ),
    ),
    141: Worked(
        problem=141,
        naive=(
            "Walk the list putting every node into a set. If you meet one you "
            "have already seen, there is a cycle."
        ),
        why_not=(
            "It is correct, and it costs memory proportional to the list. For "
            "a question whose whole point is that you can answer it with two "
            "variables, that is the expensive answer."
        ),
        insight=(
            "Two walkers at different speeds on a circular track must meet. If "
            "one moves two nodes per the other's one, a cycle closes the gap "
            "by one each step until it is zero; no cycle and the fast one ends."
        ),
        stages=(
            _s(
                "Both start at the head. Nothing is remembered but where they "
                "are.",
                "slow = head\nfast = head",
            ),
            _s(
                "The fast walker is the one that can fall off the end, so the "
                "loop guards on it. Both fast and fast.next, because the next "
                "move reads two links ahead.",
                "while fast and fast.next:",
            ),
            _s(
                "One step and two steps.",
                "    slow = slow.next\n    fast = fast.next.next",
            ),
            _s(
                "Landing on the same node is the cycle. Compare identity, not "
                "value — two different nodes can hold the same number.",
                "    if slow is fast:\n        return True\nreturn False",
            ),
        ),
    ),
    19: Worked(
        problem=19,
        naive=(
            "Walk the list once to count the nodes, then walk again to the "
            "node at length minus n and unlink the one after it."
        ),
        why_not=(
            "Two passes is not slow, but it does not work at all if the list "
            "is arriving as a stream you only get to see once — and the "
            "one-pass version is barely longer than this one."
        ),
        insight=(
            "Counting from the end is counting from the front by a fixed gap. "
            "Start one pointer n nodes ahead of another, then move them "
            "together: when the leader reaches the end, the follower is there."
        ),
        stages=(
            _s(
                "The node to remove might be the head itself, so put a dummy "
                "in front and the head stops being a special case.",
                "dummy = ListNode(0, head)\nslow = dummy\nfast = dummy",
            ),
            _s(
                "Open the gap first. This is the only place n is used.",
                "for _ in range(n):\n    fast = fast.next",
            ),
            _s(
                "Now move together. Stopping on fast.next rather than fast "
                "leaves slow one short of the target, which is where it has to "
                "be to unlink it.",
                "while fast.next:\n    slow = slow.next\n    fast = fast.next",
            ),
            _s(
                "Skip over the doomed node, and return the dummy's next — not "
                "head, which may be the node just removed.",
                "slow.next = slow.next.next\nreturn dummy.next",
            ),
        ),
    ),
    876: Worked(
        problem=876,
        naive=(
            "Count the nodes, halve the count, then walk that many steps from "
            "the head."
        ),
        why_not=(
            "It works, and it reads the list twice for something a single pass "
            "can do. It also puts the off-by-one in the arithmetic, which is "
            "where it is hardest to see."
        ),
        insight=(
            "A pointer moving twice as fast covers twice the distance in the "
            "same time. So when the fast one reaches the end, the slow one is "
            "at exactly half — no counting and no division."
        ),
        stages=(
            _s(
                "Both walkers start at the head.",
                "slow = head\nfast = head",
            ),
            _s(
                "The loop condition is the whole answer to the even case. "
                "Guarding on fast.next as well means an even list stops with "
                "slow on the SECOND middle node, which is what was asked for.",
                "while fast and fast.next:",
            ),
            _s(
                "One step against two.",
                "    slow = slow.next\n    fast = fast.next.next",
            ),
            _s(
                "Where the slow one stopped is the middle.",
                "return slow",
            ),
        ),
    ),
    83: Worked(
        problem=83,
        naive=(
            "Collect the values into a set, then build a fresh list out of the "
            "ones that survived."
        ),
        why_not=(
            "A set forgets the order, so the rebuilt list needs sorting again, "
            "and it allocates a copy of a list you were asked to edit. Neither "
            "cost is necessary here."
        ),
        insight=(
            "The list is sorted, so equal values are always neighbours. That "
            "makes a duplicate something you can spot by looking at exactly "
            "one node — the next one."
        ),
        stages=(
            _s(
                "Walk with a node that has a next to compare against.",
                "node = head\nwhile node and node.next:",
            ),
            _s(
                "Same value as the neighbour means unlink the neighbour.",
                "    if node.val == node.next.val:\n"
                "        node.next = node.next.next",
            ),
            _s(
                "And do NOT advance. A run of three equal values needs the "
                "same node to drop two neighbours in turn; stepping forward "
                "here is the classic bug.",
                "    else:\n        node = node.next",
            ),
            _s(
                "The head never moves, because a sorted list's first node is "
                "always the first of its value.",
                "return head",
            ),
        ),
    ),
    234: Worked(
        problem=234,
        naive=(
            "Copy the values into an array and compare it against its own "
            "reverse."
        ),
        why_not=(
            "Perfectly clear, and it costs a full copy of the list. The "
            "interesting version of this question is the one that uses a fixed "
            "amount of extra memory, which is what this walks through."
        ),
        insight=(
            "You cannot walk a singly linked list backwards — but you can turn "
            "the second half around so that walking it forwards IS walking "
            "backwards. Then the two halves compare head to head."
        ),
        stages=(
            _s(
                "Find the middle the same way as always: slow moves one, fast "
                "moves two.",
                "slow = head\nfast = head\nwhile fast and fast.next:\n"
                "    slow = slow.next\n    fast = fast.next.next",
            ),
            _s(
                "Reverse from the middle on. Each node's next is bent to point "
                "at the one before, so nxt has to be saved before the link is "
                "overwritten.",
                "second = None\nwhile slow:\n    nxt = slow.next\n"
                "    slow.next = second\n    second = slow\n    slow = nxt",
            ),
            _s(
                "Now walk both halves forwards. Any mismatch settles it.",
                "first = head\nwhile second:\n"
                "    if first.val != second.val:\n        return False",
            ),
            _s(
                "The reversed half is the shorter one on an odd-length list, "
                "so looping on second is what stops this walking off the end.",
                "    first = first.next\n    second = second.next\nreturn True",
            ),
        ),
    ),
    2: Worked(
        problem=2,
        naive=(
            "Read each list into a number, add the two numbers, then split the "
            "total back into digits."
        ),
        why_not=(
            "The lists can hold a hundred digits. In a language with fixed-"
            "width integers that overflows long before you get there, and even "
            "where it does not, it does more work than adding digits does."
        ),
        insight=(
            "The digits arrive least significant first, which is exactly the "
            "order long addition wants. So add them as they come and carry "
            "forward — no conversion in either direction."
        ),
        stages=(
            _s(
                "A dummy head again, so the first digit attaches like any "
                "other. Carry starts at nothing.",
                "head = ListNode()\nnode = head\ncarry = 0",
            ),
            _s(
                "Keep going while either list has digits left OR a carry is "
                "still owed. That last clause is what makes 5 + 5 come out as "
                "two nodes instead of one.",
                "while first or second or carry:\n    total = carry",
            ),
            _s(
                "Each list contributes a digit if it still has one, and a "
                "list that has run out simply contributes nothing.",
                "    if first:\n        total += first.val\n"
                "        first = first.next\n    if second:\n"
                "        total += second.val\n        second = second.next",
            ),
            _s(
                "The tens place is the carry and the units place is the digit.",
                "    carry = total // 10\n"
                "    node.next = ListNode(total % 10)\n    node = node.next",
            ),
            _s(
                "Skip the dummy on the way out.",
                "return head.next",
            ),
        ),
    ),
}


_BINARY_SEARCH: dict[int, Worked] = {
    35: Worked(
        problem=35,
        naive=(
            "Walk from the front until you find the target or a value bigger "
            "than it, and return that index."
        ),
        why_not=(
            "Linear on a sorted list, which is the one situation where you "
            "never have to be. On a million entries that is a million reads "
            "instead of twenty."
        ),
        insight=(
            "Search a half-open range and the insert point falls out for free: "
            "high can be one PAST the end, so 'belongs after everything' is "
            "just another answer rather than a special case."
        ),
        stages=(
            _s(
                "The range is [low, high) — high is len, not len - 1, because "
                "the answer may be the position after the last value.",
                "low, high = 0, len(nums)",
            ),
            _s(
                "Loop while the range holds anything at all. When low meets "
                "high the range is empty and the search is over.",
                "while low < high:\n    mid = (low + high) // 2",
            ),
            _s(
                "Too small means mid cannot be the answer, so step past it.",
                "    if nums[mid] < target:\n        low = mid + 1",
            ),
            _s(
                "Otherwise mid might BE the answer, so keep it in range. "
                "Notice there is no equality branch — this deliberately finds "
                "the leftmost position rather than any match.",
                "    else:\n        high = mid\nreturn low",
            ),
        ),
    ),
    153: Worked(
        problem=153,
        naive=(
            "Scan every value and keep the smallest one seen. Or find where a "
            "value is smaller than the one before it."
        ),
        why_not=(
            "Both read the whole list. The list is sorted apart from one "
            "rotation, and that is more than enough structure to throw half of "
            "it away at every step."
        ),
        insight=(
            "Compare the middle to the RIGHT end, not the left. If mid is "
            "bigger than the last value, the rotation point is somewhere after "
            "mid; otherwise mid is in the sorted tail and could be the minimum."
        ),
        stages=(
            _s(
                "A closed range this time, because both ends name real values "
                "and the answer is one of them.",
                "low, high = 0, len(nums) - 1",
            ),
            _s(
                "Stop when the range narrows to a single value. That value is "
                "the answer, so there is no 'not found' case to write.",
                "while low < high:\n    mid = (low + high) // 2",
            ),
            _s(
                "Bigger than the right end means everything from low to mid is "
                "on the high side of the rotation. The dip is past mid.",
                "    if nums[mid] > nums[high]:\n        low = mid + 1",
            ),
            _s(
                "Otherwise mid is already in the sorted stretch that contains "
                "the minimum — and might be it, so keep mid in range.",
                "    else:\n        high = mid\nreturn nums[low]",
            ),
        ),
    ),
    33: Worked(
        problem=33,
        naive=(
            "Find the rotation point with one binary search, then binary "
            "search the correct half for the target."
        ),
        why_not=(
            "It is not wrong, and it is two searches and a lot of index "
            "arithmetic to keep straight. The same work fits into one loop if "
            "you notice what a rotated list guarantees."
        ),
        insight=(
            "Cut a rotated sorted list anywhere and at least one half is still "
            "in plain sorted order. Work out which half that is, and then a "
            "simple range check says whether the target lives in it."
        ),
        stages=(
            _s(
                "Ordinary closed-range binary search to start with.",
                "low, high = 0, len(nums) - 1\nwhile low <= high:\n"
                "    mid = (low + high) // 2\n    if nums[mid] == target:\n"
                "        return mid",
            ),
            _s(
                "If the left end is not bigger than mid, the left half has no "
                "rotation in it and is sorted.",
                "    if nums[low] <= nums[mid]:",
            ),
            _s(
                "In a sorted half, membership is just a range check. Inside "
                "it, search there; outside it, the target must be elsewhere.",
                "        if nums[low] <= target < nums[mid]:\n"
                "            high = mid - 1\n        else:\n"
                "            low = mid + 1",
            ),
            _s(
                "Otherwise the RIGHT half is the sorted one, and the same "
                "check runs against its two ends.",
                "    else:\n"
                "        if nums[mid] < target <= nums[high]:\n"
                "            low = mid + 1\n        else:\n"
                "            high = mid - 1\nreturn -1",
            ),
        ),
    ),
    875: Worked(
        problem=875,
        naive=(
            "Try speed 1, then 2, then 3, and stop at the first one that "
            "finishes the piles within the hours allowed."
        ),
        why_not=(
            "The speed can be as large as the biggest pile, so this is a "
            "linear scan over a range that can be in the billions, with a pass "
            "over every pile at each step."
        ),
        insight=(
            "There is nothing to binary search in the input — so search the "
            "ANSWER instead. Speeds are ordered, and 'finishes in time' is "
            "false up to some speed and true forever after. That is a boundary."
        ),
        stages=(
            _s(
                "The range of possible answers, not of indexes. One banana an "
                "hour always eventually works; the largest pile always works "
                "in one hour each, so nothing faster is ever needed.",
                "low, high = 1, max(piles)",
            ),
            _s(
                "Same half-open boundary search, with speed in place of index.",
                "while low < high:\n    speed = (low + high) // 2",
            ),
            _s(
                "Time the candidate. A pile is never shared across hours, so "
                "each one costs its size divided by speed ROUNDED UP — which "
                "is what adding speed - 1 before dividing does.",
                "    hours = 0\n    for pile in piles:\n"
                "        hours += (pile + speed - 1) // speed",
            ),
            _s(
                "Fast enough means this speed is a candidate, so keep it and "
                "try slower. Too slow means everything at or below it is out.",
                "    if hours <= h:\n        high = speed\n    else:\n"
                "        low = speed + 1\nreturn low",
            ),
        ),
    ),
    278: Worked(
        problem=278,
        naive=(
            "Check version 1, then 2, then 3, and return the first one the "
            "checker calls bad."
        ),
        why_not=(
            "Each check is the expensive thing here — it is described as a "
            "call you want few of. Walking up from 1 makes as many calls as "
            "there are versions."
        ),
        insight=(
            "Good versions then bad versions, with no mixing: that is a sorted "
            "list of False then True. Finding where it flips is a binary "
            "search whose comparison happens to be a function call."
        ),
        stages=(
            _s(
                "Versions are numbered from 1, so the range starts there.",
                "low, high = 1, n",
            ),
            _s(
                "Narrow until one candidate remains. Every iteration halves "
                "the range, so n versions cost about log n calls.",
                "while low < high:\n    mid = (low + high) // 2",
            ),
            _s(
                "Bad means mid could be the FIRST bad one, so it stays in "
                "range. Discarding it here is the off-by-one that makes this "
                "return the wrong version.",
                "    if is_bad(mid):\n        high = mid",
            ),
            _s(
                "Good means the flip is somewhere after mid.",
                "    else:\n        low = mid + 1\nreturn low",
            ),
        ),
    ),
    34: Worked(
        problem=34,
        naive=(
            "Binary search for any occurrence, then walk left and right from "
            "it until the values change."
        ),
        why_not=(
            "The walk is the problem. A list that is entirely the target makes "
            "it linear, so the search that was meant to be logarithmic ends up "
            "reading everything anyway."
        ),
        insight=(
            "Do not walk after finding a match — keep searching. On a hit, "
            "record it and then carry on into the half that might hold an "
            "earlier one, or a later one, depending on which edge you want."
        ),
        stages=(
            _s(
                "One helper, told which edge it is looking for. Two calls beat "
                "two near-identical loops written out twice.",
                "def edge(first):\n    low, high = 0, len(nums) - 1\n"
                "    found = -1",
            ),
            _s(
                "A hit is remembered rather than returned, because a better "
                "one may still be out there.",
                "    while low <= high:\n        mid = (low + high) // 2\n"
                "        if nums[mid] == target:\n            found = mid",
            ),
            _s(
                "Then keep going in the direction of the edge you want — left "
                "for the first occurrence, right for the last.",
                "            if first:\n                high = mid - 1\n"
                "            else:\n                low = mid + 1",
            ),
            _s(
                "Misses behave like an ordinary search. Two runs of the same "
                "loop give both ends.",
                "        elif nums[mid] < target:\n            low = mid + 1\n"
                "        else:\n            high = mid - 1\n    return found\n\n"
                "return [edge(True), edge(False)]",
            ),
        ),
    ),
    74: Worked(
        problem=74,
        naive=(
            "Binary search the first column to find the right row, then binary "
            "search that row for the target."
        ),
        why_not=(
            "Two searches and two sets of bounds to get right, for a matrix "
            "that has more structure than that. It is not slower in any way "
            "that matters — it is just more code than the question needs."
        ),
        insight=(
            "Every row starts above where the last one ended, so reading the "
            "matrix left to right, top to bottom gives one sorted sequence. "
            "Search that, and convert the index back to a row and column."
        ),
        stages=(
            _s(
                "An empty matrix, or one with empty rows, has nothing to "
                "search and would otherwise divide by zero below.",
                "if not matrix or not matrix[0]:\n    return False",
            ),
            _s(
                "Treat it as one list of rows times cols values.",
                "rows, cols = len(matrix), len(matrix[0])\n"
                "low, high = 0, rows * cols - 1",
            ),
            _s(
                "Unfold the flat index: whole rows out of the division, "
                "position within the row out of the remainder.",
                "while low <= high:\n    mid = (low + high) // 2\n"
                "    value = matrix[mid // cols][mid % cols]",
            ),
            _s(
                "From here it is a plain binary search over values.",
                "    if value == target:\n        return True\n"
                "    if value < target:\n        low = mid + 1\n    else:\n"
                "        high = mid - 1\nreturn False",
            ),
        ),
    ),
}


_TREE_DFS: dict[int, Worked] = {
    226: Worked(
        problem=226,
        naive=(
            "Walk the tree collecting the values level by level, reverse each "
            "level, and build a new tree from the result."
        ),
        why_not=(
            "It rebuilds a tree that only needed rearranging, and the levels "
            "have to be padded with the missing positions or the rebuilt shape "
            "comes out wrong. Far more machinery than the job needs."
        ),
        insight=(
            "Mirroring a tree is swapping the two children of every node, and "
            "nothing else. A node's own swap does not depend on what happens "
            "below it, so recursion can do the whole thing."
        ),
        stages=(
            _s(
                "An empty branch mirrors to an empty branch. This is the base "
                "case and also the answer for an empty tree.",
                "if not root:\n    return None",
            ),
            _s(
                "Invert each side, and attach each result to the OTHER side. "
                "The crossover is the entire mirror.",
                "root.left, root.right = (\n"
                "    invert_tree(root.right),\n"
                "    invert_tree(root.left),\n)",
            ),
            _s(
                "Both calls finish before the assignment happens, which is "
                "what stops the second one working on an already-swapped "
                "child. Doing it in two statements needs a temporary.",
                "return root",
            ),
        ),
    ),
    112: Worked(
        problem=112,
        naive=(
            "Collect every root-to-leaf path into a list, then add up each one "
            "and see whether any total matches."
        ),
        why_not=(
            "The number of paths grows with the tree, and each one is stored "
            "in full. It also cannot stop early — the answer might be the "
            "first path, but every other one is built anyway."
        ),
        insight=(
            "The sum does not need collecting, it needs subtracting. Take each "
            "node's value off the target on the way down, and at a leaf the "
            "question is just whether what remains is that leaf."
        ),
        stages=(
            _s(
                "An empty branch is not a path to a leaf, so it can never "
                "satisfy anything. Note this is not the same as a leaf.",
                "if not root:\n    return False",
            ),
            _s(
                "A leaf is a node with neither child. That is where a path "
                "ends, so that is where the total is finally judged.",
                "if not root.left and not root.right:\n"
                "    return target_sum == root.val",
            ),
            _s(
                "Otherwise pay for this node and carry the remainder down.",
                "rest = target_sum - root.val",
            ),
            _s(
                "Either side finding a path is enough, and or() stops at the "
                "first one that does — so a lucky answer really is early.",
                "return has_path_sum(root.left, rest) or has_path_sum(\n"
                "    root.right, rest\n)",
            ),
        ),
    ),
    543: Worked(
        problem=543,
        naive=(
            "For every node, work out the depth of its left subtree and its "
            "right, add them, and keep the largest total found."
        ),
        why_not=(
            "Each depth call walks a whole subtree, and it is called once per "
            "node. On a leaning tree that is n squared — the same subtrees "
            "measured again and again."
        ),
        insight=(
            "One walk can do both jobs. Have the recursion RETURN the depth "
            "its caller needs, while recording left plus right as a candidate "
            "answer on the way back up."
        ),
        stages=(
            _s(
                "The answer lives outside the recursion, because the best path "
                "may not go through the root at all.",
                "best = 0",
            ),
            _s(
                "The helper's return value is the depth. Nothing hangs below "
                "an empty branch, so that is zero.",
                "def depth(node):\n    nonlocal best\n    if not node:\n"
                "        return 0",
            ),
            _s(
                "Measure both sides once each. This is the reuse the naive "
                "version was missing.",
                "    left = depth(node.left)\n    right = depth(node.right)",
            ),
            _s(
                "The longest path THROUGH this node is left plus right edges. "
                "Every node offers one, and the best of them is the diameter.",
                "    best = max(best, left + right)",
            ),
            _s(
                "What the caller wanted, though, is depth: the deeper side "
                "plus this node.",
                "    return 1 + max(left, right)\n\ndepth(root)\nreturn best",
            ),
        ),
    ),
    98: Worked(
        problem=98,
        naive=(
            "At each node, check that the left child is smaller and the right "
            "child is bigger, then recurse."
        ),
        why_not=(
            "It only looks one step. A node deep in the left subtree can be "
            "bigger than an ancestor while still being smaller than its own "
            "parent, and this check waves it through."
        ),
        insight=(
            "Being a search tree is not a fact about neighbours, it is a fact "
            "about ranges. Every node inherits a permitted range from its "
            "ancestors, and going left or right narrows one end of it."
        ),
        stages=(
            _s(
                "The helper carries the range down. An empty branch breaks "
                "nothing.",
                "def check(node, low, high):\n    if not node:\n"
                "        return True",
            ),
            _s(
                "A strict double comparison, because a search tree has no "
                "duplicates. This is the check the neighbour version could not "
                "make.",
                "    if not low < node.val < high:\n        return False",
            ),
            _s(
                "Going left, this node becomes the new ceiling; going right, "
                "the new floor. The other end is passed through untouched, "
                "which is how a distant ancestor's limit keeps applying.",
                "    return check(node.left, low, node.val) and check(\n"
                "        node.right, node.val, high\n    )",
            ),
            _s(
                "The root has no ancestors, so it starts unbounded.",
                'return check(root, float("-inf"), float("inf"))',
            ),
        ),
    ),
    100: Worked(
        problem=100,
        naive=(
            "Serialise both trees into lists of values and compare the lists."
        ),
        why_not=(
            "A plain list of values loses the shape. Two different trees can "
            "serialise the same way unless the empty spots are written down "
            "too, and by then you are comparing trees the hard way."
        ),
        insight=(
            "Two trees are the same when the roots hold the same value AND the "
            "left halves match AND the right halves match. The definition is "
            "already recursive; it just has to be written down."
        ),
        stages=(
            _s(
                "Two empty branches match. This is the base case that ends "
                "every successful comparison.",
                "if not first and not second:\n    return True",
            ),
            _s(
                "One empty and one not is a difference in SHAPE — the case the "
                "flattened version was blind to.",
                "if not first or not second:\n    return False",
            ),
            _s(
                "Both exist, so the values have to agree.",
                "if first.val != second.val:\n    return False",
            ),
            _s(
                "Then the same question, one level down, on both sides. and() "
                "stops at the first mismatch.",
                "return is_same_tree(first.left, second.left) and is_same_tree(\n"
                "    first.right, second.right\n)",
            ),
        ),
    ),
    101: Worked(
        problem=101,
        naive=(
            "Invert a copy of the tree and check whether the copy equals the "
            "original."
        ),
        why_not=(
            "It is a genuinely correct answer, and it costs a full copy of the "
            "tree plus two passes. The comparison it is reaching for can be "
            "done directly on the tree that is already there."
        ),
        insight=(
            "Symmetry is not a property of one node, it is a property of a "
            "PAIR. Compare left against right, and let the recursion cross "
            "over: outer edge against outer edge, inner against inner."
        ),
        stages=(
            _s(
                "The helper takes two nodes rather than one, because that is "
                "what is really being checked.",
                "def mirror(left, right):\n    if not left and not right:\n"
                "        return True",
            ),
            _s(
                "One present and one missing is exactly the asymmetry being "
                "looked for.",
                "    if not left or not right:\n        return False",
            ),
            _s(
                "Matching positions must hold matching values.",
                "    if left.val != right.val:\n        return False",
            ),
            _s(
                "Now the crossover. Left's left mirrors right's RIGHT — pair "
                "them the same way round and this becomes Same Tree, which "
                "answers a different question.",
                "    return mirror(left.left, right.right) and mirror(\n"
                "        left.right, right.left\n    )",
            ),
            _s(
                "Start by pairing the root with itself.",
                "return mirror(root, root)",
            ),
        ),
    ),
    236: Worked(
        problem=236,
        naive=(
            "Find the path from the root to each node, then walk the two paths "
            "together and take the last node they share."
        ),
        why_not=(
            "It needs two searches and both paths stored, and in a tree with "
            "no parent links, building a path means threading it back out of "
            "the recursion by hand."
        ),
        insight=(
            "Let each subtree report whether it found anything. A node that "
            "hears back from BOTH sides is the point where the two searches "
            "join, and that is the ancestor."
        ),
        stages=(
            _s(
                "Report nothing found, or report the node itself. A node "
                "counts as being below itself, which this handles by stopping "
                "here rather than searching underneath.",
                "if not root or root is p or root is q:\n    return root",
            ),
            _s(
                "Ask both sides. Each answers with a node it found, or "
                "nothing.",
                "left = lowest_common_ancestor(root.left, p, q)\n"
                "right = lowest_common_ancestor(root.right, p, q)",
            ),
            _s(
                "Both sides found something, so the two nodes are on opposite "
                "branches and this is where they meet.",
                "if left and right:\n    return root",
            ),
            _s(
                "Otherwise pass up whichever side found something — either the "
                "ancestor already worked out below, or the first of the two "
                "nodes on the way to it.",
                "return left or right",
            ),
        ),
    ),
}


_TREE_BFS: dict[int, Worked] = {
    199: Worked(
        problem=199,
        naive=(
            "Walk down the right children from the root, collecting values "
            "until there is no right child left."
        ),
        why_not=(
            "It goes wrong the moment the right spine ends early. A node deep "
            "in the LEFT subtree can still be the rightmost thing on its "
            "level, and this never sees it."
        ),
        insight=(
            "What is visible is the last node of each LEVEL, not the rightmost "
            "chain. So walk level by level and take the final node of each — "
            "which is what a queue gives you for free."
        ),
        stages=(
            _s(
                "An empty tree has nothing to see.",
                "if not root:\n    return []\nview = []\nqueue = deque([root])",
            ),
            _s(
                "Measure the level before consuming it. Children get appended "
                "as you go, so the queue's length changes mid-level and only "
                "the size taken up front marks where this row ends.",
                "while queue:\n    size = len(queue)",
            ),
            _s(
                "The last node of the row is the one that can be seen.",
                "    for i in range(size):\n        node = queue.popleft()\n"
                "        if i == size - 1:\n            view.append(node.val)",
            ),
            _s(
                "Children join the back of the queue, left first, so the next "
                "row arrives in the same left-to-right order.",
                "        if node.left:\n            queue.append(node.left)\n"
                "        if node.right:\n            queue.append(node.right)\n"
                "return view",
            ),
        ),
    ),
    103: Worked(
        problem=103,
        naive=(
            "Walk the levels alternately, queueing children right-first on the "
            "rows that need reversing."
        ),
        why_not=(
            "Flipping the queue order flips the NEXT row too, not the current "
            "one, so the alternation drifts out of step. It is a fiddly bug to "
            "find because the first two rows look right."
        ),
        insight=(
            "Do not fight the traversal. Collect every row left to right the "
            "ordinary way, and reverse the finished row before storing it — "
            "the zigzag is a presentation detail, not a walking order."
        ),
        stages=(
            _s(
                "The usual level walk, plus a flag for which way this row "
                "should read.",
                "if not root:\n    return []\nlevels = []\n"
                "queue = deque([root])\nleft_to_right = True",
            ),
            _s(
                "Taking len(queue) once at the top of the loop fixes the row "
                "boundary before any children are added.",
                "while queue:\n    level = []\n    for _ in range(len(queue)):\n"
                "        node = queue.popleft()\n        level.append(node.val)",
            ),
            _s(
                "Children always go on left first. The traversal never "
                "changes; only the output does.",
                "        if node.left:\n            queue.append(node.left)\n"
                "        if node.right:\n            queue.append(node.right)",
            ),
            _s(
                "Reverse the completed row when it is a right-to-left one, "
                "then flip the flag for the next.",
                "    if not left_to_right:\n        level.reverse()\n"
                "    levels.append(level)\n"
                "    left_to_right = not left_to_right\nreturn levels",
            ),
        ),
    ),
    111: Worked(
        problem=111,
        naive=(
            "Recurse, and return one plus the smaller of the two child depths."
        ),
        why_not=(
            "A node with only one child reports a depth of one, because the "
            "missing side measures zero — but a missing child is not a leaf, "
            "so the shallowest LEAF is further down than that."
        ),
        insight=(
            "Depth-first has to search the whole tree before it can be sure it "
            "found the shallowest leaf. Breadth-first meets the levels in "
            "order, so the first leaf it sees is the answer."
        ),
        stages=(
            _s(
                "The root is level one, so an empty tree is zero and "
                "everything else starts at one.",
                "if not root:\n    return 0\nqueue = deque([root])\ndepth = 1",
            ),
            _s(
                "One row at a time, so every node in the loop body is at the "
                "current depth.",
                "while queue:\n    for _ in range(len(queue)):\n"
                "        node = queue.popleft()",
            ),
            _s(
                "The first leaf met is the shallowest one there is — nothing "
                "on a later row could beat it. Returning here is what saves "
                "walking the rest of the tree.",
                "        if not node.left and not node.right:\n"
                "            return depth",
            ),
            _s(
                "Otherwise queue the children and go a level deeper.",
                "        if node.left:\n            queue.append(node.left)\n"
                "        if node.right:\n            queue.append(node.right)\n"
                "    depth += 1\nreturn depth",
            ),
        ),
    ),
    637: Worked(
        problem=637,
        naive=(
            "Walk the tree depth-first, tagging each value with its depth, "
            "then group by depth and average each group."
        ),
        why_not=(
            "It works and it needs a second structure to group into, plus a "
            "pass to build it. A level-order walk hands you the groups already "
            "separated."
        ),
        insight=(
            "Fixing the row size before consuming the row means everything in "
            "that pass is on one level. The count is then just that size, so "
            "the average needs no bookkeeping at all."
        ),
        stages=(
            _s(
                "An empty tree has no levels, so no averages.",
                "if not root:\n    return []\naverages = []\n"
                "queue = deque([root])",
            ),
            _s(
                "Take the size ONCE. It is both the loop bound and the divisor "
                "later, which is why it goes in a variable rather than being "
                "read twice.",
                "while queue:\n    size = len(queue)\n    total = 0",
            ),
            _s(
                "Sum the row while draining exactly that many nodes.",
                "    for _ in range(size):\n        node = queue.popleft()\n"
                "        total += node.val",
            ),
            _s(
                "Queue the next row as you go, then divide by the size that "
                "was captured before any of it was added.",
                "        if node.left:\n            queue.append(node.left)\n"
                "        if node.right:\n            queue.append(node.right)\n"
                "    averages.append(total / size)\nreturn averages",
            ),
        ),
    ),
    515: Worked(
        problem=515,
        naive=(
            "Recurse with a depth argument, and keep a dictionary from depth "
            "to the largest value seen at it."
        ),
        why_not=(
            "Nothing is wrong with it except that it stores the answer in a "
            "map keyed by depth, which then has to be turned back into a list "
            "in the right order. The level walk produces that order directly."
        ),
        insight=(
            "This is the level-average walk with the running total swapped for "
            "a running maximum. Recognising a problem as one you have already "
            "solved is most of the work."
        ),
        stages=(
            _s(
                "Same skeleton as every other level walk.",
                "if not root:\n    return []\nlargest = []\n"
                "queue = deque([root])",
            ),
            _s(
                "Start the row's best as nothing. Values can be negative, so "
                "seeding with zero would quietly return the wrong answer on a "
                "row that is entirely below it.",
                "while queue:\n    best = None\n"
                "    for _ in range(len(queue)):\n        node = queue.popleft()",
            ),
            _s(
                "First value fills it in, later ones only replace it if they "
                "beat it.",
                "        if best is None or node.val > best:\n"
                "            best = node.val",
            ),
            _s(
                "The rest is unchanged from the average version.",
                "        if node.left:\n            queue.append(node.left)\n"
                "        if node.right:\n            queue.append(node.right)\n"
                "    largest.append(best)\nreturn largest",
            ),
        ),
    ),
    1161: Worked(
        problem=1161,
        naive=(
            "Collect the values level by level into a list of rows, then sum "
            "each row and find the index of the biggest total."
        ),
        why_not=(
            "It holds every value in the tree just to add them up. The sums "
            "can be accumulated as the walk goes, and then only one number per "
            "level ever needs to exist."
        ),
        insight=(
            "The answer is a level NUMBER, not a sum, so count the levels as "
            "you walk and keep the best number alongside the best total. Ties "
            "keep the earlier level, which strict greater-than gives you."
        ),
        stages=(
            _s(
                "Levels are numbered from one, so the counter starts at zero "
                "and is bumped at the top of each row.",
                "if not root:\n    return 0\nqueue = deque([root])\n"
                "level = 0\nbest_level = 1\nbest_sum = None",
            ),
            _s(
                "Each pass of the outer loop is one level, so incrementing "
                "here keeps the number in step with the row being summed.",
                "while queue:\n    level += 1\n    total = 0",
            ),
            _s(
                "Sum the row and queue the next, exactly as before.",
                "    for _ in range(len(queue)):\n        node = queue.popleft()\n"
                "        total += node.val\n        if node.left:\n"
                "            queue.append(node.left)\n        if node.right:\n"
                "            queue.append(node.right)",
            ),
            _s(
                "Strictly greater, so a later level that only ties does not "
                "displace the shallower one. None as the starting best means "
                "an all-negative tree still records its first level.",
                "    if best_sum is None or total > best_sum:\n"
                "        best_sum = total\n        best_level = level\n"
                "return best_level",
            ),
        ),
    ),
    662: Worked(
        problem=662,
        naive=(
            "Walk the levels keeping the null children in the queue too, so "
            "each row's length is its full width."
        ),
        why_not=(
            "Keeping the gaps means keeping every position in a level, and a "
            "level of a deep sparse tree can hold billions of them. Two real "
            "nodes far apart would exhaust memory before being counted."
        ),
        insight=(
            "Number the positions instead of storing them. Give the root index "
            "0 and each child twice its parent's index — then a row's width is "
            "just its last index minus its first, gaps included."
        ),
        stages=(
            _s(
                "Every node travels with the position it would occupy in a "
                "complete tree.",
                "if not root:\n    return 0\nwidest = 0\n"
                "queue = deque([(root, 0)])",
            ),
            _s(
                "Read the first index without removing it, and start last at "
                "the same place so a single-node row measures one.",
                "while queue:\n    size = len(queue)\n    _, first = queue[0]\n"
                "    last = first",
            ),
            _s(
                "Every node drained updates last, so it ends the row holding "
                "the rightmost index.",
                "    for _ in range(size):\n        node, index = queue.popleft()\n"
                "        last = index",
            ),
            _s(
                "Children take twice the parent's index, plus one on the "
                "right. That is the standard heap numbering, and it keeps the "
                "gaps countable without storing them.",
                "        if node.left:\n"
                "            queue.append((node.left, index * 2))\n"
                "        if node.right:\n"
                "            queue.append((node.right, index * 2 + 1))",
            ),
            _s(
                "The span of the row, including the empty positions in "
                "between.",
                "    width = last - first + 1\n    if width > widest:\n"
                "        widest = width\nreturn widest",
            ),
        ),
    ),
}


_GRAPH: dict[int, Worked] = {
    733: Worked(
        problem=733,
        naive=(
            "Repaint the starting pixel, then sweep the whole image again and "
            "again, repainting any pixel next to a painted one, until a full "
            "sweep changes nothing."
        ),
        why_not=(
            "Each sweep only advances the paint by one pixel, so a long thin "
            "region costs a sweep per pixel of its length. The image gets read "
            "over and over to make one step of progress."
        ),
        insight=(
            "The region is connected, so it can be walked instead of swept. "
            "Paint a pixel, then move straight to its four neighbours and do "
            "the same — the walk goes exactly as far as the colour does."
        ),
        stages=(
            _s(
                "Remember the colour being replaced BEFORE anything is "
                "repainted, because the first repaint destroys it.",
                "start = image[sr][sc]",
            ),
            _s(
                "If the new colour is the old one, painting changes nothing "
                "and the walk would never stop. This one line is the whole "
                "termination argument.",
                "if start == color:\n    return image\n"
                "rows, cols = len(image), len(image[0])",
            ),
            _s(
                "Two ways to stop: off the edge of the image, or on a pixel "
                "that was never part of the region.",
                "def fill(r, c):\n"
                "    if r < 0 or r >= rows or c < 0 or c >= cols:\n"
                "        return\n    if image[r][c] != start:\n        return",
            ),
            _s(
                "Painting the pixel is also what marks it visited — it no "
                "longer matches start, so the walk will not come back to it. "
                "No separate seen-set is needed.",
                "    image[r][c] = color",
            ),
            _s(
                "Then the same question four times over.",
                "    fill(r + 1, c)\n    fill(r - 1, c)\n    fill(r, c + 1)\n"
                "    fill(r, c - 1)\n\nfill(sr, sc)\nreturn image",
            ),
        ),
    ),
    994: Worked(
        problem=994,
        naive=(
            "Take each rotten orange in turn and walk outwards from it, "
            "recording how far the rot reaches each fresh one."
        ),
        why_not=(
            "The oranges rot in parallel, not one source after another. "
            "Running the sources separately means every fresh orange has to "
            "keep the smallest time across all of them, and each walk covers "
            "ground the others already did."
        ),
        insight=(
            "Put every rotten orange in the queue before starting. A "
            "breadth-first walk from many sources at once expands them all in "
            "step, so the first time a fresh orange is reached is its minute."
        ),
        stages=(
            _s(
                "One pass to seed the queue with every rotten orange, and to "
                "count how many fresh ones there are to account for.",
                "rows, cols = len(grid), len(grid[0])\nqueue = deque()\n"
                "fresh = 0\nfor r in range(rows):\n    for c in range(cols):\n"
                "        if grid[r][c] == 2:\n            queue.append((r, c))\n"
                "        elif grid[r][c] == 1:\n            fresh += 1",
            ),
            _s(
                "Each pass of the outer loop is one minute. Stopping when "
                "fresh hits zero is what stops the clock running on after the "
                "last orange rots.",
                "minutes = 0\nwhile queue and fresh:\n    minutes += 1",
            ),
            _s(
                "Drain exactly the oranges that were rotten at the START of "
                "the minute. Ones that rot during it belong to the next.",
                "    for _ in range(len(queue)):\n        r, c = queue.popleft()",
            ),
            _s(
                "Spread to the four neighbours that are still fresh, marking "
                "them rotten as they are queued so no one claims them twice.",
                "        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):\n"
                "            nr, nc = r + dr, c + dc\n"
                "            if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] == 1:\n"
                "                grid[nr][nc] = 2\n                fresh -= 1\n"
                "                queue.append((nr, nc))",
            ),
            _s(
                "Anything still fresh was never reachable, which is the -1 "
                "case rather than a longer wait.",
                "return -1 if fresh else minutes",
            ),
        ),
    ),
    133: Worked(
        problem=133,
        naive=(
            "Walk the graph making a new node for each one visited, and keep a "
            "set of the originals already seen."
        ),
        why_not=(
            "A set says you have seen a node but not which copy you made of "
            "it. When a neighbour turns out to be already visited, there is no "
            "way to link to its clone, so the edges cannot be rebuilt."
        ),
        insight=(
            "Use a dictionary from original to clone rather than a set. It "
            "answers both questions at once — whether a node has been visited, "
            "and which copy to point at."
        ),
        stages=(
            _s(
                "The map is the visited record and the lookup table in one.",
                "clones = {}",
            ),
            _s(
                "Already copied means return the copy, not a new one. This is "
                "what makes a cycle terminate and what keeps shared "
                "neighbours shared.",
                "def copy(cur):\n    if not cur:\n        return None\n"
                "    if cur in clones:\n        return clones[cur]",
            ),
            _s(
                "Register the clone BEFORE recursing. A node that is its own "
                "neighbour's neighbour will come back round to itself, and by "
                "then the entry has to be there or it recurses forever.",
                "    clone = Node(cur.val)\n    clones[cur] = clone",
            ),
            _s(
                "Now the edges: each neighbour's clone, copied or fetched.",
                "    for neighbor in cur.neighbors:\n"
                "        clone.neighbors.append(copy(neighbor))\n"
                "    return clone\n\nreturn copy(node)",
            ),
        ),
    ),
    695: Worked(
        problem=695,
        naive=(
            "Find each island by walking it and collecting its cells into a "
            "list, then take the length of the longest list."
        ),
        why_not=(
            "The cells are never needed, only how many there are. Collecting "
            "them means the biggest island is held in memory in full when a "
            "single counter would do."
        ),
        insight=(
            "Let the walk RETURN a number instead of marking silently. Each "
            "call reports one for itself plus whatever its four neighbours "
            "report, and the total comes back up with no list at all."
        ),
        stages=(
            _s(
                "Off the grid contributes nothing to an area.",
                "if not grid:\n    return 0\n"
                "rows, cols = len(grid), len(grid[0])\n\ndef fill(r, c):\n"
                "    if r < 0 or c < 0 or r >= rows or c >= cols:\n"
                "        return 0",
            ),
            _s(
                "Water, or land already counted, also contributes nothing.",
                "    if grid[r][c] != 1:\n        return 0",
            ),
            _s(
                "Sinking the cell is what stops it being counted twice. It has "
                "to happen before the recursion, not after.",
                "    grid[r][c] = 0",
            ),
            _s(
                "One for this cell, plus everything the neighbours find.",
                "    return 1 + fill(r + 1, c) + fill(r - 1, c) + fill(\n"
                "        r, c + 1\n    ) + fill(r, c - 1)",
            ),
            _s(
                "Start a walk everywhere. Cells already sunk return zero "
                "immediately, so the sweep is cheap.",
                "best = 0\nfor r in range(rows):\n    for c in range(cols):\n"
                "        area = fill(r, c)\n        if area > best:\n"
                "            best = area\nreturn best",
            ),
        ),
    ),
    547: Worked(
        problem=547,
        naive=(
            "For each pair of cities, work out whether they are connected, and "
            "group the cities by that."
        ),
        why_not=(
            "Connectedness is not given directly — it is reachability through "
            "other cities. Working it out pair by pair means repeating the "
            "same search for every pair in a province."
        ),
        insight=(
            "Do not count connections, count the number of times you have to "
            "START a walk. Everything one walk reaches is one province, so a "
            "second walk can only mean a second province."
        ),
        stages=(
            _s(
                "The visited set spans all the walks, not just the current "
                "one. That is what makes the second walk mean something.",
                "n = len(is_connected)\nseen = set()",
            ),
            _s(
                "The graph is a matrix, so a city's neighbours are found by "
                "scanning its row rather than reading a list.",
                "def visit(city):\n    seen.add(city)\n"
                "    for other in range(n):",
            ),
            _s(
                "Follow every direct connection not already visited.",
                "        if is_connected[city][other] and other not in seen:\n"
                "            visit(other)",
            ),
            _s(
                "A city still unseen belongs to no province counted so far, so "
                "walking from it discovers exactly one more.",
                "groups = 0\nfor city in range(n):\n    if city not in seen:\n"
                "        visit(city)\n        groups += 1\nreturn groups",
            ),
        ),
    ),
    542: Worked(
        problem=542,
        naive=(
            "For each cell containing a one, walk outwards until a zero is "
            "found, and record the distance."
        ),
        why_not=(
            "Every one starts its own search, and searches from neighbouring "
            "cells cover almost the same ground. A grid that is mostly ones "
            "makes this quadratic in the number of cells."
        ),
        insight=(
            "Search from the zeros instead, all of them at once. A "
            "breadth-first wave from every zero reaches each cell at exactly "
            "its distance to the nearest one, in a single pass."
        ),
        stages=(
            _s(
                "Minus one means not yet reached, which doubles as the "
                "visited check later — no second grid needed.",
                "rows, cols = len(mat), len(mat[0])\n"
                "out = [[-1] * cols for _ in range(rows)]\nqueue = deque()",
            ),
            _s(
                "Every zero is a source at distance zero. Seeding them all "
                "before the walk starts is the whole trick.",
                "for r in range(rows):\n    for c in range(cols):\n"
                "        if mat[r][c] == 0:\n            out[r][c] = 0\n"
                "            queue.append((r, c))",
            ),
            _s(
                "No level bookkeeping here, because the distance is carried in "
                "the grid rather than counted by rounds.",
                "while queue:\n    r, c = queue.popleft()\n"
                "    for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):\n"
                "        nr, nc = r + dr, c + dc",
            ),
            _s(
                "Still minus one means unreached, and breadth-first means the "
                "first arrival is the nearest. So it is filled once and never "
                "revisited.",
                "        if 0 <= nr < rows and 0 <= nc < cols and out[nr][nc] == -1:\n"
                "            out[nr][nc] = out[r][c] + 1\n"
                "            queue.append((nr, nc))\nreturn out",
            ),
        ),
    ),
    417: Worked(
        problem=417,
        naive=(
            "For every cell, walk downhill and see whether it can reach the "
            "Pacific, then walk again and see whether it can reach the "
            "Atlantic."
        ),
        why_not=(
            "That is two searches per cell, each of which can cover the whole "
            "grid, and none of the work is shared between them. Cells on the "
            "same downhill path all rediscover the same route."
        ),
        insight=(
            "Reverse the direction. Start at each ocean and climb to "
            "neighbours of equal or greater height — that finds every cell "
            "that could have flowed there, in one walk per ocean."
        ),
        stages=(
            _s(
                "One set per ocean, holding the cells that can reach it.",
                "if not heights:\n    return []\n"
                "rows, cols = len(heights), len(heights[0])\n"
                "pacific = set()\natlantic = set()",
            ),
            _s(
                "Which ocean is being filled is just an argument, so one "
                "function serves both.",
                "def climb(r, c, seen):\n    seen.add((r, c))\n"
                "    for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):\n"
                "        nr, nc = r + dr, c + dc",
            ),
            _s(
                "The comparison is the reversal: water flows to lower ground, "
                "so climbing goes to neighbours that are at least as HIGH.",
                "        if 0 <= nr < rows and 0 <= nc < cols:\n"
                "            if (nr, nc) not in seen and heights[nr][nc] >= heights[r][c]:\n"
                "                climb(nr, nc, seen)",
            ),
            _s(
                "Seed from the edges: top and left for the Pacific, bottom and "
                "right for the Atlantic.",
                "for c in range(cols):\n    climb(0, c, pacific)\n"
                "    climb(rows - 1, c, atlantic)\nfor r in range(rows):\n"
                "    climb(r, 0, pacific)\n    climb(r, cols - 1, atlantic)",
            ),
            _s(
                "A cell that can reach both is in both sets, so the answer is "
                "the intersection.",
                "return [list(cell) for cell in sorted(pacific & atlantic)]",
            ),
        ),
    ),
}


_BACKTRACKING: dict[int, Worked] = {
    90: Worked(
        problem=90,
        naive=(
            "Generate every subset the ordinary way, then remove the repeats "
            "by putting them in a set."
        ),
        why_not=(
            "A list is not hashable, so each subset has to be converted to "
            "something that is, and every duplicate is still built in full "
            "before being thrown away. The work is done and then discarded."
        ),
        insight=(
            "Sort first, so equal values sit together. Then at each level, "
            "take a value only the first time it is offered — later copies at "
            "the same level would start an identical branch."
        ),
        stages=(
            _s(
                "Sorting is what makes duplicates adjacent, and adjacency is "
                "what makes them detectable with one comparison.",
                "nums.sort()\nresult = []\ncurrent = []",
            ),
            _s(
                "Every state on the way down is itself a subset, so it is "
                "recorded on arrival rather than only at the bottom.",
                "def backtrack(start):\n    result.append(current[:])",
            ),
            _s(
                "The guard is i > start, not i > 0. The FIRST copy at this "
                "level is allowed — it is the second and later ones that would "
                "repeat a branch already taken.",
                "    for i in range(start, len(nums)):\n"
                "        if i > start and nums[i] == nums[i - 1]:\n"
                "            continue",
            ),
            _s(
                "Choose, explore, then undo. The pop is what makes the same "
                "list usable for every branch instead of a fresh copy each "
                "time.",
                "        current.append(nums[i])\n        backtrack(i + 1)\n"
                "        current.pop()\n\nbacktrack(0)\nreturn result",
            ),
        ),
    ),
    46: Worked(
        problem=46,
        naive=(
            "Build the orderings by picking from the values after the last one "
            "taken, the way subsets and combinations do."
        ),
        why_not=(
            "That deliberately never looks backwards, which is right when "
            "order does not matter and wrong here. It would produce each SET "
            "of values once instead of each arrangement of them."
        ),
        insight=(
            "Order matters, so every unused value is a candidate at every "
            "step, not just the ones further along. What has to be tracked is "
            "which values are used, not how far you have got."
        ),
        stages=(
            _s(
                "A used flag per position, rather than a start index.",
                "result = []\ncurrent = []\nused = [False] * len(nums)",
            ),
            _s(
                "A full-length arrangement is finished. Copying is essential — "
                "current keeps being edited after this.",
                "def backtrack():\n    if len(current) == len(nums):\n"
                "        result.append(current[:])\n        return",
            ),
            _s(
                "Every position is offered every time, from the beginning.",
                "    for i in range(len(nums)):\n        if used[i]:\n"
                "            continue",
            ),
            _s(
                "Mark and take, then explore.",
                "        used[i] = True\n        current.append(nums[i])\n"
                "        backtrack()",
            ),
            _s(
                "Undo BOTH. Forgetting to clear the flag is the classic bug "
                "here, and it silently produces too few answers rather than "
                "an error.",
                "        current.pop()\n        used[i] = False\n\n"
                "backtrack()\nreturn result",
            ),
        ),
    ),
    39: Worked(
        problem=39,
        naive=(
            "Recurse over each candidate with a start index of i + 1, the way "
            "combinations do, to avoid repeating combinations."
        ),
        why_not=(
            "i + 1 says 'never use this candidate again', but the question "
            "allows reuse without limit. It rules out the answers that pick "
            "the same number twice, which are most of them."
        ),
        insight=(
            "Recurse with i, not i + 1. Staying put allows the same candidate "
            "again, while never going backwards still stops the same "
            "combination being built in a different order."
        ),
        stages=(
            _s(
                "The remainder is carried down rather than a running total "
                "compared at the bottom, so a branch can be abandoned early.",
                "result = []\ncurrent = []",
            ),
            _s(
                "Exactly zero left means the combination lands on the target.",
                "def backtrack(start, remaining):\n    if remaining == 0:\n"
                "        result.append(current[:])\n        return",
            ),
            _s(
                "Overshooting means every deeper branch overshoots too, since "
                "candidates are positive. This is the pruning the naive "
                "running-total version cannot do.",
                "    if remaining < 0:\n        return",
            ),
            _s(
                "Recursing with i rather than i + 1 is the entire difference "
                "from Combinations — the same candidate stays available.",
                "    for i in range(start, len(candidates)):\n"
                "        current.append(candidates[i])\n"
                "        backtrack(i, remaining - candidates[i])",
            ),
            _s(
                "And undo on the way back out.",
                "        current.pop()\n\nbacktrack(0, target)\nreturn result",
            ),
        ),
    ),
    79: Worked(
        problem=79,
        naive=(
            "Search from every cell, keeping a set of the cells used so far in "
            "the current attempt."
        ),
        why_not=(
            "Nothing is wrong with the logic — it is the set that costs. It is "
            "added to and removed from at every step of a search that already "
            "branches four ways per letter, and the grid can record the same "
            "thing for free."
        ),
        insight=(
            "The board is already a place to write. Overwrite a cell with a "
            "character the word cannot contain while you are standing on it, "
            "and put it back when you leave."
        ),
        stages=(
            _s(
                "Running off the end of the word means every letter matched.",
                "rows, cols = len(board), len(board[0])\n\n"
                "def search(r, c, i):\n    if i == len(word):\n"
                "        return True",
            ),
            _s(
                "Off the grid, or the wrong letter, ends this branch. The "
                "bounds check has to come first or the lookup below reads out "
                "of range.",
                "    if r < 0 or r >= rows or c < 0 or c >= cols:\n"
                "        return False\n    if board[r][c] != word[i]:\n"
                "        return False",
            ),
            _s(
                "Blank the cell so the four neighbours cannot walk back onto "
                "it. This is the visited set, stored in place.",
                '    board[r][c] = "#"',
            ),
            _s(
                "Four directions, and or() abandons the rest as soon as one "
                "succeeds.",
                "    found = (\n        search(r + 1, c, i + 1)\n"
                "        or search(r - 1, c, i + 1)\n"
                "        or search(r, c + 1, i + 1)\n"
                "        or search(r, c - 1, i + 1)\n    )",
            ),
            _s(
                "Restore it before returning, or a later attempt starting "
                "elsewhere finds a board full of holes.",
                "    board[r][c] = word[i]\n    return found",
            ),
            _s(
                "Any cell could be the first letter.",
                "for r in range(rows):\n    for c in range(cols):\n"
                "        if search(r, c, 0):\n            return True\n"
                "return False",
            ),
        ),
    ),
    77: Worked(
        problem=77,
        naive=(
            "Generate every arrangement of k numbers from 1 to n, then discard "
            "the ones that are reorderings of a choice already seen."
        ),
        why_not=(
            "Each choice of k numbers has k factorial arrangements, so all but "
            "one of them is built only to be thrown away. At k of five that is "
            "a hundred and twenty times too much work."
        ),
        insight=(
            "Only ever pick numbers ABOVE the last one taken. Every choice "
            "then gets built exactly once, in increasing order, and there is "
            "nothing to deduplicate."
        ),
        stages=(
            _s(
                "start is the floor for this level — the smallest value still "
                "allowed.",
                "out = []\npicked = []",
            ),
            _s(
                "k values picked is a complete choice.",
                "def walk(start):\n    if len(picked) == k:\n"
                "        out.append(list(picked))\n        return",
            ),
            _s(
                "The range runs to n inclusive, which is why it is n + 1.",
                "    for value in range(start, n + 1):\n"
                "        picked.append(value)",
            ),
            _s(
                "Recursing with value + 1 is what enforces the increasing "
                "order, and so what stops the same choice appearing twice.",
                "        walk(value + 1)\n        picked.pop()\n\nwalk(1)\n"
                "return out",
            ),
        ),
    ),
    17: Worked(
        problem=17,
        naive=(
            "Take the letters of the first digit, then for each of those "
            "append the letters of the second, and so on with a loop per digit."
        ),
        why_not=(
            "The number of loops depends on the number of digits, which cannot "
            "be written down in advance. It only works for an input length "
            "fixed when the code was written."
        ),
        insight=(
            "One digit is one LEVEL of the recursion, and its letters are that "
            "level's branches. Recursion writes a variable number of nested "
            "loops for you."
        ),
        stages=(
            _s(
                "An empty input has no combinations at all — not one empty "
                "string, which is what the recursion would otherwise return.",
                "if not digits:\n    return []",
            ),
            _s(
                "The keypad, as a lookup from digit to its letters.",
                'keys = {\n    "2": "abc",\n    "3": "def",\n    "4": "ghi",\n'
                '    "5": "jkl",\n    "6": "mno",\n    "7": "pqrs",\n'
                '    "8": "tuv",\n    "9": "wxyz",\n}\nout = []',
            ),
            _s(
                "Past the last digit means a complete string.",
                "def walk(index, built):\n    if index == len(digits):\n"
                "        out.append(built)\n        return",
            ),
            _s(
                "Each letter of this digit is one branch, and the string is "
                "passed down rather than mutated — so there is nothing to "
                "undo on the way back out.",
                "    for letter in keys[digits[index]]:\n"
                "        walk(index + 1, built + letter)\n\n"
                'walk(0, "")\nreturn out',
            ),
        ),
    ),
    131: Worked(
        problem=131,
        naive=(
            "Generate every possible way of cutting the string, then keep the "
            "ones where every piece reads the same both ways."
        ),
        why_not=(
            "There are two to the n minus one ways to cut a string, and nearly "
            "all of them fail on the very first piece. Building each one in "
            "full before testing it wastes the whole tail."
        ),
        insight=(
            "Test the piece as you cut it. If the first piece is not a "
            "palindrome, every cutting that begins with it is doomed, so that "
            "entire branch never has to be explored."
        ),
        stages=(
            _s(
                "start is where the next piece begins, so it is also how much "
                "of the string is already accounted for.",
                "out = []\nbuilt = []",
            ),
            _s(
                "Reaching the end means the whole string is covered by valid "
                "pieces.",
                "def walk(start):\n    if start == len(text):\n"
                "        out.append(list(built))\n        return",
            ),
            _s(
                "Every possible length for the next piece. The end runs to "
                "len(text) inclusive so the last piece can reach the end.",
                "    for end in range(start + 1, len(text) + 1):\n"
                "        piece = text[start:end]",
            ),
            _s(
                "The check before the recursion is the pruning — a failing "
                "piece costs one comparison instead of a whole subtree.",
                "        if piece == piece[::-1]:\n            built.append(piece)\n"
                "            walk(end)\n            built.pop()\n\nwalk(0)\n"
                "return out",
            ),
        ),
    ),
}


_HEAP: dict[int, Worked] = {
    347: Worked(
        problem=347,
        naive=(
            "Count how often each value appears, sort the counts descending, "
            "and take the first k."
        ),
        why_not=(
            "Sorting orders everything when only the top k is wanted. With a "
            "million distinct values and k of three, that is n log n spent to "
            "read three entries off the front."
        ),
        insight=(
            "A heap of size k only ever holds the best k seen so far. Push "
            "everything, and evict the smallest whenever the heap grows past "
            "k — the cost per item is log k, not log n."
        ),
        stages=(
            _s(
                "Frequencies first. Nothing about the heap helps with "
                "counting.",
                "counts = {}\nfor n in nums:\n"
                "    counts[n] = counts.get(n, 0) + 1",
            ),
            _s(
                "Count goes first in the tuple, because that is what the heap "
                "orders on. The value rides along.",
                "heap = []\nfor value, count in counts.items():\n"
                "    heapq.heappush(heap, (count, value))",
            ),
            _s(
                "This is a min-heap, so the smallest count is on top — which "
                "is exactly the one to throw away when there are too many.",
                "    if len(heap) > k:\n        heapq.heappop(heap)",
            ),
            _s(
                "Whatever survived is the top k. The question allows any "
                "order, so the heap's internal arrangement is fine as it is.",
                "return [value for count, value in heap]",
            ),
        ),
    ),
    973: Worked(
        problem=973,
        naive=(
            "Work out each point's distance, sort the points by it, and take "
            "the first k."
        ),
        why_not=(
            "Same objection as always: a full sort delivers a total order when "
            "only a threshold is needed. It is also more memory, since every "
            "point has to be held and ordered."
        ),
        insight=(
            "Keep a heap of exactly k, holding NEGATIVE distances. The min-"
            "heap then puts the FURTHEST of the current best k on top, which "
            "is the one to evict when a better point arrives."
        ),
        stages=(
            _s(
                "Comparing squared distances gives the same ordering as real "
                "ones, so the square root is never worth computing.",
                "heap = []\nfor x, y in points:\n    dist = x * x + y * y",
            ),
            _s(
                "Negating flips the heap's sense. Without it the heap would "
                "hold on to the nearest points and evict the ones being "
                "looked for.",
                "    heapq.heappush(heap, (-dist, x, y))",
            ),
            _s(
                "Over size, so drop the worst — which, negated, is on top.",
                "    if len(heap) > k:\n        heapq.heappop(heap)",
            ),
            _s(
                "The k that survived are the closest, and the distance is "
                "dropped on the way out.",
                "return [[x, y] for dist, x, y in heap]",
            ),
        ),
    ),
    1046: Worked(
        problem=1046,
        naive=(
            "Sort the stones, take the last two, work out what is left, insert "
            "it back in the right place, and repeat."
        ),
        why_not=(
            "Each round inserts into a sorted list, which shifts everything "
            "after the insertion point. That is linear per smash, and there "
            "are as many smashes as there are stones."
        ),
        insight=(
            "Only the two largest matter at any moment, and the result goes "
            "straight back into the pile. That is a priority queue — log n to "
            "take the largest and log n to return the remainder."
        ),
        stages=(
            _s(
                "The heap is a min-heap and the biggest stone is wanted, so "
                "every weight is stored negated. Heapify does the whole list "
                "in linear time, which beats pushing them one at a time.",
                "heap = [-s for s in stones]\nheapq.heapify(heap)",
            ),
            _s(
                "Two stones are needed for a smash, so one left ends it.",
                "while len(heap) > 1:",
            ),
            _s(
                "Negate on the way out to get real weights back. first is the "
                "heavier, because the more negative value popped first.",
                "    first = -heapq.heappop(heap)\n"
                "    second = -heapq.heappop(heap)",
            ),
            _s(
                "Equal weights destroy each other and nothing goes back. "
                "Otherwise the difference rejoins the pile, negated again.",
                "    if first != second:\n"
                "        heapq.heappush(heap, -(first - second))",
            ),
            _s(
                "One stone or none. The heap may be empty, which is the zero "
                "case.",
                "return -heap[0] if heap else 0",
            ),
        ),
    ),
    692: Worked(
        problem=692,
        naive=(
            "Count the words, sort by count descending, and sort alphabetically "
            "within each group of equal counts."
        ),
        why_not=(
            "Two orderings pulling in opposite directions — one descending, "
            "one ascending — is awkward to express as a single comparison, and "
            "easy to get subtly wrong on the tie-break."
        ),
        insight=(
            "Put both keys in one tuple with the count NEGATED. Then a single "
            "ascending order gives most-frequent first and, within a tie, "
            "alphabetical — no custom comparison at all."
        ),
        stages=(
            _s(
                "Counting first, as always.",
                "counts = {}\nfor word in words:\n"
                "    counts[word] = counts.get(word, 0) + 1",
            ),
            _s(
                "Negative count first, word second. Ascending on this tuple is "
                "exactly the order the question asks for.",
                "heap = [(-count, word) for word, count in counts.items()]",
            ),
            _s(
                "Heapify builds the whole thing in one pass rather than n "
                "separate pushes.",
                "heapq.heapify(heap)",
            ),
            _s(
                "Pop k times and keep the word. Popping is what produces the "
                "order — reading the heap's list directly would not.",
                "return [heapq.heappop(heap)[1] for _ in range(k)]",
            ),
        ),
    ),
    451: Worked(
        problem=451,
        naive=(
            "Count the characters, then sort the string with each character's "
            "count as its sort key."
        ),
        why_not=(
            "Sorting the characters individually does n log n work on every "
            "copy of every character, when there are only as many distinct "
            "characters as there are distinct characters."
        ),
        insight=(
            "Order the DISTINCT characters, not the string. Once they come out "
            "most-frequent first, each one's copies can be written out in a "
            "single repeat."
        ),
        stages=(
            _s(
                "One entry per distinct character, however many times it "
                "appears.",
                "counts = {}\nfor ch in s:\n"
                "    counts[ch] = counts.get(ch, 0) + 1",
            ),
            _s(
                "Negated count so the most frequent surfaces first.",
                "heap = [(-count, ch) for ch, count in counts.items()]\n"
                "heapq.heapify(heap)",
            ),
            _s(
                "Pop until empty — every character is wanted, just in order.",
                "out = []\nwhile heap:\n    count, ch = heapq.heappop(heap)",
            ),
            _s(
                "The count is negative, so negating it back gives the number "
                "of copies. Joining once at the end beats repeated "
                "concatenation.",
                '    out.append(ch * -count)\nreturn "".join(out)',
            ),
        ),
    ),
    378: Worked(
        problem=378,
        naive=(
            "Flatten the matrix into one list, sort it, and take the value at "
            "index k minus one."
        ),
        why_not=(
            "It reads and sorts every cell, throwing away the fact that each "
            "row is already sorted. For a k much smaller than the matrix, "
            "almost all of that work is wasted."
        ),
        insight=(
            "This is a k-way merge. Hold the current head of each row in a "
            "heap; the smallest of those heads is the next value overall, and "
            "its row refills the slot it left."
        ),
        stages=(
            _s(
                "Seed with the first value of each row, tagged with where it "
                "came from. Only k rows can ever contribute to the kth "
                "smallest, so there is no point seeding more.",
                "heap = []\nfor row in range(min(len(matrix), k)):\n"
                "    heapq.heappush(heap, (matrix[row][0], row, 0))",
            ),
            _s(
                "Each pop is the next smallest value in the whole matrix.",
                "value = 0\nfor _ in range(k):\n"
                "    value, row, col = heapq.heappop(heap)",
            ),
            _s(
                "Refill from the same row, one step along. That row's next "
                "value is the only new candidate the pop could have exposed.",
                "    if col + 1 < len(matrix[row]):\n"
                "        heapq.heappush(heap, (matrix[row][col + 1], row, col + 1))",
            ),
            _s(
                "After k pops, the last value taken is the kth smallest.",
                "return value",
            ),
        ),
    ),
    767: Worked(
        problem=767,
        naive=(
            "Sort the characters by frequency and lay them out in that order, "
            "inserting a different one whenever two would collide."
        ),
        why_not=(
            "Fixing collisions locally does not work, because using a "
            "character now changes which one is most pressing next. A choice "
            "that looks fine can strand the common letter at the end."
        ),
        insight=(
            "Always place the character with the most left, and hold the one "
            "just used out of the running for exactly one turn. That keeps the "
            "commonest letter spread out instead of piling up at the end."
        ),
        stages=(
            _s(
                "Counts into a max-heap by negating, as usual.",
                "counts = {}\nfor ch in s:\n"
                "    counts[ch] = counts.get(ch, 0) + 1\n"
                "heap = [(-count, ch) for ch, count in counts.items()]\n"
                "heapq.heapify(heap)",
            ),
            _s(
                "held is the character used on the previous turn — deliberately "
                "outside the heap so it cannot be chosen twice running.",
                "out = []\nheld = None",
            ),
            _s(
                "Take the most plentiful available character and place it.",
                "while heap:\n    count, ch = heapq.heappop(heap)\n"
                "    out.append(ch)",
            ),
            _s(
                "Now the previous one has served its turn and comes back. "
                "Returning it AFTER this pop is what enforces the gap.",
                "    if held:\n        heapq.heappush(heap, held)",
            ),
            _s(
                "The count is negative, so adding one uses a copy. A character "
                "with none left is dropped rather than held.",
                "    count += 1\n    held = (count, ch) if count else None",
            ),
            _s(
                "Running out early means some character was too common to "
                "separate, and no arrangement exists.",
                '    \nreturn "".join(out) if len(out) == len(s) else ""',
            ),
        ),
    ),
}


_TOPOLOGICAL: dict[int, Worked] = {
    210: Worked(
        problem=210,
        naive=(
            "Repeatedly scan the courses for one whose prerequisites are all "
            "done, take it, and start scanning again."
        ),
        why_not=(
            "Each course taken costs a fresh scan of everything still "
            "outstanding, so the scanning is quadratic. The information about "
            "what just became available is thrown away every round."
        ),
        insight=(
            "Count how many prerequisites each course is still waiting on. "
            "Finishing a course decrements its dependents, and any that reach "
            "zero are ready — so readiness is discovered, not searched for."
        ),
        stages=(
            _s(
                "Edges point from prerequisite to the course it unlocks, "
                "which is the direction the peeling travels.",
                "graph = {i: [] for i in range(num_courses)}\n"
                "indegree = [0] * num_courses\n"
                "for course, prereq in prerequisites:\n"
                "    graph[prereq].append(course)\n    indegree[course] += 1",
            ),
            _s(
                "Everything waiting on nothing can be taken immediately.",
                "queue = deque([\n    i for i in range(num_courses)\n"
                "    if indegree[i] == 0\n])\norder = []",
            ),
            _s(
                "Unlike Course Schedule, the order taken is the answer, so it "
                "is recorded rather than just counted.",
                "while queue:\n    node = queue.popleft()\n"
                "    order.append(node)",
            ),
            _s(
                "Finishing this course removes one obstacle from each course "
                "it unlocks. Reaching zero is the moment one becomes ready.",
                "    for nxt in graph[node]:\n        indegree[nxt] -= 1\n"
                "        if indegree[nxt] == 0:\n            queue.append(nxt)",
            ),
            _s(
                "A short order means some courses never reached zero, which "
                "can only happen if they depend on each other in a cycle.",
                "return order if len(order) == num_courses else []",
            ),
        ),
    ),
    310: Worked(
        problem=310,
        naive=(
            "Root the tree at every node in turn, measure its height, and keep "
            "the nodes that gave the smallest."
        ),
        why_not=(
            "That is a full traversal per node, so n squared work. Every one "
            "of those traversals covers the same tree, learning almost the "
            "same thing each time."
        ),
        insight=(
            "The best roots are in the middle, and the middle is what is left "
            "when you strip the outside. Peel off all the leaves, then the new "
            "leaves, until one or two nodes remain."
        ),
        stages=(
            _s(
                "A single node is its own centre, and has no edges for the "
                "peeling below to find.",
                "if n == 1:\n    return [0]",
            ),
            _s(
                "Undirected, so every edge is stored both ways. Sets, because "
                "neighbours get removed as the peeling goes.",
                "graph = {i: set() for i in range(n)}\nfor a, b in edges:\n"
                "    graph[a].add(b)\n    graph[b].add(a)",
            ),
            _s(
                "A leaf is a node with exactly one neighbour left.",
                "leaves = [i for i in range(n) if len(graph[i]) == 1]\n"
                "remaining = n",
            ),
            _s(
                "Stop at two, not at zero. The centre of a tree is one node or "
                "two, and peeling past that would strip the answer itself.",
                "while remaining > 2:\n    remaining -= len(leaves)\n"
                "    next_leaves = []",
            ),
            _s(
                "Detach each leaf from its only neighbour. That neighbour "
                "becomes a leaf in turn if it is now down to one edge.",
                "    for leaf in leaves:\n        neighbor = graph[leaf].pop()\n"
                "        graph[neighbor].remove(leaf)\n"
                "        if len(graph[neighbor]) == 1:\n"
                "            next_leaves.append(neighbor)\n"
                "    leaves = next_leaves\nreturn leaves",
            ),
        ),
    ),
    802: Worked(
        problem=802,
        naive=(
            "From every node, walk the graph and check whether every path it "
            "can take reaches a dead end."
        ),
        why_not=(
            "Each walk explores the whole reachable graph, and nodes share "
            "most of what they reach. It also needs cycle detection inside "
            "every walk, which is where the bugs live."
        ),
        insight=(
            "Turn the arrows around. A node with no way out is safe; a node "
            "all of whose exits lead to safe nodes is safe too. Peeling from "
            "the dead ends along reversed edges finds exactly those."
        ),
        stages=(
            _s(
                "Outdegree counts the exits still unaccounted for, and the "
                "reversed graph says who to tell when one is settled.",
                "n = len(graph)\nreverse = {i: [] for i in range(n)}\n"
                "outdegree = [0] * n",
            ),
            _s(
                "One pass builds both.",
                "for node, edges in enumerate(graph):\n"
                "    outdegree[node] = len(edges)\n    for nxt in edges:\n"
                "        reverse[nxt].append(node)",
            ),
            _s(
                "A node with nowhere to go is trivially safe — every path out "
                "of it ends immediately, there being none.",
                "queue = deque([i for i in range(n) if outdegree[i] == 0])\n"
                "safe = []",
            ),
            _s(
                "Settling a node reduces the unsettled exits of everyone "
                "pointing at it. At zero, all of that node's exits are known "
                "safe, so it is safe.",
                "while queue:\n    node = queue.popleft()\n"
                "    safe.append(node)\n    for prev in reverse[node]:\n"
                "        outdegree[prev] -= 1\n"
                "        if outdegree[prev] == 0:\n            queue.append(prev)",
            ),
            _s(
                "Anything in a cycle never drains, and so never appears. The "
                "answer is asked for in ascending order.",
                "safe.sort()\nreturn safe",
            ),
        ),
    ),
    1462: Worked(
        problem=1462,
        naive=(
            "For each query, walk the prerequisite graph from one course to "
            "see whether it reaches the other."
        ),
        why_not=(
            "A walk per query, and there can be as many queries as there are "
            "pairs of courses. Every walk re-derives reachability that the "
            "previous ones already worked out."
        ),
        insight=(
            "Work out every course's full prerequisite set once. Peeling in "
            "topological order means a course's prerequisites are all settled "
            "before it is reached, so each one just inherits and adds."
        ),
        stages=(
            _s(
                "The usual peel setup, edges running prerequisite to course.",
                "graph = {i: [] for i in range(num_courses)}\n"
                "indegree = [0] * num_courses\n"
                "for prereq, course in prerequisites:\n"
                "    graph[prereq].append(course)\n    indegree[course] += 1",
            ),
            _s(
                "One set per course, to hold everything that must come before "
                "it — directly or at any remove.",
                "needs = [set() for _ in range(num_courses)]\n"
                "queue = deque([\n    i for i in range(num_courses)\n"
                "    if indegree[i] == 0\n])",
            ),
            _s(
                "The direct prerequisite, plus everything IT needed. Because "
                "the peel arrives in order, that inner set is already "
                "complete when it is read.",
                "while queue:\n    node = queue.popleft()\n"
                "    for nxt in graph[node]:\n        needs[nxt].add(node)\n"
                "        needs[nxt] |= needs[node]",
            ),
            _s(
                "Then carry on peeling as normal.",
                "        indegree[nxt] -= 1\n        if indegree[nxt] == 0:\n"
                "            queue.append(nxt)",
            ),
            _s(
                "Every query is now a set lookup rather than a search.",
                "return [\n    prereq in needs[course]\n"
                "    for prereq, course in queries\n]",
            ),
        ),
    ),
    2115: Worked(
        problem=2115,
        naive=(
            "Loop over the recipes repeatedly, making any whose ingredients "
            "are all available, until a full pass makes nothing new."
        ),
        why_not=(
            "Every pass rechecks every recipe including the ones already made, "
            "and a chain of recipes needs as many passes as it is long. The "
            "work multiplies for no reason."
        ),
        insight=(
            "An ingredient is a prerequisite and a recipe is a course. Count "
            "the ingredients each recipe is still missing, and let each item "
            "that becomes available decrement the recipes that want it."
        ),
        stages=(
            _s(
                "Edges run from ingredient to the recipe it feeds. The count "
                "is of ingredients still missing.",
                "graph = {}\nindegree = {recipe: 0 for recipe in recipes}\n"
                "for recipe, needed in zip(recipes, ingredients):\n"
                "    for item in needed:\n"
                "        graph.setdefault(item, []).append(recipe)\n"
                "        indegree[recipe] += 1",
            ),
            _s(
                "The supplies are what is available at the start — the "
                "equivalent of the courses with no prerequisites.",
                "queue = deque(supplies)\nmade = []",
            ),
            _s(
                "An available item satisfies one requirement of each recipe "
                "that wanted it.",
                "while queue:\n    item = queue.popleft()\n"
                "    for recipe in graph.get(item, []):\n"
                "        indegree[recipe] -= 1",
            ),
            _s(
                "At zero the recipe can be made — and once made it becomes an "
                "ingredient itself, so it goes back on the queue. That is what "
                "makes recipes-of-recipes work.",
                "        if indegree[recipe] == 0:\n"
                "            made.append(recipe)\n"
                "            queue.append(recipe)\nreturn made",
            ),
        ),
    ),
    1136: Worked(
        problem=1136,
        naive=(
            "Peel the courses one at a time in a valid order, and count how "
            "many it took."
        ),
        why_not=(
            "That counts COURSES, and the question asks for semesters. Courses "
            "with no dependency between them can be taken together, so the "
            "count comes out far too high."
        ),
        insight=(
            "Everything available at the same moment is one semester. So drain "
            "the queue in whole layers, the way a level-order tree walk does, "
            "and count the layers rather than the nodes."
        ),
        stages=(
            _s(
                "Courses are numbered from one here, so the ranges start there "
                "rather than at zero.",
                "graph = {i: [] for i in range(1, n + 1)}\n"
                "indegree = {i: 0 for i in range(1, n + 1)}\n"
                "for prereq, course in relations:\n"
                "    graph[prereq].append(course)\n    indegree[course] += 1",
            ),
            _s(
                "Two counters: courses done, to detect a cycle, and semesters, "
                "which is the answer.",
                "queue = deque([\n    i for i in range(1, n + 1)\n"
                "    if indegree[i] == 0\n])\nstudied = 0\nsemesters = 0",
            ),
            _s(
                "One pass of the outer loop is one semester. Taking len(queue) "
                "before draining is what fixes the boundary — courses unlocked "
                "during the semester belong to the next.",
                "while queue:\n    semesters += 1\n"
                "    for _ in range(len(queue)):\n        node = queue.popleft()\n"
                "        studied += 1",
            ),
            _s(
                "The peel itself is unchanged.",
                "        for nxt in graph[node]:\n            indegree[nxt] -= 1\n"
                "            if indegree[nxt] == 0:\n"
                "                queue.append(nxt)",
            ),
            _s(
                "Courses left unstudied were stuck in a cycle.",
                "return semesters if studied == n else -1",
            ),
        ),
    ),
    269: Worked(
        problem=269,
        naive=(
            "Compare every pair of words and record the order of the letters "
            "wherever they differ."
        ),
        why_not=(
            "Two things go wrong. Non-adjacent words prove nothing directly, "
            "and within a pair only the FIRST difference is evidence — "
            "everything after it is unconstrained by that comparison."
        ),
        insight=(
            "Each adjacent pair of words yields exactly one edge: the first "
            "position where they differ. Collect those edges and the alphabet "
            "is a topological order of the letters."
        ),
        stages=(
            _s(
                "Every letter that appears is a node, including ones no edge "
                "ever touches.",
                "graph = {ch: set() for word in words for ch in word}\n"
                "indegree = {ch: 0 for ch in graph}",
            ),
            _s(
                "The break is essential. The first difference is the only "
                "thing the pair proves; carrying on would invent orderings "
                "the input never claimed.",
                "for first, second in zip(words, words[1:]):\n"
                "    for a, b in zip(first, second):\n        if a != b:\n"
                "            if b not in graph[a]:\n"
                "                graph[a].add(b)\n                indegree[b] += 1\n"
                "            break",
            ),
            _s(
                "No difference found, and the first word is longer: a prefix "
                "listed after the word it prefixes is impossible in any "
                "alphabet. The for-else runs exactly when no break happened.",
                '    else:\n        if len(first) > len(second):\n'
                '            return ""',
            ),
            _s(
                "Then the standard peel over letters.",
                "queue = deque([ch for ch in indegree if indegree[ch] == 0])\n"
                "order = []\nwhile queue:\n    ch = queue.popleft()\n"
                "    order.append(ch)\n    for nxt in graph[ch]:\n"
                "        indegree[nxt] -= 1\n        if indegree[nxt] == 0:\n"
                "            queue.append(nxt)",
            ),
            _s(
                "A short order means the constraints contradict each other.",
                'return "".join(order) if len(order) == len(indegree) else ""',
            ),
        ),
    ),
}


_DP: dict[int, Worked] = {
    198: Worked(
        problem=198,
        naive=(
            "Try every valid combination of houses — take one or skip it, all "
            "the way down the street — and keep the richest."
        ),
        why_not=(
            "Two choices per house is two to the n combinations. It also "
            "recomputes the best haul from house five over and over, once for "
            "every way of arriving there."
        ),
        insight=(
            "Standing at a house there are only two states worth knowing: the "
            "best if you rob it, and the best if you do not. Each depends only "
            "on the same two from the house before."
        ),
        stages=(
            _s(
                "skip is the best total having not robbed the last house; take "
                "is the best having robbed it.",
                "skip, take = 0, 0",
            ),
            _s(
                "Skipping this house means the previous house was free to go "
                "either way, so the better of the two carries forward.",
                "for n in nums:\n    skip = max(skip, take)",
            ),
            _s(
                "Robbing this one requires the previous to have been skipped, "
                "so it builds on skip — the OLD skip, before the line above "
                "changed it.",
                "    take = skip + n",
            ),
            _s(
                "Which is why both are assigned at once. The right-hand side "
                "is evaluated first, so both read the previous house's values.",
                "for n in nums:\n    skip, take = max(skip, take), skip + n\n"
                "return max(skip, take)",
            ),
        ),
    ),
    322: Worked(
        problem=322,
        naive=(
            "Take the largest coin that fits, as many times as it fits, then "
            "the next largest, and so on."
        ),
        why_not=(
            "Greed fails on ordinary denominations. With coins of one, three "
            "and four making six, taking the four first forces two ones — "
            "three coins where two threes would have done."
        ),
        insight=(
            "The best way to make an amount is one coin plus the best way to "
            "make what remains. Build that up from zero and each smaller "
            "amount is already solved when a bigger one needs it."
        ),
        stages=(
            _s(
                "amount + 1 is larger than any real answer, since no amount "
                "needs more coins than its own value. It stands in for "
                "impossible without a special value to test for.",
                "best = [amount + 1] * (amount + 1)",
            ),
            _s(
                "Making nothing takes no coins, and every other answer is "
                "eventually built on this one.",
                "best[0] = 0",
            ),
            _s(
                "Work upward, so best[value - coin] is always already final by "
                "the time it is read.",
                "for value in range(1, amount + 1):\n    for coin in coins:\n"
                "        if coin <= value:",
            ),
            _s(
                "Each coin is a candidate for being the LAST one used, and the "
                "rest of the amount is a smaller problem already solved.",
                "            best[value] = min(\n"
                "                best[value], best[value - coin] + 1\n            )",
            ),
            _s(
                "Still at the sentinel means nothing ever reached it.",
                "return best[amount] if best[amount] <= amount else -1",
            ),
        ),
    ),
    300: Worked(
        problem=300,
        naive=(
            "For each position, find the longest increasing run ending there "
            "by checking every earlier position."
        ),
        why_not=(
            "That inner check makes it n squared, which is the standard answer "
            "and not the interesting one. The question can be done in n log n "
            "by keeping different information."
        ),
        insight=(
            "Track, for each achievable LENGTH, the smallest value that could "
            "end a subsequence of that length. That list is always sorted, so "
            "each new number's place in it can be binary searched."
        ),
        stages=(
            _s(
                "tails[i] is the smallest possible tail of an increasing "
                "subsequence of length i + 1. It is not itself a subsequence — "
                "only its LENGTH is meaningful.",
                "tails = []",
            ),
            _s(
                "Binary search for the first tail that is not smaller than n. "
                "tails is sorted because a longer subsequence cannot end lower "
                "than a shorter one.",
                "for n in nums:\n    low, high = 0, len(tails)\n"
                "    while low < high:\n        mid = (low + high) // 2\n"
                "        if tails[mid] < n:\n            low = mid + 1\n"
                "        else:\n            high = mid",
            ),
            _s(
                "Past the end means n extends the longest run so far, so the "
                "answer grows by one.",
                "    if low == len(tails):\n        tails.append(n)",
            ),
            _s(
                "Otherwise n is a better ending for a run of that length — "
                "same length, more room to grow later. Overwriting is not a "
                "loss because the length is what is being counted.",
                "    else:\n        tails[low] = n",
            ),
            _s(
                "The length of the list is the answer, even though its "
                "contents may not be a real subsequence.",
                "return len(tails)",
            ),
        ),
    ),
    746: Worked(
        problem=746,
        naive=(
            "From each step, recursively try both moves and take the cheaper "
            "of the two totals."
        ),
        why_not=(
            "The two branches overlap almost entirely — step five is reached "
            "from three and from four, and its whole subtree is explored "
            "twice. That doubling compounds to two to the n."
        ),
        insight=(
            "The cheapest way to STAND on a step is its own cost plus the "
            "cheaper of the two ways of arriving. Working forwards, only the "
            "last two answers are ever needed."
        ),
        stages=(
            _s(
                "one is the cheapest way to reach the previous position, two "
                "the one before that. Both start at zero because starting on "
                "either of the first two steps is free.",
                "one, two = 0, 0",
            ),
            _s(
                "The loop runs to len(cost) inclusive, because the destination "
                "is PAST the last step, not on it.",
                "for i in range(2, len(cost) + 1):",
            ),
            _s(
                "Arrive from one step back, paying that step's cost, or from "
                "two back paying that one's. Whichever is cheaper.",
                "    one = min(one + cost[i - 1], two + cost[i - 2])",
            ),
            _s(
                "The old one becomes the new two, which is why they are "
                "assigned together — the line above must not overwrite what "
                "the line below needs.",
                "for i in range(2, len(cost) + 1):\n    one, two = min(\n"
                "        one + cost[i - 1], two + cost[i - 2]\n    ), one\n"
                "return one",
            ),
        ),
    ),
    1143: Worked(
        problem=1143,
        naive=(
            "Generate every subsequence of the first string and check each one "
            "against the second."
        ),
        why_not=(
            "A string of length n has two to the n subsequences. At twenty "
            "characters that is a million; at forty it is a trillion, and the "
            "inputs are longer than that."
        ),
        insight=(
            "Compare one pair of positions at a time. If the characters match, "
            "the answer is one plus the answer for the rest of both; if not, "
            "it is the better of dropping one character from either side."
        ),
        stages=(
            _s(
                "A grid with one extra row and column, so the empty-string "
                "cases are real cells rather than bounds checks. They are "
                "zero, which is already correct.",
                "grid = [\n    [0] * (len(second) + 1)\n"
                "    for _ in range(len(first) + 1)\n]",
            ),
            _s(
                "Filling backwards means every cell a formula reads — below, "
                "right, or diagonal — is already done.",
                "for i in range(len(first) - 1, -1, -1):\n"
                "    for j in range(len(second) - 1, -1, -1):",
            ),
            _s(
                "A match is worth one, and both strings advance — which is the "
                "diagonal.",
                "        if first[i] == second[j]:\n"
                "            grid[i][j] = 1 + grid[i + 1][j + 1]",
            ),
            _s(
                "No match means one of them must give up a character, and "
                "there is no way to know which without trying both.",
                "        else:\n            grid[i][j] = max(\n"
                "                grid[i + 1][j], grid[i][j + 1]\n            )",
            ),
            _s(
                "The corner holds the answer for both strings entire.",
                "return grid[0][0]",
            ),
        ),
    ),
    139: Worked(
        problem=139,
        naive=(
            "Try each word that the string starts with, then recurse on the "
            "remainder, backtracking whenever it fails."
        ),
        why_not=(
            "The same remainder gets reached by many different splits, and "
            "each time it is solved again from scratch. A string that ALMOST "
            "works makes this take exponential time."
        ),
        insight=(
            "Ask a simpler question: which positions are reachable? A position "
            "is reachable if some word ends there and the position it starts "
            "at is itself reachable."
        ),
        stages=(
            _s(
                "One flag per boundary between characters, plus one for the "
                "end of the string.",
                "reachable = [False] * (len(text) + 1)",
            ),
            _s(
                "The start is reachable having used no words. Everything else "
                "is built from it.",
                "reachable[0] = True",
            ),
            _s(
                "For each boundary, try each word as the one that ENDS there. "
                "Its start must be a boundary already known reachable.",
                "for end in range(1, len(text) + 1):\n    for word in words:\n"
                "        start = end - len(word)\n"
                "        if start >= 0 and reachable[start]:",
            ),
            _s(
                "The text has to actually match. One way of reaching a "
                "position is as good as any, so break once found.",
                "            if text[start:end] == word:\n"
                "                reachable[end] = True\n                break",
            ),
            _s(
                "Reaching the end means the whole string was covered.",
                "return reachable[len(text)]",
            ),
        ),
    ),
    152: Worked(
        problem=152,
        naive=(
            "Carry a running product, and start again from the current number "
            "whenever the running product would get smaller."
        ),
        why_not=(
            "That is the trick that works for sums, and products have "
            "negatives. A deeply negative running product is one negative "
            "number away from being the largest, and abandoning it loses that."
        ),
        insight=(
            "Track the smallest running product as well as the largest. "
            "Multiplying by a negative swaps their roles, so today's worst is "
            "tomorrow's best."
        ),
        stages=(
            _s(
                "Both start at the first number. The run must be non-empty, so "
                "there is no zero to start from.",
                "best = nums[0]\nhigh, low = nums[0], nums[0]",
            ),
            _s(
                "Three candidates at each step: start fresh here, extend the "
                "best run, or extend the WORST one. That third option is the "
                "whole point.",
                "for n in nums[1:]:\n    options = (n, high * n, low * n)",
            ),
            _s(
                "Assigned together, because computing high first would leave "
                "low reading a value from this step instead of the last.",
                "    high, low = max(options), min(options)",
            ),
            _s(
                "Only the maximum is the answer; low is bookkeeping that "
                "never gets returned.",
                "    if high > best:\n        best = high\nreturn best",
            ),
        ),
    ),
}


MORE: dict[int, Worked] = {
    **_STACK,
    **_LINKED_LIST,
    **_BINARY_SEARCH,
    **_TREE_DFS,
    **_TREE_BFS,
    **_GRAPH,
    **_BACKTRACKING,
    **_HEAP,
    **_TOPOLOGICAL,
    **_DP,
}
