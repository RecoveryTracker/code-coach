"""The fourth Canvas track: To-do, a web page instead of a canvas.

Dodge, Breakout and Farm draw. This one builds a page: a to-do list that
adds, crosses off, deletes, counts and remembers, made of the parts every
web page's JavaScript is made of - finding elements, changing their text
and classes, listening for events, making new elements, forms, event
delegation and localStorage.

Each step comes with its page (`html`, shown to you as index.html) and the
track's stylesheet (`css`, as style.css). The page grows as the steps do -
a box and a button at step 4, a form at step 7, delete buttons at step 8, a
counter at step 10 - and each step's starter is still the step before,
finished, so the code you carry forward meets the new page as it is.

A check runs in a real browser, never a homemade DOM (dom.py says why). It
gets `cc` - click, type, enter (Enter in a box: a form submits, as in a
browser), reload, logs and text - with `expect`, `$` and `$$`, and works the
page as a person would. It reads nothing of your code, only the page, so
any way of writing it that works, passes.
"""

from __future__ import annotations

from code_coach.canvas.content import Step

TRACK = "To-do"

CSS = """* {
  box-sizing: border-box;
}

body {
  margin: 0;
  font: 16px/1.45 system-ui, -apple-system, "Segoe UI", Roboto, sans-serif;
  background: #f4f1ea;
  color: #23262d;
}

.app {
  max-width: 440px;
  margin: 24px auto;
  padding: 20px 22px 18px;
  background: #fffdf8;
  border: 1px solid #e4dfd4;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(40, 30, 10, 0.08);
}

h1 {
  margin: 0 0 6px;
  font-size: 28px;
}

.tip {
  margin: 0 0 14px;
  color: #6d6a63;
  font-size: 14px;
}

/* Anything with the class hidden is not drawn at all. */
.hidden {
  display: none;
}

.new {
  display: flex;
  gap: 8px;
  margin: 0 0 12px;
}

.new input {
  flex: 1;
  min-width: 0;
  padding: 8px 10px;
  font: inherit;
  border: 1px solid #cfc8ba;
  border-radius: 8px;
  background: #fff;
}

.new button {
  padding: 8px 14px;
  font: inherit;
  font-weight: 600;
  color: #fff;
  background: #3f6fca;
  border: 0;
  border-radius: 8px;
  cursor: pointer;
}

#list {
  list-style: none;
  margin: 0;
  padding: 0;
}

#list li {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 9px 6px;
  border-bottom: 1px solid #ece7dc;
  cursor: pointer;
  user-select: none;
}

#list li:hover {
  background: #f8f4ea;
}

/* A to-do with the class done is struck through. */
#list li.done {
  color: #a19d94;
  text-decoration: line-through;
}

.text {
  flex: 1;
}

.delete {
  border: 0;
  background: none;
  color: #b4473b;
  font-size: 18px;
  line-height: 1;
  padding: 2px 6px;
  border-radius: 6px;
  cursor: pointer;
}

.delete:hover {
  background: #f6dcd8;
}

#left {
  margin: 12px 0 0;
  color: #6d6a63;
  font-size: 14px;
}"""

# ── The page, as it grows ──────────────────────────────────────────────

_PLAIN_ITEMS = """  <ul id="list">
    <li>Buy milk</li>
    <li>Walk the dog</li>
    <li>Learn the DOM</li>
  </ul>"""

_FULL_ITEMS = """  <ul id="list">
    <li><span class="text">Buy milk</span><button class="delete">×</button></li>
    <li><span class="text">Walk the dog</span><button class="delete">×</button></li>
    <li><span class="text">Learn the DOM</span><button class="delete">×</button></li>
  </ul>"""

_HEAD = """  <h1 id="title">My list</h1>
  <p id="tip" class="tip hidden">Click a to-do to cross it off.</p>"""

_BOX = """  <div class="new">
    <input id="new-todo" placeholder="What needs doing?" autocomplete="off">
    <button id="add">Add</button>
  </div>"""

_FORM = """  <form id="new" class="new">
    <input id="new-todo" placeholder="What needs doing?" autocomplete="off">
    <button id="add">Add</button>
  </form>"""

_HEAD_DELETE = """  <h1 id="title">My list</h1>
  <p id="tip" class="tip hidden">Click a to-do to cross it off, and × to delete it.</p>"""


def _main(*parts: str) -> str:
    return '<main class="app">\n' + "\n".join(parts) + "\n</main>"


