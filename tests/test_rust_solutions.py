"""Every Rust solution is compiled and run against real cases.

The source executed is the exact string the student is asked to type — read
straight out of the bank, not a copy kept alongside it. A copy is how a
solution stops being the one that was verified.

One rustc invocation per pattern rather than per problem: the preamble, all
eight solutions, and a block of assertions go into a single program, so the
cost is a handful of compiles rather than a hundred.
"""

from __future__ import annotations

import shutil
import unittest

from code_coach.engine import run_code
from code_coach.leetcode.problems_rust import PATTERNS

PATTERNS_BY_ID = {p.id: p for p in PATTERNS}

HAS_RUSTC = shutil.which("rustc") is not None

# Assertions per pattern. Written against the real problem statements rather
# than against whatever the code happens to do, so a plausible-but-wrong
# solution fails here instead of passing quietly.
CHECKS = {
    "lc-hashmap": """
        assert_eq!(two_sum(vec![2, 7, 11, 15], 9), vec![0, 1]);
        assert_eq!(two_sum(vec![3, 2, 4], 6), vec![1, 2]);
        assert_eq!(two_sum(vec![1, 2], 99), Vec::<i32>::new());
        assert!(contains_duplicate(vec![1, 2, 3, 1]));
        assert!(!contains_duplicate(vec![1, 2, 3]));
        assert!(is_anagram("anagram".to_string(), "nagaram".to_string()));
        assert!(!is_anagram("rat".to_string(), "car".to_string()));
        assert!(!is_anagram("a".to_string(), "ab".to_string()));
        let mut groups = group_anagrams(
            vec!["eat", "tea", "tan", "ate", "nat", "bat"]
                .into_iter()
                .map(String::from)
                .collect(),
        );
        for g in groups.iter_mut() {
            g.sort();
        }
        groups.sort();
        assert_eq!(groups.len(), 3);
        assert!(groups.contains(&vec![
            "ate".to_string(),
            "eat".to_string(),
            "tea".to_string()
        ]));
        assert_eq!(
            four_sum_count(vec![1, 2], vec![-2, -1], vec![-1, 2], vec![0, 2]),
            2
        );
        assert_eq!(subarray_sum(vec![1, 1, 1], 2), 2);
        assert_eq!(subarray_sum(vec![1, 2, 3], 3), 2);
        assert_eq!(longest_consecutive(vec![100, 4, 200, 1, 3, 2]), 4);
        assert_eq!(longest_consecutive(vec![]), 0);
        let mut board = vec![vec!['.'; 9]; 9];
        assert!(is_valid_sudoku(board.clone()));
        board[0][0] = '5';
        board[0][1] = '5';
        assert!(!is_valid_sudoku(board.clone()));
        board[0][1] = '.';
        board[1][0] = '5';
        assert!(!is_valid_sudoku(board.clone()));
        board[1][0] = '.';
        board[1][1] = '5';
        assert!(!is_valid_sudoku(board));
    """,
    "lc-two-pointers": """
        assert!(is_palindrome("A man, a plan, a canal: Panama".to_string()));
        assert!(!is_palindrome("race a car".to_string()));
        assert!(is_palindrome("".to_string()));
        assert_eq!(two_sum_sorted(vec![2, 7, 11, 15], 9), vec![1, 2]);
        assert_eq!(max_area(vec![1, 8, 6, 2, 5, 4, 8, 3, 7]), 49);
        let mut got = three_sum(vec![-1, 0, 1, 2, -1, -4]);
        got.sort();
        assert_eq!(got, vec![vec![-1, -1, 2], vec![-1, 0, 1]]);
        assert_eq!(three_sum(vec![0, 0]), Vec::<Vec<i32>>::new());
        let mut nums = vec![1, 1, 2, 2, 3];
        assert_eq!(remove_duplicates(&mut nums), 3);
        assert_eq!(&nums[..3], &[1, 2, 3]);
        let mut nums = vec![0, 1, 0, 3, 12];
        move_zeroes(&mut nums);
        assert_eq!(nums, vec![1, 3, 12, 0, 0]);
        assert_eq!(trap(vec![0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1]), 6);
        assert_eq!(trap(vec![]), 0);
        assert_eq!(
            sorted_squares(vec![-4, -1, 0, 3, 10]),
            vec![0, 1, 9, 16, 100]
        );
    """,
    "lc-sliding-window": """
        assert_eq!(max_profit(vec![7, 1, 5, 3, 6, 4]), 5);
        assert_eq!(max_profit(vec![7, 6, 4, 3, 1]), 0);
        assert_eq!(length_of_longest_substring("abcabcbb".to_string()), 3);
        assert_eq!(length_of_longest_substring("bbbbb".to_string()), 1);
        assert_eq!(length_of_longest_substring("pwwkew".to_string()), 3);
        assert_eq!(length_of_longest_substring("".to_string()), 0);
        assert_eq!(min_sub_array_len(7, vec![2, 3, 1, 2, 4, 3]), 2);
        assert_eq!(min_sub_array_len(11, vec![1, 1, 1]), 0);
        assert_eq!(character_replacement("ABAB".to_string(), 2), 4);
        assert_eq!(character_replacement("AABABBA".to_string(), 1), 4);
        assert!(
            (find_max_average(vec![1, 12, -5, -6, 50, 3], 4) - 12.75).abs() < 1e-9
        );
        assert!(check_inclusion("ab".to_string(), "eidbaooo".to_string()));
        assert!(!check_inclusion("ab".to_string(), "eidboaoo".to_string()));
        assert!(!check_inclusion("abcd".to_string(), "ab".to_string()));
        assert_eq!(longest_ones(vec![1, 1, 1, 0, 0, 0, 1, 1, 1, 1, 0], 2), 6);
        assert_eq!(
            min_window("ADOBECODEBANC".to_string(), "ABC".to_string()),
            "BANC"
        );
        assert_eq!(min_window("a".to_string(), "aa".to_string()), "");
    """,
    "lc-stack": """
        assert!(is_valid("()[]{}".to_string()));
        assert!(!is_valid("([)]".to_string()));
        assert!(!is_valid("(".to_string()));
        assert!(!is_valid(")".to_string()));
        let mut ms = MinStack::new();
        ms.push(-2);
        ms.push(0);
        ms.push(-3);
        assert_eq!(ms.get_min(), -3);
        ms.pop();
        assert_eq!(ms.top(), 0);
        assert_eq!(ms.get_min(), -2);
        assert_eq!(eval_rpn(strs(&["2", "1", "+", "3", "*"])), 9);
        assert_eq!(eval_rpn(strs(&["4", "13", "5", "/", "+"])), 6);
        assert_eq!(eval_rpn(strs(&["7", "2", "-"])), 5);
        assert_eq!(
            daily_temperatures(vec![73, 74, 75, 71, 69, 72, 76, 73]),
            vec![1, 1, 4, 2, 1, 1, 0, 0]
        );
        assert_eq!(cal_points(strs(&["5", "2", "C", "D", "+"])), 30);
        assert_eq!(simplify_path("/home//foo/".to_string()), "/home/foo");
        assert_eq!(simplify_path("/../".to_string()), "/");
        assert_eq!(simplify_path("/a/./b/../../c/".to_string()), "/c");
        assert_eq!(largest_rectangle_area(vec![2, 1, 5, 6, 2, 3]), 10);
        assert_eq!(decode_string("3[a]2[bc]".to_string()), "aaabcbc");
        assert_eq!(decode_string("3[a2[c]]".to_string()), "accaccacc");
        assert_eq!(decode_string("10[a]".to_string()), "aaaaaaaaaa");
    """,
    "lc-linked-list": """
        assert_eq!(flatten(&reverse_list(build(&[1, 2, 3]))), vec![3, 2, 1]);
        assert_eq!(flatten(&reverse_list(build(&[]))), Vec::<i32>::new());
        assert_eq!(
            flatten(&merge_two_lists(build(&[1, 2, 4]), build(&[1, 3, 4]))),
            vec![1, 1, 2, 3, 4, 4]
        );
        assert_eq!(flatten(&merge_two_lists(build(&[]), build(&[0]))), vec![0]);
        assert!(has_cycle(vec![1, 2, 1], 0));
        assert!(!has_cycle(vec![1, 2, -1], 0));
        assert!(!has_cycle(vec![-1], 0));
        assert_eq!(
            flatten(&remove_nth_from_end(build(&[1, 2, 3, 4, 5]), 2)),
            vec![1, 2, 3, 5]
        );
        assert_eq!(
            flatten(&remove_nth_from_end(build(&[1]), 1)),
            Vec::<i32>::new()
        );
        assert_eq!(flatten(&remove_nth_from_end(build(&[1, 2]), 2)), vec![2]);
        assert_eq!(flatten(&middle_node(build(&[1, 2, 3, 4, 5]))), vec![3, 4, 5]);
        assert_eq!(
            flatten(&middle_node(build(&[1, 2, 3, 4, 5, 6]))),
            vec![4, 5, 6]
        );
        assert_eq!(
            flatten(&delete_duplicates(build(&[1, 1, 2, 3, 3]))),
            vec![1, 2, 3]
        );
        assert_eq!(flatten(&delete_duplicates(build(&[1, 1, 1]))), vec![1]);
        assert!(is_palindrome_list(build(&[1, 2, 2, 1])));
        assert!(is_palindrome_list(build(&[1, 2, 1])));
        assert!(!is_palindrome_list(build(&[1, 2])));
        assert!(is_palindrome_list(build(&[])));
        assert_eq!(
            flatten(&add_two_numbers(build(&[2, 4, 3]), build(&[5, 6, 4]))),
            vec![7, 0, 8]
        );
        assert_eq!(flatten(&add_two_numbers(build(&[5]), build(&[5]))), vec![0, 1]);
    """,
    "lc-binary-search": """
        assert_eq!(search(vec![-1, 0, 3, 5, 9, 12], 9), 4);
        assert_eq!(search(vec![-1, 0, 3, 5, 9, 12], 2), -1);
        assert_eq!(search(vec![], 1), -1);
        assert_eq!(search_insert(vec![1, 3, 5, 6], 5), 2);
        assert_eq!(search_insert(vec![1, 3, 5, 6], 7), 4);
        assert_eq!(search_insert(vec![1, 3, 5, 6], 0), 0);
        assert_eq!(find_min(vec![3, 4, 5, 1, 2]), 1);
        assert_eq!(find_min(vec![11, 13, 15, 17]), 11);
        assert_eq!(search_rotated(vec![4, 5, 6, 7, 0, 1, 2], 0), 4);
        assert_eq!(search_rotated(vec![4, 5, 6, 7, 0, 1, 2], 3), -1);
        assert_eq!(search_rotated(vec![1], 1), 0);
        assert_eq!(min_eating_speed(vec![3, 6, 7, 11], 8), 4);
        assert_eq!(min_eating_speed(vec![30, 11, 23, 4, 20], 5), 30);
        assert_eq!(first_bad_version(5, |v| v >= 4), 4);
        assert_eq!(first_bad_version(1, |v| v >= 1), 1);
        assert_eq!(search_range(vec![5, 7, 7, 8, 8, 10], 8), vec![3, 4]);
        assert_eq!(search_range(vec![5, 7, 7, 8, 8, 10], 6), vec![-1, -1]);
        let matrix = vec![vec![1, 3, 5, 7], vec![10, 11, 16, 20], vec![23, 30, 34, 60]];
        assert!(search_matrix(matrix.clone(), 3));
        assert!(!search_matrix(matrix, 13));
        assert!(!search_matrix(vec![], 1));
    """,
    "lc-tree-dfs": """
        assert_eq!(max_depth(build(&v(&[3, 9, 20]))), 2);
        assert_eq!(max_depth(None), 0);
        assert_eq!(vals(&invert_tree(build(&v(&[1, 2, 3])))), vec![1, 3, 2]);
        assert!(has_path_sum(build(&v(&[5, 4, 8, 11])), 20));
        assert!(!has_path_sum(build(&v(&[1, 2, 3])), 5));
        assert!(!has_path_sum(None, 0));
        assert_eq!(diameter_of_binary_tree(build(&v(&[1, 2, 3, 4, 5]))), 3);
        assert_eq!(diameter_of_binary_tree(build(&v(&[1, 2]))), 1);
        assert!(is_valid_bst(build(&v(&[2, 1, 3]))));
        assert!(!is_valid_bst(build(&v(&[5, 1, 4, 3, 6]))));
        assert!(!is_valid_bst(build(&[
            Some(5), Some(4), Some(6), None, None, Some(3), Some(7)
        ])));
        assert!(is_valid_bst(build(&[Some(i32::MIN)])));
        assert!(is_same_tree(build(&v(&[1, 2, 3])), build(&v(&[1, 2, 3]))));
        assert!(!is_same_tree(
            build(&v(&[1, 2])),
            build(&[Some(1), None, Some(2)])
        ));
        assert!(is_symmetric(build(&[
            Some(1), Some(2), Some(2), Some(3), Some(4), Some(4), Some(3)
        ])));
        assert!(!is_symmetric(build(&[
            Some(1), Some(2), Some(2), None, Some(3), None, Some(3)
        ])));
        let tree = build(&v(&[3, 5, 1, 6, 2, 0, 8]));
        let found = lowest_common_ancestor(
            tree.clone(), build(&[Some(5)]), build(&[Some(1)])
        );
        assert_eq!(found.unwrap().borrow().val, 3);
        let found = lowest_common_ancestor(
            tree, build(&[Some(5)]), build(&[Some(2)])
        );
        assert_eq!(found.unwrap().borrow().val, 5);
    """,
    "lc-tree-bfs": """
        let tree = build(&[Some(3), Some(9), Some(20), None, None, Some(15), Some(7)]);
        assert_eq!(
            level_order(tree.clone()),
            vec![vec![3], vec![9, 20], vec![15, 7]]
        );
        assert_eq!(level_order(None), Vec::<Vec<i32>>::new());
        assert_eq!(
            right_side_view(build(&[Some(1), Some(2), Some(3), None, Some(5)])),
            vec![1, 3, 5]
        );
        assert_eq!(
            zigzag_level_order(tree.clone()),
            vec![vec![3], vec![20, 9], vec![15, 7]]
        );
        assert_eq!(min_depth(tree.clone()), 2);
        assert_eq!(min_depth(build(&[Some(2), None, Some(3)])), 2);
        assert_eq!(min_depth(None), 0);
        let avgs = average_of_levels(tree);
        assert!((avgs[0] - 3.0).abs() < 1e-9);
        assert!((avgs[1] - 14.5).abs() < 1e-9);
        assert_eq!(
            largest_values(build(&[
                Some(1), Some(3), Some(2), Some(5), Some(3), None, Some(9)
            ])),
            vec![1, 3, 9]
        );
        assert_eq!(
            largest_values(build(&[Some(-1), Some(-2), Some(-3)])),
            vec![-1, -2]
        );
        assert_eq!(
            max_level_sum(build(&[Some(1), Some(7), Some(0), Some(7), Some(-8)])),
            2
        );
        assert_eq!(max_level_sum(build(&v(&[1]))), 1);
        assert_eq!(
            width_of_binary_tree(build(&[
                Some(1), Some(3), Some(2), Some(5), Some(3), None, Some(9)
            ])),
            4
        );
        assert_eq!(width_of_binary_tree(build(&v(&[1, 3, 2, 5]))), 2);
        assert_eq!(width_of_binary_tree(None), 0);
    """,
    "lc-graph": """
        assert_eq!(
            flood_fill(vec![vec![1, 1, 1], vec![1, 1, 0], vec![1, 0, 1]], 1, 1, 2),
            vec![vec![2, 2, 2], vec![2, 2, 0], vec![2, 0, 1]]
        );
        assert_eq!(
            flood_fill(vec![vec![0, 0], vec![0, 0]], 0, 0, 0),
            vec![vec![0, 0], vec![0, 0]]
        );
        assert_eq!(num_islands(grid_of(&["11000", "11000", "00100", "00011"])), 3);
        assert_eq!(num_islands(grid_of(&["000"])), 0);
        assert_eq!(
            oranges_rotting(vec![vec![2, 1, 1], vec![1, 1, 0], vec![0, 1, 1]]),
            4
        );
        assert_eq!(
            oranges_rotting(vec![vec![2, 1, 1], vec![0, 1, 1], vec![1, 0, 1]]),
            -1
        );
        assert_eq!(oranges_rotting(vec![vec![0, 2]]), 0);
        let a = Rc::new(RefCell::new(Node::new(1)));
        let b = Rc::new(RefCell::new(Node::new(2)));
        a.borrow_mut().neighbors.push(b.clone());
        b.borrow_mut().neighbors.push(a.clone());
        let cloned = clone_graph(Some(a.clone())).unwrap();
        assert_eq!(cloned.borrow().val, 1);
        assert_eq!(cloned.borrow().neighbors.len(), 1);
        assert_eq!(cloned.borrow().neighbors[0].borrow().val, 2);
        assert!(!Rc::ptr_eq(&cloned, &a));
        assert!(Rc::ptr_eq(
            &cloned.borrow().neighbors[0].borrow().neighbors[0],
            &cloned
        ));
        assert!(clone_graph(None).is_none());
        assert_eq!(
            max_area_of_island(vec![vec![1, 1, 0], vec![1, 0, 0], vec![0, 0, 1]]),
            3
        );
        assert_eq!(max_area_of_island(vec![vec![0, 0]]), 0);
        assert_eq!(
            find_circle_num(vec![vec![1, 1, 0], vec![1, 1, 0], vec![0, 0, 1]]),
            2
        );
        assert_eq!(
            find_circle_num(vec![vec![1, 0, 0], vec![0, 1, 0], vec![0, 0, 1]]),
            3
        );
        assert_eq!(
            update_matrix(vec![vec![0, 0, 0], vec![0, 1, 0], vec![1, 1, 1]]),
            vec![vec![0, 0, 0], vec![0, 1, 0], vec![1, 2, 1]]
        );
        let flows = pacific_atlantic(vec![
            vec![1, 2, 2, 3, 5],
            vec![3, 2, 3, 4, 4],
            vec![2, 4, 5, 3, 1],
            vec![6, 7, 1, 4, 5],
            vec![5, 1, 1, 2, 4],
        ]);
        assert!(flows.contains(&vec![0, 4]));
        assert!(flows.contains(&vec![3, 0]));
        assert_eq!(flows.len(), 7);
    """,
    "lc-backtracking": """
        let mut got = subsets(vec![1, 2, 3]);
        got.sort();
        assert_eq!(got.len(), 8);
        assert!(got.contains(&vec![]));
        assert!(got.contains(&vec![1, 2, 3]));
        let mut got = subsets_with_dup(vec![1, 2, 2]);
        got.sort();
        got.dedup();
        assert_eq!(got.len(), 6);
        let got = permute(vec![1, 2, 3]);
        assert_eq!(got.len(), 6);
        assert!(got.contains(&vec![3, 2, 1]));
        let mut got = combination_sum(vec![2, 3, 6, 7], 7);
        got.sort();
        assert_eq!(got, vec![vec![2, 2, 3], vec![7]]);
        let board = grid_of(&["ABCE", "SFCS", "ADEE"]);
        assert!(exist(board.clone(), "ABCCED".to_string()));
        assert!(!exist(board, "ABCB".to_string()));
        let got = combine(4, 2);
        assert_eq!(got.len(), 6);
        assert!(got.contains(&vec![1, 2]));
        assert!(got.contains(&vec![3, 4]));
        let got = letter_combinations("23".to_string());
        assert_eq!(got.len(), 9);
        assert!(got.contains(&"ad".to_string()));
        assert!(letter_combinations("".to_string()).is_empty());
        let got = partition("aab".to_string());
        assert_eq!(got.len(), 2);
        assert!(got.contains(&vec!["aa".to_string(), "b".to_string()]));
    """,
    "lc-heap": """
        assert_eq!(find_kth_largest(vec![3, 2, 1, 5, 6, 4], 2), 5);
        assert_eq!(find_kth_largest(vec![1], 1), 1);
        let mut got = top_k_frequent(vec![1, 1, 1, 2, 2, 3], 2);
        got.sort();
        assert_eq!(got, vec![1, 2]);
        let mut got = k_closest(vec![vec![1, 3], vec![-2, 2]], 1);
        got.sort();
        assert_eq!(got, vec![vec![-2, 2]]);
        assert_eq!(last_stone_weight(vec![2, 7, 4, 1, 8, 1]), 1);
        assert_eq!(last_stone_weight(vec![1]), 1);
        assert_eq!(last_stone_weight(vec![2, 2]), 0);
        assert_eq!(
            top_k_frequent_words(
                strs(&["i", "love", "leetcode", "i", "love", "coding"]), 2
            ),
            strs(&["i", "love"])
        );
        assert_eq!(
            top_k_frequent_words(strs(&["b", "a", "c", "a", "b"]), 2),
            strs(&["a", "b"])
        );
        let sorted = frequency_sort("tree".to_string());
        assert!(sorted == "eert" || sorted == "eetr");
        assert_eq!(frequency_sort("cccaaa".to_string()).len(), 6);
        assert_eq!(
            kth_smallest(vec![vec![1, 5, 9], vec![10, 11, 13], vec![12, 13, 15]], 8),
            13
        );
        assert_eq!(kth_smallest(vec![vec![-5]], 1), -5);
        let out = reorganize_string("aab".to_string());
        assert_eq!(out.len(), 3);
        assert!(out.as_bytes().windows(2).all(|w| w[0] != w[1]));
        assert_eq!(reorganize_string("aaab".to_string()), "");
    """,
    "lc-topological": """
        assert!(can_finish(2, vec![vec![1, 0]]));
        assert!(!can_finish(2, vec![vec![1, 0], vec![0, 1]]));
        assert_eq!(find_order(2, vec![vec![1, 0]]), vec![0, 1]);
        assert_eq!(find_order(2, vec![vec![1, 0], vec![0, 1]]), Vec::<i32>::new());
        let mut centres = find_min_height_trees(
            4, vec![vec![1, 0], vec![1, 2], vec![1, 3]]
        );
        centres.sort();
        assert_eq!(centres, vec![1]);
        assert_eq!(find_min_height_trees(1, vec![]), vec![0]);
        assert_eq!(
            eventual_safe_nodes(vec![
                vec![1, 2], vec![2, 3], vec![5], vec![0], vec![5], vec![], vec![]
            ]),
            vec![2, 4, 5, 6]
        );
        assert_eq!(
            check_if_prerequisite(
                3, vec![vec![0, 1], vec![1, 2]], vec![vec![0, 2], vec![2, 0]]
            ),
            vec![true, false]
        );
        assert_eq!(
            find_all_recipes(
                strs(&["bread"]),
                vec![strs(&["yeast", "flour"])],
                strs(&["yeast", "flour", "corn"])
            ),
            strs(&["bread"])
        );
        assert_eq!(
            find_all_recipes(
                strs(&["bread", "sandwich"]),
                vec![strs(&["yeast", "flour"]), strs(&["bread", "meat"])],
                strs(&["yeast", "flour", "meat"])
            ),
            strs(&["bread", "sandwich"])
        );
        assert_eq!(minimum_semesters(3, vec![vec![1, 3], vec![2, 3]]), 2);
        assert_eq!(
            minimum_semesters(3, vec![vec![1, 2], vec![2, 3], vec![3, 1]]),
            -1
        );
        assert_eq!(
            alien_order(strs(&["wrt", "wrf", "er", "ett", "rftt"])).len(),
            5
        );
        assert_eq!(alien_order(strs(&["abc", "ab"])), "");
    """,
    "lc-dp": """
        assert_eq!(climb_stairs(2), 2);
        assert_eq!(climb_stairs(3), 3);
        assert_eq!(climb_stairs(1), 1);
        assert_eq!(rob(vec![1, 2, 3, 1]), 4);
        assert_eq!(rob(vec![2, 7, 9, 3, 1]), 12);
        assert_eq!(coin_change(vec![1, 3, 4], 6), 2);
        assert_eq!(coin_change(vec![2], 3), -1);
        assert_eq!(coin_change(vec![1], 0), 0);
        assert_eq!(length_of_lis(vec![10, 9, 2, 5, 3, 7, 101, 18]), 4);
        assert_eq!(length_of_lis(vec![7, 7, 7]), 1);
        assert_eq!(min_cost_climbing_stairs(vec![10, 15, 20]), 15);
        assert_eq!(
            min_cost_climbing_stairs(vec![1, 100, 1, 1, 1, 100, 1, 1, 100, 1]),
            6
        );
        assert_eq!(
            longest_common_subsequence("abcde".to_string(), "ace".to_string()),
            3
        );
        assert_eq!(
            longest_common_subsequence("abc".to_string(), "def".to_string()),
            0
        );
        assert!(word_break("leetcode".to_string(), strs(&["leet", "code"])));
        assert!(!word_break(
            "catsandog".to_string(),
            strs(&["cats", "dog", "sand", "and", "cat"])
        ));
        assert_eq!(max_product(vec![2, 3, -2, 4]), 6);
        assert_eq!(max_product(vec![-2, 0, -1]), 0);
        assert_eq!(max_product(vec![-2, 3, -4]), 24);
    """,
}

