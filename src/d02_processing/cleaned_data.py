import pandas as pd

def Clean_OppIns_raw():
    """
    =====================================================
    Function to clean raw data from Opportunity Insights "Geography of Mobility"
    =====================================================

    Raw data ("online_data_tables.xls") must be in data/01_raw


    """
    # This brings in the columns with a multi-indexed column
    county_stats = pd.read_excel('../../data/01_raw/Equality_Opportunity/online_data_tables.xls',
                                 sheet_name='Online Data Table 3',
                                 header=[29, 30])
    # Transposing dataframe to remove first level of multi-indexed column headers
    county_wo_multidx = county_stats.T.reset_index(level=1, drop=True).T

    # Transposing the dataframe changes the datatypes, so here we restore the appropriate
    # columns to floats
    county_mobility = pd.concat([county_wo_multidx.iloc[:, :5],
                                 county_wo_multidx.iloc[:, 5:].astype('float')], axis=1)

    # Adding column "rank_diff" as my definition of a "Mobile" county, and making boolean column
    # 0 is False, meaning a county is NOT considered mobile by my definition. 2804 counties
    # 1 is True, meaning a county IS considered mobile. 337 counties

    county_mobility['rank_diff'] = county_mobility['Absolute Upward Mobility'] - 25
    county_mobility['Target'] = (county_mobility.rank_diff >= 25).astype('int')

    # Padding FIPS code so the formatting will match when it's time to merge with next dataset
    county_mobility['County FIPS Code'] = county_mobility['County FIPS Code'].apply(
        lambda x: str(x).zfill(5))

    # Exporting data as pkl into new notebook for modeling.
    return county_mobility.to_pickle('../../data/02_intermediate/county_mobility_incomeOnly')





def Clean_CountyHealth_raw():
    """
    =====================================================
    Function to clean raw data from County Health Rankings 
    =====================================================

    Raw data ("online_data_tables.xls") must be in data/01_raw


    """

    CH_ranking = pd.read_csv('../../data/01_raw/County_Health_Rankings.csv',
                             dtype={'State code': 'str', 'County code': 'str', 'fipscode': 'str'})

    # Changing County code to string with 3-characters
    CH_ranking['County code'] = CH_ranking['County code'].apply(
        lambda x: str(x).zfill(3))

    # Changing State code to string with 2-characters
    CH_ranking['State code'] = CH_ranking['State code'].apply(
        lambda x: str(x).zfill(2))

    # Changing FIPS code to string with 5-characters
    CH_ranking['fipscode'] = CH_ranking['fipscode'].apply(
        lambda x: str(x).zfill(5))
    
    #Filter out State and Country level data = 298920 rows remaining
    county_only = CH_ranking.loc[(CH_ranking['County code'] != '000') & (CH_ranking['fipscode'] != '00nan') ]
    
    county_measures = pd.DataFrame(county_only.groupby(by=['fipscode', 'Measure name'])['Raw value'].mean())
    
    county_measures.reset_index(inplace=True)
    
    # Creating table that is long by County and wide by each measure is averaged value from all available 
    # years for given measure. 
    county_meas_piv = county_measures.pivot(index='fipscode', columns='Measure name', values='Raw value')
    
    county_meas_piv.to_pickle('../../data/02_intermediate/county_measures')
    return county_meas_piv


    
    