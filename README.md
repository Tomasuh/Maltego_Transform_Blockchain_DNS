# Maltego Explorer of the (Emer|Name)coin name system

This Maltego transform is used to explore the domain and 
IP connections stored in the (domain-)name systems for Namecoin and Emercoin.
The queried relation-database includes both current and past relations, as the blockchain allows the viewing of historical values.

Example graph where the starting node was `pationare.bit`:

![](images/example_exploration.png)

# Setup

## New export of Namecoin and Emercoin name system database

Make sure that `settings.py` has correct credentials for your Namecoin and Emercoin client and that you have enabled JSON RPC on them.
Change working directory to `export_code` and execute `export_main.py`.

## Notes Maltego transform installation
Two transforms needs to installed, one for IP lookup and one for DNS.

The maltego project filename is in the root folder of the project, named `maltego_project.py` 
and the class for IP transform is named `Blockchain_DNS_Transform_IP` and for Domain transform `Blockchain_DNS_Transform_Domain`.

With that, the installation part of [this Maltego documentation](https://docs.maltego.com/support/solutions/articles/15000017605-writing-local-transforms-in-python) should be enough to get through the installation.

## Dependencies

The dependencies in requirements.txt only need to be installed if a regenaration of the database will be done.

# Limitations

This project is more of a POC than an error-free product.
It should however be enough to aid investigations of threat-actors utilizing the name system of Emercoin and Namecoin.
