To deploy this submodule to heroku verify that you have made a commit in the campos-clientes-vittal and it have been reflected properly in odooku!

* If After deployment in heroku sometimes you get something like  "...upper modiule must be a module..." deploy again the aplication.

* If you made changes in models or forms , you need to login via bash in heroku:

heroku run bash -a erste-staging

and the run:

odooku database update (this command take a while)

