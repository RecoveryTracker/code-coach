"""More Rails: the rest of the lines, and whole blocks to type.

`rails` gave the framework twenty passages of lore and sixteen lines of
code, which is one sitting. This is the rest of it, and the part that was
missing entirely: blocks.

Every other code theme gets its blocks from the curriculum — the
fundamentals and the solution bank, whole functions with their
indentation. Rails has neither, because it has no workbook pages, so its
blocks are written here instead. That is the only way this theme can drive
Blocks mode at all, and blocks are the drill that teaches shape rather
than punctuation: what sits under what, and Enter as part of writing code.

Every line and every block below is checked with `ruby -c`, which proves
the Ruby parses. It does not prove Rails would accept it — that needs a
project, a Gemfile and a database — and the distinction is worth keeping
rather than implying a stronger check than was run.
"""

from __future__ import annotations

from code_coach.typing.snippets import Passage, _s

# ── More lore ────────────────────────────────────────────────

RAILS_LORE2: tuple[Passage, ...] = (
    _s("A Rails application is a Ruby application. Everything the framework "
       "does is a method call, which is why so much of it can be read.",
       "Rails design"),
    _s("The autoloader maps a constant to a file by name, so UserMailer "
       "lives in user_mailer.rb and nothing has to require it.",
       "Rails internals"),
    _s("Zeitwerk replaced the old autoloader and is stricter: a file that "
       "does not define the constant its name promises is an error rather "
       "than a mystery.", "Rails internals"),
    _s("A partial is a view that begins with an underscore, and rendering a "
       "collection of them is one call rather than a loop.",
       "Rails conventions"),
    _s("The flash is a hash that survives exactly one redirect, which is why "
       "notice and alert work the way they do.", "Rails conventions"),
    _s("Migrations run forwards and, when they can, backwards. Writing them "
       "with change rather than up and down is how Rails works out the "
       "reverse for you.", "Rails conventions"),
    _s("A reversible migration is worth the effort on the day a deploy goes "
       "wrong and the schema has to go back.", "Rails operations"),
    _s("Seeds are for the data an application cannot run without, not for "
       "the data that makes a demo look good.", "Rails conventions"),
    _s("find_each loads in batches of a thousand. Using each on a large "
       "table pulls every row into memory first, which is the difference.",
       "Rails performance"),
    _s("pluck asks the database for the columns you want and returns an "
       "array, skipping the model objects entirely.", "Rails performance"),
    _s("counter_cache keeps a total in a column so a count does not have to "
       "be a query, and it is the standard answer to a slow index page.",
       "Rails performance"),
    _s("A validation runs in Ruby and a database constraint runs in the "
       "database. You want both, because only one of them is true when two "
       "requests arrive at once.", "Rails gotchas"),
    _s("touch: true on a belongs_to updates the parent's timestamp, which is "
       "how a cache key for the parent knows a child changed.",
       "Rails caching"),
    _s("Russian doll caching nests fragment caches so an inner change "
       "invalidates the outer one and nothing else.", "Rails caching"),
    _s("Rails encrypts credentials into a file and keeps the key out of the "
       "repository, which is why config/master.key is in gitignore.",
       "Rails security"),
    _s("CSRF protection is on by default and the form helpers put the token "
       "in for you, which is why a hand-written form fails.",
       "Rails security"),
    _s("Turbo Frames replace one part of a page and Turbo Streams send a "
       "list of changes to apply. The first is a boundary, the second is an "
       "instruction.", "Rails design"),
    _s("Stimulus is the small half of Hotwire: controllers attached to "
       "markup with data attributes, for the behaviour Turbo cannot do "
       "alone.", "Rails design"),
    _s("Solid Queue, Solid Cache and Solid Cable moved the queue, the cache "
       "and the sockets into the database, so a small application needs one "
       "server rather than four.", "Rails design"),
    _s("Rails ships with a test framework and a fixture system, and the "
       "argument about whether to use them instead of factories is older "
       "than most of the applications having it.", "Rails testing"),
    _s("A system test drives a real browser. It is the slowest test you can "
       "write and the only one that proves the page works.",
       "Rails testing"),
    _s("rails console loads the whole application, and the sandbox flag "
       "rolls back everything you did on the way out.", "Rails tooling"),
    _s("rails routes prints every route with the helper name, which is "
       "faster than guessing what the path method is called.",
       "Rails tooling"),
    _s("bin/setup is meant to take a fresh checkout to a running "
       "application in one command, and is worth keeping true.",
       "Rails conventions"),
)


# ── More lines ───────────────────────────────────────────────
#
# Checked with `ruby -c`. Whether Rails would accept them needs a project
# and a database, which is a different claim.