HTML_LIST = _main(_HEAD, _PLAIN_ITEMS)
HTML_BOX = _main(_HEAD, _BOX, _PLAIN_ITEMS)
HTML_FORM = _main(_HEAD, _FORM, _PLAIN_ITEMS)
HTML_DELETE = _main(_HEAD_DELETE, _FORM, _FULL_ITEMS)
HTML_COUNT = _main(_HEAD_DELETE, _FORM, _FULL_ITEMS, '  <p id="left"></p>')

# ── The program, as it grows ───────────────────────────────────────────

_TOP = """// The page is index.html - open its tab to see what's on it.
const title = document.querySelector('#title');
"""

_S0 = _TOP + "console.log(title.textContent);\n"

_S1 = _TOP + "title.textContent = 'To-do';\n"

_TIP = """
const tip = document.querySelector('#tip');
tip.classList.remove('hidden');
"""

_S2 = _S1 + _TIP + """
const first = document.querySelector('#list li');
first.classList.add('done');
"""

_TOGGLE_EACH = """
const items = document.querySelectorAll('#list li');
items.forEach((item) => {
  item.addEventListener('click', () => {
    item.classList.toggle('done');
  });
});
"""

_S3 = _S1 + _TIP + _TOGGLE_EACH

_S4 = _S3 + """
const input = document.querySelector('#new-todo');
const addButton = document.querySelector('#add');

addButton.addEventListener('click', () => {
  console.log(input.value);
});
"""

_S5 = _S3 + """
const input = document.querySelector('#new-todo');
const addButton = document.querySelector('#add');
const list = document.querySelector('#list');

addButton.addEventListener('click', () => {
  const li = document.createElement('li');
  li.textContent = input.value;
  list.append(li);
  input.value = '';
});
"""

_S6 = _S3 + """
const input = document.querySelector('#new-todo');
const addButton = document.querySelector('#add');
const list = document.querySelector('#list');

addButton.addEventListener('click', () => {
  const text = input.value.trim();
  if (!text) return;

  const li = document.createElement('li');
  li.textContent = text;
  list.append(li);
  input.value = '';
});
"""

_S7 = _S3 + """
const form = document.querySelector('#new');
const input = document.querySelector('#new-todo');
const list = document.querySelector('#list');

form.addEventListener('submit', (event) => {
  event.preventDefault();
  const text = input.value.trim();
  if (!text) return;

  const li = document.createElement('li');
  li.textContent = text;
  list.append(li);
  input.value = '';
});
"""

_S8 = _S3 + """
document.querySelectorAll('.delete').forEach((button) => {
  button.addEventListener('click', () => {
    button.closest('li').remove();
  });
});

const form = document.querySelector('#new');
const input = document.querySelector('#new-todo');
const list = document.querySelector('#list');

form.addEventListener('submit', (event) => {
  event.preventDefault();
  const text = input.value.trim();
  if (!text) return;

  const li = document.createElement('li');
  const span = document.createElement('span');
  span.className = 'text';
  span.textContent = text;
  const del = document.createElement('button');
  del.className = 'delete';
  del.textContent = '×';
  del.addEventListener('click', () => li.remove());
  li.append(span, del);
  list.append(li);
  input.value = '';
});
"""

_S9 = _S1 + _TIP + """
const form = document.querySelector('#new');
const input = document.querySelector('#new-todo');
const list = document.querySelector('#list');

form.addEventListener('submit', (event) => {
  event.preventDefault();
  const text = input.value.trim();
  if (!text) return;

  const li = document.createElement('li');
  const span = document.createElement('span');
  span.className = 'text';
  span.textContent = text;
  const del = document.createElement('button');
  del.className = 'delete';
  del.textContent = '×';
  li.append(span, del);
  list.append(li);
  input.value = '';
});

list.addEventListener('click', (event) => {
  const li = event.target.closest('li');
  if (!li) return;
  if (event.target.closest('.delete')) {
    li.remove();
  } else {
    li.classList.toggle('done');
  }
});
"""

_S10 = _S1 + _TIP + """
const form = document.querySelector('#new');
const input = document.querySelector('#new-todo');
const list = document.querySelector('#list');
const left = document.querySelector('#left');

function updateCount() {
  const count = list.querySelectorAll('li:not(.done)').length;
  left.textContent = `${count} left`;
}

form.addEventListener('submit', (event) => {
  event.preventDefault();
  const text = input.value.trim();
  if (!text) return;

  const li = document.createElement('li');
  const span = document.createElement('span');
  span.className = 'text';
  span.textContent = text;
  const del = document.createElement('button');
  del.className = 'delete';
  del.textContent = '×';
  li.append(span, del);
  list.append(li);
  input.value = '';
  updateCount();
});

list.addEventListener('click', (event) => {
  const li = event.target.closest('li');
  if (!li) return;
  if (event.target.closest('.delete')) {
    li.remove();
  } else {
    li.classList.toggle('done');
  }
  updateCount();
});

updateCount();
"""

