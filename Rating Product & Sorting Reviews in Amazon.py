###################################################
# PROJE: Rating Product & Sorting Reviews in Amazon
###################################################

###################################################
# İş Problemi
###################################################

# E-ticaretteki en önemli problemlerden bir tanesi ürünlere satış sonrası verilen puanların doğru şekilde hesaplanmasıdır.
# Bu problemin çözümü e-ticaret sitesi için daha fazla müşteri memnuniyeti sağlamak, satıcılar için ürünün öne çıkması ve satın
# alanlar için sorunsuz bir alışveriş deneyimi demektir. Bir diğer problem ise ürünlere verilen yorumların doğru bir şekilde sıralanması
# olarak karşımıza çıkmaktadır. Yanıltıcı yorumların öne çıkması ürünün satışını doğrudan etkileyeceğinden dolayı hem maddi kayıp
# hem de müşteri kaybına neden olacaktır. Bu 2 temel problemin çözümünde e-ticaret sitesi ve satıcılar satışlarını arttırırken müşteriler
# ise satın alma yolculuğunu sorunsuz olarak tamamlayacaktır.

###################################################
# Veri Seti Hikayesi
###################################################

# Amazon ürün verilerini içeren bu veri seti ürün kategorileri ile çeşitli metadataları içermektedir.
# Elektronik kategorisindeki en fazla yorum alan ürünün kullanıcı puanları ve yorumları vardır.

# Değişkenler:
# reviewerID: Kullanıcı ID’si
# asin: Ürün ID’si
# reviewerName: Kullanıcı Adı
# helpful: Faydalı değerlendirme derecesi
# reviewText: Değerlendirme
# overall: Ürün rating’i
# summary: Değerlendirme özeti
# unixReviewTime: Değerlendirme zamanı
# reviewTime: Değerlendirme zamanı Raw
# day_diff: Değerlendirmeden itibaren geçen gün sayısı
# helpful_yes: Değerlendirmenin faydalı bulunma sayısı
# total_vote: Değerlendirmeye verilen oy sayısı

import pandas as pd
import numpy as np
import math
import scipy.stats as st
pd.set_option('display.width', 100)
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', 100)
pd.set_option('display.float_format', lambda x: '%.5f' % x)

df = pd.read_csv("hafta3_measurement_problems/case1/amazon_review.csv")
df.head()
df["overall"].mean()
###################################################
# Tarihe Göre Ağırlıklı Puan Ortalamasını Hesaplayınız.
###################################################

def avarege_time(df, a1=0.3 ,a2=0.25,a3=0.20,a4=0.10,a5=0.075,a6=0.075):
    return ((a1 * (df.loc[df["day_diff"] <= 30, "overall"].mean())) + \
            (a2 * (df.loc[(df["day_diff"] > 30) & (df["day_diff"] <= 90), "overall"].mean())) + \
            (a3 * (df.loc[(df["day_diff"] > 90) & (df["day_diff"] <= 180), "overall"].mean())) + \
            (a4 * (df.loc[(df["day_diff"] > 180) & (df["day_diff"] <= 365), "overall"].mean())) + \
            (a5 * (df.loc[(df["day_diff"] > 365) & (df["day_diff"] <= 720), "overall"].mean())) + \
            (a6 * (df.loc[(df["day_diff"] > 720) & (df["day_diff"] <= 1064), "overall"].mean()))).mean()


avarege_time(df)




# Ağırlıklandırılmış puanlamada her bir zaman diliminin ortalamasını karşılaştırıp yorumlayınması.


def avarege_time_print(df):
    print (f"""1: {df.loc[df["day_diff"] <= 30, "overall"].mean()} 
             2: {df.loc[(df["day_diff"] > 30) & (df["day_diff"] <= 90), "overall"].mean()} 
             3: {df.loc[(df["day_diff"] > 90) & (df["day_diff"] <= 180), "overall"].mean()}   
             4: {df.loc[(df["day_diff"] > 180) & (df["day_diff"] <= 365), "overall"].mean()}
             5: {df.loc[(df["day_diff"] > 365) & (df["day_diff"] <= 720), "overall"].mean()} 
             6: {df.loc[(df["day_diff"] > 720) & (df["day_diff"] <= 1064), "overall"].mean()}""")


avarege_time_print(df)


# Görev 2: Ürün için Ürün Detay Sayfasında Görüntülenecek 20 Review'i Belirlenmesi.

df.sort_values(by="helpful_yes", ascending=False)["reviewerID"].head(20)

# helpful_no Değişkenini Üretilmesi
df["helpful_no"] = df["total_vote"] - df["helpful_yes"]



# score_pos_neg_diff, score_average_rating ve wilson_lower_bound Skorlarını Hesaplayıp Veriye Eklnmesi


def wilson_lower_bound(up, down, confidence=0.95):
    """
    Wilson Lower Bound Score hesapla

    - Bernoulli parametresi p için hesaplanacak güven aralığının alt sınırı WLB skoru olarak kabul edilir.
    - Hesaplanacak skor ürün sıralaması için kullanılır.
    - Not:
    Eğer skorlar 1-5 arasıdaysa 1-3 negatif, 4-5 pozitif olarak işaretlenir ve bernoulli'ye uygun hale getirilebilir.
    Bu beraberinde bazı problemleri de getirir. Bu sebeple bayesian average rating yapmak gerekir.

    Parameters
    ----------
    up: int
        up count
    down: int
        down count
    confidence: float
        confidence

    Returns
    -------
    wilson score: float

    """
    n = up + down
    if n == 0:
        return 0
    z = st.norm.ppf(1 - (1 - confidence) / 2)
    phat = 1.0 * up / n
    return (phat + z * z / (2 * n) - z * math.sqrt((phat * (1 - phat) + z * z / (4 * n)) / n)) / (1 + z * z / n)

def score_poss_neg_diff(up,down):
    return up-down

def score_average_rating(up, down):
    if 0==up+down:
        return 0
    else:
        return (up-down)/(up+down)



df["score_pos_neg_diff"] = df.apply(lambda x:score_poss_neg_diff(x["helpful_yes"], x["helpful_no"]), axis=1)

df["score_average_rating"] =df.apply(lambda x:score_average_rating(x["helpful_yes"], x["helpful_no"]), axis=1)

df["wilson_lower_bound"] = df.apply(lambda x: wilson_lower_bound(x["helpful_yes"], x["helpful_no"]), axis=1)



df["wilson_lower_bound"] = df.apply(lambda x: wilson_lower_bound(x["helpful_yes"], x["helpful_no"]), axis=1)


comment = pd.DataFrame()
comment["score_pos_neg_diff"] = df.sort_values("score_pos_neg_diff", ascending=False).head(20)["reviewerID"]
comment["score_average_rating"] = df.sort_values("score_average_rating", ascending=False).head(20)["reviewerID"]
comment["wilson_lower_bound"] = df.sort_values("wilson_lower_bound", ascending=False).head(20)["reviewerID"]

df.sort_values("wilson_lower_bound", ascending=False).head(20)["reviewerID"]
