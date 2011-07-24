#!/usr/bin/python

import hashlib
import json
import os
import sys

IMAGE_EXTS = ['jpg', 'cr2', 'png']

class Doop():
    def get_dupes(self, directory_to_walk):
        """Returns a dictionary of hashes for duplicate files and folders of duplicated objects

        The object returned is a nested dictionary containing arrays of
        duplicate files with their absolute paths and duplicate folders.
        Duplicate folders are defined as having the same files (by hash)
        contained in them. This is shallow equality, only qualifying files
        hashes are considered in the encompassing folders hash.
        """
        # Dictionaries to hold the occurrences of hashes of images and complete folders
        # Their structures are:
        # { 'some_hash': ['some occurrences', 'some_other_occurrences with same hash'], ... }
        global_image_hash_dictionary = {}
        global_folder_hash_dictionary = {}

        for dirpath, dirnames, filenames in os.walk(directory_to_walk):
            # Per folder tracking
            files_checked = []
            for filename in filenames:
                file_path = os.path.join(dirpath, filename)
                if filename.split('.')[-1].lower() in IMAGE_EXTS:
                    with open(file_path, 'rb') as image:
                        # Hash aggregation for individual files
                        # Get the hash of the image, a hash of the first 8kb should be enough right?
                        md5 = hashlib.md5(image.read(1024)).hexdigest()
                        # Keep tabs of the md5's in this folder
                        files_checked.append(md5)
                        image_dups_array = global_image_hash_dictionary.get(md5, [])
                        image_dups_array.append(file_path)
                        global_image_hash_dictionary[md5] = image_dups_array

            # Hash aggregation for folders full of files
            # A hash representing all the duplicate md5's found in this folder
            duplicate_folder_hash = hash("".join(set(files_checked)))
            duplicate_folder_array = global_folder_hash_dictionary.get(duplicate_folder_hash, [])
            duplicate_folder_array.append(dirpath)
            global_folder_hash_dictionary[duplicate_folder_hash] = duplicate_folder_array

        return_duplicate_images = {}
        for key, value in global_image_hash_dictionary.items():
            if len(value) > 1:
                return_duplicate_images[key] = value

        return_duplicate_folders = {}
        for key, value in global_folder_hash_dictionary.items():
            if len(value) > 1:
                return_duplicate_folders [key] = value

        if return_duplicate_folders == {} and return_duplicate_images == {}:
            return False

        return {
            'duplicate_images': return_duplicate_images,
            'duplicate_folders': return_duplicate_folders
        }

def exit_with_error(message):
    sys.stderr.writeln(message)
    sys.exit(1)

if __name__ == '__main__':
    try:
        directory_to_walk = os.path.abspath(os.path.expanduser(sys.argv[1]))
    except IndexError:
        exit_with_error("No directory provided")
    if not os.path.isdir(directory_to_walk):
        exit_with_error("No directory provided")

    dups = Doop().get_dupes(directory_to_walk)
    if not dups:
        exit_with_error("No duplicates found")
    else:
        sys.stdout.write(json.dumps(dups, indent=4))
        sys.exit(0)