_S11 = _S1 + _TIP + """
const form = document.querySelector('#new');
const input = document.querySelector('#new-todo');
const list = document.querySelector('#list');
const left = document.querySelector('#left');

function addTodo(text, done) {
  const li = document.createElement('li');
  if (done) li.classList.add('done');
  const span = document.createElement('span');
  span.className = 'text';
  span.textContent = text;
  const del = document.createElement('button');
  del.className = 'delete';
  del.textContent = '×';
  li.append(span, del);
  list.append(li);
}

function updateCount() {
  const count = list.querySelectorAll('li:not(.done)').length;
  left.textContent = `${count} left`;
}

function save() {
  const todos = [...list.querySelectorAll('li')].map((li) => ({
    text: li.querySelector('.text').textContent,
    done: li.classList.contains('done'),
  }));
  localStorage.setItem('todos', JSON.stringify(todos));
}

function load() {
  const saved = localStorage.getItem('todos');
  if (saved === null) return;
  list.replaceChildren();
  for (const todo of JSON.parse(saved)) addTodo(todo.text, todo.done);
}

form.addEventListener('submit', (event) => {
  event.preventDefault();
  const text = input.value.trim();
  if (!text) return;

  addTodo(text, false);
  input.value = '';
  updateCount();
  save();
});

list.addEventListener('click', (event) => {
  const li = event.target.closest('li');
  if (!li) return;
  if (event.target.closest('.delete')) {
    li.remove();
  } else {
    li.classList.toggle('done');
  }
  updateCount();
  save();
});

load();
updateCount();
"""

# ── Checks ─────────────────────────────────────────────────────────────
# Each is the body of an async function run in the page once it has
# loaded. Helpers they share go in front.

_TEXTS = """const texts = () => $$('#list li').map((li) => li.textContent);
"""

_TODOS = """const todos = () => $$('#list li');
const textOf = (li) => {
  const span = li.querySelector('.text');
  return span ? span.textContent : li.textContent;
};
const find = (text) => todos().find((li) => textOf(li) === text);
const show = (list) => (list.length ? list.join(', ') : 'nothing');
"""

_CHECK1 = """const title = $('#title');
expect(title, `The heading #title is gone from the page.`);
const said = title.textContent;
expect(
  said === 'To-do',
  said === 'My list'
    ? `The heading still says "My list". Set its textContent to 'To-do'.`
    : `The heading says "${said}" - it should say exactly "To-do".`,
);
"""

_CHECK2 = """const items = $$('#list li');
expect(items.length === 3, `The list should still have its three to-dos - it has ${items.length}.`);
expect(
  !items.some((li) => li.classList.contains('.done')),
  `A class name has no dot: classList.add('done'). The dot belongs to a selector, '.done', not to the class.`,
);
const done = items.map((li) => li.classList.contains('done'));
expect(done[0], `"Buy milk" should have the class done.`);
expect(!done[1] && !done[2], `Only "Buy milk" should be crossed off.`);
const tip = $('#tip');
expect(tip && !tip.classList.contains('hidden'), `#tip still has the class hidden, so it stays hidden.`);
expect(
  tip.classList.contains('tip'),
  `#tip lost its class tip as well - take off only hidden: classList.remove('hidden').`,
);
"""

_CHECK3 = """const items = $$('#list li');
expect(items.length === 3, `The list should still have its three to-dos.`);
const done = () => items.map((li) => li.classList.contains('done'));
const start = done();
expect(
  !start.some(Boolean),
  start[0] && !start[1] && !start[2]
    ? `"Buy milk" starts crossed off - take out the line from step 2 that crossed it off.`
    : `Nothing should be crossed off before anything is clicked. Pass the listener a function - () => ... - so it runs on a click, not straight away.`,
);
cc.click(items[1], `"Walk the dog"`);
expect(done()[1], `Clicking "Walk the dog" should cross it off: toggle the class done on it.`);
expect(!done()[0] && !done()[2], `Clicking "Walk the dog" crossed off another to-do as well.`);
cc.click(items[1], `"Walk the dog" again`);
expect(!done()[1], `Clicking "Walk the dog" again should un-cross it: classList.toggle, not add.`);
cc.click(items[0], `"Buy milk"`);
cc.click(items[2], `"Learn the DOM"`);
expect(
  done()[0] && done()[2],
  `Every to-do should cross off when it's clicked, not only one - give each <li> a listener.`,
);
"""

