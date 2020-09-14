"""
The module sphinx_computron provides the "computron-injection" directive for Sphinx.
See README.rst for documentation details.
Originally authored by JP Senior, forked and reworked by Pavel Kirienko.
"""

import io
import sys
import typing
import pathlib

import docutils.nodes
import docutils.parsers.rst
import docutils.statemachine

import sphinx.util.nodes


class ComputronInjectionDirective(docutils.parsers.rst.Directive):
    has_content = True
    required_arguments = 0
    optional_arguments = 2

    # noinspection PyUnresolvedReferences
    option_spec = {
        'filename': docutils.parsers.rst.directives.path,
        'argv':     docutils.parsers.rst.directives.unchanged,
    }

    def run(self):
        filename = self.options.get('filename')
        argv = [filename]
        try:
            argv += str(self.options['argv']).split()
        except LookupError:
            pass

        source = ''
        if filename is not None:
            host_file = self.state_machine.document.current_source
            assert isinstance(host_file, str)
            abs_filename = pathlib.Path(host_file).absolute().parent / filename
            with open(str(abs_filename), 'r') as source_file:
                source = source_file.read() + '\n'
        source += '\n'.join(self.content)

        execution_output = _execute_python_collect_stdout(source, argv)

        vl = docutils.statemachine.StringList()
        for index, el in enumerate(execution_output.splitlines()):
            vl.append(el, '<computron-injection-output>', index + 1)

        node = docutils.nodes.section()
        node.document = self.state.document

        sphinx.util.nodes.nested_parse_with_titles(self.state, vl, node)

        return node.children


def _execute_python_collect_stdout(source: str, argv: typing.Sequence[str]) -> str:
    """
    Executes the supplied Python source and returns its stdout output. Stderr is not captured;
    that is, it is delivered into the host process' stderr destination (usually the terminal running Sphinx).
    """
    original_stdout, sys.stdout = sys.stdout, io.StringIO()
    original_argv, sys.argv = sys.argv, list(argv)
    try:
        # For some reason execution fails with a NameError unless globals are provided explicitly,
        # reporting that a new item defined inside the exec'd scope is not defined. Weird.
        exec(source, {'sys': 'sys'})
        return sys.stdout.getvalue()
    finally:
        sys.stdout = original_stdout
        sys.argv = original_argv


def setup(app):
    app.add_directive('computron-injection', ComputronInjectionDirective)
    return {
        'parallel_read_safe': True,
    }
