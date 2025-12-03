import os, sys
sys.path.append(os.path.pardir)
from my_app import create_app
from my_app.config import ProductionConfig

app=create_app()
#app.config.from_object("my_app.config.ProductionConfig")


if __name__=='__main__':
   app.run()