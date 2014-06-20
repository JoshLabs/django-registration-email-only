from setuptools import setup, os


packages, data_files = [], []
root_dir = os.path.dirname(__file__)
if root_dir:
    os.chdir(root_dir)

for dirpath, dirnames, filenames in os.walk('registration_email_only'):
    # Ignore dirnames that start with '.'
    for i, dirname in enumerate(dirnames):
        if dirname.startswith('.'):
            del dirnames[i]
    if '__init__.py' in filenames:
        pkg = dirpath.replace(os.path.sep, '.')
        if os.path.altsep:
            pkg = pkg.replace(os.path.altsep, '.')
        packages.append(pkg)
    elif filenames:
        prefix = dirpath[24:]  # Strip "registration_email_only/" or "registration_email_only\"
        for f in filenames:
            data_files.append(os.path.join(prefix, f))

setup(
    name='django-registration-email-only',
    version='0.1.1',
    author='Gabriel Grant',
    author_email='g@briel.ca',
    packages=packages,
    package_data={'registration_email_only': data_files},
    license='LGPL',
    long_description=open('README').read(),
    install_requires=[
        'Django>=1.4, <=1.6.5',
        'django-registration==1.0',
        'simple-import==0.1.1',
        'pyDes==2.0.1',
    ],
)