RAILS_CODE2: tuple[Passage, ...] = (
    _s("validates :status, inclusion: { in: %w[open paid shipped] }",
       "the percent-w array of strings"),
    _s("validates :total, numericality: { greater_than_or_equal_to: 0 }",
       "a numeric rule"),
    _s("has_one_attached :avatar", "ActiveStorage, in one line"),
    _s("has_rich_text :body", "ActionText, in one line"),
    _s("enum :status, { open: 0, paid: 1, shipped: 2 }",
       "an integer column read as a name"),
    _s("scope :paid, -> { where(status: 'paid') }", "another chainable query"),
    _s("scope :since, ->(date) { where('created_at > ?', date) }",
       "a scope that takes an argument"),
    _s("delegate :name, :email, to: :customer, prefix: true",
       "customer_name without writing the method"),
    _s("after_create_commit -> { broadcast_prepend_to :orders }",
       "the Turbo Stream callback"),
    _s("before_validation :normalize_email, on: :create",
       "only on create, not on update"),
    _s("self.email = email.to_s.strip.downcase", "what that method does"),
    _s("Order.where(status: 'open').order(created_at: :desc).limit(10)",
       "three calls, one query"),
    _s("Order.group(:status).count", "a hash of status to count"),
    _s("Order.pluck(:id, :total)", "arrays, not models"),
    _s("Order.find_by(reference: params[:reference])",
       "find_by returns nil, find raises"),
    _s("Order.create!(customer: customer, status: 'open')",
       "the bang raises instead of returning false"),
    _s("order.update!(status: 'paid', paid_at: Time.current)",
       "Time.current, not Time.now"),
    _s("Order.transaction do", "everything inside, or nothing"),
    _s("raise ActiveRecord::Rollback unless order.save",
       "the rollback that is not an error"),
    _s("Order.includes(:line_items).where(line_items: { sku: sku })",
       "includes with a condition on the join"),
    _s("Order.left_joins(:line_items).where(line_items: { id: nil })",
       "the orders with nothing in them"),
    _s("Order.where.not(status: 'open')", "where.not, not a string"),
    _s("Order.where(created_at: 1.week.ago..)",
       "an endless range as a condition"),
    _s("head :no_content", "a response with nothing in it"),
    _s("respond_to do |format|", "and a block per format"),
    _s("format.turbo_stream { render :created }", "the Turbo response"),
    _s("rescue_from ActiveRecord::RecordNotFound, with: :not_found",
       "handled once, for the whole controller"),
    _s("private", "and everything under it is not an action"),
    _s("def set_order", "the before_action's method"),
    _s("@order = Order.find(params[:id])", "params, and the id in it"),
    _s("redirect_to orders_path, status: :see_other",
       "the status a Turbo delete needs"),
    _s("create_table :orders do |t|", "a migration's table block"),
    _s("t.references :customer, null: false, foreign_key: true",
       "a column and a constraint in one"),
    _s("t.timestamps", "created_at and updated_at, both"),
    _s("add_index :orders, :reference, unique: true",
       "the constraint a validation cannot make"),
    _s("change_column_null :orders, :status, false",
       "tightening a column that already exists"),
    _s("ActiveRecord::Base.connection.execute(sql)",
       "the escape hatch, for when you need it"),
    _s("OrderMailer.with(order: order).confirmation.deliver_later",
       "queued, not sent in the request"),
    _s("class CleanupJob < ApplicationJob", "a background job"),
    _s("queue_as :low", "which queue it waits in"),
    _s("retry_on Net::OpenTimeout, wait: :polynomially_longer",
       "backoff without writing backoff"),
    _s("Rails.cache.fetch([order, :total], expires_in: 1.hour) do",
       "a cache key made of the record"),
    _s("Rails.logger.info { \"order #{order.id} paid\" }",
       "the block form, so the string is built only if it is logged"),
    _s("Current.user = User.find_by(id: session[:user_id])",
       "CurrentAttributes, per request"),
    _s("test 'an order starts open' do", "a Rails test, not an RSpec one"),
    _s("assert_difference -> { Order.count }, 1 do",
       "asserting on what changed"),
    _s("assert_redirected_to order_url(Order.last)",
       "the url helper, in a test"),
    _s("travel_to Time.zone.parse('2026-01-01') do",
       "freezing the clock for a block"),
)


# ── Blocks ───────────────────────────────────────────────────
#
# Whole shapes, indentation included. Blocks mode is the one that drills
# what sits under what, and Rails had nothing to offer it until now.


def _b(text: str, note: str) -> Passage:
    return Passage(text, note)


