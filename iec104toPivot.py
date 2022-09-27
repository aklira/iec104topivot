import json
import sys
import os.path
from jsonpath_ng import jsonpath
from jsonpath_ng.ext import parse

# IEC 104 M_SP_TB_1 to Pivot SpsTyp
def IEC104toP_1(pivotid, dp):
    print("IEC104toP_1 called")

    pivot_str = '''
        {
            "PIVOTTS":{
                "GTIS":{
                    "Cause":{
                        "stVal":1
                    },
                    "ComingFrom":"IEC104",
                    "Confirmation":{
                        "stVal":true
                    },
                    "Identifier":"String",
                    "Origin":{
                        "stVal":"String"
                    },
                    "SpsTyp":{
                        "q":{
                        "DetailQuality":{
                            "overflow":false
                        },
                        "Source":"process",
                        "Validity":"good",
                        "operatorBlocked":false,
                        "test":false
                        },
                        "stVal":true,
                        "t":{
                        "FractionOfSecond":1,
                        "SecondSinceEpoch":1
                        }
                    },
                    "TmOrg":{
                        "stVal":"genuine"
                    },
                    "TmValidity":{
                        "stVal":"VALID"
                    }
                }
            }
        }
    '''
    pivot = json.loads(pivot_str)

    pivot['PIVOTTS']['GTIS']['Cause']['stVal'] = dp['data_object']['do_cot']
    pivot['PIVOTTS']['GTIS']['Confirmation']['stVal'] = dp['data_object']['do_negative']
    pivot['PIVOTTS']['GTIS']['Identifier'] = pivotid
    pivot['PIVOTTS']['GTIS']['Origin']['stVal'] = dp['data_object']['do_oa']
    if dp['data_object']['do_quality_iv'] == 'true':
        pivot['PIVOTTS']['GTIS']['SpsTyp']['q']['Validity'] = 'invalid'
    if dp['data_object']['do_quality_ov'] == 'true':
        pivot['PIVOTTS']['GTIS']['SpsTyp']['q']['DetailQuality']['overflow'] = 'true'
    if dp['data_object']['do_quality_bl'] == 'true':
        pivot['PIVOTTS']['GTIS']['SpsTyp']['q']['operatorBlocked'] = 'true'
    if dp['data_object']['do_quality_sb'] == 'true':
        pivot['PIVOTTS']['GTIS']['SpsTyp']['q']['Source'] = 'substituted'
    if dp['data_object']['do_quality_nt'] == 'true':
        pivot['PIVOTTS']['GTIS']['SpsTyp']['q']['Validity'] = 'questionable'
    pivot['PIVOTTS']['GTIS']['SpsTyp']['q']['test'] = dp['data_object']['do_test']
    pivot['PIVOTTS']['GTIS']['SpsTyp']['stVal'] = dp['data_object']['do_value']
    pivot['PIVOTTS']['GTIS']['SpsTyp']['t']['SecondSinceEpoch'] = dp['data_object']['do_ts']
    if dp['data_object']['do_ts_iv'] == 'true':
        pivot['PIVOTTS']['GTIS']['TmValidity']['stVal'] = 'INVALID'
    if dp['data_object']['do_ts_sub'] == 'true':
        pivot['PIVOTTS']['GTIS']['TmOrg']['stVal'] = 'substituted'
    

    return pivot

def IEC104toPivot(pivotid, datapoint, callback):
    return callback(pivotid, datapoint)

def get_pivot_attr(jobj, v):
    jp_res = parse('$..protocols[?address=="'+ v +'"]').find(jobj)
    res = [str(match.full_path) for match in jp_res]
    s = res[0].split('.')
    path = s[0]+'.'+s[1]+'.'+s[2]+'[*]'
    jp_res = parse(path).find(jobj)
    res = [match.value for match in jp_res]
    return res

def get_mapping_rule(jobj, v1, v2):
    print(v1, v2)
    jp_res = parse('$..mapping_rules[?input_type=="'+ v1 +'" & output_type=="'+ v2 +'"]').find(jobj)
    res = [match.value for match in jp_res]
    print(res)
    return res[0]["mapping_rule"]

def main():
    fname = sys.argv[1] # exchanged data conf

    f = open('iec104_m_sp_na_1.json') # iec104 datapoint example
    datapoint = json.load(f)
    f.close()

    msg_id = str(datapoint['data_object']['do_ca']) + '-' + str(datapoint['data_object']['do_ioa'])

    if not os.path.isfile(fname):
        print('ERROR: input file not found')
    else:
        f = open(fname)
        jobj = json.load(f)
        f.close()
        res = get_pivot_attr(jobj, msg_id)
        label = res[0]['label']
        pivot_id = res[0]['pivot_id']
        pivot_type = res[0]['pivot_type']
        print(label, pivot_id, pivot_type)

        f = open('mapping_rules.json') # mapping rules conf
        jobj = json.load(f)
        f.close()
        map_r = get_mapping_rule(jobj, 'M_SP_TB_1', pivot_type)
        print(map_r)

        if map_r == 'IEC104toP_1':
            print(IEC104toPivot(pivot_id, datapoint, IEC104toP_1))

if __name__ == '__main__':
    main()

