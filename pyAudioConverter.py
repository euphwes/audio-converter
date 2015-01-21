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


def perform_conversion(files, args):

    ffmpeg_path = run_command('where', ['ffmpeg'], shell=True)
    if 'Could not find files' in ffmpeg_path:
        print("ffmpeg not found.")
        sys.exit(1)

    print('')
    print('Performing conversion:')
    print('    Output format: ' + args.format)
    if args.quality and not args.format == 'flac':
        print('    Output quality: ' + args.quality)
    print('')

    for flac in files:
        new_file = os.path.splitext(flac)[0] + '.' + args.format
        ffmpeg_args = ['-i', flac, '-qscale:a', args.quality, new_file]
        print('Converting: {}'.format(os.path.split(flac)[1]))
        run_command(ffmpeg_path, ffmpeg_args, shell=True)


def gather_files(root_directory):
    """Recursively check every file in a directory, identify the music files,
    and build a list of the full paths of all those files and return it."""

    all_files = list()
    for root, dirs, files in os.walk(root_directory):
        music_exts = ['.flac', '.FLAC', '.wav', '.WAV', '.ogg', '.OGG', '.mp3', '.MP3']
        flac_files = list(filter(lambda x: os.path.splitext(x)[1] in music_exts, files))
        flac_files = list(os.path.join(root, flac) for flac in flac_files)
        all_files.extend(flac_files)
    return all_files

#-----------------------------------------------------------------------------

parser = argparse.ArgumentParser()
parser.add_argument('directory', help='The directory whose FLAC files to convert.')
parser.add_argument('-f', '--format', required=True, help='The output format (mp3 or ogg) to convert to.', choices=['ogg','mp3','flac','wav'])
parser.add_argument('-q', '--quality', required=True, help='The desired output quality of the converted file.')
args = parser.parse_args()

# make sure format is lowercase so we don't have to deal with that later
args.format = args.format.lower()

all_files = gather_files(args.directory)
perform_conversion(all_files, args)
