Repository Management
=====================

Features
--------

* Git, SVN, Bazaar and Mercurial support.
* Clone, update, remove, enable and disable repositories.
* Show info about the latest commit.
* Database-independent management.


Known Issues / Roadmap
----------------------

* Add SSL compatiblity.
* Improve repository tests before appending to **addons_path**. A harmful repository may render the server unusable.
* Add proper usage instructions.
* When adding/removing a repo, update only the **addons_path** parameter – not the whole config file.
* Detect identical repos. Currently, https://<domain>.com/<name> != https://<domain>.com/<name>.git
* Directory symlinks are detected as a different repo, even if they are linked to the same base directory.
* Directory names follow the next – sometimes quite long – structure: <vcs>_<source>_<branch>. (Maybe make them shorter?)


Requirenments
-------------

* Git (git) (version >= 1.7.0)
    * Binary: `apt-get install git`
    * Module: `pip install gitpython` – or – `apt-get install python-git`
* Bazaar (bzr):
    * Module: `pip install bzr` – or – `apt-get install python-bzrlib`
* Subversion (svn):
    * Binary: `apt-get install subversion`
    * Module: `pip install svn` – or – `apt-get install python-svn`
* Mercurial (hg):
    * Binary: `apt-get install mercurial`
    * Module: `pip install python-hglib` – or – `apt-get install python-hglib`

\**Package manager and/or package names may differ depending on the distribution.*