# Helpers the checks use, rather than repeating the plumbing inline. Only what
# a pattern actually uses gets injected: an unused function is a warning, and
# warnings fail this test.
STRS = """
fn strs(v: &[&str]) -> Vec<String> {
    v.iter().map(|x| x.to_string()).collect()
}
"""

GRID = """
fn grid_of(rows: &[&str]) -> Vec<Vec<char>> {
    rows.iter().map(|r| r.chars().collect()).collect()
}
"""

LIST_HELPERS = """
fn build(values: &[i32]) -> Option<Box<ListNode>> {
    let mut head = None;
    for &v in values.iter().rev() {
        let mut node = Box::new(ListNode::new(v));
        node.next = head;
        head = Some(node);
    }
    head
}

fn flatten(head: &Option<Box<ListNode>>) -> Vec<i32> {
    let mut out = Vec::new();
    let mut cursor = head;
    while let Some(node) = cursor {
        out.push(node.val);
        cursor = &node.next;
    }
    out
}
"""

# Built from a level-order list with None for a gap, the way LeetCode prints
# its trees, so a check reads the same as the problem statement.
TREE_HELPERS = """
fn build(values: &[Option<i32>]) -> Tree {
    if values.is_empty() || values[0].is_none() {
        return None;
    }
    let root = Rc::new(RefCell::new(TreeNode::new(values[0].unwrap())));
    let mut queue: VecDeque<Rc<RefCell<TreeNode>>> = VecDeque::new();
    queue.push_back(root.clone());
    let mut i = 1;
    while i < values.len() {
        let parent = queue.pop_front().unwrap();
        if i < values.len() {
            if let Some(v) = values[i] {
                let child = Rc::new(RefCell::new(TreeNode::new(v)));
                parent.borrow_mut().left = Some(child.clone());
                queue.push_back(child);
            }
            i += 1;
        }
        if i < values.len() {
            if let Some(v) = values[i] {
                let child = Rc::new(RefCell::new(TreeNode::new(v)));
                parent.borrow_mut().right = Some(child.clone());
                queue.push_back(child);
            }
            i += 1;
        }
    }
    Some(root)
}

fn v(values: &[i32]) -> Vec<Option<i32>> {
    values.iter().map(|&x| Some(x)).collect()
}
"""

