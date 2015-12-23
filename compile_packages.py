''' This converts each folder in packages/ into a zip, saving the zips into zips/. This way it's easy to edit them.'''
import os
import sys
import itertools
from zipfile import ZipFile, ZIP_LZMA

BEE2_LOCATION = '../BEE2.4/src'
sys.path.append(BEE2_LOCATION)

import utils
from property_parser import Property
import vmfLib as VLib

OPTIMISE_VMF = utils.conv_bool(input('Optimise zips? '))

print('Optimising: ', OPTIMISE_VMF)


def clean_vmf(vmf_path):
    """Optimise the VMFs, removing unneeded entities or objects."""
    inst = VLib.VMF.parse(vmf_path)

    for ent in itertools.chain([inst.spawn], inst.entities[:]):
        editor = ent.editor
        # Remove useless metadata
        for cat in ('comments', 'color', 'logicalpos'):
            if cat in editor:
                del editor[cat]

        # Remove entities that have their visgroups hidden.
        if ent.hidden or not utils.conv_bool(editor.get('visgroupshown', '1'), True):
            print('Removing hidden ent')
            inst.remove_ent(ent)
            continue

        # Remove info_null entities
        if ent['classname'] == 'info_null':
            print('Removing info_null...')
            inst.remove_ent(ent)
            continue

        for solid in ent.solids[:]:
            if all(face.mat.casefold() == 'tools/toolsskip' for face in solid):
                print('Removing SKIP brush')
                ent.solids.remove(solid)
                continue

            if solid.hidden or not utils.conv_bool(solid.editor.get('visgroupshown', '1'), True):
                print('Removing hidden brush')
                ent.solids.remove(solid)
                continue

    return inst.export(inc_version=False, minimal=True)


# Delete these files, if they exist in the source folders.
# Users won't need them.
DELETE_EXTENSIONS = ['vmx', 'log', 'bsp', 'prt', 'lin']


def do_folder(zip_path, path):
    for package in os.listdir(path):
        package_path = os.path.join(path, package)
        if not os.path.isdir(package_path):
            continue

        if 'info.txt' not in os.listdir(package_path):
            do_folder(zip_path, package_path)
            continue

        print('| ' + package + '.zip')
        pack_zip_path = os.path.join(zip_path, package)

        zip_file = ZipFile(
            pack_zip_path + '.zip',
            'w',
            compression=ZIP_LZMA,
        )

        for base, dirs, files in os.walk(package_path):
            for file in files:
                full_path = os.path.normpath(os.path.join(base, file))
                rel_path = os.path.relpath(full_path, package_path)
                if file[-3:] in DELETE_EXTENSIONS:
                    print('\nX   \\' + rel_path)
                    os.remove(full_path)
                    continue
                print('.', end='', flush=True)

                if OPTIMISE_VMF and file.endswith('.vmf'):
                    print(rel_path)
                    zip_file.writestr(rel_path, clean_vmf(full_path))
                else:
                    zip_file.write(full_path, rel_path)
        print('')


def main():
    zip_path = os.path.join(os.getcwd(), 'zips/packages/')
    if os.path.isdir(zip_path):
        for file in os.listdir(zip_path):
            print('Deleting', file)
            os.remove(os.path.join(zip_path, file))
    else:
        os.makedirs(zip_path)

    path = os.path.join(os.getcwd(), 'packages\\')
    do_folder(zip_path, path)

if __name__ == '__main__':
    main()