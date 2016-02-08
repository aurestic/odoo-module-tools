Odoo Module Tools
=================

About
-----

This repository aims to offer a faster way to manage and deploy all the non-official *OpenERP/Odoo* modules.


Installation
------------

The recommended installation way is to clone this repository under your Odoo's **data_path**, this way it will be able to upgrade itself. Assuming that you are logged as **root** user and that the service is launched by the **odoo** user (who also must have his own $HOME directory), the next commands will do it:

```
# su - odoo -c "mkdir -p ~/.local/share/Odoo/repositories/8.0"
# su - odoo -c "git clone https://github.com/crimoniv/odoo-module-tools -b 8.0 ~/.local/share/Odoo/repositories/8.0/odoo_module_tools
```

Once the repository is completely cloned, its absolute path must be included in the **addons_path** parameter, in you *OpenERP/Odoo*'s config file (e.g. `/etc/odoo/openerp-server.conf`).

```
addons_path = <path1>,<path2>,/home/odoo/.local/share/Odoo/repositories/8.0/odoo_module_tools
```

\**If the previous parameter does not exists, it is safe to declare it with only one path.*


Included Modules
----------------

addon | version | summary
--- | --- | ---
[repository_management](repository_management/)* | 8.0.0.1 | Manage external repositories.
[module_external](module_external/)* | 8.0.0.1 | Upload and install modules from external sources.

\**It is highly discouraged to install the same module using both ways.*


Disclaimer
----------

* I do not assume any responsibility for any consequence of using the modules found in this repository.
* These modules are deployed with the purpose of helping developers to develop and test modules in a faster and easier way.
* It is highly discouraged their usage in a production environments, for security and stability reasons.
* Experienced and skilled users may use them for other purposes at their own risk.
