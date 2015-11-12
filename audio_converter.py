import os, argparse
from sys import stdout
from subprocess import Popen, PIPE

#-------------------------------------------------------------------------------------------------

def pprint(value):
    """ Custom print which prints the supplied value, and immediately flushes stdout. Useful if
    stdout is being buffered because we're piping it from a subprocess, but we still want to see
    printed info in the console immediately. """
    print(value)
    stdout.flush()

#-------------------------------------------------------------------------------------------------

def run_command(command, args):
    """ Runs the specified command-line tool, gathers the output, splits on newlines, and returns
    the list of lines to the caller. """
    proc = Popen([command] + args, stdout=PIPE, stderr=PIPE)
    return proc.communicate()[0].decode().split('\r\n')


def perform_conversion(args):
    """ Use ffmpeg to perform music file conversion. The arguments contain a top-level directory,
    presumably an artist directory, or containing several artist directories. The directories are
    examined recursively, and the ones containing music files are considered to be album
    directories, and those albums are processed. Those album folders are recreated at the same
    level as the original album folder, and the target format is appended to the folder name in
    parentheses. Each music file in the original album is converted to the target format, and
    placed in the newly-created directory.

    For example, consider a directory structure like this, with music files in the deepest
    directories only:

        /music
            /Green Day
                /Kerplunk
                /Insomniac
            /Tipper
                /Puzzle Dust EP
                /Shatter Box EP

    After processing with a target format of 'ogg', the music files will be converted, and placed
    in the following structure (without altering the original files or directory structure):

        /music
            /Green Day
                /Kerplunk (ogg)
                /Insomniac (ogg)
            /Tipper
                /Puzzle Dust EP (ogg)
                /Shatter Box EP (ogg)
    """

    ffmpeg_path = run_command('where', ['ffmpeg'])
    if 'Could not find files' in ffmpeg_path:
        pprint("ffmpeg not found.")
        sys.exit(1)

    pprint('\nPerforming conversion:')
    pprint('    Output format: ' + args.format)
    if args.quality and not args.format in ['flac','wav']:
        pprint('    Output quality: ' + args.quality)

    for music_in_directory in gather_files_from_subdirs(args.directory):

        current_dir = os.path.split(music_in_directory[0])[0]
        old_album_name = os.path.split(current_dir)[1]
        new_album_name = '{} ({})'.format(old_album_name, args.format)
        artist_dir = os.path.split(current_dir)[0]
        target_dir = os.path.join(artist_dir, new_album_name)

        if not os.path.exists(target_dir):
            os.makedirs(target_dir)

        pprint('\nProcessing "{}" into "{}"'.format(old_album_name, new_album_name))

        for music_file in music_in_directory:
            orig_file_no_ext = os.path.splitext(os.path.split(music_file)[1])[0]
            new_file_with_ext = '{}.{}'.format(orig_file_no_ext, args.format)
            new_file_path = os.path.join(target_dir, new_file_with_ext)

            ffmpeg_args = ['-i', music_file]
            if args.quality == '320k':
                ffmpeg_args.extend(['-b:a', args.quality, '-vn'])
            else:
                ffmpeg_args.extend(['-qscale:a', args.quality, '-vn'])
            if args.format == 'ogg':
                ffmpeg_args.extend(['-codec:a','libvorbis'])
            ffmpeg_args.append(new_file_path)

            pprint('    Converting: {}'.format(orig_file_no_ext))
            run_command(ffmpeg_path, ffmpeg_args)


def gather_files_from_subdirs(directory):
    """ Generator which yields a list of audio files from every subdirectory in the supplied
    directory, one subdirectory at a time. """

    music_exts = ['.flac', '.FLAC', '.wav', '.WAV', '.ogg', '.OGG', '.mp3', '.MP3', '.m4a', '.M4A']

    for root, _, files in os.walk(directory):
        music_files = list(filter(lambda x: os.path.splitext(x)[1] in music_exts, files))
        music_files = list(os.path.join(root, f) for f in music_files)
        if len(music_files) > 0:
            yield music_files

#-------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('directory', help='The directory whose audio files to convert.')
    parser.add_argument('-f', '--format', required=True, help='The output format (mp3 or ogg) to convert to.', choices=['ogg','mp3','flac','wav'])
    parser.add_argument('-q', '--quality', required=True, help='The desired output quality of the converted file.')
    args = parser.parse_args()

    # make sure format is lowercase so we don't have to deal with that later
    args.format = args.format.lower()

    perform_conversion(args)
