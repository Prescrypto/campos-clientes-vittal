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
and make sure that teh parent app points to the correct commit on the submodule.
  