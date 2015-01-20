import os, argparse
from subprocess import Popen, PIPE

def run_command(command, args, shell=False):
    """Runs the specified command-line tool, gathers the output, splits on
    newlines, and returns the list of lines to the caller."""

    command = [command]
    command.extend(args)

    proc = Popen(command, stdout=PIPE, stderr=PIPE, shell=shell)

    output_lines = proc.communicate()[0].decode('UTF-8').split('\r\n')
    return output_lines


def perform_ogg_conversion(files, args):

    ffmpeg_path = run_command('where', ['ffmpeg'], shell=True)
    if 'Could not find files' in ffmpeg_path:
        print("ffmpeg not found.")
        sys.exit(1)

    print('')

    for flac in files:
        new_file = os.path.splitext(flac)[0] + '.ogg'
        ffmpeg_args = ['-i', flac, '-qscale:a', args.quality, new_file]
        print('Performing: ffmpeg {}'.format(' '.join(ffmpeg_args)))
        run_command(ffmpeg_path, ffmpeg_args, shell=True)


def perform_mp3_conversion(files, args):

    ffmpeg_path = run_command('where', ['ffmpeg'], shell=True)
    if 'Could not find files' in ffmpeg_path:
        print("ffmpeg not found.")
        sys.exit(1)

    print('')

    for flac in files:
        new_file = os.path.splitext(flac)[0] + '.mp3'
        ffmpeg_args = ['-i', flac, '-qscale:a', args.quality, new_file]
        print('Performing: ffmpeg {}'.format(' '.join(ffmpeg_args)))
        run_command(ffmpeg_path, ffmpeg_args, shell=True)

#-----------------------------------------------------------------------------

parser = argparse.ArgumentParser()
parser.add_argument('directory', help='The directory whose FLAC files to convert.')
parser.add_argument('-f', '--format', required=True, help='The output format (mp3 or ogg) to convert to.', choices=['ogg','mp3'])
parser.add_argument('-q', '--quality', required=True, help='The desired output quality of the converted file.')

args = parser.parse_args()

all_files = list()
for root, dirs, files in os.walk(args.directory):
    flac_files = list(filter(lambda x: os.path.splitext(x)[1] in ['.flac', '.FLAC'], files))
    full_flacs = list(os.path.join(root, flac) for flac in flac_files)
    all_files.extend(full_flacs)

if args.format == "ogg":
    perform_ogg_conversion(all_files, args)
elif args.format == 'mp3':
    perform_mp3_conversion(all_files, args)
