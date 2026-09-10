"""Ruby on Rails: lore to read and lines to type.

Rails is a framework rather than a language, so it gets no workbook pages.
Every workbook exercise is a single file that runs on its own and prints
something; Rails needs a generated project, a Gemfile, a database and a
booted server before one line does anything at all. Pretending otherwise
would mean shipping exercises that cannot execute, which is the thing the
dark languages exist to avoid.

Typing is a different matter and Rails suits it well: the framework is
mostly a vocabulary of declarations, and the punctuation of a Rails file —
symbols, hash arguments without braces, blocks, the arrow lambda — is
exactly what fingers need to learn.

Every code line below is checked with `ruby -c` rather than written from
memory and hoped over. That proves the Ruby is well formed; it does not
prove Rails would accept it, because that needs a project and a database,
and saying so is more useful than implying a stronger check than was run.
"""

from __future__ import annotations

from code_coach.typing.snippets import Passage, _s

# ── Lore ─────────────────────────────────────────────────────

RAILS_LORE: tuple[Passage, ...] = (
    _s("Rails was extracted from Basecamp by David Heinemeier Hansson in "
       "2004, which is why it feels like a real application rather than a "
       "toolkit.", "Rails design"),
    _s("Convention over configuration is the whole idea: a class named "
       "Order maps to a table named orders, and nothing has to say so.",
       "Rails design"),
    _s("Don't repeat yourself came into wide use through Rails, though the "
       "phrase is older than the framework.", "Rails conventions"),
    _s("Model, view, controller: the model knows the data, the view knows "
       "the markup, and the controller is meant to be thin.",
       "Rails design"),
    _s("ActiveRecord is the pattern and the library: an object is a row, "
       "and the class is the table.", "Rails design"),
    _s("A migration is a change to the schema written in Ruby and kept in "
       "version control, so the database has a history.",
       "Rails conventions"),
    _s("schema.rb is generated from the migrations and is the file to "
       "trust about what the database actually looks like.",
       "Rails conventions"),
    _s("The N plus one query is the classic Rails performance bug: one "
       "query for the list and one more for each row.",
       "Rails performance"),
    _s("includes is the usual fix, loading the association up front so the "
       "loop does not go back to the database.", "Rails performance"),
    _s("Strong parameters exist because mass assignment let people set any "
       "column they liked by adding a form field.", "Rails design"),
    _s("A scope is a named query you can chain, and it returns a relation "
       "rather than an array, so nothing runs until you ask.",
       "Rails design"),
    _s("Relations are lazy. The query fires when you iterate, count or "
       "inspect it, which is why a scope costs nothing to define.",
       "Rails internals"),
    _s("before_action runs a method ahead of the controller action, and is "
       "where authentication usually lives.", "Rails conventions"),
    _s("Rails routes read as resources, and resources gives you seven "
       "actions unless you ask for fewer.", "Rails conventions"),
    _s("The asset pipeline has been rewritten more than once; importmaps "
       "and Propshaft are the modern answer to bundling.",
       "Rails design"),
    _s("Hotwire sends HTML over the wire instead of JSON, which is Rails "
       "arguing that most applications never needed a front-end "
       "framework.", "Rails design"),
    _s("Turbo replaces the page fragment the server sent back, so a form "
       "can update part of a page without you writing JavaScript.",
       "Rails design"),
    _s("ActiveJob is the queue interface and the actual queue is swappable, "
       "which is the pattern Rails uses everywhere.", "Rails design"),
    _s("Concerns are modules mixed into models and controllers, and they "
       "are also where a fat model goes to hide.", "Rails gotchas"),
    _s("Rails is opinionated on purpose. Fighting a convention is usually "
       "more work than the convention was ever costing you.",
       "Rails design"),
)


# ── Code ─────────────────────────────────────────────────────
#
# Each of these is valid Ruby, checked with `ruby -c`. Whether Rails would
# accept it needs a project and a database, which is a different claim.

RAILS_CODE: tuple[Passage, ...] = (
    _s("class Order < ApplicationRecord", "a model is a table"),
    _s("has_many :line_items, dependent: :destroy", "and what happens to them"),
    _s("belongs_to :customer, optional: true", "the other side of it"),
    _s("has_many :products, through: :line_items", "two hops, one call"),
    _s("validates :email, presence: true, uniqueness: true", "two rules, one line"),
    _s("scope :recent, -> { order(created_at: :desc) }", "a chainable query"),
    _s("before_action :authenticate_user!, except: %i[index show]",
       "the percent-i array of symbols"),
    _s("@orders = Order.includes(:customer).where(status: 'open')",
       "includes is what stops the N plus one"),
    _s("redirect_to @order, notice: 'Order was created.'", "and a flash message"),
    _s("render :new, status: :unprocessable_entity", "the status Turbo needs"),
    _s("params.require(:order).permit(:status, :total)", "strong parameters"),
    _s("resources :orders, only: %i[index show create]", "three routes, not seven"),
    _s("add_column :orders, :status, :string, default: 'open'", "a migration line"),
    _s("add_index :orders, %i[customer_id created_at]", "a composite index"),
    _s("Order.where('total > ?', 100).find_each do |order|",
       "find_each batches so the memory does not"),
    _s("rescue ActiveRecord::RecordNotFound => e", "the namespaced error"),
)
