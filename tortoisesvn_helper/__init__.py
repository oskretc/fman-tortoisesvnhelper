from fman import DirectoryPaneCommand, show_alert, show_prompt, load_json, save_json, YES, NO
from fman.fs import is_dir, exists
from fman.url import splitscheme, as_url, as_human_readable
from subprocess import DEVNULL, Popen

import os
import shlex


_TORTOISEPROCPATHDEFAULT = 'C:/Program Files/TortoiseSVN/bin/TortoiseProc.exe'
_TORTOISEPROCCONFIGFILE = 'TortoiseSVNHelper Config.json'
_TORTOISEPROCPATH = ''

settings = load_json(_TORTOISEPROCCONFIGFILE, default={'path': _TORTOISEPROCPATHDEFAULT})

if settings['path'] and exists(as_url(settings['path'])):
	_TORTOISEPROCPATH = settings['path']

else:
	_TORTOISEPROCPATH = _TORTOISEPROCPATHDEFAULT

class SVNSwtich(DirectoryPaneCommand):
	aliases = ('Svn: Switch', 'SVN: SWITCH')
	def __call__(self):
		url = self.pane.get_path()
		scheme, path = splitscheme(url)

		paths=[]
		paths.append(as_url(path))	
		if scheme != 'file://':
			show_alert('{} is not supported'.format(url))
			return

		openCommand(" /command:switch /path:", paths, path)	

class SVNCommit(DirectoryPaneCommand):
	aliases = ('Svn: Commit', 'SVN: COMMIT')
	def __call__(self):
		url = self.pane.get_path()
		scheme, path = splitscheme(url)

		paths=[]
		paths.append(as_url(path))	
		if scheme != 'file://':
			show_alert('{} is not supported'.format(url))
			return

		openCommand(" /command:commit /path:", paths, path)	

class SVNLog(DirectoryPaneCommand):
	aliases = ('Svn: Log', 'SVN: LOG')
	def __call__(self):
		url = self.pane.get_path()
		scheme, path = splitscheme(url)

		paths=[]
		paths.append(as_url(path))	
		if scheme != 'file://':
			show_alert('{} is not supported'.format(url))
			return

		openCommand(" /command:log /path:", paths, path)

class SVNUpdate(DirectoryPaneCommand):
	aliases = ('Svn: Update', 'SVN: UPDATE')
	def __call__(self):
		url = self.pane.get_path()
		scheme, path = splitscheme(url)

		paths=[]
		paths.append(as_url(path))	
		if scheme != 'file://':
			show_alert('{} is not supported'.format(url))
			return

		openCommand(" /command:update /path:", paths, path)

class SVNRepoBrowser(DirectoryPaneCommand):
	aliases = ('Svn: Open Repo Browser', 'SVN: OPEN REPO BROWSER')
	def __call__(self):
		url = self.pane.get_path()
		scheme, path = splitscheme(url)

		paths=[]
		paths.append(as_url(path))	
		if scheme != 'file://':
			show_alert('{} is not supported'.format(url))
			return

		openCommand(" /command:repobrowser /path:", paths, path)

class SVNRepoStatus(DirectoryPaneCommand):
	aliases = ('Svn: Repo Status', 'SVN: REPO STATUS')
	def __call__(self):
		url = self.pane.get_path()
		scheme, path = splitscheme(url)

		paths=[]
		paths.append(as_url(path))	
		if scheme != 'file://':
			show_alert('{} is not supported'.format(url))
			return

		openCommand(" /command:repostatus /path:", paths, path)		

class TortoiseSVNProcSetPath(DirectoryPaneCommand):
	def __call__(self):
		if set_tortoisesvnproc_install_path():
			show_alert('TortoiseSVNProc.exe path updated')
		else:
			show_alert('Failed to update TortoiseSVNProc.exe path')

def to_path(url):
	return splitscheme(url)[1]

def set_tortoisesvnproc_install_path():
	new_tortoisesvnproc_filepath, ok = show_prompt('Enter full path to TortoiseSVNProc.exe program here', default = get_current_tortoisesvnproc_install_path(), selection_start = 0, selection_end = None )

	if not ok:
		return False

	if not exists(as_url(new_tortoisesvnproc_filepath)):
		show_alert('Path to TortoiseSVNProc given is invalid')
		return False

	_TORTOISEPROCPATH = new_tortoisesvnproc_filepath
	save_json(_TORTOISEPROCCONFIGFILE, {'path': new_tortoisesvnproc_filepath})
	return True

def get_current_tortoisesvnproc_install_path():
	settings = load_json(_TORTOISEPROCCONFIGFILE, default={'path': _TORTOISEPROCPATHDEFAULT})

	if settings['path'] and exists(as_url(settings['path'])):
		return settings['path']
	else:
		return _TORTOISEPROCPATHDEFAULT

def openCommand(option, files, path):
	tortoisesvnproc_path = get_current_tortoisesvnproc_install_path()

	if not exists(as_url(tortoisesvnproc_path)):
		show_alert('Invalid TortoiseSVNProc.exe path: ' + tortoisesvnproc_path)
		choice = show_alert('Update Path to TortoiseSVNProc.exe?', buttons = YES | NO )

		if choice == YES:
			if not set_tortoisesvnproc_install_path():
				# user failed to set sublime install path. bail.
				show_alert('command failed because no valid path to TortoiseSVNProc.exe given')
				return

		else:
			# no path to use, user doesnt want to set one now. bail.
			show_alert('command failed because no valid path to TortoiseSVNProc.exe given')
			return

	# _TORTOISEPROCPATH = as_human_readable('file://'+ tortoisesvnproc_path)
	_TORTOISEPROCPATH =  tortoisesvnproc_path

	# TODO: Check if quoting is working for other platforms
	args = [shlex.quote(to_path(x)) for x in files]
	cmd= _TORTOISEPROCPATH  + " " + option + " ".join(args)
	
	env = create_clean_environment()
	Popen(cmd, shell=False, cwd=path,
		stdin=DEVNULL, stdout=DEVNULL, stderr=DEVNULL, env=env)

def create_clean_environment():
	# Pyinstaller, used by fman to ship on Linux sets LD_LIBRARY_PATH, which
	# prevents starting Qt5 applications. Remove the variable if it is set.
	env = dict(os.environ)
	try:
		del env['LD_LIBRARY_PATH']
	except KeyError:
		pass
	return env		