_CHECK4 = """cc.type('#new-todo', 'Buy bread');
cc.click('#add');
let logs = cc.logs();
expect(logs.length > 0, `Clicking Add should console.log what's in the box - nothing was logged.`);
const last = logs[logs.length - 1];
expect(
  !last.startsWith('<input'),
  `That logged the <input> itself. Log what's in it: input.value.`,
);
expect(
  logs.some((line) => line.includes('Buy bread')),
  last === ''
    ? `An empty line was logged. Read input.value inside the click listener: read once at the top, it is what was in the box before anyone typed. (And an input's textContent is always empty.)`
    : `Typing "Buy bread" and clicking Add should log "Buy bread" - the log says "${last}".`,
);
cc.type('#new-todo', 'Call mum');
cc.click('#add');
logs = cc.logs();
expect(
  logs.some((line) => line.includes('Call mum')),
  `Typing "Call mum" and clicking Add again should log "Call mum".`,
);
"""

_CHECK5 = _TEXTS + """const before = texts().length;
cc.type('#new-todo', 'Buy bread');
cc.click('#add');
let now = texts();
expect(
  now.length === before + 1,
  now.length === before
    ? `Clicking Add should add an <li> to #list - it still has ${before}. Text appended to the list is not a to-do: make one with document.createElement('li').`
    : `Clicking Add once should add one <li> - the list went from ${before} to ${now.length}.`,
);
expect(
  now[now.length - 1] === 'Buy bread',
  `The new to-do should go at the end of the list and say "Buy bread" - the last one says "${now[now.length - 1]}".`,
);
expect($('#new-todo').value === '', `Empty the box after adding, ready for the next one: input.value = ''.`);
cc.type('#new-todo', '<b>Call mum</b>');
cc.click('#add');
now = texts();
expect(
  now.length === before + 2,
  `A second Add should add a second to-do. Make a new <li> each time, inside the listener: one made at the top just moves when it is appended again.`,
);
const last = $$('#list li').pop();
expect(
  !last.querySelector('b') && last.textContent === '<b>Call mum</b>',
  `Typed text has to stay text: "<b>Call mum</b>" turned into bold. Set textContent, not innerHTML.`,
);
"""

_CHECK6 = _TEXTS + """const before = texts().length;
cc.type('#new-todo', '   Buy bread  ');
cc.click('#add');
let now = texts();
expect(now.length === before + 1, `Typing "   Buy bread  " and clicking Add should still add a to-do.`);
expect(
  now[now.length - 1] === 'Buy bread',
  `Trim the text: "   Buy bread  " should go in as "Buy bread" - it went in as "${now[now.length - 1]}".`,
);
cc.type('#new-todo', '');
cc.click('#add');
expect(
  texts().length === before + 1,
  `Clicking Add with nothing typed added an empty to-do. Leave the listener early when there's no text: if (!text) return;`,
);
cc.type('#new-todo', '    ');
cc.click('#add');
expect(
  texts().length === before + 1,
  `A box of nothing but spaces added an empty to-do: trim first, then check what's left.`,
);
"""

_CHECK7 = _TEXTS + """const before = texts().length;
cc.type('#new-todo', 'Buy bread');
cc.enter('#new-todo');
let now = texts();
expect(
  now.length !== before + 2,
  `Pressing Enter added the to-do twice. Enter clicks the form's button, so a click listener on Add adds it as well as the submit listener: take the click listener out.`,
);
expect(
  now.length === before + 1 && now[now.length - 1] === 'Buy bread',
  `Pressing Enter in the box should add the to-do: listen for submit on the form.`,
);
cc.type('#new-todo', 'Call mum');
cc.click('#add');
now = texts();
expect(
  now.length !== before + 3,
  `Clicking Add added the to-do twice: the click listener and the submit listener both add it. Take the click listener out - a click on Add submits the form anyway.`,
);
expect(
  now.length === before + 2 && now[now.length - 1] === 'Call mum',
  `Clicking Add should add the to-do too - a button in a form submits it.`,
);
cc.type('#new-todo', '   ');
cc.enter('#new-todo');
expect(texts().length === before + 2, `A box of nothing but spaces still mustn't add anything.`);
"""

