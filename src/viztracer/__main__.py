# Licensed under the Apache License: http://www.apache.org/licenses/LICENSE-2.0
# For details: https://github.com/gaogaotiantian/viztracer/blob/master/NOTICE.txt

import sys
import argparse
import os
from . import VizTracer
from . import FlameGraph
from .report_builder import ReportBuilder


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--tracer", nargs="?", choices=["c", "python"], default="c")
    parser.add_argument("--output_file", "-o", nargs="?", default=None)
    parser.add_argument("--output_dir", nargs="?", default=None)
    parser.add_argument("--quiet", action="store_true", default=False)
    parser.add_argument("--max_stack_depth", nargs="?", type=int, default=-1)
    parser.add_argument("--exclude_files", nargs="*", default=None)
    parser.add_argument("--include_files", nargs="*", default=None)
    parser.add_argument("--ignore_c_function", action="store_true", default=False)
    parser.add_argument("--log_print", action="store_true", default=False)
    parser.add_argument("--pid_suffix", action="store_true", default=False)
    parser.add_argument("--save_flamegraph", action="store_true", default=False)
    parser.add_argument("--generate_flamegraph", nargs="?", default=None)
    parser.add_argument("--run", nargs="*", default=[])
    parser.add_argument("--combine", nargs="*", default=[])
    parser.add_argument("command", nargs=argparse.REMAINDER)
    options = parser.parse_args(sys.argv[1:])

    if options.command:
        command = options.command
    elif options.run:
        command = options.run
    elif options.generate_flamegraph:
        flamegraph = FlameGraph()
        flamegraph.load(options.generate_flamegraph)
        if options.output_file:
            ofile = options.output_file
        else:
            ofile = "result_flamegraph.html"
        flamegraph.save(ofile)
        exit(0)
    elif options.combine:
        builder = ReportBuilder(options.combine)
        if options.output_file:
            ofile = options.output_file
        else:
            ofile = "result.html"
        builder.save(output_file=ofile)
        exit(0)
    else:
        parser.print_help()
        exit(0)

    try:
        f = command[0]
        code_string = open(f).read()
    except FileNotFoundError:
        print("No such file as {}".format(f))
        exit(1)
    sys.argv = command[1:]
    if options.quiet:
        verbose = 0
    else:
        verbose = 1

    if options.output_file:
        ofile = options.output_file
    elif options.pid_suffix:
        ofile = "result.json"
    else:
        ofile = "result.html"

    if options.output_dir:
        if not os.path.exists(options.output_dir):
            os.mkdir(options.output_dir)
        ofile = os.path.join(options.output_dir, ofile)
        print(ofile)

    tracer = VizTracer(
        tracer=options.tracer,
        verbose=verbose,
        output_file=ofile,
        max_stack_depth=options.max_stack_depth,
        exclude_files=options.exclude_files,
        include_files=options.include_files,
        ignore_c_function=options.ignore_c_function,
        pid_suffix=options.pid_suffix,
        log_print=options.log_print
    )
    tracer.start()
    exec(code_string)
    tracer.stop()
    tracer.save(output_file=ofile, save_flamegraph=options.save_flamegraph)
