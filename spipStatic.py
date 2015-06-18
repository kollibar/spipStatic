#! /usr/bin/env python3
import csv,re,os.path
from collections import OrderedDict

from postTraitement import postTraitement,traitementSecurite
from balises import LISTE_BALISES,baliseGenerique


def loadDataCSV(fichier):
    fichierData=open(FICHIER,'r')
    dataCsv=csv.reader(fichierData,dialect=csv.Sniffer)
    entete=None
    data=[]
    for ligne in dataCsv:
        if entete==None:
            entete=ligne
        else:
            dictLigne={}
            if len(ligne)>len(entete):
                raise IOError('ligne d\'entete comprenant moins de données que certaines lignes')
            for i in range(len(ligne)):
                dictLigne[entete[i]]=ligne[i]
            data.append(dictLigne)
    fichierData.close()
    return data

FICHIER='./data.csv'

MODELE='./modele.html'


data=loadDataCSV(FICHIER)

fModele=open(MODELE,'r').read()

# Lecture du fichier modele et extraction de la liste de variable (format #VARIABLE)
listeComplete=re.findall('#[A-Z_][A-Z_0-9]*',fModele)
listeVariable=listeComplete
##for variable in listeComplete:
##    if variable not in listeVariable:
##        listeVariable.append(variable)

### determine la position de chaque variable
##dictPos=OrderedDict()
##i=0
##for var in listeComplete:
##    i=fModele.find(var,i)
##    dictPos[var]=i
##    i+=1

for ligne in data:
    valid=True
    if 'invisible' in ligne.keys():
        if ligne['invisible'].lower in ['true','x']:
            valid=False

    #vérifie la validité du nom de fichier
    if 'nom_fichier' not in ligne.keys():
        valid=False
    else:
        if ligne['nom_fichier']=='':
            valid=False

    if valid: # si la ligne est valide, traitement
        fichier=fModele

        i=0
        # remplacement de la liste des variables
        varNum=0
        while varNum<len(listeVariable):
            var=listeVariable[varNum]
            n=1
            j=fichier.find(var,i)

            if fichier[j+len(var)]=='{':
                k=fichier.find('}',j+len(var))
                param=tuple(fichier[j+len(var)+1:k-1].split(','))
            else:
                k=j+len(var)
                param=None
            
            tv=0 # tv=0 -> traitement normal, tv=1 -> sans postTraitement, tv=2 -> sans traitement (ni sécu, ni postTraitement)
            if fichier[j+len(var)]=='*':
                if fichier[j+len(var)+1]=='*':
                    tv=2
                else:
                    tv=1
            k+=tv

            # recherche de la valeur de la balise
            if var[1:].lower() in ligne.keys(): # variable trouvé dans la ligne en cours
                valeur=ligne[var[1:].lower()]
            elif var[1:].lower() in LISTE_BALISES:
                if param==None:
                    valeur=baliseGenerique(var[1:].lower())
                else:
                    valeur=baliseGenerique(var[1:].lower(),*args)
            else:
                valeur=var # si pas trouvé, pas de remplacement

            # application des traitements sur la balise (traitement sécurité et postTraitement)
            if tv<2:
                valeur=traitementSecurite(valeur)
            if tv<1:
                valeur=postTraitement(valeur)

            if fichier[j+len(var)]=='|': # ajout des filtres
                pass # A FAIRE


            if fichier[j-1]=='(': #TRAITEMENT DES BLOCS [  (#BALISE)   ]
                deb=fichier.rfind('[',0,j)
                d=fichier.rfind(']',0,j)
                while d>deb:
                    deb=fichier.rfind('[',0,deb)
                    d=fichier.rfind(']',0,d)
                    if deb==-1:
                        raise IOError('erreur [] [ manquant')
                fin=fichier.find(']',k)
                f=fichier.find('[',k)
                while f<fin and f!=-1:
                    fin=fichier.find(']',fin)
                    f=fichier.find('[',f)
                    if fin==-1:
                        raise IOError('erreur [] ] manquant')

                if valeur!='': # si pas vide, on garde le bloc
                    i=j+len(valeur)-2 # actualisation position debut recherche prochaine balise
                    valeur=fichier[deb+1:j-1]+valeur+fichier[k+1:fin]
                else: # si vide on supprime le bloc
                    i=deb # actualisation position debut recherche prochaine balise
                    # verifie la présence de balise dans la zone à supprimer et incrémenter d'autant n pour les sauter !!
                    if varNum+1<len(listeVariable):
                        while fichier.find(listeVariable[varNum+n],k,fin)!=-1:
                            n+=1
                            if varNum+n==len(listeVariable):
                                break
                    
                j=deb
                k=fin+1
            else: # si pas de bloc
                i=j+len(valeur) # actualisation position debut recherche prochaine balise

            #calcul du decalage de position des variables suivantes
            decalage=j+len(valeur)-k

            # modifie la variable
            fichier=fichier[:j]+valeur+fichier[k:]
            varNum+=n
            
##            #actualise la position de toutes les variables
##            for elt in dictPos.keys():
##                if dictPos[elt]>=k:
##                    dictPos[elt]+=decalage

        # enregistrement du fichier
        print(ligne['nom_fichier'])
        fCree=open(ligne['nom_fichier'],'w')
        fCree.write(fichier)
        fCree.close()