_CHECK8 = _TODOS + """cc.type('#new-todo', 'Buy bread');
cc.enter('#new-todo');
const li = todos().pop();
const span = li.querySelector('span.text');
expect(span, `A new to-do should hold its text in a <span class="text">, like the three in index.html.`);
expect(
  span.textContent === 'Buy bread',
  `The new to-do's <span class="text"> should say "Buy bread" - it says "${span.textContent}".`,
);
const del = li.querySelector('button.delete');
expect(del, `A new to-do should have a <button class="delete"> after its text, like the three in index.html.`);
cc.click(del, `× on "Buy bread"`);
expect(!li.isConnected, `Clicking × on "Buy bread" should remove that to-do.`);
expect(
  todos().map(textOf).join('|') === 'Buy milk|Walk the dog|Learn the DOM',
  `Clicking × on "Buy bread" should remove only "Buy bread" - the list now has: ${show(todos().map(textOf))}.`,
);
cc.click(find('Walk the dog').querySelector('.delete'), `× on "Walk the dog"`);
const left = todos().map(textOf);
expect(
  left.join('|') === 'Buy milk|Learn the DOM',
  left.length === 3
    ? `Clicking × on "Walk the dog" did nothing: the × buttons already in the page need listeners too.`
    : `Clicking × on "Walk the dog" should remove only "Walk the dog" - the list now has: ${show(left)}.`,
);
"""

_CHECK9 = _TODOS + """const isDone = (text) => find(text).classList.contains('done');
cc.type('#new-todo', 'Buy bread');
cc.enter('#new-todo');
cc.click(find('Buy bread').querySelector('.text'), `"Buy bread"`);
expect(
  !find('Buy bread').querySelector('.text').classList.contains('done'),
  `That crossed off the <span>, not the to-do. event.target is what was clicked - the text - so find its <li>: event.target.closest('li').`,
);
expect(
  isDone('Buy bread'),
  `Clicking a new to-do should cross it off. The listeners from step 3 went to the to-dos that existed then; one listener on #list reaches every to-do.`,
);
cc.click(find('Walk the dog').querySelector('.text'), `"Walk the dog"`);
expect(
  isDone('Walk the dog'),
  `Clicking "Walk the dog" should cross it off. If it stays as it was, two listeners are toggling it and the second undoes the first - take out the ones from step 3.`,
);
cc.click(find('Walk the dog'), `"Walk the dog" again`);
expect(
  !isDone('Walk the dog'),
  `Clicking "Walk the dog" again should un-cross it, wherever on the to-do the click lands. closest('li') finds the to-do from the text, and from the <li> itself.`,
);
const extra = document.createElement('li');
extra.innerHTML = '<span class="text">Made elsewhere</span><button class="delete">×</button>';
$('#list').append(extra);
cc.click(extra.querySelector('.text'), `a to-do put in #list some other way`);
expect(
  extra.classList.contains('done'),
  `A to-do put in #list some other way should cross off too: one listener on #list handles every to-do, whenever it was made.`,
);
cc.click(extra.querySelector('.delete'), `× on a to-do put in #list some other way`);
expect(
  !extra.isConnected,
  extra.querySelector('.delete')
    ? `× should remove a to-do put in #list some other way too.`
    : `× removed only itself. Remove its to-do: event.target.closest('li').remove().`,
);
cc.click(find('Buy milk').querySelector('.delete'), `× on "Buy milk"`);
expect(!find('Buy milk'), `Clicking × on "Buy milk" should remove it.`);
expect(todos().length === 3, `Clicking × should remove only its own to-do.`);
"""

_LEFT = """const left = () => {
  const p = $('#left');
  return p ? p.textContent.trim() : '';
};
"""

_CHECK10 = _TODOS + _LEFT + """expect(
  left() === '3 left',
  left() === ''
    ? `#left is empty. Fill it in when the page starts, as well as after each change.`
    : `#left should start at "3 left" - it says "${left()}".`,
);
cc.type('#new-todo', 'Buy bread');
cc.enter('#new-todo');
expect(left() === '4 left', `After adding a to-do, #left should say "4 left" - it says "${left()}".`);
cc.click(find('Walk the dog').querySelector('.text'), `"Walk the dog"`);
expect(
  left() === '3 left',
  `Crossing off "Walk the dog" should bring #left down to "3 left" - it says "${left()}". Count only the to-dos without the class done.`,
);
cc.click(find('Walk the dog').querySelector('.text'), `"Walk the dog" again`);
expect(left() === '4 left', `Un-crossing it should put #left back to "4 left" - it says "${left()}".`);
cc.click(find('Walk the dog').querySelector('.text'), `"Walk the dog" a third time`);
cc.click(find('Walk the dog').querySelector('.delete'), `× on "Walk the dog"`);
expect(
  left() === '3 left',
  `Deleting "Walk the dog", which was done, should leave #left at "3 left" - it says "${left()}".`,
);
cc.click(find('Buy milk').querySelector('.delete'), `× on "Buy milk"`);
expect(
  left() === '2 left',
  `Deleting "Buy milk", which wasn't done, should bring #left down to "2 left" - it says "${left()}". Count once the to-do is gone, not before.`,
);
"""

