"""Template Tölvera program.

Example:
    $ python tolvera/basics/template.py
"""

from tolvera import Tolvera, run

def main(**kwargs):
    tv = Tolvera(**kwargs)

    @tv.render
    def _():
        return tv.px

if __name__ == '__main__':
    run(main)
