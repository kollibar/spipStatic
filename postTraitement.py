#! /usr/bin/env python3

def postTraitement(var):
    """procède au traitement des variables avant affichage"""
    # remplacement des fin de ligne
    var=var.replace('\r\n','\n').replace('\r','\n')

    for postTrait in LISTE_POSTTRAITEMENT:
        var=postTrait(var)
    return var

def paragraphisationVariable(var):
    """postTraitement
si un saut de ligne est trouvé ajoute <p></p>"""
    if '\r' in var or '\n' in var:
        var='<p>'+var.replace('\n','</p>\n<p>')+'</p>'
    return var

def protectEmail(var):
    """postTraitement
protège les emails contre le spam"""
    #A FAIRE
    return var

def traitementSecurite(var):
    """applique tous les traitements de sécurités sur une variable"""
    for traitSecu in LISTE_TRAITEMENTSECURITE:
        var=traitSecu(var)
    return var


LISTE_POSTTRAITEMENT=[paragraphisationVariable,protectEmail]
LISTE_TRAITEMENTSECURITE=[]
