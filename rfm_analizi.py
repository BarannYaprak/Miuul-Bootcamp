###############################################################
# RFM ile Müşteri Segmentasyonu (Customer Segmentation with RFM)
###############################################################

###############################################################
# İş Problemi (Business Problem)
###############################################################
# FLO müşterilerini segmentlere ayırıp bu segmentlere göre pazarlama stratejileri belirlemek istiyor.
# Buna yönelik olarak müşterilerin davranışları tanımlanacak ve bu davranış öbeklenmelerine göre gruplar oluşturulacak..

###############################################################
# Veri Seti Hikayesi
###############################################################

# Veri seti son alışverişlerini 2020 - 2021 yıllarında OmniChannel(hem online hem offline alışveriş yapan) olarak yapan müşterilerin geçmiş alışveriş davranışlarından
# elde edilen bilgilerden oluşmaktadır.

# master_id: Eşsiz müşteri numarası
# order_channel : Alışveriş yapılan platforma ait hangi kanalın kullanıldığı (Android, ios, Desktop, Mobile, Offline)
# last_order_channel : En son alışverişin yapıldığı kanal
# first_order_date : Müşterinin yaptığı ilk alışveriş tarihi
# last_order_date : Müşterinin yaptığı son alışveriş tarihi
# last_order_date_online : Muşterinin online platformda yaptığı son alışveriş tarihi
# last_order_date_offline : Muşterinin offline platformda yaptığı son alışveriş tarihi
# order_num_total_ever_online : Müşterinin online platformda yaptığı toplam alışveriş sayısı
# order_num_total_ever_offline : Müşterinin offline'da yaptığı toplam alışveriş sayısı
# customer_value_total_ever_offline : Müşterinin offline alışverişlerinde ödediği toplam ücret
# customer_value_total_ever_online : Müşterinin online alışverişlerinde ödediği toplam ücret
# interested_in_categories_12 : Müşterinin son 12 ayda alışveriş yaptığı kategorilerin listesi


import datetime as dt
import pandas as pd
pd.set_option('display.max_columns', None)
# pd.set_option('display.max_rows', None)
pd.set_option('display.float_format', lambda x: '%.3f' % x)


def on_hazirlik(path):
    """
    Pandas ile dosyayı okur ve tarih değişkenelerini uygun hale getirir flo datasetine özel bir fonksiyondur
    :param path: Okunacak dosyanın yolu
    :return: df
    """
    df = pd.read_csv(path)
    df.dropna(inplace=True)
    dates = ["first_order_date", "last_order_date", "last_order_date_online", "last_order_date_offline"]
    for column in dates:
        df[column] = df[column].apply(pd.to_datetime)

    df["total_order"] = df["order_num_total_ever_online"] + df["order_num_total_ever_offline"]
    df["total_customer_value"] = df["customer_value_total_ever_online"] + df["customer_value_total_ever_offline"]
    df = df[df["total_order"] > 1]
    return df

df = on_hazirlik("flo_data_20k.csv")



def rfm(df):
    #RFM Metriklerinin Hesaplanması

    df["last_order_date"].max()
    today_date = dt.datetime(2021, 6, 2)
    type(today_date)
    rfm = df.groupby("master_id").agg({"last_order_date": lambda order_date: (today_date - order_date).dt.days,
                                       "total_order": lambda order: order.sum(),
                                       "total_customer_value": lambda customer_value: customer_value.sum()})

    rfm.columns = ["recency", "frequency", "monetary"]



    # RF ve RFM Skorlarının Hesaplanması

    rfm["recency_score"] = pd.qcut(rfm["recency"], q=5, labels=[5, 4, 3, 2, 1])
    rfm["frequency_score"] = pd.qcut(rfm["frequency"].rank(method="first"), q=5, labels=[1, 2, 3, 4, 5])
    rfm["monetary_score"] = pd.qcut(rfm["monetary"], q=5, labels=[1, 2, 3, 4, 5])
    rfm["rf_score"] = (rfm['recency_score'].astype(str) +
                       rfm['frequency_score'].astype(str))

    # RF Skorlarının Segment Olarak Tanımlanması

    seg_map = {
        r'[1-2][1-2]': 'hibernating',
        r'[1-2][3-4]': 'at_Risk',
        r'[1-2]5': 'cant_loose',
        r'3[1-2]': 'about_to_sleep',
        r'33': 'need_attention',
        r'[3-4][4-5]': 'loyal_customers',
        r'41': 'promising',
        r'51': 'new_customers',
        r'[4-5][2-3]': 'potential_loyalists',
        r'5[4-5]': 'champions'
    }

    rfm["segment"] = rfm['rf_score'].replace(seg_map, regex=True)
    return rfm

rfm = rfm(df)

def select_crm(df,segments,cat,path,save=False):
    """
    Segmentlere ayrılmış müşterilerden istediğimiz segmentler ve istediğimiz kategorilerden alışveriş yapan müşterilerin olduğu
    bir dataframe return eder istenirse bu dataframe csv dosyası olarak kaydedilebilir
    :param df: Verilerin olduğu dataframe
    :param segments: sorgulanmak istenen müşteri segmentleri
    :param cat: Müşerilerin alışveriş yaptığı kategoriler
    :param path: csv dosyasının kaydedileceği yol
    :param save: dosya kaydedilsin mi parametresi
    :return: df
    """

    rfm = df[segments]
    rfm.reset_index()
    df_cat = df[df["interested_in_categories_12"].str.contains(cat)]
    df_customers = pd.merge(rfm, df_cat, on="master_id")
    df_customers= df_customers[["master_id"]]

    if save:
        df_customers.to_csv(path)

    return df_customers

select_crm()