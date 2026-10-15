"""Web (Python): the learner writes a small web app in Python and a real server runs it.

    lib/web.py    the tiny Flask-like library a program imports (`from web import app, ...`)
    driver.py     the child process: loads the program, serves it on 127.0.0.1, answers `logs`/`stop`
    session.py    sessions for the Try it panel: a registry of children, requests made against them
    check.py      run_pyweb_check: a step's check makes real HTTP requests to the learner's app

See the "Python web" paragraph in CLAUDE.md.
"""
