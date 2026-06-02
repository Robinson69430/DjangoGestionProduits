Voici les prérequis :
Python 3.10+ 
Je recommande VS Code mais tout autre IDE fait pour django sont possible. Dans le cas où vous utilisez VS Code, téléchargez l'extension VS Code : Python 

L'installation : 

Cloner le projet :
git clone https://github.com/Robinson69430/DjangoGestionProduits/

Ensuite il faut creer l'environnement virtuel :

cd DjangoGestionProduits

python -m venv .venv

Puis activer votre environnement :
.venv\Scripts\activate

Ensuite :
pip install django

Maintenant il faut appliquer les migrations : 
python manage.py migrate

Enfin vous pouvez lancer le projet grâce à : 
python manage.py runserver
