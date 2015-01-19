import os, argparse
from subprocess import Popen, PIPE

def run_command(command, args, shell=False):
    ''' Runs the specified command-line tool, gathers the output, splits on
    newlines, and returns the list of lines to the caller.
    '''

    command = [command]
    command.extend(args)

    proc = Popen(command, stdout=PIPE, stderr=PIPE, shell=shell)

    output_lines = proc.communicate()[0].decode('UTF-8').split('\r\n')
    return output_lines

#-----------------------------------------------------------------------------

ffmpeg_path = run_command('where', ['ffmpeg'], shell=True)
if 'Could not find files' in ffmpeg_path:
    print("ffmpeg not found.")
    sys.exit(1)