_CHECK11 = _TODOS + _LEFT + """const state = () => todos().map((li) => textOf(li) + (li.classList.contains('done') ? ' (done)' : ''));
const same = (a, b) => a.join('|') === b.join('|');
const explain = (before, after) => {
  if (same(before, after)) return;
  const was = `Before the reload: ${show(before)}. After it: ${show(after)}.`;
  expect(after.length > 0, `After a reload the list was empty - was it saved? ${was}`);
  expect(
    !same(after, ['Buy milk', 'Walk the dog', 'Learn the DOM'].concat(before)),
    `After a reload the page's own three to-dos were still there beside the saved ones. Empty the list - list.replaceChildren() - before building the saved ones. ${was}`,
  );
  const plain = (list) => list.map((t) => t.replace(' (done)', ''));
  expect(
    !same(plain(before), plain(after)),
    `After a reload every to-do came back, but not which ones were done. Save done with each to-do, after a toggle as well, and load it. ${was}`,
  );
  expect(false, `After a reload the list should be just as it was. ${was} Save after every add, toggle and delete.`);
};
expect(
  same(state(), ['Buy milk', 'Walk the dog', 'Learn the DOM']),
  `With nothing saved yet, the page should keep its three to-dos - it shows: ${show(state())}.`,
);
cc.type('#new-todo', 'Buy bread');
cc.enter('#new-todo');
cc.click(find('Walk the dog').querySelector('.text'), `"Walk the dog"`);
cc.click(find('Learn the DOM').querySelector('.delete'), `× on "Learn the DOM"`);
const before = state();
await cc.reload();
explain(before, state());
expect(
  left() === '2 left',
  `After a reload #left should count what was loaded: "2 left" - it says "${left()}". Update the count after loading.`,
);
cc.click(find('Buy bread').querySelector('.text'), `"Buy bread", after the reload`);
cc.click(find('Buy milk').querySelector('.delete'), `× on "Buy milk", after the reload`);
const again = state();
await cc.reload();
explain(again, state());
expect(left() === '0 left', `After the second reload #left should say "0 left" - it says "${left()}".`);
"""

