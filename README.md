# Open Prime Rando
Open Source randomizer patcher for Prime 2 and eventually 3.



# Updating hash files

Some tests compare the output of the patcher against pre-recorded hash files. When a code change intentionally alters the output, these files need to be regenerated.

## Setup

The tests require ISO files for Metroid Prime 2: Echoes. Create a `.env` file in the repository root:

```
PRIME2_ISO=/path/to/prime2_ntsc.iso
PRIME2_PAL_ISO=/path/to/prime2_pal.iso
```

> These can also be set as regular environment variables instead of using `.env`.

## Running locally

```sh
uv run pytest --update-hashes -n 2
```

This runs only the hash-comparison tests and writes the new hashes in place of the old ones.

## Via GitHub (pull requests)

Anyone with write access to the repository can comment `/update-hashes` on a pull request. A workflow will run the tests on the self-hosted runner, commit the updated files, and push them to the PR branch.

# Credits

# Echoes

Banner image created by rekameohs. 