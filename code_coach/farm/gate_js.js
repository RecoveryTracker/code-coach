// Which parts of JavaScript a farm program uses - the reading half of
// code_coach/farm/gate.py, which decides what is still locked.
//
// Run as:  node gate_js.js [path to typescript]
//
// The program comes in on stdin. One line of JSON goes out:
//
//   [{"feature", "line", "col", "snippet", "what", "index"}, ...]
//
// feature is one of data.LANGUAGE_FEATURES, line is 1-based, what is how
// the message names the thing ("`+`", "A list"), and index marks a[i],
// which could be a list's index or a dictionary's key. Every use is
// listed, locked or not: which ones are locked is gate.py's business.
//
// null instead means "no answer": the program does not parse - its run
// will report that, in node's own words - or TypeScript is not installed.
//
// The parser is TypeScript's. It reads plain JavaScript too, and the web
// app already has it in web/node_modules, so there is nothing to install.
"use strict";
const fs = require("fs");
const path = require("path");

function load(where) {
  try {
    return require(where);
  } catch (error) {
    return null;
  }
}

const ts = load(process.argv[2] || path.join(__dirname, "..", "..", "web", "node_modules", "typescript"));

// A syntax error, or TypeScript written into a .js file (`let x: number`).
// The bare parser accepts the second - it is happy to read types - so ask a
// one-file program, which also runs the checks that keep .js files plain.
// node would refuse either, so neither is the gate's to judge.
function parses(sf) {
  const host = {
    getSourceFile: (name) => (name === sf.fileName ? sf : undefined),
    getDefaultLibFileName: () => "lib.d.ts",
    writeFile: () => {},
    getCurrentDirectory: () => "",
    getDirectories: () => [],
    fileExists: (name) => name === sf.fileName,
    readFile: () => undefined,
    getCanonicalFileName: (name) => name,
    useCaseSensitiveFileNames: () => true,
    getNewLine: () => "\n",
  };
  const program = ts.createProgram({
    rootNames: [sf.fileName],
    options: { allowJs: true, noLib: true, noResolve: true, types: [] },
    host,
  });
  return program.getSyntacticDiagnostics(sf).length === 0;
}

function uses(code) {
  const K = ts.SyntaxKind;
  const sf = ts.createSourceFile("farm.js", code, ts.ScriptTarget.Latest, true, ts.ScriptKind.JS);
  if (!parses(sf)) return null;
  const found = [];

  // `at` is where the use is, when that is not where its node starts: the
  // `+` of `a + b`, not the `a`.
  function add(feature, node, what, at, index) {
    const where = sf.getLineAndCharacterOfPosition(at === undefined ? node.getStart(sf) : at);
    found.push({
      feature,
      line: where.line + 1,
      col: where.character,
      snippet: node.getText(sf).split(/\r\n|\r|\n/)[0].trim(),
      what,
      index: Boolean(index),
    });
  }

  // -1 is a number, not the minus operator applied to one: free, as in the game.
  function isNumber(node) {
    while (node.kind === K.ParenthesizedExpression) node = node.expression;
    return node.kind === K.NumericLiteral || node.kind === K.BigIntLiteral;
  }

  function binary(node) {
    const op = node.operatorToken;
    const at = op.getStart(sf);
    if (op.kind === K.CommaToken) return;
    // Plain `=` only names a value. `+=` does sums as well.
    if (op.kind === K.EqualsToken) {
      add("variables", node, "A variable", at);
      return;
    }
    add("operators", node, "`" + op.getText(sf) + "`", at);
    if (op.kind >= K.FirstCompoundAssignment && op.kind <= K.LastCompoundAssignment) {
      add("variables", node, "A variable", at);
    }
  }

  function inspect(node) {
    switch (node.kind) {
      case K.WhileStatement:
        add("while", node, "`while`");
        break;
      case K.DoStatement:
        add("while", node, "`do ... while`");
        break;
      case K.IfStatement:
        add("if", node, "`if`");
        break;
      case K.ConditionalExpression:
        add("if", node, "`? :`", node.questionToken.getStart(sf));
        break;
      // switch is an if by another name, and the game has neither until Speed.
      case K.SwitchStatement:
        add("if", node, "`switch`");
        break;
      case K.ForStatement:
      case K.ForOfStatement:
      case K.ForInStatement:
        add("for", node, "`for`");
        break;
      case K.BinaryExpression:
        binary(node);
        break;
      case K.PrefixUnaryExpression:
        if ((node.operator === K.MinusToken || node.operator === K.PlusToken) && isNumber(node.operand)) break;
        add("operators", node, "`" + ts.tokenToString(node.operator) + "`");
        if (node.operator === K.PlusPlusToken || node.operator === K.MinusMinusToken) {
          add("variables", node, "A variable");
        }
        break;
      case K.PostfixUnaryExpression:
        add("operators", node, "`" + ts.tokenToString(node.operator) + "`");
        add("variables", node, "A variable");
        break;
      // let/const/var - except the one a for...of or for...in names, which
      // is the loop's own, as `i` is in Python's `for i in range(3)`.
      case K.VariableDeclarationList: {
        const loop = node.parent;
        const header = (loop.kind === K.ForOfStatement || loop.kind === K.ForInStatement) && loop.initializer === node;
        if (!header) add("variables", node, "A variable");
        break;
      }
      case K.FunctionDeclaration:
      case K.FunctionExpression:
      case K.ArrowFunction:
      case K.MethodDeclaration:
      case K.Constructor:
      case K.GetAccessor:
      case K.SetAccessor:
        add("functions", node, "A function of your own");
        break;
      case K.ClassDeclaration:
      case K.ClassExpression:
        add("functions", node, "A class of your own");
        break;
      case K.ArrayLiteralExpression:
        add("lists", node, "A list");
        break;
      case K.ElementAccessExpression:
        add("lists", node, "Indexing with `[ ]`", undefined, true);
        break;
      case K.ObjectLiteralExpression:
        add("dicts", node, "An object `{ }`");
        break;
      case K.NewExpression: {
        const name = node.expression.kind === K.Identifier ? node.expression.text : "";
        if (name === "Map" || name === "WeakMap") add("dicts", node, "A `Map`");
        else if (name === "Set" || name === "WeakSet") add("dicts", node, "A `Set`");
        else if (name === "Array") add("lists", node, "A list");
        break;
      }
      case K.CallExpression: {
        const callee = node.expression;
        if (callee.kind === K.ImportKeyword) add("import", node, "`import()`");
        else if (callee.kind === K.Identifier && callee.text === "require") add("import", node, "`require()`");
        else if (callee.kind === K.Identifier && callee.text === "Array") add("lists", node, "A list");
        break;
      }
      case K.ImportDeclaration:
      case K.ImportEqualsDeclaration:
        add("import", node, "`import`");
        break;
      case K.ExportDeclaration:
        if (node.moduleSpecifier) add("import", node, "`export ... from`");
        break;
    }
  }

  (function visit(node) {
    inspect(node);
    ts.forEachChild(node, visit);
  })(sf);
  return found;
}

let answer = null;
if (ts) {
  try {
    answer = uses(fs.readFileSync(0, "utf8"));
  } catch (error) {
    answer = null; // a program too deep to walk, say: no answer, not a crash
  }
}
process.stdout.write(JSON.stringify(answer) + "\n");
