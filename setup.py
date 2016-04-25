from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext

setup(
	name = "DragonCreole",
	packages = ["dragoncreole"],
	version = "0.2.0",
	description = "Optimized parser for creole-like markup language",
	author = "Zauber Paracelsus",
	author_email = "admin@zauberparacelsus.xyz",
	url = "http://github.com/zauberparacelsus/dragoncreole",
	download_url = "https://github.com/zauberparacelsus/dragoncreole/tarball/0.2",
	keywords = ["parser", "markup", "html"],
	install_requires= [
		'html2text',
		'cython'
	],
	classifiers = [
		"Programming Language :: Python",
		"Development Status :: 4 - Beta",
		"Environment :: Other Environment",
		"Intended Audience :: Developers",
		"License :: OSI Approved :: Mozilla Public License 2.0 (MPL 2.0)",
		"Operating System :: OS Independent",
		"Topic :: Software Development :: Libraries :: Python Modules",
		"Topic :: Text Processing :: Markup :: HTML"
	],
	long_description = "",
	cmdclass = {"build_ext": build_ext},
	ext_modules = [Extension("dragoncreole.DragonCreoleC", ["dragoncreole/dragoncreole.py"])]
)