TODO_STEPS: tuple[Step, ...] = (
    Step(
        id="todo-01-text",
        title="Change the page",
        teaches=(
            "A web page is a tree of elements, the DOM, and JavaScript can "
            "reach into it. This track builds a to-do list on a real page: "
            "index.html is the page, style.css its look, and app.js - the "
            "editor - runs at the end of it. document.querySelector takes a "
            "CSS selector - '#title' for the element with id=\"title\", 'li' "
            "for the first <li> - and hands back the first element that "
            "matches, or null when none does. An element's textContent is "
            "the text inside it: set it, and the page changes there and "
            "then, with no loop and no redraw - the browser does that."
        ),
        goal="Change the heading's text from \"My list\" to \"To-do\".",
        starter=_S0,
        solution=_S1,
        check=_CHECK1,
        hint="title.textContent = 'To-do';",
        track=TRACK,
        html=HTML_LIST,
        css=CSS,
    ),
    Step(
        id="todo-02-classes",
        title="Add and remove a class",
        teaches=(
            "Classes are how a stylesheet knows which look to give an "
            "element. style.css strikes through any to-do with the class "
            "done, and hides anything with the class hidden. classList is an "
            "element's set of classes: classList.add('done') puts one on, "
            "classList.remove('hidden') takes one off, classList.toggle "
            "flips it and classList.contains asks. A class name has no dot - "
            "'.done' with a dot is a selector, the way querySelector wants it."
        ),
        goal="Cross off \"Buy milk\" by adding the class done to it, and show the tip by removing the class hidden from #tip.",
        starter=_S1,
        solution=_S2,
        check=_CHECK2,
        hint="tip.classList.remove('hidden');  document.querySelector('#list li').classList.add('done');",
        track=TRACK,
        html=HTML_LIST,
        css=CSS,
    ),
    Step(
        id="todo-03-click",
        title="Respond to a click",
        teaches=(
            "A page mostly waits. addEventListener('click', fn) asks the "
            "browser to call fn each time that element is clicked - not now, "
            "later, once per click - so hand it a function, () => ..., not "
            "the result of calling one. querySelectorAll finds every match "
            "instead of the first, and its forEach visits each, so every "
            "<li> can get a listener of its own. Inside, "
            "classList.toggle('done') crosses a to-do off on one click and "
            "back on the next."
        ),
        goal=(
            "Make clicking a to-do toggle the class done on it, and take out "
            "the line that crossed off \"Buy milk\" - from now on, whoever "
            "uses the page decides what's done."
        ),
        starter=_S2,
        solution=_S3,
        check=_CHECK3,
        hint="items.forEach((item) => { item.addEventListener('click', () => item.classList.toggle('done')); });",
        track=TRACK,
        html=HTML_LIST,
        css=CSS,
    ),
    Step(
        id="todo-04-value",
        title="Read what was typed",
        teaches=(
            "The page has a box and a button now. What's typed in an "
            "<input> is its value - not its textContent, which is always "
            "empty for an input, since nothing is written between its tags. "
            "And value is read at the moment you ask: read it once at the top "
            "and you get what was in the box when the page loaded, which is "
            "nothing. Read it inside the click listener and you get what's "
            "there when Add is clicked. console.log prints under the page."
        ),
        goal="When Add is clicked, console.log what's in the #new-todo box.",
        starter=_S3,
        solution=_S4,
        check=_CHECK4,
        hint="addButton.addEventListener('click', () => { console.log(input.value); });",
        track=TRACK,
        html=HTML_BOX,
        css=CSS,
    ),
    Step(
        id="todo-05-append",
        title="Put a new element on the page",
        teaches=(
            "document.createElement('li') makes an element that isn't on "
            "the page yet - it floats, attached to nothing, until you put it "
            "somewhere. Give it its text, then list.append(li) adds it as "
            "the last thing in the list and the page shows it. Use "
            "textContent for anything a person typed, never innerHTML: "
            "innerHTML reads text as HTML, so typing <b>hi</b> makes bold "
            "text - or, from a stranger, runs their code. The new to-dos "
            "won't cross off yet; step 9 is about why."
        ),
        goal=(
            "When Add is clicked, add a new <li> holding the typed text to "
            "the end of #list, and empty the box."
        ),
        starter=_S4,
        solution=_S5,
        check=_CHECK5,
        hint="const li = document.createElement('li'); li.textContent = input.value; list.append(li);",
        track=TRACK,
        html=HTML_BOX,
        css=CSS,
    ),
    Step(
        id="todo-06-trim",
        title="Ignore empty to-dos",
        teaches=(
            "People type stray spaces, and click Add on an empty box. "
            "trim() hands back a string without the spaces at either end - "
            "'  milk  '.trim() is 'milk' - and an empty string is falsy, so "
            "if (!text) return; leaves the listener early when there's "
            "nothing to add. Trim first, then test: a box of spaces trims to "
            "'' and is turned away like an empty one."
        ),
        goal="Trim the typed text before adding it, and add nothing when what's left is empty.",
        starter=_S5,
        solution=_S6,
        check=_CHECK6,
        hint="const text = input.value.trim(); if (!text) return;",
        track=TRACK,
        html=HTML_BOX,
        css=CSS,
    ),
    Step(
        id="todo-07-form",
        title="Add with Enter: a form",
        teaches=(
            "The box and the button are inside a <form> now, and a form "
            "gives you Enter for free: Enter in the box submits it, and so "
            "does clicking its button. Submitting fires a submit event on "
            "the form - and then, by default, the browser sends the form off "
            "and loads the page again, losing everything added to it. Try "
            "Add in the preview and watch. event.preventDefault() in a "
            "submit listener cancels that, so listen for submit on the form "
            "instead of click on the button, and Enter and Add both come to "
            "you."
        ),
        goal=(
            "Move the adding into a submit listener on the #new form that "
            "calls event.preventDefault(), and take out the click listener, "
            "so Enter and Add each add one to-do and the page doesn't reload."
        ),
        starter=_S6,
        solution=_S7,
        check=_CHECK7,
        hint="form.addEventListener('submit', (event) => { event.preventDefault(); /* then add, as before */ });",
        track=TRACK,
        html=HTML_FORM,
        css=CSS,
    ),
    Step(
        id="todo-08-delete",
        title="Delete a to-do",
        teaches=(
            "The to-dos in the page now each hold a text <span> and a × "
            "button, and new ones should match. An element can hold others: "
            "make the span and the button, append both to the li - "
            "li.append(span, del) - and the li to the list. element.remove() "
            "takes an element off the page, children and all. In a × "
            "button's listener its to-do is still in reach: the li you just "
            "made, or, for the three already in the page, "
            "button.closest('li') - the nearest element above it that "
            "matches."
        ),
        goal=(
            "Make each new to-do an <li> holding a <span class=\"text\"> with "
            "the text and a <button class=\"delete\">, and make every × - on "
            "the three in the page and on new ones - remove its to-do."
        ),
        starter=_S7,
        solution=_S8,
        check=_CHECK8,
        hint="del.addEventListener('click', () => li.remove());  and for the three in the page: button.closest('li').remove()",
        track=TRACK,
        html=HTML_DELETE,
        css=CSS,
    ),
    Step(
        id="todo-09-delegation",
        title="One listener for the whole list",
        teaches=(
            "New to-dos still don't cross off: the listeners from step 3 "
            "went onto the <li>s that existed then, and new ones were never "
            "given one. Rather than a listener per to-do, put one on the "
            "list: a click on anything inside it bubbles up to #list, and "
            "event.target says what was actually clicked. "
            "event.target.closest('li') is the to-do it's in, whenever that "
            "was made, and event.target.closest('.delete') says whether it "
            "was the ×. That's event delegation, and it handles to-dos that "
            "don't exist yet."
        ),
        goal=(
            "Replace the per-to-do listeners - the toggling ones and the × "
            "ones - with one click listener on #list: a click on a .delete "
            "removes its to-do, and any other click on a to-do toggles done "
            "on it, for every to-do, old or new."
        ),
        starter=_S8,
        solution=_S9,
        check=_CHECK9,
        hint=(
            "const li = event.target.closest('li'); if (!li) return; "
            "if (event.target.closest('.delete')) li.remove(); else li.classList.toggle('done');"
        ),
        track=TRACK,
        html=HTML_DELETE,
        css=CSS,
    ),
    Step(
        id="todo-10-count",
        title="Count what's left",
        teaches=(
            "Nothing on a page changes unless code changes it. When a to-do "
            "is added, crossed off or deleted, the rest of the page doesn't "
            "know, so a counter has to be told. Put the counting in one "
            "function - the to-dos without the class done are "
            "list.querySelectorAll('li:not(.done)') - and write the number "
            "into #left; then call it once when the page starts and again "
            "after every change."
        ),
        goal=(
            "Make #left say how many to-dos aren't done, as \"3 left\", and "
            "keep it right after every add, toggle and delete."
        ),
        starter=_S9,
        solution=_S10,
        check=_CHECK10,
        hint="function updateCount() { left.textContent = `${list.querySelectorAll('li:not(.done)').length} left`; }",
        track=TRACK,
        html=HTML_COUNT,
        css=CSS,
    ),
    Step(
        id="todo-11-storage",
        title="Remember the list",
        teaches=(
            "Reload the page and the list resets: it lived in the page, and "
            "a reload throws the page away. localStorage keeps strings for a "
            "site across reloads and restarts - setItem('todos', text), and "
            "getItem('todos'), which is null when nothing was saved. Strings "
            "only, so make the to-dos an array of { text, done } and save "
            "JSON.stringify of it; load with JSON.parse. Save after every "
            "change; when the page starts, if something was saved, empty the "
            "list and build the saved ones. Here, Run is a reload: what you "
            "saved survives it."
        ),
        goal=(
            "Save the to-dos to localStorage after every add, toggle and "
            "delete, and load them when the page starts, so a reload brings "
            "back the same list - and with nothing saved yet, keep the three "
            "in the page."
        ),
        starter=_S10,
        solution=_S11,
        check=_CHECK11,
        hint=(
            "localStorage.setItem('todos', JSON.stringify(todos));  "
            "const saved = localStorage.getItem('todos'); if (saved !== null) { list.replaceChildren(); /* JSON.parse(saved)... */ }"
        ),
        track=TRACK,
        html=HTML_COUNT,
        css=CSS,
    ),
    Step(
        id="todo-12-yours",
        title="Make it yours",
        teaches=(
            "That's a working app - it adds, crosses off, deletes, counts "
            "and remembers - and every part of it is elements and events. "
            "Some things to try, using only what you've met: a \"Clear done\" "
            "button, made with createElement and put beside #left; filters - "
            "All, Active, Done - that hide to-dos with a class; double-click "
            "a to-do to edit it (the dblclick event, and an <input> swapped "
            "in for the span); Escape to empty the box (keydown and "
            "event.key)."
        ),
        goal="No check here - add whatever you like. Run is a reload, so what you save stays.",
        starter=_S11,
        solution=_S11,
        check="",
        track=TRACK,
        html=HTML_COUNT,
        css=CSS,
    ),
)
