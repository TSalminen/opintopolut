# -*- coding: utf-8 -*-
"""
Created on Fri Jun  5 08:38:37 2020

@author: Tuukka
"""

import pandas as pd
import re

def poistaIdDuplikaatit(df, bg):
    if 'duplicate' not in df.columns:
        df = pd.merge(df, bg[['studentId', 'duplicate']], how="left", on="studentId")
        df = df.loc[df['duplicate'] == False]
        df.drop(columns=['duplicate'], inplace = True)
        return df
    
    df = df.loc[df['duplicate'] == False]
    return df


def meitsi(df):    
    """ Rajaa DataFramen omiin suorituksiin """
    
    omat = pd.read_csv("../aputiedostot/omat_suoritukset.csv", encoding = "ISO-8859-1")
    
    omat['date'] = pd.to_datetime(omat['date']).apply(lambda x: x.date())
    df['date'] = pd.to_datetime(df['date']).apply(lambda x: x.date())
    
    mahdollisetIdt = df['studentId'].unique()
    omaId = False
    
    for i, r in omat.iterrows():
        for sar in omat.columns:
            if sar != "isModule":
                rajattu = df.loc[df[sar] == r[sar]]
                if len(rajattu) > 0:
                    mahdollisetIdt = [x for x in rajattu['studentId'] if x in mahdollisetIdt]
                if len(mahdollisetIdt) == 1:
                    omaId = mahdollisetIdt[0]
                    break
        if omaId: break
    
    if omaId:
        print("OmaId löytyi, palautetaan df")
        omadf = df.loc[df['studentId'] == omaId]
        # print(omadf.head())
        # omadf.to_csv(hakemisto+'meitsi.csv', index=False)
        # omadf.to_excel(hakemisto+'meitsi.xlsx', index=False)
        return omadf    
    else:
        raise Exception("Virhe rajaa.meitsi(): omaa Id:tä ei löydy.")


def bg_sarakkeen_mukaan(df, bg, sarake=None, rajausehto=None):
    if sarake in df.columns:
        df = df.loc[df[sarake] == rajausehto]    
        return df
    
    # print()
    # print(len(df))
    df = pd.merge(df, bg[['studentId', sarake]], how="left", on="studentId")
    # print(len(df))
    # print()
    df = df.loc[df[sarake] == rajausehto]
    df.drop(columns=[sarake], inplace=True)
    return df


def koulutusohjelma(df, bg, rajattavaohjelma=None):
    df = bg_sarakkeen_mukaan(df, bg, sarake='koulutusohjelma', rajausehto=rajattavaohjelma)
    return df

def aloituslukuvuosi(df, bg, lukuvuosi=None):
    df = bg_sarakkeen_mukaan(df, bg, sarake='aloitusvuosi', rajausehto=lukuvuosi)
    return df


def aloituskuukaudet(df, bg, minimi=7, maksimi=9):
    if 'aloituskuukausi' in df.columns:
        df = df.loc[(df['aloituskuukausi'] >= minimi) & (df['aloituskuukausi'] <= maksimi)]
        return df
    
    df = pd.merge(df, bg[['studentId', 'aloituskuukausi']], how="left", on="studentId")
    df = df.loc[(df['aloituskuukausi'] >= minimi) & (df['aloituskuukausi'] <= maksimi)]
    df.drop(columns=['aloituskuukausi'], inplace=True)
    return df

def poista_uudemmat_suoritukset(df):
    """ Kesken. Poistaa myös kaikki osasuoritukset ja vaihtuvasisältöiset kurssit """
    df = df.sort_values(['studentId', 'date', 'isModule', 'coursecode', 'course'])
    df = df.drop_duplicates(subset=['studentId', 'coursecode', 'course', 'gradeSimple', 'op'])
    return df


def tutkintoon_asti(df, tutkinto=None):
    if tutkinto == None:
        print("tutkintoon_asti: ei annettua tutkintoa")
        return df
        
    if tutkinto == "kandi": ehto = 'andidaatti'
    elif tutkinto == "maisteri": ehto = 'maisteri'
    else:
        print("virhe tutkintoon_asti:", tutkinto)
        return df
    
    # regex = "("+ehto+"\s|"+ehto+"$)"
    regex = "andidaatti"
    
    maxdatedf = df.groupby('studentId').max()
    maxdatedf.reset_index(inplace=True)
    maxdatedf.rename(columns={'date': 'maxdate'}, inplace=True)
    df = df.merge(maxdatedf[['studentId','maxdate']], how="left", on="studentId")
    
    kandiloc = df.loc[(df['isModule']) & (df['course'].str.contains(regex))]
    kandiloc.rename(columns={'date': 'kandidate'}, inplace=True)
    df = pd.merge(df, kandiloc[['studentId', 'kandidate']], how="left", on="studentId")
    
    df.loc[df['kandidate'].notnull(), 'maxdate'] = df['kandidate']    
    df = df.loc[df['date'] <= df['maxdate']]    
    # df.drop(columns=['kandidate', 'maxdate'], inplace=True)
    
    return df


def kasviskandi12(df, bg):
    # hakemisto = "../data_v3/"
    # dftiedosto = "dataset.csv"
    # bgtiedosto = "student_background.csv"
    
    # df = pd.read_csv(hakemisto+dftiedosto, delimiter=",") #, encoding = "ISO-8859-1"
    # print(df.head())
    
    # bg = pd.read_csv(hakemisto+bgtiedosto, delimiter=",") #, encoding = "ISO-8859-1"
    # print(bg.head())
    
    # print(bg['koulutusohjelma'].unique())
    # print(len(df))
    df = pd.merge(df, bg, how="left", on="studentId")
    # print(len(df))
    # print(df.head())
    # print(df.columns)
    # print(len(df), len(df['studentId'].unique()))
    
    df = df.loc[df['koulutusohjelma'] == 'Kasvatustieteet (yleinen ja aikuiskasvatustiede)']
    
    print(len(df), len(df['studentId'].unique()))
    df = df.loc[df['aloitusvuosi'] == "Lv 2012-2013"]
    print(len(df), len(df['studentId'].unique()))
    df = df.loc[df['aloituskuukausi'] >= 7]
    print(len(df), len(df['studentId'].unique()))
    df = df.loc[df['aloituskuukausi'] <= 9]
    print(len(df), len(df['studentId'].unique()))
    
    maxdatedf = df.groupby('studentId').max()
    maxdatedf.reset_index(inplace=True)
    maxdatedf.rename(columns={'date': 'maxdate'}, inplace=True)
    df = pd.merge(df, maxdatedf[['studentId','maxdate']], how="left", on="studentId")
    
    kandiloc = df.loc[(df['isModule'] == True) & (df['course'].str.contains('andidaat'))]
    kandiloc.rename(columns={'date': 'kandidate'}, inplace=True)
    df = pd.merge(df, kandiloc[['studentId', 'kandidate']], how="left", on="studentId")
    
    df.loc[df['kandidate'].notnull(), 'maxdate'] = df['kandidate']
    
    df = df.loc[df['date'] <= df['maxdate']]
    
    df.drop(columns=['kandidate', 'maxdate'], inplace=True)
    
    print(len(df), len(df['studentId'].unique()))
    
    print()
    
    return df
    
    
    
    # df['kandi'] = (df['isModule'] == True) & (df['course'].str.contains('andidaat'))
    # print(df['kandi'].head())
    # print(df['kandi'].unique())
    
    # print(df.groupby('kandi').count())
    
    
    # df.to_csv(hakemisto+"dataset_kasviskandit12.csv", index=False)