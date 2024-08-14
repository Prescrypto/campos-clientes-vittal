To deploy this submodule to heroku verify that you have made a commit in the campos-clientes-vittal and it have been reflected properly in odooku!

* If After deployment in heroku sometimes you get something like  "...upper package must be a module..." deploy again the aplication.

* If you made changes in models or forms , you need to login via bash in heroku:

heroku run bash -a erste-staging

and the run:

odooku database update (this command take a while)

This update database changes, but you need to reflect the changes
in the correspondent App. via:

https://erste-staging.herokuapp.com/

-> Applications, select the correct app and then press "Update" button

this operation reflects th changes.

* Note: 

This development is based on a main Module: "Odoo" and various submodules, like "campos_clientes_vittal", when you made changes on a submodule made sure you reflect the submodule change on the parent app.
and make sure that the parent app points to the correct commit on the submodule.


* Vagrant Ambient:

cd /vagrant

source virtualenv/bin/activate

cd odoo/

./odoo-bin -r vagrant -w vagrant -d db_odoo --db_host 127.0.0.1 --addons-path=addons,prescrypto/campos_clientes_vittal --dev=all -u campos_clientes_vittal,account,contacts,sale,product,base,l10n_mx,contract,models_export_vittal,base,board,account,crm --log-request --log-response --log-web --log-level=debug --logfile=/vagrant/logs/prescrypto_odoo.log --logrotate

cd /mnt/prescrypto-odoo

./odoo-bin -r odoo -w odoo -d db_odoo --db_host db --addons-path=addons,prescrypto/campos_clientes_vittal,prescrypto/rest_api --dev=all -u campos_clientes_vittal,account,contacts,sale,product,base,l10n_mx,contract,models_export_vittal,base,board,account,crm,rest_api --log-request --log-response --log-web --log-level=debug --logfile=prescrypto_odoo.log --logrotate


deactivate

http://192.168.50.4:8069/


\                    <field name="recurring_payment_days"/>

* Extra Modules
add module journal cancel to enable invoice cancelation


docker compose exec web bash

docker compose up -d --build

admin / admin


## Install Requird Odoo modules

1 - Contacts Directory	
2 - Timesheets	
3 - Project	
4 - Forum	
5 - Discuss	
6 - CRM	
7 - Sales	
8 - Dashboards	
9 - Invoicing	
10 - Website Builder	
11 - Accounting and Finance	
12 - Employee Directory	
13 - REST API	Andrey Sinyanskiy SP	10.0.1.3.0	Installed
14 - Online Events	
15 - Calendar	
16 - Campos de Clientes	

## Run using configuration file
cd /mnt/prescrypto-odoo;
./odoo-bin -c /etc/odoo/odoo.conf


## Updating modules
cd /mnt/prescrypto-odoo
./odoo-bin -c /etc/odoo/odoo.conf -u campos_clientes_vittal,account,contacts,sale,product,base,l10n_mx,contract,models_export_vittal,base,board,account,crm,rest_api


## Logs

cd /mnt/prescrypto-odoo;
tail -f prescrypto_odoo.log


## Backup Database
pg_dump -U odoo -h db db_odoo > odoo10_backup.sql

python3 migrate.py --config=/etc/odoo/odoo.conf --database=db_odoo --update=all



docker compose exec web bash 

docker compose exec -u root -ti web bash

pip3 install -r requirements.txt

./odoo-bin -c /etc/odoo/odoo.conf --update=all –stop-after-init


docker compose logs -f  | tee log.txt



docker compose cp d52s4kko2tbtip_2024-08-12_21-21-52.dump db:/latest.dump

docker compose exec -it db pg_restore -U odoo -d db_odoo060724 /latest.dump

docker compose exec -it db pg_restore -U odoo --dbname=d52s4kko2tbtip  --no-owner /latest.dump



docker compose exec -it db psql -U odoo -d postgres
CREATE DATABASE d52s4kko2tbtip;
\q


./odoo-bin -d d52s4kko2tbtip --i18n-overwrite --update=all
