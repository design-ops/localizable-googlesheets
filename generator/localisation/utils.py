from os import path, makedirs
from hashlib import sha1


def create_file(output_dir: str, filename: str):
    """
    Creates a file handle to the given filename and returns it.
    """
    filepath = path.join(output_dir, filename)
    makedirs(path.dirname(filepath), exist_ok=True)

    file = open(filepath, "w+")
    return file


def __hash(path: str) -> str:
    BLOCKSIZE = 65536
    hasher = sha1()
    with open(path, 'rb') as f:
        buffer = f.read(BLOCKSIZE)
        while len(buffer) > 0:
            hasher.update(buffer)
            buffer = f.read(BLOCKSIZE)
    return hasher.hexdigest()


def create_checksum(filename, strings_paths: (dict, dict), output_dir=".") -> str:
    """
    Creates a checksum of the given filename
    """
    with create_file(output_dir=output_dir, filename=filename) as f:
        for item in strings_paths:
            for localisation in item:
                sha_hash = __hash(item[localisation])
                f.write("{} {}\n".format(sha_hash, localisation))

        return path.realpath(f.name)