RAILS_BLOCKS: tuple[Passage, ...] = (
    _b(
        "class Order < ApplicationRecord\n"
        "  belongs_to :customer\n"
        "  has_many :line_items, dependent: :destroy\n"
        "\n"
        "  validates :status, presence: true\n"
        "end",
        "a model, top to bottom",
    ),
    _b(
        "class Customer < ApplicationRecord\n"
        "  has_many :orders\n"
        "  has_many :line_items, through: :orders\n"
        "\n"
        "  scope :active, -> { where(active: true) }\n"
        "end",
        "through, and a scope",
    ),
    _b(
        "def index\n"
        "  @orders = Order.includes(:customer).recent.limit(50)\n"
        "end",
        "an index action that does not N plus one",
    ),
    _b(
        "def create\n"
        "  @order = Order.new(order_params)\n"
        "  if @order.save\n"
        "    redirect_to @order, notice: 'Order was created.'\n"
        "  else\n"
        "    render :new, status: :unprocessable_entity\n"
        "  end\n"
        "end",
        "the create action, both halves",
    ),
    _b(
        "def update\n"
        "  if @order.update(order_params)\n"
        "    redirect_to @order, status: :see_other\n"
        "  else\n"
        "    render :edit, status: :unprocessable_entity\n"
        "  end\n"
        "end",
        "update, and the status Turbo needs",
    ),
    _b(
        "private\n"
        "\n"
        "def order_params\n"
        "  params.require(:order).permit(:status, :total, :customer_id)\n"
        "end",
        "strong parameters, where they live",
    ),
    _b(
        "class CreateOrders < ActiveRecord::Migration[8.0]\n"
        "  def change\n"
        "    create_table :orders do |t|\n"
        "      t.references :customer, null: false, foreign_key: true\n"
        "      t.string :status, null: false, default: 'open'\n"
        "      t.decimal :total, precision: 10, scale: 2\n"
        "\n"
        "      t.timestamps\n"
        "    end\n"
        "  end\n"
        "end",
        "a migration, and change works backwards too",
    ),
    _b(
        "class AddReferenceToOrders < ActiveRecord::Migration[8.0]\n"
        "  def change\n"
        "    add_column :orders, :reference, :string\n"
        "    add_index :orders, :reference, unique: true\n"
        "  end\n"
        "end",
        "a column and the index that guards it",
    ),
    _b(
        "Rails.application.routes.draw do\n"
        "  resources :orders do\n"
        "    resources :line_items, only: %i[create destroy]\n"
        "  end\n"
        "\n"
        "  root 'orders#index'\n"
        "end",
        "nested resources, and a root",
    ),
    _b(
        "class OrdersController < ApplicationController\n"
        "  before_action :authenticate_user!\n"
        "  before_action :set_order, only: %i[show edit update destroy]\n"
        "\n"
        "  def show; end\n"
        "end",
        "the top of a controller",
    ),
    _b(
        "module Archivable\n"
        "  extend ActiveSupport::Concern\n"
        "\n"
        "  included do\n"
        "    scope :archived, -> { where.not(archived_at: nil) }\n"
        "  end\n"
        "end",
        "a concern, and what included do is for",
    ),
    _b(
        "class OrderTotal\n"
        "  def initialize(order)\n"
        "    @order = order\n"
        "  end\n"
        "\n"
        "  def call\n"
        "    @order.line_items.sum { |item| item.price * item.quantity }\n"
        "  end\n"
        "end",
        "a plain object, for the logic a model should not hold",
    ),
    _b(
        "class ChargeOrderJob < ApplicationJob\n"
        "  queue_as :default\n"
        "  retry_on Net::OpenTimeout, wait: :polynomially_longer\n"
        "\n"
        "  def perform(order)\n"
        "    Payments.charge(order)\n"
        "  end\n"
        "end",
        "a job, with its retry rule",
    ),
    _b(
        "Order.transaction do\n"
        "  order.update!(status: 'paid')\n"
        "  Payment.create!(order: order, amount: order.total)\n"
        "end",
        "two writes that happen together or not at all",
    ),
    _b(
        "Order.where(status: 'open')\n"
        "     .where('created_at < ?', 30.days.ago)\n"
        "     .find_each(batch_size: 500) do |order|\n"
        "  order.update!(status: 'expired')\n"
        "end",
        "a chain across lines, and a batched walk",
    ),
    _b(
        "class OrderTest < ActiveSupport::TestCase\n"
        "  test 'an order starts open' do\n"
        "    order = Order.create!(customer: customers(:one))\n"
        "    assert_equal 'open', order.status\n"
        "  end\n"
        "end",
        "a model test, and a fixture",
    ),
)