# Tree DFS has no level walk of its own, so it needs one to check against.
TREE_VALS = """
fn vals(root: &Tree) -> Vec<i32> {
    let mut out = Vec::new();
    let mut queue: VecDeque<Rc<RefCell<TreeNode>>> = VecDeque::new();
    if let Some(node) = root {
        queue.push_back(node.clone());
    }
    while let Some(node) = queue.pop_front() {
        out.push(node.borrow().val);
        let left = node.borrow().left.clone();
        let right = node.borrow().right.clone();
        if let Some(left) = left {
            queue.push_back(left);
        }
        if let Some(right) = right {
            queue.push_back(right);
        }
    }
    out
}
"""

HELPERS_FOR = {
    "lc-stack": [STRS],
    "lc-linked-list": [LIST_HELPERS],
    "lc-tree-dfs": ["use std::collections::VecDeque;", TREE_HELPERS, TREE_VALS],
    "lc-tree-bfs": [TREE_HELPERS],
    "lc-graph": [GRID],
    "lc-backtracking": [GRID],
    "lc-heap": [STRS],
    "lc-topological": [STRS],
    "lc-dp": [STRS],
}


@unittest.skipUnless(HAS_RUSTC, "needs rustc on PATH")
class RustSolutionTests(unittest.TestCase):
    def _run_pattern(self, pattern_id: str) -> None:
        pattern = PATTERNS_BY_ID[pattern_id]
        parts = list(pattern.preamble)
        parts.extend(HELPERS_FOR.get(pattern_id, []))
        parts.extend(p.code for p in pattern.problems)
        parts.append("fn main() {\n" + CHECKS[pattern_id] + "\n}")
        out, err, code = run_code("\n\n".join(parts), language="rust")
        self.assertEqual(code, 0, (err or out)[:2000])
        # Warnings mean the student is being taught to type something rustc
        # already objects to, which is its own kind of wrong.
        self.assertNotIn("warning:", err, err[:2000])

    def test_every_pattern_compiles_and_holds(self) -> None:
        for pattern_id in CHECKS:
            with self.subTest(pattern=pattern_id):
                self._run_pattern(pattern_id)


