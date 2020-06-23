# -*- coding: utf-8 -*-
"""
Created on Sun Jun 14 17:50:59 2020

@author: Tuukka
"""
import datetime
import numpy as np
import math

def seuraava_periodi(d, tyyppi="float"):
    lv_alkaa = lv_alkamisvuosi_datesta(d)
    periodi = paivamaaran_periodi(d)
    
    lv_siirretty, p_siirretty = siirra_tuple(lv_alkaa, periodi, 1)
    
    if tyyppi == "float":
        return lv_siirretty + p_siirretty / 10
        # if periodi == 4:
        #     return lv_alkaa+1 + 0.1
        # return lv_alkaa + (periodi+1) / 10
    
    if tyyppi == "alkamisPvm":
        pdict = make_pdict(lv_siirretty)
        return pdict[p_siirretty][0]
    
def lv_alkamisvuosi_datesta(d):
    if d.month <= 8:
        return d.year - 1
    return d.year

def paivamaaran_periodi(d):
    lv = lv_alkamisvuosi_datesta(d)
    pdict = make_pdict(lv)
    
    for k, v in pdict.items():
        if d >= v[0] and d <= v[1]:
            return k
        
def siirra_tuple(lv, p, delta):
    p_lkm = 5
    p_tot = lv * p_lkm + p
    p_tot_d = p_tot + delta
    p_tot_d -= 1
    lv_new_float = p_tot_d / p_lkm
    lv_new = int(lv_new_float)
    p_new = p_tot_d - lv_new * p_lkm + 1
    return (lv_new, p_new)

def siirra_float(f, delta):
    lv = int(f)
    p = f - lv
    lv_new, p_new = siirra_tuple(lv, p, delta)
    return lv_new + p_new / 10

def make_pdict(vuosi):
    return {1: [datetime.datetime(vuosi, 9, 1), datetime.datetime(vuosi, 10, 26)],
            2: [datetime.datetime(vuosi, 10, 27), datetime.datetime(vuosi+1, 1, 13)],
            3: [datetime.datetime(vuosi+1, 1, 14), datetime.datetime(vuosi+1, 3, 9)],
            4: [datetime.datetime(vuosi+1, 3, 10), datetime.datetime(vuosi+1, 5, 30)],
            5: [datetime.datetime(vuosi+1, 5, 31), datetime.datetime(vuosi+1, 8, 31)]}


def lukuvuosiStr(d):
    lv_alkaa = lv_alkamisvuosi_datesta(d)
    return "".join(["Lv ", str(lv_alkaa), "-", str(lv_alkaa+1)])

def vuosiperiodi(d, tyyppi="float"):
    lv_alkaa = lv_alkamisvuosi_datesta(d)    
    periodi = paivamaaran_periodi(d)
    
    if tyyppi == "tuple":
        return (lv_alkaa, periodi)
    
    return lv_alkaa + periodi / 10


def lisaa_opiskelulukuvuosi(df):
    df['opiskelulukuvuosi'] = df['suoritusvuosiperiodi'].astype(int) - df['aloitusvuosiperiodi'].astype(int) + 1
    df.loc[df['opiskelulukuvuosi'] < 1, 'opiskelulukuvuosi'] = 0
    return df

def lisaa_opiskeluvuosi(df):
    df['opiskeluvuosi'] = df['suoritusvuosiperiodi'] - df['aloitusvuosiperiodi'] + 1
    df['opiskeluvuosi'] = np.floor(df['opiskeluvuosi']).astype(int)
    df.loc[df['opiskeluvuosi'] < 1, 'opiskeluvuosi'] = 0
    return df

def lisaa_opiskeluperiodi(df):
    df['temp_1s'] = df['suoritusvuosiperiodi'].astype(int) * 5 + (df['suoritusvuosiperiodi'] - df['suoritusvuosiperiodi'].astype(int)) * 10
    df['temp_2a'] = df['aloitusvuosiperiodi'].astype(int) * 5 + (df['aloitusvuosiperiodi'] - df['aloitusvuosiperiodi'].astype(int)) * 10
    
    df['opiskeluperiodi'] = df['temp_1s'] - df['temp_2a'] + 1
    df.loc[df['opiskeluperiodi'] < 1, 'opiskeluperiodi'] = 0
    
    df.drop(columns=['temp_1s', 'temp_2a'], inplace=True)
    return df

def lisaa_opiskeluvuosiperiodi(df):
    df['opiskeluvuosiperiodi'] = df['opiskeluvuosi'] + (df['opiskeluperiodi'] - (df['opiskeluvuosi'] - 1) * 5) / 10
    df.loc[df['opiskeluvuosiperiodi'] < 1, 'opiskeluvuosiperiodi'] = 0
    return df

def kumulatiivinen_opdf(df, lower_limit=0, upper_limit=0, aloita_nollasta=False):
    lower_limit = muuta_float_periodeiksi(lower_limit)
    upper_limit = muuta_float_periodeiksi(upper_limit)
    
    res = df[['studentId']]
    res = res.drop_duplicates()
    res = res.set_index('studentId')
    
    aloitusperiodi = 0
    if aloita_nollasta:
        aloitusperiodi = 1
    
    for i in range(lower_limit, upper_limit+1):
        df2 = df.loc[(df['opiskeluperiodi'] >= aloitusperiodi) & (df['opiskeluperiodi'] <= i) & (~df['isModule']) & (df['gradeSimple'] != 'Hylätty')]
        df2 = df2.groupby(['studentId']).sum()[['op']]
        # df2.reset_index(inplace=True)
        df2.rename(columns={'op':str(muuta_periodit_floatiksi(i))}, inplace=True)        
        res = res.merge(df2, how='left', on='studentId')
    
    res = res.fillna(0)
    
    # if aloita_nollasta:
    #     df2 = df.loc[df['opiskeluperiodi'] <= 0]
    #     df2 = df2.groupby(['studentId']).sum()[['op']]
    #     # df2.reset_index(inplace=True)
    #     df2.rename(columns={'op':'lahtopisteet'}, inplace=True)        
    #     res = res.merge(df2, how='left', on='studentId')
    #     res = res.fillna(0)
    #     for i in range(lower_limit, upper_limit+1):
    #         res[str(muuta_periodit_floatiksi(i))] = res[str(muuta_periodit_floatiksi(i))] - res['lahtopisteet']
            
    #     res.drop(columns=['lahtopisteet', '0'], inplace=True)
        
    return res

def muuta_float_periodeiksi(x):
    if x == 0: return 0
    vuodet = (int(x)-1) * 5
    periodit = (x - int(x)) * 10
    return int(vuodet + periodit)

def muuta_periodit_floatiksi(x):
    vuosia = math.ceil(x / 5)
    if vuosia == 0: return 0
    periodeja = x - (vuosia-1) * 5
    return vuosia + periodeja / 10