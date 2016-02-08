Repository Management
=====================

Features
--------

* Git, SVN, Bazaar and Mercurial suppport.


Known Issues / Roadmap
----------------------

* SSL compatiblity.
* Test VCS before adding it to **addons_path**.
* Add proper instructions.
* When adding/removing a repo, update only the **addons_path** parameter – not the whole config file.
* Detect identical repos: https://github.com/crimoniv/odoo-module-tools == https://github.com/crimoniv/odoo-module-tools.git
* Directory symlinks are detected as a different repo, even if they are linked to the same base directory.


Requirenments
-------------

* Git (git) (version >= 1.7.0)
    * Binary: apt-get install git
    * Module: pip install gitpython – or – apt-get install python-git
* Bazaar (bzr):
    * Module: pip install bzr – or – apt-get install python-bzrlib
* Subversion (svn):
    * Binary: apt-get install subversion
    * Module: pip install svn – or – apt-get install python-svn
* Mercurial (hg):
    * Binary: apt-get install mercurial
    * Module: pip install python-hglib – or – apt-get install python-hglib