class CoverageTests(unittest.TestCase):
    """These run with or without a toolchain."""

    def test_every_pattern_present_has_checks(self) -> None:
        """A pattern with no assertions would compile and prove nothing."""
        self.assertEqual(sorted(CHECKS), sorted(p.id for p in PATTERNS))

    def test_every_pattern_mirrors_the_python_bank(self) -> None:
        """Same problems, same order — that is what lets you switch language
        without losing your place."""
        from code_coach.leetcode.problems import PATTERNS_BY_ID as PY

        for pattern in PATTERNS:
            with self.subTest(pattern=pattern.id):
                theirs = [p.number for p in PY[pattern.id].problems]
                mine = [p.number for p in pattern.problems]
                self.assertEqual(mine, theirs)
                titles = [p.title for p in PY[pattern.id].problems]
                self.assertEqual([p.title for p in pattern.problems], titles)

    def test_the_bank_is_registered_now_that_it_is_whole(self) -> None:
        """It was deliberately unregistered while partial, because a half bank
        makes has_own_bank say yes and the missing patterns serve Python."""
        from code_coach.leetcode.bank import has_own_bank, patterns_for_language

        self.assertTrue(has_own_bank("rust"))
        self.assertEqual(len(patterns_for_language("rust")), len(PATTERNS))

    def test_it_covers_every_problem(self) -> None:
        from code_coach.leetcode.problems import all_problems

        theirs = sorted(p.number for p in all_problems())
        mine = sorted(p.number for pat in PATTERNS for p in pat.problems)
        self.assertEqual(mine, theirs)


if __name__ == "__main__":
    unittest.main()
