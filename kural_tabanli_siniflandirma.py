import pandas as pd

pd.set_option('display.max_columns', None)
pd.set_option('display.max_row', None)

df = pd.read_csv(r"C:\Users\Hp\Desktop\Miuul Bootcamp\persona.csv")
df.info()
def all_info(df, head=5):
    """
    Datafame'nin betimsel istatistiklerini gösterir
    Parameters
    ----------
    df = arguman olarak aldığı Dataframe

    head = Head sayısı

    Returns
    Betimsel istatistikler
    -------

    """
    print(f"###################### HEAD ###############\n{df.head(head)}")
    print(f"###################### İNFO ###############\n{df.info()}")
    print(f"###################### SHAPE ###############\n{df.shape}")
    print(f"###################### TYPES ###############\n{df.dtypes}")
    print(f"###################### TAİL ###############\n{df.tail(head)}")
    print(f"###################### NA ###############\n{df.isnull().sum()}")
    print(f"###################### DECSRİBE ###############\n{df.describe([0, 0.05, 0.50, 0.95, 0.99, 1]).T}")


all_info(df)


df["SOURCE"].nunique()
df["SOURCE"].value_counts()

df["PRICE"].nunique()
df["PRICE"].unique()
df["PRICE"].value_counts()
df["COUNTRY"].value_counts()
df.groupby("COUNTRY").agg({"PRICE": "sum"})
df["SOURCE"].value_counts()
df.groupby("COUNTRY").agg({"PRICE": "mean"})
df.groupby("SOURCE").agg({"PRICE": "mean"})
df.groupby(["COUNTRY", "SOURCE"]).agg({"PRICE": "mean"})
new = df.groupby([ "COUNTRY", "SOURCE", "SEX", "AGE"]).agg({"PRICE": "mean"})
agg_df = new.sort_values("PRICE", ascending=False)
print(agg_df)
agg_df.reset_index(inplace=True)
agg_df.columns
agg_df["SOURCE"]

label =["15_20", "20_25", "25_35", "35_45", "45_66"]
agg_df["AGE_CAT"] = pd.qcut(agg_df["AGE"], 5, labels=label)
agg_df.groupby("AGE_CAT").agg({"PRICE": "mean"})
agg_df["AGE_CAT"].value_counts()

based = ["_".join(agg_df.loc[i, ['COUNTRY', 'SOURCE', 'SEX', 'AGE_CAT']]) for i in range(len(agg_df))]
type(based)
agg_df["customers_level_based"] = based
agg_df["customers_level_based"].value_counts()

based_df = agg_df.groupby("customers_level_based").agg({"PRICE": "mean"})
based_df.reset_index(inplace=True)


agg_df=df.groupby('customer_based_level').agg({'PRICE':"mean"}) #personaları tekilleştiriyoruz
agg_df.reset_index(inplace=True) #price seğişkeni üst indexte kaldığı için onu da değişkene çeviriyoruz.
agg_df.value_counts() #her personadan 1 adet var.


label =["D", "C", "B", "A"]
based_df["SEGMENT"] = pd.qcut(based_df["PRICE"], 4 ,labels=label)

based_df.groupby("SEGMENT").agg({"PRICE": ["min", "max", "sum"]})

#33 yaşında ANDROID kullanan bir Türk kadını
#35 yaşında IOS kullanan bir Fransız kadını

new_user_1 = "tur_android_female_31_40"

new_user_2 = "fra_ios_female_25_35"

new_user_3="tur_android_female_41_60"

based_df[based_df["customers_level_based"]== new_user_1]["PRICE"]
based_df[based_df["customers_level_based"]== new_user_2]["PRICE"]
based_df[based_df["customers_level_based"]== new_user_3]["PRICE"]